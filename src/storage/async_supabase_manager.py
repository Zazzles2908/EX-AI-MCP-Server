"""
Async Supabase Manager for EXAI MCP Server
Provides async wrapper around synchronous Supabase client for MCP compatibility

WEEK 2 (2025-10-19): Async Supabase Operations
- Async wrapper pattern for MCP protocol compatibility
- ThreadPoolExecutor for non-blocking operations
- Fire-and-forget pattern for non-critical writes
- Graceful degradation on failures
"""

import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from supabase import create_client, Client
from src.storage.supabase_client import SupabaseStorageManager

logger = logging.getLogger(__name__)


class AsyncSupabaseManager:
    """
    Async wrapper around SupabaseStorageManager for MCP compatibility.
    
    The MCP protocol is synchronous, but we want non-blocking Supabase operations.
    This class provides async methods that run sync operations in a thread pool.
    
    Features:
    - Async wrapper pattern using ThreadPoolExecutor
    - Fire-and-forget pattern for non-critical writes
    - Graceful degradation on failures
    - Singleton pattern for resource efficiency
    """
    
    _instance: Optional['AsyncSupabaseManager'] = None
    _lock = asyncio.Lock()
    
    def __init__(self, pool_size: int = 5):
        """
        Initialize async Supabase manager.
        
        Args:
            pool_size: Number of worker threads for async operations
        """
        self.pool_size = pool_size
        self.executor = ThreadPoolExecutor(max_workers=pool_size, thread_name_prefix="supabase-async")
        self.sync_client = SupabaseStorageManager()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        
        logger.info(f"AsyncSupabaseManager initialized with pool_size={pool_size}")
    
    @classmethod
    async def get_instance(cls, pool_size: int = 5) -> 'AsyncSupabaseManager':
        """
        Get or create singleton instance (async-safe).
        
        Args:
            pool_size: Number of worker threads (only used on first call)
            
        Returns:
            AsyncSupabaseManager instance
        """
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(pool_size=pool_size)
        return cls._instance
    
    def _get_loop(self) -> asyncio.AbstractEventLoop:
        """Get or create event loop."""
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
        return self._loop
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """
        Run synchronous function in thread pool executor.
        
        Args:
            func: Synchronous function to run
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Result from function
        """
        loop = self._get_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: func(*args, **kwargs)
        )
    
    async def save_conversation_async(
        self,
        conversation_id: str,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        fire_and_forget: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Save conversation asynchronously.
        
        Args:
            conversation_id: Unique conversation identifier
            user_id: User identifier
            title: Optional conversation title
            metadata: Optional metadata dictionary
            fire_and_forget: If True, don't wait for result (non-blocking)
            
        Returns:
            Saved conversation data (None if fire_and_forget=True or on error)
        """
        try:
            if fire_and_forget:
                # Fire-and-forget: Schedule task but don't wait
                asyncio.create_task(
                    self._run_in_executor(
                        self.sync_client.save_conversation,
                        conversation_id,
                        user_id,
                        title,
                        metadata
                    )
                )
                logger.debug(f"Fire-and-forget save for conversation {conversation_id}")
                return None
            else:
                # Wait for result
                result = await self._run_in_executor(
                    self.sync_client.save_conversation,
                    conversation_id,
                    user_id,
                    title,
                    metadata
                )
                logger.debug(f"Async save completed for conversation {conversation_id}")
                return result
                
        except Exception as e:
            logger.error(f"Async save failed for conversation {conversation_id}: {e}")
            return None
    
    async def get_conversation_async(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation asynchronously.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Conversation data or None if not found/error
        """
        try:
            result = await self._run_in_executor(
                self.sync_client.get_conversation,
                conversation_id
            )
            logger.debug(f"Async get completed for conversation {conversation_id}")
            return result
        except Exception as e:
            logger.error(f"Async get failed for conversation {conversation_id}: {e}")
            return None
    
    async def save_message_async(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        fire_and_forget: bool = True  # Messages are often non-critical
    ) -> Optional[Dict[str, Any]]:
        """
        Save message asynchronously.
        
        Args:
            conversation_id: Conversation identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
            fire_and_forget: If True, don't wait for result (default: True for messages)
            
        Returns:
            Saved message data (None if fire_and_forget=True or on error)
        """
        try:
            if fire_and_forget:
                # Fire-and-forget: Schedule task but don't wait
                asyncio.create_task(
                    self._run_in_executor(
                        self.sync_client.save_message,
                        conversation_id,
                        role,
                        content,
                        metadata
                    )
                )
                logger.debug(f"Fire-and-forget save for message in {conversation_id}")
                return None
            else:
                # Wait for result
                result = await self._run_in_executor(
                    self.sync_client.save_message,
                    conversation_id,
                    role,
                    content,
                    metadata
                )
                logger.debug(f"Async message save completed for {conversation_id}")
                return result
                
        except Exception as e:
            logger.error(f"Async message save failed for {conversation_id}: {e}")
            return None
    
    async def get_conversation_history_async(
        self,
        conversation_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get conversation history asynchronously.
        
        Args:
            conversation_id: Conversation identifier
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages (empty list on error)
        """
        try:
            result = await self._run_in_executor(
                self.sync_client.get_conversation_history,
                conversation_id,
                limit
            )
            logger.debug(f"Async history get completed for {conversation_id}")
            return result or []
        except Exception as e:
            logger.error(f"Async history get failed for {conversation_id}: {e}")
            return []
    
    async def shutdown(self):
        """Shutdown executor gracefully."""
        logger.info("Shutting down AsyncSupabaseManager...")
        self.executor.shutdown(wait=True)
        logger.info("AsyncSupabaseManager shutdown complete")
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.executor.shutdown(wait=False)
        except Exception:
            pass


# Singleton instance getter (convenience function)
async def get_async_supabase_manager(pool_size: int = 5) -> AsyncSupabaseManager:
    """
    Get singleton AsyncSupabaseManager instance.
    
    Args:
        pool_size: Number of worker threads (only used on first call)
        
    Returns:
        AsyncSupabaseManager instance
    """
    return await AsyncSupabaseManager.get_instance(pool_size=pool_size)

