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

# Import protocol adapter for dual protocol support
from src.daemon.ws.protocol_adapter import ProtocolAdapter

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
        port: int = 8079,  # Port for semaphore isolation
        provider_registry=None  # Provider registry for ProtocolAdapter
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
            provider_registry: ProviderRegistry instance for ProtocolAdapter
        """
        self.session_manager = session_manager
        self.server_tools = server_tools
        self.validated_env = validated_env
        self.port = port
        self.provider_registry = provider_registry

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

        # Initialize protocol adapter for dual protocol support
        self.protocol_adapter = ProtocolAdapter(self.tool_executor, provider_registry)

        # Configuration
        self.retry_after_secs = int(validated_env.get("RETRY_AFTER_SECS", 5))

    def _find_tool_by_name(self, name: str):
        """
        Find a tool by name, handling both dict and list formats.

        Args:
            name: Tool name to find

        Returns:
            Tool dict/object if found, None otherwise
        """
        if not self.server_tools:
            return None

        # Handle dict format
        if isinstance(self.server_tools, dict):
            return self.server_tools.get(name)

        # Handle list format
        if isinstance(self.server_tools, list):
            for tool in self.server_tools:
                if isinstance(tool, dict):
                    if tool.get('name') == name:
                        return tool
                else:
                    if getattr(tool, 'name', None) == name:
                        return tool

        return None

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

        Routes messages to appropriate handlers based on protocol type.

        Args:
            ws: WebSocket connection
            session_id: Session ID
            msg: Message dictionary
            resilient_ws_manager: Optional ResilientWebSocketManager instance
        """
        # Detect protocol type
        if "jsonrpc" in msg and msg.get("jsonrpc") == "2.0":
            # MCP JSON-RPC protocol - route to ProtocolAdapter
            logger.debug(f"[ROUTER] Detected MCP JSON-RPC protocol for message: {msg.get('method', 'unknown')}")
            try:
                await self.protocol_adapter.handle_message(msg, ws)
            except Exception as e:
                logger.error(f"[ROUTER] Error handling MCP message: {e}", exc_info=True)
                await _safe_send(
                    ws,
                    create_error_response(
                        ErrorCode.INTERNAL_ERROR,
                        f"MCP message handling failed: {str(e)}",
                        request_id=msg.get("id", "unknown")
                    ),
                    resilient_ws_manager=resilient_ws_manager
                )
        elif "op" in msg:
            # EXAI custom protocol - handle as before
            op = msg.get("op")
            req_id = msg.get("request_id", "unknown")

            logger.debug(f"[ROUTER] Detected EXAI custom protocol for operation: {op}")

            # Route based on operation
            if op in ("tool_call", "call_tool"):
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
                        ErrorCode.INVALID_REQUEST,
                        f"Unknown operation: {op}",
                        request_id=req_id
                    ),
                    resilient_ws_manager=resilient_ws_manager
                )
        else:
            # Unknown message format
            await _safe_send(
                ws,
                create_error_response(
                    ErrorCode.INVALID_REQUEST,
                    "Unknown message format - must have 'op' (EXAI) or 'jsonrpc' (MCP) field"
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
            # Handle both "tool" and "name" formats (for backward compatibility)
            tool_name = None
            if "tool" in msg:
                # Standard format: {"op": "tool_call", "tool": {"name": "..."}, "arguments": {...}}
                tool_name = msg["tool"].get("name") if isinstance(msg["tool"], dict) else msg.get("tool")
            elif "name" in msg:
                # Alternative format: {"op": "call_tool", "name": "...", "arguments": {...}}
                tool_name = msg.get("name")
            else:
                await _safe_send(
                    ws,
                    create_error_response(ErrorCode.INVALID_REQUEST, "Missing 'tool' or 'name' field", request_id=req_id),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            arguments = msg.get("arguments", {})

            if not tool_name:
                await _safe_send(
                    ws,
                    create_error_response(ErrorCode.INVALID_REQUEST, "Missing tool name", request_id=req_id),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Normalize tool name
            normalized_name = normalize_tool_name(tool_name)

            # Check if tool exists (handle both dict and list formats)
            tool = self._find_tool_by_name(normalized_name)
            if tool is None:
                await _safe_send(
                    ws,
                    create_error_response(ErrorCode.TOOL_NOT_FOUND, f"Tool not found: {normalized_name}", request_id=req_id),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Validate arguments
            try:
                validate_tool_arguments(normalized_name, arguments)
            except InputValidationError as e:
                await _safe_send(
                    ws,
                    create_error_response(ErrorCode.INVALID_ARGUMENTS, str(e), request_id=req_id),
                    resilient_ws_manager=resilient_ws_manager
                )
                return

            # Check cache for duplicate request
            call_key = make_call_key(normalized_name, arguments)
            cached_result = await self.cache_manager.get_cached_result(call_key)
            logger.info(f"[DEBUG_CACHE] Cache check for {call_key}: cached_result={cached_result is not None}")
            if cached_result is not None:
                logger.info(f"[DEBUG_CACHE] Sending cached result, type={type(cached_result)}")
                await _safe_send(
                    ws,
                    {
                        "op": "call_tool_res",  # CRITICAL FIX (2025-11-04): Changed from "result" to "call_tool_res"
                        "request_id": req_id,
                        "outputs": cached_result,  # Changed from "result" to "outputs"
                        "from_cache": True
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
                logger.info(f"[DEBUG_CACHE] Cached result sent")
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
                            "op": "call_tool_res",  # CRITICAL FIX (2025-11-04): Changed from "result" to "call_tool_res"
                            "request_id": req_id,
                            "outputs": result,  # Changed from "result" to "outputs"
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

            logger.info(f"[DEBUG_ROUTER] About to call execute_tool for {normalized_name}")
            # Execute tool
            try:
                logger.info(f"[DEBUG_ROUTER] About to await execute_tool...")
                success, outputs, error_msg = await asyncio.wait_for(
                    self.tool_executor.execute_tool(
                        normalized_name,
                        arguments,
                        ws,
                        req_id,
                        resilient_ws_manager
                    ),
                    timeout=30.0
                )
                logger.info(f"[DEBUG_ROUTER] execute_tool returned: success={success}, outputs_type={type(outputs)}, error_msg={error_msg}")
            except asyncio.TimeoutError:
                logger.error(f"[DEBUG_ROUTER] execute_tool TIMED OUT after 30s")
                raise
            except Exception as e:
                logger.error(f"[DEBUG_ROUTER] Exception during execute_tool: {type(e).__name__}: {e}", exc_info=True)
                raise

            # Set result in future and send response
            if success:
                inflight_future.set_result(outputs)
                # Cache successful result
                await self.cache_manager.cache_result(call_key, outputs)
                # Send successful response to client
                logger.info(f"[DEBUG_SEND] About to send result for {req_id}, outputs type: {type(outputs)}, len: {len(outputs) if isinstance(outputs, list) else 'N/A'}")
                send_success = await _safe_send(
                    ws,
                    {
                        "op": "call_tool_res",  # CRITICAL FIX (2025-11-04): Changed from "result" to "call_tool_res" to match shim expectation
                        "request_id": req_id,
                        "outputs": outputs  # Changed from "result" to "outputs" to match protocol
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
                logger.info(f"[DEBUG_SEND] Send result for {req_id}: success={send_success}")
            else:
                inflight_future.set_exception(Exception(error_msg or "Unknown error"))
                # Send error response to client
                await _safe_send(
                    ws,
                    create_error_response(ErrorCode.INTERNAL_ERROR, error_msg or "Unknown error", request_id=req_id),
                    resilient_ws_manager=resilient_ws_manager
                )

        except Exception as e:
            logger.error(f"Error handling tool call: {e}", exc_info=True)
            await _safe_send(
                ws,
                create_error_response(ErrorCode.INTERNAL_ERROR, str(e), request_id=req_id),
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
        import logging
        logger = logging.getLogger("src.daemon.ws.request_router")
        logger.info(f"[LIST_TOOLS] Handling list_tools request, req_id={req_id}")

        try:
            # Import the server tools registry
            # This needs to be imported dynamically to avoid circular imports
            try:
                logger.info(f"[LIST_TOOLS] Attempting to import SERVER_TOOLS from src.server...")
                from src.server import SERVER_TOOLS  # type: ignore
                logger.info(f"[LIST_TOOLS] Successfully imported SERVER_TOOLS, type={type(SERVER_TOOLS)}, len={len(SERVER_TOOLS) if SERVER_TOOLS else 'N/A'}")
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
                        # Skip tools with empty or invalid names
                        tool_name = getattr(tool, 'name', '')
                        if not tool_name or not isinstance(tool_name, str) or not tool_name.strip():
                            logger.warning(f"[LIST_TOOLS] Skipping tool with invalid/empty name from registry: {tool_name!r}")
                            continue
                        tools_list.append({
                            "name": tool_name,
                            "description": getattr(tool, 'description', ''),
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
            if self.server_tools:
                # Handle both dict and list formats
                tools_iterable = self.server_tools.values() if isinstance(self.server_tools, dict) else self.server_tools

                for tool in tools_iterable:
                    # Tool can be a dict or an object with attributes
                    if isinstance(tool, dict):
                        name = tool.get('name', '')
                    else:
                        name = getattr(tool, 'name', '')

                    # Skip tools with empty or invalid names (prevents "String should have at least 1 character" errors)
                    if not name or not isinstance(name, str) or not name.strip():
                        logger.warning(f"[LIST_TOOLS] Skipping tool with invalid/empty name: {name!r}")
                        continue

                    # Get description
                    if isinstance(tool, dict):
                        description = tool.get('description', '')
                        input_schema = tool.get('inputSchema', {})
                    else:
                        description = getattr(tool, 'description', '')
                        # Get input schema - might be an attribute or method
                        input_schema = getattr(tool, 'inputSchema', None)
                        if input_schema is None:
                            # Try to get via method
                            input_schema = getattr(tool, 'get_input_schema', lambda: {"type": "object"})()

                    tools_list.append({
                        "name": name,
                        "description": description,
                        "inputSchema": input_schema
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
                    ErrorCode.TOOL_EXECUTION_ERROR,
                    f"Failed to list tools: {str(e)}",
                    request_id=req_id
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
