"""
Centralized Error Capture System

Provides decorators and utilities for capturing errors across all system layers
and recording them in the monitoring system for visibility.

Created: 2025-10-24
EXAI Consultation: b8fa5032-ff61-4020-9892-fe07ee438a3c
Phase: 1 - Critical Monitoring Fixes
"""

import functools
import traceback
import logging
import sys
from typing import Callable, Optional, Dict, Any
from utils.monitoring import get_monitor

logger = logging.getLogger(__name__)


def capture_errors(
    connection_type: str,
    script_name: Optional[str] = None,
    context_extractor: Optional[Callable] = None,
    record_success: bool = False
):
    """
    Decorator to capture and record errors in the monitoring system.
    
    This decorator:
    1. Captures exceptions from the decorated function
    2. Records them in the monitoring system BEFORE logging
    3. Re-raises the exception to maintain existing error handling flow
    4. Optionally records successful executions for performance tracking
    
    Args:
        connection_type: Type of connection (websocket, redis, supabase, kimi, glm)
        script_name: Name of the script (auto-detected if None)
        context_extractor: Function to extract additional context from args/kwargs
        record_success: Whether to record successful executions (default: False)
    
    Example:
        @capture_errors(connection_type="glm", record_success=True)
        def generate_content(model, messages):
            # ... implementation ...
            pass
    
    Example with context extractor:
        def extract_tool_context(*args, **kwargs):
            return {
                "tool_name": kwargs.get("tool_name"),
                "parameters": kwargs.get("parameters")
            }
        
        @capture_errors(
            connection_type="websocket",
            context_extractor=extract_tool_context
        )
        def execute_tool(tool_name, parameters):
            # ... implementation ...
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Auto-detect script name from function module
        nonlocal script_name
        if script_name is None:
            script_name = func.__module__.split('.')[-1] + '.py'
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            monitor = get_monitor()
            function_name = func.__name__
            start_time = None
            
            # Extract context if extractor provided
            context = {}
            if context_extractor:
                try:
                    context = context_extractor(*args, **kwargs) or {}
                except Exception as e:
                    logger.warning(f"Context extractor failed: {e}")
            
            try:
                # Track start time for performance monitoring
                import time
                start_time = time.time()
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Record success if requested
                if record_success:
                    response_time_ms = (time.time() - start_time) * 1000
                    monitor.record_event(
                        connection_type=connection_type,
                        direction="success",
                        script_name=script_name,
                        function_name=function_name,
                        data_size_bytes=sys.getsizeof(result) if result else 0,
                        response_time_ms=response_time_ms,
                        error=None,
                        metadata=context
                    )
                
                return result
                
            except Exception as e:
                # Calculate response time (time to error)
                response_time_ms = None
                if start_time:
                    response_time_ms = (time.time() - start_time) * 1000
                
                # Get full error details
                error_type = type(e).__name__
                error_message = str(e)
                error_traceback = traceback.format_exc()
                
                # Build error metadata
                error_metadata = {
                    "error_type": error_type,
                    "error_message": error_message,
                    "error_traceback": error_traceback,
                    **context  # Include extracted context
                }
                
                # CRITICAL: Record error BEFORE logging
                # This ensures monitoring gets the error even if logging fails
                try:
                    monitor.record_event(
                        connection_type=connection_type,
                        direction="error",
                        script_name=script_name,
                        function_name=function_name,
                        data_size_bytes=0,
                        response_time_ms=response_time_ms,
                        error=f"{error_type}: {error_message}",
                        metadata=error_metadata
                    )
                except Exception as record_error:
                    # If recording fails, log it but don't let it break the flow
                    logger.error(f"Failed to record error in monitoring: {record_error}")
                
                # Re-raise the original exception to maintain existing error handling
                raise
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            monitor = get_monitor()
            function_name = func.__name__
            start_time = None
            
            # Extract context if extractor provided
            context = {}
            if context_extractor:
                try:
                    context = context_extractor(*args, **kwargs) or {}
                except Exception as e:
                    logger.warning(f"Context extractor failed: {e}")
            
            try:
                # Track start time for performance monitoring
                import time
                start_time = time.time()
                
                # Execute the async function
                result = await func(*args, **kwargs)
                
                # Record success if requested
                if record_success:
                    response_time_ms = (time.time() - start_time) * 1000
                    monitor.record_event(
                        connection_type=connection_type,
                        direction="success",
                        script_name=script_name,
                        function_name=function_name,
                        data_size_bytes=sys.getsizeof(result) if result else 0,
                        response_time_ms=response_time_ms,
                        error=None,
                        metadata=context
                    )
                
                return result
                
            except Exception as e:
                # Calculate response time (time to error)
                response_time_ms = None
                if start_time:
                    response_time_ms = (time.time() - start_time) * 1000
                
                # Get full error details
                error_type = type(e).__name__
                error_message = str(e)
                error_traceback = traceback.format_exc()
                
                # Build error metadata
                error_metadata = {
                    "error_type": error_type,
                    "error_message": error_message,
                    "error_traceback": error_traceback,
                    **context  # Include extracted context
                }
                
                # CRITICAL: Record error BEFORE logging
                try:
                    monitor.record_event(
                        connection_type=connection_type,
                        direction="error",
                        script_name=script_name,
                        function_name=function_name,
                        data_size_bytes=0,
                        response_time_ms=response_time_ms,
                        error=f"{error_type}: {error_message}",
                        metadata=error_metadata
                    )
                except Exception as record_error:
                    logger.error(f"Failed to record error in monitoring: {record_error}")
                
                # Re-raise the original exception
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Context extractors for common use cases

def extract_tool_context(*args, **kwargs) -> Dict[str, Any]:
    """Extract context from tool execution"""
    return {
        "tool_name": kwargs.get("tool_name") or (args[0] if args else None),
        "parameters": kwargs.get("arguments") or kwargs.get("parameters"),
    }


def extract_provider_context(*args, **kwargs) -> Dict[str, Any]:
    """Extract context from provider API calls"""
    return {
        "model": kwargs.get("model"),
        "messages": len(kwargs.get("messages", [])) if kwargs.get("messages") else None,
        "stream": kwargs.get("stream"),
        "temperature": kwargs.get("temperature"),
    }


def extract_storage_context(*args, **kwargs) -> Dict[str, Any]:
    """Extract context from storage operations"""
    return {
        "operation": kwargs.get("operation") or (args[0] if args else None),
        "table": kwargs.get("table"),
        "conversation_id": kwargs.get("conversation_id"),
    }


def extract_websocket_context(*args, **kwargs) -> Dict[str, Any]:
    """Extract context from WebSocket operations"""
    return {
        "message_type": kwargs.get("message_type"),
        "request_id": kwargs.get("request_id"),
        "client_id": kwargs.get("client_id"),
    }

