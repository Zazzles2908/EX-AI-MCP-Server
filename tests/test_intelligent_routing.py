
"""
Intelligent Routing Validation Tests

Tests to validate the GLM-4.5-Flash AI manager routing decisions,
provider selection logic, cost-aware routing, and fallback mechanisms.
"""

import asyncio
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
        config = {
            "INTELLIGENT_ROUTING_ENABLED": True,
            "COST_AWARE_ROUTING": True,
            "WEB_SEARCH_PROVIDER": "glm",
            "FILE_PROCESSING_PROVIDER": "kimi",
            "MAX_RETRIES": 3,
            "REQUEST_TIMEOUT": 30
        }
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': 'test-zhipuai-key',
            'MOONSHOT_API_KEY': 'test-moonshot-key'
        }):
            return IntelligentRouter(config)

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
        
        decision = await router.route_request(request)
        
        # Web search should route to GLM
        assert decision.provider == ProviderType.GLM
        assert decision.confidence > 0.8
        assert "web" in decision.reasoning.lower() or "search" in decision.reasoning.lower()

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
        
        decision = await router.route_request(request)
        
        # File processing should route to Kimi
        assert decision.provider == ProviderType.KIMI
        assert decision.confidence > 0.8
        assert "file" in decision.reasoning.lower() or "process" in decision.reasoning.lower()

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
        
        # Test that routing considers cost estimates
        decision = await router.route_request(request)
        
        # Verify cost estimates are reasonable
        assert decision.estimated_cost >= 0
        assert decision.estimated_time >= 0

    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, router):
        """Test fallback mechanisms when primary provider fails"""
        request = {
            "tool": "web_search",
            "parameters": {"query": "test query"}
        }
        
        # Test that routing decisions include fallback providers
        decision = await router.route_request(request)
        
        # Verify fallback is configured
        assert decision.fallback_provider is not None
        assert decision.fallback_provider != decision.provider

    @pytest.mark.asyncio
    async def test_routing_decision_confidence(self, router):
        """Test that routing decisions include confidence scores"""
        request = {"tool": "web_search", "parameters": {"query": "news"}}
        
        decision = await router.route_request(request)
        
        # Verify confidence is within valid range
        assert 0 <= decision.confidence <= 1
        assert decision.confidence > 0.7  # Should have high confidence for clear tasks

    @pytest.mark.asyncio
    async def test_task_type_classification(self, router):
        """Test accurate task type classification"""
        # Test web search classification
        web_request = {"tool": "web_search", "parameters": {"query": "weather"}}
        web_task = await router._analyze_task_type(web_request)
        assert web_task == TaskType.WEB_SEARCH
        
        # Test file processing classification
        file_request = {"tool": "file_read", "parameters": {"path": "code.py"}}
        file_task = await router._analyze_task_type(file_request)
        assert file_task == TaskType.FILE_PROCESSING
        
        # Test code analysis classification
        code_request = {"tool": "code_analysis", "parameters": {"code": "def test(): pass"}}
        code_task = await router._analyze_task_type
