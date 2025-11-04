"""
Storage Circuit Breaker Module

Provides circuit breaker protection and retry logic for Supabase storage operations.
Implements resilience patterns to prevent cascading failures.
"""

import os
import time
import logging
from typing import Tuple, Optional, Any, Callable
from functools import wraps

# Import circuit breaker manager
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

# Import custom exceptions
from src.storage.storage_exceptions import RetryableError, NonRetryableError

logger = logging.getLogger(__name__)


class StorageCircuitBreaker:
    """Circuit breaker wrapper for Supabase storage operations."""

    def __init__(self):
        self.breaker = circuit_breaker_manager.get_breaker('supabase')

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: When circuit is open
            RetryableError: For temporary failures
            NonRetryableError: For permanent failures
        """
        try:
            # Wrap with circuit breaker
            return self.breaker(func)(*args, **kwargs)

        except pybreaker.CircuitBreakerError:
            # Circuit breaker is OPEN - service unavailable
            logger.error(f"Supabase circuit breaker OPEN - cannot execute {func.__name__}")
            raise NonRetryableError("Service temporarily unavailable (circuit breaker open)")

        except Exception as e:
            # Classify error and raise appropriate exception
            is_retryable, _ = self._classify_error(e)
            if is_retryable:
                raise RetryableError(str(e))
            else:
                raise NonRetryableError(str(e))

    def _classify_error(self, error: Exception) -> Tuple[bool, str]:
        """
        Classify error as retryable or non-retryable.

        Args:
            error: Exception to classify

        Returns:
            Tuple of (is_retryable, error_category)
        """
        error_str = str(error).lower()
        error_type = type(error).__name__

        # Non-retryable errors (permanent failures)
        non_retryable_indicators = [
            "authentication failed",
            "invalid api key",
            "permission denied",
            "not authorized",
            "resource not found",
            "schema violation",
            "unique constraint",
            "duplicate key",
            "invalid input syntax",
            "column does not exist",
            "table does not exist",
            "invalid credentials",
            "jwt expired",
            "invalid jwt",
            "422",  # Unprocessable entity
            "400",  # Bad request
            "401",  # Unauthorized
            "403",  # Forbidden
            "404",  # Not found
        ]

        # Retryable errors (temporary failures)
        retryable_indicators = [
            "connection refused",
            "connection reset",
            "timeout",
            "timed out",
            "temporary failure",
            "service unavailable",
            "internal server error",
            "bad gateway",
            "gateway timeout",
            "rate limit",
            "too many requests",
            "503",  # Service unavailable
            "502",  # Bad gateway
            "504",  # Gateway timeout
            "429",  # Too many requests
            "500",  # Internal server error
        ]

        # Check for non-retryable errors first
        for indicator in non_retryable_indicators:
            if indicator in error_str:
                return False, "non_retryable"

        # Check for retryable errors
        for indicator in retryable_indicators:
            if indicator in error_str:
                return True, "retryable"

        # Network errors are typically retryable
        if error_type in ('ConnectionError', 'TimeoutError', 'OSError'):
            return True, "network"

        # Default to non-retryable for unknown errors
        logger.debug(f"Unclassified error type: {error_type}, treating as non-retryable")
        return False, "unknown"


def with_circuit_breaker(func: Callable) -> Callable:
    """
    Decorator to add circuit breaker protection to storage operations.

    Args:
        func: Function to protect

    Returns:
        Wrapped function with circuit breaker protection
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        circuit_breaker = StorageCircuitBreaker()
        return circuit_breaker.call(func, self, *args, **kwargs)

    return wrapper


def with_retry(max_retries: int = 3, base_delay: float = 0.1, max_delay: float = 5.0):
    """
    Decorator to add retry logic with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(self, *args, **kwargs)

                except RetryableError as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == max_retries:
                        logger.error(f"Operation failed after {max_retries} retries: {e}")
                        raise NonRetryableError(f"Operation failed after {max_retries} retries: {e}")

                    # Calculate delay with exponential backoff and jitter
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = delay * 0.1 * (2 * attempt - 1)  # Add some randomness
                    delay = max(0, delay + jitter)

                    logger.warning(f"Retryable error on attempt {attempt + 1}/{max_retries + 1}, retrying in {delay:.2f}s: {e}")
                    time.sleep(delay)

                except NonRetryableError:
                    # Don't retry non-retryable errors
                    raise

            # Should never reach here
            if last_exception:
                raise last_exception

        return wrapper
    return decorator
