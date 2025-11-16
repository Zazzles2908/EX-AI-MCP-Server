"""
Enhanced Router Integration Middleware

This module provides integration middleware to add enhanced intelligent routing
capabilities to the existing EX-AI MCP Server routing system.

Features:
- Transparent integration with existing providers
- Request characteristic extraction
- Strategy-based routing decisions
- Performance tracking and adaptation
- Circuit breaker protection
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from .enhanced_intelligent_router import (
    EnhancedIntelligentRouter,
    RoutingStrategy,
    RequestCharacteristics,
    RoutingDecision,
    get_enhanced_router
)
from .base import ModelProvider, ProviderType

logger = logging.getLogger(__name__)


class EnhancedRouterMiddleware:
    """
    Middleware for enhanced intelligent routing integration.
    
    This middleware:
    - Wraps existing routing logic transparently
    - Extracts request characteristics for intelligent routing
    - Provides fallback to existing routing when needed
    - Tracks performance and adapts over time
    """
    
    def __init__(
        self,
        enhanced_router: Optional[EnhancedIntelligentRouter] = None,
        enable_fallback: bool = True,
        enable_performance_tracking: bool = True
    ):
        """
        Initialize enhanced router middleware.
        
        Args:
            enhanced_router: Enhanced router instance
            enable_fallback: Enable fallback to original routing
            enable_performance_tracking: Enable performance tracking
        """
        self.enhanced_router = enhanced_router
        self.enable_fallback = enable_fallback
        self.enable_performance_tracking = enable_performance_tracking
        
        # Original routing functions (for fallback)
        self.original_routing_functions = {}
        
        logger.info(
            f"EnhancedRouterMiddleware initialized: "
            f"fallback={enable_fallback}, "
            f"tracking={enable_performance_tracking}"
        )

    def _get_enhanced_router(self) -> EnhancedIntelligentRouter:
        """Get or create the enhanced router instance."""
        if self.enhanced_router is None:
            # Create a new router if not provided
            self.enhanced_router = EnhancedIntelligentRouter()
        return self.enhanced_router

    async def route_with_enhanced_intelligence(
        self,
        request_data: Dict[str, Any],
        available_providers: Dict[str, Dict[str, Any]],
        strategy: Optional[RoutingStrategy] = None
    ) -> Tuple[RoutingDecision, bool]:
        """
        Route request using enhanced intelligence with fallback.
        
        Args:
            request_data: Request data
            available_providers: Available providers
            strategy: Optional routing strategy
            
        Returns:
            Tuple of (routing_decision, used_enhanced_routing)
        """
        try:
            # Get router instance
            router = self._get_enhanced_router()
            
            # Extract request characteristics
            request_characteristics = self.extract_request_characteristics(request_data)
            
            # Use enhanced routing
            routing_decision = await router.route_request(
                request_characteristics,
                available_providers,
                strategy
            )
            
            logger.debug(
                f"Enhanced routing decision: {routing_decision.provider}/"
                f"{routing_decision.model} via {routing_decision.strategy_used.value}"
            )
            
            return routing_decision, True
            
        except Exception as e:
            logger.error(f"Enhanced routing failed: {e}")
            
            if self.enable_fallback:
                # Use fallback routing
                routing_decision = await self._fallback_routing(
                    request_data, available_providers
                )
                return routing_decision, False
            else:
                raise

    def register_original_routing_function(self, name: str, function):
        """Register an original routing function for fallback."""
        self.original_routing_functions[name] = function
        logger.debug(f"Registered original routing function: {name}")

    def extract_request_characteristics(
        self,
        request_data: Dict[str, Any]
    ) -> RequestCharacteristics:
        """
        Extract request characteristics from request data.
        
        Args:
            request_data: Request data dictionary
            
        Returns:
            RequestCharacteristics object
        """
        # Extract request type
        request_type = self._determine_request_type(request_data)
        
        # Estimate complexity
        complexity_score = self._estimate_complexity(request_data)
        
        # Estimate token usage
        token_estimate = self._estimate_token_usage(request_data)
        
        # Check required capabilities
        supports_thinking = request_data.get('thinking_mode', False)
        requires_vision = bool(request_data.get('images', []))
        requires_function_calling = bool(request_data.get('tools', []))
        
        # Determine sensitivity levels
        urgency_level = request_data.get('urgency_level', 'medium')
        cost_sensitivity = request_data.get('cost_sensitivity', 'medium')
        response_time_sensitivity = request_data.get('response_time_sensitivity', 'medium')
        
        return RequestCharacteristics(
            request_type=request_type,
            complexity_score=complexity_score,
            token_estimate=token_estimate,
            supports_thinking=supports_thinking,
            requires_vision=requires_vision,
            requires_function_calling=requires_function_calling,
            urgency_level=urgency_level,
            cost_sensitivity=cost_sensitivity,
            response_time_sensitivity=response_time_sensitivity
        )

    def _determine_request_type(self, request_data: Dict[str, Any]) -> str:
        """Determine the type of request based on data."""
        tool_name = request_data.get('tool_name', '').lower()
        prompt = request_data.get('prompt', '').lower()
        messages = request_data.get('messages', [])
        
        # Analyze tool name
        if any(word in tool_name for word in ['debug', 'analyze', 'review']):
            return 'debug'
        elif any(word in tool_name for word in ['chat', 'talk', 'conversation']):
            return 'chat'
        elif any(word in tool_name for word in ['generate', 'create', 'write']):
            return 'generate'
        elif any(word in tool_name for word in ['search', 'find', 'query']):
            return 'search'
        elif any(word in tool_name for word in ['image', 'vision', 'visual']):
            return 'vision'
        elif any(word in tool_name for word in ['planning', 'strategy', 'design']):
            return 'planning'
        
        # Analyze prompt content
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ['debug', 'error', 'bug', 'issue']):
            return 'debug'
        elif any(word in prompt_lower for word in ['analyze', 'explain', 'understand']):
            return 'analyze'
        elif any(word in prompt_lower for word in ['create', 'generate', 'write']):
            return 'generate'
        
        # Default to general chat
        return 'chat'

    def _estimate_complexity(self, request_data: Dict[str, Any]) -> float:
        """Estimate request complexity (0.0 to 1.0)."""
        complexity_indicators = []
        
        # Tool-based indicators
        tool_name = request_data.get('tool_name', '').lower()
        if any(word in tool_name for word in ['debug', 'analyze', 'plan']):
            complexity_indicators.append(0.8)
        elif any(word in tool_name for word in ['search', 'query']):
            complexity_indicators.append(0.6)
        
        # Content-based indicators
        prompt = request_data.get('prompt', '')
        messages = request_data.get('messages', [])
        
        # Length indicators
        total_text = prompt + ' '.join(str(msg.get('content', '')) for msg in messages)
        if len(total_text) > 2000:
            complexity_indicators.append(0.7)
        elif len(total_text) > 1000:
            complexity_indicators.append(0.5)
        
        # Multi-step indicators
        if 'steps' in prompt.lower() or 'process' in prompt.lower():
            complexity_indicators.append(0.8)
        
        # Technical indicators
        if any(word in total_text.lower() for word in ['algorithm', 'architecture', 'design pattern']):
            complexity_indicators.append(0.9)
        
        # Return average or default
        if complexity_indicators:
            return sum(complexity_indicators) / len(complexity_indicators)
        else:
            return 0.5  # Medium complexity

    def _estimate_token_usage(self, request_data: Dict[str, Any]) -> int:
        """Estimate token usage for the request."""
        prompt = request_data.get('prompt', '')
        messages = request_data.get('messages', [])
        
        # Estimate input tokens
        total_text = prompt + ' '.join(str(msg.get('content', '')) for msg in messages)
        estimated_input_tokens = len(total_text) // 4  # Rough estimation
        
        # Estimate output tokens based on request type
        tool_name = request_data.get('tool_name', '').lower()
        max_tokens = request_data.get('max_output_tokens')
        
        if max_tokens:
            estimated_output_tokens = max_tokens
        elif any(word in tool_name for word in ['debug', 'analyze']):
            estimated_output_tokens = 2000  # Detailed analysis
        elif any(word in tool_name for word in ['generate', 'create']):
            estimated_output_tokens = 1500  # Content generation
        elif any(word in tool_name for word in ['search', 'find']):
            estimated_output_tokens = 500   # Brief responses
        else:
            estimated_output_tokens = 1000  # Default
        
        return estimated_input_tokens + estimated_output_tokens

    def _get_enhanced_router(self) -> EnhancedIntelligentRouter:
        """Get or create the enhanced router instance."""
        if self.enhanced_router is None:
            # Create a new router if not provided
            self.enhanced_router = EnhancedIntelligentRouter()
        return self.enhanced_router
        """
        Route request using enhanced intelligence with fallback.
        
        Args:
            request_data: Request data
            available_providers: Available providers
            strategy: Optional routing strategy
            
        Returns:
            Tuple of (routing_decision, used_enhanced_routing)
        """
        try:
            # Extract request characteristics
            request_characteristics = self.extract_request_characteristics(request_data)
            
            # Use enhanced routing
            routing_decision = await self.enhanced_router.route_request(
                request_characteristics,
                available_providers,
                strategy
            )
            
            logger.debug(
                f"Enhanced routing decision: {routing_decision.provider}/"
                f"{routing_decision.model} via {routing_decision.strategy_used.value}"
            )
            
            return routing_decision, True
            
        except Exception as e:
            logger.error(f"Enhanced routing failed: {e}")
            
            if self.enable_fallback:
                # Use fallback routing
                routing_decision = await self._fallback_routing(
                    request_data, available_providers
                )
                return routing_decision, False
            else:
                raise

    async def _fallback_routing(
        self,
        request_data: Dict[str, Any],
        available_providers: Dict[str, Dict[str, Any]]
    ) -> RoutingDecision:
        """Fallback to original routing logic."""
        
        # Use the first available provider as simple fallback
        provider_name = next(iter(available_providers.keys()))
        provider_info = available_providers[provider_name]
        
        # Select a basic model
        models = provider_info.get('models', ['default'])
        model = models[0] if models else 'default'
        
        return RoutingDecision(
            provider=provider_name,
            model=model,
            strategy_used=RoutingStrategy.PERFORMANCE_WEIGHTED,
            confidence=0.5,
            reasoning="Fallback routing - enhanced intelligence unavailable",
            estimated_latency_ms=1000.0,
            estimated_cost=0.001,
            fallback_available=False
        )

    async def record_request_outcome(
        self,
        provider: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0,
        error_message: Optional[str] = None
    ):
        """Record request outcome for performance tracking."""
        if self.enable_performance_tracking:
            self.enhanced_router.record_request_outcome(
                provider=provider,
                success=success,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
                error_message=error_message
            )

    def get_routing_recommendations(self) -> Dict[str, Any]:
        """Get routing recommendations and statistics."""
        stats = self.enhanced_router.get_routing_statistics()
        
        # Add middleware-specific recommendations
        recommendations = {
            'strategy_recommendations': self._get_strategy_recommendations(),
            'performance_insights': self._get_performance_insights(stats),
            'provider_health': self._get_provider_health(stats),
            'optimization_suggestions': self._get_optimization_suggestions(stats)
        }
        
        return {
            'statistics': stats,
            'recommendations': recommendations
        }

    def _get_strategy_recommendations(self) -> Dict[str, str]:
        """Get strategy recommendations based on recent patterns."""
        recent_requests = [
            req for req in self.enhanced_router.request_history
            if req['timestamp'] > time.time() - 3600  # Last hour
        ]
        
        if not recent_requests:
            return {'default': 'Insufficient data for recommendations'}
        
        # Analyze request types
        request_types = {}
        for req in recent_requests:
            req_type = req['request_type']
            request_types[req_type] = request_types.get(req_type, 0) + 1
        
        # Recommend strategies based on request patterns
        recommendations = {}
        for req_type, count in request_types.items():
            if count >= 10:  # Sufficient data
                if req_type in ['debug', 'analyze']:
                    recommendations[req_type] = 'RELIABILITY_FOCUSED - High accuracy needed'
                elif req_type in ['chat', 'generate']:
                    recommendations[req_type] = 'COST_OPTIMIZED - Balance cost and quality'
                elif req_type == 'search':
                    recommendations[req_type] = 'PERFORMANCE_WEIGHTED - Fast responses needed'
                else:
                    recommendations[req_type] = 'ADAPTIVE - Let system choose optimal strategy'
        
        return recommendations

    def _get_performance_insights(self, stats: Dict[str, Any]) -> Dict[str, str]:
        """Get performance insights from statistics."""
        insights = {}
        
        # Analyze provider performance
        provider_performance = stats.get('provider_performance', {})
        for provider, perf in provider_performance.items():
            success_rate = perf.get('success_rate', 0)
            avg_latency = perf.get('average_latency_ms', 0)
            
            if success_rate < 0.8:
                insights[provider] = f"Low success rate: {success_rate:.1%} - Consider circuit breaker"
            elif avg_latency > 2000:
                insights[provider] = f"High latency: {avg_latency:.0f}ms - May impact user experience"
            else:
                insights[provider] = f"Performance: {success_rate:.1%} success, {avg_latency:.0f}ms latency"
        
        return insights

    def _get_provider_health(self, stats: Dict[str, Any]) -> Dict[str, str]:
        """Get provider health status."""
        health_status = {}
        circuit_states = stats.get('circuit_breaker_states', {})
        
        for provider, state in circuit_states.items():
            if state == 'open':
                health_status[provider] = 'UNHEALTHY - Circuit breaker open'
            elif state == 'half_open':
                health_status[provider] = 'RECOVERING - Testing recovery'
            else:
                health_status[provider] = 'HEALTHY - Normal operation'
        
        return health_status

    def _get_optimization_suggestions(self, stats: Dict[str, Any]) -> List[str]:
        """Get optimization suggestions."""
        suggestions = []
        
        provider_performance = stats.get('provider_performance', {})
        
        # Check for underperforming providers
        for provider, perf in provider_performance.items():
            success_rate = perf.get('success_rate', 0)
            total_requests = perf.get('total_requests', 0)
            
            if success_rate < 0.7:
                suggestions.append(f"Consider disabling {provider} - Low success rate: {success_rate:.1%}")
            
            if total_requests < 10:
                suggestions.append(f"Consider removing {provider} - Insufficient usage data")
        
        # Check circuit breaker states
        circuit_states = stats.get('circuit_breaker_states', {})
        open_providers = [p for p, state in circuit_states.items() if state == 'open']
        if open_providers:
            suggestions.append(f"Circuit breakers open for: {', '.join(open_providers)} - Check provider status")
        
        return suggestions

    async def reset_provider_metrics(self, provider_name: str):
        """Reset metrics for a specific provider."""
        await self.enhanced_router.reset_provider_metrics(provider_name)

    def configure_routing_strategy(self, strategy: RoutingStrategy, weight: float = 1.0):
        """Configure routing strategy weights."""
        if strategy in self.enhanced_router.strategy_weights:
            self.enhanced_router.strategy_weights[strategy] = weight
            logger.info(f"Updated strategy weight for {strategy.value}: {weight}")

    def configure_provider_cost(self, provider_type: str, cost_per_token: float):
        """Configure provider cost estimates."""
        self.enhanced_router.cost_estimates[provider_type] = cost_per_token
        logger.info(f"Updated cost estimate for {provider_type}: ${cost_per_token}/token")


# Global middleware instance
_global_middleware: Optional[EnhancedRouterMiddleware] = None


async def get_enhanced_router_middleware() -> EnhancedRouterMiddleware:
    """Get the global enhanced router middleware instance."""
    global _global_middleware
    if _global_middleware is None:
        enhanced_router = await get_enhanced_router()
        _global_middleware = EnhancedRouterMiddleware(enhanced_router)
    return _global_middleware


# Integration helpers

async def enhance_existing_routing(
    existing_routing_function,
    provider_registry,
    strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE
) -> EnhancedRouterMiddleware:
    """
    Enhance existing routing with intelligent capabilities.
    
    Args:
        existing_routing_function: Original routing function
        provider_registry: Provider registry object
        strategy: Default routing strategy
        
    Returns:
        EnhancedRouterMiddleware instance
    """
    middleware = await get_enhanced_router_middleware()
    
    # Register providers with enhanced router
    for provider_name, provider_info in provider_registry.items():
        await middleware.enhanced_router.register_provider(
            provider_name=provider_name,
            provider_type=provider_info.get('type', 'unknown'),
            capabilities=provider_info.get('capabilities', {}),
            base_url=provider_info.get('base_url'),
            cost_per_token=provider_info.get('cost_per_token')
        )
    
    # Register original routing for fallback
    middleware.register_original_routing_function('original', existing_routing_function)
    
    logger.info(f"Enhanced routing configured with strategy: {strategy.value}")
    
    return middleware


async def create_enhanced_routing_wrapper(
    existing_provider_functions: Dict[str, callable],
    strategy: RoutingStrategy = RoutingStrategy.ADAPTIVE
) -> EnhancedRouterMiddleware:
    """
    Create enhanced routing wrapper for provider functions.
    
    Args:
        existing_provider_functions: Dict of provider name to function
        strategy: Default routing strategy
        
    Returns:
        EnhancedRouterMiddleware instance
    """
    middleware = await get_enhanced_router_middleware()
    
    # Register provider functions
    for provider_name, provider_func in existing_provider_functions.items():
        # Extract provider type from function name or metadata
        provider_type = provider_name.split('_')[0] if '_' in provider_name else provider_name
        
        # Get provider capabilities (simplified)
        capabilities = {
            'supports_vision': 'vision' in provider_name.lower(),
            'supports_function_calling': True,  # Assume most support this
            'supports_extended_thinking': 'thinking' in provider_name.lower(),
            'supported_models': ['default']  # Simplified
        }
        
        await middleware.enhanced_router.register_provider(
            provider_name=provider_name,
            provider_type=provider_type,
            capabilities=capabilities
        )
    
    return middleware
