"""
Resilience patterns for file upload operations.

Batch 9: Enhanced Reliability (2025-11-02)
- Task 9.1: Retry Logic with exponential backoff and jitter
- Task 9.2: Circuit Breaker Pattern with state management

EXAI Validation: Continuation ID 2990f86f-4ce1-457d-9398-516d599e5902
Model: Kimi Thinking Preview (deep analysis mode)

Key Features:
- Provider-specific error handling (429, 500, 502, 503, 504)
- Full jitter implementation (random.uniform(0, delay))
- Circuit breaker state persistence and provider isolation
- Comprehensive logging for monitoring
- Configurable via environment variables
"""

import asyncio
import random
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIGURATION CLASSES
# ============================================================================

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = None,
        base_delay: float = None,
        max_delay: float = None,
        exponential_base: float = None,
        jitter: bool = None
    ):
        # Load from environment with defaults
        self.max_attempts = max_attempts or int(os.getenv('RETRY_MAX_ATTEMPTS', '3'))
        self.base_delay = base_delay or float(os.getenv('RETRY_BASE_DELAY', '1.0'))
        self.max_delay = max_delay or float(os.getenv('RETRY_MAX_DELAY', '60.0'))
        self.exponential_base = exponential_base or float(os.getenv('RETRY_EXPONENTIAL_BASE', '2.0'))
        self.jitter = jitter if jitter is not None else os.getenv('RETRY_JITTER', 'true').lower() == 'true'


class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""
    
    def __init__(
        self,
        failure_threshold: int = None,
        success_threshold: int = None,
        timeout: float = None,
        half_open_max_calls: int = None
    ):
        # Load from environment with defaults
        self.failure_threshold = failure_threshold or int(os.getenv('CIRCUIT_BREAKER_FAILURE_THRESHOLD', '5'))
        self.success_threshold = success_threshold or int(os.getenv('CIRCUIT_BREAKER_SUCCESS_THRESHOLD', '2'))
        self.timeout = timeout or float(os.getenv('CIRCUIT_BREAKER_TIMEOUT', '60.0'))
        self.half_open_max_calls = half_open_max_calls or int(os.getenv('CIRCUIT_BREAKER_HALF_OPEN_MAX_CALLS', '1'))


# ============================================================================
# RETRY HANDLER (Task 9.1)
# ============================================================================

class RetryHandler:
    """Handles retry logic with exponential backoff and full jitter.
    
    EXAI Adjustment: Provider-specific error handling and full jitter implementation.
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.enabled = os.getenv('RESILIENCE_RETRY_ENABLED', 'true').lower() == 'true'
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and full jitter.
        
        EXAI Adjustment: Use full jitter (random.uniform(0, delay)) instead of simple random.
        This provides better distribution and prevents thundering herd.
        """
        delay = min(
            self.config.base_delay * (self.config.exponential_base ** attempt),
            self.config.max_delay
        )
        
        if self.config.jitter:
            # Full jitter: random between 0 and calculated delay
            delay = random.uniform(0, delay)
        
        return delay
    
    def _should_retry(self, error: Exception) -> bool:
        """Determine if error is retryable.
        
        EXAI Adjustment: Provider-specific error handling for HTTP status codes.
        Retryable: 429 (rate limit), 500, 502, 503, 504 (server errors)
        Non-retryable: 400, 401, 403, 404 (client errors)
        """
        # Check HTTP status codes if available
        if hasattr(error, 'status_code'):
            retryable_codes = [429, 500, 502, 503, 504]
            return error.status_code in retryable_codes
        
        # Check exception types
        retryable_errors = (
            ConnectionError,
            TimeoutError,
            asyncio.TimeoutError,
        )
        
        return isinstance(error, retryable_errors)
    
    async def retry_async(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic.
        
        EXAI Adjustment: Enhanced logging for monitoring.
        """
        if not self.enabled:
            return await func(*args, **kwargs)
        
        last_exception = None
        func_name = getattr(func, '__name__', str(func))
        
        for attempt in range(self.config.max_attempts):
            try:
                logger.debug(f"[RETRY] Attempt {attempt + 1}/{self.config.max_attempts} for {func_name}")
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"[RETRY] Success on attempt {attempt + 1} for {func_name}")
                
                return result
                
            except Exception as e:
                last_exception = e
                
                if not self._should_retry(e):
                    logger.warning(f"[RETRY] Non-retryable error for {func_name}: {e}")
                    raise
                
                if attempt < self.config.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    logger.info(f"[RETRY] Attempt {attempt + 1} failed for {func_name}, retrying after {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"[RETRY] Max retries ({self.config.max_attempts}) exceeded for {func_name}: {e}")
        
        raise last_exception


# ============================================================================
# CIRCUIT BREAKER (Task 9.2)
# ============================================================================

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreaker:
    """Circuit breaker pattern for provider resilience.
    
    EXAI Adjustment: Provider isolation with class-level state persistence.
    """
    
    def __init__(self, config: Optional[CircuitBreakerConfig] = None, provider_name: str = "default"):
        self.config = config or CircuitBreakerConfig()
        self.provider_name = provider_name
        self.enabled = os.getenv('RESILIENCE_CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
        
        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        if self.state != CircuitState.OPEN:
            return False
        
        if self.last_failure_time is None:
            return True
        
        timeout_elapsed = (
            datetime.now() - self.last_failure_time
        ).total_seconds() >= self.config.timeout
        
        return timeout_elapsed
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection.
        
        EXAI Adjustment: Enhanced logging for state transitions.
        """
        if not self.enabled:
            return await func(*args, **kwargs)
        
        func_name = getattr(func, '__name__', str(func))
        
        # Check if circuit should attempt reset
        if self._should_attempt_reset():
            old_state = self.state
            self.state = CircuitState.HALF_OPEN
            self.half_open_calls = 0
            logger.info(f"[CIRCUIT] State transition: {old_state.value} → {self.state.value} for {self.provider_name}")
        
        # Reject if circuit is open
        if self.state == CircuitState.OPEN:
            error_msg = f"Circuit breaker is OPEN for {self.provider_name} - provider unavailable"
            logger.warning(f"[CIRCUIT] {error_msg}")
            raise Exception(error_msg)
        
        # Limit calls in half-open state
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.config.half_open_max_calls:
                error_msg = f"Circuit breaker HALF_OPEN for {self.provider_name} - max calls exceeded"
                logger.warning(f"[CIRCUIT] {error_msg}")
                raise Exception(error_msg)
            self.half_open_calls += 1
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call.
        
        EXAI Adjustment: Log state transitions for monitoring.
        """
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                old_state = self.state
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"[CIRCUIT] State transition: {old_state.value} → {self.state.value} for {self.provider_name} - provider recovered")
        else:
            # Reset failure count on success in CLOSED state
            self.failure_count = 0
    
    def _on_failure(self):
        """Handle failed call.
        
        EXAI Adjustment: Log state transitions for monitoring.
        """
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            old_state = self.state
            self.state = CircuitState.OPEN
            self.success_count = 0
            logger.warning(f"[CIRCUIT] State transition: {old_state.value} → {self.state.value} for {self.provider_name} - recovery failed")
        elif self.failure_count >= self.config.failure_threshold:
            old_state = self.state
            self.state = CircuitState.OPEN
            logger.error(f"[CIRCUIT] State transition: {old_state.value} → {self.state.value} for {self.provider_name} - {self.failure_count} failures")


# ============================================================================
# RESILIENT PROVIDER (Combined Pattern)
# ============================================================================

class ResilientProvider:
    """Combines retry and circuit breaker patterns.
    
    EXAI Adjustment: Provider isolation with class-level circuit breaker state.
    """
    
    # Class-level circuit breaker state (shared across instances)
    _circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def __init__(
        self,
        provider_name: str,
        retry_config: Optional[RetryConfig] = None,
        circuit_config: Optional[CircuitBreakerConfig] = None
    ):
        self.provider_name = provider_name
        self.retry_handler = RetryHandler(retry_config)
        
        # Get or create circuit breaker for this provider
        if provider_name not in self._circuit_breakers:
            self._circuit_breakers[provider_name] = CircuitBreaker(circuit_config, provider_name)
        
        self.circuit_breaker = self._circuit_breakers[provider_name]
        self.enabled = os.getenv('RESILIENCE_ENABLED', 'true').lower() == 'true'
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute with both retry and circuit breaker protection."""
        if not self.enabled:
            return await func(*args, **kwargs)
        
        # Retry wraps circuit breaker
        return await self.retry_handler.retry_async(
            self.circuit_breaker.call,
            func,
            *args,
            **kwargs
        )

