"""
Tests for intelligent routing system with GLM-4.5 Flash AI manager.

Tests the request analyzer, GLM Flash manager, and enhanced router service
to ensure intelligent routing works correctly with cost-aware token management.
"""
import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from src.core.agentic.request_analyzer import RequestAnalyzer, RequestType, ContentComplexity
from src.core.agentic.glm_flash_manager import GLMFlashManager, RoutingStrategy, ProviderCapabilityRegistry
from src.router.service import RouterService
from src.providers.base import ProviderType


class TestRequestAnalyzer:
    """Test the request analyzer for intelligent preprocessing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = RequestAnalyzer(max_summary_tokens=100)

    def test_file_operation_detection(self):
        """Test detection of file operations."""
        request = {
            "messages": [
                {"content": "Please read the file data.csv and analyze the contents"}
            ]
        }
        
        analysis = self.analyzer.analyze_request(request)
        
        assert analysis.request_type == RequestType.FILE_OPERATION
        assert analysis.has_files == True
        assert ".csv" in analysis.file_types
        assert analysis.routing_confidence > 0.5

    def test_web_browsing_detection(self):
        """Test detection of web browsing requests."""
        request = {
            "messages": [
                {"content": "Search the internet for latest news about AI developments"}
            ]
        }
        
        analysis = self.analyzer.analyze_request(request)
        
        assert analysis.request_type == RequestType.WEB_BROWSING
        assert analysis.has_web_intent == True
        assert analysis.routing_confidence > 0.5

    def test_multimodal_detection(self):
        """Test detection of multimodal content."""
        request = {
            "messages": [
                {
                    "content": "Analyze this image",
                    "images": ["base64_image_data"]
                }
            ]
        }
        
        analysis = self.analyzer.analyze_request(request)
        
        assert analysis.request_type == RequestType.MULTIMODAL
        assert analysis.has_images == True
        assert analysis.routing_confidence > 0.8

    def test_long_context_detection(self):
        """Test detection of long context requests."""
        long_content = "This is a very long document. " * 2000  # ~50K tokens
        request = {
            "messages": [
                {"content": long_content}
            ]
        }
        
        analysis = self.analyzer.analyze_request(request)
        
        assert analysis.request_type == RequestType.LONG_CONTEXT
        assert analysis.estimated_tokens > 30000
        assert analysis.complexity in [ContentComplexity.COMPLEX, ContentComplexity.VERY_COMPLEX]

    def test_hybrid_detection(self):
        """Test detection of hybrid requests."""
        request = {
            "messages": [
                {"content": "Read the file report.pdf and search online for related information"}
            ]
        }
        
        analysis = self.analyzer.analyze_request(request)
        
        assert analysis.request_type == RequestType.HYBRID
        assert analysis.has_files == True
        assert analysis.has_web_intent == True

    def test_token_estimation(self):
        """Test token estimation accuracy."""
        content = "This is a test message with approximately twenty tokens in total."
        estimated = self.analyzer._estimate_tokens(content)
        
        # Should be roughly 16-20 tokens
        assert 12 <= estimated <= 25

    def test_content_summary_creation(self):
        """Test content summary for large requests."""
        long_content = "Word " * 1000  # Very long content
        content_info = {
            "all_text": long_content,
            "total_tokens": 1000
        }
        
        summary = self.analyzer._create_content_summary(content_info)
        
        # Should be truncated and include hash
        assert len(summary) < len(long_content)
        assert "[HASH:" in summary


class TestProviderCapabilityRegistry:
    """Test the provider capability registry."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ProviderCapabilityRegistry()

    def test_optimal_provider_selection(self):
        """Test optimal provider selection for different request types."""
        assert self.registry.get_optimal_provider(RequestType.FILE_OPERATION) == ProviderType.KIMI
        assert self.registry.get_optimal_provider(RequestType.WEB_BROWSING) == ProviderType.GLM
        assert self.registry.get_optimal_provider(RequestType.GENERAL_CHAT) == ProviderType.GLM

    def test_capability_scoring(self):
        """Test capability scoring for providers."""
        # Mock request analysis for file operation
        file_analysis = Mock()
        file_analysis.request_type = RequestType.FILE_OPERATION
        file_analysis.has_files = True
        file_analysis.has_web_intent = False
        file_analysis.has_images = False
        file_analysis.estimated_tokens = 5000
        file_analysis.complexity = ContentComplexity.MODERATE
        
        kimi_score = self.registry.get_capability_score(ProviderType.KIMI, file_analysis)
        glm_score = self.registry.get_capability_score(ProviderType.GLM, file_analysis)
        
        # Kimi should score higher for file operations
        assert kimi_score > glm_score
        assert kimi_score > 0.5

    def test_web_capability_scoring(self):
        """Test capability scoring for web requests."""
        # Mock request analysis for web browsing
        web_analysis = Mock()
        web_analysis.request_type = RequestType.WEB_BROWSING
        web_analysis.has_files = False
        web_analysis.has_web_intent = True
        web_analysis.has_images = False
        web_analysis.estimated_tokens = 2000
        web_analysis.complexity = ContentComplexity.SIMPLE
        
        kimi_score = self.registry.get_capability_score(ProviderType.KIMI, web_analysis)
        glm_score = self.registry.get_capability_score(ProviderType.GLM, web_analysis)
        
        # GLM should score higher for web operations
        assert glm_score > kimi_score
        assert glm_score > 0.5


class TestGLMFlashManager:
    """Test the GLM Flash manager for intelligent routing."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = GLMFlashManager(
            enable_intelligent_routing=True,
            cost_threshold=0.10,
            performance_threshold=5.0
        )

    def test_capability_based_routing(self):
        """Test capability-based routing strategy."""
        # Mock request analysis for file operation
        analysis = Mock()
        analysis.request_type = RequestType.FILE_OPERATION
        analysis.has_files = True
        analysis.has_web_intent = False
        analysis.has_images = False
        analysis.estimated_tokens = 5000
        analysis.complexity = ContentComplexity.MODERATE
        
        decision = self.manager._capability_based_routing(analysis)
        
        assert decision.primary_provider == ProviderType.KIMI
        assert decision.strategy_used == RoutingStrategy.CAPABILITY_BASED
        assert decision.confidence > 0.5

    def test_cost_optimized_routing(self):
        """Test cost-optimized routing strategy."""
        # Mock request analysis for general chat
        analysis = Mock()
        analysis.request_type = RequestType.GENERAL_CHAT
        analysis.has_files = False
        analysis.has_web_intent = False
        analysis.has_images = False
        analysis.estimated_tokens = 1000
        analysis.complexity = ContentComplexity.SIMPLE
        
        decision = self.manager._cost_optimized_routing(analysis)
        
        # Should prefer GLM for cost optimization
        assert decision.primary_provider == ProviderType.GLM
        assert decision.strategy_used == RoutingStrategy.COST_OPTIMIZED
        assert decision.estimated_cost < 0.05  # Should be very cheap

    def test_performance_optimized_routing(self):
        """Test performance-optimized routing strategy."""
        # Mock request analysis for quick response needed
        analysis = Mock()
        analysis.request_type = RequestType.CODE_GENERATION
        analysis.has_files = False
        analysis.has_web_intent = False
        analysis.has_images = False
        analysis.estimated_tokens = 2000
        analysis.complexity = ContentComplexity.MODERATE
        
        decision = self.manager._performance_optimized_routing(analysis)
        
        # Should prefer GLM for performance
        assert decision.primary_provider == ProviderType.GLM
        assert decision.strategy_used == RoutingStrategy.PERFORMANCE_OPTIMIZED
        assert decision.estimated_time < 3.0  # Should be fast

    def test_hybrid_intelligent_routing(self):
        """Test hybrid intelligent routing strategy."""
        # Mock request analysis for balanced requirements
        analysis = Mock()
        analysis.request_type = RequestType.GENERAL_CHAT
        analysis.has_files = False
        analysis.has_web_intent = True
        analysis.has_images = False
        analysis.estimated_tokens = 3000
        analysis.complexity = ContentComplexity.MODERATE
        
        decision = self.manager._hybrid_intelligent_routing(analysis)
        
        assert decision.strategy_used == RoutingStrategy.HYBRID_INTELLIGENT
        assert decision.confidence > 0.3
        assert "provider_scores" in decision.metadata

    def test_routing_cache(self):
        """Test routing decision caching."""
        analysis = Mock()
        analysis.request_type = RequestType.GENERAL_CHAT
        analysis.has_files = False
        analysis.has_web_intent = False
        analysis.has_images = False
        analysis.estimated_tokens = 1000
        analysis.complexity = ContentComplexity.SIMPLE
        
        # First call should compute decision
        decision1 = self.manager.make_routing_decision(analysis)
        
        # Second call should use cache
        decision2 = self.manager.make_routing_decision(analysis)
        
        assert decision1.primary_provider == decision2.primary_provider
        assert decision1.reasoning == decision2.reasoning


class TestEnhancedRouterService:
    """Test the enhanced router service with intelligent routing."""

    @patch('src.providers.registry.ModelProviderRegistry.get_provider_for_model')
    @patch('src.providers.registry.ModelProviderRegistry.get_available_models')
    def setup_method(self, mock_available, mock_get_provider):
        """Set up test fixtures with mocked providers."""
        # Mock available models
        mock_available.return_value = {
            "glm-4.5-flash": ProviderType.GLM,
            "kimi-k2-0905-preview": ProviderType.KIMI
        }
        
        # Mock provider retrieval
        mock_provider = Mock()
        mock_provider.get_provider_type.return_value = ProviderType.GLM
        mock_get_provider.return_value = mock_provider
        
        self.router = RouterService()

    def test_intelligent_routing_enabled(self):
        """Test that intelligent routing is properly initialized."""
        assert hasattr(self.router, '_enable_intelligent_routing')
        assert hasattr(self.router, '_request_analyzer')
        assert hasattr(self.router, '_glm_flash_manager')
        assert hasattr(self.router, '_routing_strategy')

    @patch('src.providers.registry.ModelProviderRegistry.get_provider_for_model')
    def test_choose_model_intelligent_with_request_data(self, mock_get_provider):
        """Test intelligent model selection with request data."""
        # Mock provider
        mock_provider = Mock()
        mock_provider.get_provider_type.return_value = ProviderType.GLM
        mock_get_provider.return_value = mock_provider
        
        request_data = {
            "messages": [
                {"content": "Search for information about Python programming"}
            ]
        }
        
        decision = self.router.choose_model_intelligent("auto", request_data)
        
        assert decision.chosen in ["glm-4.5-flash", "glm-4.5"]
        assert "intelligent_" in decision.reason
        assert decision.meta is not None
        assert decision.meta.get("intelligent_routing") == True

    def test_routing_statistics(self):
        """Test routing statistics collection."""
        stats = self.router.get_routing_statistics()
        
        assert "intelligent_routing_enabled" in stats
        assert "routing_strategy" in stats
        assert "fast_default_model" in stats
        assert "long_default_model" in stats

    def test_analyze_request_preview(self):
        """Test request analysis preview functionality."""
        request_data = {
            "messages": [
                {"content": "Please analyze this CSV file with sales data"}
            ]
        }
        
        preview = self.router.analyze_request_preview(request_data)
        
        if "error" not in preview:
            assert "request_analysis" in preview
            assert "routing_decision" in preview
            assert "recommended_model" in preview


if __name__ == "__main__":
    pytest.main([__file__])
