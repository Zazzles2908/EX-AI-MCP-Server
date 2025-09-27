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

# Load environment variables
try:
    from dotenv import load_dotenv

    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
            print(f"[ex-mcp] loaded .env from {env_path}", file=sys.stderr)
    else:
        if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
            print(f"[ex-mcp] no .env file found at {env_path}", file=sys.stderr)

except ImportError:
    if _env_true("EX_MCP_BOOTSTRAP_DEBUG"):
        print("[ex-mcp] python-dotenv not available, skipping .env load", file=sys.stderr)
except Exception as dotenv_err:
    msg = f"[ex-mcp] dotenv load failed: {dotenv_err}"
    _write_wrapper_error(msg)

def _hot_reload_env() -> None:
    """Hot reload environment variables from .env file."""
    try:
        from dotenv import load_dotenv as _ld
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            _ld(env_path, override=True)
    except Exception:
        # Never let hot-reload break a tool call
        pass

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

from tools import (
    AnalyzeTool,
    ChallengeTool,
    ChatTool,
    CodeReviewTool,
    ConsensusTool,
    DebugIssueTool,
    DocgenTool,
    ListModelsTool,
    PlannerTool,
    PrecommitTool,
    RefactorTool,
    SecauditTool,
    SelfCheckTool,
    TestGenTool,
    ThinkDeepTool,
    TracerTool,
    VersionTool,
)

# Import modular server components
from src.server.providers import configure_providers
from src.server.tools import filter_disabled_tools
from src.server.handlers import (
    handle_call_tool,
    handle_get_prompt,
    handle_list_prompts,
    handle_list_tools,
)

# Auggie integration check
AUGGIE_ACTIVE = _env_true("AUGGIE_ACTIVE")
AUGGIE_WRAPPERS_AVAILABLE = False

try:
    from auggie.wrappers import AUGGIE_WRAPPERS_AVAILABLE
except ImportError:
    pass

def detect_auggie_cli() -> bool:
    """Detect if running under Auggie CLI."""
    return any(
        "auggie" in arg.lower() or "aug" in arg.lower()
        for arg in sys.argv
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
def setup_logging():
    """Set up logging configuration."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Create logs directory
    logs_dir = Path(".logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stderr),
            RotatingFileHandler(
                logs_dir / "server.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )

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
setup_logging()
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("EX MCP Server")

# Tool registry
TOOLS = {
    "chat": ChatTool(),
    "thinkdeep": ThinkDeepTool(),
    "planner": PlannerTool(),
    "consensus": ConsensusTool(),
    "codereview": CodeReviewTool(),
    "precommit": PrecommitTool(),
    "debug": DebugIssueTool(),
    "secaudit": SecauditTool(),
    "docgen": DocgenTool(),
    "analyze": AnalyzeTool(),
    "refactor": RefactorTool(),
    "tracer": TracerTool(),
    "testgen": TestGenTool(),
    "challenge": ChallengeTool(),
    "listmodels": ListModelsTool(),
    "version": VersionTool(),
    "selfcheck": SelfCheckTool(),
}

# Auggie tool registration
if (AUGGIE_ACTIVE or detect_auggie_cli()) and AUGGIE_WRAPPERS_AVAILABLE:
    logger.info("Registering Auggie-optimized tools (aug_*) alongside originals")

    class AugChatTool(ChatTool):
        def get_name(self) -> str:
            return "aug_chat"

        def get_description(self) -> str:
            return f"[Auggie-optimized] {super().get_description()}"

    class AugThinkDeepTool(ThinkDeepTool):
        def get_name(self) -> str:
            return "aug_thinkdeep"

        def get_description(self) -> str:
            return f"[Auggie-optimized] {super().get_description()}"

    class AugConsensusTool(ConsensusTool):
        def get_name(self) -> str:
            return "aug_consensus"

        def get_description(self) -> str:
            return f"[Auggie-optimized] {super().get_description()}"

    # Register Auggie tools
    TOOLS.update({
        "aug_chat": AugChatTool(),
        "aug_thinkdeep": AugThinkDeepTool(),
        "aug_consensus": AugConsensusTool(),
    })

# Global state
IS_AUTO_MODE = _env_true("EX_AUTO_MODE")
_providers_configured = False

def _ensure_providers_configured():
    """Ensure providers are configured when server is used as a module."""
    global _providers_configured
    if not _providers_configured:
        try:
            configure_providers()
            _providers_configured = True
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
    start_ts = time.time()
    try:
        result = await handle_call_tool(name, arguments)
        # Emit toolcall JSONL for transparency
        try:
            import json as _json
            req_id = (arguments or {}).get("request_id")
            duration_s = round(time.time() - start_ts, 3)
            # Compute adaptive preview and summary (raw output preserved)
            def _clamp(v, lo, hi):
                return max(lo, min(hi, v))
            def _derive_bullets(text, max_bullets=5):
                try:
                    import re as _re
                    if not text:
                        return []
                    parts = [_p.strip() for _p in _re.split(r'[\n\.;]+', str(text)) if _p.strip()]
                    return parts[:max_bullets]
                except Exception:
                    return []
            def _compute_preview_and_summary(args, res, duration_s):
                import os as _os, re as _re, math as _math
                # result text extraction
                if isinstance(res, dict):
                    res_text = str(res.get("result", "")) or str(res)
                else:
                    res_text = str(res)
                out_chars = len(res_text or "")
                retries = int((args or {}).get("retries", 0) or 0)
                error_flag = 1 if (args or {}).get("error") else 0
                base = _math.log10(max(1, out_chars)) + 0.4*retries + 0.3*error_flag + 0.002*(duration_s*1000.0)
                env_max = int((_os.getenv("EXAI_TOOLCALL_PREVIEW_MAX_CHARS", "2000") or "2000"))
                n = int(_clamp(round(120*base), 280, env_max))
                preview = (res_text or "")[:n] + ("..." if out_chars > n else "")
                sum_max_words = int((_os.getenv("EXAI_TOOLCALL_SUMMARY_MAX_WORDS", "600") or "600"))
                target_words = int(_clamp(round(180*base), 150, sum_max_words))
                words = _re.split(r'\s+', (res_text or "").strip())
                summary_text = " ".join(words[:target_words])
                prompt_text = (args or {}).get("prompt")
                bullets = _derive_bullets(prompt_text, max_bullets=5)
                return {
                    "result_preview": preview,
                    "result_preview_len": n,
                    "result_truncated": out_chars > n,
                    "prompt_bullets": bullets,

                    "summary_words": target_words,
                    "summary_text": summary_text
                }
            preview_info = _compute_preview_and_summary(arguments, result, duration_s)
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
                import os as _os, json as _json, re as _re
                flag = (_os.getenv("EXAI_TOOLCALL_LOG_RAW_FULL", "false") or "false").strip().lower() == "true"
                if flag:
                    # Extract raw result text only (do not include prompts/system)
                    if isinstance(result, dict):
                        _raw_text = str(result.get("result", "") or result)
                    else:
                        _raw_text = str(result)
                    _raw_text = _raw_text or ""
                    # Basic redaction for likely secrets
                    try:
                        _raw_text = _re.sub(r"sk-[A-Za-z0-9]{16,}", "sk-***REDACTED***", _raw_text)
                        _raw_text = _re.sub(r"[A-Fa-f0-9]{32,}", "***REDACTED_HEX***", _raw_text)
                        _raw_text = _re.sub(r"[A-Za-z0-9]{40,}", "***REDACTED_TOKEN***", _raw_text)
                    except Exception:
                        pass
                    # Size cap ~10MB
                    try:
                        _cap = 10*1024*1024
                        _bytes = _raw_text.encode("utf-8")
                        _truncated = False
                        if len(_bytes) > _cap:
                            _raw_text = _bytes[: int(_cap*0.95)].decode("utf-8", errors="ignore") + "... [TRUNCATED]"
                            _truncated = True
                    except Exception:
                        _truncated = False
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
            except Exception:
                pass

        except Exception:
            pass
        return result
    except Exception as e:
        # Log error envelope, then re-raise
        try:
            import json as _json
            req_id = (arguments or {}).get("request_id")
            logging.getLogger("toolcalls").info(_json.dumps({
                "timestamp": time.time(),
                "tool": name,
                "request_id": req_id,
                "error": str(e)
            }))
        except Exception:
            pass
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
    # Configure providers
    try:
        configure_providers()
    except Exception as e:
        logger.error(f"Failed to configure providers: {e}")
        sys.exit(1)

    # Filter disabled tools
    global TOOLS
    TOOLS = filter_disabled_tools(TOOLS)
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
