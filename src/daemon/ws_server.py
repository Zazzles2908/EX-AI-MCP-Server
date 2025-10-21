import asyncio
import json
import logging
import os
import secrets
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

# Semaphore manager imports removed - reverting to original implementation

# Bootstrap logging setup
import sys
_bootstrap_path = Path(__file__).resolve().parents[2]
if str(_bootstrap_path) not in sys.path:
    sys.path.insert(0, str(_bootstrap_path))

from src.bootstrap import setup_logging, get_repo_root, configure_websockets_logging
from src.core.config import get_config

# PHASE 3 (2025-10-18): Import monitoring utilities
from utils.monitoring import record_websocket_event, get_monitor
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-18): Import connection manager and rate limiter for resilience
from src.daemon.connection_manager import get_connection_manager
from src.resilience.rate_limiter import get_rate_limiter

# PHASE 4 (2025-10-19): Import resilient WebSocket manager for connection resilience
from src.monitoring.resilient_websocket import ResilientWebSocketManager

# Week 2 Fix #8 (2025-10-21): Import standardized error handling
from src.daemon.error_handling import (
    ErrorCode,
    create_error_response,
    create_tool_error_response,
    handle_exception,
    log_error,
    ToolNotFoundError,
)

# Week 2 Fix #9 (2025-10-21): Import input validation
from src.daemon.input_validation import (
    validate_tool_arguments,
    ValidationError as InputValidationError,
)

# Code Refactoring (2025-10-21): Import message validators from ws package
from src.daemon.ws.validators import (
    validate_message as _validate_message,
    get_conversation_id_from_arguments as _get_conversation_id_from_arguments,
)

# Code Refactoring (2025-10-21): Import semaphore management from middleware package
from src.daemon.middleware.semaphores import (
    SemaphoreGuard,
    recover_semaphore_leaks as _recover_semaphore_leaks_impl,
    check_semaphore_health as _check_semaphore_health_impl,
)

# Week 3 Fix #15 (2025-10-21): Import extracted WebSocket modules
from src.daemon.ws.connection_manager import (
    serve_connection,
    _safe_send,
    _safe_recv,
)
from src.daemon.ws.request_router import RequestRouter
from src.daemon.ws.session_handler import SessionHandler
from src.daemon.ws.health_monitor import HealthMonitor

# Week 3 Fix #12 (2025-10-21): Import environment variable validation framework
from src.daemon.env_validation import (
    load_and_validate_environment,
    get_env_var,
    CriticalEnvironmentVariableError,
)

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

# Week 3 Fix #12 (2025-10-21): Load and validate environment variables
# This replaces the old pattern of reading env vars without validation
try:
    _validated_env = load_and_validate_environment()
    logger.info("Environment variables validated successfully")
except CriticalEnvironmentVariableError as e:
    logger.error(f"Critical environment variable validation failed: {e}")
    logger.error("Server cannot start with invalid configuration")
    sys.exit(1)

# Week 3 Fix #12 (2025-10-21): Use validated environment variables
# These are now guaranteed to be valid or have safe defaults
EXAI_WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")  # Not validated (non-critical)
EXAI_WS_PORT = _validated_env["EXAI_WS_PORT"]
MAX_MSG_BYTES = _validated_env["EXAI_WS_MAX_BYTES"]

# MESSAGE BUS REMOVED (2025-10-18): Message bus functionality has been completely removed
# to eliminate code bloat and complexity. All payloads are now delivered via WebSocket.


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


# Semaphore guard context manager for guaranteed cleanup
# Code Refactoring (2025-10-21): SemaphoreGuard moved to src/daemon/middleware/semaphores.py
# Imported above as: from src.daemon.middleware.semaphores import SemaphoreGuard


# Atomic cache for thread-safe operations
class AtomicCache:
    """
    Thread-safe cache operations using asyncio.Lock.

    Prevents race conditions in cache access patterns by ensuring
    atomic check-then-update operations.
    """

    def __init__(self):
        self._lock = asyncio.Lock()
        self._cache = {}

    async def get(self, key: str, default=None):
        """Get value from cache atomically."""
        async with self._lock:
            return self._cache.get(key, default)

    async def set(self, key: str, value):
        """Set value in cache atomically."""
        async with self._lock:
            self._cache[key] = value

    async def pop(self, key: str, default=None):
        """Remove and return value from cache atomically."""
        async with self._lock:
            return self._cache.pop(key, default)

    async def contains(self, key: str) -> bool:
        """Check if key exists in cache atomically."""
        async with self._lock:
            return key in self._cache

    async def clear_expired(self, ttl_func):
        """Clear expired entries using provided TTL function."""
        async with self._lock:
            now = time.time()
            expired_keys = [k for k, v in self._cache.items() if ttl_func(v, now)]
            for k in expired_keys:
                self._cache.pop(k, None)
            return len(expired_keys)


# Week 3 Fix #12 (2025-10-21): Use validated auth token
_configured_token = _validated_env.get("EXAI_WS_TOKEN", "")
_auth_token_manager = _TokenManager(_configured_token)

# CRITICAL: Log auth configuration status (for debugging auth issues)
if _configured_token:
    logger.info(f"[AUTH] Authentication enabled (token first 10 chars): {_configured_token[:10]}...")
else:
    logger.warning("[AUTH] Authentication DISABLED (EXAI_WS_TOKEN is empty). "
                   "All connections will be accepted without auth validation. "
                   "Set EXAI_WS_TOKEN in .env file to enable authentication.")

# PHASE 4 (2025-10-19): Updated ping interval to 30s for faster connection timeout detection
# This aligns with ResilientWebSocketManager's 120s connection timeout (4 missed pings)
# Week 3 Fix #12 (2025-10-21): Use validated ping timeout
PING_INTERVAL = int(os.getenv("EXAI_WS_PING_INTERVAL", "30"))  # 30s interval (not validated yet)
PING_TIMEOUT = _validated_env["EXAI_WS_PING_TIMEOUT"]
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
HELLO_TIMEOUT = float(os.getenv("EXAI_WS_HELLO_TIMEOUT", "15"))  # allow slower clients to hello (not validated yet)
# Heartbeat cadence while tools run; keep <10s to satisfy clients with 10s idle cutoff
PROGRESS_INTERVAL = float(os.getenv("EXAI_WS_PROGRESS_INTERVAL_SECS", "8.0"))  # Not validated yet
# Week 3 Fix #12 (2025-10-21): Use validated semaphore limits
SESSION_MAX_INFLIGHT = _validated_env["EXAI_WS_SESSION_MAX_INFLIGHT"]
GLOBAL_MAX_INFLIGHT = _validated_env["EXAI_WS_GLOBAL_MAX_INFLIGHT"]
KIMI_MAX_INFLIGHT = int(os.getenv("EXAI_WS_KIMI_MAX_INFLIGHT", "6"))  # Not validated yet
GLM_MAX_INFLIGHT = int(os.getenv("EXAI_WS_GLM_MAX_INFLIGHT", "4"))  # Not validated yet

# BUG FIX #11 (Phase 2 - 2025-10-20): Per-session semaphore feature flag
# When enabled, uses per-conversation semaphores instead of global semaphore
# This allows concurrent processing of different conversations
# Week 3 Fix #12 (2025-10-21): Use validated boolean flag
USE_PER_SESSION_SEMAPHORES = _validated_env["USE_PER_SESSION_SEMAPHORES"]

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
    """Check if a port is listening. Week 2 Fix #6 (2025-10-21): Centralized timeout."""
    timeout = float(os.getenv("EXAI_PORT_CHECK_TIMEOUT", "0.25"))
    try:
        with socket.create_connection((host, port), timeout=timeout):
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

# Semaphores for concurrency control
_global_sem = asyncio.BoundedSemaphore(GLOBAL_MAX_INFLIGHT)
_provider_sems: dict[str, asyncio.BoundedSemaphore] = {
    "KIMI": asyncio.BoundedSemaphore(KIMI_MAX_INFLIGHT),
    "GLM": asyncio.BoundedSemaphore(GLM_MAX_INFLIGHT),
}

# Atomic cache instances to prevent race conditions
_inflight_cache = AtomicCache()
_inflight_meta_cache = AtomicCache()

# Week 3 Fix #11 (2025-10-21): Lazy initialization for asyncio primitives
# asyncio.Lock and asyncio.Event require a running event loop, so we initialize them lazily
_inflight_lock: Optional[asyncio.Lock] = None
_shutdown: Optional[asyncio.Event] = None

async def _get_inflight_lock() -> asyncio.Lock:
    """Get or create the inflight lock with lazy initialization."""
    global _inflight_lock
    if _inflight_lock is None:
        _inflight_lock = asyncio.Lock()
    return _inflight_lock

async def _get_shutdown_event() -> asyncio.Event:
    """Get or create the shutdown event with lazy initialization."""
    global _shutdown
    if _shutdown is None:
        _shutdown = asyncio.Event()
    return _shutdown

# PHASE 4 (2025-10-19): Initialize resilient WebSocket manager
# This will be initialized in main_async() to use the existing _safe_send as fallback
_resilient_ws: Optional[ResilientWebSocketManager] = None
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


async def _check_and_set_inflight(call_key: str, req_id: str, expires_at: float) -> tuple[bool, Optional[dict]]:
    """Atomically check if call is in-flight and set if not."""
    async with await _get_inflight_lock():
        # Get metadata atomically
        meta = await _inflight_meta_cache.get(call_key)

        # TTL cleanup if needed
        if meta and float(meta.get("expires_at", 0)) <= time.time():
            await _inflight_meta_cache.pop(call_key)
            await _inflight_cache.pop(call_key)
            meta = None

        # Check if already in-flight
        if await _inflight_cache.contains(call_key) and meta:
            return True, meta

        # Set as in-flight
        await _inflight_cache.set(call_key, asyncio.Event())
        await _inflight_meta_cache.set(call_key, {"req_id": req_id, "expires_at": expires_at})
        return False, None


async def _cleanup_inflight(call_key: str) -> None:
    """Atomically clean up inflight tracking."""
    async with await _get_inflight_lock():
        event = await _inflight_cache.pop(call_key)
        if event:
            event.set()
        await _inflight_meta_cache.pop(call_key)


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


# Week 3 Fix #15 (2025-10-21): _safe_recv() moved to src/daemon/ws/connection_manager.py


# Week 3 Fix #15 (2025-10-21): _safe_send() moved to src/daemon/ws/connection_manager.py


# Code Refactoring (2025-10-21): Validation functions moved to src/daemon/ws/validators.py
# - validate_message() -> imported as _validate_message
# - get_conversation_id_from_arguments() -> imported as _get_conversation_id_from_arguments

# Week 3 Fix #15 (2025-10-21): _handle_message() moved to src/daemon/ws/request_router.py
# The function is now part of RequestRouter.handle_message() method







# Week 3 Fix #15 (2025-10-21): _serve_connection() moved to src/daemon/ws/connection_manager.py
# The function is now available as serve_connection() (imported at top of file)



# Week 3 Fix #15 (2025-10-21): Semaphore health functions moved to src/daemon/ws/health_monitor.py
# - _recover_semaphore_leaks() -> HealthMonitor._recover_semaphore_leaks()
# - _check_semaphore_health() -> HealthMonitor._check_semaphore_health()
# - _periodic_semaphore_health() -> HealthMonitor._periodic_semaphore_health()


# Week 3 Fix #15 (2025-10-21): _periodic_session_cleanup() moved to src/daemon/ws/session_handler.py
# The function is now part of SessionHandler.start_periodic_cleanup() method


# Week 3 Fix #15 (2025-10-21): _health_writer() moved to src/daemon/ws/health_monitor.py
# The function is now part of HealthMonitor._health_writer() method


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

    # Week 2 Fix #7 (2025-10-21): Validate timeout configuration at startup
    logger.info("Validating timeout configuration...")
    try:
        from config import TimeoutConfig
        TimeoutConfig.validate_all()
        logger.info("Timeout configuration validated successfully")
    except ValueError as e:
        logger.error(f"FATAL: Invalid timeout configuration: {e}")
        logger.error("Please check your environment variables and fix the configuration")
        return  # Exit - cannot run with invalid timeout configuration

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

    # CRITICAL FIX (2025-10-16): Initialize conversation storage at startup
    # This prevents lazy initialization on every call which adds 300-700ms latency
    logger.info("Initializing conversation storage at daemon startup...")
    try:
        from utils.conversation.storage_factory import initialize_conversation_storage
        initialize_conversation_storage()
        logger.info("Conversation storage initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize conversation storage at startup: {e}", exc_info=True)
        logger.warning("Daemon will start but conversation storage may have degraded performance")

    # BUG FIX #11 (2025-10-20): Pre-warm external connections to reduce first-call latency
    # This establishes Supabase and Redis connections before accepting requests
    logger.info("Pre-warming external connections...")
    try:
        from src.daemon.warmup import warmup_all
        await warmup_all()
        logger.info("External connections pre-warmed successfully")
    except Exception as e:
        logger.error(f"Failed to pre-warm connections: {e}", exc_info=True)
        logger.warning("Daemon will start but first request may have higher latency")

    # BUG FIX #11 (2025-10-20): Initialize conversation queue for async writes
    # This starts the async queue consumer for fire-and-forget conversation updates
    logger.info("Initializing conversation queue...")
    try:
        from src.daemon.conversation_queue import get_conversation_queue
        await get_conversation_queue()
        logger.info("Conversation queue initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize conversation queue: {e}", exc_info=True)
        logger.warning("Daemon will start but conversation writes may be slower")

    # BUG FIX #11 (Phase 2 - 2025-10-20): Initialize session semaphore manager for concurrent processing
    # This enables per-conversation semaphores to allow concurrent EXAI requests
    logger.info("Initializing session semaphore manager...")
    try:
        from src.daemon.session_semaphore_manager import get_session_semaphore_manager
        await get_session_semaphore_manager()
        logger.info("Session semaphore manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize session semaphore manager: {e}", exc_info=True)
        logger.warning("Daemon will start but concurrent requests may block each other")

    # Week 3 Fix #15 (2025-10-21): Initialize extracted WebSocket modules
    logger.info("Initializing WebSocket modules...")

    # Initialize SessionHandler
    session_handler = SessionHandler(session_manager=_sessions)

    # Initialize HealthMonitor
    health_monitor = HealthMonitor(
        health_path=_health_path,
        global_sem=_global_sem,
        provider_sems=_provider_sems,
        session_handler=session_handler,
        server_tools=SERVER_TOOLS,
        host=EXAI_WS_HOST,
        port=EXAI_WS_PORT,
        started_at=STARTED_AT,
        global_max_inflight=GLOBAL_MAX_INFLIGHT,
        provider_max_inflight={"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}
    )

    # Initialize RequestRouter
    request_router = RequestRouter(
        session_manager=_sessions,
        server_tools=SERVER_TOOLS,
        global_sem=_global_sem,
        provider_sems=_provider_sems,
        validated_env=_validated_env,
        use_per_session_semaphores=USE_PER_SESSION_SEMAPHORES
    )

    logger.info("WebSocket modules initialized successfully")

    # CRITICAL FIX (P1): Validate timeout hierarchy on startup
    logger.info("Validating timeout hierarchy...")
    try:
        from config import TimeoutConfig
        tool_timeout = float(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "180"))
        daemon_timeout = TimeoutConfig.get_daemon_timeout()

        if daemon_timeout <= tool_timeout:
            logger.error(f"CRITICAL: Daemon timeout ({daemon_timeout}s) must be greater than tool timeout ({tool_timeout}s)")
            logger.error("This will cause tools to timeout before the daemon can handle them properly.")
            logger.error("Please fix your timeout configuration or update TimeoutConfig.get_daemon_timeout()")
        else:
            ratio = daemon_timeout / tool_timeout
            logger.info(f"Timeout hierarchy validated: daemon={daemon_timeout}s, tool={tool_timeout}s (ratio={ratio:.2f}x)")

            # Warn if ratio is too low
            if ratio < 1.3:
                logger.warning(f"Timeout ratio is low ({ratio:.2f}x). Consider increasing daemon timeout for better reliability.")
    except Exception as e:
        logger.error(f"Failed to validate timeout hierarchy: {e}")

    # Wrapper to handle post-handshake protocol errors gracefully
    async def _connection_wrapper(ws: WebSocketServerProtocol) -> None:
        """
        Wrapper that catches POST-HANDSHAKE protocol errors.
        Handshake errors are suppressed via configure_websockets_logging() in bootstrap.
        This wrapper handles errors that occur AFTER successful WebSocket upgrade.
        """
        try:
            # Week 3 Fix #15 (2025-10-21): Use extracted serve_connection from connection_manager
            await serve_connection(
                ws,
                connection_manager=get_connection_manager(),
                rate_limiter=get_rate_limiter(),
                session_manager=_sessions,
                auth_token_manager=_auth_token_manager,
                message_handler=request_router.handle_message,
                hello_timeout=HELLO_TIMEOUT,
                resilient_ws_manager=_resilient_ws
            )
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

    # PHASE 4 (2025-10-19): Initialize resilient WebSocket manager
    global _resilient_ws
    _resilient_ws = ResilientWebSocketManager(fallback_send=_safe_send)
    await _resilient_ws.start_background_tasks()
    logger.info("[RESILIENT_WS] Started resilient WebSocket manager with background tasks")

    logger.info(f"Starting WS daemon on ws://{EXAI_WS_HOST}:{EXAI_WS_PORT}")
    try:
        async with websockets.serve(
            _connection_wrapper,  # Handles post-handshake protocol errors
            EXAI_WS_HOST,
            EXAI_WS_PORT,
            max_size=MAX_MSG_BYTES,
            ping_interval=PING_INTERVAL,
            ping_timeout=PING_TIMEOUT,
            # Week 3 Fix #12 (2025-10-21): Use validated close timeout
            close_timeout=float(_validated_env["EXAI_WS_CLOSE_TIMEOUT"]),
        ):
            # Week 3 Fix #15 (2025-10-21): Start background tasks using extracted modules
            # Start health monitoring tasks
            health_writer_task, semaphore_health_task = health_monitor.start_monitoring_tasks(stop_event)

            # Start session cleanup task
            session_cleanup_task = asyncio.create_task(session_handler.start_periodic_cleanup(stop_event))

            logger.info("[BACKGROUND_TASKS] Started health monitoring and session cleanup tasks")

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
        # PHASE 4 (2025-10-19): Stop resilient WebSocket manager background tasks
        if _resilient_ws:
            await _resilient_ws.stop_background_tasks()
            logger.info("[RESILIENT_WS] Stopped resilient WebSocket manager")

        _remove_pidfile()
        # Shutdown async logging to flush all messages
        from src.utils.async_logging import shutdown_async_logging
        shutdown_async_logging()


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()

