"""
Conversation Storage Factory

Provides factory function to get appropriate conversation storage backend.
Supports in-memory, Supabase, and dual storage modes with configuration.
"""

import os
import logging
from typing import Literal, Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def get_conversation_storage(
    backend: Optional[Literal["memory", "supabase", "dual"]] = None,
    fallback: bool = True
):
    """
    Factory function to get appropriate conversation storage

    Args:
        backend: Storage backend type (memory, supabase, dual)
                If None, reads from CONVERSATION_STORAGE_BACKEND env var
        fallback: Enable fallback to in-memory storage on errors

    Returns:
        Conversation storage instance
    """
    if backend is None:
        backend = os.getenv("CONVERSATION_STORAGE_BACKEND", "memory")

    # DEBUG: Log storage backend selection
    logger.info(f"[STORAGE_FACTORY] Creating conversation storage: backend={backend}, fallback={fallback}")
    
    if backend == "memory":
        from .memory import InMemoryConversation
        return InMemoryConversation()
    
    elif backend == "supabase":
        from .supabase_memory import get_supabase_memory
        return get_supabase_memory(fallback_to_memory=fallback)
    
    elif backend == "dual":
        return DualStorageConversation(fallback=fallback)
    
    else:
        logger.warning(f"Unknown backend '{backend}', defaulting to memory")
        from .memory import InMemoryConversation
        return InMemoryConversation()


class DualStorageConversation:
    """
    Dual storage: Write to both Supabase and in-memory, read from Supabase with fallback.
    
    This provides the safest migration path:
    - All conversations are persisted to Supabase
    - In-memory storage provides immediate fallback
    - Gradual migration without downtime
    """
    
    def __init__(self, fallback: bool = True):
        """
        Initialize dual storage
        
        Args:
            fallback: Enable fallback to in-memory on Supabase errors
        """
        from .supabase_memory import get_supabase_memory
        from .memory import InMemoryConversation
        
        self.supabase = get_supabase_memory(fallback_to_memory=False)
        self.memory = InMemoryConversation()
        self.fallback = fallback
        
        logger.info("Initialized dual storage (Supabase + in-memory)")
    
    def get_thread(self, continuation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get thread from Supabase with fallback to in-memory
        
        Args:
            continuation_id: Unique conversation identifier
        
        Returns:
            Thread context dict or None
        """
        # Try Supabase first
        try:
            thread = self.supabase.get_thread(continuation_id)
            if thread:
                logger.debug(f"Retrieved thread {continuation_id} from Supabase")
                return thread
        except Exception as e:
            logger.warning(f"Supabase get_thread failed: {e}")
        
        # Fallback to in-memory
        if self.fallback:
            logger.debug(f"Falling back to in-memory for thread {continuation_id}")
            return self.memory.get_thread(continuation_id)
        
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
        Add turn to both Supabase and in-memory storage
        
        Args:
            continuation_id: Unique conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            files: Optional list of file paths
            images: Optional list of image paths
            metadata: Optional metadata
            tool_name: Optional tool name
        
        Returns:
            True if at least one storage succeeded
        """
        supabase_success = False
        memory_success = False
        
        # Try Supabase
        try:
            supabase_success = self.supabase.add_turn(
                continuation_id, role, content, files, images, metadata, tool_name
            )
            if supabase_success:
                logger.debug(f"Saved turn to Supabase: {continuation_id}")
        except Exception as e:
            logger.warning(f"Supabase add_turn failed: {e}")
        
        # Always write to in-memory (for fallback)
        try:
            memory_success = self.memory.add_turn(
                continuation_id, role, content, files, images, metadata, tool_name
            )
            if memory_success:
                logger.debug(f"Saved turn to in-memory: {continuation_id}")
        except Exception as e:
            logger.warning(f"In-memory add_turn failed: {e}")
        
        # Success if either succeeded
        success = supabase_success or memory_success
        
        if not success:
            logger.error(f"Failed to save turn to both storages: {continuation_id}")
        
        return success
    
    def build_conversation_history(
        self,
        continuation_id: str,
        model_context: Optional[Dict] = None
    ) -> tuple[str, int]:
        """
        Build conversation history from Supabase with fallback
        
        Args:
            continuation_id: Unique conversation identifier
            model_context: Optional model context for token counting
        
        Returns:
            Tuple of (history_string, token_count)
        """
        # Try Supabase first
        try:
            history, tokens = self.supabase.build_conversation_history(
                continuation_id, model_context
            )
            if history:
                return history, tokens
        except Exception as e:
            logger.warning(f"Supabase build_conversation_history failed: {e}")
        
        # Fallback to in-memory
        if self.fallback:
            try:
                from .memory import build_conversation_history
                return build_conversation_history(
                    self.memory.get_thread(continuation_id),
                    model_context
                )
            except Exception as e:
                logger.warning(f"In-memory build_conversation_history failed: {e}")
        
        return "", 0


# Convenience functions for backward compatibility
def get_thread(continuation_id: str) -> Optional[Dict[str, Any]]:
    """Get thread using configured storage backend"""
    storage = get_conversation_storage()
    return storage.get_thread(continuation_id)


def add_turn(
    continuation_id: str,
    role: str,
    content: str,
    files: Optional[List[str]] = None,
    images: Optional[List[str]] = None,
    metadata: Optional[Dict] = None,
    tool_name: Optional[str] = None
) -> bool:
    """Add turn using configured storage backend"""
    storage = get_conversation_storage()
    return storage.add_turn(
        continuation_id, role, content, files, images, metadata, tool_name
    )


def build_conversation_history(
    continuation_id: str,
    model_context: Optional[Dict] = None
) -> tuple[str, int]:
    """Build conversation history using configured storage backend"""
    storage = get_conversation_storage()
    return storage.build_conversation_history(continuation_id, model_context)

