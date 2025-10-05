"""
Session Management with Lifecycle Tracking

This module provides session lifecycle management with:
- Automatic session cleanup on disconnect
- Session timeout for inactive sessions
- Session limits enforcement
- Session metrics collection
- Activity tracking

Configuration (via environment variables):
- EXAI_WS_SESSION_MAX_INFLIGHT: Max concurrent requests per session (default: 8)
- SESSION_TIMEOUT_SECS: Session timeout in seconds (default: 3600 = 1 hour)
- SESSION_MAX_CONCURRENT: Maximum concurrent sessions (default: 100)
- SESSION_CLEANUP_INTERVAL: Cleanup interval in seconds (default: 300 = 5 minutes)

Usage:
    from src.daemon.session_manager import SessionManager

    manager = SessionManager()

    # Create session
    session = await manager.ensure("session-id")

    # Update activity
    await manager.update_activity("session-id")

    # Cleanup stale sessions
    cleaned = await manager.cleanup_stale_sessions()

    # Get metrics
    metrics = await manager.get_session_metrics()
"""

import asyncio
import os
import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

# Configuration from environment
DEFAULT_MAX_INFLIGHT = int(os.getenv("EXAI_WS_SESSION_MAX_INFLIGHT", "8"))
DEFAULT_SESSION_TIMEOUT_SECS = int(os.getenv("SESSION_TIMEOUT_SECS", "3600"))  # 1 hour
DEFAULT_MAX_CONCURRENT_SESSIONS = int(os.getenv("SESSION_MAX_CONCURRENT", "100"))
DEFAULT_CLEANUP_INTERVAL_SECS = int(os.getenv("SESSION_CLEANUP_INTERVAL", "300"))  # 5 minutes


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


class SessionManager:
    """
    Session tracker with lifecycle management.

    Features:
    - Per-session inflight quota enforcement
    - Session timeout detection and cleanup
    - Session limits enforcement
    - Activity tracking
    - Metrics collection

    Configuration:
    - session_timeout_secs: Timeout for inactive sessions (default: 3600s = 1 hour)
    - max_concurrent_sessions: Maximum concurrent sessions (default: 100)
    - cleanup_interval_secs: Cleanup interval (default: 300s = 5 minutes)
    """

    def __init__(
        self,
        session_timeout_secs: int = DEFAULT_SESSION_TIMEOUT_SECS,
        max_concurrent_sessions: int = DEFAULT_MAX_CONCURRENT_SESSIONS,
        cleanup_interval_secs: int = DEFAULT_CLEANUP_INTERVAL_SECS
    ) -> None:
        """
        Initialize SessionManager.

        Args:
            session_timeout_secs: Timeout for inactive sessions in seconds
            max_concurrent_sessions: Maximum number of concurrent sessions
            cleanup_interval_secs: Interval for automatic cleanup in seconds
        """
        self._sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()
        self.session_timeout_secs = session_timeout_secs
        self.max_concurrent_sessions = max_concurrent_sessions
        self.cleanup_interval_secs = cleanup_interval_secs

        logger.info(
            f"[SESSION_MANAGER] Initialized with timeout={session_timeout_secs}s, "
            f"max_sessions={max_concurrent_sessions}, cleanup_interval={cleanup_interval_secs}s"
        )

    async def ensure(self, session_id: Optional[str]) -> Session:
        """
        Ensure session exists, creating if necessary.

        Args:
            session_id: Session ID (auto-generated if None)

        Returns:
            Session object

        Raises:
            RuntimeError: If maximum concurrent sessions exceeded
        """
        if not session_id:
            session_id = str(uuid.uuid4())

        async with self._lock:
            sess = self._sessions.get(session_id)
            if not sess:
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
        Remove session.

        Args:
            session_id: Session ID to remove
        """
        async with self._lock:
            removed = self._sessions.pop(session_id, None)
            if removed:
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

    async def update_activity(self, session_id: str) -> None:
        """
        Update last activity timestamp for session.

        Args:
            session_id: Session ID
        """
        async with self._lock:
            sess = self._sessions.get(session_id)
            if sess:
                sess.last_activity = time.time()
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
        Cleanup sessions that have timed out.

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
        """
        async with self._lock:
            total_sessions = len(self._sessions)

            if total_sessions == 0:
                return {
                    "total_sessions": 0,
                    "active_sessions": 0,
                    "oldest_session_age": 0,
                    "newest_session_age": 0,
                    "avg_session_age": 0
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
                "avg_session_age": sum(session_ages) / len(session_ages) if session_ages else 0
            }

