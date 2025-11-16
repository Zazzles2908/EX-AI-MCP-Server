"""
Tool Executor

Handles tool execution with semaphore management and progress updates.
Provides concurrency control, timeout handling, and streaming support.

This is part of the Phase 3 refactoring that split the large request_router.py
into focused modules:
- router_utils.py: Utility functions
- cache_manager.py: Result caching and inflight tracking
- tool_executor.py: Tool execution with semaphore management (this file)
- request_router.py: Main message routing logic
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Tuple

from websockets.server import WebSocketServerProtocol

# Import connection manager for _safe_send
from src.daemon.ws.connection_manager import _safe_send

# Import middleware
from src.daemon.middleware.semaphores import SemaphoreGuard
from src.daemon.error_handling import ToolNotFoundError

# Import utilities
from utils.monitoring import record_websocket_event
from utils.timezone_helper import log_timestamp
from utils.infrastructure.semantic_cache import get_semantic_cache

from src.daemon.error_handling import ToolExecutionError, ErrorCode, log_error

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Handles tool execution with semaphore management and progress updates.

    Provides:
    - Tool execution with timeout
    - Semaphore-based concurrency control
    - Progress updates during long-running operations
    - Error handling and recovery
    - Semantic caching for AI-powered tools
    """

    def __init__(
        self,
        server_tools: Dict[str, Any],
        global_sem: asyncio.Semaphore,
        provider_sems: Dict[str, asyncio.Semaphore],
        call_timeout: float,
        progress_interval: float,
        use_per_session_semaphores: bool = False
    ):
        """
        Initialize tool executor.

        Args:
            server_tools: Dictionary of available tools
            global_sem: Global semaphore for concurrency control
            provider_sems: Provider-specific semaphores
            call_timeout: Timeout for tool calls (seconds)
            progress_interval: Interval for progress updates (seconds)
            use_per_session_semaphores: Whether to use per-session semaphores
        """
        self.server_tools = server_tools
        self.global_sem = global_sem
        self.provider_sems = provider_sems
        self.call_timeout = call_timeout
        self.progress_interval = progress_interval
        self.use_per_session_semaphores = use_per_session_semaphores

        # Initialize semantic cache
        try:
            self.semantic_cache = get_semantic_cache()
            logger.info("[SEMANTIC_CACHE] Initialized semantic cache")
        except Exception as e:
            log_error(ErrorCode.INTERNAL_ERROR, f"Failed to initialize cache: {e}", exc_info=True)
            self.semantic_cache = None

    def _should_cache_tool(self, tool_name: str) -> bool:
        """
        Determine if a tool should use semantic caching.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool should be cached, False otherwise
        """
        # Cache only tools that call AI providers
        cacheable_tools = {
            'chat', 'analyze', 'codereview', 'debug', 'thinkdeep',
            'testgen', 'refactor', 'planner', 'docgen', 'secaudit',
            'tracer', 'consensus', 'precommit'
        }
        return tool_name in cacheable_tools

    def _should_cache_request(self, arguments: Dict[str, Any]) -> bool:
        """
        Determine if a specific request should be cached.

        Args:
            arguments: Tool arguments

        Returns:
            True if request should be cached, False otherwise
        """
        # Don't cache continuation requests
        session_id = arguments.get('session_id')
        if session_id is not None:
            return False
        return True

    def _extract_cache_params(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract cache parameters from tool arguments.

        Args:
            arguments: Tool arguments

        Returns:
            Dictionary with cache parameters
        """
        # Extract prompt for semantic caching
        # Different tools use different parameter names for prompts
        prompt = (
            arguments.get('prompt') or
            arguments.get('question') or
            arguments.get('task') or
            str(arguments)
        )

        # Extract other relevant parameters
        params = {
            'prompt': prompt,
            'model': arguments.get('model'),
            'temperature': arguments.get('temperature'),
            'tool_name': arguments.get('tool_name'),
        }

        # Remove None values
        return {k: v for k, v in params.items() if v is not None}

    async def execute_tool(
        self,
        name: str,
        arguments: dict,
        ws: WebSocketServerProtocol,
        req_id: str,
        resilient_ws_manager=None
    ) -> Tuple[bool, Optional[list], Optional[str]]:
        """
        Execute a tool with semaphore management and progress tracking.

        Args:
            name: Tool name
            arguments: Tool arguments
            ws: WebSocket connection
            req_id: Request ID
            resilient_ws_manager: Optional WebSocket manager

        Returns:
            Tuple of (success, outputs, error_msg)
        """
        # DEBUG: Log tool execution attempt (MCP 1.20.0 compatibility check)
        logger.info(f"[DEBUG] execute_tool called: name={name}, req_id={req_id}")
        logger.info(f"[DEBUG] Available tools: {list(self.server_tools.keys())}")

        # Get tool
        tool = self.server_tools.get(name)
        if not tool:
            log_error(ErrorCode.TOOL_NOT_FOUND, f"Tool not found: {name}", req_id)
            raise ToolNotFoundError(name, available_tools=list(self.server_tools.keys()))

        # DEBUG: Log tool object details
        logger.info(f"[DEBUG] Tool found: {tool}, type: {type(tool)}")
        logger.info(f"[DEBUG] Tool has execute method: {hasattr(tool, 'execute')}")
        if hasattr(tool, 'execute'):
            import inspect
            sig = inspect.signature(tool.execute)
            logger.info(f"[DEBUG] Tool execute signature: {sig}")

        # Check semantic cache first
        cache_params = None
        if self._should_cache_tool(name) and self._should_cache_request(arguments):
            cache_params = self._extract_cache_params(arguments)
            if self.semantic_cache:
                try:
                    cached_result = self.semantic_cache.get(**cache_params)
                    if cached_result is not None:
                        logger.info(f"[SEMANTIC_CACHE] Cache hit for {name}")
                        return True, cached_result, None
                except Exception as e:
                    log_error(ErrorCode.INTERNAL_ERROR, f"Failed to get cached result: {e}", req_id, exc_info=True)

        # Determine provider
        provider_name = self._get_provider_for_tool(name)
        provider_sem = self.provider_sems.get(provider_name) if provider_name else None

        # Start timing
        start_time = time.perf_counter()
        provider_sem_wait_ms = 0

        # Use context managers for safe semaphore management
        async with SemaphoreGuard(self.global_sem, f"global_sem_{name}"):
            # Calculate global semaphore wait time
            global_sem_wait_ms = (time.perf_counter() - start_time) * 1000

            if provider_sem:
                provider_sem_start = time.perf_counter()
                async with SemaphoreGuard(provider_sem, f"provider_sem_{provider_name}_{name}"):
                    provider_sem_wait_ms = (time.perf_counter() - provider_sem_start) * 1000

                    processing_start = time.perf_counter()
                    success, outputs, error_msg = await self._execute_tool_with_progress(
                        tool, arguments, ws, req_id, resilient_ws_manager
                    )

                    processing_ms = (time.perf_counter() - processing_start) * 1000
            else:
                provider_sem_wait_ms = 0
                processing_start = time.perf_counter()

                success, outputs, error_msg = await self._execute_tool_with_progress(
                    tool, arguments, ws, req_id, resilient_ws_manager
                )

                processing_ms = (time.perf_counter() - processing_start) * 1000

        # Calculate total latency
        total_latency_ms = (time.perf_counter() - start_time) * 1000

        # Inject latency metrics into outputs metadata
        if success and outputs:
            latency_metrics = {
                'latency_ms': round(total_latency_ms, 2),
                'global_sem_wait_ms': round(global_sem_wait_ms, 2),
                'provider_sem_wait_ms': round(provider_sem_wait_ms, 2),
                'processing_ms': round(processing_ms, 2),
                'provider_name': provider_name
            }

            try:
                if outputs and len(outputs) > 0 and isinstance(outputs[0], dict):
                    if 'metadata' not in outputs[0]:
                        outputs[0]['metadata'] = {}
                    outputs[0]['metadata']['latency_metrics'] = latency_metrics
            except Exception as e:
                logger.warning(f"[LATENCY] Failed to inject metrics into outputs: {e}")

        # Cache successful results
        if success and outputs and cache_params and self.semantic_cache:
            try:
                self.semantic_cache.set(
                    **cache_params,
                    response=outputs
                )
                logger.info(f"[SEMANTIC_CACHE] Cached result for {name}")
            except Exception as e:
                log_error(ErrorCode.INTERNAL_ERROR, f"Failed to cache result for {name}: {e}", req_id, exc_info=True)

        # Return result after semaphores are released
        logger.info(f"[DEBUG_RETURN] execute_tool returning: success={success}, outputs_type={type(outputs)}, error_msg={error_msg}")
        return success, outputs, error_msg

    def _get_provider_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Determine which provider a tool belongs to.

        Args:
            tool_name: Tool name

        Returns:
            Provider name (KIMI, GLM) or None for generic tools
        """
        # Simple heuristic: check tool name prefix
        tool_lower = tool_name.lower()
        if "kimi" in tool_lower or "moonshot" in tool_lower:
            return "KIMI"
        elif "glm" in tool_lower:
            return "GLM"
        return None

    async def _execute_tool_with_progress(
        self,
        tool,
        arguments: dict,
        ws: WebSocketServerProtocol,
        req_id: str,
        resilient_ws_manager
    ) -> Tuple[bool, Optional[list], Optional[str]]:
        """
        Execute tool with timeout and progress updates.

        Args:
            tool: Tool to execute
            arguments: Tool arguments
            ws: WebSocket connection
            req_id: Request ID
            resilient_ws_manager: WebSocket manager

        Returns:
            Tuple of (success, outputs, error_msg)
        """
        success = False
        outputs = None
        error_msg = None

        # Start progress task
        progress_task = asyncio.create_task(
            self._send_progress_updates(ws, req_id, resilient_ws_manager)
        )

        try:
            # Create streaming callback for progressive chunk delivery
            async def on_chunk(chunk: str):
                """Forward streaming chunks to WebSocket client."""
                await self._send_stream_chunk(ws, req_id, chunk, resilient_ws_manager)

            # DEBUG: Log before tool execution
            logger.info(f"[DEBUG] About to execute tool: {tool}")
            logger.info(f"[DEBUG] Arguments keys: {list(arguments.keys()) if arguments else []}")

            # Execute tool with timeout and streaming callback
            logger.info(f"[DEBUG] Calling tool.execute() with on_chunk callback...")
            result = await asyncio.wait_for(
                tool.execute(arguments, on_chunk=on_chunk),
                timeout=self.call_timeout
            )
            logger.info(f"[DEBUG] Tool execution completed successfully, result type: {type(result)}")

            # Extract outputs (result is already a list of TextContent)
            from src.daemon.ws.router_utils import normalize_outputs
            outputs = normalize_outputs(result)
            success = True

            # Send completion message after streaming finishes
            await self._send_stream_completion(ws, req_id, outputs, resilient_ws_manager)

        except asyncio.TimeoutError:
            error_msg = f"Tool execution timed out after {self.call_timeout}s"
            logger.warning(f"[{req_id}] {error_msg}")

        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            log_error(ErrorCode.TOOL_EXECUTION_ERROR, error_msg, req_id, exc_info=True)
            # Get tool name for error reporting
            tool_name = tool.get_name() if hasattr(tool, 'get_name') else str(tool)
            logger.error(f"[{req_id}] Tool '{tool_name}' failed but continuing workflow: {str(e)}")
            # FIXED: Don't raise exception - return error gracefully to allow workflow continuation
            # This prevents a single tool failure from terminating the entire agent workflow
            success = False
            error_msg = f"Tool '{tool_name}' unavailable: {str(e)}"
            
            # Send error response to client
            try:
                await _safe_send(
                    ws,
                    {
                        "op": "error",
                        "request_id": req_id,
                        "error": {
                            "code": "TOOL_EXECUTION_ERROR",
                            "message": error_msg
                        }
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
            except Exception as send_error:
                logger.warning(f"[{req_id}] Failed to send error response: {send_error}")

        finally:
            # Cleanup progress task
            progress_task.cancel()
            try:
                await progress_task
            except asyncio.CancelledError:
                # Expected cancellation
                pass
            except Exception as cleanup_error:
                logger.warning(f"[{req_id}] Unexpected error during progress task cleanup: {cleanup_error}")

        return success, outputs, error_msg

    async def _send_progress_updates(
        self,
        ws: WebSocketServerProtocol,
        req_id: str,
        resilient_ws_manager=None
    ) -> None:
        """Send periodic progress updates during tool execution."""
        try:
            while True:
                await asyncio.sleep(self.progress_interval)
                await _safe_send(
                    ws,
                    {
                        "op": "progress",
                        "request_id": req_id,
                        "message": "Tool execution in progress..."
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
        except asyncio.CancelledError:
            # Normal cancellation when tool completes
            pass
        except Exception as e:
            logger.debug(f"Progress update failed: {e}")

    async def _send_stream_chunk(
        self,
        ws: WebSocketServerProtocol,
        req_id: str,
        chunk: str,
        resilient_ws_manager=None
    ) -> None:
        """Send a streaming chunk to the client."""
        try:
            await _safe_send(
                ws,
                {
                    "op": "stream_chunk",
                    "request_id": req_id,
                    "chunk": chunk,
                    "timestamp": log_timestamp()
                },
                resilient_ws_manager=resilient_ws_manager
            )
        except Exception as e:
            logger.debug(f"Stream chunk send failed: {e}")

    async def _send_stream_completion(
        self,
        ws: WebSocketServerProtocol,
        req_id: str,
        outputs: Optional[list],
        resilient_ws_manager=None
    ) -> None:
        """Send final tool result after streaming completes.

        Args:
            ws: WebSocket connection
            req_id: Request ID
            outputs: Tool execution outputs to send
            resilient_ws_manager: WebSocket manager
        """
        try:
            # Send the final tool result (replaces stream_complete + call_tool_res)
            if outputs is not None:
                logger.info(f"Sending final tool result for {req_id}, outputs type: {type(outputs)}, len: {len(outputs) if isinstance(outputs, list) else 'N/A'}")
                await _safe_send(
                    ws,
                    {
                        "op": "call_tool_res",
                        "request_id": req_id,
                        "outputs": outputs
                    },
                    resilient_ws_manager=resilient_ws_manager
                )
                logger.info(f"Final tool result sent successfully for {req_id}")
        except Exception as e:
            logger.error(f"Stream completion send failed: {e}", exc_info=True)
