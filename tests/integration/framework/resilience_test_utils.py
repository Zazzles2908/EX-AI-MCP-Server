"""
Resilience Test Utilities for Circuit Breaker and Retry Testing.

Provides helpers for testing circuit breaker behavior, retry logic, and error recovery.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import logging
import time
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerTestHelper:
    """
    Helper for testing circuit breaker behavior.
    
    Provides utilities for:
    - Triggering circuit breaker state changes
    - Waiting for specific states
    - Verifying state transitions
    """
    
    circuit_breaker: Any
    timeout_seconds: float = 30.0
    
    async def trigger_failures(self, count: int, delay_ms: float = 0.0) -> None:
        """
        Trigger multiple failures to open the circuit breaker.
        
        Args:
            count: Number of failures to trigger
            delay_ms: Delay between failures in milliseconds
        """
        for i in range(count):
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)
            
            # Trigger failure
            await self.circuit_breaker._on_failure()
            logger.debug(f"Triggered failure {i+1}/{count}")
    
    async def wait_for_state(
        self,
        expected_state: CircuitBreakerState,
        timeout_seconds: Optional[float] = None
    ) -> bool:
        """
        Wait for circuit breaker to reach expected state.
        
        Args:
            expected_state: Expected circuit breaker state
            timeout_seconds: Maximum time to wait (default: self.timeout_seconds)
        
        Returns:
            True if state reached, False if timeout
        """
        timeout = timeout_seconds or self.timeout_seconds
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self.get_current_state()
            if current_state == expected_state:
                logger.info(f"Circuit breaker reached state: {expected_state.value}")
                return True
            
            await asyncio.sleep(0.1)
        
        logger.warning(f"Timeout waiting for state {expected_state.value}")
        return False
    
    def get_current_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        if hasattr(self.circuit_breaker, 'is_open'):
            if self.circuit_breaker.is_open:
                return CircuitBreakerState.OPEN
            elif hasattr(self.circuit_breaker, 'is_half_open') and self.circuit_breaker.is_half_open:
                return CircuitBreakerState.HALF_OPEN
            else:
                return CircuitBreakerState.CLOSED
        
        # Fallback: check state attribute
        if hasattr(self.circuit_breaker, 'state'):
            state_str = str(self.circuit_breaker.state).lower()
            if 'open' in state_str and 'half' not in state_str:
                return CircuitBreakerState.OPEN
            elif 'half' in state_str:
                return CircuitBreakerState.HALF_OPEN
            else:
                return CircuitBreakerState.CLOSED
        
        return CircuitBreakerState.CLOSED
    
    async def trigger_recovery(self, success_count: int = 1) -> None:
        """
        Trigger successful operations to close the circuit breaker.
        
        Args:
            success_count: Number of successful operations to trigger
        """
        for i in range(success_count):
            await self.circuit_breaker._on_success()
            logger.debug(f"Triggered success {i+1}/{success_count}")
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        if hasattr(self.circuit_breaker, 'get_stats'):
            return self.circuit_breaker.get_stats()
        
        return {
            "state": self.get_current_state().value,
            "failure_count": getattr(self.circuit_breaker, 'failure_count', 0),
            "success_count": getattr(self.circuit_breaker, 'success_count', 0)
        }


@dataclass
class RetryTestHelper:
    """
    Helper for testing retry logic.
    
    Provides utilities for:
    - Simulating retry scenarios
    - Tracking retry attempts
    - Verifying retry behavior
    """
    
    max_retries: int = 3
    retry_delay_ms: float = 100.0
    
    async def simulate_retry_scenario(
        self,
        operation: Callable,
        fail_count: int = 2,
        success_on_final: bool = True
    ) -> tuple[bool, int]:
        """
        Simulate a retry scenario with controlled failures.
        
        Args:
            operation: Async operation to retry
            fail_count: Number of times to fail before success
            success_on_final: Whether final attempt should succeed
        
        Returns:
            (success, attempt_count) tuple
        """
        attempt = 0
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # Simulate failure for first N attempts
                if attempt <= fail_count:
                    raise Exception(f"Simulated failure on attempt {attempt}")
                
                # Execute operation
                await operation()
                logger.info(f"Operation succeeded on attempt {attempt}")
                return (True, attempt)
            
            except Exception as e:
                logger.debug(f"Attempt {attempt} failed: {e}")
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay_ms / 1000.0)
                else:
                    if success_on_final:
                        # Force success on final attempt
                        await operation()
                        return (True, attempt)
                    else:
                        logger.warning(f"All {self.max_retries} attempts failed")
                        return (False, attempt)
        
        return (False, attempt)
    
    async def measure_retry_timing(
        self,
        operation: Callable,
        expected_retries: int
    ) -> dict:
        """
        Measure timing of retry attempts.
        
        Args:
            operation: Async operation to retry
            expected_retries: Expected number of retries
        
        Returns:
            Timing statistics dict
        """
        start_time = time.time()
        attempt_times = []
        
        for attempt in range(expected_retries):
            attempt_start = time.time()
            
            try:
                await operation()
            except Exception:
                pass
            
            attempt_duration = (time.time() - attempt_start) * 1000
            attempt_times.append(attempt_duration)
            
            if attempt < expected_retries - 1:
                await asyncio.sleep(self.retry_delay_ms / 1000.0)
        
        total_duration = (time.time() - start_time) * 1000
        
        return {
            "total_duration_ms": total_duration,
            "attempt_count": len(attempt_times),
            "attempt_times_ms": attempt_times,
            "avg_attempt_time_ms": sum(attempt_times) / len(attempt_times) if attempt_times else 0
        }


async def simulate_circuit_breaker_failure(
    circuit_breaker: Any,
    failure_count: int = 5,
    delay_ms: float = 0.0
) -> None:
    """
    Simulate failures to trigger circuit breaker opening.
    
    Args:
        circuit_breaker: Circuit breaker instance
        failure_count: Number of failures to trigger
        delay_ms: Delay between failures
    
    Example:
        >>> await simulate_circuit_breaker_failure(cb, failure_count=5)
    """
    helper = CircuitBreakerTestHelper(circuit_breaker)
    await helper.trigger_failures(failure_count, delay_ms)


async def wait_for_circuit_breaker_state(
    circuit_breaker: Any,
    expected_state: CircuitBreakerState,
    timeout_seconds: float = 30.0
) -> bool:
    """
    Wait for circuit breaker to reach expected state.
    
    Args:
        circuit_breaker: Circuit breaker instance
        expected_state: Expected state
        timeout_seconds: Maximum wait time
    
    Returns:
        True if state reached, False if timeout
    
    Example:
        >>> success = await wait_for_circuit_breaker_state(cb, CircuitBreakerState.OPEN)
    """
    helper = CircuitBreakerTestHelper(circuit_breaker, timeout_seconds)
    return await helper.wait_for_state(expected_state)


async def verify_retry_backoff(
    retry_attempts: list[float],
    expected_backoff_multiplier: float = 2.0,
    tolerance: float = 0.1
) -> bool:
    """
    Verify that retry delays follow exponential backoff pattern.
    
    Args:
        retry_attempts: List of retry delay times in milliseconds
        expected_backoff_multiplier: Expected backoff multiplier
        tolerance: Acceptable deviation (0.0-1.0)
    
    Returns:
        True if backoff pattern is correct
    
    Example:
        >>> delays = [100, 200, 400, 800]
        >>> is_valid = await verify_retry_backoff(delays, expected_backoff_multiplier=2.0)
    """
    if len(retry_attempts) < 2:
        return True
    
    for i in range(1, len(retry_attempts)):
        expected_delay = retry_attempts[i-1] * expected_backoff_multiplier
        actual_delay = retry_attempts[i]
        
        # Check if within tolerance
        deviation = abs(actual_delay - expected_delay) / expected_delay
        if deviation > tolerance:
            logger.warning(
                f"Backoff deviation at attempt {i}: "
                f"expected={expected_delay:.2f}ms, actual={actual_delay:.2f}ms, "
                f"deviation={deviation:.2%}"
            )
            return False
    
    return True

