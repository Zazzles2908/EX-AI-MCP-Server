"""
Storage Telemetry Module

Performance tracking and monitoring for Supabase storage operations.
Provides decorators for tracking performance, data sizes, and errors.
"""

import json
import time
import logging
from functools import wraps
from typing import Any, Optional

# Import monitoring utilities
from utils.monitoring import record_supabase_event
from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)


def track_storage_performance(operation_type: Optional[str] = None):
    """
    Decorator to track performance of storage operations.

    Tracks execution time, data sizes, and errors for monitoring.
    Automatically determines operation type from function name if not specified.

    Args:
        operation_type: Override operation type ("query" or "write")
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            start = time.time()
            result = None
            error = None

            try:
                result = func(self, *args, **kwargs)
                duration = time.time() - start

                # Log performance metrics
                logger.debug(f"{func.__name__} completed in {duration:.3f}s")

                # Alert on slow operations (> 500ms)
                if duration > 0.5:
                    logger.warning(f"Slow operation: {func.__name__} took {duration:.3f}s")

                # Determine operation type
                if operation_type:
                    op_type = operation_type
                elif "get" in func.__name__ or "fetch" in func.__name__:
                    op_type = "query"
                else:
                    op_type = "write"

                # Calculate request size
                request_size = len(json.dumps(kwargs).encode('utf-8')) if kwargs else 0

                # Calculate response size
                response_size = 0
                if result:
                    if isinstance(result, (list, dict)):
                        try:
                            response_size = len(json.dumps(result).encode('utf-8'))
                        except (TypeError, ValueError):
                            response_size = len(str(result).encode('utf-8'))

                # Use response size if available, otherwise use request size
                data_size = response_size if response_size > 0 else request_size

                # Record telemetry event
                record_supabase_event(
                    direction="receive" if op_type == "query" else "send",
                    function_name=f"SupabaseStorageManager.{func.__name__}",
                    data_size=data_size,
                    response_time_ms=duration * 1000,
                    metadata={
                        "operation": op_type,
                        "slow": duration > 0.5,
                        "request_size": request_size,
                        "response_size": response_size,
                        "timestamp": log_timestamp()
                    }
                )

                return result

            except Exception as e:
                error = str(e)
                duration = time.time() - start

                # Enhanced error capture with full traceback
                import traceback
                error_type = type(e).__name__
                error_traceback = traceback.format_exc()

                # Calculate request size for error
                request_size = len(str(kwargs).encode('utf-8')) if kwargs else 0

                # Record error event
                record_supabase_event(
                    direction="error",
                    function_name=f"SupabaseStorageManager.{func.__name__}",
                    data_size=request_size,
                    response_time_ms=duration * 1000,
                    error=f"{error_type}: {error}",
                    metadata={
                        "error_type": error_type,
                        "error_message": error,
                        "error_traceback": error_traceback,
                        "request_size": request_size,
                        "timestamp": log_timestamp()
                    }
                )

                raise

        return wrapper
    return decorator
