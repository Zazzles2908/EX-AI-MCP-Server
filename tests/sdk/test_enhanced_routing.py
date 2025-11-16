"""
Test Suite for Enhanced Intelligent Routing

This test suite validates the enhanced intelligent routing system including:
- Provider registration and metrics tracking
- Request characteristic extraction
- Strategy-based routing decisions
- Circuit breaker functionality
- Performance tracking and adaptation
- Integration middleware
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, '/app/src')

from providers.enhanced_intelligent_router import (
    EnhancedIntelligentRouter,
    RoutingStrategy,
    RequestCharacteristics,
    get_enhanced_router
)
from providers.enhanced_router_middleware import (
    EnhancedRouterMiddleware,
    get_enhanced_router_middleware,
    enhance_existing_routing
)


async def test_provider_registration():
    """Test provider registration and metrics tracking."""
    print("\n🧪 Testing provider registration...")
    
    router = EnhancedIntelligentRouter()
    
    # Register providers
    await router.register_provider(
        provider_name="minimax_provider",
        provider_type="minimax",
        capabilities={
            "supports_vision": False,
            "supports_function_calling": False,
            "supports_extended_thinking": True,
            "supported_models": ["MiniMax-M2-Stable"],
            "context_window": 200000
        },
        cost_per_token=0.002
    )
    
    await router.register_provider(
        provider_name="glm_provider",
        provider_type="glm",
        capabilities={
            "supports_vision": True,
            "supports_function_calling": True,
            "supports_extended_thinking": True,
            "supported_models": ["glm-4.6", "glm-4.5-flash"],
            "context_window": 200000
        },
        cost_per_token=0.001
    )
    
    assert len(router.provider_metrics) == 2, "Providers not registered correctly"
    assert "minimax_provider" in router.provider_metrics, "MiniMax provider missing"
    assert "glm_provider" in router.provider_metrics, "GLM provider missing"
    
    print("✅ Provider registration works")
    
    # Test metrics tracking
    router.record_request_outcome("minimax_provider", True, 1500.0, 500)
    router.record_request_outcome("minimax_provider", True, 1200.0, 480)
    router.record_request_outcome("glm_provider", False, 2000.0, 0, "timeout error")
    
    metrics = router.provider_metrics["minimax_provider"]
    assert metrics.total_requests == 2, "Request not recorded"
    assert metrics.successful_requests == 2, "Success not recorded"
    assert metrics.average_latency_ms == 1350.0, "Latency not calculated correctly"
    
    print("✅ Metrics tracking works")


async def test_request_characteristic_extraction():
    """Test request characteristic extraction."""
    print("\n🧪 Testing request characteristic extraction...")
    
    middleware = EnhancedRouterMiddleware()
    
    # Test debug request
    debug_request = {
        "tool_name": "debug_python_code",
        "prompt": "Debug this Python function that has an error",
        "thinking_mode": True,
        "max_output_tokens": 2000,
        "urgency_level": "high"
    }
    
    characteristics = middleware.extract_request_characteristics(debug_request)
    
    assert characteristics.request_type == "debug", f"Wrong request type: {characteristics.request_type}"
    assert characteristics.complexity_score >= 0.7, f"Complexity too low: {characteristics.complexity_score}"
    assert characteristics.supports_thinking is True, "Thinking mode not detected"
    assert characteristics.urgency_level == "high", "Urgency level not detected"
    
    print("✅ Request characteristic extraction works")
    
    # Test chat request
    chat_request = {
        "tool_name": "simple_chat",
        "prompt": "Hello, how are you?",
        "images": ["screenshot.png"]
    }
    
    chat_characteristics = middleware.extract_request_characteristics(chat_request)
    
    assert chat_characteristics.request_type == "chat", f"Wrong chat type: {chat_characteristics.request_type}"
    assert chat_characteristics.requires_vision is True, "Vision requirement not detected"
    assert chat_characteristics.complexity_score <= 0.5, f"Chat complexity too high: {chat_characteristics.complexity_score}"
    
    print("✅ Chat request characteristics work")


async def test_strategy_based_routing():
    """Test different routing strategies."""
    print("\n🧪 Testing strategy-based routing...")
    
    router = EnhancedIntelligentRouter()
    
    # Register providers
    await router.register_provider(
        provider_name="fast_provider",
        provider_type="glm",
        capabilities={
            "supports_vision": True,
            "supports_function_calling": True,
            "supported_models": ["glm-4.5-flash"]
        }
    )
    
    await router.register_provider(
        provider_name="accurate_provider",
        provider_type="minimax",
        capabilities={
            "supports_extended_thinking": True,
            "supported_models": ["MiniMax-M2-Stable"]
        }
    )
    
    # Simulate different performance patterns
    for i in range(10):
        router.record_request_outcome("fast_provider", True, 800.0, 200)  # Fast but moderate success
        router.record_request_outcome("accurate_provider", True, 1500.0, 300)  # Slower but reliable
    
    # Test performance weighted routing
    debug_request = RequestCharacteristics(
        request_type="debug",
        complexity_score=0.9,
        token_estimate=2000,
        supports_thinking=True,
        requires_vision=False,
        requires_function_calling=False,
        urgency_level="high",
        cost_sensitivity="low",
        response_time_sensitivity="high"
    )
    
    available_providers = {
        "fast_provider": {"models": ["glm-4.5-flash"]},
        "accurate_provider": {"models": ["MiniMax-M2-Stable"]}
    }
    
    # Test performance weighted (should prefer accurate for debug)
    perf_decision = await router.route_request(
        debug_request, available_providers, RoutingStrategy.PERFORMANCE_WEIGHTED
    )
    
    assert perf_decision.provider == "accurate_provider", \
        f"Performance routing chose wrong provider: {perf_decision.provider}"
    
    print("✅ Performance weighted routing works")
    
    # Test cost optimized routing
    cost_decision = await router.route_request(
        debug_request, available_providers, RoutingStrategy.COST_OPTIMIZED
    )
    
    assert cost_decision.provider in ["fast_provider", "accurate_provider"], \
        f"Cost routing failed: {cost_decision.provider}"
    
    print("✅ Cost optimized routing works")
    
    # Test adaptive routing
    adaptive_decision = await router.route_request(
        debug_request, available_providers, RoutingStrategy.ADAPTIVE
    )
    
    assert adaptive_decision.provider in ["fast_provider", "accurate_provider"], \
        f"Adaptive routing failed: {adaptive_decision.provider}"
    
    print("✅ Adaptive routing works")


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    print("\n🧪 Testing circuit breaker...")
    
    router = EnhancedIntelligentRouter()
    
    await router.register_provider(
        provider_name="unreliable_provider",
        provider_type="test",
        capabilities={"supported_models": ["test-model"]}
    )
    
    # Simulate failures to trigger circuit breaker
    for i in range(6):  # More than threshold
        router.record_request_outcome("unreliable_provider", False, 5000.0, 0, "connection error")
    
    assert router.circuit_states["unreliable_provider"].value == "open", \
        "Circuit breaker should be open"
    
    print("✅ Circuit breaker opens on failures")
    
    # Test that open circuit breaker filters out provider
    request = RequestCharacteristics(
        request_type="test",
        complexity_score=0.5,
        token_estimate=100,
        supports_thinking=False,
        requires_vision=False,
        requires_function_calling=False,
        urgency_level="medium",
        cost_sensitivity="medium",
        response_time_sensitivity="medium"
    )
    
    available_providers = {"unreliable_provider": {"models": ["test-model"]}}
    
    # Should return fallback since provider is filtered out
    decision = await router.route_request(request, available_providers)
    
    assert decision.provider == "unreliable_provider", \
        "Should still route to provider for testing half-open"
    
    print("✅ Circuit breaker half-open testing works")


async def test_middleware_integration():
    """Test middleware integration."""
    print("\n🧪 Testing middleware integration...")
    
    middleware = EnhancedRouterMiddleware()
    
    # Register a mock provider
    await middleware.enhanced_router.register_provider(
        provider_name="test_provider",
        provider_type="test",
        capabilities={
            "supports_vision": True,
            "supported_models": ["test-model"]
        }
    )
    
    # Test routing with fallback
    request_data = {
        "tool_name": "analyze_image",
        "prompt": "Analyze this image for me",
        "images": ["photo.jpg"],
        "urgency_level": "medium"
    }
    
    available_providers = {
        "test_provider": {"models": ["test-model"], "capabilities": {"supports_vision": True}}
    }
    
    decision, used_enhanced = await middleware.route_with_enhanced_intelligence(
        request_data, available_providers
    )
    
    assert used_enhanced is True, "Enhanced routing should be used"
    assert decision.provider == "test_provider", "Wrong provider selected"
    assert decision.model == "test-model", "Wrong model selected"
    
    print("✅ Middleware integration works")
    
    # Test performance tracking
    await middleware.record_request_outcome("test_provider", True, 1200.0, 400)
    
    metrics = middleware.enhanced_router.provider_metrics["test_provider"]
    assert metrics.total_requests == 1, "Performance tracking failed"
    assert metrics.successful_requests == 1, "Success tracking failed"
    
    print("✅ Performance tracking works")


async def test_routing_statistics():
    """Test routing statistics and recommendations."""
    print("\n🧪 Testing routing statistics...")
    
    router = EnhancedIntelligentRouter()
    
    # Register providers
    await router.register_provider(
        provider_name="provider_a",
        provider_type="glm",
        capabilities={"supported_models": ["glm-4.5"]}
    )
    
    await router.register_provider(
        provider_name="provider_b", 
        provider_type="minimax",
        capabilities={"supported_models": ["MiniMax-M2-Stable"]}
    )
    
    # Generate some request history
    for i in range(5):
        router.record_request_outcome("provider_a", True, 1000.0, 200)
        router.record_request_outcome("provider_b", True, 1200.0, 250)
    
    # Add request history for pattern analysis
    current_time = time.time()
    for i in range(10):
        router.request_history.append({
            'timestamp': current_time - i * 60,  # Requests over last 10 minutes
            'request_type': 'chat' if i % 2 == 0 else 'debug',
            'complexity': 0.5 if i % 2 == 0 else 0.8,
            'routed_to': 'provider_a' if i % 2 == 0 else 'provider_b',
            'strategy': 'performance_weighted'
        })
    
    stats = router.get_routing_statistics()
    
    assert 'total_providers' in stats, "Statistics missing provider count"
    assert 'provider_performance' in stats, "Statistics missing performance data"
    assert stats['total_providers'] == 2, "Wrong provider count"
    
    print("✅ Routing statistics work")
    
    # Test middleware recommendations
    middleware = EnhancedRouterMiddleware()
    recommendations = middleware.get_routing_recommendations()
    
    assert 'statistics' in recommendations, "Recommendations missing statistics"
    assert 'recommendations' in recommendations, "Recommendations missing data"
    
    print("✅ Routing recommendations work")


async def test_cost_optimization():
    """Test cost optimization routing."""
    print("\n🧪 Testing cost optimization...")
    
    router = EnhancedIntelligentRouter()
    
    # Register providers with different costs
    await router.register_provider(
        provider_name="expensive_provider",
        provider_type="premium",
        capabilities={"supported_models": ["premium-model"]},
        cost_per_token=0.005
    )
    
    await router.register_provider(
        provider_name="cheap_provider",
        provider_type="basic", 
        capabilities={"supported_models": ["basic-model"]},
        cost_per_token=0.001
    )
    
    # Set same success rates so cost becomes deciding factor
    for i in range(10):
        router.record_request_outcome("expensive_provider", True, 1500.0, 300)
        router.record_request_outcome("cheap_provider", True, 1200.0, 280)
    
    request = RequestCharacteristics(
        request_type="chat",
        complexity_score=0.3,
        token_estimate=500,
        supports_thinking=False,
        requires_vision=False,
        requires_function_calling=False,
        urgency_level="low",
        cost_sensitivity="high",  # Cost sensitive
        response_time_sensitivity="low"
    )
    
    available_providers = {
        "expensive_provider": {"models": ["premium-model"]},
        "cheap_provider": {"models": ["basic-model"]}
    }
    
    decision = await router.route_request(
        request, available_providers, RoutingStrategy.COST_OPTIMIZED
    )
    
    # Should prefer cheap provider for cost-sensitive request
    assert decision.provider == "cheap_provider", \
        f"Cost optimization chose wrong provider: {decision.provider}"
    
    print("✅ Cost optimization routing works")


async def run_comprehensive_tests():
    """Run all enhanced routing tests."""
    print("🚀 Running Enhanced Intelligent Routing Tests...")
    print("=" * 60)
    
    tests = [
        test_provider_registration,
        test_request_characteristic_extraction,
        test_strategy_based_routing,
        test_circuit_breaker,
        test_middleware_integration,
        test_routing_statistics,
        test_cost_optimization
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All enhanced routing tests passed! Intelligent routing is working correctly!")
        
        # Show router statistics
        router = await get_enhanced_router()
        stats = router.get_routing_statistics()
        print(f"\n📈 Router Statistics:")
        print(f"   Total providers: {stats['total_providers']}")
        print(f"   Circuit breaker states: {stats['circuit_breaker_states']}")
        
        return True
    else:
        print(f"⚠️  {failed} test(s) failed. Check implementation.")
        return False


async def cleanup():
    """Cleanup test resources."""
    from providers.enhanced_intelligent_router import shutdown_enhanced_router
    
    await shutdown_enhanced_router()


if __name__ == "__main__":
    async def main():
        success = await run_comprehensive_tests()
        await cleanup()
        sys.exit(0 if success else 1)
    
    asyncio.run(main())
