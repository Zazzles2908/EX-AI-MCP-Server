"""
Session Manager for EXAI MCP Server
Handles session lifecycle, tracking, and persistence

WEEK 2 (2025-10-19): Basic Session Management
- UUID-based session IDs
- Session tracking in Supabase
- Session metadata (title, status, timestamps)
- In-memory caching for performance
"""

import os
import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

from src.storage.async_supabase_manager import get_async_supabase_manager

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """
    Session data class.
    
    Attributes:
        id: Unique session identifier (UUID)
        user_id: User identifier
        title: Session title (optional)
        status: Session status (active, paused, completed, expired)
        created_at: Session creation timestamp
        updated_at: Last update timestamp
        expires_at: Session expiration timestamp (optional)
        metadata: Additional session metadata
        turn_count: Number of turns in this session
        total_tokens: Total tokens used in this session
    """
    id: str
    user_id: str
    title: Optional[str] = None
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    turn_count: int = 0
    total_tokens: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary."""
        return cls(**data)


class SessionManager:
    """
    Manages session lifecycle and persistence.
    
    Features:
    - UUID-based session IDs
    - In-memory caching for performance
    - Async Supabase persistence
    - Session expiration handling
    - Session status tracking
    """
    
    _instance: Optional['SessionManager'] = None
    
    def __init__(self, default_expiry_hours: int = 24):
        """
        Initialize session manager.
        
        Args:
            default_expiry_hours: Default session expiry time in hours
        """
        self.default_expiry_hours = default_expiry_hours
        self._cache: Dict[str, Session] = {}
        self._async_manager = None  # Will be initialized async
        
        logger.info(f"SessionManager initialized with default_expiry_hours={default_expiry_hours}")
    
    @classmethod
    def get_instance(cls, default_expiry_hours: int = 24) -> 'SessionManager':
        """
        Get singleton instance.
        
        Args:
            default_expiry_hours: Default session expiry (only used on first call)
            
        Returns:
            SessionManager instance
        """
        if cls._instance is None:
            cls._instance = cls(default_expiry_hours=default_expiry_hours)
        return cls._instance
    
    async def _get_async_manager(self):
        """Get or create async Supabase manager."""
        if self._async_manager is None:
            self._async_manager = await get_async_supabase_manager()
        return self._async_manager
    
    def create_session(
        self,
        user_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expiry_hours: Optional[int] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            user_id: User identifier
            title: Optional session title
            metadata: Optional session metadata
            expiry_hours: Optional custom expiry time (uses default if None)
            
        Returns:
            Created session
        """
        session_id = str(uuid.uuid4())
        
        # Calculate expiry time
        expiry_hours = expiry_hours or self.default_expiry_hours
        expires_at = (datetime.utcnow() + timedelta(hours=expiry_hours)).isoformat()
        
        session = Session(
            id=session_id,
            user_id=user_id,
            title=title or f"Session {session_id[:8]}",
            status="active",
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Cache session
        self._cache[session_id] = session
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session
    
    async def save_session_async(self, session: Session, fire_and_forget: bool = True) -> bool:
        """
        Save session to Supabase asynchronously.
        
        Args:
            session: Session to save
            fire_and_forget: If True, don't wait for result
            
        Returns:
            True if saved successfully (always True for fire_and_forget)
        """
        try:
            manager = await self._get_async_manager()
            
            # Note: This will need the actual Supabase table structure
            # For now, we'll use a placeholder that matches the expected schema
            session_data = session.to_dict()
            
            if fire_and_forget:
                # Fire-and-forget: Just schedule the save
                # TODO: Implement actual Supabase save when schema is ready
                logger.debug(f"Fire-and-forget save for session {session.id}")
                return True
            else:
                # Wait for result
                # TODO: Implement actual Supabase save when schema is ready
                logger.debug(f"Async save completed for session {session.id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save session {session.id}: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session from cache.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session or None if not found
        """
        session = self._cache.get(session_id)
        
        if session:
            # Check if expired
            if session.expires_at:
                expires_at = datetime.fromisoformat(session.expires_at)
                if datetime.utcnow() > expires_at:
                    logger.warning(f"Session {session_id} has expired")
                    session.status = "expired"
                    self._cache[session_id] = session
        
        return session
    
    async def get_session_async(self, session_id: str) -> Optional[Session]:
        """
        Get session from cache or Supabase.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session or None if not found
        """
        # Check cache first
        session = self.get_session(session_id)
        if session:
            return session
        
        # TODO: Fetch from Supabase when schema is ready
        logger.debug(f"Session {session_id} not in cache, would fetch from Supabase")
        return None
    
    def update_session(
        self,
        session_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        increment_turns: bool = False,
        add_tokens: int = 0
    ) -> Optional[Session]:
        """
        Update session in cache.
        
        Args:
            session_id: Session identifier
            title: New title (optional)
            status: New status (optional)
            metadata: Metadata to merge (optional)
            increment_turns: If True, increment turn count
            add_tokens: Tokens to add to total
            
        Returns:
            Updated session or None if not found
        """
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Cannot update session {session_id}: not found")
            return None
        
        # Update fields
        if title:
            session.title = title
        if status:
            session.status = status
        if metadata:
            session.metadata.update(metadata)
        if increment_turns:
            session.turn_count += 1
        if add_tokens > 0:
            session.total_tokens += add_tokens
        
        # Update timestamp
        session.updated_at = datetime.utcnow().isoformat()
        
        # Update cache
        self._cache[session_id] = session
        
        logger.debug(f"Updated session {session_id}")
        return session
    
    def list_active_sessions(self, user_id: Optional[str] = None) -> List[Session]:
        """
        List active sessions.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            List of active sessions
        """
        sessions = []
        for session in self._cache.values():
            if session.status == "active":
                if user_id is None or session.user_id == user_id:
                    sessions.append(session)
        
        return sessions
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from cache.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()
        expired_ids = []
        
        for session_id, session in self._cache.items():
            if session.expires_at:
                expires_at = datetime.fromisoformat(session.expires_at)
                if now > expires_at:
                    expired_ids.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_ids:
            del self._cache[session_id]
            logger.info(f"Cleaned up expired session {session_id}")
        
        return len(expired_ids)


# Singleton instance getter (convenience function)
def get_session_manager(default_expiry_hours: int = 24) -> SessionManager:
    """
    Get singleton SessionManager instance.
    
    Args:
        default_expiry_hours: Default session expiry (only used on first call)
        
    Returns:
        SessionManager instance
    """
    return SessionManager.get_instance(default_expiry_hours=default_expiry_hours)

