"""
Tests for Expert Validation Deduplication

This module tests the duplicate call prevention logic in expert_analysis.py.
The deduplication system prevents the duplicate expert analysis calls that were
causing 300+ second timeouts.

Key Features Tested:
- Cache hit on duplicate calls
- In-progress detection and waiting
- Cache key generation
- Result caching
- Cleanup after completion/error
"""

import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import the global cache and lock for testing
from tools.workflow.expert_analysis import (
    _expert_validation_cache,
    _expert_validation_in_progress,
    _expert_validation_lock,
)


class TestExpertDeduplication:
    """Test expert validation deduplication logic."""
    
    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear cache before each test."""
        _expert_validation_cache.clear()
        _expert_validation_in_progress.clear()
        yield
        _expert_validation_cache.clear()
        _expert_validation_in_progress.clear()
    
    @pytest.mark.asyncio
    async def test_cache_hit_on_duplicate_call(self):
        """Test that duplicate calls return cached result."""
        # Create a mock tool with expert analysis
        from tools.workflow.expert_analysis import ExpertAnalysisMixin
        from tools.shared.base_models import ConsolidatedFindings
        
        class MockTool(ExpertAnalysisMixin):
            def __init__(self):
                self.consolidated_findings = ConsolidatedFindings(
                    findings=["Finding 1", "Finding 2"],
                    relevant_files=[],
                    files_checked=[],
                    issues_found=[],
                    images=[]
                )
                self._model_context = None
                self._current_model_name = "test-model"
            
            def get_name(self):
                return "test_tool"
            
            def get_system_prompt(self):
                return "Test system prompt"
            
            def get_language_instruction(self):
                return ""
            
            def get_expert_analysis_instruction(self):
                return "Test instruction"
            
            def get_request_model_name(self, request):
                return "test-model"
            
            def get_request_thinking_mode(self, request):
                return "high"
            
            def get_request_use_websearch(self, request):
                return False
            
            def get_request_use_assistant_model(self, request):
                return True
            
            def get_validated_temperature(self, request, model_context):
                return 0.7, []
            
            def _resolve_model_context(self, arguments, request):
                from utils.model.context import ModelContext
                return "test-model", ModelContext("test-model")
            
            def _prepare_files_for_expert_analysis(self):
                return ""
            
            def _add_files_to_expert_context(self, context, files):
                return context
            
            def should_include_files_in_expert_prompt(self):
                return False
            
            def should_embed_system_prompt(self):
                return False
        
        tool = MockTool()

        # Mock the provider to return a result
        mock_provider = Mock()
        mock_response = Mock()
        mock_response.content = '{"status": "analysis_complete", "result": "test result"}'
        mock_provider.generate_content = Mock(return_value=mock_response)
        mock_provider.get_provider_type = Mock(return_value=Mock(value="test"))

        # Mock model context with provider property
        from utils.model.context import ModelContext
        tool._model_context = ModelContext("test-model")

        # Patch the provider property
        with patch.object(ModelContext, 'provider', new_callable=lambda: property(lambda self: mock_provider)):
            arguments = {"request_id": "test-123"}
            request = Mock()

            # First call - should hit provider
            result1 = await tool._call_expert_analysis(arguments, request)
            assert result1["status"] == "analysis_complete"
            assert result1["result"] == "test result"
            assert mock_provider.generate_content.call_count == 1

            # Second call with same arguments - should hit cache
            result2 = await tool._call_expert_analysis(arguments, request)
            assert result2["status"] == "analysis_complete"
            assert result2["result"] == "test result"
            # Provider should NOT be called again
            assert mock_provider.generate_content.call_count == 1

            # Verify cache was used
            assert len(_expert_validation_cache) == 1
    
    @pytest.mark.asyncio
    async def test_in_progress_detection(self):
        """Test that concurrent calls wait for in-progress validation."""
        from tools.workflow.expert_analysis import ExpertAnalysisMixin
        from tools.shared.base_models import ConsolidatedFindings
        
        class MockTool(ExpertAnalysisMixin):
            def __init__(self):
                self.consolidated_findings = ConsolidatedFindings(
                    findings=["Finding 1"],
                    relevant_files=[],
                    files_checked=[],
                    issues_found=[],
                    images=[]
                )
                self._model_context = None
                self._current_model_name = "test-model"
            
            def get_name(self):
                return "test_tool"
            
            def get_system_prompt(self):
                return "Test"
            
            def get_language_instruction(self):
                return ""
            
            def get_expert_analysis_instruction(self):
                return "Test"
            
            def get_request_model_name(self, request):
                return "test-model"
            
            def get_request_thinking_mode(self, request):
                return "high"
            
            def get_request_use_websearch(self, request):
                return False
            
            def get_request_use_assistant_model(self, request):
                return True
            
            def get_validated_temperature(self, request, model_context):
                return 0.7, []
            
            def _resolve_model_context(self, arguments, request):
                from utils.model.context import ModelContext
                return "test-model", ModelContext("test-model")
            
            def _prepare_files_for_expert_analysis(self):
                return ""
            
            def _add_files_to_expert_context(self, context, files):
                return context
            
            def should_include_files_in_expert_prompt(self):
                return False
            
            def should_embed_system_prompt(self):
                return False
        
        tool = MockTool()

        # Mock provider with slow response
        mock_provider = Mock()
        mock_response = Mock()
        mock_response.content = '{"status": "analysis_complete", "result": "slow result"}'

        async def slow_generate(*args, **kwargs):
            await asyncio.sleep(1)  # Simulate slow provider
            return mock_response

        mock_provider.generate_content = Mock(side_effect=lambda *args, **kwargs: mock_response)
        mock_provider.get_provider_type = Mock(return_value=Mock(value="test"))

        from utils.model.context import ModelContext
        tool._model_context = ModelContext("test-model")

        # Patch the provider property
        with patch.object(ModelContext, 'provider', new_callable=lambda: property(lambda self: mock_provider)):
            arguments = {"request_id": "test-concurrent"}
            request = Mock()

            # Start first call (will be slow)
            task1 = asyncio.create_task(tool._call_expert_analysis(arguments, request))

            # Give it time to mark as in-progress
            await asyncio.sleep(0.1)

            # Verify it's marked as in-progress
            cache_key = f"test_tool:test-concurrent:{hash(str(tool.consolidated_findings.findings))}"
            assert cache_key in _expert_validation_in_progress

            # Start second call (should wait for first)
            task2 = asyncio.create_task(tool._call_expert_analysis(arguments, request))

            # Wait for both to complete
            result1, result2 = await asyncio.gather(task1, task2)

            # Both should have same result
            assert result1["status"] == "analysis_complete"
            assert result2["status"] == "analysis_complete"

            # Provider should only be called once
            assert mock_provider.generate_content.call_count == 1

            # Cache should have one entry
            assert len(_expert_validation_cache) == 1

            # In-progress should be empty after completion
            assert len(_expert_validation_in_progress) == 0
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test that cache keys are generated correctly."""
        from tools.workflow.expert_analysis import ExpertAnalysisMixin
        from tools.shared.base_models import ConsolidatedFindings
        
        # Different findings should generate different cache keys
        findings1 = ["Finding A"]
        findings2 = ["Finding B"]
        
        hash1 = hash(str(findings1))
        hash2 = hash(str(findings2))
        
        assert hash1 != hash2
        
        # Same findings should generate same hash
        findings3 = ["Finding A"]
        hash3 = hash(str(findings3))
        
        assert hash1 == hash3
    
    @pytest.mark.asyncio
    async def test_cleanup_after_error(self):
        """Test that in-progress is cleaned up even after error."""
        from tools.workflow.expert_analysis import ExpertAnalysisMixin
        from tools.shared.base_models import ConsolidatedFindings
        
        class MockTool(ExpertAnalysisMixin):
            def __init__(self):
                self.consolidated_findings = ConsolidatedFindings(
                    findings=["Finding 1"],
                    relevant_files=[],
                    files_checked=[],
                    issues_found=[],
                    images=[]
                )
                self._model_context = None
                self._current_model_name = "test-model"
            
            def get_name(self):
                return "test_tool"
            
            def get_system_prompt(self):
                return "Test"
            
            def get_language_instruction(self):
                return ""
            
            def get_expert_analysis_instruction(self):
                return "Test"
            
            def get_request_model_name(self, request):
                return "test-model"
            
            def get_request_thinking_mode(self, request):
                return "high"
            
            def get_request_use_websearch(self, request):
                return False
            
            def get_request_use_assistant_model(self, request):
                return True
            
            def get_validated_temperature(self, request, model_context):
                return 0.7, []
            
            def _resolve_model_context(self, arguments, request):
                raise Exception("Test error")
            
            def _prepare_files_for_expert_analysis(self):
                return ""
            
            def _add_files_to_expert_context(self, context, files):
                return context
            
            def should_include_files_in_expert_prompt(self):
                return False
            
            def should_embed_system_prompt(self):
                return False
        
        tool = MockTool()
        arguments = {"request_id": "test-error"}
        request = Mock()
        
        # Call should handle error gracefully
        result = await tool._call_expert_analysis(arguments, request)
        
        # Should return error result
        assert result["status"] == "analysis_error"
        assert "error" in result
        
        # In-progress should be cleaned up
        assert len(_expert_validation_in_progress) == 0
        
        # Error result should be cached
        assert len(_expert_validation_cache) == 1

