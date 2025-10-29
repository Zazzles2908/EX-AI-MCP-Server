"""
Async Upload Wrapper Decorator

Provides feature flag-controlled async/sync execution with:
- Automatic fallback on errors
- Metrics collection
- Retry logic
- Timeout handling

Usage:
    @async_upload_wrapper
    def upload_file(file_path: str) -> str:
        # Sync implementation
        return upload_sync(file_path)
    
    # Will automatically use async if enabled and rollout percentage allows
    result = upload_file(file_path)
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Callable, Any, Optional, Type, Tuple

from tools.config.async_upload_config import get_config
from tools.monitoring.async_upload_metrics import get_metrics_collector, UploadMetrics

logger = logging.getLogger(__name__)


class FallbackConfig:
    """Configuration for fallback behavior"""
    RETRYABLE_ERRORS = (TimeoutError, ConnectionError, OSError, asyncio.TimeoutError)
    MAX_RETRIES = 2


def async_upload_wrapper(
    func: Callable,
    request_id: Optional[str] = None,
    file_size_mb: float = 0.0,
    provider: str = "unknown"
) -> Callable:
    """
    Decorator to add async capability with feature flags.
    
    Args:
        func: Sync function to wrap
        request_id: Optional request identifier for consistent rollout
        file_size_mb: File size in MB (for metrics)
        provider: Upload provider name (for metrics)
    
    Returns:
        Wrapped function that uses async if enabled
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        config = get_config()
        metrics_collector = get_metrics_collector()
        
        start_time = time.time()
        execution_type = "sync"
        fallback_used = False
        error_type = None
        
        try:
            # Check if async should be used
            if config.enabled and config.should_use_async(request_id):
                execution_type = "async"
                
                # Try async execution with retries
                for attempt in range(config.max_retries + 1):
                    try:
                        logger.debug(f"Async execution attempt {attempt + 1}/{config.max_retries + 1}")
                        
                        # Create event loop if needed
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_closed():
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                        
                        # Run async function with timeout
                        result = loop.run_until_complete(
                            asyncio.wait_for(
                                _async_execute(func, *args, **kwargs),
                                timeout=config.timeout_seconds
                            )
                        )
                        
                        # Success
                        duration_ms = (time.time() - start_time) * 1000
                        metrics_collector.record_upload(UploadMetrics(
                            execution_type=execution_type,
                            success=True,
                            duration_ms=duration_ms,
                            file_size_mb=file_size_mb,
                            provider=provider,
                            request_id=request_id
                        ))
                        return result
                        
                    except Exception as e:
                        error_type = type(e).__name__
                        
                        # Check if we should retry
                        if attempt < config.max_retries and isinstance(e, FallbackConfig.RETRYABLE_ERRORS):
                            logger.warning(
                                f"Async attempt {attempt + 1} failed with {error_type}, "
                                f"retrying: {e}"
                            )
                            continue
                        
                        # No more retries or non-retryable error
                        if config.fallback_on_error:
                            logger.warning(
                                f"Async execution failed after {attempt + 1} attempts, "
                                f"falling back to sync: {e}"
                            )
                            fallback_used = True
                            execution_type = "sync_fallback"
                            break
                        else:
                            # Record failure and re-raise
                            duration_ms = (time.time() - start_time) * 1000
                            metrics_collector.record_upload(UploadMetrics(
                                execution_type=execution_type,
                                success=False,
                                duration_ms=duration_ms,
                                error_type=error_type,
                                file_size_mb=file_size_mb,
                                provider=provider,
                                request_id=request_id
                            ))
                            raise
            
            # Sync execution (either fallback or async disabled)
            result = func(*args, **kwargs)
            
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_upload(UploadMetrics(
                execution_type=execution_type,
                success=True,
                duration_ms=duration_ms,
                fallback_used=fallback_used,
                file_size_mb=file_size_mb,
                provider=provider,
                request_id=request_id
            ))
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            duration_ms = (time.time() - start_time) * 1000
            
            metrics_collector.record_upload(UploadMetrics(
                execution_type=execution_type,
                success=False,
                duration_ms=duration_ms,
                error_type=error_type,
                fallback_used=fallback_used,
                file_size_mb=file_size_mb,
                provider=provider,
                request_id=request_id
            ))
            raise
    
    return wrapper


async def _async_execute(func: Callable, *args, **kwargs) -> Any:
    """
    Execute a sync function in an async context using thread pool.
    
    Args:
        func: Sync function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        Function result
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)

