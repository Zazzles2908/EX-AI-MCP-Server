"""
Truncation detection utility for EXAI responses.

This module provides functions to detect when API responses are truncated
due to max_tokens limits and log these events for monitoring.

Created: 2025-10-21 (Phase 2.1.2)
Purpose: Detect and monitor truncated responses
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def check_truncation(response: Dict[str, Any], model_name: str) -> Dict[str, Any]:
    """
    Check if an API response was truncated due to max_tokens limit.
    
    Args:
        response: API response dictionary (OpenAI-compatible format)
        model_name: Name of the model used
    
    Returns:
        Dictionary with truncation information:
        {
            'is_truncated': bool,
            'finish_reason': str,
            'model': str,
            'usage': dict (if available),
            'timestamp': str
        }
    """
    truncation_info = {
        'is_truncated': False,
        'finish_reason': None,
        'model': model_name,
        'usage': None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    try:
        # Extract finish_reason from response
        # OpenAI-compatible format: response['choices'][0]['finish_reason']
        if 'choices' in response and len(response['choices']) > 0:
            finish_reason = response['choices'][0].get('finish_reason')
            truncation_info['finish_reason'] = finish_reason
            
            # Check if truncated
            # finish_reason can be: 'stop', 'length', 'tool_calls', 'content_filter', etc.
            if finish_reason == 'length':
                truncation_info['is_truncated'] = True
                logger.warning(
                    f"Truncated response detected for model {model_name}. "
                    f"finish_reason='{finish_reason}'"
                )
        
        # Extract usage information if available
        if 'usage' in response:
            truncation_info['usage'] = {
                'prompt_tokens': response['usage'].get('prompt_tokens', 0),
                'completion_tokens': response['usage'].get('completion_tokens', 0),
                'total_tokens': response['usage'].get('total_tokens', 0)
            }
            
            if truncation_info['is_truncated']:
                logger.info(
                    f"Truncation details - Model: {model_name}, "
                    f"Prompt tokens: {truncation_info['usage']['prompt_tokens']}, "
                    f"Completion tokens: {truncation_info['usage']['completion_tokens']}"
                )
    
    except Exception as e:
        logger.error(f"Error checking truncation for model {model_name}: {e}")
        truncation_info['error'] = str(e)
    
    return truncation_info


def should_log_truncation(truncation_info: Dict[str, Any]) -> bool:
    """
    Determine if a truncation event should be logged to Supabase.
    
    Args:
        truncation_info: Truncation information from check_truncation()
    
    Returns:
        True if event should be logged, False otherwise
    """
    # Only log actual truncations
    if not truncation_info.get('is_truncated', False):
        return False
    
    # Don't log if there was an error during detection
    if 'error' in truncation_info:
        return False
    
    return True


def format_truncation_event(
    truncation_info: Dict[str, Any],
    tool_name: Optional[str] = None,
    conversation_id: Optional[str] = None,
    additional_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format truncation information for Supabase logging.
    
    Args:
        truncation_info: Truncation information from check_truncation()
        tool_name: Name of the EXAI tool that was called (e.g., 'debug', 'codereview')
        conversation_id: Conversation/continuation ID if available
        additional_context: Additional context to include in the log
    
    Returns:
        Formatted event dictionary ready for Supabase insertion
    """
    event = {
        'timestamp': truncation_info.get('timestamp'),
        'model': truncation_info.get('model'),
        'finish_reason': truncation_info.get('finish_reason'),
        'is_truncated': truncation_info.get('is_truncated', False),
        'tool_name': tool_name,
        'conversation_id': conversation_id,
    }
    
    # Add usage information if available
    if truncation_info.get('usage'):
        event['prompt_tokens'] = truncation_info['usage'].get('prompt_tokens', 0)
        event['completion_tokens'] = truncation_info['usage'].get('completion_tokens', 0)
        event['total_tokens'] = truncation_info['usage'].get('total_tokens', 0)
    
    # Add additional context
    if additional_context:
        event['context'] = additional_context
    
    return event


def log_truncation_to_supabase_sync(
    truncation_event: Dict[str, Any],
    supabase_client: Optional[Any] = None
) -> bool:
    """
    Synchronously log truncation event to Supabase for monitoring.

    This is the SYNC version for calling from sync contexts (e.g., kimi_chat.py).
    Designed for backup/recovery logging - failures are logged but don't block execution.

    Args:
        truncation_event: Formatted truncation event from format_truncation_event()
        supabase_client: Supabase client instance (optional, will create if None)

    Returns:
        True if logged successfully, False otherwise
    """
    try:
        # Import Supabase client if not provided
        if supabase_client is None:
            try:
                from src.utils.supabase_client import get_supabase_client
                supabase_client = get_supabase_client()
            except ImportError:
                logger.debug("Supabase client not available, skipping truncation logging")
                return False

        # Insert into truncation_events table
        # Note: Table needs to be created in Supabase first
        result = supabase_client.table('truncation_events').insert(truncation_event).execute()

        if result.data:
            logger.info(f"✅ Truncation event logged to Supabase: {truncation_event['model']}")
            return True
        else:
            logger.debug(f"Failed to log truncation event: {result}")
            return False

    except Exception as e:
        # Log locally but don't fail the main operation
        # This is backup/recovery logging - failures are acceptable
        logger.debug(f"Supabase truncation logging failed (non-critical): {e}")
        return False


async def log_truncation_to_supabase(
    truncation_event: Dict[str, Any],
    supabase_client: Optional[Any] = None
) -> bool:
    """
    Asynchronously log truncation event to Supabase for monitoring.

    This is the ASYNC version for calling from async contexts (e.g., async_kimi_chat.py).
    Designed for backup/recovery logging - failures are logged but don't block execution.

    Args:
        truncation_event: Formatted truncation event from format_truncation_event()
        supabase_client: Supabase client instance (optional, will create if None)

    Returns:
        True if logged successfully, False otherwise
    """
    try:
        # Import Supabase client if not provided
        if supabase_client is None:
            try:
                from src.utils.supabase_client import get_supabase_client
                supabase_client = get_supabase_client()
            except ImportError:
                logger.debug("Supabase client not available, skipping truncation logging")
                return False

        # Insert into truncation_events table
        # Note: Table needs to be created in Supabase first
        result = supabase_client.table('truncation_events').insert(truncation_event).execute()

        if result.data:
            logger.info(f"✅ Truncation event logged to Supabase: {truncation_event['model']}")
            return True
        else:
            logger.debug(f"Failed to log truncation event: {result}")
            return False

    except Exception as e:
        # Log locally but don't fail the main operation
        # This is backup/recovery logging - failures are acceptable
        logger.debug(f"Supabase truncation logging failed (non-critical): {e}")
        return False


def get_truncation_stats(
    supabase_client: Optional[Any] = None,
    model_name: Optional[str] = None,
    tool_name: Optional[str] = None,
    hours: int = 24
) -> Dict[str, Any]:
    """
    Get truncation statistics from Supabase.
    
    Args:
        supabase_client: Supabase client instance
        model_name: Filter by specific model (optional)
        tool_name: Filter by specific tool (optional)
        hours: Number of hours to look back (default: 24)
    
    Returns:
        Dictionary with truncation statistics
    """
    try:
        if supabase_client is None:
            from src.utils.supabase_client import get_supabase_client
            supabase_client = get_supabase_client()
        
        # Build query
        query = supabase_client.table('truncation_events').select('*')
        
        # Add filters
        if model_name:
            query = query.eq('model', model_name)
        if tool_name:
            query = query.eq('tool_name', tool_name)
        
        # Time filter (last N hours)
        from datetime import timedelta
        cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        query = query.gte('timestamp', cutoff_time)
        
        # Execute query
        result = query.execute()
        
        # Calculate statistics
        events = result.data if result.data else []
        total_events = len(events)
        
        # Group by model
        by_model = {}
        for event in events:
            model = event.get('model', 'unknown')
            if model not in by_model:
                by_model[model] = 0
            by_model[model] += 1
        
        # Group by tool
        by_tool = {}
        for event in events:
            tool = event.get('tool_name', 'unknown')
            if tool not in by_tool:
                by_tool[tool] = 0
            by_tool[tool] += 1
        
        return {
            'total_truncations': total_events,
            'by_model': by_model,
            'by_tool': by_tool,
            'time_range_hours': hours,
            'events': events
        }
    
    except Exception as e:
        logger.error(f"Error getting truncation stats: {e}")
        return {
            'total_truncations': 0,
            'by_model': {},
            'by_tool': {},
            'error': str(e)
        }

