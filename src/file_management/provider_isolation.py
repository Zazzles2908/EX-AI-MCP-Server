"""
Provider Isolation Manager

Implements separate failure domains for Kimi and GLM providers with
independent circuit breakers and graceful degradation.

Week 2 Implementation (2025-11-02):
- Separate failure domains for each provider
- Independent circuit breakers per provider
- Graceful degradation when one provider fails
- Prevents cascade failures between providers
- Automatic provider selection based on health
"""

import asyncio
import logging
import os
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass

from src.file_management.persistent_circuit_breaker import (
    PersistentCircuitBreaker,
    CircuitBreakerConfig,
    CircuitState
)
from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Supported provider types"""
    KIMI = "kimi"
    GLM = "glm"


@dataclass
class ProviderHealth:
    """Health status for a provider"""
    provider: ProviderType
    is_healthy: bool
    circuit_state: CircuitState
    failures: int
    last_check: float


class ProviderIsolationManager:
    """
    Manages provider isolation with independent circuit breakers.
    
    Features:
    - Separate failure domains for Kimi and GLM
    - Independent circuit breakers prevent cascade failures
    - Graceful degradation (use healthy provider when one fails)
    - Automatic provider selection based on health
    - Prometheus metrics for provider health
    """
    
    # Prometheus metrics
    provider_health_status = Gauge(
        'provider_health_status',
        'Provider health status (1=healthy, 0=unhealthy)',
        ['provider']
    )
    
    provider_selection_total = Counter(
        'provider_selection_total',
        'Total provider selections',
        ['provider', 'reason']
    )
    
    cascade_prevention_total = Counter(
        'cascade_prevention_total',
        'Total cascade failures prevented',
        ['failed_provider', 'fallback_provider']
    )
    
    def __init__(self, redis_client: Optional['redis.Redis'] = None):
        self.redis = redis_client
        self._circuit_breakers: Dict[ProviderType, PersistentCircuitBreaker] = {}
        self._lock = asyncio.Lock()

        # Configurable file size threshold for provider selection (default: 20MB)
        self.file_size_threshold = int(os.getenv('PROVIDER_FILE_SIZE_THRESHOLD', '20971520'))

        # Initialize circuit breakers for each provider
        self._init_circuit_breakers()

    def _init_circuit_breakers(self):
        """Initialize independent circuit breakers for each provider"""
        for provider in ProviderType:
            config = CircuitBreakerConfig(
                name=f"provider_{provider.value}",
                failure_threshold=5,
                timeout=60,
                half_open_max_calls=3,
                success_threshold=2,
                max_timeout=300,
                backoff_multiplier=2.0
            )
            self._circuit_breakers[provider] = PersistentCircuitBreaker(
                config=config,
                redis_manager=self.redis
            )
            
            logger.info(f"Initialized circuit breaker for provider: {provider.value}")
    
    def get_circuit_breaker(self, provider: ProviderType) -> PersistentCircuitBreaker:
        """Get circuit breaker for specific provider"""
        return self._circuit_breakers[provider]
    
    async def get_provider_health(self, provider: ProviderType) -> ProviderHealth:
        """Get health status for a provider"""
        async with self._lock:  # Add locking to prevent race conditions
            circuit_breaker = self._circuit_breakers[provider]
            metrics = await circuit_breaker.get_metrics()
            circuit_state = await circuit_breaker.get_state()

            is_healthy = circuit_state == CircuitState.CLOSED

            # Update metrics
            self.provider_health_status.labels(provider=provider.value).set(
                1 if is_healthy else 0
            )

            return ProviderHealth(
                provider=provider,
                is_healthy=is_healthy,
                circuit_state=circuit_state,
                failures=metrics['failures'],
                last_check=metrics.get('last_failure_time', 0)
            )
    
    async def get_all_provider_health(self) -> Dict[ProviderType, ProviderHealth]:
        """Get health status for all providers"""
        health_status = {}
        for provider in ProviderType:
            health_status[provider] = await self.get_provider_health(provider)
        return health_status
    
    async def select_provider(
        self,
        preferred_provider: Optional[ProviderType] = None,
        file_size: Optional[int] = None
    ) -> ProviderType:
        """
        Select best available provider based on health and preferences.
        
        Selection logic:
        1. If preferred provider is healthy, use it
        2. If preferred provider is unhealthy, use fallback provider (graceful degradation)
        3. If both unhealthy, use preferred provider (will trigger circuit breaker)
        4. If no preference, select based on file size or health
        """
        health_status = await self.get_all_provider_health()
        
        # If preferred provider specified
        if preferred_provider:
            preferred_health = health_status[preferred_provider]
            
            if preferred_health.is_healthy:
                self.provider_selection_total.labels(
                    provider=preferred_provider.value,
                    reason="preferred_healthy"
                ).inc()
                return preferred_provider
            
            # Preferred provider unhealthy, try fallback
            fallback_provider = (
                ProviderType.GLM if preferred_provider == ProviderType.KIMI
                else ProviderType.KIMI
            )
            fallback_health = health_status[fallback_provider]
            
            if fallback_health.is_healthy:
                logger.warning(
                    f"Provider {preferred_provider.value} unhealthy "
                    f"(state: {preferred_health.circuit_state.value}), "
                    f"using fallback: {fallback_provider.value}"
                )
                self.cascade_prevention_total.labels(
                    failed_provider=preferred_provider.value,
                    fallback_provider=fallback_provider.value
                ).inc()
                self.provider_selection_total.labels(
                    provider=fallback_provider.value,
                    reason="cascade_prevention"
                ).inc()
                return fallback_provider
            
            # Both unhealthy, use preferred (will trigger circuit breaker)
            logger.error(
                f"Both providers unhealthy: {preferred_provider.value} "
                f"({preferred_health.circuit_state.value}), "
                f"{fallback_provider.value} ({fallback_health.circuit_state.value})"
            )
            self.provider_selection_total.labels(
                provider=preferred_provider.value,
                reason="both_unhealthy"
            ).inc()
            return preferred_provider
        
        # No preference, select based on health
        kimi_health = health_status[ProviderType.KIMI]
        glm_health = health_status[ProviderType.GLM]
        
        if kimi_health.is_healthy and glm_health.is_healthy:
            # Both healthy, select based on file size if provided
            if file_size:
                # Use Kimi for smaller files, GLM for larger files
                # Threshold configurable via PROVIDER_FILE_SIZE_THRESHOLD env var
                selected = ProviderType.KIMI if file_size < self.file_size_threshold else ProviderType.GLM
                self.provider_selection_total.labels(
                    provider=selected.value,
                    reason="file_size_optimization"
                ).inc()
                return selected
            
            # Default to Kimi
            self.provider_selection_total.labels(
                provider=ProviderType.KIMI.value,
                reason="default_both_healthy"
            ).inc()
            return ProviderType.KIMI
        
        elif kimi_health.is_healthy:
            self.provider_selection_total.labels(
                provider=ProviderType.KIMI.value,
                reason="only_healthy"
            ).inc()
            return ProviderType.KIMI
        
        elif glm_health.is_healthy:
            self.provider_selection_total.labels(
                provider=ProviderType.GLM.value,
                reason="only_healthy"
            ).inc()
            return ProviderType.GLM
        
        # Both unhealthy, default to Kimi
        logger.error("Both providers unhealthy, defaulting to Kimi")
        self.provider_selection_total.labels(
            provider=ProviderType.KIMI.value,
            reason="both_unhealthy_default"
        ).inc()
        return ProviderType.KIMI
    
    async def execute_with_isolation(
        self,
        provider: ProviderType,
        operation: callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute operation with provider isolation.
        
        Uses provider-specific circuit breaker to prevent cascade failures.
        """
        circuit_breaker = self._circuit_breakers[provider]
        
        async with circuit_breaker:
            return await operation(*args, **kwargs)
    
    async def reset_provider(self, provider: ProviderType):
        """Manually reset circuit breaker for a provider"""
        circuit_breaker = self._circuit_breakers[provider]
        await circuit_breaker.reset()
        logger.info(f"Reset circuit breaker for provider: {provider.value}")
    
    async def reset_all_providers(self):
        """Manually reset all provider circuit breakers"""
        for provider in ProviderType:
            await self.reset_provider(provider)
        logger.info("Reset all provider circuit breakers")
    
    async def get_isolation_metrics(self) -> Dict[str, Any]:
        """Get isolation metrics for all providers"""
        metrics = {}
        for provider in ProviderType:
            circuit_breaker = self._circuit_breakers[provider]
            metrics[provider.value] = await circuit_breaker.get_metrics()
        return metrics

    async def cleanup(self):
        """Cleanup resources and close all circuit breakers"""
        async with self._lock:
            for provider, breaker in self._circuit_breakers.items():
                await breaker.cleanup()
                logger.info(f"Provider isolation: cleaned up circuit breaker for {provider.value}")
            logger.info("Provider isolation manager cleaned up successfully")


# Singleton instance
_provider_isolation_manager: Optional[ProviderIsolationManager] = None


def get_provider_isolation_manager(
    redis_manager: Optional[RedisManager] = None
) -> ProviderIsolationManager:
    """Get singleton provider isolation manager"""
    global _provider_isolation_manager
    
    if _provider_isolation_manager is None:
        _provider_isolation_manager = ProviderIsolationManager(redis_manager)
    
    return _provider_isolation_manager

