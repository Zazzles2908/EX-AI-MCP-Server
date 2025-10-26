"""
Multi-User Session Manager for JWT-Based Authentication

Handles user session lifecycle with Supabase backend:
- Session creation with cryptographically secure IDs
- Session validation with optimistic locking
- Automatic cleanup of expired sessions
- User context tracking

Author: EXAI Agent
Date: 2025-10-27
Based on: EXAI QA Review (continuation_id: qa-review-2025-10-27)
"""

import asyncio
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MultiUserSessionManager:
    """
    Manages user sessions for multi-user MCP connections with JWT authentication.
    
    Features:
    - Cryptographically secure session ID generation
    - Optimistic locking for concurrent updates
    - Automatic cleanup of expired sessions
    - Session binding to client metadata
    """
    
    def __init__(self, supabase_client, session_timeout: int = 3600):
        """
        Initialize MultiUserSessionManager.
        
        Args:
            supabase_client: Supabase client instance
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.db = supabase_client
        self.timeout = session_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        
        logger.info(f"MultiUserSessionManager initialized with {session_timeout}s timeout")
    
    async def start(self):
        """Start background cleanup task"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
            logger.info("Multi-user session cleanup task started")
    
    async def stop(self):
        """Stop background cleanup task"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Multi-user session cleanup task stopped")
    
    async def create_session(
        self, 
        user_id: str, 
        client_id: str, 
        client_ip: str = "unknown",
        user_agent: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Create a new session for a user.
        
        Args:
            user_id: User ID from JWT
            client_id: Client identifier
            client_ip: Client IP address
            user_agent: Client user agent string
            
        Returns:
            Session data dictionary
            
        Raises:
            RuntimeError: If session creation fails
        """
        try:
            # Generate cryptographically secure session ID
            session_id = secrets.token_urlsafe(32)
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(seconds=self.timeout)
            
            # Create session in database
            result = self.db.table('mcp_sessions').insert({
                'user_id': user_id,
                'session_id': session_id,
                'connection_status': 'connected',
                'expires_at': expires_at.isoformat(),
                'version': 1,
                'metadata': {
                    'client_id': client_id,
                    'client_ip': client_ip,
                    'user_agent': user_agent,
                    'created_at': datetime.utcnow().isoformat()
                }
            }).execute()
            
            if not result.data or len(result.data) == 0:
                raise RuntimeError("Session creation returned no data")
            
            session = result.data[0]
            
            # Cache session locally
            self._active_sessions[session_id] = session
            
            logger.info(f"Created session {session_id[:8]}... for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session for user {user_id}: {e}")
            raise RuntimeError(f"Session creation failed: {e}")
    
    async def validate_session(
        self, 
        session_id: str, 
        user_id: str,
        update_activity: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a session and optionally update last_active.
        
        Args:
            session_id: Session ID to validate
            user_id: Expected user ID
            update_activity: Whether to update last_active timestamp
            
        Returns:
            Session data if valid, None otherwise
        """
        try:
            # Check local cache first
            if session_id in self._active_sessions:
                cached_session = self._active_sessions[session_id]
                
                # Verify user_id matches
                if cached_session.get('user_id') != user_id:
                    logger.warning(f"Session {session_id[:8]}... user_id mismatch")
                    return None
                
                # Check expiration
                expires_at = datetime.fromisoformat(cached_session['expires_at'])
                if expires_at < datetime.utcnow():
                    logger.info(f"Session {session_id[:8]}... expired (cached)")
                    await self._cleanup_session(cached_session['id'])
                    return None
            
            # Query database
            result = self.db.table('mcp_sessions').select('*').eq(
                'session_id', session_id
            ).eq('user_id', user_id).execute()
            
            if not result.data or len(result.data) == 0:
                logger.warning(f"Session {session_id[:8]}... not found")
                return None
            
            session = result.data[0]
            
            # Check expiration
            expires_at = datetime.fromisoformat(session['expires_at'])
            if expires_at < datetime.utcnow():
                logger.info(f"Session {session_id[:8]}... expired")
                await self._cleanup_session(session['id'])
                return None
            
            # Update last_active with optimistic locking
            if update_activity:
                update_result = self.db.table('mcp_sessions').update({
                    'last_active': datetime.utcnow().isoformat(),
                    'version': session['version'] + 1
                }).eq('id', session['id']).eq('version', session['version']).execute()
                
                if not update_result.data or len(update_result.data) == 0:
                    # Version conflict - session was updated elsewhere
                    logger.warning(f"Session {session_id[:8]}... version conflict")
                    # Re-fetch to get latest version
                    return await self.validate_session(session_id, user_id, update_activity=False)
                
                session = update_result.data[0]
            
            # Update cache
            self._active_sessions[session_id] = session
            
            return session
            
        except Exception as e:
            logger.error(f"Session validation failed for {session_id[:8]}...: {e}")
            return None
    
    async def update_session_status(
        self, 
        session_id: str, 
        status: str
    ) -> bool:
        """
        Update session connection status.
        
        Args:
            session_id: Session ID
            status: New status ('connected', 'disconnected', 'error')
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            result = self.db.table('mcp_sessions').update({
                'connection_status': status,
                'last_active': datetime.utcnow().isoformat()
            }).eq('session_id', session_id).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Updated session {session_id[:8]}... status to {status}")
                
                # Update cache
                if session_id in self._active_sessions:
                    self._active_sessions[session_id]['connection_status'] = status
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update session status: {e}")
            return False
    
    async def _cleanup_session(self, session_id: str):
        """Delete a specific session"""
        try:
            self.db.table('mcp_sessions').delete().eq('id', session_id).execute()
            
            # Remove from cache
            for sid, session in list(self._active_sessions.items()):
                if session.get('id') == session_id:
                    del self._active_sessions[sid]
                    break
                    
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions"""
        logger.info("Starting multi-user session cleanup background task")
        
        while True:
            try:
                # Sleep first to avoid immediate cleanup on startup
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Delete expired sessions
                result = self.db.table('mcp_sessions').delete().lt(
                    'expires_at', datetime.utcnow().isoformat()
                ).execute()
                
                if result.data and len(result.data) > 0:
                    count = len(result.data)
                    logger.info(f"Cleaned up {count} expired sessions")
                    
                    # Clear from cache
                    expired_ids = {s['session_id'] for s in result.data}
                    for sid in list(self._active_sessions.keys()):
                        if sid in expired_ids:
                            del self._active_sessions[sid]
                
            except asyncio.CancelledError:
                logger.info("Multi-user session cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Multi-user session cleanup failed: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error
    
    async def get_user_sessions(self, user_id: str) -> list:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active session dictionaries
        """
        try:
            result = self.db.table('mcp_sessions').select('*').eq(
                'user_id', user_id
            ).eq('connection_status', 'connected').execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    async def disconnect_session(self, session_id: str):
        """
        Disconnect a session (mark as disconnected, don't delete).
        
        Args:
            session_id: Session ID to disconnect
        """
        await self.update_session_status(session_id, 'disconnected')

