"""
WebSocket Session Handler

Handles session lifecycle management and periodic cleanup.
Extracted from ws_server.py as part of Week 3 Fix #15 (2025-10-21).

This module contains:
- SessionHandler class - Session lifecycle management
- Periodic session cleanup task
- Session activity tracking
"""

import asyncio
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


class SessionHandler:
    """
    Handles WebSocket session lifecycle and cleanup.
    
    Provides:
    - Session creation and removal
    - Session activity tracking
    - Periodic cleanup of stale sessions
    """
    
    def __init__(self, session_manager):
        """
        Initialize session handler.
        
        Args:
            session_manager: SessionManager instance
        """
        self.session_manager = session_manager
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def create_session(self, session_id: str):
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Session object
        """
        return await self.session_manager.ensure(session_id)
    
    async def remove_session(self, session_id: str) -> None:
        """
        Remove a session.
        
        Args:
            session_id: Session identifier to remove
        """
        try:
            await self.session_manager.remove(session_id)
        except Exception as e:
            logger.warning(f"Failed to remove session {session_id}: {e}")
    
    async def update_activity(self, session_id: str) -> None:
        """
        Update session activity timestamp.
        
        Args:
            session_id: Session identifier
        """
        try:
            await self.session_manager.update_activity(session_id)
        except Exception as e:
            logger.debug(f"Failed to update activity for session {session_id}: {e}")
    
    async def list_session_ids(self) -> list[str]:
        """
        Get list of active session IDs.
        
        Returns:
            List of session IDs
        """
        try:
            return await self.session_manager.list_ids()
        except Exception as e:
            logger.debug(f"Failed to list session IDs: {e}")
            return []
    
    async def start_periodic_cleanup(self, stop_event: asyncio.Event) -> None:
        """
        Start periodic session cleanup task.
        
        Week 2 Fix #12 (2025-10-21): Cleanup stale sessions to prevent memory leaks.
        Removes sessions that have exceeded their timeout period due to inactivity.
        
        Args:
            stop_event: Event to signal task shutdown
        """
        cleanup_interval = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))  # 5 minutes default
        
        logger.info(f"[SESSION_CLEANUP] Starting periodic cleanup (interval: {cleanup_interval}s)")
        
        while not stop_event.is_set():
            try:
                cleaned = await self.session_manager.cleanup_stale_sessions()
                if cleaned > 0:
                    logger.info(f"[SESSION_CLEANUP] Cleaned up {cleaned} stale sessions")
            except Exception as e:
                logger.error(f"[SESSION_CLEANUP] Error during cleanup: {e}", exc_info=True)
            
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=cleanup_interval)
            except asyncio.TimeoutError:
                continue
        
        logger.info("[SESSION_CLEANUP] Periodic cleanup task stopped")
    
    def start_cleanup_task(self, stop_event: asyncio.Event) -> asyncio.Task:
        """
        Start the cleanup task and return the task object.
        
        Args:
            stop_event: Event to signal task shutdown
            
        Returns:
            Cleanup task
        """
        self.cleanup_task = asyncio.create_task(self.start_periodic_cleanup(stop_event))
        return self.cleanup_task
    
    async def stop_cleanup_task(self) -> None:
        """Stop the cleanup task if running."""
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

