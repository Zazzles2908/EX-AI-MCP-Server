"""
Graceful Degradation and Error Handling Utilities

This module provides graceful degradation capabilities with circuit breaker pattern
for handling failures in provider calls, expert validation, and web search operations.

Key Features:
- Execute functions with automatic fallback on failure
- Circuit breaker pattern to prevent cascading failures
- Exponential backoff for retries
- Comprehensive logging of failures and recoveries
- Global singleton for consistent state management

Usage:
    from utils.error_handling import get_graceful_degradation
    
    gd = get_graceful_degradation()
    
    async def primary():
        return await some_risky_operation()
    
    async def fallback():
        return await safe_fallback_operation()
    
    result = await gd.execute_with_fallback(
        primary,
        fallback,
        timeout_secs=60.0,
        max_retries=2,
        operation_name="my_operation"
    )
"""

import asyncio
import time
import logging
from typing import Callable, Any, Optional, Dict
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and operation cannot proceed."""
    pass


class GracefulDegradation:
    """
    Handles graceful degradation for failures with circuit breaker pattern.
    
    Circuit Breaker States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail fast with fallback
    - HALF_OPEN: Testing if service recovered (not implemented yet)
    
    Configuration:
    - failure_threshold: Number of failures before circuit opens (default: 5)
    - recovery_timeout: Seconds before circuit closes after opening (default: 300)
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 300.0
    ):
        """
        Initialize graceful degradation handler.
        
        Args:
            failure_threshold: Number of failures before circuit opens
            recovery_timeout: Seconds before circuit closes after opening
        """
        self.circuit_breakers: Dict[str, Dict] = {}
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
    async def execute_with_fallback(
        self,
        primary_fn: Callable,
        fallback_fn: Optional[Callable] = None,
        timeout_secs: float = 60.0,
        max_retries: int = 2,
        operation_name: Optional[str] = None
    ) -> Any:
        """
        Execute function with fallback and timeout.
        
        Execution Flow:
        1. Check circuit breaker status
        2. If open, use fallback immediately
        3. If closed, try primary function with retries
        4. On failure, try fallback function
        5. Update circuit breaker state
        
        Args:
            primary_fn: Primary function to execute
            fallback_fn: Optional fallback function
            timeout_secs: Timeout in seconds for each attempt
            max_retries: Maximum retry attempts (0 = no retries)
            operation_name: Name for circuit breaker tracking
            
        Returns:
            Result from primary or fallback function
            
        Raises:
            CircuitBreakerOpen: If circuit breaker is open and no fallback
            Exception: If both primary and fallback fail
        """
        op_name = operation_name or primary_fn.__name__
        
        # Check circuit breaker
        if self._is_circuit_open(op_name):
            logger.warning(f"[CIRCUIT_BREAKER] Circuit open for {op_name}")
            if fallback_fn:
                logger.info(f"[CIRCUIT_BREAKER] Using fallback for {op_name}")
                try:
                    return await self._execute_with_timeout(
                        fallback_fn, timeout_secs
                    )
                except Exception as e:
                    logger.error(f"[CIRCUIT_BREAKER] Fallback also failed for {op_name}: {e}")
                    raise
            raise CircuitBreakerOpen(f"{op_name} circuit breaker is open")
        
        # Try primary function with retries
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                result = await self._execute_with_timeout(
                    primary_fn, timeout_secs
                )
                self._record_success(op_name)
                if attempt > 0:
                    logger.info(f"[GRACEFUL_DEGRADATION] {op_name} succeeded on attempt {attempt + 1}")
                return result
                
            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(
                    f"[GRACEFUL_DEGRADATION] {op_name} timed out "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                if attempt < max_retries:
                    backoff = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.debug(f"[GRACEFUL_DEGRADATION] Retrying {op_name} after {backoff}s backoff")
                    await asyncio.sleep(backoff)
                    continue
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"[GRACEFUL_DEGRADATION] {op_name} failed: {e} "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                if attempt < max_retries:
                    backoff = 2 ** attempt
                    logger.debug(f"[GRACEFUL_DEGRADATION] Retrying {op_name} after {backoff}s backoff")
                    await asyncio.sleep(backoff)
                    continue
        
        # All retries failed
        self._record_failure(op_name)
        
        # Try fallback
        if fallback_fn:
            logger.info(f"[GRACEFUL_DEGRADATION] Primary failed, using fallback for {op_name}")
            try:
                return await self._execute_with_timeout(
                    fallback_fn, timeout_secs
                )
            except Exception as fallback_error:
                logger.error(f"[GRACEFUL_DEGRADATION] Fallback also failed for {op_name}: {fallback_error}")
                raise
        
        # No fallback, raise last error
        logger.error(f"[GRACEFUL_DEGRADATION] {op_name} failed with no fallback available")
        raise last_error
        
    async def _execute_with_timeout(
        self,
        fn: Callable,
        timeout_secs: float
    ) -> Any:
        """
        Execute function with timeout.
        
        Handles both async and sync functions.
        
        Args:
            fn: Function to execute
            timeout_secs: Timeout in seconds
            
        Returns:
            Result from function
            
        Raises:
            asyncio.TimeoutError: If function exceeds timeout
        """
        if asyncio.iscoroutinefunction(fn):
            return await asyncio.wait_for(fn(), timeout=timeout_secs)
        else:
            # Run sync function in thread pool to avoid blocking
            return await asyncio.wait_for(
                asyncio.to_thread(fn), timeout=timeout_secs
            )
            
    def _is_circuit_open(self, operation_name: str) -> bool:
        """
        Check if circuit breaker is open.
        
        Circuit opens when:
        - Failures >= failure_threshold
        - Time since last failure < recovery_timeout
        
        Circuit closes when:
        - recovery_timeout has elapsed since last failure
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            True if circuit is open, False otherwise
        """
        if operation_name not in self.circuit_breakers:
            return False
            
        cb = self.circuit_breakers[operation_name]
        
        # Check if enough failures
        if cb["failures"] < self.failure_threshold:
            return False
            
        # Check if recovery timeout elapsed
        time_since_failure = time.time() - cb["last_failure"]
        if time_since_failure >= self.recovery_timeout:
            # Reset circuit breaker
            logger.info(f"[CIRCUIT_BREAKER] Circuit recovered for {operation_name}")
            cb["failures"] = 0
            return False
            
        return True
        
    def _record_success(self, operation_name: str):
        """
        Record successful execution.
        
        Resets failure count to 0.
        
        Args:
            operation_name: Name of the operation
        """
        if operation_name in self.circuit_breakers:
            prev_failures = self.circuit_breakers[operation_name]["failures"]
            self.circuit_breakers[operation_name]["failures"] = 0
            if prev_failures > 0:
                logger.info(f"[CIRCUIT_BREAKER] Circuit reset for {operation_name} (was {prev_failures} failures)")
            
    def _record_failure(self, operation_name: str):
        """
        Record failed execution.
        
        Increments failure count and updates last failure time.
        Opens circuit if failure threshold reached.
        
        Args:
            operation_name: Name of the operation
        """
        if operation_name not in self.circuit_breakers:
            self.circuit_breakers[operation_name] = {
                "failures": 0,
                "last_failure": 0
            }
        
        self.circuit_breakers[operation_name]["failures"] += 1
        self.circuit_breakers[operation_name]["last_failure"] = time.time()
        
        failures = self.circuit_breakers[operation_name]["failures"]
        logger.warning(
            f"[CIRCUIT_BREAKER] Failure recorded for {operation_name} "
            f"({failures}/{self.failure_threshold})"
        )
        
        if failures >= self.failure_threshold:
            logger.error(
                f"[CIRCUIT_BREAKER] Circuit OPENED for {operation_name} "
                f"(threshold {self.failure_threshold} reached)"
            )
        
    def get_circuit_status(self, operation_name: str) -> Dict[str, Any]:
        """
        Get circuit breaker status for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Dictionary with status information:
            - status: "open" or "closed"
            - failures: Number of failures
            - last_failure: Timestamp of last failure
            - time_until_recovery: Seconds until circuit closes (if open)
        """
        if operation_name not in self.circuit_breakers:
            return {
                "status": "closed",
                "failures": 0,
                "last_failure": None,
                "time_until_recovery": 0
            }
            
        cb = self.circuit_breakers[operation_name]
        is_open = self._is_circuit_open(operation_name)
        
        return {
            "status": "open" if is_open else "closed",
            "failures": cb["failures"],
            "last_failure": cb["last_failure"],
            "time_until_recovery": max(
                0,
                self.recovery_timeout - (time.time() - cb["last_failure"])
            ) if is_open else 0
        }
    
    def get_all_circuit_statuses(self) -> Dict[str, Dict[str, Any]]:
        """
        Get status of all circuit breakers.
        
        Returns:
            Dictionary mapping operation names to their status
        """
        return {
            op_name: self.get_circuit_status(op_name)
            for op_name in self.circuit_breakers.keys()
        }


# Global graceful degradation instance
_graceful_degradation = GracefulDegradation()


def get_graceful_degradation() -> GracefulDegradation:
    """
    Get global graceful degradation instance.
    
    Returns:
        Global GracefulDegradation instance
    """
    return _graceful_degradation


def with_fallback(
    fallback_fn: Optional[Callable] = None,
    timeout_secs: float = 60.0,
    max_retries: int = 2
):
    """
    Decorator for graceful degradation with fallback.
    
    Usage:
        @with_fallback(fallback_fn=my_fallback, timeout_secs=30)
        async def my_function():
            # Primary implementation
            pass
    
    Args:
        fallback_fn: Optional fallback function
        timeout_secs: Timeout in seconds
        max_retries: Maximum retry attempts
        
    Returns:
        Decorated function
    """
    def decorator(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            gd = get_graceful_degradation()
            
            async def primary():
                return await fn(*args, **kwargs)
            
            async def fallback():
                if fallback_fn:
                    return await fallback_fn(*args, **kwargs)
                return None
            
            return await gd.execute_with_fallback(
                primary,
                fallback if fallback_fn else None,
                timeout_secs,
                max_retries,
                fn.__name__
            )
        
        return wrapper
    return decorator

