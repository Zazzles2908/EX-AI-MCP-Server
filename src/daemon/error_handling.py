"""
Standardized Error Handling for EXAI MCP Server
Week 2 Fix #8 (2025-10-21): Consistent error handling across the codebase

This module provides:
- Standardized error codes and response format
- Custom exception classes for different error types
- Error logging utilities with appropriate severity levels
- Error handling decorators for common patterns

Usage:
    from src.daemon.error_handling import MCPError, ErrorCode, create_error_response
    
    # Create error response
    error = create_error_response(
        code=ErrorCode.TOOL_NOT_FOUND,
        message="Tool not found: example_tool",
        request_id="req-123"
    )
    
    # Raise custom exception
    raise ToolNotFoundError("example_tool", available_tools=["tool1", "tool2"])
"""

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


# =============================================================================
# Error Codes
# =============================================================================

class ErrorCode:
    """
    Standardized error codes for MCP server.
    
    Categories:
    - 4xx: Client errors (invalid requests, not found, etc.)
    - 5xx: Server errors (internal errors, service unavailable, etc.)
    - 1xxx: MCP-specific errors (tool errors, provider errors, etc.)
    """
    
    # Client errors (4xx)
    INVALID_REQUEST = "INVALID_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    NOT_FOUND = "NOT_FOUND"
    TIMEOUT = "TIMEOUT"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    OVER_CAPACITY = "OVER_CAPACITY"
    
    # Server errors (5xx)
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # MCP-specific errors (1xxx)
    TOOL_NOT_FOUND = "TOOL_NOT_FOUND"
    TOOL_EXECUTION_ERROR = "TOOL_EXECUTION_ERROR"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    PROTOCOL_ERROR = "PROTOCOL_ERROR"


# =============================================================================
# Error Response Creation
# =============================================================================

def create_error_response(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized error response.
    
    Args:
        code: Error code from ErrorCode class
        message: Human-readable error message
        request_id: Optional request ID for correlation
        details: Optional additional error details
    
    Returns:
        Dictionary with standardized error format
    """
    error_response = {
        "code": code,
        "message": message,
    }
    
    if details:
        error_response["details"] = details
    
    return {"error": error_response}


def log_error(
    code: str,
    message: str,
    request_id: Optional[str] = None,
    exc_info: bool = False
) -> None:
    """
    Log error with appropriate severity level.
    
    Args:
        code: Error code from ErrorCode class
        message: Error message
        request_id: Optional request ID for correlation
        exc_info: Whether to include exception traceback
    """
    # Determine log level based on error code
    if code in [ErrorCode.INTERNAL_ERROR, ErrorCode.SERVICE_UNAVAILABLE, ErrorCode.PROVIDER_ERROR]:
        # Server errors - ERROR level
        log_msg = f"[{code}] {message}"
        if request_id:
            log_msg = f"[req:{request_id}] {log_msg}"
        logger.error(log_msg, exc_info=exc_info)
        
    elif code in [ErrorCode.TOOL_EXECUTION_ERROR, ErrorCode.TIMEOUT]:
        # Execution errors - WARNING level
        log_msg = f"[{code}] {message}"
        if request_id:
            log_msg = f"[req:{request_id}] {log_msg}"
        logger.warning(log_msg, exc_info=exc_info)
        
    elif code in [ErrorCode.VALIDATION_ERROR, ErrorCode.NOT_FOUND, ErrorCode.TOOL_NOT_FOUND]:
        # Client errors - INFO level
        log_msg = f"[{code}] {message}"
        if request_id:
            log_msg = f"[req:{request_id}] {log_msg}"
        logger.info(log_msg)
        
    else:
        # Unknown error code - WARNING level
        log_msg = f"[{code}] {message}"
        if request_id:
            log_msg = f"[req:{request_id}] {log_msg}"
        logger.warning(log_msg, exc_info=exc_info)


# =============================================================================
# Custom Exception Classes
# =============================================================================

class MCPError(Exception):
    """
    Base exception for MCP server errors.
    
    All custom exceptions should inherit from this class.
    """
    
    def __init__(
        self,
        message: str,
        code: str = ErrorCode.INTERNAL_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_response(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert exception to error response format."""
        return create_error_response(
            code=self.code,
            message=self.message,
            request_id=request_id,
            details=self.details
        )


class ToolNotFoundError(MCPError):
    """Raised when a requested tool is not found."""
    
    def __init__(self, tool_name: str, available_tools: Optional[list] = None):
        message = f"Tool not found: {tool_name}"
        details = {}
        if available_tools:
            details["available_tools"] = available_tools
        super().__init__(message, ErrorCode.TOOL_NOT_FOUND, details)
        self.tool_name = tool_name


class ToolExecutionError(MCPError):
    """Raised when tool execution fails."""
    
    def __init__(self, tool_name: str, original_error: Exception):
        message = f"Tool execution failed: {tool_name}"
        details = {"original_error": str(original_error)}
        super().__init__(message, ErrorCode.TOOL_EXECUTION_ERROR, details)
        self.tool_name = tool_name
        self.original_error = original_error


class ValidationError(MCPError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        full_message = f"Validation failed for '{field}': {message}"
        details = {"field": field}
        if value is not None:
            details["value"] = str(value)
        super().__init__(full_message, ErrorCode.VALIDATION_ERROR, details)
        self.field = field


class ProviderError(MCPError):
    """Raised when AI provider fails."""
    
    def __init__(self, provider: str, original_error: Exception):
        message = f"Provider error ({provider}): {str(original_error)}"
        details = {"provider": provider, "original_error": str(original_error)}
        super().__init__(message, ErrorCode.PROVIDER_ERROR, details)
        self.provider = provider
        self.original_error = original_error


class TimeoutError(MCPError):
    """Raised when operation times out."""
    
    def __init__(self, operation: str, timeout_seconds: float):
        message = f"Operation '{operation}' timed out after {timeout_seconds}s"
        details = {"operation": operation, "timeout_seconds": timeout_seconds}
        super().__init__(message, ErrorCode.TIMEOUT, details)
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class OverCapacityError(MCPError):
    """Raised when server is over capacity."""
    
    def __init__(self, resource: str, current: int, maximum: int):
        message = f"Over capacity: {resource} ({current}/{maximum})"
        details = {"resource": resource, "current": current, "maximum": maximum}
        super().__init__(message, ErrorCode.OVER_CAPACITY, details)
        self.resource = resource


# =============================================================================
# Error Handling Utilities
# =============================================================================

def handle_exception(
    exc: Exception,
    request_id: Optional[str] = None,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convert any exception to standardized error response.
    
    Args:
        exc: Exception to handle
        request_id: Optional request ID for correlation
        context: Optional context description (e.g., "tool execution")
    
    Returns:
        Standardized error response dictionary
    """
    # If it's already an MCPError, use its response
    if isinstance(exc, MCPError):
        log_error(exc.code, exc.message, request_id, exc_info=True)
        return exc.to_response(request_id)
    
    # Handle asyncio.TimeoutError
    if isinstance(exc, __builtins__.TimeoutError):
        error = TimeoutError(context or "operation", timeout_seconds=0)
        log_error(error.code, error.message, request_id, exc_info=True)
        return error.to_response(request_id)
    
    # Handle generic exceptions
    message = f"Unexpected error"
    if context:
        message = f"Unexpected error during {context}"
    message = f"{message}: {str(exc)}"
    
    log_error(ErrorCode.INTERNAL_ERROR, message, request_id, exc_info=True)
    
    return create_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
        request_id=request_id,
        details={"internal_error": str(exc)}
    )


def create_tool_error_response(
    request_id: str,
    error: Exception,
    tool_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create error response for tool call failures.
    
    Args:
        request_id: Request ID for correlation
        error: Exception that occurred
        tool_name: Optional tool name for context
    
    Returns:
        Dictionary with op="call_tool_res" and error field
    """
    error_response = handle_exception(
        error,
        request_id=request_id,
        context=f"tool execution ({tool_name})" if tool_name else "tool execution"
    )
    
    return {
        "op": "call_tool_res",
        "request_id": request_id,
        **error_response
    }

