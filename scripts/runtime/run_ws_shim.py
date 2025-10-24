
#!/usr/bin/env python
import asyncio
import json
import os
import sys
import uuid
import re
from typing import Any, Dict, List

# Bootstrap: Setup path and load environment
from pathlib import Path
# CRITICAL FIX (2025-10-21): Changed from parents[1] to parents[2] after moving to scripts/runtime/
# scripts/runtime/run_ws_shim.py -> parents[2] = repo root
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root, setup_logging

# Load environment variables
load_env()

# Import TimeoutConfig for coordinated timeout hierarchy
from config import TimeoutConfig

import websockets
from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Setup logging
logger = setup_logging("ws_shim", log_file=str(get_repo_root() / "logs" / "ws_shim.log"))
logger.debug(f"EX WS Shim starting pid={os.getpid()} py={sys.executable} repo={get_repo_root()}")

EXAI_WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
EXAI_WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
SESSION_ID = os.getenv("EXAI_SESSION_ID", str(uuid.uuid4()))

# CRITICAL: Validate auth token configuration
if EXAI_WS_TOKEN:
    logger.debug(f"[AUTH] Using auth token from .env (first 10 chars): {EXAI_WS_TOKEN[:10]}...")
else:
    logger.warning("[AUTH] No auth token configured (EXAI_WS_TOKEN is empty). "
                   "If daemon requires auth, connections will fail. "
                   "Set EXAI_WS_TOKEN in .env file to match daemon's token.")
MAX_MSG_BYTES = int(os.getenv("EXAI_WS_MAX_BYTES", str(32 * 1024 * 1024)))
PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "45"))
PING_TIMEOUT = int(os.getenv("EXAI_WS_PING_TIMEOUT", "30"))
EXAI_WS_AUTOSTART = os.getenv("EXAI_WS_AUTOSTART", "true").strip().lower() == "true"
EXAI_WS_CONNECT_TIMEOUT = float(os.getenv("EXAI_WS_CONNECT_TIMEOUT", "30"))  # Use config value (30s default) for reliable Docker daemon connection
EXAI_WS_HANDSHAKE_TIMEOUT = float(os.getenv("EXAI_WS_HANDSHAKE_TIMEOUT", "15"))
EXAI_SHIM_ACK_GRACE_SECS = float(os.getenv("EXAI_SHIM_ACK_GRACE_SECS", "120"))

# Health check configuration
HEALTH_FILE = get_repo_root() / "logs" / "ws_daemon.health.json"
# CRITICAL FIX (2025-10-15): Increased from 20s to 120s to prevent false positives during long operations
# The daemon updates health file every 10s, but during long operations (web search, rate limit retries,
# large streaming responses), the health file may not update for extended periods. 120s allows for:
# - GLM/Kimi streaming timeouts (300s/600s) to trigger first
# - Rate limit retries with exponential backoff
# - Web search operations
# If health file is >120s old, daemon is likely truly stuck or crashed
HEALTH_FRESH_SECS = 120.0  # Health file must be updated within this many seconds to be considered fresh
SKIP_HEALTH_CHECK = os.getenv("EXAI_WS_SKIP_HEALTH_CHECK", "false").strip().lower() == "true"  # Skip health check for Docker/remote daemons

server = Server(os.getenv("MCP_SERVER_ID", "ex-ws-shim"))

_ws = None  # type: ignore
_ws_lock = asyncio.Lock()
_health_monitor_task = None  # type: ignore
_last_successful_call = 0.0  # Track last successful tool call
_shutdown_event = None  # type: ignore  # Global shutdown event for graceful termination
_stdin_monitor_task = None  # type: ignore  # Task monitoring stdin for parent death


def _extract_clean_content(raw_text: str) -> str:
    """Extract clean content from EXAI MCP JSON responses or return as-is."""
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, dict) and 'content' in parsed:
            content = parsed['content']
            if isinstance(content, str):
                # Remove progress sections and agent turn markers if present
                content = re.sub(r'=== PROGRESS ===.*?=== END PROGRESS ===\n*', '', content, flags=re.DOTALL)
                content = re.sub(r"\n*---\n*\n*AGENT'S TURN:.*", '', content, flags=re.DOTALL)
                return content.strip()
            return str(content)
    except Exception:
        pass
    return raw_text.strip()


async def _parent_process_monitor():
    """
    Monitor parent process to detect when MCP client dies.

    CRITICAL FIX (2025-10-19): Prevents orphaned processes when MCP client crashes.
    When the parent MCP client (Augment Code, Claude Desktop) dies, this process
    becomes orphaned. This monitor detects parent death and triggers graceful shutdown.

    Uses psutil to check if parent process still exists.
    """
    global _shutdown_event
    try:
        import psutil

        # Get parent process ID
        parent_pid = os.getppid()
        logger.info(f"[PARENT_MONITOR] Started monitoring parent process (PID: {parent_pid})")

        # Check if parent exists
        try:
            parent = psutil.Process(parent_pid)
            parent_name = parent.name()
            logger.info(f"[PARENT_MONITOR] Parent process: {parent_name} (PID: {parent_pid})")
        except psutil.NoSuchProcess:
            logger.warning(f"[PARENT_MONITOR] Parent process {parent_pid} not found - may already be dead")
            _shutdown_event.set()
            return

        # Monitor parent process
        while not _shutdown_event.is_set():
            try:
                # Check if parent still exists
                if not psutil.pid_exists(parent_pid):
                    logger.warning(f"[PARENT_MONITOR] Parent process {parent_pid} died. Initiating shutdown...")
                    _shutdown_event.set()
                    break

                # Also check if parent is a zombie (defunct)
                try:
                    parent = psutil.Process(parent_pid)
                    if parent.status() == psutil.STATUS_ZOMBIE:
                        logger.warning(f"[PARENT_MONITOR] Parent process {parent_pid} is zombie. Initiating shutdown...")
                        _shutdown_event.set()
                        break
                except psutil.NoSuchProcess:
                    logger.warning(f"[PARENT_MONITOR] Parent process {parent_pid} disappeared. Initiating shutdown...")
                    _shutdown_event.set()
                    break

                # Check every 5 seconds
                await asyncio.sleep(5.0)

            except Exception as e:
                logger.error(f"[PARENT_MONITOR] Error checking parent process: {e}")
                await asyncio.sleep(5.0)

    except ImportError:
        logger.warning("[PARENT_MONITOR] psutil not available - parent monitoring disabled")
        logger.warning("[PARENT_MONITOR] Install psutil to enable orphaned process prevention")
    except Exception as e:
        logger.exception(f"[PARENT_MONITOR] Fatal error in parent monitor: {e}")
    finally:
        logger.info("[PARENT_MONITOR] Parent process monitor stopped")


async def _connection_health_monitor():
    """
    DEPRECATED (2025-10-15): Health monitor no longer needed with always-up proxy pattern.

    The new _ensure_ws() function implements infinite retry with auto-reconnect,
    so we don't need to exit the shim process anymore. This function is kept
    for backward compatibility but does nothing.

    OLD APPROACH (removed):
    - Monitored connection health every 30s
    - Exited shim after 90s of failures
    - Relied on Augment to restart shim
    - Problem: Augment only restarts when you toggle settings!

    NEW APPROACH (in _ensure_ws):
    - Infinite retry loop with exponential backoff
    - Never exits, just keeps trying to reconnect
    - When Docker comes back, automatically reconnects
    - No manual intervention needed!
    """
    logger.info("[HEALTH_MONITOR] Health monitor disabled - using always-up proxy pattern instead")
    # Sleep forever - this task does nothing now
    while True:
        await asyncio.sleep(3600)


def _check_daemon_health() -> tuple[bool, str]:
    """
    Check if WebSocket daemon is running and healthy.

    Returns:
        tuple[bool, str]: (is_healthy, status_message)
    """
    import time

    # Check if health file exists
    if not HEALTH_FILE.exists():
        return False, (
            "WebSocket daemon health file not found.\n"
            "This usually means the daemon is not running.\n"
            "\n"
            "To start the daemon:\n"
            "  Windows: .\\scripts\\force_restart.ps1\n"
            "  Linux/Mac: ./scripts/force_restart.sh\n"
            "\n"
            "To check daemon status:\n"
            "  python scripts/ws/ws_status.py"
        )

    # Check if health file is fresh
    try:
        health_data = json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
        health_timestamp = float(health_data.get("t", 0))
        age = time.time() - health_timestamp

        if age > HEALTH_FRESH_SECS:
            return False, (
                f"WebSocket daemon health file is stale ({int(age)}s old).\n"
                "The daemon may have crashed or stopped responding.\n"
                "\n"
                "To restart the daemon:\n"
                "  Windows: .\\scripts\\force_restart.ps1\n"
                "  Linux/Mac: ./scripts/force_restart.sh\n"
                "\n"
                "To check daemon logs:\n"
                "  tail -f logs/ws_daemon.log"
            )

        # Health file is fresh - daemon is likely running
        pid = health_data.get("pid", "unknown")
        sessions = health_data.get("sessions", 0)
        return True, f"Daemon appears healthy (PID: {pid}, Sessions: {sessions})"

    except Exception as e:
        return False, (
            f"Failed to read daemon health file: {e}\n"
            "\n"
            "To restart the daemon:\n"
            "  Windows: .\\scripts\\force_restart.ps1\n"
            "  Linux/Mac: ./scripts/force_restart.sh"
        )


async def _start_daemon_if_configured() -> None:
    if not EXAI_WS_AUTOSTART:
        return
    try:
        # Launch the daemon in the same venv Python, non-blocking
        py = sys.executable
        # CRITICAL FIX (2025-10-24): Use correct daemon path
        daemon = str(_repo_root / "scripts" / "ws" / "run_ws_daemon.py")
        logger.info(f"Autostarting WS daemon: {py} -u {daemon}")
        # Use CREATE_NEW_PROCESS_GROUP on Windows implicitly via asyncio
        await asyncio.create_subprocess_exec(py, "-u", daemon, cwd=str(_repo_root))
    except Exception as e:
        logger.warning(f"Failed to autostart WS daemon: {e}")


async def _ensure_ws():
    """
    ALWAYS-UP PROXY PATTERN (2025-10-15) - Production-Hardened Version

    This function implements an auto-reconnecting WebSocket connection that NEVER gives up.
    When Docker container restarts, this function will keep retrying until the daemon is back.

    Key features:
    - Infinite retry with exponential backoff (0.25s → 30s cap)
    - Jitter to prevent thundering herd
    - Backoff reset on successful connection
    - Tiered logging to avoid spam
    - Connection validation via ping

    This solves the "manual Augment toggle" problem:
    - Augment only re-runs the shim command when you toggle settings
    - By never exiting, the shim stays alive and auto-reconnects when Docker comes back
    - User never needs to toggle Augment settings after Docker restart!

    Based on GLM-4.6 recommendations for production robustness.
    """
    # CRITICAL FIX (GLM-4.6): Import at function level, not inside exception handler
    import random

    global _ws
    if _ws and not _ws.closed:
        return _ws

    async with _ws_lock:
        if _ws and not _ws.closed:
            return _ws

        uri = f"ws://{EXAI_WS_HOST}:{EXAI_WS_PORT}"
        autostart_attempted = False
        retry_count = 0

        # Backoff configuration (GLM-4.6 recommended)
        base_delay = 0.25  # Start with 250ms
        max_delay = 30.0   # Cap at 30 seconds (increased from 5s)
        max_jitter = 0.1   # 10% jitter to prevent thundering herd

        # Connection validation timeout (GLM-4.6: make configurable)
        ping_timeout = float(os.getenv("EXAI_WS_PING_VALIDATION_TIMEOUT", "5.0"))

        # CRITICAL: Infinite retry loop - never give up!
        while True:
            try:
                retry_count += 1

                # Optional health check (can be skipped for Docker/remote daemons)
                if not SKIP_HEALTH_CHECK and retry_count == 1:
                    # Only check health on first attempt to avoid spam
                    is_healthy, health_message = _check_daemon_health()
                    if is_healthy:
                        logger.info(f"Daemon health check passed: {health_message}")
                    else:
                        logger.warning(f"Daemon health check failed (will retry): {health_message}")

                # Attempt WebSocket connection
                _pi = None if PING_INTERVAL <= 0 else PING_INTERVAL
                _pt = None if _pi is None or PING_TIMEOUT <= 0 else PING_TIMEOUT
                _ws = await websockets.connect(
                    uri,
                    max_size=MAX_MSG_BYTES,
                    ping_interval=_pi,
                    ping_timeout=_pt,
                    open_timeout=EXAI_WS_HANDSHAKE_TIMEOUT,
                )

                # Hello handshake
                await _ws.send(json.dumps({
                    "op": "hello",
                    "session_id": SESSION_ID,
                    "token": EXAI_WS_TOKEN,
                }))

                # Wait for ack
                ack_raw = await asyncio.wait_for(_ws.recv(), timeout=EXAI_WS_HANDSHAKE_TIMEOUT)
                ack = json.loads(ack_raw)
                if not ack.get("ok"):
                    raise RuntimeError(f"WS daemon refused connection: {ack}")

                # Validate connection with ping (GLM-4.6 recommended)
                try:
                    await asyncio.wait_for(_ws.ping(), timeout=ping_timeout)
                except Exception as ping_err:
                    logger.warning(f"Connection ping failed: {ping_err}. Retrying...")
                    await _ws.close()
                    raise RuntimeError("Connection validation failed")

                # Success! Log before resetting retry_count (GLM-4.6: atomic operation)
                if retry_count > 1:
                    logger.info(f"✅ Reconnected to WebSocket daemon at {uri} after {retry_count} attempts")
                else:
                    logger.info(f"Successfully connected to WebSocket daemon at {uri}")

                # CRITICAL FIX (GLM-4.6): Reset retry count BEFORE return to ensure atomicity
                # This prevents race conditions where retry_count doesn't reflect actual attempts
                retry_count = 0
                return _ws

            except Exception as e:
                # Try autostart once if connection refused
                if not autostart_attempted:
                    autostart_attempted = True
                    logger.info("Attempting to autostart WebSocket daemon...")
                    await _start_daemon_if_configured()

                # Tiered logging strategy (GLM-4.6 recommended)
                # Log immediately on first failure, then at milestones, then every 10th
                if retry_count == 1:
                    logger.warning(f"Failed to connect to {uri}: {e}. Will retry indefinitely...")
                elif retry_count in [5, 20, 50]:
                    logger.warning(f"Connection attempt {retry_count} failed. Still retrying...")
                elif retry_count % 10 == 0:
                    logger.warning(f"Still trying to connect to {uri} (attempt {retry_count})...")

                # Exponential backoff with jitter (GLM-4.6 recommended)
                # Formula: min(base * 2^min(retry, 8), max) + random_jitter
                # CRITICAL FIX (GLM-4.6): Import moved to top of function
                delay = min(base_delay * (2 ** min(retry_count, 8)), max_delay)
                jitter = random.uniform(0, max_jitter * delay)
                total_delay = delay + jitter

                if retry_count <= 5 or retry_count % 10 == 0:
                    logger.debug(f"Next retry in {total_delay:.1f}s (base: {delay:.1f}s, jitter: {jitter:.1f}s)")

                await asyncio.sleep(total_delay)

                # CRITICAL: Continue loop - never raise exception, never exit!
                continue


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    ws = await _ensure_ws()
    await ws.send(json.dumps({"op": "list_tools"}))
    raw = await ws.recv()
    msg = json.loads(raw)
    if msg.get("op") != "list_tools_res":
        raise RuntimeError(f"Unexpected reply from daemon: {msg}")
    tools = []
    for t in msg.get("tools", []):
        tools.append(Tool(name=t.get("name"), description=t.get("description"), inputSchema=t.get("inputSchema") or {"type": "object"}))
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    global _last_successful_call
    import time

    async def _once() -> List[TextContent]:
        ws = await _ensure_ws()
        req_id = str(uuid.uuid4())
        await ws.send(json.dumps({
            "op": "call_tool",
            "request_id": req_id,
            "name": name,
            "arguments": arguments or {},
        }))
        # Read until matching request_id with timeout
        # Use coordinated timeout hierarchy: shim timeout = 2x workflow tool timeout
        timeout_s = float(TimeoutConfig.get_shim_timeout())  # Auto-calculated (default: 240s)
        ack_grace = float(os.getenv("EXAI_SHIM_ACK_GRACE_SECS", "30"))
        deadline = asyncio.get_running_loop().time() + timeout_s
        while True:
            remaining = max(0.1, deadline - asyncio.get_running_loop().time())
            try:
                raw = await asyncio.wait_for((await _ensure_ws()).recv(), timeout=remaining)
            except asyncio.TimeoutError:
                raise RuntimeError("Daemon did not return call_tool_res in time")
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            # Dynamically extend wait on call_tool_ack for this request
            if msg.get("request_id") == req_id and msg.get("op") == "call_tool_ack":
                ack_timeout = float(msg.get("timeout") or 0) or timeout_s
                grace = float(os.getenv("EXAI_SHIM_ACK_GRACE_SECS", EXAI_SHIM_ACK_GRACE_SECS))
                deadline = asyncio.get_running_loop().time() + ack_timeout + grace
                continue
            # Ignore progress or unrelated messages
            if msg.get("request_id") == req_id and msg.get("op") == "progress":
                continue
            if msg.get("op") == "call_tool_res" and msg.get("request_id") == req_id:
                if msg.get("error"):
                    raise RuntimeError(f"Daemon error: {msg['error']}")
                # Prefer top-level 'text' compatibility field from WS daemon when present
                if isinstance(msg.get("text"), str) and msg.get("text").strip():
                    cleaned = _extract_clean_content(msg["text"])
                    return [TextContent(type="text", text=cleaned)]
                outs = []
                for o in msg.get("outputs", []):
                    if (o or {}).get("type") == "text":
                        outs.append(TextContent(type="text", text=(o or {}).get("text") or ""))
                    else:
                        outs.append(TextContent(type="text", text=json.dumps(o)))
                return outs
    # Try once, then reconnect and retry once on timeout/connection errors
    try:
        result = await _once()
        # Track successful call for health monitoring
        _last_successful_call = time.time()
        return result
    except Exception as e:
        if "did not return call_tool_res" in str(e) or "ConnectionClosed" in str(type(e)):
            try:
                # Force reconnect
                global _ws
                if _ws and not _ws.closed:
                    await _ws.close()
                _ws = None
                result = await _once()
                # Track successful call after reconnection
                _last_successful_call = time.time()
                return result
            except Exception:
                raise
        raise

# Single stdio entrypoint (cleaned up)

def main() -> None:
    global _health_monitor_task, _stdin_monitor_task, _shutdown_event
    init_opts = server.create_initialization_options()
    try:
        from mcp.server.stdio import stdio_server as _stdio_server
        async def _runner():
            global _shutdown_event, _stdin_monitor_task, _health_monitor_task

            # Create shutdown event
            _shutdown_event = asyncio.Event()

            # CRITICAL FIX (2025-10-19): Start parent process monitor to detect parent death
            # This prevents orphaned processes when MCP client crashes
            _stdin_monitor_task = asyncio.create_task(_parent_process_monitor())
            logger.info("[MAIN] Started parent process monitor for orphaned process prevention")

            # Start health monitor task (deprecated but kept for compatibility)
            _health_monitor_task = asyncio.create_task(_connection_health_monitor())
            logger.info("[MAIN] Started connection health monitor for auto-reconnection")

            try:
                async with _stdio_server() as (read_stream, write_stream):
                    # Run server with shutdown monitoring
                    server_task = asyncio.create_task(server.run(read_stream, write_stream, init_opts))
                    shutdown_task = asyncio.create_task(_shutdown_event.wait())

                    # Wait for either server completion or shutdown signal
                    done, pending = await asyncio.wait(
                        [server_task, shutdown_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )

                    # If shutdown was triggered, cancel server
                    if shutdown_task in done:
                        logger.warning("[MAIN] Shutdown event triggered - cancelling server")
                        server_task.cancel()
                        try:
                            await server_task
                        except asyncio.CancelledError:
                            pass

                    # Cancel pending tasks
                    for task in pending:
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

            finally:
                # Cleanup monitor tasks
                if _stdin_monitor_task and not _stdin_monitor_task.done():
                    _stdin_monitor_task.cancel()
                if _health_monitor_task and not _health_monitor_task.done():
                    _health_monitor_task.cancel()

        asyncio.run(_runner())
    except KeyboardInterrupt:
        logger.info("EX WS Shim interrupted; exiting cleanly")
    except Exception:
        logger.exception("EX WS Shim fatal error during stdio_server")
        sys.exit(1)


if __name__ == "__main__":
    main()
