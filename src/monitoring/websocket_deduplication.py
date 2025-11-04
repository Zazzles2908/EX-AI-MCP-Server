"""
WebSocket Deduplication - Message deduplication logic.

This module provides message deduplication functionality to prevent
duplicate messages during WebSocket reconnection and retry operations.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""

import json
import time
from typing import Optional, Set, Dict


class MessageDeduplicator:
    """
    Handles message deduplication to prevent duplicate message delivery.

    This class tracks recently sent messages using unique IDs and cleans
    up expired entries to prevent memory leaks. Messages are scoped to
    individual client connections to prevent cross-connection interference.
    """

    def __init__(
        self,
        ttl_seconds: float = 300.0,
        enabled: bool = True
    ):
        """
        Initialize message deduplicator.

        Args:
            ttl_seconds: Time-to-live for message IDs in seconds (default: 300/5 minutes)
            enabled: Enable deduplication (default: True)
        """
        self._enabled = enabled
        self._ttl_seconds = ttl_seconds
        self._sent_message_ids: Set[str] = set()
        self._message_id_timestamps: Dict[str, float] = {}
        self._current_client_id: Optional[str] = None

    def set_current_client_id(self, client_id: str):
        """
        Set the current client ID for connection-scoped deduplication.

        This method should be called before sending each message to ensure
        deduplication is scoped to the correct connection.

        Args:
            client_id: Unique identifier for the current client connection
        """
        self._current_client_id = client_id

    def get_message_id(self, message: dict) -> Optional[str]:
        """
        Generate unique message ID for deduplication.

        Uses xxhash (fast + consistent) with SHA256 fallback if xxhash unavailable.
        Built-in hash() is NOT used because it's randomized per-process (security feature),
        causing false negatives in deduplication after server restarts.

        For connection-scoped deduplication, includes client_id in the hash
        to prevent cross-connection interference (e.g., hello_ack messages).

        Args:
            message: Message dictionary

        Returns:
            Unique message ID string or None if deduplication is disabled
        """
        if not self._enabled:
            return None

        # Use message ID if present, otherwise generate from content
        if "id" in message:
            return str(message["id"])

        # Generate ID from message content
        content = json.dumps(message, sort_keys=True)

        # Include client_id for connection-scoped deduplication
        if self._current_client_id:
            content = f"{self._current_client_id}:{content}"

        # Try xxhash first (fastest + consistent)
        try:
            import xxhash
            return xxhash.xxh64(content).hexdigest()
        except ImportError:
            # Fallback to SHA256 (slower but consistent)
            import hashlib
            return hashlib.sha256(content.encode()).hexdigest()

    def is_duplicate(self, message_id: Optional[str]) -> bool:
        """
        Check if message was recently sent (deduplication).

        This method:
        1. Cleans up expired message IDs
        2. Checks if the message ID has been seen recently
        3. Adds new message IDs to the tracking set
        4. Returns True if duplicate, False otherwise

        Args:
            message_id: Unique message ID to check

        Returns:
            True if message is a duplicate, False otherwise
        """
        if not message_id or not self._enabled:
            return False

        # Clean up expired message IDs
        current_time = time.time()
        expired_ids = [
            mid for mid, timestamp in self._message_id_timestamps.items()
            if current_time - timestamp > self._ttl_seconds
        ]
        for mid in expired_ids:
            self._sent_message_ids.discard(mid)
            del self._message_id_timestamps[mid]

        # Check if duplicate
        if message_id in self._sent_message_ids:
            return True

        # Mark as sent
        self._sent_message_ids.add(message_id)
        self._message_id_timestamps[message_id] = current_time
        return False

    def clear(self):
        """Clear all tracked message IDs."""
        self._sent_message_ids.clear()
        self._message_id_timestamps.clear()

    def get_stats(self) -> dict:
        """
        Get deduplication statistics.

        Returns:
            Dictionary with deduplication stats
        """
        current_time = time.time()
        expired_count = sum(
            1 for timestamp in self._message_id_timestamps.values()
            if current_time - timestamp > self._ttl_seconds
        )

        return {
            "enabled": self._enabled,
            "ttl_seconds": self._ttl_seconds,
            "total_tracked": len(self._sent_message_ids),
            "active_ids": len(self._sent_message_ids) - expired_count,
            "expired_ids": expired_count,
            "memory_usage": {
                "message_ids": len(self._sent_message_ids),
                "timestamps": len(self._message_id_timestamps)
            }
        }

    def cleanup_expired(self) -> int:
        """
        Cleanup expired message IDs.

        Returns:
            Number of expired IDs removed
        """
        current_time = time.time()
        expired_ids = [
            mid for mid, timestamp in self._message_id_timestamps.items()
            if current_time - timestamp > self._ttl_seconds
        ]

        for mid in expired_ids:
            self._sent_message_ids.discard(mid)
            del self._message_id_timestamps[mid]

        return len(expired_ids)


__all__ = [
    "MessageDeduplicator"
]
