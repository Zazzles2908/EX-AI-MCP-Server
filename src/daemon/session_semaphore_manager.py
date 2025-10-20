"""
Session-based semaphore manager for concurrent EXAI request processing.

BUG FIX #11 (Phase 2 - 2025-10-20): Replace global semaphore with per-session semaphores
to enable concurrent processing of different conversations.

This module provides:
- Per-conversation semaphore management
- Automatic cleanup of inactive sessions
- Configurable concurrency limits per session
- Monitoring and metrics for semaphore usage
"""

import asyncio
import time
import logging
from typing import Dict, Optional
from datetime import datetime

# Use standard logging instead of loguru for compatibility
logger = logging.getLogger(__name__)


class SessionSemaphoreManager:
    """
    Manages per-session semaphores for concurrent EXAI request processing.
    
    BUG FIX #11 (Phase 2 - 2025-10-20): This replaces the global semaphore
    with per-conversation semaphores to enable concurrent processing.
    
    Features:
    - Per-conversation semaphore isolation
    - Automatic cleanup of inactive sessions
    - Configurable concurrency limits
    - Usage tracking and monitoring
    
    Usage:
        manager = SessionSemaphoreManager(max_concurrent_per_session=1)
        await manager.start_cleanup_task()
        
        # In request handler:
        semaphore = await manager.get_semaphore(conversation_id)
        async with semaphore:
            # Process request
            pass
    """
    
    def __init__(
        self,
        max_concurrent_per_session: int = 1,
        cleanup_interval: int = 300,
        inactive_timeout: int = 300
    ):
        """
        Initialize session semaphore manager.
        
        Args:
            max_concurrent_per_session: Maximum concurrent requests per conversation
            cleanup_interval: How often to run cleanup (seconds)
            inactive_timeout: How long before a session is considered inactive (seconds)
        """
        self._semaphores: Dict[str, asyncio.Semaphore] = {}
        self._last_used: Dict[str, float] = {}
        self._max_concurrent_per_session = max_concurrent_per_session
        self._cleanup_interval = cleanup_interval
        self._inactive_timeout = inactive_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Metrics
        self._total_sessions_created = 0
        self._total_sessions_cleaned = 0
        
        logger.info(
            f"[SESSION_SEM] Initialized SessionSemaphoreManager "
            f"(max_concurrent_per_session={max_concurrent_per_session}, "
            f"cleanup_interval={cleanup_interval}s, "
            f"inactive_timeout={inactive_timeout}s)"
        )
    
    async def get_semaphore(self, conversation_id: str) -> asyncio.Semaphore:
        """
        Get or create a semaphore for the given conversation.
        
        Args:
            conversation_id: Unique conversation identifier
            
        Returns:
            Semaphore for this conversation
        """
        if conversation_id not in self._semaphores:
            self._semaphores[conversation_id] = asyncio.Semaphore(
                self._max_concurrent_per_session
            )
            self._total_sessions_created += 1
            logger.debug(
                f"[SESSION_SEM] Created semaphore for conversation {conversation_id} "
                f"(total sessions: {len(self._semaphores)})"
            )
        
        # Update last used timestamp
        self._last_used[conversation_id] = time.time()
        
        return self._semaphores[conversation_id]
    
    async def cleanup_inactive_sessions(self):
        """
        Background task to remove semaphores for inactive sessions.
        
        Runs periodically to clean up sessions that haven't been used
        for longer than inactive_timeout.
        """
        logger.info("[SESSION_SEM] Cleanup task started")
        
        while self._running:
            try:
                await asyncio.sleep(self._cleanup_interval)
                
                current_time = time.time()
                inactive_sessions = [
                    conv_id for conv_id, last_used in self._last_used.items()
                    if current_time - last_used > self._inactive_timeout
                ]
                
                if inactive_sessions:
                    for conv_id in inactive_sessions:
                        del self._semaphores[conv_id]
                        del self._last_used[conv_id]
                        self._total_sessions_cleaned += 1
                    
                    logger.info(
                        f"[SESSION_SEM] Cleaned up {len(inactive_sessions)} inactive sessions "
                        f"(remaining: {len(self._semaphores)})"
                    )
                else:
                    logger.debug(
                        f"[SESSION_SEM] No inactive sessions to clean "
                        f"(active sessions: {len(self._semaphores)})"
                    )
                    
            except Exception as e:
                logger.error(f"[SESSION_SEM] Error in cleanup task: {e}", exc_info=True)
        
        logger.info("[SESSION_SEM] Cleanup task stopped")
    
    async def start_cleanup_task(self):
        """
        Start the background cleanup task.
        
        Should be called during server initialization.
        """
        if self._cleanup_task is not None:
            logger.warning("[SESSION_SEM] Cleanup task already running")
            return
        
        self._running = True
        self._cleanup_task = asyncio.create_task(self.cleanup_inactive_sessions())
        logger.info("[SESSION_SEM] Cleanup task started")
    
    async def stop_cleanup_task(self):
        """
        Stop the background cleanup task.
        
        Should be called during server shutdown.
        """
        if self._cleanup_task is None:
            logger.warning("[SESSION_SEM] No cleanup task to stop")
            return
        
        self._running = False
        
        # Wait for cleanup task to finish
        try:
            await asyncio.wait_for(self._cleanup_task, timeout=5.0)
        except asyncio.TimeoutError:
            logger.warning("[SESSION_SEM] Cleanup task did not stop gracefully, cancelling")
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        self._cleanup_task = None
        logger.info("[SESSION_SEM] Cleanup task stopped")
    
    def get_metrics(self) -> dict:
        """
        Get metrics about session semaphore usage.
        
        Returns:
            Dictionary with metrics
        """
        return {
            "active_sessions": len(self._semaphores),
            "total_sessions_created": self._total_sessions_created,
            "total_sessions_cleaned": self._total_sessions_cleaned,
            "max_concurrent_per_session": self._max_concurrent_per_session,
            "cleanup_interval": self._cleanup_interval,
            "inactive_timeout": self._inactive_timeout,
            "running": self._running
        }


# Global session semaphore manager instance
_session_semaphore_manager: Optional[SessionSemaphoreManager] = None


async def get_session_semaphore_manager() -> SessionSemaphoreManager:
    """
    Get or create the global session semaphore manager.
    
    Returns:
        SessionSemaphoreManager instance
    """
    global _session_semaphore_manager
    
    if _session_semaphore_manager is None:
        # Import here to avoid circular dependency
        import os
        
        max_concurrent = int(os.getenv("SESSION_MAX_CONCURRENT", "1"))
        cleanup_interval = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))
        inactive_timeout = int(os.getenv("SESSION_INACTIVE_TIMEOUT", "300"))
        
        _session_semaphore_manager = SessionSemaphoreManager(
            max_concurrent_per_session=max_concurrent,
            cleanup_interval=cleanup_interval,
            inactive_timeout=inactive_timeout
        )
        await _session_semaphore_manager.start_cleanup_task()
        logger.info("[SESSION_SEM] Global session semaphore manager initialized")
    
    return _session_semaphore_manager


def get_session_semaphore_manager_sync() -> Optional[SessionSemaphoreManager]:
    """
    Get the global session semaphore manager (synchronous version).
    
    Returns:
        SessionSemaphoreManager instance if initialized, None otherwise
        
    Note:
        This function does NOT create the manager if it doesn't exist.
        The manager must be initialized during server startup via get_session_semaphore_manager().
    """
    global _session_semaphore_manager
    return _session_semaphore_manager

