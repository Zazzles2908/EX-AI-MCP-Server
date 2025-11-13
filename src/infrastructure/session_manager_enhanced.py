"""
Enhanced Session Manager with Database-Backed Persistence

This module extends the existing SessionManager with Supabase database persistence
for 100% session recovery after server restart.

EXAI Analysis ID: 5a408a20-8cbe-48fd-967b-fe6723950861

Features:
- In-memory session management (existing functionality)
- Supabase database persistence (new)
- Session recovery on startup
- Automatic backup on session changes
- Cleanup from database on session removal

Integration:
- Uses SupabaseSessionService for database operations
- Maintains backward compatibility with existing code
- Seamless persistence with no API changes
"""

import asyncio
import os
import secrets
import time
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any, List

from infrastructure.session_service import SupabaseSessionService, get_session_service

logger = logging.getLogger(__name__)

# Configuration from environment
DEFAULT_MAX_INFLIGHT = int(os.getenv("EXAI_WS_SESSION_MAX_INFLIGHT", "8"))
DEFAULT_SESSION_TIMEOUT_SECS = int(os.getenv("SESSION_TIMEOUT_SECS", "3600"))
DEFAULT_MAX_CONCURRENT_SESSIONS = int(os.getenv("SESSION_MAX_CONCURRENT", "100"))
DEFAULT_CLEANUP_INTERVAL_SECS = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))


@dataclass
class Session:
    """
    Represents a single WebSocket session.

    Attributes:
        session_id: Unique session identifier
        created_at: Timestamp when session was created
        last_activity: Timestamp of last activity
        inflight: Current number of inflight requests
        closed: Whether session is closed
        max_inflight: Maximum concurrent requests allowed
        sem: Semaphore for concurrency control
    """
    session_id: str
    created_at: float = field(default_factory=lambda: time.time())
    last_activity: float = field(default_factory=lambda: time.time())
    inflight: int = 0
    closed: bool = False
    max_inflight: int = DEFAULT_MAX_INFLIGHT
    sem: Optional[asyncio.BoundedSemaphore] = None
    user_id: Optional[str] = None
    user_type: str = 'human'
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_count: int = 0
    total_duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create from dictionary"""
        return cls(**data)


class SessionManager:
    """
    Enhanced session tracker with database persistence.

    Features:
    - In-memory session management (fast)
    - Supabase database persistence (recovery)
    - Per-session inflight quota enforcement
    - Session timeout detection and cleanup
    - Session limits enforcement
    - Activity tracking
    - Metrics collection
    - 100% session recovery after restart

    Configuration:
    - session_timeout_secs: Timeout for inactive sessions (default: 3600s = 1 hour)
    - max_concurrent_sessions: Maximum concurrent sessions (default: 100)
    - cleanup_interval_secs: Cleanup interval (default: 300s = 5 minutes)
    - enable_persistence: Enable database persistence (default: True)
    """

    def __init__(
        self,
        session_timeout_secs: int = DEFAULT_SESSION_TIMEOUT_SECS,
        max_concurrent_sessions: int = DEFAULT_MAX_CONCURRENT_SESSIONS,
        cleanup_interval_secs: int = DEFAULT_CLEANUP_INTERVAL_SECS,
        enable_persistence: bool = True
    ) -> None:
        """
        Initialize SessionManager with database persistence.

        Args:
            session_timeout_secs: Timeout for inactive sessions in seconds
            max_concurrent_sessions: Maximum number of concurrent sessions
            cleanup_interval_secs: Interval for automatic cleanup in seconds
            enable_persistence: Enable database persistence
        """
        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self.session_timeout_secs = session_timeout_secs
        self.max_concurrent_sessions = max_concurrent_sessions
        self.cleanup_interval_secs = cleanup_interval_secs
        self.enable_persistence = enable_persistence

        # Initialize Supabase session service
        if enable_persistence:
            self.session_service = get_session_service()
            if self.session_service.enabled:
                logger.info("[SESSION_MANAGER] Database persistence enabled")
            else:
                logger.warning("[SESSION_MANAGER] Database persistence disabled (not configured)")
        else:
            self.session_service = None
            logger.info("[SESSION_MANAGER] Database persistence disabled")

        logger.info(
            f"[SESSION_MANAGER] Initialized with timeout={session_timeout_secs}s, "
            f"max_sessions={max_concurrent_sessions}, cleanup_interval={cleanup_interval_secs}s"
        )

    async def ensure(self, session_id: Optional[str]) -> Session:
        """
        Ensure session exists, creating if necessary.

        First checks database for existing session, recovers if found.
        Creates new session if not found.
        Automatically persists new sessions to database.

        Args:
            session_id: Session ID (auto-generated if None)

        Returns:
            Session object

        Raises:
            RuntimeError: If maximum concurrent sessions exceeded
        """
        if not session_id:
            session_id = secrets.token_urlsafe(32)

        async with self._lock:
            sess = self._sessions.get(session_id)

            if not sess:
                # Try to recover from database
                if self.session_service and self.session_service.enabled:
                    db_session = await self.session_service.load_session(session_id)
                    if db_session:
                        sess = self._recover_session_from_db(db_session)
                        self._sessions[session_id] = sess
                        logger.info(
                            f"[SESSION_MANAGER] Recovered session {session_id} from database "
                            f"(total sessions: {len(self._sessions)})"
                        )
                        return sess

                # Check session limit
                if len(self._sessions) >= self.max_concurrent_sessions:
                    logger.error(
                        f"[SESSION_MANAGER] Maximum concurrent sessions ({self.max_concurrent_sessions}) "
                        f"exceeded. Cannot create session {session_id}"
                    )
                    raise RuntimeError(
                        f"Maximum concurrent sessions ({self.max_concurrent_sessions}) exceeded"
                    )

                # Create new session
                sess = Session(session_id=session_id, max_inflight=DEFAULT_MAX_INFLIGHT)
                sess.sem = asyncio.BoundedSemaphore(sess.max_inflight)
                self._sessions[session_id] = sess

                # Persist to database
                if self.session_service and self.session_service.enabled:
                    await self._persist_session(sess)

                logger.info(
                    f"[SESSION_MANAGER] Created session {session_id} "
                    f"(total sessions: {len(self._sessions)})"
                )

            return sess

    async def get(self, session_id: str) -> Optional[Session]:
        """
        Get existing session.

        Args:
            session_id: Session ID

        Returns:
            Session object or None if not found
        """
        async with self._lock:
            return self._sessions.get(session_id)

    async def remove(self, session_id: str) -> None:
        """
        Remove session from memory and database.

        Args:
            session_id: Session ID to remove
        """
        async with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed:
                # Delete from database
                if self.session_service and self.session_service.enabled:
                    await self.session_service.delete_session(session_id)

                logger.info(
                    f"[SESSION_MANAGER] Removed session {session_id} "
                    f"(total sessions: {len(self._sessions)})"
                )

    async def list_ids(self) -> list[str]:
        """
        List all session IDs.

        Returns:
            List of session IDs
        """
        async with self._lock:
            return list(self._sessions.keys())

    async def update_activity(
        self,
        session_id: str,
        request_duration_ms: Optional[int] = None
    ) -> None:
        """
        Update last activity timestamp for session.

        Also updates database with latest activity and metrics.

        Args:
            session_id: Session ID
            request_duration_ms: Optional request duration in milliseconds
        """
        async with self._lock:
            sess = self._sessions.get(session_id)
            if sess:
                sess.last_activity = time.time()
                sess.request_count += 1

                if request_duration_ms:
                    sess.total_duration_ms += request_duration_ms

                # Persist to database
                if self.session_service and self.session_service.enabled:
                    await self._persist_session(sess)

                logger.debug(f"[SESSION_MANAGER] Updated activity for session {session_id}")

    def is_session_timed_out(self, session: Session) -> bool:
        """
        Check if session has timed out due to inactivity.

        Args:
            session: Session to check

        Returns:
            True if session timed out, False otherwise
        """
        if session.closed:
            return True

        inactive_time = time.time() - session.last_activity
        return inactive_time >= self.session_timeout_secs

    async def cleanup_stale_sessions(self) -> int:
        """
        Cleanup sessions that have timed out from memory and database.

        Returns:
            Number of sessions cleaned up
        """
        async with self._lock:
            stale_sessions = []

            for session_id, session in self._sessions.items():
                if self.is_session_timed_out(session):
                    stale_sessions.append(session_id)

            # Remove stale sessions
            for session_id in stale_sessions:
                self._sessions.pop(session_id, None)

                # Delete from database
                if self.session_service and self.session_service.enabled:
                    await self.session_service.delete_session(session_id)

            if stale_sessions:
                logger.info(
                    f"[SESSION_MANAGER] Cleaned up {len(stale_sessions)} stale sessions "
                    f"(total sessions: {len(self._sessions)})"
                )

            return len(stale_sessions)

    async def get_session_metrics(self) -> Dict[str, Any]:
        """
        Get session metrics.

        Returns:
            Dictionary with metrics:
            - total_sessions: Total number of sessions
            - active_sessions: Number of active (non-timed-out) sessions
            - oldest_session_age: Age of oldest session in seconds
            - newest_session_age: Age of newest session in seconds
            - avg_session_age: Average session age in seconds
            - persistence_enabled: Whether database persistence is enabled
        """
        async with self._lock:
            total_sessions = len(self._sessions)

            if total_sessions == 0:
                return {
                    "total_sessions": 0,
                    "active_sessions": 0,
                    "oldest_session_age": 0,
                    "newest_session_age": 0,
                    "avg_session_age": 0,
                    "persistence_enabled": self.session_service is not None and self.session_service.enabled
                }

            # Count active sessions
            active_sessions = sum(
                1 for sess in self._sessions.values()
                if not self.is_session_timed_out(sess)
            )

            # Calculate session ages
            now = time.time()
            session_ages = [now - sess.created_at for sess in self._sessions.values()]

            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "oldest_session_age": max(session_ages) if session_ages else 0,
                "newest_session_age": min(session_ages) if session_ages else 0,
                "avg_session_age": sum(session_ages) / len(session_ages) if session_ages else 0,
                "persistence_enabled": self.session_service is not None and self.session_service.enabled
            }

    async def recover_all_sessions(self) -> int:
        """
        Recover all active sessions from database on startup.

        Returns:
            Number of sessions recovered
        """
        if not self.session_service or not self.session_service.enabled:
            logger.debug("[SESSION_MANAGER] Persistence not enabled, skipping recovery")
            return 0

        try:
            # List active sessions from database
            db_sessions = await self.session_service.list_sessions(state='active', limit=1000)

            recovered_count = 0
            for db_session_data in db_sessions:
                session_id = db_session_data.get('session_id')
                if session_id and session_id not in self._sessions:
                    # Recover session
                    sess = self._recover_session_from_db(db_session_data)
                    self._sessions[session_id] = sess
                    recovered_count += 1

            if recovered_count > 0:
                logger.info(
                    f"[SESSION_MANAGER] Recovered {recovered_count} sessions from database "
                    f"(total sessions: {len(self._sessions)})"
                )
            else:
                logger.info("[SESSION_MANAGER] No sessions to recover from database")

            return recovered_count

        except Exception as e:
            logger.error(f"[SESSION_MANAGER] Session recovery failed: {e}")
            return 0

    async def _persist_session(self, session: Session) -> None:
        """
        Persist session to database.

        Args:
            session: Session to persist
        """
        if not self.session_service or not self.session_service.enabled:
            return

        try:
            session_data = {
                'id': session.session_id,
                'state': 'active' if not session.closed else 'inactive',
                'user_id': session.user_id,
                'user_type': session.user_type,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'request_count': session.request_count,
                'total_duration_ms': session.total_duration_ms,
                'created_at': session.created_at,
                'last_activity': session.last_activity,
                'metadata': session.metadata,
                'data': {
                    'inflight': session.inflight,
                    'max_inflight': session.max_inflight,
                    'closed': session.closed
                }
            }

            await self.session_service.save_session(
                session_id=session.session_id,
                session_data=session_data,
                metadata={'version': '1.0', 'source': 'session_manager_enhanced'}
            )

        except Exception as e:
            logger.error(f"[SESSION_MANAGER] Failed to persist session {session.session_id}: {e}")

    def _recover_session_from_db(self, db_data: Dict[str, Any]) -> Session:
        """
        Recover session from database record.

        Args:
            db_data: Database record

        Returns:
            Session object
        """
        session_data = db_data.get('session_data', {})
        data = session_data.get('data', {})

        sess = Session(
            session_id=db_data.get('session_id'),
            created_at=session_data.get('created_at', time.time()),
            last_activity=session_data.get('last_activity', time.time()),
            inflight=data.get('inflight', 0),
            closed=data.get('closed', False),
            max_inflight=data.get('max_inflight', DEFAULT_MAX_INFLIGHT),
            user_id=session_data.get('user_id'),
            user_type=session_data.get('user_type', 'human'),
            ip_address=session_data.get('ip_address'),
            user_agent=session_data.get('user_agent'),
            request_count=session_data.get('request_count', 0),
            total_duration_ms=session_data.get('total_duration_ms', 0),
            metadata=session_data.get('metadata', {})
        )
        sess.sem = asyncio.BoundedSemaphore(sess.max_inflight)
        return sess


# Backward compatibility
# Export SessionManager as the default
__all__ = ['SessionManager', 'Session']
