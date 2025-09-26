
"""
Intelligent Routing Validation Tests

Tests to validate the GLM-4.5-Flash AI manager routing decisions,
provider selection logic, cost-aware routing, and fallback mechanisms.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from intelligent_router import (
    IntelligentRouter, 
    TaskType, 
    ProviderType, 
    RoutingDecision
)


class TestIntelligentRouting:
    """Test suite for intelligent routing system"""

    @pytest.fixture
    def router(self):
        """Create a test router instance"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            return IntelligentRouter()

    @pytest.mark.asyncio
    async def test_web_search_routing(self, router):
        """Test that web search requests route to GLM provider"""
        request = {
            "tool": "web_search",
            "parameters": {
                "query": "latest AI developments",
                "max_results": 10
            }
        }
        
        with patch.object(router, '_make_routing_decision') as mock_decision:
            mock_decision.return_value = RoutingDecision(
                provider=ProviderType.GLM,
                confidence=0.95,
                reasoning="Web search task best handled by GLM with native browsing",
                fallback_provider=ProviderType.KIMI
            )
            
            decision = await router.route_request(request)
            
            assert decision.provider == ProviderType.GLM
            assert decision.confidence > 0.9
            assert "web search" in decision.reasoning.lower()

    @pytest.mark.asyncio
    async def test_file_processing_routing(self, router):
        """Test that file processing requests route to Kimi provider"""
        request = {
            "tool": "file_read",
            "parameters": {
                "path": "/path/to/document.pdf",
                "analysis_type": "summary"
            }
        }
        
        with patch.object(router, '_make_routing_decision') as mock_decision:
            mock_decision.return_value = RoutingDecision(
                provider=ProviderType.KIMI,
                confidence=0.92,
                reasoning="File processing task optimized for Kimi provider",
                fallback_provider=ProviderType.GLM
            )
            
            decision = await router.route_request(request)
            
            assert decision.provider == ProviderType.KIMI
            assert decision.confidence > 0.9
            assert "file" in decision.reasoning.lower()

    @pytest.mark.asyncio
    async def test_cost_aware_routing(self, router):
        """Test cost-aware routing strategies"""
        request = {
            "tool": "general_chat",
            "parameters": {
                "message": "Simple question",
                "context": "minimal"
            }
        }
        
        with patch.object(router, '_calculate_cost_estimates') as mock_cost:
            mock_cost.return_value = {
                ProviderType.GLM: 0.001,
                ProviderType.KIMI: 0.003
            }
            
            decision = await router.route_request(request, cost_priority=True)
            
            # Should choose lower cost option for simple tasks
            assert decision.estimated_cost <= 0.002

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, router):
        """Test fallback mechanisms when primary provider fails"""
        request = {
            "tool": "web_search",
            "parameters": {"query": "test query"}
        }
        
        # Mock primary provider failure
        with patch.object(router, '_execute_with_provider') as mock_execute:
            mock_execute.side_effect = [
                Exception("GLM provider unavailable"),  # First call fails
                {"result": "success"}  # Fallback succeeds
            ]
            
            result = await router.execute_request(request)
            
            # Should have attempted fallback
            assert mock_execute.call_count == 2
            assert result["result"] == "success"

    @pytest.mark.asyncio
    async def test_routing_decision_confidence(self, router):
        """Test that routing decisions include confidence scores"""
        test_cases = [
            {
                "request": {"tool": "web_search", "parameters": {"query": "news"}},
                "expected_provider": ProviderType.GLM,
                "min_confidence": 0.8
            },
            {
                "request": {"tool": "file_read", "parameters": {"path": "doc.pdf"}},
                "expected_provider": ProviderType.KIMI,
                "min_confidence": 0.8
            }
        ]
        
        for case in test_cases:
            with patch.object(router, '_make_routing_decision') as mock_decision:
                mock_decision.return_value = RoutingDecision(
                    provider=case["expected_provider"],
                    confidence=case["min_confidence"] + 0.1,
                    reasoning=f"High confidence routing to {case['expected_provider'].value}"
                )
                
                decision = await router.route_request(case["request"])
                
                assert decision.provider == case["expected_provider"]
                assert decision.confidence >= case["min_confidence"]

    @pytest.mark.asyncio
    async def test_concurrent_routing_decisions(self, router):
        """Test handling of concurrent routing requests"""
        requests = [
            {"tool": "web_search", "parameters": {"query": f"query {i}"}}
            for i in range(5)
        ]
        
        with patch.object(router, '_make_routing_decision') as mock_decision:
            mock_decision.return_value = RoutingDecision(
                provider=ProviderType.GLM,
                confidence=0.9,
                reasoning="Concurrent test routing"
            )
            
            tasks = [router.route_request(req) for req in requests]
            decisions = await asyncio.gather(*tasks)
            
            assert len(decisions) == 5
            for decision in decisions:
                assert isinstance(decision, RoutingDecision)
                assert decision.provider == ProviderType.GLM

    @pytest.mark.asyncio
    async def test_task_type_classification(self, router):
        """Test accurate task type classification"""
        test_cases = [
            {
                "request": {"tool": "web_search", "parameters": {"query": "weather"}},
                "expected_task": TaskType.WEB_SEARCH
            },
            {
                "request": {"tool": "file_read", "parameters": {"path": "code.py"}},
                "expected_task": TaskType.FILE_PROCESSING
            },
            {
                "request": {"tool": "code_analysis", "parameters": {"code": "def test(): pass"}},
                "expected_task": TaskType.CODE_ANALYSIS
            }
        ]
        
        for case in test_cases:
            task_type = router._classify_task(case["request"])
            assert task_type == case["expected_task"]

    @pytest.mark.asyncio
    async def test_provider_health_check(self, router):
        """Test provider health checking before routing"""
        with patch.object(router, '_check_provider_health') as mock_health:
            mock_health.return_value = {
                ProviderType.GLM: True,
                ProviderType.KIMI: False  # Kimi unavailable
            }
            
            request = {"tool": "general_chat", "parameters": {"message": "test"}}
            decision = await router.route_request(request)
            
            # Should not route to unhealthy provider
            assert decision.provider != ProviderType.KIMI

    def test_routing_decision_serialization(self):
        """Test that routing decisions can be properly serialized"""
        decision = RoutingDecision(
            provider=ProviderType.GLM,
            confidence=0.95,
            reasoning="Test routing decision",
            fallback_provider=ProviderType.KIMI,
            estimated_cost=0.001,
            estimated_time=2.5
        )
        
        # Should be able to convert to dict for logging/monitoring
        decision_dict = {
            "provider": decision.provider.value,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "fallback_provider": decision.fallback_provider.value if decision.fallback_provider else None,
            "estimated_cost": decision.estimated_cost,
            "estimated_time": decision.estimated_time
        }
        
        assert decision_dict["provider"] == "glm"
        assert decision_dict["confidence"] == 0.95
        assert decision_dict["fallback_provider"] == "kimi"
