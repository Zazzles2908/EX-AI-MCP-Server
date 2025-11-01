"""
Global Conversation Storage Singleton

CRITICAL FIX (2025-10-24): This module provides a SINGLE global storage instance
to prevent multiple instances with separate request caches.

PROBLEM IDENTIFIED:
- Multiple code paths were creating separate storage instances
- Each instance had its own `_thread_cache` dictionary
- Request cache (L0) was ineffective because cache hits checked different instances
- Result: 4x Supabase query duplication per request with continuation_id

SOLUTION:
- Single global storage instance shared across ALL code paths
- All imports use this module to get the same instance
- Request cache works correctly because all calls check the same cache
- Result: 1 Supabase query + 3 cache hits = 75% cost reduction

USAGE:
    from utils.conversation.global_storage import get_thread, add_turn
    
    # Get thread (uses global storage instance)
    thread = get_thread(continuation_id)
    
    # Add turn (uses global storage instance)
    add_turn(continuation_id, "user", "Hello", files=["file.py"])

MIGRATION:
    Replace all instances of:
        from utils.conversation.memory import get_thread, add_turn
    With:
        from utils.conversation.global_storage import get_thread, add_turn
"""

import logging
import threading
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# Global singleton instance and lock for thread-safe initialization
_global_storage = None
_global_lock = threading.Lock()


def get_global_storage():
    """
    Get the single global storage instance (SINGLETON PATTERN)
    
    This ensures ALL code paths use the SAME storage instance,
    which means they all share the SAME request cache (_thread_cache).
    
    Returns:
        Global storage instance (singleton)
    """
    global _global_storage
    
    if _global_storage is None:
        with _global_lock:
            # Double-check pattern
            if _global_storage is None:
                from utils.conversation.storage_factory import get_conversation_storage
                _global_storage = get_conversation_storage()
                logger.info(f"[GLOBAL_STORAGE] Created global storage instance: {type(_global_storage).__name__} (id={id(_global_storage)})")
    
    return _global_storage


def get_thread(continuation_id: str):
    """
    Get thread using global storage instance with automatic format conversion

    This is the ONLY correct way to get a thread. It ensures the request cache
    works properly by using the same storage instance across all call sites.

    CRITICAL FIX (2025-10-24): Converts Supabase dict format to ThreadContext model
    to maintain compatibility with code expecting ThreadContext objects.

    Args:
        continuation_id: Unique conversation identifier

    Returns:
        ThreadContext object or None if not found
    """
    from utils.conversation.models import ThreadContext, ConversationTurn

    storage = get_global_storage()
    thread_data = storage.get_thread(continuation_id)

    if not thread_data:
        return None

    # If already a ThreadContext, return as-is
    if isinstance(thread_data, ThreadContext):
        logger.debug(f"[GLOBAL_STORAGE] Thread {continuation_id} already ThreadContext")
        return thread_data

    # Convert Supabase dict format to ThreadContext
    if isinstance(thread_data, dict):
        logger.debug(f"[GLOBAL_STORAGE] Converting dict to ThreadContext for {continuation_id}")
        try:
            # Convert messages to turns
            turns = []
            for msg in thread_data.get('messages', []):
                turn = ConversationTurn(
                    role=msg.get('role', 'user'),
                    content=msg.get('content', ''),
                    timestamp=msg.get('created_at', ''),
                    files=msg.get('files'),
                    images=msg.get('images'),
                    tool_name=msg.get('tool_name'),
                    model_provider=msg.get('model_provider'),
                    model_name=msg.get('model_name'),
                    model_metadata=msg.get('model_metadata')
                )
                turns.append(turn)

            # Extract metadata
            metadata = thread_data.get('metadata', {})

            # Create ThreadContext
            context = ThreadContext(
                thread_id=thread_data.get('id', continuation_id),
                parent_thread_id=metadata.get('parent_thread_id'),
                created_at=thread_data.get('created_at', ''),
                last_updated_at=thread_data.get('updated_at', ''),
                tool_name=metadata.get('tool_name', 'unknown'),
                turns=turns,
                initial_context=metadata.get('initial_context', {}),
                session_fingerprint=metadata.get('session_fingerprint'),
                client_friendly_name=metadata.get('client_friendly_name')
            )
            logger.debug(f"[GLOBAL_STORAGE] Converted to ThreadContext ({len(turns)} turns)")
            return context
        except Exception as e:
            logger.error(f"[GLOBAL_STORAGE] Failed to convert dict to ThreadContext: {e}", exc_info=True)
            return None

    logger.warning(f"[GLOBAL_STORAGE] Unexpected thread data type: {type(thread_data)}")
    return None


def add_turn(
    continuation_id: str,
    role: str,
    content: str,
    files: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
    tool_name: Optional[str] = None,
    model_provider: Optional[str] = None,
    model_name: Optional[str] = None,
    model_metadata: Optional[Dict] = None
) -> bool:
    """
    Add turn using global storage instance

    CRITICAL FIX (2025-10-24): Added model_provider, model_name, model_metadata parameters
    to match the signature expected by tools/simple/base.py and other callers.

    These parameters are merged into the metadata dict before passing to storage.

    Args:
        continuation_id: Unique conversation identifier
        role: Message role (user, assistant, system)
        content: Message content
        files: Optional list of file paths
        images: Optional list of image paths
        metadata: Optional metadata
        tool_name: Optional tool name
        model_provider: Optional model provider (e.g., "glm", "kimi")
        model_name: Optional model name (e.g., "glm-4.6")
        model_metadata: Optional model metadata (e.g., thinking mode, tokens)

    Returns:
        True if successful, False otherwise
    """
    # Merge model parameters into metadata
    if metadata is None:
        metadata = {}

    if model_provider:
        metadata['model_provider'] = model_provider
    if model_name:
        metadata['model_name'] = model_name
    if model_metadata:
        metadata['model_metadata'] = model_metadata

    storage = get_global_storage()
    return storage.add_turn(
        continuation_id, role, content, files, images, metadata, tool_name
    )


# PHASE 2 FIX (2025-11-01): Removed clear_request_cache() function
# Request-scoped cache has been eliminated as part of cache layer reduction


def get_messages_array(continuation_id: str, max_messages: int = 50) -> List[Dict[str, Any]]:
    """
    Get messages in SDK-native array format
    
    Args:
        continuation_id: Unique conversation identifier
        max_messages: Maximum number of messages to return
    
    Returns:
        List of message dicts in SDK format
    """
    storage = get_global_storage()
    if hasattr(storage, 'get_messages_array'):
        return storage.get_messages_array(continuation_id, max_messages)
    else:
        # Fallback: convert thread to messages
        thread = storage.get_thread(continuation_id)
        if not thread:
            return []
        
        messages = []
        for msg in thread.get('messages', [])[:max_messages]:
            messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })
        return messages


# ============================================================================
# Validation Functions (for testing)
# ============================================================================

def validate_singleton():
    """
    Validate that get_global_storage() returns the same instance
    
    This is a test function to verify the singleton pattern works correctly.
    
    Returns:
        True if singleton pattern is working, False otherwise
    """
    storage1 = get_global_storage()
    storage2 = get_global_storage()
    
    if storage1 is storage2:
        logger.info(f"✅ Singleton validation passed: {id(storage1)} == {id(storage2)}")
        return True
    else:
        logger.error(f"❌ Singleton validation FAILED: {id(storage1)} != {id(storage2)}")
        return False


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics from global storage
    
    Returns:
        Dict with cache statistics (hits, misses, size, etc.)
    """
    storage = get_global_storage()
    
    stats = {
        'storage_type': type(storage).__name__,
        'storage_id': id(storage),
        'has_request_cache': hasattr(storage, '_thread_cache'),
        'cache_size': 0,
        'cache_enabled': False
    }
    
    # Try to get cache stats from Supabase storage
    if hasattr(storage, '_thread_cache'):
        stats['cache_size'] = len(storage._thread_cache)
        stats['cache_enabled'] = getattr(storage, '_request_cache_enabled', False)
    elif hasattr(storage, 'supabase'):
        # DualStorageConversation wrapper
        if hasattr(storage.supabase, '_thread_cache'):
            stats['cache_size'] = len(storage.supabase._thread_cache)
            stats['cache_enabled'] = getattr(storage.supabase, '_request_cache_enabled', False)
    
    return stats

