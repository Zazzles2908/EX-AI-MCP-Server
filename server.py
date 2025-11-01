"""
EX MCP Server - Production-Ready Implementation v2.0

This module implements the production-ready MCP (Model Context Protocol) server with
intelligent routing capabilities using GLM-4.5-Flash as an AI manager.

Key Features:
- Intelligent routing between GLM (web browsing) and Kimi (file processing) providers
- GLM-4.5-Flash as AI manager for routing decisions
- Cost-aware routing strategies with fallback mechanisms
- Production-ready error handling and retry logic
- MCP protocol compliance with WebSocket support
- Comprehensive logging and monitoring

Architecture:
- MCP Server: Handles protocol communication and tool discovery
- Intelligent Router: Routes requests based on task type and provider capabilities
- Provider System: GLM for web search, Kimi for file processing
- Fallback System: Automatic retry with alternative providers
- Configuration: Streamlined environment-based configuration

The server supports both stdio and WebSocket transports for maximum compatibility.
"""

import asyncio
import atexit
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional, Dict, List


# Environment and configuration setup
def _env_true(key: str, default: str = "false") -> bool:
    """Check if environment variable is set to a truthy value."""
    return os.getenv(key, default).lower() in ("true", "1", "yes", "on")

def _write_wrapper_error(text: str) -> None:
    """Write error message to stderr with proper formatting."""
    try:
        print(f"[ex-mcp] {text}", file=sys.stderr, flush=True)
    except Exception:
        pass

# Bootstrap and environment loading
if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
    print("[ex-mcp] bootstrap starting (pid=%s, py=%s)" % (os.getpid(), sys.executable), file=sys.stderr)

# Use bootstrap module for environment loading
from src.bootstrap import load_env, get_repo_root

# Load environment variables
env_loaded = load_env()
if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
    if env_loaded:
        print(f"[ex-mcp] loaded .env from {get_repo_root() / '.env'}", file=sys.stderr)
    else:
        print(f"[ex-mcp] no .env file found at {get_repo_root() / '.env'}", file=sys.stderr)

def _hot_reload_env() -> None:
    """Hot reload environment variables from .env file."""
    load_env(override=True)

# Import MCP components
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        GetPromptResult,
        Prompt,
        PromptsCapability,
        ServerCapabilities,
        TextContent,
        Tool,
        ToolsCapability,
    )

    # MCP SDK compatibility
    try:
        from mcp.types import ToolAnnotations
    except ImportError:
        ToolAnnotations = None

except ImportError as e:
    _write_wrapper_error(f"Failed to import MCP components: {e}")
    sys.exit(1)

# Import tools and configuration
from config import __version__
# Re-export follow-up helper for tools that import from server
from src.server.utils import get_follow_up_instructions  # type: ignore

# Only import tools needed for Auggie wrappers (all other tools loaded via ToolRegistry)
from tools import ChatTool, ConsensusTool, ThinkDeepTool

# Import modular server components
from src.server.providers import configure_providers
from src.server.tools import filter_disabled_tools, filter_by_provider_capabilities
from src.server.handlers import (
    handle_call_tool,
    handle_get_prompt,
    handle_list_prompts,
    handle_list_tools,
)

# Logging configuration
class LocalTimeFormatter(logging.Formatter):
    """Custom formatter that uses local time instead of UTC."""

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            s = "%s,%03d" % (t, record.msecs)
        return s

class JsonLineFormatter(logging.Formatter):
    """JSON line formatter for structured logging."""

    def format(self, record):
        import json
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "tool_name"):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, "model"):
            log_entry["model"] = record.model
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id

        return json.dumps(log_entry)

# Configure logging
def setup_server_logging():
    """Set up logging configuration with specialized loggers."""
    from src.bootstrap import setup_logging as bootstrap_setup_logging

    # Setup basic logging using bootstrap
    bootstrap_setup_logging("server", log_file=str(get_repo_root() / "logs" / "server.log"))

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logs_dir = get_repo_root() / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Set up structured logging for metrics
    metrics_logger = logging.getLogger("metrics")
    metrics_handler = RotatingFileHandler(
        logs_dir / "metrics.jsonl",
        maxBytes=50*1024*1024,  # 50MB
        backupCount=3
    )
    metrics_handler.setFormatter(JsonLineFormatter())
    metrics_logger.addHandler(metrics_handler)
    metrics_logger.setLevel(logging.INFO)

    # Dedicated JSONL for router decisions (pure JSON lines)
    router_logger = logging.getLogger("router")
    router_handler = RotatingFileHandler(
        logs_dir / "router.jsonl",
        maxBytes=50*1024*1024,
        backupCount=3
    )
    router_handler.setFormatter(logging.Formatter("%(message)s"))
    router_logger.addHandler(router_handler)
    router_logger.setLevel(logging.INFO)
    # Dedicated JSONL for tool call results (pure JSON lines)
    toolcalls_logger = logging.getLogger("toolcalls")
    toolcalls_handler = RotatingFileHandler(
        logs_dir / "toolcalls.jsonl",
        maxBytes=50*1024*1024,
        backupCount=3
    )
    toolcalls_handler.setFormatter(logging.Formatter("%(message)s"))
    toolcalls_logger.addHandler(toolcalls_handler)
    toolcalls_logger.setLevel(logging.INFO)
    # Optional: Dedicated JSONL for raw tool call outputs (guarded by env)
    toolcalls_raw_logger = logging.getLogger("toolcalls_raw")
    toolcalls_raw_handler = RotatingFileHandler(
        logs_dir / "toolcalls_raw.jsonl",
        maxBytes=50*1024*1024,
        backupCount=3
    )
    toolcalls_raw_handler.setFormatter(logging.Formatter("%(message)s"))
    toolcalls_raw_logger.addHandler(toolcalls_raw_handler)
    toolcalls_raw_logger.setLevel(logging.INFO)
    toolcalls_raw_logger.propagate = False

    toolcalls_logger.propagate = False

    router_logger.propagate = False

# Initialize logging
setup_server_logging()
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("EX MCP Server")

# ============================================================================
# SINGLETON INITIALIZATION (Mission 1: Kill the singleton race)
# ============================================================================
# CRITICAL: Use bootstrap.singletons to ensure providers and tools are initialized
# exactly once per process, regardless of whether server.py or ws_server.py imports first.
#
# This replaces the previous pattern where both entry points could independently call:
# - configure_providers()
# - ToolRegistry().build_tools()
# - register_provider_specific_tools()
#
# Now all initialization happens through idempotent bootstrap functions that use
# module-level flags to prevent re-execution.

from src.bootstrap import ensure_tools_built, ensure_provider_tools_registered

# Build tools once (idempotent - safe to call multiple times)
TOOLS = ensure_tools_built()

# NOTE: Provider-specific tools are NOT registered at import time
# They will be registered on-demand when:
# 1. main() is called (stdio server)
# 2. list_tools is called (WebSocket daemon)
# This ensures providers are configured before attempting tool registration

# Legacy function kept for backward compatibility with ws_server.py imports
# Now delegates to bootstrap.singletons for idempotent behavior
def register_provider_specific_tools() -> None:
    """
    Legacy wrapper for backward compatibility.
    Delegates to bootstrap.singletons.ensure_provider_tools_registered().
    """
    ensure_provider_tools_registered(TOOLS)

# Auggie tool registration
# Global state
IS_AUTO_MODE = _env_true("EX_AUTO_MODE")

def _ensure_providers_configured():
    """
    Ensure providers are configured when server is used as a module.

    Legacy wrapper for backward compatibility with ws_server.py imports.
    Delegates to bootstrap.singletons.ensure_providers_configured().
    """
    from src.bootstrap import ensure_providers_configured
    try:
        ensure_providers_configured()
    except Exception as e:
        logger.warning(f"Provider configuration failed: {e}")

# Register MCP handlers
@server.list_tools()
async def list_tools_handler():
    """Handle MCP list_tools requests."""
    return await handle_list_tools()

@server.call_tool()
async def call_tool_handler(name: str, arguments: dict[str, Any]):
    """Handle MCP call_tool requests."""
    _ensure_providers_configured()
    # Ensure provider-specific tools are registered once providers are live
    try:
        register_provider_specific_tools()
    except Exception:
        pass
    start_ts = time.time()
    try:
        result = await handle_call_tool(name, arguments)
        # Emit toolcall JSONL for transparency
        try:
            import json as _json
            from src.server.logging_utils import compute_preview_and_summary

            req_id = (arguments or {}).get("request_id")
            duration_s = round(time.time() - start_ts, 3)

            # Compute adaptive preview and summary using extracted utility
            preview_info = compute_preview_and_summary(arguments, result, duration_s)
            payload = {
                "timestamp": time.time(),
                "tool": name,
                "request_id": req_id,
                "duration_s": duration_s,
            }
            payload.update(preview_info)
            logging.getLogger("toolcalls").info(_json.dumps(payload))
            # Optional raw mirror: write full model output (no system prompts) when enabled
            try:
                import os as _os, json as _json
                from src.server.logging_utils import redact_sensitive_data, truncate_large_text

                flag = (_os.getenv("EXAI_TOOLCALL_LOG_RAW_FULL", "false") or "false").strip().lower() == "true"
                if flag:
                    # Extract raw result text only (do not include prompts/system)
                    if isinstance(result, dict):
                        _raw_text = str(result.get("result", "") or result)
                    else:
                        _raw_text = str(result)
                    _raw_text = _raw_text or ""

                    # Redact sensitive data using extracted utility
                    _raw_text = redact_sensitive_data(_raw_text)

                    # Truncate if too large using extracted utility
                    _raw_text, _truncated = truncate_large_text(_raw_text, max_bytes=10*1024*1024)

                    _raw_payload = {
                        "timestamp": time.time(),
                        "tool": name,
                        "request_id": req_id,
                        "duration_s": duration_s,
                        "raw_len": len(_raw_text),
                        "truncated": _truncated,
                        "raw": _raw_text,
                    }
                    logging.getLogger("toolcalls_raw").info(_json.dumps(_raw_payload))
            except Exception as log_err:
                # Non-critical: Raw logging failure shouldn't break tool execution
                logging.getLogger("server").warning(f"Failed to log raw tool output: {log_err}")

        except Exception as log_err:
            # Non-critical: Logging failure shouldn't break tool execution
            logging.getLogger("server").warning(f"Failed to log tool call: {log_err}")
        return result
    except Exception as e:
        # Log error envelope, then re-raise (critical path)
        try:
            import json as _json
            req_id = (arguments or {}).get("request_id")
            logging.getLogger("toolcalls").info(_json.dumps({
                "timestamp": time.time(),
                "tool": name,
                "request_id": req_id,
                "error": str(e)
            }))
        except Exception as log_err:
            # Non-critical: Error logging failure shouldn't suppress the original error
            logging.getLogger("server").warning(f"Failed to log tool error: {log_err}")
        raise

@server.list_prompts()
async def list_prompts_handler():
    """Handle MCP list_prompts requests."""
    return await handle_list_prompts()

@server.get_prompt()
async def get_prompt_handler(name: str, arguments: dict[str, Any] = None):
    """Handle MCP get_prompt requests."""
    return await handle_get_prompt(name, arguments)

async def main():
    """Main server entry point."""
    global TOOLS  # Declare global before any use

    # Configure providers using bootstrap singleton (idempotent)
    from src.bootstrap import ensure_providers_configured, ensure_provider_tools_registered
    try:
        ensure_providers_configured()
        # Register provider-specific tools now that providers are configured
        ensure_provider_tools_registered(TOOLS)
    except Exception as e:
        logger.error(f"Failed to configure providers: {e}")
        sys.exit(1)

    # Filter disabled tools
    TOOLS = filter_disabled_tools(TOOLS)
    TOOLS = filter_by_provider_capabilities(TOOLS)
    # Set up stdio streams and run server
    # mcp.server.stdio.stdio_server is an async context manager in current SDK
    async with stdio_server() as (read_stream, write_stream):

        # Configure progress notifications
        try:
            from utils.progress import set_mcp_notifier

            async def _notify_progress(level: str, msg: str):
                try:
                    # Try to emit via MCP session if available
                    rc = getattr(server, "_request_context", None)
                    sess = getattr(rc, "session", None) if rc else None
                    if sess and hasattr(sess, "send_log_message"):
                        await sess.send_log_message(level=level, data=f"[PROGRESS] {msg}")
                except Exception:
                    pass
                finally:
                    # Mirror to internal logger
                    try:
                        log_level = {"debug": 10, "info": 20, "warning": 30, "error": 40}.get(level, 20)
                        server._logger.log(log_level, f"[PROGRESS] {msg}")
                    except Exception:
                        pass

            set_mcp_notifier(_notify_progress)
        except Exception:
            pass

        # Emit handshake breadcrumb
        try:
            if _env_true("EX_MCP_STDERR_BREADCRUMBS"):
                print("[ex-mcp] stdio_server started; awaiting MCP handshake...", file=sys.stderr)
        except Exception:
            pass

        # Run server
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=os.getenv("MCP_SERVER_NAME", "EX MCP Server"),
                server_version=__version__,
                capabilities=ServerCapabilities(
                    tools=ToolsCapability(),
                    prompts=PromptsCapability(),
                ),
            ),
        )

def run():
    """Console script entry point for ex-mcp-server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
