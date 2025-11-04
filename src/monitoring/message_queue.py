"""
Message Queue - Abstract and in-memory message queue implementations.

This module provides message queuing infrastructure for WebSocket operations
including an abstract base class and an in-memory implementation with
async support.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.monitoring.websocket_models import QueuedMessage
from src.monitoring.websocket_exceptions import MessageQueueError


logger = logging.getLogger(__name__)

# Configuration constants (extracted for easier testing)
DEFAULT_MAX_QUEUE_SIZE = 1000
DEFAULT_MESSAGE_TTL = 300.0  # 5 minutes


class MessageQueue(ABC):
    """
    Abstract base class for message queue implementations.

    This interface defines the contract for message queuing systems
    used by the ResilientWebSocketManager to store and retrieve
    pending messages.
    """

    @abstractmethod
    async def enqueue(self, client_id: str, message: dict) -> bool:
        """
        Add message to queue.

        Args:
            client_id: Unique identifier for the client
            message: Message dictionary to enqueue

        Returns:
            True if successful, False if queue is full or other error
        """
        pass

    @abstractmethod
    async def dequeue(self, client_id: str) -> Optional[QueuedMessage]:
        """
        Get next message from queue.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Next QueuedMessage or None if queue is empty
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        Remove expired messages.

        Returns:
            Count of removed messages
        """
        pass

    @abstractmethod
    def get_queue_size(self, client_id: str) -> int:
        """
        Get current queue size for client.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Number of messages in queue (0 if empty or not found)
        """
        pass

    @abstractmethod
    def get_total_queue_size(self) -> int:
        """
        Get total size of all queues.

        Returns:
            Total number of messages across all client queues
        """
        pass

    @abstractmethod
    def get_client_ids(self) -> list:
        """
        Get list of all client IDs with queues.

        Returns:
            List of client IDs
        """
        pass


class InMemoryMessageQueue(MessageQueue):
    """
    In-memory implementation of message queue.

    This implementation uses asyncio.Queue for thread-safe async operations
    with client-scoped queues managed internally.
    """

    def __init__(self, max_queue_size: int = DEFAULT_MAX_QUEUE_SIZE):
        """
        Initialize in-memory message queue.

        Args:
            max_queue_size: Maximum size for each client queue
        """
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
        self._max_queue_size = max_queue_size
        logger.info(f"Initialized InMemoryMessageQueue with max_queue_size={max_queue_size}")

    async def enqueue(self, client_id: str, message: dict) -> bool:
        """
        Add message to queue.

        Args:
            client_id: Unique identifier for the client
            message: Message dictionary to enqueue

        Returns:
            True if successful, False if queue is full
        """
        async with self._lock:
            # Create queue for client if it doesn't exist
            if client_id not in self._queues:
                self._queues[client_id] = asyncio.Queue(maxsize=self._max_queue_size)

            queue = self._queues[client_id]

            # Handle full queue by dropping oldest message
            if queue.full():
                logger.warning(
                    f"Queue full for client {client_id}, dropping oldest message. "
                    f"Queue size: {queue.qsize()}"
                )
                try:
                    queue.get_nowait()  # Drop oldest
                except asyncio.QueueEmpty:
                    pass

            queued_msg = QueuedMessage(message=message)
            try:
                await queue.put(queued_msg)
                logger.debug(
                    f"Enqueued message for client {client_id}, "
                    f"queue size: {queue.qsize()}"
                )
                return True
            except asyncio.QueueFull:
                logger.error(f"Failed to enqueue message for client {client_id}")
                return False

    async def dequeue(self, client_id: str) -> Optional[QueuedMessage]:
        """
        Get next message from queue.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Next QueuedMessage or None if queue is empty
        """
        async with self._lock:
            if client_id not in self._queues:
                return None

            queue = self._queues[client_id]
            try:
                msg = queue.get_nowait()

                # Check if expired
                if msg.is_expired(DEFAULT_MESSAGE_TTL):
                    logger.debug(
                        f"Discarding expired message for client {client_id}, "
                        f"age: {msg.age_seconds:.1f}s"
                    )
                    return await self.dequeue(client_id)  # Try next message

                return msg
            except asyncio.QueueEmpty:
                return None

    async def cleanup_expired(self) -> int:
        """
        Remove expired messages from all queues.

        Returns:
            Count of removed messages
        """
        removed_count = 0
        async with self._lock:
            for client_id, queue in list(self._queues.items()):
                temp_queue = asyncio.Queue(maxsize=self._max_queue_size)
                while not queue.empty():
                    try:
                        msg = queue.get_nowait()
                        if not msg.is_expired(DEFAULT_MESSAGE_TTL):
                            await temp_queue.put(msg)
                        else:
                            removed_count += 1
                    except asyncio.QueueEmpty:
                        break

                # Replace old queue with cleaned queue
                self._queues[client_id] = temp_queue

                # Remove empty queues
                if temp_queue.empty():
                    del self._queues[client_id]

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired messages")
        return removed_count

    def get_queue_size(self, client_id: str) -> int:
        """
        Get current queue size for client.

        Args:
            client_id: Unique identifier for the client

        Returns:
            Number of messages in queue (0 if empty or not found)
        """
        if client_id not in self._queues:
            return 0
        return self._queues[client_id].qsize()

    def get_total_queue_size(self) -> int:
        """
        Get total size of all queues.

        Returns:
            Total number of messages across all client queues
        """
        # This is a read-only operation, no lock needed for queue.qsize()
        # The lock is only needed for queue modifications (enqueue/dequeue)
        return sum(queue.qsize() for queue in self._queues.values())

    def get_client_ids(self) -> list:
        """
        Get list of all client IDs with queues.

        Returns:
            List of client IDs
        """
        # This is a read-only operation, no lock needed
        # The lock is only needed for queue modifications (enqueue/dequeue)
        return list(self._queues.keys())

    def to_dict(self) -> Dict[str, Any]:
        """
        Get queue statistics as dictionary.

        Returns:
            Dictionary with queue statistics
        """
        return {
            "total_queues": len(self._queues),
            "total_messages": self.get_total_queue_size(),
            "client_queues": {
                client_id: queue.qsize()
                for client_id, queue in self._queues.items()
            }
        }


__all__ = [
    "MessageQueue",
    "InMemoryMessageQueue"
]
