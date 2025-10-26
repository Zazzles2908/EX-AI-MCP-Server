"""
WebSocket Connection Manager

Handles WebSocket connection lifecycle, authentication, and message routing.
Extracted from ws_server.py as part of Week 3 Fix #15 (2025-10-21).

This module contains:
- Connection handling (_serve_connection)
- Safe send/receive operations (_safe_send, _safe_recv)
- Connection authentication and validation
- Connection lifecycle management
"""

import asyncio
import json
import logging
import os
import secrets
import time
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol

# Import error handling
from src.daemon.error_handling import (
    create_error_response,
    ErrorCode,
    log_error,
)

# Import validation
from src.daemon.ws.validators import validate_message as _validate_message

# Import monitoring
from utils.monitoring import get_monitor, record_websocket_event
from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)


async def _safe_recv(ws: WebSocketServerProtocol, timeout: float):
    """
    Safely receive a message from WebSocket with timeout.
    
    Args:
        ws: WebSocket connection
        timeout: Timeout in seconds
        
    Returns:
        Message string or None if connection closed or timeout
    """
    try:
        return await asyncio.wait_for(ws.recv(), timeout=timeout)
    except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
        return None
    except asyncio.TimeoutError:
        return None


async def _safe_send(
    ws: WebSocketServerProtocol,
    payload: dict,
    critical: bool = False,
    resilient_ws_manager=None
) -> bool:
    """
    Best-effort send that swallows disconnects and logs at debug level.

    PHASE 4 (2025-10-19): Now uses ResilientWebSocketManager for automatic retry and queuing.

    Args:
        ws: WebSocket connection
        payload: Message payload to send
        critical: If True, queue message for retry on failure (default: False)
        resilient_ws_manager: Optional ResilientWebSocketManager instance

    Returns False if the connection is closed or an error occurred, True on success.
    """
    start_time = time.time()
    message_json = json.dumps(payload)
    data_size = len(message_json.encode('utf-8'))

    # PHASE 4 (2025-10-19): Use ResilientWebSocketManager if available
    if resilient_ws_manager is not None:
        try:
            # CRITICAL DEBUG (2025-10-27): Log EVERY send attempt via ResilientWebSocketManager
            logger.info(f"[SAFE_SEND_RESILIENT] Attempting to send op={payload.get('op')} size={data_size} bytes")
            success = await resilient_ws_manager.send(ws, payload, critical=critical)
            logger.info(f"[SAFE_SEND_RESILIENT] Send result: success={success} op={payload.get('op')}")

            # Monitor successful sends (sample 1 in 10 for performance)
            if success and hash(payload.get("request_id", "")) % 10 == 0:
                response_time_ms = (time.time() - start_time) * 1000
                record_websocket_event(
                    direction="send",
                    function_name="_safe_send",
                    data_size=data_size,
                    response_time_ms=response_time_ms,
                    metadata={"op": payload.get("op"), "timestamp": log_timestamp(), "resilient": True}
                )

            return success
        except Exception as e:
            logger.warning(f"ResilientWebSocketManager error (op: {payload.get('op', 'unknown')}): {e}")
            # Fall through to legacy send

    # Legacy fallback (if ResilientWebSocketManager not initialized or failed)
    try:
        # CRITICAL DEBUG (2025-10-27): Log EVERY send attempt
        logger.info(f"[SAFE_SEND] Attempting to send op={payload.get('op')} size={data_size} bytes")
        await ws.send(message_json)
        logger.info(f"[SAFE_SEND] Successfully sent op={payload.get('op')}")

        # PHASE 3 (2025-10-18): Monitor successful sends (sample 1 in 10 for performance)
        if hash(payload.get("request_id", "")) % 10 == 0:
            response_time_ms = (time.time() - start_time) * 1000
            record_websocket_event(
                direction="send",
                function_name="_safe_send",
                data_size=data_size,
                response_time_ms=response_time_ms,
                metadata={"op": payload.get("op"), "timestamp": log_timestamp()}
            )

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
        logger.warning(f"_safe_send: unexpected error sending {payload.get('op')}: {e}")
        return False


async def serve_connection(
    ws: WebSocketServerProtocol,
    *,
    connection_manager,
    rate_limiter,
    session_manager,
    auth_token_manager,
    message_handler,
    hello_timeout: float,
    resilient_ws_manager=None,
) -> None:
    """
    Handle a single WebSocket connection lifecycle.
    
    This function manages:
    - Connection limits and rate limiting
    - Authentication (hello handshake)
    - Session creation and management
    - Message routing to handler
    - Connection cleanup
    
    Args:
        ws: WebSocket connection
        connection_manager: Connection manager instance
        rate_limiter: Rate limiter instance
        session_manager: Session manager instance
        auth_token_manager: Auth token manager instance
        message_handler: Message handler function
        hello_timeout: Timeout for hello message (seconds)
        resilient_ws_manager: Optional ResilientWebSocketManager instance
    """
    # Get client IP for connection tracking
    try:
        client_ip, client_port = ws.remote_address if hasattr(ws, 'remote_address') else ("unknown", 0)
    except Exception as e:
        logger.debug(f"[WS_CONNECTION] Could not get remote address: {e}")
        client_ip, client_port = "unknown", 0

    # PHASE 1 (2025-10-18): Enforce connection limits
    can_accept, rejection_reason = connection_manager.can_accept_connection(client_ip)

    if not can_accept:
        logger.warning(
            f"[WS_CONNECTION] Connection rejected from {client_ip}:{client_port} - {rejection_reason}"
        )
        # PHASE 3: Monitor rejected connections
        record_websocket_event(
            direction="reject",
            function_name="serve_connection",
            data_size=0,
            metadata={
                "client_ip": client_ip,
                "client_port": client_port,
                "reason": rejection_reason,
                "timestamp": log_timestamp()
            }
        )
        try:
            # Gracefully reject with WebSocket close code
            # 1008 = Policy Violation (rate limit/connection limit)
            await ws.close(code=1008, reason=rejection_reason)
        except Exception as e:
            logger.debug(f"Failed to close rejected connection: {e}")
        return

    # Initialize session variable to prevent UnboundLocalError in exception handlers
    # PHASE 2.3 FIX (2025-10-25): Variable scope fix for sess
    sess = None

    # Generate unique connection ID for tracking
    # Week 2 Fix #11 (2025-10-21): Use cryptographically secure connection IDs
    connection_id = secrets.token_urlsafe(32)  # 256 bits of entropy
    connection_manager.register_connection(connection_id, client_ip)

    try:
        logger.info(f"[WS_CONNECTION] New connection from {client_ip}:{client_port} (id: {connection_id})")

        # PHASE 3 (2025-10-18): Monitor connection establishment
        record_websocket_event(
            direction="connect",
            function_name="serve_connection",
            data_size=0,
            metadata={
                "client_ip": client_ip,
                "client_port": client_port,
                "connection_id": connection_id,
                "timestamp": log_timestamp()
            }
        )
        get_monitor().increment_active_connections("websocket")

        # Expect hello first with timeout, handle abrupt client disconnects gracefully
        hello_raw = await _safe_recv(ws, timeout=hello_timeout)
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

        # Parse and validate hello message
        try:
            hello = json.loads(hello_raw)
        except Exception as e:
            logger.warning(f"Failed to parse hello message: {e}")
            try:
                await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "invalid_hello"}, resilient_ws_manager=resilient_ws_manager)
                try:
                    await ws.close(code=4000, reason="invalid hello")
                except Exception as e2:
                    logger.debug(f"Failed to close connection after invalid hello: {e2}")
            except Exception as e2:
                logger.debug(f"Failed to send hello_ack error: {e2}")
            return

        # Validate hello op
        if hello.get("op") != "hello":
            logger.warning(f"Client sent message without hello op: {hello.get('op')}")
            try:
                await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "missing_hello"}, resilient_ws_manager=resilient_ws_manager)
                try:
                    await ws.close(code=4001, reason="missing hello")
                except Exception as e:
                    logger.debug(f"Failed to close connection after missing hello: {e}")
            except Exception as e:
                logger.debug(f"Failed to send missing_hello error: {e}")
            return

        # Authenticate token
        token = hello.get("token", "") or ""  # PHASE 2.3 FIX (2025-10-25): Handle None token
        current_auth_token = await auth_token_manager.get()
        if current_auth_token and token != current_auth_token:
            # Enhanced logging for auth debugging (show first 10 chars only for security)
            expected_preview = current_auth_token[:10] + "..." if len(current_auth_token) > 10 else current_auth_token
            received_preview = token[:10] + "..." if len(token) > 10 else (token if token else "<empty>")
            logger.warning(f"[AUTH] Client sent invalid auth token. "
                           f"Expected: {expected_preview}, Received: {received_preview}")
            try:
                await _safe_send(ws, {"op": "hello_ack", "ok": False, "error": "unauthorized"}, resilient_ws_manager=resilient_ws_manager)
                try:
                    await ws.close(code=4003, reason="unauthorized")
                except Exception as e:
                    logger.debug(f"Failed to close connection after unauthorized: {e}")
            except Exception as e:
                logger.debug(f"Failed to send unauthorized error: {e}")
            return

        # Create session
        # MULTI-INSTANCE FIX (2025-10-26): Use client's session_id if provided and valid
        # This allows multiple VSCode instances to maintain unique session identities
        client_session_id = hello.get("session_id")

        def _is_valid_session_id(sid: str) -> bool:
            """Validate client-provided session ID format and length"""
            if not sid or not isinstance(sid, str):
                return False
            # Allow reasonable length (3-64 chars) and safe characters (alphanumeric, dash, underscore)
            return (3 <= len(sid) <= 64 and
                    sid.replace("-", "").replace("_", "").isalnum())

        if client_session_id and _is_valid_session_id(client_session_id):
            session_id = client_session_id
            logger.info(f"[SESSION] Using client-provided session ID: {session_id}")
        else:
            # Fallback to random if client doesn't provide one or it's invalid
            # Week 2 Fix #11 (2025-10-21): Use cryptographically secure session IDs
            session_id = secrets.token_urlsafe(32)  # 256 bits of entropy
            if client_session_id:
                logger.warning(f"[SESSION] Client provided invalid session ID, using random: {session_id[:8]}...")
            else:
                logger.debug(f"[SESSION] No client session ID provided, using random: {session_id[:8]}...")

        sess = await session_manager.ensure(session_id)
        
        # Send hello acknowledgment
        try:
            ok = await _safe_send(ws, {"op": "hello_ack", "ok": True, "session_id": sess.session_id}, resilient_ws_manager=resilient_ws_manager)
            if not ok:
                return
        except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
            # Client closed during hello ack; just return
            return

        # Message processing loop
        try:
            async for raw in ws:
                # CRITICAL DEBUG (2025-10-27): Log ALL incoming messages
                logger.info(f"[MSG_LOOP] Received raw message from {sess.session_id}: {raw[:200]}...")
                try:
                    msg = json.loads(raw)
                    logger.info(f"[MSG_LOOP] Parsed message op={msg.get('op')} for session={sess.session_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse JSON message from client (session: {sess.session_id}): {e}")

                    # Week 2 Fix #8 (2025-10-21): Standardized error handling - Location 9
                    error_response = create_error_response(
                        code=ErrorCode.VALIDATION_ERROR,
                        message="Invalid JSON: message could not be parsed",
                        request_id=None,  # request_id not available when JSON parsing fails
                        details={"parse_error": str(e)}
                    )
                    log_error(ErrorCode.VALIDATION_ERROR, f"JSON parsing failed: {e}", request_id=None)

                    # Try to inform client; ignore if already closed
                    try:
                        await _safe_send(ws, {"op": "error", **error_response}, resilient_ws_manager=resilient_ws_manager)
                    except Exception as e2:
                        logger.debug(f"Failed to send invalid_json error: {e2}")
                    continue

                # Validate message structure before processing
                is_valid, error_msg = _validate_message(msg)
                if not is_valid:
                    logger.warning(f"Invalid message structure from client (session: {sess.session_id}): {error_msg}")
                    try:
                        req_id = msg.get("request_id") if isinstance(msg, dict) else None
                        error_response = create_error_response(
                            code=ErrorCode.INVALID_REQUEST,
                            message=f"Invalid message: {error_msg}",
                            request_id=req_id,
                            details={"validation_error": error_msg}
                        )
                        log_error(ErrorCode.INVALID_REQUEST, f"Message validation failed: {error_msg}", request_id=req_id)

                        # Send error response with appropriate op based on message type
                        op = msg.get("op") if isinstance(msg, dict) else None
                        if op == "call_tool":
                            await _safe_send(ws, {
                                "op": "call_tool_res",
                                "request_id": req_id,
                                **error_response
                            }, resilient_ws_manager=resilient_ws_manager)
                        else:
                            await _safe_send(ws, {"op": "error", **error_response}, resilient_ws_manager=resilient_ws_manager)
                    except Exception as e:
                        logger.debug(f"Failed to send invalid_message error: {e}")
                    continue

                # PHASE 1 (2025-10-18): Enforce rate limiting
                allowed, rejection_reason = rate_limiter.is_allowed(
                    ip=client_ip,
                    user_id=sess.session_id,
                    tokens=1
                )

                if not allowed:
                    logger.warning(
                        f"[WS_RATE_LIMIT] Message rejected from {client_ip} (session: {sess.session_id}) - {rejection_reason}"
                    )
                    # PHASE 3: Monitor rate limit rejections
                    record_websocket_event(
                        direction="rate_limit",
                        function_name="serve_connection",
                        data_size=len(raw.encode('utf-8')) if isinstance(raw, str) else len(raw),
                        metadata={
                            "client_ip": client_ip,
                            "session_id": sess.session_id,
                            "reason": rejection_reason,
                            "timestamp": log_timestamp()
                        }
                    )

                    # Week 2 Fix #8 (2025-10-21): Standardized error handling - Location 8
                    req_id = None
                    try:
                        msg = json.loads(raw)
                        req_id = msg.get("request_id") if isinstance(msg, dict) else None
                    except Exception:
                        pass  # request_id not available for rate limit errors

                    error_response = create_error_response(
                        code=ErrorCode.OVER_CAPACITY,
                        message=f"Rate limit exceeded: {rejection_reason}",
                        request_id=req_id,
                        details={"reason": rejection_reason, "client_ip": client_ip}
                    )
                    log_error(ErrorCode.OVER_CAPACITY, f"Rate limit exceeded: {rejection_reason}", request_id=req_id)

                    try:
                        await _safe_send(ws, {
                            "op": "error",
                            **error_response
                        }, resilient_ws_manager=resilient_ws_manager)
                    except Exception as e:
                        logger.debug(f"Failed to send rate_limit error: {e}")
                    continue

                # Route message to handler
                try:
                    await message_handler(ws, sess.session_id, msg, resilient_ws_manager=resilient_ws_manager)
                except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
                    # Client disconnected mid-processing; exit loop
                    break
        except (websockets.exceptions.ConnectionClosedError, ConnectionAbortedError, ConnectionResetError):
            # Iterator may raise on abrupt close; treat as normal disconnect
            pass
    finally:
        # PHASE 1 (2025-10-18): Unregister connection from connection manager
        try:
            connection_manager.unregister_connection(connection_id)
        except Exception as e:
            logger.warning(f"Failed to unregister connection {connection_id}: {e}")

        # Clean up session (only if session was created)
        # PHASE 2.3 FIX (2025-10-25): Add null check for sess
        if sess is not None:
            try:
                await session_manager.remove(sess.session_id)
            except Exception as e:
                logger.warning(f"Failed to remove session {sess.session_id}: {e}")

