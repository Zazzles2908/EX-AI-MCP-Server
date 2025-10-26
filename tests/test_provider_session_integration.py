"""
Tests for Provider Session Integration

Verifies that provider classes actually use session-managed wrapper functions.

Created: 2025-10-21
Phase: 2.2.4 - MCP Server Integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestKimiProviderSessionIntegration:
    """Tests for Kimi provider session integration."""
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_session')
    def test_kimi_provider_uses_session_wrapper(self, mock_session_wrapper):
        """Test that KimiModelProvider.chat_completions_create() calls session wrapper."""
        from src.providers.kimi import KimiModelProvider
        
        # Mock the session wrapper to return a test response
        mock_session_wrapper.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response',
            'metadata': {
                'session': {
                    'session_id': 'test_session',
                    'request_id': 'test_request',
                    'duration_seconds': 0.5
                }
            }
        }
        
        # Create provider instance
        provider = KimiModelProvider(api_key='test_key')
        
        # Call chat_completions_create
        result = provider.chat_completions_create(
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            temperature=0.6
        )
        
        # Verify session wrapper was called
        mock_session_wrapper.assert_called_once()
        call_kwargs = mock_session_wrapper.call_args[1]
        assert call_kwargs['model'] == 'moonshot-v1-8k'
        assert call_kwargs['temperature'] == 0.6
        
        # Verify session metadata is in response
        assert 'metadata' in result
        assert 'session' in result['metadata']
        assert result['metadata']['session']['session_id'] == 'test_session'
    
    @patch('src.providers.kimi_chat.chat_completions_create_with_session')
    def test_kimi_provider_passes_all_parameters(self, mock_session_wrapper):
        """Test that all parameters are passed through to session wrapper."""
        from src.providers.kimi import KimiModelProvider
        
        mock_session_wrapper.return_value = {'provider': 'kimi', 'content': 'test'}
        
        provider = KimiModelProvider(api_key='test_key')
        
        # Call with various parameters
        provider.chat_completions_create(
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            tools=[{'type': 'function', 'function': {'name': 'test'}}],
            tool_choice='auto',
            temperature=0.8,
            max_output_tokens=1000
        )
        
        # Verify all parameters were passed
        call_kwargs = mock_session_wrapper.call_args[1]
        assert call_kwargs['model'] == 'moonshot-v1-8k'
        assert call_kwargs['tools'] is not None
        assert call_kwargs['tool_choice'] == 'auto'
        assert call_kwargs['temperature'] == 0.8
        assert call_kwargs['max_output_tokens'] == 1000


class TestGLMProviderSessionIntegration:
    """Tests for GLM provider session integration."""
    
    @patch('src.providers.glm_chat.chat_completions_create_messages_with_session')
    def test_glm_provider_uses_session_wrapper(self, mock_session_wrapper):
        """Test that GLMModelProvider.chat_completions_create() calls session wrapper."""
        from src.providers.glm import GLMModelProvider
        
        # Mock the session wrapper to return a test response
        mock_session_wrapper.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response',
            'metadata': {
                'session': {
                    'session_id': 'test_session',
                    'request_id': 'test_request',
                    'duration_seconds': 0.5
                }
            }
        }
        
        # Create provider instance
        provider = GLMModelProvider(api_key='test_key')
        
        # Call chat_completions_create
        result = provider.chat_completions_create(
            model='glm-4.5-flash',
            messages=[{'role': 'user', 'content': 'Hello'}],
            temperature=0.3
        )
        
        # Verify session wrapper was called
        mock_session_wrapper.assert_called_once()
        call_kwargs = mock_session_wrapper.call_args[1]
        assert call_kwargs['model'] == 'glm-4.5-flash'
        assert call_kwargs['temperature'] == 0.3
        
        # Verify session metadata is in response
        assert 'metadata' in result
        assert 'session' in result['metadata']
        assert result['metadata']['session']['session_id'] == 'test_session'
    
    @patch('src.providers.glm_chat.chat_completions_create_messages_with_session')
    def test_glm_provider_passes_all_parameters(self, mock_session_wrapper):
        """Test that all parameters are passed through to session wrapper."""
        from src.providers.glm import GLMModelProvider
        
        mock_session_wrapper.return_value = {'provider': 'glm', 'content': 'test'}
        
        provider = GLMModelProvider(api_key='test_key')
        
        # Call with various parameters
        provider.chat_completions_create(
            model='glm-4.6',
            messages=[{'role': 'user', 'content': 'Hello'}],
            tools=[{'type': 'function', 'function': {'name': 'test'}}],
            tool_choice='auto',
            temperature=0.5,
            thinking_mode='enabled'
        )
        
        # Verify all parameters were passed
        call_kwargs = mock_session_wrapper.call_args[1]
        assert call_kwargs['model'] == 'glm-4.6'
        assert call_kwargs['tools'] is not None
        assert call_kwargs['tool_choice'] == 'auto'
        assert call_kwargs['temperature'] == 0.5
        assert 'thinking_mode' in call_kwargs


class TestSessionIntegrationEndToEnd:
    """End-to-end tests for session integration."""
    
    @patch('src.utils.concurrent_session_manager.ConcurrentSessionManager.execute_with_session')
    @patch('src.providers.kimi_chat.chat_completions_create_with_continuation')
    def test_kimi_end_to_end_session_flow(self, mock_continuation, mock_execute):
        """Test complete flow from provider to session manager for Kimi."""
        from src.providers.kimi import KimiModelProvider
        
        # Mock continuation to return test response
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test response'
        }
        
        # Mock execute_with_session to add session context
        def mock_exec(provider, model, func, **kwargs):
            result = func()
            result['metadata'] = result.get('metadata', {})
            result['metadata']['session'] = {
                'session_id': 'test_session',
                'request_id': kwargs.get('request_id', 'auto_generated'),
                'duration_seconds': 0.5
            }
            return result
        
        mock_execute.side_effect = mock_exec
        
        # Create provider and call
        provider = KimiModelProvider(api_key='test_key')
        result = provider.chat_completions_create(
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        
        # Verify session manager was called
        mock_execute.assert_called_once()
        assert mock_execute.call_args[1]['provider'] == 'kimi'
        assert mock_execute.call_args[1]['model'] == 'moonshot-v1-8k'
        
        # Verify session context in result
        assert 'session' in result['metadata']
    
    @patch('src.utils.concurrent_session_manager.ConcurrentSessionManager.execute_with_session')
    @patch('src.providers.glm_chat.chat_completions_create')
    def test_glm_end_to_end_session_flow(self, mock_chat, mock_execute):
        """Test complete flow from provider to session manager for GLM."""
        from src.providers.glm import GLMModelProvider
        
        # Mock chat to return test response
        mock_chat.return_value = {
            'provider': 'glm',
            'model': 'glm-4.5-flash',
            'content': 'Test response'
        }
        
        # Mock execute_with_session to add session context
        def mock_exec(provider, model, func, **kwargs):
            result = func()
            result['metadata'] = result.get('metadata', {})
            result['metadata']['session'] = {
                'session_id': 'test_session',
                'request_id': kwargs.get('request_id', 'auto_generated'),
                'duration_seconds': 0.5
            }
            return result
        
        mock_execute.side_effect = mock_exec
        
        # Create provider and call
        provider = GLMModelProvider(api_key='test_key')
        result = provider.chat_completions_create(
            model='glm-4.5-flash',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        
        # Verify session manager was called
        mock_execute.assert_called_once()
        assert mock_execute.call_args[1]['provider'] == 'glm'
        assert mock_execute.call_args[1]['model'] == 'glm-4.5-flash'
        
        # Verify session context in result
        assert 'session' in result['metadata']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

