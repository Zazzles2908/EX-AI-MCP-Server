"""
WebSocket Request Router - Backward Compatibility Wrapper

This module provides backward compatibility for code importing from request_router.py.
All functionality has been refactored into focused modules:
- router_utils.py: Utility functions (normalize_tool_name, normalize_outputs, make_call_key)
- cache_manager.py: Result caching and inflight tracking
- tool_executor.py: Tool execution with semaphore management
- request_router.py: Main message routing logic (this file)

The original request_router.py (1,120 lines) has been split into 4 focused modules.
New code should import directly from the specific modules.

For backwards compatibility, this wrapper re-exports all public APIs.
"""

# Re-export from router_utils.py
from src.daemon.ws.router_utils import (
    normalize_tool_name,
    normalize_outputs,
    make_call_key
)

# Re-export from cache_manager.py
from src.daemon.ws.cache_manager import CacheManager

# Re-export from tool_executor.py
from src.daemon.ws.tool_executor import ToolExecutor

# Import the main RequestRouter class (will be defined below)

# Maintain the original module docstring
__doc__ = """
WebSocket Request Router

Handles message routing, tool execution, caching, and deduplication.

PHASE 3 REFACTORING (2025-11-04):
This module has been refactored into focused components:
- router_utils.py: Utility functions
- cache_manager.py: Result caching
- tool_executor.py: Tool execution
- request_router.py: Main routing logic

For new code, import directly from the specific modules.
"""

# Import all necessary modules for RequestRouter
import asyncio
import logging
from typing import Any, Dict, Optional

from websockets.server import WebSocketServerProtocol

# Import error handling
from src.daemon.error_handling import (
    create_error_response,
    ErrorCode,
    log_error,
)

# Import validation
from src.daemon.input_validation import validate_tool_arguments, ValidationError as InputValidationError

# Import monitoring
from utils.monitoring import record_websocket_event
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-24): Import error capture
from utils.monitoring.error_capture import capture_errors, extract_tool_context

# Import connection manager for _safe_send
from src.daemon.ws.connection_manager import _safe_send

# Import logging utilities
from src.utils.logging_utils import get_logger, SamplingLogger

# Module-specific configuration
import os

_MODULE_LOG_LEVEL = os.getenv("LOG_LEVEL_REQUEST_ROUTER", os.getenv("LOG_LEVEL", "ERROR"))
_MODULE_SAMPLE_RATE = float(os.getenv("LOG_SAMPLE_RATE_REQUEST_ROUTER", "0.05"))

# Create module logger
logger = get_logger(__name__)
logger.setLevel(_MODULE_LOG_LEVEL)

# Sampling logger for high-frequency operations
sampling_logger = SamplingLogger(logger, sample_rate=_MODULE_SAMPLE_RATE)


class RequestRouter:
    """
    Main request router that handles WebSocket message routing.

    Orchestrates:
    - Message validation and routing
    - Tool execution via ToolExecutor
    - Result caching via CacheManager
    - Error handling and responses
    """

    def __init__(
        self,
        session_manager,
        server_tools: Dict[str, Any],
        global_sem: asyncio.Semaphore,
        provider_sems: Dict[str, asyncio.Semaphore],
        validated_env: Dict[str, Any],
        use_per_session_semaphores: bool = False,
        port: int = 8079  # Port for semaphore isolation
    ):
        """
        Initialize request router.

        Args:
            session_manager: Session manager instance
            server_tools: Dictionary of available tools
            global_sem: Global semaphore for concurrency control (port-specific)
            port: WebSocket server port for semaphore isolation
            provider_sems: Provider-specific semaphores
            validated_env: Validated environment variables
            use_per_session_semaphores: Whether to use per-session semaphores
        """
        self.session_manager = session_manager
        self.server_tools = server_tools
        self.validated_env = validated_env
        self.port = port

        # Log port-specific initialization
        logger.info(f"[PORT_ISOLATION] RequestRouter initialized for port {self.port}")

        # Initialize cache manager
        inflight_ttl = int(validated_env.get("INFLIGHT_TTL_SECS", 300))
        result_ttl = int(validated_env.get("RESULT_TTL_SECS", 300))
        self.cache_manager = CacheManager(
            inflight_ttl_secs=inflight_ttl,
            result_ttl_secs=result_ttl
        )

        # Initialize tool executor
        call_timeout = float(validated_env.get("WORKFLOW_TOOL_TIMEOUT_SECS", 300.0))
        progress_interval = float(validated_env.get("PROGRESS_INTERVAL", 5.0))
        self.tool_executor = ToolExecutor(
            server_tools=server_tools,
            global_sem=global_sem,
            provider_sems=provider_sems,
            call_timeout=call_timeout,
            progress_interval=progress_interval,
            use_per_session_semaphores=use_per_session_semaphores
        )

        # Configuration
        self.retry_after_secs = int(validated_env.get("RETRY_AFTER_SECS", 5))

    # Wrap handle_message with error capture
    @capture_errors(
        connection_type="websocket",
        script_name="request_router.py",
        context_extractor=lambda *args, **kwargs: {
            "operation": args[3].get("op") if len(args) > 3 and isinstance(args[3], dict) else kwargs.get("msg", {}).get("op"),
            "session_id": args[2] if len(args) > 2 else kwargs.get("session_id"),
            "request_id": args[3].get("request_id") if len(args) > 3 and isinstance(args[3], dict) else kwargs.get("msg", {}).get("request_id"),
        }
    )
    async def handle_message(
        self,
        ws: WebSocketServerProtocol,
        session_id: str,
        msg: Dict[str, Any],
        resilient_ws_manager=None
    ) -> None:
        """
        Handle a WebSocket message.

        Routes messages to appropriate handlers based on operation type.

        Args:
            ws: WebSocket connection
            session_id: Session ID
            msg: Message dictionary
            resilient_ws_manager: Optional ResilientWebSocketManager instance
        """
        op = msg.get("op")
        req_id = msg.get("request_id", "unknown")

        # Route based on operation
        if op == "tool_call":
            await self._handle_tool_call(ws, session_id, msg, req_id, resilient_ws_manager)
        elif op == "cancel":
            await self._handle_cancel(ws, session_id, msg, req_id, resilient_ws_manager)
        elif op == "ping":
            await self._handle_ping(ws, req_id, resilient_ws_manager)
        elif op == "list_tools":
            await self._handle_list_tools(ws, req_id, resilient_ws_manager)
        else:
            await _safe_send(
                ws,
                create_error_response(
                    req_id,
                    ErrorCode.INVALID_REQUEST,
                    f"Unknown operation: {op}"
                ),
                resilient_ws_manager=resilient_ws_manager
            )

    async def _handle_tool_call(
        self,
        ws: WebSocketServerProtocol,
        session_id: str,
        msg: Dict[str, Any],
        req_id: str,
        resilient_ws_manager=None
    ) -> None:
        """Handle a tool call request."""
        try:
            # Validate message structure
            if "tool" not in msg:
                await _safe_send(
                    ws,
                    create_error_response(req_id, ErrorCode.INVALID_REQUEST, "Missing 'tool' field"),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Extract tool information
            tool_name = msg["tool"].get("name") if isinstance(msg["tool"], dict) else msg.get("tool")
            arguments = msg.get("arguments", {})

            if not tool_name:
                await _safe_send(
                    ws,
                    create_error_response(req_id, ErrorCode.INVALID_REQUEST, "Missing tool name"),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Normalize tool name
            normalized_name = normalize_tool_name(tool_name)

            # Check if tool exists
            if normalized_name not in self.server_tools:
                await _safe_send(
                    ws,
                    create_error_response(req_id, ErrorCode.TOOL_NOT_FOUND, f"Tool not found: {normalized_name}"),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Validate arguments
            try:
                validate_tool_arguments(normalized_name, arguments)
            except InputValidationError as e:
                await _safe_send(
                    ws,
                    create_error_response(req_id, ErrorCode.INVALID_ARGUMENTS, str(e)),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Check cache for duplicate request
            call_key = make_call_key(normalized_name, arguments)
            cached_result = await self.cache_manager.get_cached_result(call_key)
            if cached_result is not None:
                await _safe_send(
                    ws,
                    {
                        "op": "result",
                        "request_id": req_id,
                        "result": cached_result,
                        "from_cache": True
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Check for inflight request
            inflight_future = await self.cache_manager.get_inflight(req_id)
            if inflight_future:
                # Wait for existing request
                try:
                    result = await inflight_future
                    await _safe_send(
                        ws,
                        {
                            "op": "result",
                            "request_id": req_id,
                            "result": result,
                            "from_inflight": True
                        },
                        resilient_ws_manager=resilient_ws_manager
                    )
                    return
                except Exception:
                    # Inflight request failed, continue with new execution
                    pass

            # Create future for this request
            inflight_future = asyncio.Future()
            await self.cache_manager.add_inflight(req_id, inflight_future)

            # Execute tool
            success, outputs, error_msg = await self.tool_executor.execute_tool(
                normalized_name,
                arguments,
                ws,
                req_id,
                resilient_ws_manager
            )

            # Set result in future
            if success:
                inflight_future.set_result(outputs)
                # Cache successful result
                await self.cache_manager.cache_result(call_key, outputs)
            else:
                inflight_future.set_exception(Exception(error_msg or "Unknown error"))

        except Exception as e:
            logger.error(f"Error handling tool call: {e}", exc_info=True)
            await _safe_send(
                ws,
                create_error_response(req_id, ErrorCode.INTERNAL_ERROR, str(e)),
                resilient_ws_manager=resilient_ws_manager
            )

    async def _handle_cancel(
        self,
        ws: WebSocketServerProtocol,
        session_id: str,
        msg: Dict[str, Any],
        req_id: str,
        resilient_ws_manager=None
    ) -> None:
        """Handle a cancellation request."""
        # For now, just acknowledge the cancellation
        await _safe_send(
            ws,
            {
                "op": "cancelled",
                "request_id": req_id,
                "timestamp": log_timestamp()
            },
            resilient_ws_manager=resilient_ws_manager
        )

    async def _handle_ping(
        self,
        ws: WebSocketServerProtocol,
        req_id: str,
        resilient_ws_manager=None
    ) -> None:
        """Handle a ping request."""
        await _safe_send(
            ws,
            {
                "op": "pong",
                "request_id": req_id,
                "timestamp": log_timestamp()
            },
            resilient_ws_manager=resilient_ws_manager
        )

    async def _handle_list_tools(
        self,
        ws: WebSocketServerProtocol,
        req_id: str,
        resilient_ws_manager=None
    ) -> None:
        """Handle a list_tools request."""
        try:
            # Import the server tools registry
            # This needs to be imported dynamically to avoid circular imports
            try:
                from server import SERVER_TOOLS  # type: ignore
            except ImportError:
                # Fallback - try to get from the registry
                try:
                    from src.server.registry_bridge import get_registry
                    reg = get_registry()
                    reg.build()
                    tools_dict = reg.list_tools()
                    # Convert to list format
                    tools_list = []
                    for tool in tools_dict.values():
                        tools_list.append({
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.get_input_schema() if hasattr(tool, 'get_input_schema') else {}
                        })
                except Exception:
                    tools_list = []

                await _safe_send(
                    ws,
                    {
                        "op": "list_tools_res",
                        "request_id": req_id,
                        "tools": tools_list,
                        "timestamp": log_timestamp()
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Convert SERVER_TOOLS to list format
            tools_list = []
            if SERVER_TOOLS:
                for tool in SERVER_TOOLS.values():
                    tools_list.append({
                        "name": tool.get("name", ""),
                        "description": tool.get("description", ""),
                        "inputSchema": tool.get("inputSchema", {"type": "object"})
                    })

            await _safe_send(
                ws,
                {
                    "op": "list_tools_res",
                    "request_id": req_id,
                    "tools": tools_list,
                    "timestamp": log_timestamp()
                },
                resilient_ws_manager=resilient_ws_manager
            )
        except Exception as e:
            logger.error(f"Error in list_tools: {e}", exc_info=True)
            await _safe_send(
                ws,
                create_error_response(
                    req_id,
                    ErrorCode.TOOL_EXECUTION_ERROR,
                    f"Failed to list tools: {str(e)}"
                ),
                resilient_ws_manager=resilient_ws_manager
            )


# Ensure all expected names are available for backward compatibility
__all__ = [
    # Utility functions
    'normalize_tool_name',
    'normalize_outputs',
    'make_call_key',

    # Classes
    'CacheManager',
    'ToolExecutor',
    'RequestRouter',
]

# Maintain the original module structure for any code doing "from src.daemon.ws.request_router import X"
# All re-exported items above will be available
