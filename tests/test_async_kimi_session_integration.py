"""
Tests for Async Kimi Chat Session Integration

Tests the integration of async concurrent session manager with async_kimi_chat.py provider.

Created: 2025-10-21
Phase: 2.2.3 - Provider Integration (Async)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from src.providers.async_kimi_chat import chat_completions_create_async_with_session


@pytest.mark.asyncio
class TestAsyncKimiSessionIntegration:
    """Tests for async Kimi chat session integration."""
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_basic(self, mock_continuation):
        """Test basic async session wrapper functionality."""
        # Mock the async continuation function
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test async response',
            'usage': {'total_tokens': 100},
            'metadata': {}
        }
        
        # Create mock async client
        mock_client = Mock()
        
        # Call async session wrapper
        result = await chat_completions_create_async_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        
        # Verify result structure
        assert result['provider'] == 'kimi'
        assert result['model'] == 'moonshot-v1-8k'
        assert result['content'] == 'Test async response'
        
        # Verify session metadata was added
        assert 'metadata' in result
        assert 'session' in result['metadata']
        assert 'session_id' in result['metadata']['session']
        assert 'request_id' in result['metadata']['session']
        assert 'duration_seconds' in result['metadata']['session']
        
        # Verify continuation function was called
        mock_continuation.assert_called_once()
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_with_custom_request_id(self, mock_continuation):
        """Test async session wrapper with custom request ID."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test async response',
            'metadata': {}
        }
        
        mock_client = Mock()
        custom_request_id = "async_req_123"
        
        result = await chat_completions_create_async_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            request_id=custom_request_id
        )
        
        # Verify custom request ID was used
        assert result['metadata']['session']['request_id'] == custom_request_id
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_error_handling(self, mock_continuation):
        """Test async session wrapper error handling."""
        # Mock continuation to raise error
        mock_continuation.side_effect = ValueError("Test async error")
        
        mock_client = Mock()
        
        # Verify error is propagated
        with pytest.raises(ValueError, match="Test async error"):
            await chat_completions_create_async_with_session(
                mock_client,
                model='moonshot-v1-8k',
                messages=[{'role': 'user', 'content': 'Hello'}]
            )
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_with_timeout(self, mock_continuation):
        """Test async session wrapper with custom timeout."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test async response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = await chat_completions_create_async_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            timeout_seconds=60.0
        )
        
        # Verify result was returned
        assert result['content'] == 'Test async response'
        assert 'session' in result['metadata']
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_preserves_continuation_params(self, mock_continuation):
        """Test that async session wrapper preserves continuation parameters."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test async response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = await chat_completions_create_async_with_session(
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
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_async_session_wrapper_preserves_cache_params(self, mock_continuation):
        """Test that async session wrapper preserves cache parameters."""
        mock_continuation.return_value = {
            'provider': 'kimi',
            'model': 'moonshot-v1-8k',
            'content': 'Test async response',
            'metadata': {}
        }
        
        mock_client = Mock()
        
        result = await chat_completions_create_async_with_session(
            mock_client,
            model='moonshot-v1-8k',
            messages=[{'role': 'user', 'content': 'Hello'}],
            cache_id='async_cache_123',
            reset_cache_ttl=True
        )
        
        # Verify continuation function was called with cache params
        call_kwargs = mock_continuation.call_args[1]
        assert call_kwargs['cache_id'] == 'async_cache_123'
        assert call_kwargs['reset_cache_ttl'] is True
    
    @patch('src.providers.async_kimi_chat.chat_completions_create_async_with_continuation')
    async def test_concurrent_async_sessions(self, mock_continuation):
        """Test multiple concurrent async sessions."""
        import asyncio
        
        # Mock different responses for each call
        call_count = 0
        async def mock_response(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate async work
            return {
                'provider': 'kimi',
                'model': 'moonshot-v1-8k',
                'content': f'Response {call_count}',
                'metadata': {}
            }
        
        mock_continuation.side_effect = mock_response
        mock_client = Mock()
        
        # Create 5 concurrent async requests
        tasks = [
            chat_completions_create_async_with_session(
                mock_client,
                model='moonshot-v1-8k',
                messages=[{'role': 'user', 'content': f'Hello {i}'}]
            )
            for i in range(5)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all completed
        assert len(results) == 5
        for result in results:
            assert 'session' in result['metadata']
            assert result['content'].startswith('Response')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

