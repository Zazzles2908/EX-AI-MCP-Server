"""
Tests for GLM Chat Session Integration

Tests the integration of concurrent session manager with glm_chat.py provider.

Created: 2025-10-21
Phase: 2.2.3 - Provider Integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.providers.glm_chat import chat_completions_create_with_session


class TestGLMSessionIntegration:
    """Tests for GLM chat session integration."""
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_basic(self, mock_continuation):
        """Test basic session wrapper functionality."""
        # Mock the continuation function
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'usage': {'total_tokens': 100},
            'metadata': {}
        }
        
        # Call session wrapper
        result = chat_completions_create_with_session(
            'Hello, how are you?',
            model='glm-4.5-flash'
        )
        
        # Verify result structure
        assert result['provider'] == 'glm'
        assert result['model'] == 'glm-4.5-flash'
        assert result['content'] == 'Test response'
        
        # Verify session metadata was added
        assert 'metadata' in result
        assert 'session' in result['metadata']
        assert 'session_id' in result['metadata']['session']
        assert 'request_id' in result['metadata']['session']
        assert 'duration_seconds' in result['metadata']['session']
        
        # Verify continuation function was called
        mock_continuation.assert_called_once()
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_with_custom_request_id(self, mock_continuation):
        """Test session wrapper with custom request ID."""
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {}
        }
        
        custom_request_id = "custom_req_456"
        
        result = chat_completions_create_with_session(
            'Hello',
            model='glm-4.5-flash',
            request_id=custom_request_id
        )
        
        # Verify custom request ID was used
        assert result['metadata']['session']['request_id'] == custom_request_id
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_error_handling(self, mock_continuation):
        """Test session wrapper error handling."""
        # Mock continuation to raise error
        mock_continuation.side_effect = ValueError("Test error")
        
        # Verify error is propagated
        with pytest.raises(ValueError, match="Test error"):
            chat_completions_create_with_session(
                'Hello',
                model='glm-4.5-flash'
            )
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_with_timeout(self, mock_continuation):
        """Test session wrapper with custom timeout."""
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {}
        }
        
        result = chat_completions_create_with_session(
            'Hello',
            model='glm-4.5-flash',
            timeout_seconds=60.0
        )
        
        # Verify result was returned
        assert result['content'] == 'Test response'
        assert 'session' in result['metadata']
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_preserves_continuation_params(self, mock_continuation):
        """Test that session wrapper preserves continuation parameters."""
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {}
        }
        
        result = chat_completions_create_with_session(
            'Hello',
            model='glm-4.5-flash',
            enable_continuation=True,
            max_continuation_attempts=5,
            max_total_tokens=50000
        )
        
        # Verify continuation function was called with correct params
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['enable_continuation'] is True
        assert call_kwargs['max_continuation_attempts'] == 5
        assert call_kwargs['max_total_tokens'] == 50000
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_preserves_websearch_param(self, mock_continuation):
        """Test that session wrapper preserves websearch parameter."""
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {}
        }
        
        result = chat_completions_create_with_session(
            'Hello',
            model='glm-4.5-flash',
            use_websearch=True
        )
        
        # Verify continuation function was called with websearch param
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['use_websearch'] is True
    
    @patch('src.providers.glm_chat.chat_completions_create_with_continuation')
    def test_session_wrapper_with_system_prompt(self, mock_continuation):
        """Test session wrapper with system prompt."""
        mock_continuation.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {}
        }
        
        result = chat_completions_create_with_session(
            'Hello',
            system_prompt='You are a helpful assistant',
            model='glm-4.5-flash'
        )
        
        # Verify continuation function was called with system prompt
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['system_prompt'] == 'You are a helpful assistant'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

