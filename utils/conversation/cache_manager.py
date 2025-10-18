"""
Conversation Cache Manager

Multi-layer caching for conversation storage to reduce Supabase HTTP calls.

Architecture:
- L1: In-memory LRU cache (configurable TTL, 100 items) - fastest
- L2: Redis distributed cache (configurable TTL) - fast, persistent across restarts
- L3: Supabase storage - persistent, source of truth

Performance Target:
- Cache hit: 0 Supabase calls
- Cache miss: 2 Supabase calls (1 load, 1 save)
- Reduces overhead from 350-1050ms to 10-50ms

Created: 2025-10-16 21:15 AEDT
Updated: 2025-10-16 23:55 AEDT (Refactored to use BaseCacheManager - composition pattern)
Issue: 926e2c85-98d0-4163-a0c3-7299ee05416c
"""

import logging
import os
import threading
from typing import Optional, Dict, Any, List

from utils.caching.base_cache_manager import BaseCacheManager

logger = logging.getLogger(__name__)


class ConversationCacheManager:
    """
    Conversation-specific cache manager using BaseCacheManager internally.

    Provides domain-specific methods for caching conversations and messages
    while delegating actual caching logic to BaseCacheManager.

    Uses composition pattern to eliminate code duplication.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize cache manager (only once)"""
        if self._initialized:
            return

        # Configurable TTLs from environment variables
        l1_ttl = int(os.getenv("L1_CACHE_TTL_SECS", "300"))  # 5min default
        l2_ttl = int(os.getenv("L2_CACHE_TTL_SECS", "1800"))  # 30min default
        enable_redis = os.getenv("ENABLE_REDIS_CACHE", "true").lower() == "true"

        # Use BaseCacheManager internally with conversation-specific settings
        self._cache_manager = BaseCacheManager(
            l1_maxsize=100,
            l1_ttl=l1_ttl,
            l2_ttl=l2_ttl,
            enable_redis=enable_redis,
            cache_prefix="conversation"
        )

        self._initialized = True
        logger.info(f"[CACHE_MANAGER] Conversation cache manager initialized (L1_TTL={l1_ttl}s, L2_TTL={l2_ttl}s)")
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation from cache (L1 → L2 → None)

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation dict or None if not in cache
        """
        return self._cache_manager.get(conversation_id)
    
    def get_messages(self, conversation_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get messages from cache (L1 → L2 → None)

        Args:
            conversation_id: Conversation ID

        Returns:
            List of message dicts or None if not in cache
        """
        cache_key = f"{conversation_id}:messages"
        return self._cache_manager.get(cache_key)

    def set_conversation(self, conversation_id: str, conversation: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Write conversation to all cache layers (write-through)

        Args:
            conversation_id: Conversation ID
            conversation: Conversation dict
            ttl: Optional TTL override (uses L2 default if not specified)
        """
        self._cache_manager.set(conversation_id, conversation, ttl)

    def set_messages(self, conversation_id: str, messages: List[Dict[str, Any]], ttl: Optional[int] = None) -> None:
        """
        Write messages to all cache layers (write-through)

        Args:
            conversation_id: Conversation ID
            messages: List of message dicts
            ttl: Optional TTL override (uses L2 default if not specified)
        """
        cache_key = f"{conversation_id}:messages"
        self._cache_manager.set(cache_key, messages, ttl)
    
    def invalidate(self, conversation_id: str) -> None:
        """
        Invalidate conversation from all cache layers

        Args:
            conversation_id: Conversation ID
        """
        # Delete conversation
        self._cache_manager.delete(conversation_id)

        # Delete messages
        cache_key = f"{conversation_id}:messages"
        self._cache_manager.delete(cache_key)

        logger.debug(f"[CACHE_MANAGER] INVALIDATE: {conversation_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics with hit ratio"""
        return self._cache_manager.get_stats()

    def clear_stats(self) -> None:
        """Clear cache statistics"""
        self._cache_manager.clear_stats()


# Global singleton instance
_cache_manager = None


def get_cache_manager() -> ConversationCacheManager:
    """Get singleton cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = ConversationCacheManager()
    return _cache_manager

