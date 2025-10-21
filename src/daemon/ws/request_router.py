"""
WebSocket Request Router

Handles message routing, tool execution, caching, and deduplication.
Extracted from ws_server.py as part of Week 3 Fix #15 (2025-10-21).

This module contains:
- RequestRouter class - Main message routing logic
- ToolExecutor class - Tool execution with semaphore management
- CacheManager class - Result caching and inflight tracking
- Utility functions - Normalization, key generation, etc.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from websockets.server import WebSocketServerProtocol

# Import connection manager for _safe_send
from src.daemon.ws.connection_manager import _safe_send

# Import error handling
from src.daemon.error_handling import (
    create_error_response,
    ErrorCode,
    log_error,
)

# Import validation
from src.daemon.input_validation import validate_tool_arguments, ValidationError as InputValidationError

# Import semaphore management
from src.daemon.middleware.semaphores import SemaphoreGuard

# Import monitoring
from utils.monitoring import record_websocket_event
from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def normalize_tool_name(name: str) -> str:
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


def normalize_outputs(outputs: List[Any]) -> List[Dict[str, Any]]:
    """
    Normalize tool outputs to standard format.
    
    Converts various output formats (mcp.types.TextContent, dicts, etc.)
    to a consistent list of {"type": "text", "text": "..."} dictionaries.
    """
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


def make_call_key(name: str, arguments: Dict[str, Any]) -> str:
    """
    Generate a deterministic cache key for tool calls.
    
    Used for deduplication and result caching.
    """
    try:
        # Sort keys for deterministic hashing
        args_str = json.dumps(arguments, sort_keys=True)
        combined = f"{name}:{args_str}"
        return hashlib.sha256(combined.encode()).hexdigest()
    except Exception as e:
        logger.warning(f"Failed to create call key: {e}")
        # Fallback to simple concatenation
        return f"{name}:{str(arguments)}"


# ============================================================================
# CACHE MANAGER
# ============================================================================

class CacheManager:
    """
    Manages result caching and inflight request tracking.
    
    Provides:
    - Result caching by request_id and call_key
    - Inflight request tracking for deduplication
    - Automatic cache expiration
    """
    
    def __init__(self, inflight_ttl_secs: int = 300, result_ttl_secs: int = 300):
        """
        Initialize cache manager.
        
        Args:
            inflight_ttl_secs: TTL for inflight entries (default: 300s)
            result_ttl_secs: TTL for cached results (default: 300s)
        """
        self.inflight_ttl_secs = inflight_ttl_secs
        self.result_ttl_secs = result_ttl_secs
        
        # Cache storage
        self._results_cache: Dict[str, Dict[str, Any]] = {}  # request_id -> {t, payload}
        self._results_cache_by_key: Dict[str, Dict[str, Any]] = {}  # call_key -> {t, outputs}
        self._inflight_reqs: Dict[str, Dict[str, Any]] = {}  # call_key -> {req_id, expires_at}
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def check_and_set_inflight(self, call_key: str, req_id: str, expires_at: float) -> Tuple[bool, Optional[str]]:
        """
        Atomically check if a request is inflight and set it if not.
        
        Returns:
            (is_duplicate, existing_req_id)
            - (True, req_id) if duplicate found
            - (False, None) if not duplicate (and now set as inflight)
        """
        async with self._lock:
            # Clean up expired entries
            now = time.time()
            expired = [k for k, v in self._inflight_reqs.items() if v.get("expires_at", 0) < now]
            for k in expired:
                self._inflight_reqs.pop(k, None)
            
            # Check if already inflight
            existing = self._inflight_reqs.get(call_key)
            if existing and existing.get("expires_at", 0) > now:
                return True, existing.get("req_id")
            
            # Set as inflight
            self._inflight_reqs[call_key] = {
                "req_id": req_id,
                "expires_at": expires_at
            }
            return False, None
    
    async def cleanup_inflight(self, call_key: str) -> None:
        """Remove inflight entry for a call key."""
        async with self._lock:
            self._inflight_reqs.pop(call_key, None)
    
    def store_result(self, req_id: str, payload: Dict[str, Any]) -> None:
        """Store result by request_id."""
        self._results_cache[req_id] = {"t": time.time(), "payload": payload}
        self._gc_results_cache()
    
    def get_cached_result(self, req_id: str) -> Optional[Dict[str, Any]]:
        """Get cached result by request_id."""
        rec = self._results_cache.get(req_id)
        if not rec:
            return None
        if time.time() - rec.get("t", 0) > self.result_ttl_secs:
            self._results_cache.pop(req_id, None)
            return None
        return rec.get("payload")
    
    def store_result_by_key(self, call_key: str, outputs: List[Dict[str, Any]]) -> None:
        """Store result by call_key."""
        self._results_cache_by_key[call_key] = {"t": time.time(), "outputs": outputs}
        self._gc_results_cache()
    
    def get_cached_by_key(self, call_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached result by call_key."""
        rec = self._results_cache_by_key.get(call_key)
        if not rec:
            return None
        if time.time() - rec.get("t", 0) > self.result_ttl_secs:
            self._results_cache_by_key.pop(call_key, None)
            return None
        return rec.get("outputs")
    
    def _gc_results_cache(self) -> None:
        """Garbage collect expired cache entries."""
        now = time.time()
        
        # GC results cache
        expired_ids = [k for k, v in self._results_cache.items() if now - v.get("t", 0) > self.result_ttl_secs]
        for k in expired_ids:
            self._results_cache.pop(k, None)
        
        # GC results cache by key
        expired_keys = [k for k, v in self._results_cache_by_key.items() if now - v.get("t", 0) > self.result_ttl_secs]
        for k in expired_keys:
            self._results_cache_by_key.pop(k, None)


# ============================================================================
# TOOL EXECUTOR
# ============================================================================

class ToolExecutor:
    """
    Handles tool execution with semaphore management and progress updates.

    Provides:
    - Tool execution with timeout
    - Semaphore-based concurrency control
    - Progress updates during long-running operations
    - Error handling and recovery
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

    async def execute_tool(
        self,
        ws: WebSocketServerProtocol,
        session_id: str,
        name: str,
        arguments: Dict[str, Any],
        req_id: str,
        session_manager,
        resilient_ws_manager=None
    ) -> Tuple[bool, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Execute a tool with semaphore management and progress updates.

        Returns:
            (success, outputs, error_message)
            - (True, outputs, None) on success
            - (False, None, error_msg) on failure
        """
        tool = self.server_tools.get(name)
        if not tool:
            return False, None, f"Unknown tool: {name}"

        # Determine which semaphore to use
        provider_name = self._get_provider_for_tool(name)
        provider_sem = self.provider_sems.get(provider_name) if provider_name else None

        # Acquire semaphores manually (global + provider)
        global_acquired = False
        provider_acquired = False

        try:
            # Acquire global semaphore
            await self.global_sem.acquire()
            global_acquired = True

            # Acquire provider semaphore if needed
            if provider_sem:
                await provider_sem.acquire()
                provider_acquired = True

            # Execute tool with timeout and progress updates
            try:
                # Start progress task
                progress_task = asyncio.create_task(
                    self._send_progress_updates(ws, req_id, resilient_ws_manager)
                )

                try:
                    # Execute tool with timeout
                    result = await asyncio.wait_for(
                        tool.execute(arguments),
                        timeout=self.call_timeout
                    )

                    # Extract outputs (result is already a list of TextContent)
                    outputs = normalize_outputs(result)
                    return True, outputs, None

                except asyncio.TimeoutError:
                    error_msg = f"Tool execution timed out after {self.call_timeout}s"
                    logger.warning(f"[{req_id}] {error_msg}")
                    return False, None, error_msg

                except Exception as e:
                    error_msg = f"Tool execution failed: {str(e)}"
                    logger.error(f"[{req_id}] {error_msg}", exc_info=True)
                    return False, None, error_msg

                finally:
                    # Cancel progress task
                    progress_task.cancel()
                    try:
                        await progress_task
                    except asyncio.CancelledError:
                        pass

            except Exception as e:
                error_msg = f"Semaphore management failed: {str(e)}"
                logger.error(f"[{req_id}] {error_msg}", exc_info=True)
                return False, None, error_msg

        finally:
            # Release semaphores in reverse order
            if provider_acquired and provider_sem:
                try:
                    provider_sem.release()
                except Exception as e:
                    logger.error(f"[{req_id}] Failed to release provider semaphore: {e}")

            if global_acquired:
                try:
                    self.global_sem.release()
                except Exception as e:
                    logger.error(f"[{req_id}] Failed to release global semaphore: {e}")

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
            # Don't propagate - progress updates are best-effort

    def _get_provider_for_tool(self, tool_name: str) -> Optional[str]:
        """
        Determine which provider a tool belongs to.

        Returns provider name (KIMI, GLM) or None for generic tools.
        """
        # Simple heuristic: check tool name prefix
        tool_lower = tool_name.lower()
        if "kimi" in tool_lower or "moonshot" in tool_lower:
            return "KIMI"
        elif "glm" in tool_lower or "zhipu" in tool_lower:
            return "GLM"
        return None


# ============================================================================
# REQUEST ROUTER
# ============================================================================

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
        use_per_session_semaphores: bool = False
    ):
        """
        Initialize request router.

        Args:
            session_manager: Session manager instance
            server_tools: Dictionary of available tools
            global_sem: Global semaphore for concurrency control
            provider_sems: Provider-specific semaphores
            validated_env: Validated environment variables
            use_per_session_semaphores: Whether to use per-session semaphores
        """
        self.session_manager = session_manager
        self.server_tools = server_tools
        self.validated_env = validated_env

        # Initialize cache manager
        inflight_ttl = int(validated_env.get("INFLIGHT_TTL_SECS", 300))
        result_ttl = int(validated_env.get("RESULT_TTL_SECS", 300))
        self.cache_manager = CacheManager(
            inflight_ttl_secs=inflight_ttl,
            result_ttl_secs=result_ttl
        )

        # Initialize tool executor
        call_timeout = float(validated_env.get("KIMI_CHAT_TOOL_TIMEOUT_SECS", 180.0))
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
        # Update session activity
        await self.session_manager.update_activity(session_id)

        # Check message size
        try:
            import sys
            msg_size = sys.getsizeof(json.dumps(msg))
            tool_call_max = self.validated_env["TOOL_CALL_MAX_SIZE"]

            if msg_size > tool_call_max:
                error_response = create_error_response(
                    code=ErrorCode.OVER_CAPACITY,
                    message=f"Request too large: {msg_size} bytes exceeds limit of {tool_call_max} bytes",
                    request_id=msg.get("request_id"),
                    details={"actual_size": msg_size, "limit": tool_call_max}
                )
                log_error(
                    ErrorCode.OVER_CAPACITY,
                    f"Oversized request rejected: {msg_size} bytes (limit: {tool_call_max})",
                    request_id=msg.get("request_id")
                )
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": msg.get("request_id"),
                    **error_response
                }, resilient_ws_manager=resilient_ws_manager)
                return
        except Exception as e:
            logger.warning(f"Failed to check message size: {e}")

        # Route based on operation
        op = msg.get("op")

        if op == "list_tools":
            await self._handle_list_tools(ws, resilient_ws_manager)
        elif op == "call_tool":
            await self._handle_call_tool(ws, session_id, msg, resilient_ws_manager)
        else:
            logger.warning(f"Unknown operation: {op}")
            await _safe_send(ws, {
                "op": "error",
                **create_error_response(
                    code=ErrorCode.INVALID_REQUEST,
                    message=f"Unknown operation: {op}",
                    request_id=msg.get("request_id")
                )
            }, resilient_ws_manager=resilient_ws_manager)

    async def _handle_list_tools(
        self,
        ws: WebSocketServerProtocol,
        resilient_ws_manager=None
    ) -> None:
        """Handle list_tools operation."""
        tools = []
        for name, tool in self.server_tools.items():
            try:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.get_input_schema(),
                })
            except Exception as e:
                logger.warning(f"Failed to get full schema for tool '{name}': {e}")
                # Fallback to minimal descriptor
                tools.append({
                    "name": name,
                    "description": getattr(tool, "description", name),
                    "inputSchema": {"type": "object"}
                })

        await _safe_send(ws, {
            "op": "list_tools_res",
            "tools": tools
        }, resilient_ws_manager=resilient_ws_manager)

    async def _handle_call_tool(
        self,
        ws: WebSocketServerProtocol,
        session_id: str,
        msg: Dict[str, Any],
        resilient_ws_manager=None
    ) -> None:
        """Handle call_tool operation."""
        orig_name = msg.get("name")
        name = normalize_tool_name(orig_name)
        arguments = msg.get("arguments") or {}
        req_id = msg.get("request_id")

        # Log tool call
        logger.info(f"=== TOOL CALL RECEIVED ===")
        logger.info(f"Session: {session_id}")
        logger.info(f"Tool: {name} (original: {orig_name})")
        logger.info(f"Request ID: {req_id}")
        try:
            args_preview = json.dumps(arguments, indent=2)[:500]
            logger.info(f"Arguments (first 500 chars): {args_preview}")
        except Exception as e:
            logger.warning(f"Failed to serialize arguments for logging: {e}")
            logger.info(f"Arguments: <unable to serialize>")
        logger.info(f"=== PROCESSING ===")

        # Validate arguments
        try:
            arguments = validate_tool_arguments(name, arguments)
            logger.debug(f"[{req_id}] Arguments validated successfully")
        except InputValidationError as e:
            error_response = e.to_response(request_id=req_id)
            log_error(ErrorCode.VALIDATION_ERROR, str(e), request_id=req_id)
            await _safe_send(ws, {
                "op": "call_tool_res",
                "request_id": req_id,
                **error_response
            }, resilient_ws_manager=resilient_ws_manager)
            return

        # Check if tool exists
        if name not in self.server_tools:
            error_response = create_error_response(
                code=ErrorCode.TOOL_NOT_FOUND,
                message=f"Unknown tool: {orig_name}",
                request_id=req_id,
                details={"requested_tool": orig_name}
            )
            log_error(ErrorCode.TOOL_NOT_FOUND, f"Tool not found: {orig_name}", request_id=req_id)
            await _safe_send(ws, {
                "op": "call_tool_res",
                "request_id": req_id,
                **error_response
            }, resilient_ws_manager=resilient_ws_manager)
            return

        # Check for cached result
        cached = self.cache_manager.get_cached_result(req_id)
        if cached:
            logger.info(f"[{req_id}] Returning cached result")
            await _safe_send(ws, cached, resilient_ws_manager=resilient_ws_manager)
            return

        # Check for duplicate inflight request
        call_key = make_call_key(name, arguments)
        expires_at = time.time() + self.cache_manager.inflight_ttl_secs
        is_duplicate, existing_req_id = await self.cache_manager.check_and_set_inflight(
            call_key, req_id, expires_at
        )

        if is_duplicate:
            # Check if we have cached result from the duplicate
            cached_outputs = self.cache_manager.get_cached_by_key(call_key)
            if cached_outputs:
                logger.info(f"[{req_id}] Returning cached result from duplicate request {existing_req_id}")
                response = {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "ok": True,
                    "outputs": cached_outputs
                }
                self.cache_manager.store_result(req_id, response)
                await _safe_send(ws, response, resilient_ws_manager=resilient_ws_manager)
                return
            else:
                # Duplicate is still processing - send retry response
                logger.info(f"[{req_id}] Duplicate request detected (original: {existing_req_id}), sending retry")
                error_response = create_error_response(
                    code=ErrorCode.OVER_CAPACITY,
                    message=f"Duplicate request in progress (original: {existing_req_id})",
                    request_id=req_id,
                    details={
                        "retry_after_secs": self.retry_after_secs,
                        "original_request_id": existing_req_id
                    }
                )
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    **error_response
                }, resilient_ws_manager=resilient_ws_manager)
                return

        # Execute tool
        try:
            success, outputs, error_msg = await self.tool_executor.execute_tool(
                ws=ws,
                session_id=session_id,
                name=name,
                arguments=arguments,
                req_id=req_id,
                session_manager=self.session_manager,
                resilient_ws_manager=resilient_ws_manager
            )

            if success:
                # Success response
                response = {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    "ok": True,
                    "outputs": outputs
                }
                self.cache_manager.store_result(req_id, response)
                self.cache_manager.store_result_by_key(call_key, outputs)
                await _safe_send(ws, response, resilient_ws_manager=resilient_ws_manager)
            else:
                # Error response
                error_response = create_error_response(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=error_msg,
                    request_id=req_id
                )
                log_error(ErrorCode.INTERNAL_ERROR, error_msg, request_id=req_id)
                await _safe_send(ws, {
                    "op": "call_tool_res",
                    "request_id": req_id,
                    **error_response
                }, resilient_ws_manager=resilient_ws_manager)
        finally:
            # Clean up inflight tracking
            await self.cache_manager.cleanup_inflight(call_key)

