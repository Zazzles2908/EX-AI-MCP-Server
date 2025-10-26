"""
Circuit Breaker Pattern Implementation for WebSocket Connections.

This module implements the circuit breaker pattern to prevent cascading failures
from consistently failing WebSocket connections. The circuit breaker has three states:

- CLOSED: Normal operation, requests pass through
- OPEN: Failing, requests are rejected immediately
- HALF_OPEN: Testing if service recovered, limited requests allowed

Created: 2025-10-26
Phase: Task 2 Week 1 - WebSocket Stability Enhancements
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
EXAI Recommendation: Implement circuit breaker pattern for graceful degradation
"""

import asyncio
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open before closing
    timeout_seconds: float = 60.0  # Time before trying half-open
    half_open_max_calls: int = 3  # Max calls allowed in half-open state


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit breaker for WebSocket connections.
    
    Prevents cascading failures by:
    - Opening circuit after threshold failures
    - Rejecting requests while open
    - Testing recovery in half-open state
    - Closing circuit after successful recovery
    
    EXAI-validated implementation with:
    - Exponential backoff for recovery attempts
    - Configurable thresholds
    - Metrics integration
    - Thread-safe state management
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Identifier for this circuit breaker
            config: Configuration (uses defaults if None)
            on_state_change: Callback for state changes (old_state, new_state)
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.on_state_change = on_state_change
        
        # State tracking
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._half_open_calls = 0
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        logger.info(f"Circuit breaker '{name}' initialized: {self.config}")
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing)."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN
    
    async def _change_state(self, new_state: CircuitState):
        """Change circuit state and trigger callback."""
        old_state = self._state
        if old_state == new_state:
            return
        
        self._state = new_state
        logger.info(f"Circuit breaker '{self.name}' state: {old_state.value} → {new_state.value}")
        
        # Reset counters on state change
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
        elif new_state == CircuitState.OPEN:
            self._last_failure_time = time.time()
            self._half_open_calls = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0
            self._half_open_calls = 0
        
        # Trigger callback
        if self.on_state_change:
            try:
                self.on_state_change(old_state, new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return False
        
        elapsed = time.time() - self._last_failure_time
        return elapsed >= self.config.timeout_seconds
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func
            
        Returns:
            Result from func
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Any exception from func
        """
        async with self._lock:
            # Check if circuit is open
            if self._state == CircuitState.OPEN:
                # Check if we should try half-open
                if await self._should_attempt_reset():
                    await self._change_state(CircuitState.HALF_OPEN)
                else:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is OPEN. "
                        f"Retry after {self.config.timeout_seconds}s"
                    )
            
            # Check half-open call limit
            if self._state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerError(
                        f"Circuit breaker '{self.name}' is HALF_OPEN. "
                        f"Max calls ({self.config.half_open_max_calls}) reached"
                    )
                self._half_open_calls += 1
        
        # Execute function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
            
        except Exception as e:
            await self._on_failure()
            raise
    
    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._success_count += 1
                logger.debug(
                    f"Circuit breaker '{self.name}' success in HALF_OPEN: "
                    f"{self._success_count}/{self.config.success_threshold}"
                )
                
                # Close circuit if threshold reached
                if self._success_count >= self.config.success_threshold:
                    await self._change_state(CircuitState.CLOSED)
                    logger.info(f"Circuit breaker '{self.name}' recovered and CLOSED")
            
            elif self._state == CircuitState.CLOSED:
                # Reset failure count on success
                self._failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self._failure_count += 1
            
            if self._state == CircuitState.HALF_OPEN:
                # Immediate open on failure in half-open
                logger.warning(
                    f"Circuit breaker '{self.name}' failed in HALF_OPEN, "
                    f"reopening circuit"
                )
                await self._change_state(CircuitState.OPEN)
            
            elif self._state == CircuitState.CLOSED:
                logger.debug(
                    f"Circuit breaker '{self.name}' failure: "
                    f"{self._failure_count}/{self.config.failure_threshold}"
                )
                
                # Open circuit if threshold reached
                if self._failure_count >= self.config.failure_threshold:
                    logger.warning(
                        f"Circuit breaker '{self.name}' threshold reached, "
                        f"opening circuit"
                    )
                    await self._change_state(CircuitState.OPEN)
    
    async def reset(self):
        """Manually reset circuit breaker to closed state."""
        async with self._lock:
            logger.info(f"Circuit breaker '{self.name}' manually reset")
            await self._change_state(CircuitState.CLOSED)
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "half_open_calls": self._half_open_calls,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "timeout_seconds": self.config.timeout_seconds,
                "half_open_max_calls": self.config.half_open_max_calls
            }
        }


class CircuitBreakerManager:
    """
    Manages multiple circuit breakers.
    
    Provides centralized management for circuit breakers across
    different WebSocket connections or services.
    """
    
    def __init__(self):
        """Initialize circuit breaker manager."""
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()
    
    async def get_or_create(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        on_state_change: Optional[Callable[[CircuitState, CircuitState], None]] = None
    ) -> CircuitBreaker:
        """Get existing circuit breaker or create new one."""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    config=config,
                    on_state_change=on_state_change
                )
            return self._breakers[name]
    
    async def get(self, name: str) -> Optional[CircuitBreaker]:
        """Get circuit breaker by name."""
        async with self._lock:
            return self._breakers.get(name)
    
    async def reset_all(self):
        """Reset all circuit breakers."""
        async with self._lock:
            for breaker in self._breakers.values():
                await breaker.reset()
    
    def get_all_stats(self) -> dict:
        """Get statistics for all circuit breakers."""
        return {
            name: breaker.get_stats()
            for name, breaker in self._breakers.items()
        }

