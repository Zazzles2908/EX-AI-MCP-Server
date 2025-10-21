"""
Circuit Breaker Manager for External Service Calls

Implements circuit breaker pattern to prevent cascading failures when external
services (Redis, Supabase, Kimi, GLM) become unavailable.

Based on EXAI recommendations (Conversation: 2d0fb045-b73d-42e8-a4eb-faf6751a5052)

Circuit Breaker States:
- CLOSED: Normal operation, requests pass through
- OPEN: Service is failing, requests fail immediately
- HALF_OPEN: Testing if service has recovered

Phase 1 Implementation (2025-10-18)
"""

import logging
from typing import Dict, Optional
import pybreaker
from prometheus_client import Counter, Gauge

logger = logging.getLogger(__name__)

# Prometheus metrics for circuit breaker state
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service']
)

circuit_breaker_failures = Counter(
    'circuit_breaker_failures_total',
    'Total failures detected by circuit breaker',
    ['service']
)

circuit_breaker_state_changes = Counter(
    'circuit_breaker_state_changes_total',
    'Total circuit breaker state changes',
    ['service', 'from_state', 'to_state']
)


class CircuitBreakerListener(pybreaker.CircuitBreakerListener):
    """Listener for circuit breaker state changes with Prometheus integration"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def state_change(self, breaker, old_state, new_state):
        """Called when circuit breaker state changes (EXAI Fix #5 - 2025-10-21: Enhanced logging)"""
        # Use emoji for visibility in logs
        state_emoji = {
            'closed': '✅',
            'open': '🔴',
            'half_open': '🟡'
        }
        emoji = state_emoji.get(new_state.name.lower(), '⚪')

        logger.warning(
            f"{emoji} [CIRCUIT_BREAKER] Service: {self.service_name}, "
            f"State Change: {old_state.name} → {new_state.name}, "
            f"Fail Count: {breaker.fail_counter}"
        )
        
        # Update Prometheus metrics
        state_value = {
            'closed': 0,
            'open': 1,
            'half_open': 2
        }.get(new_state.name.lower(), -1)
        
        circuit_breaker_state.labels(service=self.service_name).set(state_value)
        circuit_breaker_state_changes.labels(
            service=self.service_name,
            from_state=old_state.name.lower(),
            to_state=new_state.name.lower()
        ).inc()
    
    def failure(self, breaker, exc):
        """Called when a failure is recorded"""
        logger.debug(f"Circuit breaker [{self.service_name}]: Failure recorded - {exc}")
        circuit_breaker_failures.labels(service=self.service_name).inc()
    
    def success(self, breaker):
        """Called when a successful call is recorded"""
        logger.debug(f"Circuit breaker [{self.service_name}]: Success recorded")


class CircuitBreakerManager:
    """
    Manages circuit breakers for all external services
    
    Provides centralized circuit breaker management with service-specific
    configurations based on EXAI recommendations:
    
    - Redis: fail_max=5, reset_timeout=60s (high tolerance, quick recovery)
    - Supabase: fail_max=3, reset_timeout=30s (lower tolerance, quick recovery)
    - Kimi: fail_max=4, reset_timeout=120s (moderate tolerance, slower recovery)
    - GLM: fail_max=4, reset_timeout=120s (moderate tolerance, slower recovery)
    """
    
    def __init__(self):
        self._breakers: Dict[str, pybreaker.CircuitBreaker] = {}
        self._initialize_breakers()
        logger.info("Circuit breaker manager initialized")
    
    def _initialize_breakers(self):
        """Initialize circuit breakers for all external services"""
        
        # Redis circuit breaker
        # High tolerance (5 failures) because Redis is critical but usually reliable
        # Quick recovery (60s) to restore caching quickly
        self._breakers['redis'] = pybreaker.CircuitBreaker(
            fail_max=5,
            reset_timeout=60,
            listeners=[CircuitBreakerListener('redis')],
            name='redis'
        )
        
        # Supabase circuit breaker
        # Lower tolerance (3 failures) because database failures are serious
        # Quick recovery (30s) to restore persistence quickly
        self._breakers['supabase'] = pybreaker.CircuitBreaker(
            fail_max=3,
            reset_timeout=30,
            listeners=[CircuitBreakerListener('supabase')],
            name='supabase'
        )
        
        # Kimi API circuit breaker
        # Moderate tolerance (4 failures) for LLM provider
        # Slower recovery (120s) to avoid hammering external API
        self._breakers['kimi'] = pybreaker.CircuitBreaker(
            fail_max=4,
            reset_timeout=120,
            listeners=[CircuitBreakerListener('kimi')],
            name='kimi'
        )
        
        # GLM API circuit breaker
        # Moderate tolerance (4 failures) for LLM provider
        # Slower recovery (120s) to avoid hammering external API
        self._breakers['glm'] = pybreaker.CircuitBreaker(
            fail_max=4,
            reset_timeout=120,
            listeners=[CircuitBreakerListener('glm')],
            name='glm'
        )
        
        # Initialize Prometheus metrics to 0 (closed state)
        for service in self._breakers.keys():
            circuit_breaker_state.labels(service=service).set(0)
        
        logger.info(f"Initialized {len(self._breakers)} circuit breakers: {list(self._breakers.keys())}")
    
    def get_breaker(self, service_name: str) -> Optional[pybreaker.CircuitBreaker]:
        """
        Get circuit breaker for a service
        
        Args:
            service_name: Name of the service ('redis', 'supabase', 'kimi', 'glm')
        
        Returns:
            Circuit breaker instance or None if service not found
        """
        breaker = self._breakers.get(service_name)
        if not breaker:
            logger.warning(f"No circuit breaker found for service: {service_name}")
        return breaker
    
    def get_state(self, service_name: str) -> Optional[str]:
        """
        Get current state of a circuit breaker
        
        Args:
            service_name: Name of the service
        
        Returns:
            State name ('closed', 'open', 'half_open') or None
        """
        breaker = self.get_breaker(service_name)
        if breaker:
            return breaker.current_state.name.lower()
        return None
    
    def reset(self, service_name: str) -> bool:
        """
        Manually reset a circuit breaker to closed state
        
        Args:
            service_name: Name of the service
        
        Returns:
            True if reset successful, False otherwise
        """
        breaker = self.get_breaker(service_name)
        if breaker:
            try:
                breaker.close()
                logger.info(f"Circuit breaker [{service_name}] manually reset to CLOSED")
                return True
            except Exception as e:
                logger.error(f"Failed to reset circuit breaker [{service_name}]: {e}")
                return False
        return False
    
    def get_all_states(self) -> Dict[str, str]:
        """
        Get states of all circuit breakers
        
        Returns:
            Dictionary mapping service names to their current states
        """
        return {
            service: breaker.current_state.name.lower()
            for service, breaker in self._breakers.items()
        }


# Singleton instance - import this in other modules
circuit_breaker_manager = CircuitBreakerManager()

