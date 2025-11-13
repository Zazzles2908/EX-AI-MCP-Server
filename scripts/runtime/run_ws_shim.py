#!/usr/bin/env python
"""
EXAI MCP Shim - Protocol Translator
Bridges standard MCP protocol <-> EXAI custom WebSocket protocol.

This shim connects to the EXAI daemon (running in Docker) and translates:
- MCP stdio messages -> Custom WebSocket protocol
- Custom WebSocket responses -> MCP stdio responses

PROCESS MANAGEMENT FIX: Added proper signal handling to prevent orphaned child processes.
"""

import asyncio
import json
import logging
import os
import signal
import sys
from pathlib import Path
from typing import Any, Dict, List

import websockets
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Setup paths
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Setup logging FIRST (before using logger)
logger = logging.getLogger(__name__)

# Load environment
try:
    from src.bootstrap import load_env
    load_env()
except Exception as e:
    logger.warning(f"Could not load env from bootstrap: {e}")
    # Try loading .env manually
    from dotenv import load_dotenv
    env_file = os.getenv('ENV_FILE', '.env')
    load_dotenv(env_file)

# Configuration
DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3010"))

# Initialize MCP server
app = Server("exai-mcp")

# Global daemon connection
_daemon_ws = None
_daemon_lock = asyncio.Lock()


async def get_daemon_connection():
    """Get or create WebSocket connection to daemon."""
    global _daemon_ws
    async with _daemon_lock:
        if _daemon_ws is None or _daemon_ws.closed:
            # DEBUG: Log environment variables
            token = os.getenv("EXAI_WS_TOKEN", "NOT SET")
            logger.info(f"[DAEMON_CONNECT] Token: {token[:20]}...")
            logger.info(f"[DAEMON_CONNECT] Host: {DAEMON_HOST}, Port: {DAEMON_PORT}")

            daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
            logger.info(f"[DAEMON_CONNECT] Connecting to {daemon_uri}...")

            try:
                _daemon_ws = await websockets.connect(daemon_uri)
                logger.info("[DAEMON_CONNECT] ✓ Connected to daemon")

                # Send hello with token
                auth_token = os.getenv("EXAI_WS_TOKEN", "")
                logger.info(f"[HELLO] Token from env: {auth_token[:20] if auth_token else 'EMPTY'}...")

                hello_msg = {
                    "op": "hello",
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "exai-mcp-shim", "version": "1.0.0"},
                    "token": auth_token
                }
                await _daemon_ws.send(json.dumps(hello_msg))
                logger.info("[HELLO] ✓ Hello sent to daemon")

                # Wait for hello_ack (increased timeout to 30s for stability under load)
                response = await asyncio.wait_for(_daemon_ws.recv(), timeout=30)
                hello_ack = json.loads(response)
                logger.info(f"[HELLO] ✓ Received hello_ack: ok={hello_ack.get('ok')}")

                if not hello_ack.get("ok"):
                    error_msg = hello_ack.get('error', 'Unknown error')
                    logger.error(f"[HELLO] ✗ Daemon rejected connection: {error_msg}")
                    await _daemon_ws.close()
                    _daemon_ws = None
                    raise Exception(f"Daemon authentication failed: {error_msg}")

            except asyncio.TimeoutError as e:
                logger.error(f"[DAEMON_CONNECT] ✗ Timeout waiting for daemon response: {e}")
                if _daemon_ws and not _daemon_ws.closed:
                    await _daemon_ws.close()
                _daemon_ws = None
                raise
            except Exception as e:
                logger.error(f"[DAEMON_CONNECT] ✗ Failed to connect: {e}", exc_info=True)
                if _daemon_ws and not _daemon_ws.closed:
                    await _daemon_ws.close()
                _daemon_ws = None
                raise

        return _daemon_ws


@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Handle tools/list - get list from daemon."""
    logger.info("[TOOLS] List tools requested")
    try:
        daemon_ws = await get_daemon_connection()
        request_id = f"list_{id(daemon_ws)}"

        # Send list_tools request to daemon
        await daemon_ws.send(json.dumps({
            "op": "list_tools",
            "id": request_id
        }))

        # Wait for response
        response = await asyncio.wait_for(daemon_ws.recv(), timeout=30)
        data = json.loads(response)

        daemon_tools = data.get("tools", [])
        logger.info(f"[TOOLS] ✓ Received {len(daemon_tools)} tools from daemon")

        # Convert daemon tool format to MCP Tool format
        mcp_tools = []
        for tool in daemon_tools:
            mcp_tool = Tool(
                name=tool["name"],
                description=tool.get("description", ""),
                inputSchema=tool.get("inputSchema", {}),
                title=tool.get("title", None),
                outputSchema=tool.get("outputSchema", None)
            )
            mcp_tools.append(mcp_tool)

        return mcp_tools

    except Exception as e:
        logger.error(f"[TOOLS] ✗ Failed to list tools: {e}", exc_info=True)
        return []


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tools/call - execute tool via daemon."""
    logger.info(f"[TOOL_CALL] Tool: {name}")
    try:
        daemon_ws = await get_daemon_connection()
        request_id = f"call_{id(daemon_ws)}"

        # Send call_tool request to daemon
        await daemon_ws.send(json.dumps({
            "op": "call_tool",
            "id": request_id,
            "name": name,
            "arguments": arguments
        }))

        # Wait for response
        response = await asyncio.wait_for(daemon_ws.recv(), timeout=60)
        data = json.loads(response)

        result = data.get("result", [])
        logger.info(f"[TOOL_CALL] ✓ Tool '{name}' executed successfully")

        # Convert result to TextContent
        content = []
        for item in result:
            if isinstance(item, dict) and "text" in item:
                content.append(TextContent(type="text", text=item["text"]))
            elif isinstance(item, str):
                content.append(TextContent(type="text", text=item))
            else:
                content.append(TextContent(type="text", text=str(item)))

        return content

    except Exception as e:
        logger.error(f"[TOOL_CALL] ✗ Tool '{name}' failed: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]


async def main():
    """Main shim server using stdio."""
    logger.info(f"=" * 60)
    logger.info(f"EXAI MCP Shim Starting (stdio mode)")
    logger.info(f"  Daemon: {DAEMON_HOST}:{DAEMON_PORT}")
    logger.info(f"=" * 60)

    # Run server using stdio
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    # Setup logging - CRITICAL: Send to stderr for MCP protocol compliance
    # Temporarily disable logging to test if MCP responses go to stdout
    log_level = os.getenv("LOG_LEVEL", "WARNING")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stderr,  # FIX: Send all logs to stderr, not stdout
        force=True  # Override any existing configuration
    )
    # Reduce noise from MCP library logging
    logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.ERROR)
    logging.getLogger("mcp").setLevel(logging.ERROR)

    # Set process group for proper cleanup
    # This ensures child processes are terminated when parent exits
    # FIX: Windows compatibility - only call on Unix systems
    try:
        if hasattr(os, 'setpgrp'):
            os.setpgrp()
            logger.info("Process group set for Unix/Linux")
        else:
            logger.info("Windows detected - skipping process group set")
    except Exception as e:
        logger.warning(f"Could not set process group: {e}")

    # Global flag for shutdown
    shutting_down = False

    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        global shutting_down
        if shutting_down:
            # Force kill if already shutting down
            logger.warning("Forced shutdown initiated")
            try:
                if hasattr(os, 'killpg'):
                    os.killpg(0, signal.SIGKILL)
            except Exception:
                pass
            return

        logger.info(f"Received signal {signum}, shutting down gracefully...")
        shutting_down = True

        # Kill entire process group (Unix only)
        try:
            if hasattr(os, 'killpg'):
                os.killpg(0, signal.SIGTERM)
        except Exception as e:
            logger.warning(f"Error sending SIGTERM to process group: {e}")

        # Exit
        sys.exit(0)

    # Register signal handlers (Windows-compatible)
    # On Windows, signal only works for SIGINT, not SIGTERM
    try:
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, signal_handler)
    except Exception:
        pass
    try:
        signal.signal(signal.SIGINT, signal_handler)
    except Exception:
        logger.warning("Could not register SIGINT handler")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shim stopped by user")
    except Exception as e:
        logger.error(f"Shim fatal error: {e}", exc_info=True)
        sys.exit(1)
