import asyncio
import json
import logging
import os
import signal
import time
import uuid
from datetime import timedelta
from pathlib import Path
import socket

from typing import Any, Dict, List, Optional

import websockets
# Note: Using generic type hint instead of deprecated WebSocketServerProtocol
# The websockets library deprecated WebSocketServerProtocol in favor of the new asyncio API
# For backward compatibility with the legacy API, we use Any for type hints
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from websockets.legacy.server import WebSocketServerProtocol
else:
    WebSocketServerProtocol = Any

from .session_manager import SessionManager

# Bootstrap logging setup
import sys
_bootstrap_path = Path(__file__).resolve().parents[2]
if str(_bootstrap_path) not in sys.path:
    sys.path.insert(0, str(_bootstrap_path))

from src.bootstrap import setup_logging, get_repo_root, configure_websockets_logging
from src.core.config import get_config
from src.core.message_bus_client import MessageBusClient

LOG_DIR = get_repo_root() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# CRITICAL FIX: Setup async-safe logging to prevent deadlocks in async contexts
# Python's standard logging uses thread locks that can deadlock in async code
from src.utils.async_logging import setup_async_safe_logging
_log_listener = setup_async_safe_logging(level=logging.INFO)

# Setup logging with UTF-8 support for Windows consoles
logger = setup_logging("ws_daemon", log_file=str(LOG_DIR / "ws_daemon.log"))

# Suppress websockets library handshake noise (port scanners, health checks)
configure_websockets_logging()

# NOTE: Environment is already loaded by bootstrap.load_env() in run_ws_daemon.py
# No need to load .env again here - it's already loaded before this module is imported

EXAI_WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))  # CRITICAL FIX: Changed default from 8765 to 8079
MAX_MSG_BYTES = int(os.getenv("EXAI_WS_MAX_BYTES", str(32 * 1024 * 1024)))

# Initialize message bus client (lazy initialization, won't crash if config invalid)
_message_bus_client: Optional[MessageBusClient] = None

def _get_message_bus_client() -> Optional[MessageBusClient]:
    """Get or initialize the message bus client."""
    global _message_bus_client
    if _message_bus_client is None:
        try:
            config = get_config()
            if config.message_bus_enabled:
                _message_bus_client = MessageBusClient()
                logger.info("Message bus client initialized successfully")
            else:
                logger.info("Message bus disabled in configuration")
        except Exception as e:
            logger.error(f"Failed to initialize message bus client: {e}")
            logger.warning("Message bus will not be available")
    return _message_bus_client


# Thread-safe token manager for secure token rotation with audit logging
class _TokenManager:
    """Thread-safe authentication token manager with audit logging."""

    def __init__(self, initial_token: str = ""):
        self._lock = asyncio.Lock()
        self._token = initial_token

    async def get(self) -> str:
        """Get current authentication token."""
        async with self._lock:
            return self._token

    async def rotate(self, old_token: str, new_token: str) -> bool:
        """
        Rotate authentication token with validation and audit logging.

        Args:
            old_token: Current token for validation
            new_token: New token to set

        Returns:
            True if rotation successful, False if old_token doesn't match
        """
        async with self._lock:
            if self._token and old_token != self._token:
                logger.warning(f"[SECURITY] Token rotation failed: invalid old token")
                return False
            self._token = new_token
            logger.info(f"[SECURITY] Authentication token rotated successfully")
            return True


# Initialize auth token manager with validation
_configured_token = os.getenv("EXAI_WS_TOKEN", "")
_auth_token_manager = _TokenManager(_configured_token)

# CRITICAL: Log auth configuration status (for debugging auth issues)
if _configured_token:
    logger.info(f"[AUTH] Authentication enabled (token first 10 chars): {_configured_token[:10]}...")
else:
    logger.warning("[AUTH] Authentication DISABLED (EXAI_WS_TOKEN is empty). "
                   "All connections will be accepted without auth validation. "
                   "Set EXAI_WS_TOKEN in .env file to enable authentication.")

PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "45"))  # wider interval to reduce false timeouts
PING_TIMEOUT = int(os.getenv("EXAI_WS_PING_TIMEOUT", "30"))    # allow slower systems to respond to pings
# WS-level hard ceiling for a single tool invocation; keep small to avoid client-perceived hangs

# ============================================================================
# SINGLETON TOOL REGISTRY (Mission 2: One authoritative tool list)
# ============================================================================
# CRITICAL: Import TOOLS from server.py to ensure both entry points share the
# same dict object reference. server.py initializes TOOLS via bootstrap.singletons
# which ensures idempotent initialization.
#
# Identity check: assert server.TOOLS is ws_server.SERVER_TOOLS  # Same object!
#
# This replaces the previous pattern where ws_server.py might build its own
# tool registry, causing divergence between stdio and WebSocket transports.

from server import TOOLS as SERVER_TOOLS  # type: ignore
from server import _ensure_providers_configured  # type: ignore
from server import handle_call_tool as SERVER_HANDLE_CALL_TOOL  # type: ignore
from server import register_provider_specific_tools  # type: ignore

from src.providers.registry import ModelProviderRegistry  # type: ignore
from src.providers.base import ProviderType  # type: ignore

# Import TimeoutConfig for coordinated timeout hierarchy
from config import TimeoutConfig

CALL_TIMEOUT = TimeoutConfig.get_daemon_timeout()  # Auto-calculated: 1.5x workflow tool timeout (default: 180s)
HELLO_TIMEOUT = float(os.getenv("EXAI_WS_HELLO_TIMEOUT", "15"))  # allow slower clients to hello
# Heartbeat cadence while tools run; keep <10s to satisfy clients with 10s idle cutoff
PROGRESS_INTERVAL = float(os.getenv("EXAI_WS_PROGRESS_INTERVAL_SECS", "8.0"))
SESSION_MAX_INFLIGHT = int(os.getenv("EXAI_WS_SESSION_MAX_INFLIGHT", "8"))
GLOBAL_MAX_INFLIGHT = int(os.getenv("EXAI_WS_GLOBAL_MAX_INFLIGHT", "24"))
KIMI_MAX_INFLIGHT = int(os.getenv("EXAI_WS_KIMI_MAX_INFLIGHT", "6"))
GLM_MAX_INFLIGHT = int(os.getenv("EXAI_WS_GLM_MAX_INFLIGHT", "4"))

# ============================================================================
# OBSERVABILITY FILES (Mission 4: Document JSONL vs JSON intent)
# ============================================================================
# JSONL (append-only time-series): Metrics are appended for historical analysis
_metrics_path = LOG_DIR / "ws_daemon.metrics.jsonl"

# JSON (overwrite snapshot): Health is overwritten for current status checks
_health_path = LOG_DIR / "ws_daemon.health.json"

PID_FILE = LOG_DIR / "ws_daemon.pid"
STARTED_AT: float | None = None


def _create_pidfile() -> bool:
    """Create an exclusive PID file. Returns True if created, False if already exists.
    If a stale file exists (e.g., after a crash), we leave it in place for now and
    rely on bind attempt and health probe to decide how to proceed.
    """
    try:
        # Exclusive create
        with open(PID_FILE, "x", encoding="utf-8") as f:
            f.write(str(os.getpid()))
        return True
    except FileExistsError:
        return False
    except Exception:
        # Do not fail daemon start purely due to pidfile problems
        return True


def _remove_pidfile() -> None:
    try:
        if PID_FILE.exists():
            PID_FILE.unlink(missing_ok=True)  # type: ignore[arg-type]
    except (OSError, PermissionError) as e:
        logger.warning(f"Failed to remove PID file {PID_FILE}: {e}")
        # Continue - stale PID file is not critical for operation

def _is_port_listening(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.25):
            return True
    except Exception:
        return False


def _is_health_fresh(max_age_s: float = 20.0) -> bool:
    try:
        if not _health_path.exists():
            return False
        data = json.loads(_health_path.read_text(encoding="utf-8"))
        t = float(data.get("t") or 0)
        return (time.time() - t) <= max_age_s
    except Exception:
        return False

_sessions = SessionManager()
_global_sem = asyncio.BoundedSemaphore(GLOBAL_MAX_INFLIGHT)
_provider_sems: dict[str, asyncio.BoundedSemaphore] = {
    "KIMI": asyncio.BoundedSemaphore(KIMI_MAX_INFLIGHT),
    "GLM": asyncio.BoundedSemaphore(GLM_MAX_INFLIGHT),
}
# Track in-flight calls by semantic call key so duplicate calls can await the same result
_inflight_by_key: dict[str, asyncio.Event] = {}
# Track inflight request metadata for fast-fail duplicate responses and TTL cleanup
_inflight_meta_by_key: dict[str, dict] = {}
# Lock to protect concurrent access to _inflight_by_key and _inflight_meta_by_key
_inflight_lock = asyncio.Lock()

_shutdown = asyncio.Event()
RESULT_TTL_SECS = int(os.getenv("EXAI_WS_RESULT_TTL", "600"))
# TTL for inflight entries (seconds) — default to CALL_TIMEOUT so we don't hold keys longer than the daemon's ceiling
INFLIGHT_TTL_SECS = int(os.getenv("EXAI_WS_INFLIGHT_TTL_SECS", str(CALL_TIMEOUT)))
# Retry-after hint for capacity responses (seconds)
RETRY_AFTER_SECS = int(os.getenv("EXAI_WS_RETRY_AFTER_SECS", "1"))
_results_cache: dict[str, dict] = {}
# Cache by semantic call key (tool name + normalized arguments) to survive req_id changes across reconnects
_results_cache_by_key: dict[str, dict] = {}
_inflight_reqs: set[str] = set()


def _gc_results_cache() -> None:
    try:
        now = time.time()
        expired = [rid for rid, rec in _results_cache.items() if now - rec.get("t", 0) > RESULT_TTL_SECS]
        for rid in expired:
            _results_cache.pop(rid, None)
        expired_keys = [k for k, rec in _results_cache_by_key.items() if now - rec.get("t", 0) > RESULT_TTL_SECS]
        for k in expired_keys:
            _results_cache_by_key.pop(k, None)
    except (KeyError, AttributeError, TypeError) as e:
        logger.error(f"Failed to clean up results cache: {e}", exc_info=True)
        # Continue - cache cleanup failure is not critical for current request


def _store_result(req_id: str, payload: dict) -> None:
    _results_cache[req_id] = {"t": time.time(), "payload": payload}
    _gc_results_cache()


def _get_cached_result(req_id: str) -> dict | None:
    rec = _results_cache.get(req_id)
    if not rec:
        return None
    if time.time() - rec.get("t", 0) > RESULT_TTL_SECS:
        _results_cache.pop(req_id, None)
        return None
    return rec.get("payload")


def _make_call_key(name: str, arguments: dict) -> str:
    try:
        # Stable JSON key for arguments (already JSON-serializable from client)
        key_obj = {"name": name, "arguments": arguments}
        return json.dumps(key_obj, sort_keys=True, separators=(",", ":"))
    except Exception:
        # Fallback: best-effort string
        return f"{name}:{str(arguments)}"


def _store_result_by_key(call_key: str, outputs: list[dict]) -> None:
    _results_cache_by_key[call_key] = {"t": time.time(), "outputs": outputs}
    _gc_results_cache()


def _get_cached_by_key(call_key: str) -> list[dict] | None:
    rec = _results_cache_by_key.get(call_key)
    if not rec:
        return None
    if time.time() - rec.get("t", 0) > RESULT_TTL_SECS:
        _results_cache_by_key.pop(call_key, None)
        return None
    return rec.get("outputs")


# Tool name normalization to tolerate IDE-side aliasing (e.g., chat_EXAI-WS -> chat)
def _normalize_tool_name(name: str) -> str:
    """
    Normalize tool names by stripping common suffixes.

    This handles MCP client-side aliasing where tools may be suffixed with
    _EXAI-WS, -EXAI-WS, _EXAI_WS, or -EXAI_WS.

    Examples:
        chat_EXAI-WS -> chat
        analyze_EXAI-WS -> analyze
        kimi_chat_with_tools_EXAI-WS -> kimi_chat_with_tools
    """
    try:
        # Generic suffix-stripping for all EXAI-WS variants
        # This automatically handles all tools without hardcoded aliases
        for suf in ("_EXAI-WS", "-EXAI-WS", "_EXAI_WS", "-EXAI_WS"):
            if name.endswith(suf):
                return name[: -len(suf)]
    except (AttributeError, TypeError) as e:
        logger.warning(f"Failed to normalize tool name '{name}': {e}")
        # Return original name - normalization is cosmetic
    return name



def _normalize_outputs(outputs: List[Any]) -> List[Dict[str, Any]]:
    norm: List[Dict[str, Any]] = []
    for o in outputs or []:
        try:
            # mcp.types.TextContent has attributes type/text
            t = getattr(o, "type", None) or (o.get("type") if isinstance(o, dict) else None)
            if t == "text":
                text = getattr(o, "text", None) or (o.get("text") if isinstance(o, dict) else None)
                norm.append({"type": "text", "text": text or ""})
            else:
                # Fallback: best-effort stringification
                norm.append({"type": "text", "text": str(o)})
        except Exception:
            norm.append({"type": "text", "text": str(o)})
    return norm


async def _safe_recv(ws: WebSocketServerProtocol, timeout: float):
    try:
        return await asyncio.wait_for(ws.recv(), timeout=timeout)
    except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
        return None
    except asyncio.TimeoutError:
        return None


async def _safe_send(ws: WebSocketServerProtocol, payload: dict) -> bool:
    """Best-effort send that swallows disconnects and logs at debug level.

    Returns False if the connection is closed or an error occurred, True on success.
    """
    try:
        await ws.send(json.dumps(payload))
        return True
    except (
        websockets.exceptions.ConnectionClosedOK,
        websockets.exceptions.ConnectionClosedError,
        ConnectionAbortedError,
        ConnectionResetError,
    ):
        # Normal disconnect during send; treat as benign
        logger.debug("_safe_send: connection closed while sending %s", payload.get("op"))
        return False
    except Exception as e:
        logger.debug("_safe_send: unexpected send error: %s", e)
        return False


def _validate_message(msg: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate WebSocket message structure and required fields.

    Provides defense-in-depth validation to complement protocol-level size limits.
    Checks message structure, operation validity, and field types.

    Args:
        msg: Parsed JSON message from client

    Returns:
        (is_valid, error_message) - error_message is None if valid
    """
    if not isinstance(msg, dict):
        return (False, "message must be a JSON object")

    op = msg.get("op")
    if not isinstance(op, str):
        return (False, "missing or invalid 'op' field (must be string)")

    # Validate operation-specific required fields
    if op == "call_tool":
        name = msg.get("name")
        if not isinstance(name, str) or not name:
            return (False, "call_tool requires 'name' (non-empty string)")

        req_id = msg.get("request_id")
        if req_id is not None and not isinstance(req_id, str):
            return (False, "request_id must be a string")

        arguments = msg.get("arguments")
        if arguments is not None and not isinstance(arguments, dict):
            return (False, "arguments must be a JSON object")

    elif op == "rotate_token":
        old = msg.get("old")
        new = msg.get("new")
        if not isinstance(old, str) or not isinstance(new, str):
            return (False, "rotate_token requires 'old' and 'new' (strings)")

    elif op not in ("list_tools", "health", "hello"):
        # Unknown operation - allow it to be handled by existing code path
        # which will send {"op": "error", "message": f"Unknown op: {op}"}
        pass

    return (True, None)


async def _handle_message(ws: WebSocketServerProtocol, session_id: str, msg: Dict[str, Any]) -> None:
    op = msg.get("op")
    if op == "list_tools":
        # NOTE: Providers are configured at daemon startup (see main_async())
        # No need to call _ensure_providers_configured() here - it's already done
        # Build a minimal tool descriptor set
        tools = []
        for name, tool in SERVER_TOOLS.items():
            try:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.get_input_schema(),
                })
            except Exception as e:
                logger.warning(f"Failed to get full schema for tool '{name}': {e}")
                # Fallback to minimal descriptor
                tools.append({"name": name, "description": getattr(tool, "description", name), "inputSchema": {"type": "object"}})
        await _safe_send(ws, {"op": "list_tools_res", "tools": tools})
        return

    if op == "call_tool":
        orig_name = msg.get("name")
        name = _normalize_tool_name(orig_name)
        arguments = msg.get("arguments") or {}
        req_id = msg.get("request_id")

        # CRITICAL FIX: Add comprehensive logging for tool calls
        logger.info(f"=== TOOL CALL RECEIVED ===")
        logger.info(f"Session: {session_id}")
        logger.info(f"Tool: {name} (original: {orig_name})")
        logger.info(f"Request ID: {req_id}")
        try:
            args_preview = json.dumps(arguments, indent=2)[:500]
            logger.info(f"Arguments (first 500 chars): {args_preview}")
        except Exception as e:
            logger.warning(f"Failed to serialize arguments for logging: {e}")
            # Continue - logging failure should not block execution
            logger.info(f"Arguments: <unable to serialize>")
        logger.info(f"=== PROCESSING ===")

        # NOTE: Providers are configured at daemon startup (see main_async())
        # No need to call _ensure_providers_configured() here - it's already done
        # This prevents deadlock when called in async context
        tool = SERVER_TOOLS.get(name)
        if not tool:
            await _safe_send(ws, {
                "op": "call_tool_res",
                "request_id": req_id,
                "error": {"code": "TOOL_NOT_FOUND", "message": f"Unknown tool: {orig_name}"}
            })
            return

        # Determine provider gate based on requested model or defaults
        prov_key = ""
        try:
            model_name = (arguments or {}).get("model")
            if not model_name:
                from config import DEFAULT_MODEL as _DEF_MODEL  # type: ignore
                model_name = _DEF_MODEL
            if model_name:
                # Check which provider advertises this model
                if model_name in set(ModelProviderRegistry.get_available_model_names(provider_type=ProviderType.KIMI)):
                    prov_key = "KIMI"
                elif model_name in set(ModelProviderRegistry.get_available_model_names(provider_type=ProviderType.GLM)):
                    prov_key = "GLM"
        except Exception as e:
            logger.warning(f"Failed to detect provider for tool '{name}': {e}")
            # Continue with empty provider key - metrics may be less accurate
            prov_key = ""

        # Backpressure: try acquire global, provider and per-session slots without waiting
        # Fast-path duplicate handling: if client retries with same req_id, serve result or inform inflight
        cached = _get_cached_result(req_id)
        if cached:
            await _safe_send(ws, cached)
            return
        # Semantic de-duplication: if client reconnects and reissues the same call with a new req_id, serve cached outputs
        # Build a call_key that includes model and provider to reduce collisions across providers/models
        try:
            _args_for_key = dict(arguments)
        except Exception as e:
            logger.warning(f"Failed to convert arguments to dict for call_key (type: {type(arguments)}): {e}")
            # Fallback to original arguments or empty dict
            _args_for_key = arguments or {}
        # Include provider hint explicitly (may be empty if unknown)
        if prov_key:
            _args_for_key["__prov"] = prov_key
        # Ensure model field is present for keying (if omitted by client, default model may be used)
        if "model" not in _args_for_key and (arguments or {}).get("model"):
            _args_for_key["model"] = arguments.get("model")
        call_key = _make_call_key(name, _args_for_key)
        # Optional: disable semantic coalescing per tool via env EXAI_WS_DISABLE_COALESCE_FOR_TOOLS
        try:
            _disable_set = {s.strip().lower() for s in os.getenv("EXAI_WS_DISABLE_COALESCE_FOR_TOOLS", "").split(",") if s.strip()}
        except Exception as e:
            logger.error(f"Failed to parse EXAI_WS_DISABLE_COALESCE_FOR_TOOLS env variable: {e}")
            # Continue with empty set - coalescing will work normally
            _disable_set = set()
        if name.lower() in _disable_set:
            # Make call_key unique to avoid coalescing for this tool
            call_key = f"{call_key}::{uuid.uuid4()}"
        cached_outputs = _get_cached_by_key(call_key)
        if cached_outputs is not None:
            payload = {"op": "call_tool_res", "request_id": req_id, "outputs": cached_outputs}
            await _safe_send(ws, payload)
            _store_result(req_id, payload)
            return
        if req_id in _inflight_reqs:
            await _safe_send(ws, {"op": "progress", "request_id": req_id, "name": name, "t": time.time(), "note": "duplicate request; still processing"})
            return

        # Coalesce duplicate semantic calls across reconnects: if another call with the same call_key is in-flight,
        # fast-fail duplicates immediately with a 409-style response including the original request_id.
        now_ts = time.time()
        async with _inflight_lock:
            try:
                meta = _inflight_meta_by_key.get(call_key)
                # TTL cleanup: drop stale inflight entries
                if meta and float(meta.get("expires_at", 0)) <= now_ts:
                    _inflight_meta_by_key.pop(call_key, None)
                    _inflight_by_key.pop(call_key, None)
                    meta = None
            except Exception as e:
                logger.error(f"Failed to retrieve inflight metadata for call_key '{call_key}': {e}", exc_info=True)
                # Continue without metadata - duplicate detection may not work for this call
                meta = None
            if call_key in _inflight_by_key and meta:
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "error": {"code": "DUPLICATE", "message": "duplicate call in flight", "original_request_id": meta.get("req_id")}
                })
                return
            else:
                _inflight_by_key[call_key] = asyncio.Event()
                _inflight_meta_by_key[call_key] = {"req_id": req_id, "expires_at": now_ts + float(INFLIGHT_TTL_SECS)}


        try:
            await asyncio.wait_for(_global_sem.acquire(), timeout=0.001)
        except asyncio.TimeoutError:
            await _safe_send(ws, {
                "op": "call_tool_res",
                "request_id": req_id,
                "error": {"code": "OVER_CAPACITY", "message": "Global concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
            })
            return
        # Defer ACK until after provider+session capacity to ensure a single ACK per request
        # Also emit an immediate progress breadcrumb so clients see activity right away
        await _safe_send(ws, {
            "op": "progress",
            "request_id": req_id,
            "name": name,
            "t": time.time(),
            "note": "accepted, awaiting provider/session capacity"
        })

        prov_acquired = False
        if prov_key and prov_key in _provider_sems:
            try:
                await asyncio.wait_for(_provider_sems[prov_key].acquire(), timeout=0.001)
                prov_acquired = True
            except asyncio.TimeoutError:
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "error": {"code": "OVER_CAPACITY", "message": f"{prov_key} concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
                })
                _global_sem.release()
                return
            # Defer ACK; will send once after session acquisition to guarantee a single ACK

        acquired_session = False
        try:
            try:
                await asyncio.wait_for((await _sessions.get(session_id)).sem.acquire(), timeout=0.001)  # type: ignore
                acquired_session = True
            except asyncio.TimeoutError:
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "error": {"code": "OVER_CAPACITY", "message": "Session concurrency limit reached; retry soon", "retry_after": RETRY_AFTER_SECS}
                })
                try:
                    _global_sem.release()
                except Exception as e:
                    logger.error(f"Failed to release global semaphore (over capacity path): {e}", exc_info=True)
                    # Continue - semaphore state may be corrupted but don't block response
                return
            start = time.time()
            # Single ACK after global+provider+session acquisition
            await _safe_send(ws, {
                "op": "call_tool_ack",
                "request_id": req_id,
                "accepted": True,
                "timeout": CALL_TIMEOUT,
                "name": name,
            })

            # Inject session and call_key into arguments for provider-side idempotency and context cache
            try:
                arguments = dict(arguments)
                arguments.setdefault("_session_id", session_id)
                arguments.setdefault("_call_key", call_key)
            except (TypeError, AttributeError) as e:
                logger.warning(f"Failed to inject session metadata into arguments: {e}")
                # Continue with original arguments - tracking will be incomplete but tool can still execute

            _inflight_reqs.add(req_id)
            try:
                # Emit periodic progress while tool runs
                # Compute a hard deadline for this tool invocation
                tool_timeout = CALL_TIMEOUT
                try:
                    if name == "kimi_chat_with_tools":
                        # Short timeout for normal chat; longer for web-enabled runs
                        _kimitt = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_SECS", "180"))
                        _kimiweb = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS", "300"))
                        # arguments is a dict we pass into the tool below; check websearch flag if present
                        use_web = False
                        try:
                            use_web = bool(arguments.get("use_websearch"))
                        except (AttributeError, TypeError, KeyError):
                            use_web = False
                        if use_web:
                            # For web-enabled calls, allow the higher web timeout explicitly
                            tool_timeout = int(_kimiweb)
                        else:
                            tool_timeout = min(tool_timeout, int(_kimitt))
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(f"Failed to calculate Kimi-specific timeout: {e}, using default")
                    # tool_timeout already set to default value above
                deadline = start + float(tool_timeout)


                # REMOVED: Auto model override that broke agentic routing for continuations
                # The model resolution logic in request_handler_model_resolution.py
                # already handles "auto" correctly for all cases including continuations
                # No need to override here at WS boundary

                tool_task = asyncio.create_task(SERVER_HANDLE_CALL_TOOL(name, arguments))
                while True:
                    try:
                        outputs = await asyncio.wait_for(tool_task, timeout=PROGRESS_INTERVAL)
                        break
                    except asyncio.TimeoutError:
                        # Heartbeat progress to client
                        await _safe_send(ws, {
                            "op": "progress",
                            "request_id": req_id,
                            "name": name,
                            "t": time.time(),
                        })
                        # Enforce hard deadline
                        if time.time() >= deadline:
                            try:
                                tool_task.cancel()
                            except Exception as e:
                                logger.warning(f"Failed to cancel tool task for '{name}' (req_id: {req_id}): {e}")
                                # Continue - task may complete anyway
                            await _safe_send(ws, {
                                "op": "call_tool_res",
                                "request_id": req_id,
                                "error": {"code": "TIMEOUT", "message": f"call_tool exceeded {tool_timeout}s"}
                            })
                            try:
                                async with _inflight_lock:
                                    if call_key in _inflight_by_key:
                                        _inflight_by_key[call_key].set()
                                        _inflight_by_key.pop(call_key, None)
                                    _inflight_meta_by_key.pop(call_key, None)
                            except Exception as e:
                                logger.error(f"Failed to clean up inflight tracking after timeout (call_key: {call_key}): {e}", exc_info=True)
                                # Continue - cleanup failure may cause memory leak but don't block response
                            return
                latency = time.time() - start

                # Record performance metrics
                try:
                    from utils.infrastructure.performance_metrics import record_tool_call
                    record_tool_call(name, success=True, latency_ms=latency * 1000)
                except Exception:
                    pass  # Don't fail if metrics unavailable

                # CRITICAL FIX: Log successful tool completion
                logger.info(f"=== TOOL CALL COMPLETE ===")
                logger.info(f"Tool: {name}")
                logger.info(f"Duration: {latency:.2f}s")
                logger.info(f"Provider: {prov_key or 'unknown'}")
                logger.info(f"Session: {session_id}")
                logger.info(f"Request ID: {req_id}")
                logger.info(f"Success: True")
                logger.info(f"=== END ===")

                try:
                    with _metrics_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "t": time.time(), "op": "call_tool", "lat": latency,
                            "sess": session_id, "name": name, "prov": prov_key or ""
                        }) + "\n")
                except (OSError, PermissionError, IOError) as e:
                    logger.error(f"Failed to write JSONL metrics: {e}")
                    # Continue - metrics logging failure should not block response
                outputs_norm = _normalize_outputs(outputs)
                # Payload delivery guard: ensure a first non-empty block if enabled
                try:
                    if (not outputs_norm) and os.getenv("EX_ENSURE_NONEMPTY_FIRST", "false").strip().lower() == "true":
                        diag = {
                            "status": "no_payload_from_tool",
                            "diagnostic_stub": True,
                            "tool": name,
                            "session": session_id,
                            "ts": time.time(),
                        }
                        outputs_norm = [{"type": "text", "text": json.dumps(diag, separators=(",", ":"))}]
                except Exception as e:
                    logger.warning(f"Failed to create diagnostic stub for empty payload (tool: {name}): {e}")
                    # Continue - diagnostic stub is optional, empty outputs will be handled below

                # Ensure at least one text block for UI surfacing even if tool returned no outputs
                if not outputs_norm:
                    outputs_norm = [{"type": "text", "text": ""}]

                # MESSAGE BUS INTEGRATION: Check if payload should be stored in message bus
                message_bus_used = False
                try:
                    message_bus_client = _get_message_bus_client()
                    if message_bus_client is not None:
                        # Calculate payload size
                        payload_json = json.dumps({"outputs": outputs_norm})
                        payload_size = len(payload_json.encode('utf-8'))

                        # Check if should use message bus (>1MB threshold)
                        if message_bus_client.should_use_message_bus(payload_size):
                            # Generate transaction ID
                            transaction_id = f"txn_{uuid.uuid4().hex}"

                            # Store in message bus
                            logger.info(f"Storing large payload in message bus: {payload_size} bytes, txn={transaction_id}")
                            success = await message_bus_client.store_message(
                                transaction_id=transaction_id,
                                session_id=session_id,
                                tool_name=name,
                                provider_name=prov_key or "unknown",
                                payload={"outputs": outputs_norm},
                                metadata={
                                    "request_id": req_id,
                                    "timestamp": time.time(),
                                    "payload_size_bytes": payload_size
                                }
                            )

                            if success:
                                # Replace outputs with transaction ID reference
                                logger.info(f"Message bus storage successful, returning transaction ID")
                                outputs_norm = [{
                                    "type": "text",
                                    "text": json.dumps({
                                        "message_bus_transaction_id": transaction_id,
                                        "payload_size_bytes": payload_size,
                                        "retrieval_required": True,
                                        "session_id": session_id,
                                        "tool_name": name
                                    }, separators=(",", ":"))
                                }]
                                message_bus_used = True
                            else:
                                # Circuit breaker opened, fallback to WebSocket
                                logger.warning(f"Message bus storage failed (circuit breaker), using WebSocket fallback")
                        else:
                            logger.debug(f"Payload size {payload_size} bytes below threshold, using WebSocket")
                except Exception as e:
                    logger.error(f"Message bus integration error: {e}", exc_info=True)
                    logger.warning("Falling back to WebSocket delivery")
                    # Continue with original outputs_norm

                # Detect serialized ToolOutput error-style payloads and surface via error channel
                error_obj = None
                try:
                    for o in outputs_norm:
                        if isinstance(o, dict) and isinstance(o.get("text"), str):
                            t = o.get("text", "").strip()
                            if t.startswith("{") and t.endswith("}"):
                                import json as _json
                                parsed = _json.loads(t)
                                status = str(parsed.get("status", "")).lower()
                                if status in {"code_too_large", "error", "execution_error", "resend_prompt"}:
                                    error_obj = {
                                        "code": status.upper(),
                                        "message": parsed.get("content") or parsed.get("error") or "Request rejected by preflight validation",
                                        "metadata": parsed.get("metadata") or {}
                                    }
                                    break
                except Exception as e:
                    logger.debug(f"Failed to parse error object from tool output (tool: {name}): {e}")
                    # Continue - error object parsing is optional, tool output will be sent as-is
                    error_obj = None

                result_payload = {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "outputs": outputs_norm,
                }
                if error_obj:
                    result_payload["error"] = error_obj

                # Optional compatibility: include a top-level 'text' field concatenating output texts
                try:
                    if os.getenv("EXAI_WS_COMPAT_TEXT", "true").strip().lower() == "true":
                        texts = [o.get("text", "") for o in outputs_norm if isinstance(o, dict)]
                        result_payload["text"] = "\n\n".join([t for t in texts if t])
                except Exception as e:
                    logger.debug(f"Failed to create compatibility text field (tool: {name}): {e}")
                    # Continue - compatibility field is optional

                await _safe_send(ws, result_payload)
                _store_result(req_id, result_payload)
                # Store by semantic call key to allow delivery across reconnects with new req_id
                try:
                    _store_result_by_key(call_key, outputs_norm)
                    # Signal any duplicate waiters on this call_key
                    async with _inflight_lock:
                        if call_key in _inflight_by_key:
                            _inflight_by_key[call_key].set()
                            _inflight_by_key.pop(call_key, None)
                        _inflight_meta_by_key.pop(call_key, None)
                except Exception as e:
                    logger.error(f"Failed to clean up inflight tracking after success (call_key: {call_key}): {e}", exc_info=True)
                    # Continue - cleanup failure may cause memory leak but response already sent
            except asyncio.TimeoutError:
                # CRITICAL FIX: Log timeout errors
                latency_timeout = time.time() - start

                # Record performance metrics
                try:
                    from utils.infrastructure.performance_metrics import record_tool_call
                    record_tool_call(name, success=False, latency_ms=latency_timeout * 1000, error_type="TimeoutError")
                except Exception:
                    pass  # Don't fail if metrics unavailable

                logger.error(f"=== TOOL CALL TIMEOUT ===")
                logger.error(f"Tool: {name}")
                logger.error(f"Duration: {latency_timeout:.2f}s")
                logger.error(f"Timeout Limit: {CALL_TIMEOUT}s")
                logger.error(f"Session: {session_id}")
                logger.error(f"Request ID: {req_id}")
                logger.error(f"=== END ===")

                # Log to failures file
                try:
                    failures_path = _metrics_path.parent / "tool_failures.jsonl"
                    with failures_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "t": time.time(),
                            "tool": name,
                            "error": f"TIMEOUT after {CALL_TIMEOUT}s",
                            "duration": latency_timeout,
                            "session": session_id,
                            "request_id": req_id
                        }) + "\n")
                except Exception as e:
                    logger.warning(f"Failed to write timeout to failures log (tool: {name}): {e}")
                    # Continue - failure logging is not critical

                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "error": {"code": "TIMEOUT", "message": f"call_tool exceeded {CALL_TIMEOUT}s"}
                })
                try:
                    async with _inflight_lock:
                        if call_key in _inflight_by_key:
                            _inflight_by_key[call_key].set()
                            _inflight_by_key.pop(call_key, None)
                        _inflight_meta_by_key.pop(call_key, None)
                except Exception as e:
                    logger.error(f"Failed to clean up inflight tracking after timeout (call_key: {call_key}): {e}", exc_info=True)
                    # Continue - cleanup failure may cause memory leak but error response already sent
            except Exception as e:
                # CRITICAL FIX: Log tool execution errors
                latency_error = time.time() - start

                # Record performance metrics
                try:
                    from utils.infrastructure.performance_metrics import record_tool_call
                    error_type = type(e).__name__
                    record_tool_call(name, success=False, latency_ms=latency_error * 1000, error_type=error_type)
                except Exception:
                    pass  # Don't fail if metrics unavailable

                logger.error(f"=== TOOL CALL FAILED ===")
                logger.error(f"Tool: {name}")
                logger.error(f"Duration: {latency_error:.2f}s")
                logger.error(f"Session: {session_id}")
                logger.error(f"Request ID: {req_id}")
                logger.error(f"Error: {str(e)}")
                logger.exception(f"Full traceback:")
                logger.error(f"=== END ===")

                # Log to failures file
                try:
                    failures_path = _metrics_path.parent / "tool_failures.jsonl"
                    with failures_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps({
                            "t": time.time(),
                            "tool": name,
                            "error": str(e),
                            "duration": latency_error,
                            "session": session_id,
                            "request_id": req_id
                        }) + "\n")
                except Exception as e2:
                    logger.warning(f"Failed to write error to failures log (tool: {name}): {e2}")
                    # Continue - failure logging is not critical

                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "error": {"code": "EXEC_ERROR", "message": str(e)}
                })
                try:
                    async with _inflight_lock:
                        if call_key in _inflight_by_key:
                            _inflight_by_key[call_key].set()
                            _inflight_by_key.pop(call_key, None)
                        _inflight_meta_by_key.pop(call_key, None)
                except Exception as e2:
                    logger.error(f"Failed to clean up inflight tracking after error (call_key: {call_key}): {e2}", exc_info=True)
                    # Continue - cleanup failure may cause memory leak but error response already sent
        finally:
            if acquired_session:
                try:
                    (await _sessions.get(session_id)).sem.release()  # type: ignore
                except Exception as e:
                    logger.error(f"Failed to release session semaphore (session: {session_id}): {e}", exc_info=True)
                    # Continue - semaphore state may be corrupted but don't block cleanup
            if prov_acquired:
                try:
                    _provider_sems[prov_key].release()
                except Exception as e:
                    logger.error(f"Failed to release provider semaphore (provider: {prov_key}): {e}", exc_info=True)
                    # Continue - semaphore state may be corrupted but don't block cleanup
            try:
                _global_sem.release()
            except Exception as e:
                logger.error(f"Failed to release global semaphore: {e}", exc_info=True)
                # Continue - semaphore state may be corrupted but don't block cleanup
        return

    if op == "rotate_token":
        old = msg.get("old") or ""
        new = msg.get("new") or ""
        if not old or not new:
            await _safe_send(ws, {"op": "rotate_token_res", "ok": False, "error": "missing_params"})
            return
        # Use thread-safe token manager with audit logging
        success = await _auth_token_manager.rotate(old, new)
        if not success:
            await _safe_send(ws, {"op": "rotate_token_res", "ok": False, "error": "unauthorized"})
            return
        await _safe_send(ws, {"op": "rotate_token_res", "ok": True})
        return

    if op == "health":
        # Snapshot basic health (Mission 4: Add tool_count for divergence detection)
        try:
            sess_ids = await _sessions.list_ids()
        except Exception as e:
            logger.warning(f"Failed to list session IDs for health check: {e}")
            # Continue with empty list - health check will show 0 sessions
            sess_ids = []
        uptime_seconds = int(time.time() - STARTED_AT) if STARTED_AT else 0
        snapshot = {
            "t": time.time(),
            "uptime_human": str(timedelta(seconds=uptime_seconds)),
            "sessions": len(sess_ids),
            "global_capacity": GLOBAL_MAX_INFLIGHT,
            "tool_count": len(SERVER_TOOLS),  # Mission 4: Detect tool list divergence
        }
        await _safe_send(ws, {"op": "health_res", "ok": True, "health": snapshot})
        return

    # Unknown op
    await _safe_send(ws, {"op": "error", "message": f"Unknown op: {op}"})





async def _serve_connection(ws: WebSocketServerProtocol) -> None:
    # Log connection source for debugging
    try:
        client_ip, client_port = ws.remote_address if hasattr(ws, 'remote_address') else ("unknown", 0)
        logger.info(f"[WS_CONNECTION] New connection from {client_ip}:{client_port}")
    except Exception as e:
        logger.debug(f"[WS_CONNECTION] Could not get remote address: {e}")
        client_ip, client_port = "unknown", 0

    # Expect hello first with timeout, handle abrupt client disconnects gracefully
    hello_raw = await _safe_recv(ws, timeout=HELLO_TIMEOUT)
    if not hello_raw:
        # Client connected but did not send hello or disconnected; close quietly
        # This is common for health checks, port scanners, or misconfigured clients
        logger.debug(f"[WS_CONNECTION] No hello received from {client_ip}:{client_port} (likely health check or scanner)")
        try:
            await ws.close(code=4002, reason="hello timeout or disconnect")
        except Exception as e:
            logger.debug(f"Failed to close connection after hello timeout: {e}")
            # Continue - connection may already be closed
        return


    try:
        hello = json.loads(hello_raw)
    except Exception as e:
        logger.warning(f"Failed to parse hello message: {e}")
        try:
            await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "invalid_hello"})
            try:
                await ws.close(code=4000, reason="invalid hello")
            except Exception as e2:
                logger.debug(f"Failed to close connection after invalid hello: {e2}")
                # Continue - connection may already be closed
        except Exception as e2:
            logger.debug(f"Failed to send hello_ack error: {e2}")
            # Continue - connection may already be closed
        return

    if hello.get("op") != "hello":
        logger.warning(f"Client sent message without hello op: {hello.get('op')}")
        try:
            await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "missing_hello"})
            try:
                await ws.close(code=4001, reason="missing hello")
            except Exception as e:
                logger.debug(f"Failed to close connection after missing hello: {e}")
                # Continue - connection may already be closed
        except Exception as e:
            logger.debug(f"Failed to send missing_hello error: {e}")
            # Continue - connection may already be closed
        return

    token = hello.get("token", "")
    current_auth_token = await _auth_token_manager.get()
    if current_auth_token and token != current_auth_token:
        # Enhanced logging for auth debugging (show first 10 chars only for security)
        expected_preview = current_auth_token[:10] + "..." if len(current_auth_token) > 10 else current_auth_token
        received_preview = token[:10] + "..." if len(token) > 10 else (token if token else "<empty>")
        logger.warning(f"[AUTH] Client sent invalid auth token. "
                       f"Expected: {expected_preview}, Received: {received_preview}")
        try:
            await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "unauthorized"})
            try:
                await ws.close(code=4003, reason="unauthorized")
            except Exception as e:
                logger.debug(f"Failed to close connection after unauthorized: {e}")
                # Continue - connection may already be closed
        except Exception as e:
            logger.debug(f"Failed to send unauthorized error: {e}")
            # Continue - connection may already be closed
        return

    # Always assign a fresh daemon-side session id for isolation
    session_id = str(uuid.uuid4())
    sess = await _sessions.ensure(session_id)
    try:
        ok = await _safe_send(ws, {"op": "hello_ack", "ok": True, "session_id": sess.session_id})
        if not ok:
            return
    except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
        # Client closed during hello ack; just return
        return

    try:
        async for raw in ws:
            try:
                msg = json.loads(raw)
            except Exception as e:
                logger.warning(f"Failed to parse JSON message from client (session: {sess.session_id}): {e}")
                # Try to inform client; ignore if already closed
                try:
                    await _safe_send(ws, {"op": "error", "message": "invalid_json"})
                except Exception as e2:
                    logger.debug(f"Failed to send invalid_json error: {e2}")
                    # Continue - connection may already be closed
                continue

            # Validate message structure before processing
            is_valid, error_msg = _validate_message(msg)
            if not is_valid:
                logger.warning(f"Invalid message structure from client (session: {sess.session_id}): {error_msg}")
                try:
                    await _safe_send(ws, {"op": "error", "message": f"invalid_message: {error_msg}"})
                except Exception as e:
                    logger.debug(f"Failed to send invalid_message error: {e}")
                    # Continue - connection may already be closed
                continue

            try:
                await _handle_message(ws, sess.session_id, msg)
            except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
                # Client disconnected mid-processing; exit loop
                break
    except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
        # Iterator may raise on abrupt close; treat as normal disconnect
        pass
    finally:
        try:
            await _sessions.remove(sess.session_id)
        except Exception as e:
            logger.warning(f"Failed to remove session {sess.session_id}: {e}")
            # Continue - session cleanup failure is not critical


async def _health_writer(stop_event: asyncio.Event) -> None:
    """
    Health writer task that updates health file every 10 seconds.

    CRITICAL FIX (P0): Added timeout to prevent indefinite blocking on session list.
    If session manager lock is held for >2s, use empty list to keep health file fresh.
    """
    last_successful_write = time.time()

    while not stop_event.is_set():
        try:
            # CRITICAL FIX: Add timeout to prevent indefinite blocking on session lock
            # If lock is held for >2s, fall back to empty list to keep health file updating
            try:
                sess_ids = await asyncio.wait_for(_sessions.list_ids(), timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Health writer timeout getting session IDs (lock held >2s), using empty list")
                sess_ids = []
            except Exception as e:
                logger.debug(f"Failed to list session IDs for health writer: {e}")
                # Continue with empty list - health file will show 0 sessions
                sess_ids = []

            # Approximate inflight via semaphore value
            try:
                inflight_global = GLOBAL_MAX_INFLIGHT - _global_sem._value  # type: ignore[attr-defined]
            except Exception as e:
                logger.debug(f"Failed to get global semaphore value for health writer: {e}")
                # Continue with None - health file will show null for inflight
                inflight_global = None

            uptime_seconds = int(time.time() - STARTED_AT) if STARTED_AT else 0
            snapshot = {
                "t": time.time(),
                "pid": os.getpid(),
                "host": EXAI_WS_HOST,
                "port": EXAI_WS_PORT,
                "started_at": STARTED_AT,
                "uptime_human": str(timedelta(seconds=uptime_seconds)),
                "sessions": len(sess_ids),
                "global_capacity": GLOBAL_MAX_INFLIGHT,
                "global_inflight": inflight_global,
                "tool_count": len(SERVER_TOOLS),  # Mission 4: Detect tool list divergence
            }

            try:
                _health_path.write_text(json.dumps(snapshot, sort_keys=True, indent=2), encoding="utf-8")
                last_successful_write = time.time()
            except Exception as e:
                logger.warning(f"Failed to write health file: {e}")
                # Continue - health file write failure is not critical

            # CRITICAL FIX: Monitor health writer staleness
            time_since_write = time.time() - last_successful_write
            if time_since_write > 30:
                logger.critical(
                    f"Health writer failed for {int(time_since_write)}s - daemon may be stuck. "
                    "This indicates a serious issue with the event loop or blocking operations."
                )

        except Exception as e:
            logger.error(f"Health writer error: {e}", exc_info=True)
            # Continue running even on errors to keep health file updating

        try:
            await asyncio.wait_for(stop_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            continue


async def main_async() -> None:
    global STARTED_AT
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _signal(*_args):
        stop_event.set()

    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, _signal)
        except NotImplementedError:
            # Windows may not support signal handlers in some environments
            pass

    # Best-effort single-instance guard with stale lock auto-clear
    if not _create_pidfile():
        # If PID file exists but no one is listening OR health is stale, clear it
        if (not _is_port_listening(EXAI_WS_HOST, EXAI_WS_PORT)) or (not _is_health_fresh()):
            logger.warning("Stale PID file or no active listener detected; removing %s", PID_FILE)
            _remove_pidfile()
            if not _create_pidfile():
                logger.error("Unable to recreate PID file after clearing stale lock. Exiting.")
                return
        else:
            logger.warning(
                "PID file exists at %s - another WS daemon may already be running. If you recently crashed or rebooted, "
                "verify with logs/ws_daemon.health.json or check port %s. Exiting.",
                PID_FILE,
                EXAI_WS_PORT,
            )
            return

    STARTED_AT = time.time()

    # CRITICAL FIX: Configure providers and register tools at startup (not per-request)
    # This prevents deadlock when _ensure_providers_configured() is called in async context
    logger.info("Configuring providers and registering tools at daemon startup...")
    try:
        _ensure_providers_configured()
        register_provider_specific_tools()
        logger.info(f"Providers configured successfully. Total tools available: {len(SERVER_TOOLS)}")
    except Exception as e:
        logger.error(f"Failed to configure providers at startup: {e}", exc_info=True)
        logger.warning("Daemon will start but provider-specific tools may not be available")

    # Wrapper to handle post-handshake protocol errors gracefully
    async def _connection_wrapper(ws: WebSocketServerProtocol) -> None:
        """
        Wrapper that catches POST-HANDSHAKE protocol errors.
        Handshake errors are suppressed via configure_websockets_logging() in bootstrap.
        This wrapper handles errors that occur AFTER successful WebSocket upgrade.
        """
        try:
            await _serve_connection(ws)
        except websockets.exceptions.InvalidMessage as e:
            # Post-handshake protocol violation (invalid WebSocket frames)
            try:
                client_ip, client_port = ws.remote_address if hasattr(ws, 'remote_address') else ("unknown", 0)
                logger.debug(f"[WS_PROTOCOL] Invalid WebSocket frame from {client_ip}:{client_port}: {e}")
            except Exception:
                logger.debug(f"[WS_PROTOCOL] Invalid WebSocket frame: {e}")
        except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError) as e:
            # Client disconnected unexpectedly
            logger.debug(f"[WS_DISCONNECT] Client disconnected: {type(e).__name__}")
        except Exception as e:
            # Unexpected error - log at warning level
            try:
                client_ip, client_port = ws.remote_address if hasattr(ws, 'remote_address') else ("unknown", 0)
                logger.warning(f"[WS_ERROR] Unexpected error handling connection from {client_ip}:{client_port}: {e}")
            except Exception:
                logger.warning(f"[WS_ERROR] Unexpected error handling connection: {e}")

    logger.info(f"Starting WS daemon on ws://{EXAI_WS_HOST}:{EXAI_WS_PORT}")
    try:
        async with websockets.serve(
            _connection_wrapper,  # Handles post-handshake protocol errors
            EXAI_WS_HOST,
            EXAI_WS_PORT,
            max_size=MAX_MSG_BYTES,
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
            close_timeout=1.0,
        ):
            # Start health writer
            asyncio.create_task(_health_writer(stop_event))
            # Wait indefinitely until a signal or external shutdown sets the event
            await stop_event.wait()
    except OSError as e:
        # Friendly message on address-in-use
        if getattr(e, "errno", None) in (98, 10048):  # 98=EADDRINUSE (POSIX), 10048=WSAEADDRINUSE (Windows)
            logger.error(
                "Address already in use: ws://%s:%s. A daemon is likely already running. "
                "Use scripts/run_ws_shim.py to connect, or stop the existing daemon. See logs/mcp_server.log and logs/ws_daemon.health.json.",
                EXAI_WS_HOST,
                EXAI_WS_PORT,
            )
            return
        raise
    finally:
        _remove_pidfile()
        # Shutdown async logging to flush all messages
        from src.utils.async_logging import shutdown_async_logging
        shutdown_async_logging()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

