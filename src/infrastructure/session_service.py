"""
Supabase Session Service - Database-Backed Session Persistence

This module provides 100% session recovery after server restart by integrating
SessionManager with Supabase database storage.

EXAI Analysis ID: 5a408a20-8cbe-48fd-967b-fe6723950861

Architecture:
- Stores session state in public.sessions table
- Enables session recovery on startup
- Provides CRUD operations for session persistence
- Integrates seamlessly with existing SessionManager

Features:
- UUID primary key for scalability
- Session state tracking (active, inactive, expired)
- User metadata and request metrics
- Automatic timestamp management
- JSONB flexibility for session data
"""

import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from uuid import uuid4

from supabase import Client

logger = logging.getLogger(__name__)


class SupabaseSessionService:
    """
    Session persistence service via Supabase

    Provides database-backed session storage for 100% recovery after restart.
    Integrates with SessionManager to persist and recover session state.

    Usage:
        session_service = SupabaseSessionService()
        await session_service.save_session(session_id, session_data)
        loaded = await session_service.load_session(session_id)
    """

    def __init__(self, client: Optional[Client] = None):
        """
        Initialize Supabase session service

        Args:
            client: Optional Supabase client (uses singleton if not provided)
        """
        self._client = client
        self._enabled = True
        self._session_table = 'sessions'

        # Validate configuration
        if not self._client:
            try:
                from src.storage.storage_manager import get_storage_manager
                storage = get_storage_manager()
                if storage.enabled:
                    self._client = storage.get_client()
                    logger.info("[SESSION_SERVICE] Initialized with Supabase client")
                else:
                    self._enabled = False
                    logger.warning("[SESSION_SERVICE] Supabase not configured, disabled")
            except Exception as e:
                self._enabled = False
                logger.error(f"[SESSION_SERVICE] Initialization failed: {e}")

    @property
    def enabled(self) -> bool:
        """Check if session service is enabled"""
        return self._enabled and self._client is not None

    async def save_session(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save session to Supabase for persistence

        Args:
            session_id: Unique session identifier
            session_data: Session state data
            metadata: Optional additional metadata

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("[SESSION_SERVICE] Service not enabled, skipping save")
            return False

        try:
            # Prepare session record
            session_record = {
                'session_id': session_id,
                'session_data': session_data,
                'session_state': session_data.get('state', 'active'),
                'user_id': session_data.get('user_id'),
                'user_type': session_data.get('user_type', 'human'),
                'ip_address': session_data.get('ip_address'),
                'user_agent': session_data.get('user_agent'),
                'request_count': session_data.get('request_count', 0),
                'total_duration_ms': session_data.get('total_duration_ms'),
                'last_activity_at': datetime.now(timezone.utc).isoformat(),
                'metadata': metadata or {
                    'version': '1.0',
                    'schema': 'standard',
                    'source': 'session_manager'
                }
            }

            # Upsert session (insert or update)
            result = self._client.table(self._session_table).upsert(
                session_record,
                on_conflict='session_id'
            ).execute()

            if result.data:
                logger.debug(f"[SESSION_SERVICE] Saved session {session_id[:8]}...")
                return True
            else:
                logger.error(f"[SESSION_SERVICE] Failed to save session {session_id}")
                return False

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] Save failed for {session_id}: {e}")
            return False

    async def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session from Supabase for recovery

        Args:
            session_id: Unique session identifier

        Returns:
            Session data dict if found, None otherwise
        """
        if not self.enabled:
            logger.debug("[SESSION_SERVICE] Service not enabled, skipping load")
            return None

        try:
            result = self._client.table(self._session_table).select('*').eq(
                'session_id', session_id
            ).execute()

            if result.data and len(result.data) > 0:
                session_record = result.data[0]
                logger.debug(f"[SESSION_SERVICE] Loaded session {session_id[:8]}...")
                return session_record
            else:
                logger.debug(f"[SESSION_SERVICE] Session not found: {session_id[:8]}...")
                return None

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] Load failed for {session_id}: {e}")
            return None

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session from Supabase

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("[SESSION_SERVICE] Service not enabled, skipping delete")
            return False

        try:
            result = self._client.table(self._session_table).delete().eq(
                'session_id', session_id
            ).execute()

            if result.data:
                logger.debug(f"[SESSION_SERVICE] Deleted session {session_id[:8]}...")
                return True
            else:
                logger.error(f"[SESSION_SERVICE] Failed to delete session {session_id}")
                return False

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] Delete failed for {session_id}: {e}")
            return False

    async def list_sessions(
        self,
        state: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List sessions from Supabase

        Args:
            state: Optional state filter (active, inactive, expired)
            limit: Maximum number of results

        Returns:
            List of session records
        """
        if not self.enabled:
            logger.debug("[SESSION_SERVICE] Service not enabled, returning empty list")
            return []

        try:
            query = self._client.table(self._session_table).select('*')

            if state:
                query = query.eq('session_state', state)

            query = query.limit(limit)

            result = query.execute()

            if result.data:
                logger.debug(f"[SESSION_SERVICE] Listed {len(result.data)} sessions")
                return result.data
            else:
                return []

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] List failed: {e}")
            return []

    async def cleanup_expired_sessions(self, older_than_days: int = 7) -> int:
        """
        Clean up expired sessions from Supabase

        Args:
            older_than_days: Delete sessions older than this many days

        Returns:
            Number of sessions deleted
        """
        if not self.enabled:
            logger.debug("[SESSION_SERVICE] Service not enabled, skipping cleanup")
            return 0

        try:
            cutoff_date = datetime.now(timezone.utc)
            cutoff_date = cutoff_date.replace(
                day=cutoff_date.day - older_than_days
            )

            result = self._client.table(self._session_table).delete().lt(
                'last_activity_at', cutoff_date.isoformat()
            ).execute()

            count = len(result.data) if result.data else 0
            logger.info(f"[SESSION_SERVICE] Cleaned up {count} expired sessions")
            return count

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] Cleanup failed: {e}")
            return 0

    async def update_session_activity(
        self,
        session_id: str,
        request_duration_ms: Optional[int] = None
    ) -> bool:
        """
        Update session last activity timestamp

        Args:
            session_id: Unique session identifier
            request_duration_ms: Optional request duration in milliseconds

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False

        try:
            update_data = {
                'last_activity_at': datetime.now(timezone.utc).isoformat()
            }

            # Increment request count
            session = await self.load_session(session_id)
            if session:
                current_count = session.get('request_count', 0)
                update_data['request_count'] = current_count + 1

                # Update total duration if provided
                if request_duration_ms:
                    current_duration = session.get('total_duration_ms', 0)
                    update_data['total_duration_ms'] = current_duration + request_duration_ms

            result = self._client.table(self._session_table).update(
                update_data
            ).eq('session_id', session_id).execute()

            return bool(result.data)

        except Exception as e:
            logger.error(f"[SESSION_SERVICE] Activity update failed for {session_id}: {e}")
            return False

    def serialize_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Serialize session for Supabase storage

        Args:
            session: Raw session from SessionManager

        Returns:
            Serialized session data
        """
        return {
            'session_id': session.get('id'),
            'state': session.get('state', 'active'),
            'user_id': session.get('user_id'),
            'user_type': session.get('user_type', 'human'),
            'created_at': session.get('created_at'),
            'last_activity': session.get('last_activity'),
            'request_count': session.get('request_count', 0),
            'total_duration_ms': session.get('total_duration_ms', 0),
            'ip_address': session.get('ip_address'),
            'user_agent': session.get('user_agent'),
            'metadata': session.get('metadata', {}),
            'data': session.get('data', {})
        }

    def deserialize_session(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deserialize session from Supabase record

        Args:
            record: Session record from database

        Returns:
            Deserialized session for SessionManager
        """
        return {
            'id': record.get('session_id'),
            'state': record.get('session_state', 'active'),
            'user_id': record.get('user_id'),
            'user_type': record.get('user_type', 'human'),
            'created_at': record.get('created_at'),
            'last_activity': record.get('last_activity_at'),
            'request_count': record.get('request_count', 0),
            'total_duration_ms': record.get('total_duration_ms', 0),
            'ip_address': record.get('ip_address'),
            'user_agent': record.get('user_agent'),
            'metadata': record.get('metadata', {}),
            'data': record.get('session_data', {})
        }


# Global instance
_session_service = None


def get_session_service() -> SupabaseSessionService:
    """
    Get or create session service singleton

    Returns:
        SupabaseSessionService instance
    """
    global _session_service
    if _session_service is None:
        _session_service = SupabaseSessionService()
    return _session_service
