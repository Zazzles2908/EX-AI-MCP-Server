"""
Resilience Wrapper

Combines circuit breaker and retry logic for unified resilient operations.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-10-31
"""

import logging
from typing import Any, Callable, Optional

from .circuit_breaker import CircuitBreaker
from .retry_logic import RetryConfig, RetryLogic

logger = logging.getLogger(__name__)


class ResilienceWrapper:
    """
    Unified resilience wrapper combining circuit breaker and retry logic.
    
    Provides a single interface for resilient operations with both
    circuit breaker protection and retry capabilities.
    """
    
    def __init__(
        self,
        name: str,
        circuit_breaker_config: Optional[dict] = None,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize resilience wrapper.
        
        Args:
            name: Operation name
            circuit_breaker_config: Circuit breaker configuration dict
            retry_config: Retry configuration object
        """
        self.name = name
        
        # Initialize circuit breaker
        cb_config = circuit_breaker_config or {}
        self.circuit_breaker = CircuitBreaker(
            name=name,
            failure_threshold=cb_config.get('failure_threshold', 5),
            recovery_timeout=cb_config.get('recovery_timeout', 60),
            success_threshold=cb_config.get('success_threshold', 2),
        )
        
        # Initialize retry logic
        self.retry_logic = RetryLogic(
            retry_config or RetryConfig()
        )
        
        self.operation_count = 0
        self.success_count = 0
        self.failure_count = 0
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with resilience protection.
        
        Flow:
        1. Check circuit breaker state
        2. If CLOSED or HALF_OPEN, attempt with retry logic
        3. Track success/failure
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If operation fails after all retries or circuit is OPEN
        """
        self.operation_count += 1
        
        try:
            # Execute through circuit breaker with retry logic
            result = self.circuit_breaker.call(
                self._execute_with_retry,
                func,
                *args,
                **kwargs
            )
            self.success_count += 1
            logger.debug(
                f"[{self.name}] Operation succeeded "
                f"(total: {self.operation_count}, success: {self.success_count})"
            )
            return result
        
        except Exception as e:
            self.failure_count += 1
            logger.error(
                f"[{self.name}] Operation failed: {e} "
                f"(total: {self.operation_count}, failures: {self.failure_count})"
            )
            raise
    
    def _execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        return self.retry_logic.execute(func, *args, **kwargs)
    
    def get_metrics(self) -> dict:
        """Get comprehensive resilience metrics."""
        total = self.operation_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0.0
        
        return {
            'name': self.name,
            'operation_count': self.operation_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': success_rate,
            'circuit_breaker': self.circuit_breaker.get_metrics(),
            'retry_logic': self.retry_logic.get_metrics(),
        }
    
    def reset(self) -> None:
        """Reset resilience wrapper state."""
        self.circuit_breaker.reset()
        self.operation_count = 0
        self.success_count = 0
        self.failure_count = 0
        logger.info(f"[{self.name}] Resilience wrapper reset")


class ResilienceWrapperFactory:
    """Factory for creating and managing resilience wrappers."""
    
    _wrappers: dict[str, ResilienceWrapper] = {}
    
    @classmethod
    def create(
        cls,
        name: str,
        circuit_breaker_config: Optional[dict] = None,
        retry_config: Optional[RetryConfig] = None,
    ) -> ResilienceWrapper:
        """
        Create or get resilience wrapper.
        
        Args:
            name: Wrapper name
            circuit_breaker_config: Circuit breaker configuration
            retry_config: Retry configuration
            
        Returns:
            ResilienceWrapper instance
        """
        if name not in cls._wrappers:
            cls._wrappers[name] = ResilienceWrapper(
                name=name,
                circuit_breaker_config=circuit_breaker_config,
                retry_config=retry_config,
            )
        return cls._wrappers[name]
    
    @classmethod
    def get(cls, name: str) -> Optional[ResilienceWrapper]:
        """Get existing resilience wrapper."""
        return cls._wrappers.get(name)
    
    @classmethod
    def get_all_metrics(cls) -> dict:
        """Get metrics for all wrappers."""
        return {
            name: wrapper.get_metrics()
            for name, wrapper in cls._wrappers.items()
        }
    
    @classmethod
    def reset_all(cls) -> None:
        """Reset all wrappers."""
        for wrapper in cls._wrappers.values():
            wrapper.reset()
        logger.info("All resilience wrappers reset")
    
    @classmethod
    def clear(cls) -> None:
        """Clear all wrappers."""
        cls._wrappers.clear()
        logger.info("All resilience wrappers cleared")

