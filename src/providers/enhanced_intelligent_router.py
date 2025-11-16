"""
Enhanced Intelligent Routing Logic - Parallax-Inspired Implementation

This module provides advanced request routing capabilities inspired by Parallax's
intelligent routing system. It includes:

1. Provider performance tracking and adaptive routing
2. Dynamic routing based on historical success rates
3. Cost-aware routing decisions
4. Load balancing between providers
5. Real-time performance monitoring
6. Circuit breaker patterns for failed providers

Key Parallax-inspired features:
- Performance-weighted provider selection
- Historical success rate tracking
- Dynamic cost optimization
- Adaptive routing based on request characteristics
- Intelligent fallback strategies
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

from .base import ProviderType

logger = logging.getLogger(__name__)


class RoutingStrategy(Enum):
    """Available routing strategies."""
    PERFORMANCE_WEIGHTED = "performance_weighted"
    COST_OPTIMIZED = "cost_optimized"
    LOAD_BALANCED = "load_balanced"
    RELIABILITY_FOCUSED = "reliability_focused"
    ADAPTIVE = "adaptive"


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ProviderMetrics:
    """Metrics for a provider's performance."""
    provider_name: str
    provider_type: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_latency_ms: float = 0.0
    last_request_time: float = 0.0
    consecutive_failures: int = 0
    success_rate: float = 0.0
    cost_per_request: float = 0.0
    tokens_per_request: float = 0.0
    
    def __post_init__(self):
        """Calculate derived metrics."""
        self._update_success_rate()
    
    def _update_success_rate(self):
        """Update success rate calculation."""
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests
        else:
            self.success_rate = 0.0


@dataclass
class RoutingDecision:
    """Represents a routing decision with reasoning."""
    provider: str
    model: str
    strategy_used: RoutingStrategy
    confidence: float
    reasoning: str
    estimated_latency_ms: float
    estimated_cost: float
    fallback_available: bool = True
    circuit_state: CircuitState = CircuitState.CLOSED


@dataclass
class RequestCharacteristics:
    """Characteristics of a request that influence routing decisions."""
    request_type: str  # chat, generate, analyze, debug, etc.
    complexity_score: float  # 0.0 to 1.0
    token_estimate: int
    supports_thinking: bool
    requires_vision: bool
    requires_function_calling: bool
    urgency_level: str  # low, medium, high
    cost_sensitivity: str  # low, medium, high
    response_time_sensitivity: str  # low, medium, high


class EnhancedIntelligentRouter:
    """
    Enhanced intelligent router inspired by Parallax architecture.
    
    Features:
    - Performance tracking and adaptive routing
    - Historical success rate analysis
    - Cost-aware provider selection
    - Load balancing with circuit breakers
    - Dynamic strategy selection
    """
    
    def __init__(
        self,
        default_strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE,
        performance_window: int = 100,  # Number of requests to consider
        circuit_breaker_threshold: int = 5,
        circuit_breaker_timeout: float = 60.0,
        min_success_rate: float = 0.7
    ):
        """
        Initialize enhanced intelligent router.
        
        Args:
            default_strategy: Default routing strategy
            performance_window: Number of requests to track for performance
            circuit_breaker_threshold: Failure threshold for circuit breaker
            circuit_breaker_timeout: Timeout before trying to close circuit
            min_success_rate: Minimum success rate for provider inclusion
        """
        self.default_strategy = default_strategy
        self.performance_window = performance_window
        self.circuit_breaker_threshold = circuit_breaker_threshold
        self.circuit_breaker_timeout = circuit_breaker_timeout
        self.min_success_rate = min_success_rate
        
        # Provider performance tracking
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        self.provider_capabilities: Dict[str, Dict[str, Any]] = {}
        self.circuit_states: Dict[str, CircuitState] = {}
        
        # Request history for pattern analysis
        self.request_history: deque = deque(maxlen=1000)
        
        # Routing strategy weights
        self.strategy_weights = {
            RoutingStrategy.PERFORMANCE_WEIGHTED: 0.4,
            RoutingStrategy.COST_OPTIMIZED: 0.3,
            RoutingStrategy.LOAD_BALANCED: 0.2,
            RoutingStrategy.RELIABILITY_FOCUSED: 0.1
        }
        
        # Provider cost estimates (can be configured externally)
        self.cost_estimates = {
            "minimax": 0.002,      # Per token
            "glm": 0.001,          # Per token  
            "kimi": 0.0015,        # Per token
            "custom": 0.003        # Per token
        }
        
        logger.info(
            f"EnhancedIntelligentRouter initialized: "
            f"strategy={default_strategy.value}, "
            f"window={performance_window}, "
            f"circuit_threshold={circuit_breaker_threshold}"
        )

    def register_provider(
        self,
        provider_name: str,
        provider_type: str,
        capabilities: Dict[str, Any],
        base_url: Optional[str] = None,
        cost_per_token: Optional[float] = None
    ):
        """
        Register a provider with the router.
        
        Args:
            provider_name: Provider identifier
            provider_type: Provider type (minimax, glm, kimi, etc.)
            capabilities: Provider capabilities and supported features
            base_url: Optional provider base URL
            cost_per_token: Optional cost override
        """
        self.provider_capabilities[provider_name] = capabilities
        
        # Initialize metrics
        self.provider_metrics[provider_name] = ProviderMetrics(
            provider_name=provider_name,
            provider_type=provider_type
        )
        
        # Initialize circuit state
        self.circuit_states[provider_name] = CircuitState.CLOSED
        
        # Update cost estimate if provided
        if cost_per_token:
            self.cost_estimates[provider_type] = cost_per_token
        
        logger.info(
            f"Registered provider {provider_name} ({provider_type}) "
            f"with capabilities: {list(capabilities.keys())}"
        )

    async def route_request(
        self,
        request: RequestCharacteristics,
        available_providers: Dict[str, Dict[str, Any]],
        strategy: Optional[RoutingStrategy] = None
    ) -> RoutingDecision:
        """
        Route a request using intelligent logic.
        
        Args:
            request: Request characteristics
            available_providers: Currently available providers
            strategy: Optional routing strategy override
            
        Returns:
            RoutingDecision with provider, model, and reasoning
        """
        strategy = strategy or self.default_strategy
        
        # Filter available providers based on circuit breakers
        viable_providers = self._filter_circuit_breakers(available_providers)
        
        if not viable_providers:
            logger.warning("No viable providers available, using circuit breaker override")
            viable_providers = available_providers
        
        # Get candidate providers based on request requirements
        candidate_providers = self._filter_by_capabilities(request, viable_providers)
        
        if not candidate_providers:
            logger.warning("No providers meet requirements, using fallback")
            # Return first available provider as fallback
            provider_name = next(iter(available_providers.keys()))
            return self._create_fallback_decision(provider_name, request, strategy)
        
        # Apply routing strategy
        routing_decision = await self._apply_routing_strategy(
            request, candidate_providers, strategy
        )
        
        # Update request history
        self.request_history.append({
            'timestamp': time.time(),
            'request_type': request.request_type,
            'complexity': request.complexity_score,
            'routed_to': routing_decision.provider,
            'strategy': strategy.value
        })
        
        return routing_decision

    def _filter_circuit_breakers(
        self, 
        providers: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Filter providers based on circuit breaker states."""
        filtered = {}
        current_time = time.time()
        
        for provider_name, provider_info in providers.items():
            circuit_state = self.circuit_states.get(provider_name, CircuitState.CLOSED)
            
            if circuit_state == CircuitState.CLOSED:
                # Provider is available
                filtered[provider_name] = provider_info
                
            elif circuit_state == CircuitState.OPEN:
                # Check if timeout has passed to try half-open
                metrics = self.provider_metrics.get(provider_name)
                if metrics and (current_time - metrics.last_request_time) > self.circuit_breaker_timeout:
                    # Try half-open
                    self.circuit_states[provider_name] = CircuitState.HALF_OPEN
                    filtered[provider_name] = provider_info
                    logger.info(f"Circuit breaker half-open for provider {provider_name}")
                    
            elif circuit_state == CircuitState.HALF_OPEN:
                # Allow limited requests to test recovery
                filtered[provider_name] = provider_info
        
        return filtered

    def _filter_by_capabilities(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Filter providers based on request requirements."""
        filtered = {}
        
        for provider_name, provider_info in providers.items():
            capabilities = self.provider_capabilities.get(provider_name, {})
            
            # Check required capabilities
            if request.requires_vision and not capabilities.get('supports_vision', False):
                continue
                
            if request.requires_function_calling and not capabilities.get('supports_function_calling', False):
                continue
                
            if request.supports_thinking and not capabilities.get('supports_extended_thinking', False):
                continue
            
            # Check success rate threshold
            metrics = self.provider_metrics.get(provider_name)
            if metrics and metrics.success_rate < self.min_success_rate:
                continue
            
            filtered[provider_name] = provider_info
        
        return filtered

    async def _apply_routing_strategy(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]],
        strategy: RoutingStrategy
    ) -> RoutingDecision:
        """Apply the specified routing strategy."""
        
        if strategy == RoutingStrategy.PERFORMANCE_WEIGHTED:
            return await self._performance_weighted_routing(request, providers)
        elif strategy == RoutingStrategy.COST_OPTIMIZED:
            return await self._cost_optimized_routing(request, providers)
        elif strategy == RoutingStrategy.LOAD_BALANCED:
            return await self._load_balanced_routing(request, providers)
        elif strategy == RoutingStrategy.RELIABILITY_FOCUSED:
            return await self._reliability_focused_routing(request, providers)
        elif strategy == RoutingStrategy.ADAPTIVE:
            return await self._adaptive_routing(request, providers)
        else:
            # Fallback to performance weighted
            return await self._performance_weighted_routing(request, providers)

    async def _performance_weighted_routing(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Route based on historical performance."""
        best_provider = None
        best_score = -1
        best_model = None
        
        for provider_name, provider_info in providers.items():
            metrics = self.provider_metrics.get(provider_name)
            capabilities = self.provider_capabilities.get(provider_name, {})
            
            # Calculate performance score
            performance_score = (
                metrics.success_rate * 0.4 +
                (1.0 - min(metrics.average_latency_ms / 5000, 1.0)) * 0.3 +  # Latency score
                min(metrics.total_requests / 100, 1.0) * 0.3  # Experience score
            )
            
            # Adjust for request complexity
            if request.complexity_score > 0.7:
                performance_score *= 1.2  # Prefer experienced providers for complex requests
            
            if performance_score > best_score:
                best_score = performance_score
                best_provider = provider_name
                best_model = self._select_best_model(provider_name, request)
        
        return self._create_routing_decision(
            best_provider, best_model, request, RoutingStrategy.PERFORMANCE_WEIGHTED,
            f"Performance score: {best_score:.3f} (success_rate: {self.provider_metrics[best_provider].success_rate:.2%})"
        )

    async def _cost_optimized_routing(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Route based on cost optimization."""
        best_provider = None
        best_cost = float('inf')
        best_model = None
        
        for provider_name, provider_info in providers.items():
            metrics = self.provider_metrics.get(provider_name)
            provider_type = metrics.provider_type
            cost_per_token = self.cost_estimates.get(provider_type, 0.002)
            
            estimated_cost = request.token_estimate * cost_per_token
            
            # Adjust for reliability
            if metrics.success_rate < 0.8:
                estimated_cost *= 1.5  # Add reliability penalty
            
            if estimated_cost < best_cost:
                best_cost = estimated_cost
                best_provider = provider_name
                best_model = self._select_best_model(provider_name, request)
        
        return self._create_routing_decision(
            best_provider, best_model, request, RoutingStrategy.COST_OPTIMIZED,
            f"Estimated cost: ${best_cost:.4f} for {request.token_estimate} tokens"
        )

    async def _load_balanced_routing(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Route based on current load balancing."""
        best_provider = None
        best_load_score = float('inf')
        best_model = None
        
        current_time = time.time()
        
        for provider_name, provider_info in providers.items():
            metrics = self.provider_metrics.get(provider_name)
            
            # Calculate load score (lower is better)
            recent_requests = sum(1 for req in self.request_history 
                                if req['routed_to'] == provider_name and 
                                current_time - req['timestamp'] < 300)  # Last 5 minutes
            
            load_score = recent_requests * metrics.average_latency_ms
            
            # Adjust for provider capacity
            if load_score < best_load_score:
                best_load_score = load_score
                best_provider = provider_name
                best_model = self._select_best_model(provider_name, request)
        
        return self._create_routing_decision(
            best_provider, best_model, request, RoutingStrategy.LOAD_BALANCED,
            f"Load score: {best_load_score:.1f} (recent requests: {int(best_load_score/metrics.average_latency_ms if metrics.average_latency_ms > 0 else 1000)})"
        )

    async def _reliability_focused_routing(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Route prioritizing reliability."""
        best_provider = None
        best_reliability = 0
        best_model = None
        
        for provider_name, provider_info in providers.items():
            metrics = self.provider_metrics.get(provider_name)
            
            reliability_score = metrics.success_rate
            
            # Prefer providers with low failure rates
            if metrics.consecutive_failures == 0:
                reliability_score *= 1.1
            
            if reliability_score > best_reliability:
                best_reliability = reliability_score
                best_provider = provider_name
                best_model = self._select_best_model(provider_name, request)
        
        return self._create_routing_decision(
            best_provider, best_model, request, RoutingStrategy.RELIABILITY_FOCUSED,
            f"Reliability score: {best_reliability:.2%}"
        )

    async def _adaptive_routing(
        self,
        request: RequestCharacteristics,
        providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Adaptive routing that combines multiple strategies."""
        
        # Analyze request characteristics
        strategy_scores = {}
        
        # Cost sensitivity
        if request.cost_sensitivity == "high":
            cost_decision = await self._cost_optimized_routing(request, providers)
            strategy_scores[RoutingStrategy.COST_OPTIMIZED] = 1.0
        
        # Response time sensitivity
        if request.response_time_sensitivity == "high":
            perf_decision = await self._performance_weighted_routing(request, providers)
            strategy_scores[RoutingStrategy.PERFORMANCE_WEIGHTED] = 1.0
        
        # Urgency
        if request.urgency_level == "high":
            load_decision = await self._load_balanced_routing(request, providers)
            strategy_scores[RoutingStrategy.LOAD_BALANCED] = 1.0
        
        # Complexity
        if request.complexity_score > 0.8:
            reliability_decision = await self._reliability_focused_routing(request, providers)
            strategy_scores[RoutingStrategy.RELIABILITY_FOCUSED] = 1.0
        
        # Default to performance weighted if no specific needs
        if not strategy_scores:
            perf_decision = await self._performance_weighted_routing(request, providers)
            return perf_decision
        
        # Combine strategies based on weights
        combined_scores = defaultdict(float)
        for strategy, decision in strategy_scores.items():
            weight = self.strategy_weights[strategy]
            combined_scores[decision.provider] += weight
        
        # Select provider with highest combined score
        best_provider = max(combined_scores, key=combined_scores.get)
        best_model = self._select_best_model(best_provider, request)
        
        return self._create_routing_decision(
            best_provider, best_model, request, RoutingStrategy.ADAPTIVE,
            f"Combined strategy scores: {dict(combined_scores)}"
        )

    def _select_best_model(
        self,
        provider_name: str,
        request: RequestCharacteristics
    ) -> str:
        """Select the best model for a provider based on request characteristics."""
        capabilities = self.provider_capabilities.get(provider_name, {})
        models = capabilities.get('supported_models', ['default'])
        
        # Select model based on request characteristics
        if request.supports_thinking:
            # Prefer thinking-capable models
            for model in models:
                if 'thinking' in model.lower() or 'k2' in model.lower():
                    return model
        
        if request.complexity_score > 0.8:
            # Prefer larger context models for complex requests
            for model in models:
                if any(x in model.lower() for x in ['4.6', 'k2', 'large']):
                    return model
        
        # Default to first available model
        return models[0] if models else 'default'

    def _create_routing_decision(
        self,
        provider: str,
        model: str,
        request: RequestCharacteristics,
        strategy: RoutingStrategy,
        reasoning: str
    ) -> RoutingDecision:
        """Create a routing decision object."""
        metrics = self.provider_metrics.get(provider)
        
        estimated_latency = metrics.average_latency_ms if metrics else 1000.0
        estimated_cost = request.token_estimate * self.cost_estimates.get(
            metrics.provider_type if metrics else 'unknown', 0.002
        )
        
        # Calculate confidence based on provider metrics
        if metrics:
            confidence = (
                metrics.success_rate * 0.5 +
                (1.0 - min(metrics.consecutive_failures / 10, 1.0)) * 0.3 +
                min(metrics.total_requests / 100, 1.0) * 0.2
            )
        else:
            confidence = 0.5
        
        return RoutingDecision(
            provider=provider,
            model=model,
            strategy_used=strategy,
            confidence=confidence,
            reasoning=reasoning,
            estimated_latency_ms=estimated_latency,
            estimated_cost=estimated_cost,
            fallback_available=len(self.provider_metrics) > 1,
            circuit_state=self.circuit_states.get(provider, CircuitState.CLOSED)
        )

    def _create_fallback_decision(
        self,
        provider: str,
        request: RequestCharacteristics,
        strategy: RoutingStrategy
    ) -> RoutingDecision:
        """Create a fallback routing decision."""
        return self._create_routing_decision(
            provider, 'default', request, strategy,
            "Fallback decision - no viable candidates"
        )

    def record_request_outcome(
        self,
        provider: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0,
        error_message: Optional[str] = None
    ):
        """Record the outcome of a routed request."""
        metrics = self.provider_metrics.get(provider)
        if not metrics:
            return
        
        current_time = time.time()
        
        # Update metrics
        metrics.total_requests += 1
        metrics.last_request_time = current_time
        
        # Update latency (exponential moving average)
        if metrics.average_latency_ms == 0:
            metrics.average_latency_ms = latency_ms
        else:
            metrics.average_latency_ms = (metrics.average_latency_ms * 0.8) + (latency_ms * 0.2)
        
        if success:
            metrics.successful_requests += 1
            metrics.consecutive_failures = 0
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
            
            # Update circuit breaker state
            circuit_state = self.circuit_states.get(provider, CircuitState.CLOSED)
            if (circuit_state == CircuitState.CLOSED and 
                metrics.consecutive_failures >= self.circuit_breaker_threshold):
                self.circuit_states[provider] = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened for provider {provider} "
                             f"({metrics.consecutive_failures} consecutive failures)")
            elif circuit_state == CircuitState.HALF_OPEN and not success:
                # Return to open on failure during half-open test
                self.circuit_states[provider] = CircuitState.OPEN
                logger.info(f"Circuit breaker reopened for provider {provider}")
            elif circuit_state == CircuitState.HALF_OPEN and success:
                # Close circuit on success during half-open test
                self.circuit_states[provider] = CircuitState.CLOSED
                logger.info(f"Circuit breaker closed for provider {provider} (recovered)")
        
        # Update success rate
        metrics._update_success_rate()
        
        logger.debug(
            f"Recorded outcome for {provider}: "
            f"success={success}, latency={latency_ms}ms, "
            f"success_rate={metrics.success_rate:.2%}"
        )

    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing statistics."""
        stats = {
            'total_providers': len(self.provider_metrics),
            'circuit_breaker_states': {
                name: state.value for name, state in self.circuit_states.items()
            },
            'provider_performance': {},
            'strategy_effectiveness': {},
            'recent_request_patterns': {}
        }
        
        # Provider performance
        for name, metrics in self.provider_metrics.items():
            stats['provider_performance'][name] = {
                'success_rate': metrics.success_rate,
                'average_latency_ms': metrics.average_latency_ms,
                'total_requests': metrics.total_requests,
                'consecutive_failures': metrics.consecutive_failures,
                'cost_per_request': metrics.cost_per_request
            }
        
        # Strategy effectiveness
        current_time = time.time()
        for strategy in RoutingStrategy:
            strategy_requests = [
                req for req in self.request_history
                if req['strategy'] == strategy.value and
                current_time - req['timestamp'] < 3600  # Last hour
            ]
            
            if strategy_requests:
                success_count = sum(1 for req in self.request_history
                                  if req['strategy'] == strategy.value and
                                  current_time - req['timestamp'] < 3600 and
                                  # This is simplified - in real implementation,
                                  # you'd track success outcomes separately
                                  req['routed_to'] in self.provider_metrics)
                
                stats['strategy_effectiveness'][strategy.value] = {
                    'requests_last_hour': len(strategy_requests),
                    'estimated_success_rate': success_count / len(strategy_requests) if strategy_requests else 0
                }
        
        return stats

    async def reset_provider_metrics(self, provider_name: str):
        """Reset metrics for a specific provider."""
        if provider_name in self.provider_metrics:
            self.provider_metrics[provider_name] = ProviderMetrics(
                provider_name=provider_name,
                provider_type=self.provider_metrics[provider_name].provider_type
            )
            logger.info(f"Reset metrics for provider {provider_name}")

    async def shutdown(self):
        """Shutdown the router and cleanup resources."""
        logger.info("Enhanced intelligent router shutdown")
        # In a real implementation, you'd save metrics to persistent storage here


# Global router instance
_global_router: Optional[EnhancedIntelligentRouter] = None


async def get_enhanced_router() -> EnhancedIntelligentRouter:
    """Get the global enhanced router instance."""
    global _global_router
    if _global_router is None:
        _global_router = EnhancedIntelligentRouter()
    return _global_router


async def shutdown_enhanced_router():
    """Shutdown the global enhanced router."""
    global _global_router
    if _global_router:
        await _global_router.shutdown()
        _global_router = None
