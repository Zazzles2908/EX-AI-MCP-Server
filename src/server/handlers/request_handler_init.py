"""
Request Handler Initialization Module

This module contains all initialization logic for the request handler including:
- Environment setup and configuration
- Import management (lazy imports to avoid circular dependencies)
- Tool registry building
- Request ID generation
- Shared utility functions
"""

import logging
import os
import uuid as _uuid
from typing import Any, Dict, Optional

# Core imports
from mcp.types import TextContent
from config import DEFAULT_MODEL

# Progress tracking
from utils.progress import start_progress_capture, get_progress_log

# Lazy imports to avoid circular dependencies
server = None  # type: ignore

# Optional provider configuration
try:
    from src.server.providers import configure_providers  # type: ignore
except Exception:
    def configure_providers():  # type: ignore
        return None

# ToolOutput for error normalization and file-size checks
try:
    from tools.models import ToolOutput
except Exception:
    ToolOutput = None  # type: ignore

# Environment flags and test override shims
THINK_ROUTING_ENABLED = os.getenv("THINK_ROUTING_ENABLED", "true").strip().lower() == "true"
_resolve_auto_model = None  # monkeypatchable by tests
_os = os  # alias used in legacy code paths

# Logger
logger = logging.getLogger(__name__)

# Local env helpers to avoid coupling to server module
try:
    from server import _env_true as _server_env_true  # type: ignore
    from server import _hot_reload_env as _server_hot_reload_env  # type: ignore
    _env_true = _server_env_true  # type: ignore
    _hot_reload_env = _server_hot_reload_env  # type: ignore
except Exception:  # pragma: no cover - safe fallback
    def _env_true(key: str, default: str = "false") -> bool:  # type: ignore
        try:
            import os as _os
            return (_os.getenv(key, default) or "").strip().lower() in {"1", "true", "yes", "on"}
        except Exception:
            return False
    
    def _hot_reload_env() -> None:  # type: ignore
        pass

# Provider configuration guard
try:
    from server import _ensure_providers_configured as _ensure_providers_configured  # type: ignore
except Exception:  # pragma: no cover
    def _ensure_providers_configured() -> None:  # type: ignore
        pass


def generate_request_id() -> str:
    """Generate a unique request ID for tracking."""
    return str(_uuid.uuid4())


def build_tool_registry() -> Dict[str, Any]:
    """
    Build dynamic tool registry and return active tool map.
    
    Returns:
        Dictionary mapping tool names to tool objects
    """
    try:
        from src.server.registry_bridge import get_registry as _get_reg  # type: ignore
        _reg = _get_reg()
        _reg.build()
        return _reg.list_tools()
    except Exception:
        return {}


def setup_monitoring_config() -> Dict[str, Any]:
    """
    Load watchdog and timeout configuration from environment.
    
    Returns:
        Dictionary with monitoring configuration
    """
    config = {}
    
    # Watchdog configuration
    try:
        config['watchdog_enabled'] = _env_true("WATCHDOG_ENABLED", "false")
        config['watchdog_timeout'] = int(os.getenv("WATCHDOG_TIMEOUT", "300"))
        config['heartbeat_interval'] = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
    except Exception:
        config['watchdog_enabled'] = False
        config['watchdog_timeout'] = 300
        config['heartbeat_interval'] = 30
    
    return config


def initialize_request(name: str, arguments: Dict[str, Any]) -> tuple[str, Dict[str, Any], Dict[str, Any]]:
    """
    Initialize request with ID, tool map, and monitoring configuration.
    
    Args:
        name: Tool name
        arguments: Tool arguments
        
    Returns:
        Tuple of (request_id, tool_map, monitoring_config)
    """
    # Ensure providers are configured
    try:
        _ensure_providers_configured()
    except Exception:
        pass
    
    # Generate request ID
    req_id = generate_request_id()
    
    # Log request
    logger.info(f"MCP tool call: {name} req_id={req_id}")
    logger.debug(f"MCP tool arguments: {list(arguments.keys())} req_id={req_id}")
    
    # Build tool registry
    tool_map = build_tool_registry()
    
    # Setup monitoring
    monitoring_config = setup_monitoring_config()
    monitoring_config['req_id'] = req_id
    
    # Log to activity file
    try:
        mcp_activity_logger = logging.getLogger("mcp_activity")
        if getattr(mcp_activity_logger, "disabled", False) and _env_true("ACTIVITY_LOG", "true"):
            mcp_activity_logger.disabled = False
        mcp_activity_logger.info(f"TOOL_CALL: {name} with {len(arguments)} arguments req_id={req_id}")
    except Exception:
        pass
    
    # Initialize JSONL event tracking
    try:
        from utils.tool_events import ToolCallEvent as __Evt, ToolEventSink as __Sink
        _ex_mirror = _env_true("EX_MIRROR_ACTIVITY_TO_JSONL", "false")
        _evt = __Evt(provider="boundary", tool_name=name, args={"arg_count": len(arguments), "req_id": req_id})
        _sink = __Sink()
        
        # Record continuation_id early for telemetry if present
        if _evt:
            _cid = arguments.get("continuation_id")
            if _cid:
                _evt.metadata["continuation_id"] = _cid
        
        monitoring_config['event'] = _evt
        monitoring_config['sink'] = _sink
        monitoring_config['ex_mirror'] = _ex_mirror
    except Exception:
        monitoring_config['event'] = None
        monitoring_config['sink'] = None
        monitoring_config['ex_mirror'] = False
    
    return req_id, tool_map, monitoring_config


# Export public API
__all__ = [
    'THINK_ROUTING_ENABLED',
    'DEFAULT_MODEL',
    'ToolOutput',
    'logger',
    '_env_true',
    '_hot_reload_env',
    '_ensure_providers_configured',
    '_resolve_auto_model',
    '_os',
    'generate_request_id',
    'build_tool_registry',
    'setup_monitoring_config',
    'initialize_request',
]

