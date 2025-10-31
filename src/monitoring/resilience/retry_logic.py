"""
Retry Logic with Exponential Backoff

Implements retry logic with exponential backoff for resilient operations.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-10-31
"""

import logging
import random
import time
from typing import Any, Callable, Optional, Type

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry logic."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: Optional[list] = None,
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_attempts: Maximum number of attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter
            retryable_exceptions: List of exceptions to retry on
        """
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or [Exception]


class RetryLogic:
    """Retry logic with exponential backoff."""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """
        Initialize retry logic.
        
        Args:
            config: Retry configuration
        """
        self.config = config or RetryConfig()
        self.attempt_count = 0
        self.last_error: Optional[Exception] = None
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries exhausted
        """
        self.attempt_count = 0
        self.last_error = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            self.attempt_count = attempt
            
            try:
                result = func(*args, **kwargs)
                if attempt > 1:
                    logger.info(f"Succeeded on attempt {attempt}/{self.config.max_attempts}")
                return result
            
            except Exception as e:
                self.last_error = e
                
                # Check if exception is retryable
                if not self._is_retryable(e):
                    logger.error(f"Non-retryable exception: {e}")
                    raise
                
                # Check if we have more attempts
                if attempt >= self.config.max_attempts:
                    logger.error(
                        f"All {self.config.max_attempts} attempts failed. "
                        f"Last error: {e}"
                    )
                    raise
                
                # Calculate delay
                delay = self._calculate_delay(attempt)
                logger.warning(
                    f"Attempt {attempt}/{self.config.max_attempts} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                
                time.sleep(delay)
        
        # Should not reach here
        raise self.last_error or Exception("Retry logic failed")
    
    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable."""
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay with exponential backoff.
        
        Args:
            attempt: Current attempt number (1-based)
            
        Returns:
            Delay in seconds
        """
        # Exponential backoff: initial_delay * (base ^ (attempt - 1))
        delay = self.config.initial_delay * (
            self.config.exponential_base ** (attempt - 1)
        )
        
        # Cap at max delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter if enabled
        if self.config.jitter:
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            delay += jitter
        
        return delay
    
    def get_metrics(self) -> dict:
        """Get retry metrics."""
        return {
            'attempt_count': self.attempt_count,
            'max_attempts': self.config.max_attempts,
            'last_error': str(self.last_error) if self.last_error else None,
            'config': {
                'initial_delay': self.config.initial_delay,
                'max_delay': self.config.max_delay,
                'exponential_base': self.config.exponential_base,
                'jitter': self.config.jitter,
            }
        }


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            config = RetryConfig(
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                jitter=jitter,
            )
            retry = RetryLogic(config)
            return retry.execute(func, *args, **kwargs)
        return wrapper
    return decorator

