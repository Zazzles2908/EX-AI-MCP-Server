"""
Conversation ID Mapper for Supabase Storage

Maps continuation_id (string UUID) to Supabase conversation ID (UUID primary key).
Provides caching and lazy creation for efficient conversation management.
"""

import logging
from typing import Optional, Dict
from .supabase_client import get_storage_manager

logger = logging.getLogger(__name__)


class ConversationMapper:
    """
    Maps continuation_id to Supabase conversation ID with caching.
    
    Features:
    - Lazy conversation creation
    - ID mapping cache
    - Efficient lookups
    - Error handling
    """
    
    def __init__(self):
        """Initialize mapper with storage manager and cache"""
        self.storage = get_storage_manager()
        self._id_cache: Dict[str, str] = {}  # continuation_id -> conv_id cache
    
    def get_or_create_conversation(
        self,
        continuation_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Get conversation ID or create new one
        
        Args:
            continuation_id: Unique conversation identifier
            title: Optional conversation title
            metadata: Optional metadata
        
        Returns:
            Conversation UUID or None on error
        """
        if not self.storage.enabled:
            logger.debug("Supabase storage not enabled, skipping conversation mapping")
            return None
        
        # Check cache first
        if continuation_id in self._id_cache:
            logger.debug(f"Found cached conversation ID for {continuation_id}")
            return self._id_cache[continuation_id]
        
        # Look up in Supabase
        conv = self.storage.get_conversation_by_continuation_id(continuation_id)
        
        if conv:
            conv_id = conv['id']
            logger.debug(f"Found existing conversation: {continuation_id} -> {conv_id}")
        else:
            # Create new conversation
            conv_id = self.storage.save_conversation(
                continuation_id=continuation_id,
                title=title,
                metadata=metadata
            )
            if conv_id:
                logger.info(f"Created new conversation: {continuation_id} -> {conv_id}")
            else:
                logger.error(f"Failed to create conversation for {continuation_id}")
                return None
        
        # Cache the mapping
        self._id_cache[continuation_id] = conv_id
        return conv_id
    
    def clear_cache(self):
        """Clear the ID mapping cache"""
        self._id_cache.clear()
        logger.debug("Cleared conversation ID cache")
    
    def get_cached_id(self, continuation_id: str) -> Optional[str]:
        """Get cached conversation ID without database lookup"""
        return self._id_cache.get(continuation_id)


# Global instance
_conversation_mapper: Optional[ConversationMapper] = None


def get_conversation_mapper() -> ConversationMapper:
    """Get global conversation mapper instance"""
    global _conversation_mapper
    if _conversation_mapper is None:
        _conversation_mapper = ConversationMapper()
    return _conversation_mapper

