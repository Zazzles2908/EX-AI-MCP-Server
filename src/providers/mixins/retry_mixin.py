"""
Retry Mixin for Provider Classes

Provides configurable retry logic with exponential backoff for API calls.
Extracted from openai_compatible.py to eliminate code duplication.
"""

import logging
import time
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)


class RetryMixin:
    """
    Mixin providing retry logic with exponential backoff.
    
    This mixin handles:
    - Configurable retry attempts
    - Progressive delay backoff
    - Error retryability checking
    - Logging and progress tracking
    """

    DEFAULT_MAX_RETRIES = 4
    DEFAULT_RETRY_DELAYS = [1, 3, 5, 8]  # Progressive delays in seconds

    def _execute_with_retry(
        self,
        operation: Callable[[], Any],
        operation_name: str,
        max_retries: Optional[int] = None,
        retry_delays: Optional[list[float]] = None,
        is_retryable_fn: Optional[Callable[[Exception], bool]] = None,
    ) -> Any:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Callable that performs the operation
            operation_name: Name of operation for logging
            max_retries: Maximum number of retry attempts (default: 4)
            retry_delays: List of delays between retries (default: [1, 3, 5, 8])
            is_retryable_fn: Function to check if error is retryable (default: _is_error_retryable)
            
        Returns:
            Result from successful operation
            
        Raises:
            RuntimeError: If all retries fail
        """
        if max_retries is None:
            max_retries = self.DEFAULT_MAX_RETRIES
        if retry_delays is None:
            retry_delays = self.DEFAULT_RETRY_DELAYS
        if is_retryable_fn is None:
            is_retryable_fn = getattr(self, '_is_error_retryable', lambda e: True)

        last_exception = None
        actual_attempts = 0

        for attempt in range(max_retries):
            actual_attempts = attempt + 1
            try:
                return operation()
            except Exception as e:
                last_exception = e
                
                # Check if this is a retryable error
                is_retryable = is_retryable_fn(e)
                
                if is_retryable and attempt < max_retries - 1:
                    delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                    logger.warning(
                        f"Retryable error for {operation_name}, "
                        f"attempt {actual_attempts}/{max_retries}: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    break

        # If we get here, all retries failed
        error_msg = (
            f"{operation_name} error after {actual_attempts} "
            f"attempt{'s' if actual_attempts > 1 else ''}: {str(last_exception)}"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from last_exception

