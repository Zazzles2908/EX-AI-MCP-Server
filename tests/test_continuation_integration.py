"""
Integration tests for automatic continuation across all providers.

Tests Phase 2.1.3 implementation:
- Continuation manager functionality
- Provider integration (kimi_chat, async_kimi_chat, glm_chat)
- Token tracking across continuations
- Loop prevention and error handling
- Multi-turn continuation scenarios

Created: 2025-10-21
"""

import pytest
import logging
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

# Import continuation utilities
from src.utils.continuation_manager import (
    ContinuationManager,
    ContinuationSession,
    ContinuationResult,
    get_continuation_manager,
)

logger = logging.getLogger(__name__)


class TestContinuationSession:
    """Test ContinuationSession class."""
    
    def test_session_initialization(self):
        """Test session is initialized with correct defaults."""
        session = ContinuationSession(
            session_id="test-session",
            max_total_tokens=10000,
            max_attempts=3
        )
        
        assert session.session_id == "test-session"
        assert session.max_total_tokens == 10000
        assert session.max_attempts == 3
        assert session.cumulative_tokens == 0
        assert session.attempt_count == 0
        assert len(session.response_chunks) == 0
    
    def test_should_continue_max_attempts(self):
        """Test that continuation stops at max attempts."""
        session = ContinuationSession("test", max_attempts=2)
        session.attempt_count = 2
        
        should_continue, reason = session.should_continue("new response", 100)
        
        assert should_continue is False
        assert "Max attempts" in reason
    
    def test_should_continue_max_tokens(self):
        """Test that continuation stops at max tokens."""
        session = ContinuationSession("test", max_total_tokens=1000)
        session.cumulative_tokens = 900
        
        should_continue, reason = session.should_continue("new response", 200)
        
        assert should_continue is False
        assert "Max total tokens" in reason
    
    def test_should_continue_duplicate_response(self):
        """Test that continuation stops on duplicate responses."""
        session = ContinuationSession("test")
        session.response_chunks.append("same response")
        
        should_continue, reason = session.should_continue("same response", 100)
        
        assert should_continue is False
        assert "No progress" in reason or "duplicate" in reason.lower()
    
    def test_should_continue_empty_response(self):
        """Test that continuation stops on empty responses."""
        session = ContinuationSession("test")
        
        should_continue, reason = session.should_continue("", 100)
        
        assert should_continue is False
        assert "Empty response" in reason
    
    def test_should_continue_valid(self):
        """Test that continuation proceeds with valid response."""
        session = ContinuationSession("test")
        session.response_chunks.append("first response")
        
        should_continue, reason = session.should_continue("second response", 100)
        
        assert should_continue is True
        assert reason is None
    
    def test_add_response_chunk(self):
        """Test adding response chunks updates state correctly."""
        session = ContinuationSession("test")
        
        session.add_response_chunk("chunk 1", 100)
        assert session.attempt_count == 1
        assert session.cumulative_tokens == 100
        assert len(session.response_chunks) == 1
        
        session.add_response_chunk("chunk 2", 150)
        assert session.attempt_count == 2
        assert session.cumulative_tokens == 250
        assert len(session.response_chunks) == 2
    
    def test_merge_responses(self):
        """Test merging response chunks."""
        session = ContinuationSession("test")
        session.response_chunks = ["Hello ", "world", "!"]
        
        merged = session.merge_responses()
        
        assert merged == "Hello world!"
    
    def test_backoff_delays(self):
        """Test backoff delay progression."""
        session = ContinuationSession("test", backoff_delays=[0, 1.0, 2.0])
        
        assert session.get_backoff_delay() == 0
        session.attempt_count = 1
        assert session.get_backoff_delay() == 1.0
        session.attempt_count = 2
        assert session.get_backoff_delay() == 2.0
        session.attempt_count = 3
        assert session.get_backoff_delay() == 2.0  # Uses last delay


class TestContinuationManager:
    """Test ContinuationManager class."""
    
    def test_create_session(self):
        """Test creating a continuation session."""
        manager = ContinuationManager()
        
        session = manager.create_session("test-id", max_total_tokens=5000, max_attempts=2)
        
        assert session.session_id == "test-id"
        assert session.max_total_tokens == 5000
        assert session.max_attempts == 2
        assert "test-id" in manager.active_sessions
    
    def test_get_session(self):
        """Test retrieving an existing session."""
        manager = ContinuationManager()
        session = manager.create_session("test-id")
        
        retrieved = manager.get_session("test-id")
        
        assert retrieved is session
    
    def test_cleanup_session(self):
        """Test cleaning up a session."""
        manager = ContinuationManager()
        manager.create_session("test-id")
        
        manager.cleanup_session("test-id")
        
        assert "test-id" not in manager.active_sessions
    
    def test_generate_continuation_prompt(self):
        """Test continuation prompt generation."""
        manager = ContinuationManager()
        
        prompt = manager.generate_continuation_prompt(
            original_request="Write a long essay about AI",
            last_response_chunk="...and this is where the discussion ends"
        )
        
        assert "continue" in prompt.lower()
        assert "Write a long essay" in prompt
        assert "where the discussion ends" in prompt
    
    def test_extract_response_content_choices_format(self):
        """Test extracting content from choices format."""
        manager = ContinuationManager()
        response = {
            'choices': [{
                'message': {'content': 'Test content'}
            }]
        }
        
        content = manager.extract_response_content(response)
        
        assert content == 'Test content'
    
    def test_extract_response_content_direct_format(self):
        """Test extracting content from direct format."""
        manager = ContinuationManager()
        response = {'content': 'Direct content'}
        
        content = manager.extract_response_content(response)
        
        assert content == 'Direct content'
    
    def test_extract_token_usage(self):
        """Test extracting token usage from response."""
        manager = ContinuationManager()
        response = {
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 200,
                'total_tokens': 300
            }
        }
        
        tokens = manager.extract_token_usage(response)
        
        assert tokens == 300
    
    def test_extract_token_usage_fallback(self):
        """Test token usage extraction with fallback calculation."""
        manager = ContinuationManager()
        response = {
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 200
            }
        }
        
        tokens = manager.extract_token_usage(response)
        
        assert tokens == 300  # Sum of prompt + completion


class TestContinuationResult:
    """Test ContinuationResult class."""
    
    def test_result_initialization(self):
        """Test result is initialized with correct defaults."""
        result = ContinuationResult()
        
        assert result.complete_response == ""
        assert result.is_complete is False
        assert result.attempts_made == 0
        assert result.total_tokens_used == 0
        assert result.error_message is None
        assert result.was_truncated is False
        assert len(result.response_chunks) == 0
    
    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = ContinuationResult()
        result.complete_response = "Test response"
        result.is_complete = True
        result.attempts_made = 2
        result.total_tokens_used = 500
        
        result_dict = result.to_dict()
        
        assert result_dict['is_complete'] is True
        assert result_dict['attempts_made'] == 2
        assert result_dict['total_tokens_used'] == 500
        assert result_dict['complete_response_length'] == len("Test response")


class TestProviderIntegration:
    """Test provider integration with continuation."""
    
    def test_kimi_chat_continuation_wrapper_exists(self):
        """Test that kimi_chat has continuation wrapper."""
        from src.providers.kimi_chat import chat_completions_create_with_continuation
        
        assert callable(chat_completions_create_with_continuation)
    
    def test_async_kimi_chat_continuation_wrapper_exists(self):
        """Test that async_kimi_chat has continuation wrapper."""
        from src.providers.async_kimi_chat import chat_completions_create_async_with_continuation
        
        assert callable(chat_completions_create_async_with_continuation)
    
    def test_glm_chat_continuation_wrapper_exists(self):
        """Test that glm_chat has continuation wrapper."""
        from src.providers.glm_chat import chat_completions_create_with_continuation
        
        assert callable(chat_completions_create_with_continuation)


class TestGlobalManager:
    """Test global continuation manager."""
    
    def test_get_continuation_manager_singleton(self):
        """Test that get_continuation_manager returns singleton."""
        manager1 = get_continuation_manager()
        manager2 = get_continuation_manager()
        
        assert manager1 is manager2


class TestErrorHandling:
    """Test error handling in continuation logic."""
    
    def test_continuation_with_invalid_response(self):
        """Test continuation handles invalid responses gracefully."""
        manager = ContinuationManager()
        
        # Invalid response structure
        content = manager.extract_response_content({'invalid': 'structure'})
        
        assert content == ""  # Should return empty string, not crash
    
    def test_continuation_with_missing_usage(self):
        """Test continuation handles missing usage data."""
        manager = ContinuationManager()
        
        tokens = manager.extract_token_usage({})
        
        assert tokens == 0  # Should return 0, not crash

