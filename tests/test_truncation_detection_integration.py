"""
Integration tests for truncation detection across all providers.

Tests Phase 2.1.2 implementation:
- Truncation detection in kimi_chat.py
- Truncation detection in async_kimi_chat.py
- Truncation detection in glm_chat.py
- Supabase logging (sync and async)
- Error handling and graceful degradation

Created: 2025-10-21
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import truncation detection utilities
from src.utils.truncation_detector import (
    check_truncation,
    should_log_truncation,
    format_truncation_event,
    log_truncation_to_supabase_sync,
    log_truncation_to_supabase,
)

logger = logging.getLogger(__name__)


class TestTruncationDetection:
    """Test truncation detection utility functions."""
    
    def test_check_truncation_with_length_finish_reason(self):
        """Test that finish_reason='length' is detected as truncation."""
        response = {
            'choices': [{
                'finish_reason': 'length',
                'message': {'content': 'test'}
            }],
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 500,
                'total_tokens': 600
            }
        }
        
        result = check_truncation(response, 'kimi-k2-0905-preview')
        
        assert result['is_truncated'] is True
        assert result['finish_reason'] == 'length'
        assert result['model'] == 'kimi-k2-0905-preview'
        assert result['usage']['prompt_tokens'] == 100
        assert result['usage']['completion_tokens'] == 500
    
    def test_check_truncation_with_stop_finish_reason(self):
        """Test that finish_reason='stop' is NOT detected as truncation."""
        response = {
            'choices': [{
                'finish_reason': 'stop',
                'message': {'content': 'test'}
            }]
        }
        
        result = check_truncation(response, 'glm-4.6')
        
        assert result['is_truncated'] is False
        assert result['finish_reason'] == 'stop'
    
    def test_should_log_truncation_true(self):
        """Test that truncated responses should be logged."""
        truncation_info = {
            'is_truncated': True,
            'finish_reason': 'length',
            'model': 'test-model'
        }
        
        assert should_log_truncation(truncation_info) is True
    
    def test_should_log_truncation_false_not_truncated(self):
        """Test that non-truncated responses should NOT be logged."""
        truncation_info = {
            'is_truncated': False,
            'finish_reason': 'stop'
        }
        
        assert should_log_truncation(truncation_info) is False
    
    def test_should_log_truncation_false_with_error(self):
        """Test that responses with detection errors should NOT be logged."""
        truncation_info = {
            'is_truncated': True,
            'error': 'Some error occurred'
        }
        
        assert should_log_truncation(truncation_info) is False
    
    def test_format_truncation_event(self):
        """Test formatting truncation event for Supabase."""
        truncation_info = {
            'timestamp': '2025-10-21T10:00:00Z',
            'model': 'kimi-k2-0905-preview',
            'finish_reason': 'length',
            'is_truncated': True,
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 500,
                'total_tokens': 600
            }
        }
        
        event = format_truncation_event(
            truncation_info,
            tool_name='debug',
            conversation_id='test-conv-123',
            additional_context={'test': 'data'}
        )
        
        assert event['model'] == 'kimi-k2-0905-preview'
        assert event['finish_reason'] == 'length'
        assert event['is_truncated'] is True
        assert event['tool_name'] == 'debug'
        assert event['conversation_id'] == 'test-conv-123'
        assert event['prompt_tokens'] == 100
        assert event['completion_tokens'] == 500
        assert event['total_tokens'] == 600
        assert event['context'] == {'test': 'data'}


class TestSupabaseLogging:
    """Test Supabase logging functions."""
    
    def test_sync_logging_success(self):
        """Test successful synchronous Supabase logging."""
        # Mock Supabase client
        mock_client = Mock()
        mock_result = Mock()
        mock_result.data = [{'id': 'test-id'}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_result
        
        event = {
            'model': 'test-model',
            'finish_reason': 'length',
            'is_truncated': True
        }
        
        result = log_truncation_to_supabase_sync(event, supabase_client=mock_client)
        
        assert result is True
        mock_client.table.assert_called_once_with('truncation_events')
    
    def test_sync_logging_failure_graceful(self):
        """Test that sync logging failures are handled gracefully."""
        # Mock Supabase client that raises exception
        mock_client = Mock()
        mock_client.table.side_effect = Exception("Supabase unavailable")
        
        event = {'model': 'test-model'}
        
        # Should not raise exception
        result = log_truncation_to_supabase_sync(event, supabase_client=mock_client)
        
        assert result is False
    
    def test_sync_logging_no_client_graceful(self):
        """Test that missing Supabase client is handled gracefully."""
        event = {'model': 'test-model'}

        # Call without client - should handle gracefully
        # This tests the ImportError path when get_supabase_client fails
        result = log_truncation_to_supabase_sync(event, supabase_client=None)

        # Should return False (either due to import error or connection error)
        # but should NOT raise an exception
        assert isinstance(result, bool)
    
    @pytest.mark.asyncio
    async def test_async_logging_success(self):
        """Test successful asynchronous Supabase logging."""
        # Mock Supabase client
        mock_client = Mock()
        mock_result = Mock()
        mock_result.data = [{'id': 'test-id'}]
        mock_client.table.return_value.insert.return_value.execute.return_value = mock_result
        
        event = {
            'model': 'test-model',
            'finish_reason': 'length',
            'is_truncated': True
        }
        
        result = await log_truncation_to_supabase(event, supabase_client=mock_client)
        
        assert result is True
        mock_client.table.assert_called_once_with('truncation_events')


class TestProviderIntegration:
    """Test truncation detection integration in providers."""
    
    def test_kimi_chat_truncation_detection_exists(self):
        """Verify truncation detection code exists in kimi_chat.py."""
        from src.providers import kimi_chat
        import inspect
        
        source = inspect.getsource(kimi_chat.chat_completions_create)
        
        # Verify truncation detection imports
        assert 'check_truncation' in source
        assert 'log_truncation_to_supabase_sync' in source
        
        # Verify error handling
        assert 'except Exception as trunc_err' in source
    
    def test_async_kimi_chat_truncation_detection_exists(self):
        """Verify truncation detection code exists in async_kimi_chat.py."""
        from src.providers import async_kimi_chat
        import inspect
        
        source = inspect.getsource(async_kimi_chat.chat_completions_create_async)
        
        # Verify truncation detection imports
        assert 'check_truncation' in source
        assert 'log_truncation_to_supabase' in source
        
        # Verify error handling
        assert 'except Exception as trunc_err' in source
    
    def test_glm_chat_truncation_detection_exists(self):
        """Verify truncation detection code exists in glm_chat.py."""
        from src.providers import glm_chat
        import inspect
        
        source = inspect.getsource(glm_chat.generate_content)
        
        # Verify truncation detection imports
        assert 'check_truncation' in source
        assert 'log_truncation_to_supabase_sync' in source
        
        # Verify error handling
        assert 'except Exception as trunc_err' in source


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    def test_truncation_check_with_invalid_response(self):
        """Test that invalid responses don't crash truncation check."""
        # Empty response
        result = check_truncation({}, 'test-model')
        assert result['is_truncated'] is False
        
        # Missing choices
        result = check_truncation({'usage': {}}, 'test-model')
        assert result['is_truncated'] is False
        
        # Invalid structure
        result = check_truncation({'choices': []}, 'test-model')
        assert result['is_truncated'] is False
    
    def test_format_event_with_missing_fields(self):
        """Test that formatting works with missing fields."""
        truncation_info = {
            'timestamp': '2025-10-21T10:00:00Z',
            'model': 'test-model',
            # Missing finish_reason, usage, etc.
        }
        
        event = format_truncation_event(truncation_info)
        
        # Should still create valid event
        assert event['model'] == 'test-model'
        assert event['timestamp'] == '2025-10-21T10:00:00Z'
        assert 'finish_reason' in event
        assert 'is_truncated' in event


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

