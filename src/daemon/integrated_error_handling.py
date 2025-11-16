"""
Integration Module: Enhanced Error Handling with Existing Error System

This module provides seamless integration between:
1. Existing error_handling.py (standardized error codes and responses)
2. Enhanced error_handling.py (categorization, metrics, and alerting)
3. Error capture system (monitoring and logging)

This ensures backward compatibility while adding advanced error management.
"""

import logging
from typing import Any, Dict, Optional, Union
from datetime import datetime, timezone

# Import existing error handling
from src.daemon.error_handling import (
    ErrorCode, log_error, create_error_response, MCPError, 
    ToolNotFoundError, ToolExecutionError, ProviderError, TimeoutError
)

# Import enhanced error handling
from src.daemon.enhanced_error_handling import (
    ErrorCategory, ErrorSeverity, ErrorMetrics, 
    log_enhanced_error, get_enhanced_handler, EnhancedErrorHandler
)

logger = logging.getLogger(__name__)


class IntegratedErrorHandler:
    """Integrated error handler that combines both error systems."""
    
    def __init__(self):
        self.enhanced_handler = get_enhanced_handler()
        
    def log_integrated_error(
        self,
        code: str,
        message: str,
        request_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        provider_name: Optional[str] = None,
        exception: Optional[Exception] = None,
        response_time_ms: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ) -> Dict[str, Any]:
        """
        Log error using both systems for maximum compatibility and insight.
        
        This function:
        1. Creates standard error response (backward compatibility)
        2. Logs enhanced error with categorization and metrics
        3. Triggers alerting if necessary
        4. Returns standardized response format
        """
        
        # Enhance context with correlation information
        enhanced_context = context or {}
        if request_id:
            enhanced_context["request_id"] = request_id
        if tool_name:
            enhanced_context["tool_name"] = tool_name
        if provider_name:
            enhanced_context["provider_name"] = provider_name
        if response_time_ms:
            enhanced_context["response_time_ms"] = response_time_ms
            
        # Log enhanced error for categorization and metrics
        enhanced_metrics = self.enhanced_handler.log_enhanced_error(
            error_code=code,
            message=message,
            request_id=request_id,
            tool_name=tool_name,
            provider_name=provider_name,
            exception=exception,
            response_time_ms=response_time_ms,
            context=enhanced_context,
            exc_info=exc_info
        )
        
        # Log using existing system for backward compatibility
        log_error(code, message, request_id, exc_info=exc_info)
        
        # Create standardized error response
        error_response = create_error_response(
            code=code,
            message=message,
            request_id=request_id,
            details=enhanced_context
        )
        
        return error_response
    
    def handle_tool_execution_error(
        self,
        tool_name: str,
        original_error: Exception,
        request_id: Optional[str] = None,
        response_time_ms: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Handle tool execution errors with enhanced categorization.
        
        Args:
            tool_name: Name of the tool that failed
            original_error: The original exception
            request_id: Optional request ID for correlation
            response_time_ms: Optional response time
            
        Returns:
            Standardized error response
        """
        
        # Determine appropriate error code and message
        if isinstance(original_error, ToolNotFoundError):
            # Already handled tool not found
            return original_error.to_response(request_id)
        
        if isinstance(original_error, TimeoutError):
            code = ErrorCode.TIMEOUT
            message = f"Tool execution timed out: {tool_name}"
        elif isinstance(original_error, ProviderError):
            code = ErrorCode.PROVIDER_ERROR
            message = f"Provider error during tool execution: {tool_name}"
        else:
            code = ErrorCode.TOOL_EXECUTION_ERROR
            message = f"Tool execution failed: {tool_name}"
        
        # Create context for enhanced logging
        context = {
            "tool_name": tool_name,
            "original_error_type": type(original_error).__name__,
            "original_error_message": str(original_error)
        }
        
        return self.log_integrated_error(
            code=code,
            message=message,
            request_id=request_id,
            tool_name=tool_name,
            exception=original_error,
            response_time_ms=response_time_ms,
            context=context,
            exc_info=True
        )
    
    def handle_provider_error(
        self,
        provider_name: str,
        original_error: Exception,
        request_id: Optional[str] = None,
        response_time_ms: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle provider/API errors with enhanced categorization.
        
        Args:
            provider_name: Name of the provider (e.g., "kimi", "glm")
            original_error: The original exception
            request_id: Optional request ID for correlation
            response_time_ms: Optional response time
            context: Additional context information
            
        Returns:
            Standardized error response
        """
        
        message = f"Provider error ({provider_name}): {str(original_error)}"
        
        enhanced_context = context or {}
        enhanced_context.update({
            "provider_name": provider_name,
            "original_error_type": type(original_error).__name__,
            "original_error_message": str(original_error)
        })
        
        return self.log_integrated_error(
            code=ErrorCode.PROVIDER_ERROR,
            message=message,
            request_id=request_id,
            provider_name=provider_name,
            exception=original_error,
            response_time_ms=response_time_ms,
            context=enhanced_context,
            exc_info=True
        )
    
    def get_error_dashboard_data(self) -> Dict[str, Any]:
        """Get data for error monitoring dashboard."""
        return self.enhanced_handler.get_error_summary()


# Global integrated error handler instance
_integrated_handler: Optional[IntegratedErrorHandler] = None


def get_integrated_handler() -> IntegratedErrorHandler:
    """Get the global integrated error handler instance."""
    global _integrated_handler
    if _integrated_handler is None:
        _integrated_handler = IntegratedErrorHandler()
    return _integrated_handler


# Convenience functions for common use cases

def log_tool_error(
    tool_name: str,
    error: Exception,
    request_id: Optional[str] = None,
    response_time_ms: Optional[float] = None
) -> Dict[str, Any]:
    """Convenience function for logging tool execution errors."""
    handler = get_integrated_handler()
    return handler.handle_tool_execution_error(tool_name, error, request_id, response_time_ms)


def log_provider_error(
    provider_name: str,
    error: Exception,
    request_id: Optional[str] = None,
    response_time_ms: Optional[float] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for logging provider errors."""
    handler = get_integrated_handler()
    return handler.handle_provider_error(provider_name, error, request_id, response_time_ms, context)


def log_server_error(
    message: str,
    request_id: Optional[str] = None,
    exception: Optional[Exception] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for logging server errors."""
    handler = get_integrated_handler()
    return handler.log_integrated_error(
        code=ErrorCode.INTERNAL_ERROR,
        message=message,
        request_id=request_id,
        exception=exception,
        context=context,
        exc_info=exception is not None
    )


def log_client_error(
    message: str,
    code: str = ErrorCode.INVALID_REQUEST,
    request_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience function for logging client errors."""
    handler = get_integrated_handler()
    return handler.log_integrated_error(
        code=code,
        message=message,
        request_id=request_id,
        context=context,
        exc_info=False
    )


# Export the integrated handler for easy import
__all__ = [
    'IntegratedErrorHandler',
    'get_integrated_handler',
    'log_tool_error',
    'log_provider_error', 
    'log_server_error',
    'log_client_error',
    'get_error_dashboard_data'
]
