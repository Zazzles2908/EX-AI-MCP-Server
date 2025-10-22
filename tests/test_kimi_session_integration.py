"""
Tests for Kimi Chat Session Integration

Tests the integration of concurrent session manager with kimi_chat.py provider.

Created: 2025-10-21
Phase: 2.2.3 - Provider Integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.providers.kimi_chat import chat_completions_create_with_session


class TestKimiSessionIntegration:
    """Tests for Kimi chat session integration."""
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_basic(self, mock_continuation):
        """Test basic session wrapper functionality."""
        # Mock the continuation function
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'usage': {'total_tokens': 100},
            'metadata': {}
        }
        
        # Create mock client
        mock_client = Mock()
        
        # Call session wrapper
        result = chat_completions_create_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        
        # Verify result structure
        assert result['provider'] == 'kimi'
        assert result['model'] == 'moonshot-v1-8k'
        assert result['content'] == 'Test response'
        
        # Verify session metadata was added
        assert 'metadata' in result
        assert 'session' in result['metadata']
        assert 'session_id' in result['metadata']['session']
        assert 'request_id' in result['metadata']['session']
        assert 'duration_seconds' in result['metadata']['session']
        
        # Verify continuation function was called
        mock_continuation.assert_called_once()
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_with_custom_request_id(self, mock_continuation):
        """Test session wrapper with custom request ID."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'metadata': {}
        }
        
        mock_client = Mock()
        custom_request_id = "custom_req_123"
        
        result = chat_completions_create_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            request_id=custom_request_id
        )
        
        # Verify custom request ID was used
        assert result['metadata']['session']['request_id'] == custom_request_id
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_error_handling(self, mock_continuation):
        """Test session wrapper error handling."""
        # Mock continuation to raise error
        mock_continuation.side_effect = ValueError("Test error")
        
        mock_client = Mock()
        
        # Verify error is propagated
        with pytest.raises(ValueError, match="Test error"):
            chat_completions_create_with_session(
                mock_client,
                model='moonshot-v1-8k',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_with_timeout(self, mock_continuation):
        """Test session wrapper with custom timeout."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = chat_completions_create_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            timeout_seconds=60.0
        )
        
        # Verify result was returned
        assert result['content'] == 'Test response'
        assert 'session' in result['metadata']
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_preserves_continuation_params(self, mock_continuation):
        """Test that session wrapper preserves continuation parameters."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = chat_completions_create_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            enable_continuation=True,
            max_continuation_attempts=5,
            max_total_tokens=50000
        )
        
        # Verify continuation function was called with correct params
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['enable_continuation'] is True
        assert call_kwargs['max_continuation_attempts'] == 5
        assert call_kwargs['max_total_tokens'] == 50000
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_preserves_cache_params(self, mock_continuation):
        """Test that session wrapper preserves cache parameters."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = chat_completions_create_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            cache_id='test_cache_123',
            reset_cache_ttl=True
        )
        
        # Verify continuation function was called with cache params
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['cache_id'] == 'test_cache_123'
        assert call_kwargs['reset_cache_ttl'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

