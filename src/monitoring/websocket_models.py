"""
WebSocket Models - Data structures for WebSocket operations.

This module defines the core data structures used throughout the
WebSocket resilience system including connection state and message queuing.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from websockets.server import WebSocketServerProtocol


@dataclass
class ConnectionState:
    """
    Tracks the state of a WebSocket connection.

    This data class maintains all relevant information about an active
    WebSocket connection including activity tracking, retry state, and
    message queuing.
    """
    websocket: WebSocketServerProtocol
    last_message_time: float = field(default_factory=time.time)
    is_connected: bool = True
    retry_count: int = 0
    pending_messages: asyncio.Queue = field(
        default_factory=lambda: asyncio.Queue(maxsize=1000)
    )

    def update_activity(self):
        """Update last activity timestamp."""
        self.last_message_time = time.time()

    def is_timeout(self, timeout_seconds: float = 120.0) -> bool:
        """
        Check if connection has timed out.

        Args:
            timeout_seconds: Connection timeout in seconds (default: 120)

        Returns:
            True if connection has timed out, False otherwise
        """
        return (time.time() - self.last_message_time) > timeout_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection state to dictionary for logging/stats."""
        return {
            "is_connected": self.is_connected,
            "retry_count": self.retry_count,
            "last_activity": self.last_message_time,
            "queue_size": self.pending_messages.qsize(),
            "is_timeout": self.is_timeout()
        }


@dataclass
class QueuedMessage:
    """
    Represents a message in the pending queue.

    This data class wraps messages with metadata needed for reliable
    delivery including enqueue time and retry tracking.
    """
    message: dict
    enqueued_at: float = field(default_factory=time.time)
    retry_count: int = 0

    def is_expired(self, ttl_seconds: float = 300.0) -> bool:
        """
        Check if message has exceeded TTL.

        Args:
            ttl_seconds: Message TTL in seconds (default: 300/5 minutes)

        Returns:
            True if message is expired, False otherwise
        """
        return (time.time() - self.enqueued_at) > ttl_seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert queued message to dictionary for logging/stats."""
        return {
            "message": self.message,
            "enqueued_at": self.enqueued_at,
            "retry_count": self.retry_count,
            "is_expired": self.is_expired(),
            "age_seconds": time.time() - self.enqueued_at
        }


__all__ = [
    "ConnectionState",
    "QueuedMessage"
]
