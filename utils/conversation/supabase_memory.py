"""
Supabase Conversation Memory

Provides persistent conversation storage using Supabase with fallback to in-memory storage.
Compatible with existing conversation memory interface for seamless integration.
"""

import logging
from typing import Optional, Dict, Any, List
from src.storage.supabase_client import get_storage_manager
from src.storage.conversation_mapper import get_conversation_mapper
from src.storage.file_handler import get_file_handler

logger = logging.getLogger(__name__)


class SupabaseConversationMemory:
    """
    Persistent conversation memory using Supabase.
    
    Features:
    - Conversation persistence
    - Message history storage
    - File upload integration
    - Fallback to in-memory storage
    - Compatible with existing memory interface
    """
    
    def __init__(self, fallback_to_memory: bool = True):
        """
        Initialize Supabase conversation memory
        
        Args:
            fallback_to_memory: Enable fallback to in-memory storage on errors
        """
        self.storage = get_storage_manager()
        self.mapper = get_conversation_mapper()
        self.file_handler = get_file_handler()
        self.fallback_to_memory = fallback_to_memory
        
        # Import in-memory functions for fallback
        if fallback_to_memory:
            try:
                from .memory import get_thread as memory_get_thread
                from .memory import add_turn as memory_add_turn
                self._memory_get_thread = memory_get_thread
                self._memory_add_turn = memory_add_turn
            except ImportError:
                logger.warning("In-memory fallback not available")
                self.fallback_to_memory = False
    
    def get_thread(self, continuation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation thread from Supabase
        
        Args:
            continuation_id: Unique conversation identifier
        
        Returns:
            Thread context dict or None if not found
        """
        if not self.storage.enabled:
            if self.fallback_to_memory:
                logger.debug("Supabase not enabled, using in-memory fallback")
                return self._memory_get_thread(continuation_id)
            return None
        
        try:
            # Get conversation from Supabase
            conv = self.storage.get_conversation_by_continuation_id(continuation_id)
            
            if not conv:
                logger.debug(f"No conversation found for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_get_thread(continuation_id)
                return None
            
            # Get messages
            messages = self.storage.get_conversation_messages(conv['id'])
            
            # Convert to thread format
            thread = {
                'id': continuation_id,
                'conversation_id': conv['id'],
                'messages': messages,
                'metadata': conv.get('metadata', {}),
                'storage': 'supabase',
                'created_at': conv.get('created_at'),
                'updated_at': conv.get('updated_at')
            }
            
            logger.debug(f"Retrieved thread {continuation_id} with {len(messages)} messages")
            return thread
        
        except Exception as e:
            logger.error(f"Error getting thread {continuation_id}: {e}")
            if self.fallback_to_memory:
                logger.debug("Falling back to in-memory storage")
                return self._memory_get_thread(continuation_id)
            return None
    
    def add_turn(
        self,
        continuation_id: str,
        role: str,
        content: str,
        files: Optional[List[str]] = None,
        images: Optional[List[str]] = None,
        metadata: Optional[Dict] = None,
        tool_name: Optional[str] = None
    ) -> bool:
        """
        Add a conversation turn to Supabase
        
        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata
            tool_name: Optional tool name
        
        Returns:
            True if successful, False otherwise
        """
        if not self.storage.enabled:
            if self.fallback_to_memory:
                logger.debug("Supabase not enabled, using in-memory fallback")
                return self._memory_add_turn(
                    continuation_id, role, content, files, images, metadata, tool_name
                )
            return False
        
        try:
            # Get or create conversation
            conv_id = self.mapper.get_or_create_conversation(
                continuation_id=continuation_id,
                title=f"Conversation {continuation_id[:8]}",
                metadata={'tool_name': tool_name} if tool_name else None
            )
            
            if not conv_id:
                logger.error(f"Failed to get/create conversation for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_add_turn(
                        continuation_id, role, content, files, images, metadata, tool_name
                    )
                return False
            
            # Process files if provided
            file_ids = []
            all_files = (files or []) + (images or [])
            
            if all_files:
                processed_files = self.file_handler.process_files(
                    file_paths=all_files,
                    context_id=continuation_id,
                    upload_immediately=True
                )
                
                # Extract file IDs and link to conversation
                for file_info in processed_files:
                    file_id = file_info.get('file_id')
                    if file_id:
                        file_ids.append(file_id)
                        self.storage.link_file_to_conversation(conv_id, file_id)
            
            # Prepare message metadata
            msg_metadata = metadata or {}
            msg_metadata['file_ids'] = file_ids
            msg_metadata['tool_name'] = tool_name
            
            # Save message
            msg_id = self.storage.save_message(
                conversation_id=conv_id,
                role=role,
                content=content,
                metadata=msg_metadata
            )
            
            if msg_id:
                logger.debug(f"Saved turn for {continuation_id}: {role} message")
                return True
            else:
                logger.error(f"Failed to save message for {continuation_id}")
                if self.fallback_to_memory:
                    return self._memory_add_turn(
                        continuation_id, role, content, files, images, metadata, tool_name
                    )
                return False
        
        except Exception as e:
            logger.error(f"Error adding turn to {continuation_id}: {e}")
            if self.fallback_to_memory:
                logger.debug("Falling back to in-memory storage")
                return self._memory_add_turn(
                    continuation_id, role, content, files, images, metadata, tool_name
                )
            return False
    
    def build_conversation_history(
        self,
        continuation_id: str,
        model_context: Optional[Dict] = None
    ) -> tuple[str, int]:
        """
        Build conversation history string from Supabase
        
        Args:
            continuation_id: Unique conversation identifier
            model_context: Optional model context for token counting
        
        Returns:
            Tuple of (history_string, token_count)
        """
        thread = self.get_thread(continuation_id)
        
        if not thread or not thread.get('messages'):
            return "", 0
        
        # Build history string
        history_parts = ["=== CONVERSATION HISTORY ===\n"]
        
        for msg in thread['messages']:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            history_parts.append(f"\n**{role.upper()}:**\n{content}\n")
        
        history_parts.append("\n=== END CONVERSATION HISTORY ===\n")
        history_string = "".join(history_parts)
        
        # Estimate token count (rough estimate: 4 chars per token)
        token_count = len(history_string) // 4
        
        return history_string, token_count


# Global instance
_supabase_memory: Optional[SupabaseConversationMemory] = None


def get_supabase_memory(fallback_to_memory: bool = True) -> SupabaseConversationMemory:
    """Get global Supabase conversation memory instance"""
    global _supabase_memory
    if _supabase_memory is None:
        _supabase_memory = SupabaseConversationMemory(fallback_to_memory=fallback_to_memory)
    return _supabase_memory

