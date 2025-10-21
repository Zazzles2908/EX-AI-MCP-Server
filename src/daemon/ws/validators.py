"""
WebSocket Message Validation Module

This module provides validation functions for WebSocket messages in the EX-AI MCP Server.
Extracted from ws_server.py as part of code refactoring (2025-10-21).

Functions:
    validate_message: Validate WebSocket message structure and required fields
    get_conversation_id_from_arguments: Extract conversation ID from tool arguments
"""

from typing import Any, Dict, Optional


def validate_message(msg: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate WebSocket message structure and required fields.

    Provides defense-in-depth validation to complement protocol-level size limits.
    Checks message structure, operation validity, and field types.

    Args:
        msg: Parsed JSON message from client

    Returns:
        (is_valid, error_message) - error_message is None if valid

    Examples:
        >>> validate_message({"op": "call_tool", "name": "test"})
        (True, None)
        
        >>> validate_message({"op": "call_tool"})
        (False, "call_tool requires 'name' (non-empty string)")
        
        >>> validate_message("not a dict")
        (False, "message must be a JSON object")
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


def get_conversation_id_from_arguments(arguments: Dict[str, Any], session_id: str) -> str:
    """
    Extract conversation ID from tool arguments for session semaphore management.

    BUG FIX #11 (Phase 2 - 2025-10-20): This function extracts the conversation_id
    from tool arguments to enable per-conversation semaphore isolation.

    Args:
        arguments: Tool call arguments
        session_id: WebSocket session ID (fallback)

    Returns:
        Conversation ID string (continuation_id if available, otherwise session_id)

    Examples:
        >>> get_conversation_id_from_arguments({"continuation_id": "abc123"}, "sess_1")
        'abc123'
        
        >>> get_conversation_id_from_arguments({}, "sess_1")
        'session_sess_1'
        
        >>> get_conversation_id_from_arguments({"continuation_id": ""}, "sess_1")
        'session_sess_1'
    """
    # Try to get continuation_id from arguments
    conv_id = arguments.get("continuation_id")

    # Fallback to session_id if no continuation_id
    if not conv_id or not isinstance(conv_id, str):
        conv_id = f"session_{session_id}"

    return conv_id

