"""
Resilient WebSocket Manager for handling connection failures and message queuing.

This module provides a robust WebSocket communication layer with:
- Pending message queue for disconnected clients
- Automatic retry with exponential backoff
- Connection timeout detection
- Message TTL (300s for pending messages)

Created: 2025-10-19
Phase: Week 1 Day 1-2 - WebSocket Resilience
"""

import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

logger = logging.getLogger(__name__)

# Configuration constants
MESSAGE_TTL_SECONDS = 300  # 5 minutes
MAX_RETRY_DELAY = 60.0  # 1 minute
BASE_RETRY_DELAY = 1.0  # 1 second
CONNECTION_TIMEOUT = 120.0  # 2 minutes
MAX_QUEUE_SIZE = 1000  # Prevent unbounded growth


@dataclass
class ConnectionState:
    """Tracks the state of a WebSocket connection."""
    websocket: WebSocketServerProtocol
    last_message_time: float = field(default_factory=time.time)
    is_connected: bool = True
    retry_count: int = 0
    pending_messages: asyncio.Queue = field(default_factory=lambda: asyncio.Queue(maxsize=MAX_QUEUE_SIZE))
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_message_time = time.time()
    
    def is_timeout(self) -> bool:
        """Check if connection has timed out."""
        return (time.time() - self.last_message_time) > CONNECTION_TIMEOUT


@dataclass
class QueuedMessage:
    """Represents a message in the pending queue."""
    message: dict
    enqueued_at: float = field(default_factory=time.time)
    retry_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if message has exceeded TTL."""
        return (time.time() - self.enqueued_at) > MESSAGE_TTL_SECONDS


class MessageQueue(ABC):
    """Abstract base class for message queue implementations."""
    
    @abstractmethod
    async def enqueue(self, client_id: str, message: dict) -> bool:
        """Add message to queue. Returns True if successful."""
        pass
    
    @abstractmethod
    async def dequeue(self, client_id: str) -> Optional[QueuedMessage]:
        """Get next message from queue. Returns None if empty."""
        pass
    
    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Remove expired messages. Returns count of removed messages."""
        pass
    
    @abstractmethod
    def get_queue_size(self, client_id: str) -> int:
        """Get current queue size for client."""
        pass


class InMemoryMessageQueue(MessageQueue):
    """In-memory implementation of message queue."""
    
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()
    
    async def enqueue(self, client_id: str, message: dict) -> bool:
        """Add message to queue."""
        async with self._lock:
            if client_id not in self._queues:
                self._queues[client_id] = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
            
            queue = self._queues[client_id]
            if queue.full():
                logger.warning(f"Queue full for client {client_id}, dropping oldest message")
                try:
                    queue.get_nowait()  # Drop oldest
                except asyncio.QueueEmpty:
                    pass
            
            queued_msg = QueuedMessage(message=message)
            try:
                await queue.put(queued_msg)
                logger.debug(f"Enqueued message for client {client_id}, queue size: {queue.qsize()}")
                return True
            except asyncio.QueueFull:
                logger.error(f"Failed to enqueue message for client {client_id}")
                return False
    
    async def dequeue(self, client_id: str) -> Optional[QueuedMessage]:
        """Get next message from queue."""
        async with self._lock:
            if client_id not in self._queues:
                return None
            
            queue = self._queues[client_id]
            try:
                msg = queue.get_nowait()
                # Check if expired
                if msg.is_expired():
                    logger.debug(f"Discarding expired message for client {client_id}")
                    return await self.dequeue(client_id)  # Try next message
                return msg
            except asyncio.QueueEmpty:
                return None
    
    async def cleanup_expired(self) -> int:
        """Remove expired messages from all queues."""
        removed_count = 0
        async with self._lock:
            for client_id, queue in list(self._queues.items()):
                temp_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
                while not queue.empty():
                    try:
                        msg = queue.get_nowait()
                        if not msg.is_expired():
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
        """Get current queue size for client."""
        if client_id not in self._queues:
            return 0
        return self._queues[client_id].qsize()


class ResilientWebSocketManager:
    """
    Manages WebSocket connections with resilience features.
    
    Features:
    - Pending message queue for disconnected clients
    - Automatic retry with exponential backoff
    - Connection timeout detection
    - Message TTL (300s)
    """
    
    def __init__(self, fallback_send: Optional[Callable] = None, queue: Optional[MessageQueue] = None):
        """
        Initialize the resilient WebSocket manager.
        
        Args:
            fallback_send: Optional fallback send function (for gradual migration)
            queue: Optional custom message queue implementation (defaults to in-memory)
        """
        self._fallback_send = fallback_send
        self._queue = queue or InMemoryMessageQueue()
        self._connections: Dict[str, ConnectionState] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._retry_task: Optional[asyncio.Task] = None
    
    def _get_client_id(self, websocket: WebSocketServerProtocol) -> str:
        """Generate unique client ID from websocket."""
        try:
            if hasattr(websocket, 'remote_address'):
                host, port = websocket.remote_address
                return f"{host}:{port}"
        except Exception:
            pass
        return str(id(websocket))
    
    def _get_retry_delay(self, retry_count: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        delay = min(BASE_RETRY_DELAY * (2 ** retry_count), MAX_RETRY_DELAY)
        jitter = random.uniform(0, 0.1 * delay)
        return delay + jitter
    
    async def send(self, websocket: WebSocketServerProtocol, message: dict, critical: bool = False) -> bool:
        """
        Send message with resilience.
        
        Args:
            websocket: WebSocket connection
            message: Message dict to send
            critical: If True, queue message on failure for retry
            
        Returns:
            True if sent successfully, False if queued for retry
        """
        client_id = self._get_client_id(websocket)
        
        try:
            # Try direct send first
            message_json = json.dumps(message)
            await websocket.send(message_json)
            
            # Update connection state
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].update_activity()
                    self._connections[client_id].retry_count = 0  # Reset on success
            
            logger.debug(f"Successfully sent message to {client_id}")
            return True
            
        except ConnectionClosed as e:
            logger.warning(f"Connection closed for {client_id}: {e}")
            
            # Queue for retry if critical
            if critical:
                queued = await self._queue.enqueue(client_id, message)
                if queued:
                    logger.info(f"Queued critical message for {client_id}, queue size: {self._queue.get_queue_size(client_id)}")
                else:
                    logger.error(f"Failed to queue message for {client_id}")
            
            # Update connection state
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].is_connected = False
            
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending to {client_id}: {e}")
            return False

    async def register_connection(self, websocket: WebSocketServerProtocol):
        """Register a new WebSocket connection."""
        client_id = self._get_client_id(websocket)
        async with self._lock:
            self._connections[client_id] = ConnectionState(websocket=websocket)
        logger.info(f"Registered connection for {client_id}")

    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        """Unregister a WebSocket connection."""
        client_id = self._get_client_id(websocket)
        async with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]
        logger.info(f"Unregistered connection for {client_id}")

    async def _retry_pending_messages(self):
        """Background task to retry pending messages."""
        logger.info("Starting pending message retry task")

        while True:
            try:
                await asyncio.sleep(5)  # Check every 5 seconds

                # Get list of clients with pending messages
                async with self._lock:
                    client_ids = list(self._connections.keys())

                for client_id in client_ids:
                    # Try to send pending messages
                    while True:
                        queued_msg = await self._queue.dequeue(client_id)
                        if queued_msg is None:
                            break  # No more messages

                        # Get connection state
                        async with self._lock:
                            if client_id not in self._connections:
                                logger.debug(f"Client {client_id} no longer connected, discarding message")
                                break

                            conn_state = self._connections[client_id]
                            if not conn_state.is_connected:
                                # Re-queue and wait for reconnection
                                await self._queue.enqueue(client_id, queued_msg.message)
                                break

                        # Try to send
                        try:
                            message_json = json.dumps(queued_msg.message)
                            await conn_state.websocket.send(message_json)
                            logger.info(f"Successfully sent queued message to {client_id}")
                            conn_state.update_activity()
                            conn_state.retry_count = 0

                        except ConnectionClosed:
                            # Re-queue with incremented retry count
                            queued_msg.retry_count += 1
                            if queued_msg.retry_count < 5:  # Max 5 retries
                                await self._queue.enqueue(client_id, queued_msg.message)
                                logger.debug(f"Re-queued message for {client_id}, retry {queued_msg.retry_count}")
                            else:
                                logger.warning(f"Discarding message for {client_id} after {queued_msg.retry_count} retries")
                            break

                        except Exception as e:
                            logger.error(f"Error retrying message for {client_id}: {e}")
                            break

            except Exception as e:
                logger.error(f"Error in retry task: {e}")
                await asyncio.sleep(10)  # Back off on error

    async def _cleanup_expired_messages(self):
        """Background task to cleanup expired messages."""
        logger.info("Starting expired message cleanup task")

        while True:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                removed = await self._queue.cleanup_expired()
                if removed > 0:
                    logger.info(f"Cleaned up {removed} expired messages")

                # Also check for timed-out connections
                async with self._lock:
                    timed_out = [
                        client_id for client_id, state in self._connections.items()
                        if state.is_timeout()
                    ]

                for client_id in timed_out:
                    logger.warning(f"Connection timeout detected for {client_id}")
                    async with self._lock:
                        if client_id in self._connections:
                            self._connections[client_id].is_connected = False

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)

    async def start_background_tasks(self):
        """Start background tasks for retry and cleanup."""
        if self._retry_task is None or self._retry_task.done():
            self._retry_task = asyncio.create_task(self._retry_pending_messages())
            logger.info("Started retry background task")

        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
            logger.info("Started cleanup background task")

    async def stop_background_tasks(self):
        """Stop background tasks."""
        if self._retry_task and not self._retry_task.done():
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped retry background task")

        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped cleanup background task")

    def get_stats(self) -> dict:
        """Get statistics about connections and queues."""
        stats = {
            "total_connections": len(self._connections),
            "connected": sum(1 for c in self._connections.values() if c.is_connected),
            "disconnected": sum(1 for c in self._connections.values() if not c.is_connected),
            "total_queued_messages": sum(
                self._queue.get_queue_size(client_id)
                for client_id in self._connections.keys()
            ),
            "connections": {}
        }

        for client_id, state in self._connections.items():
            stats["connections"][client_id] = {
                "is_connected": state.is_connected,
                "retry_count": state.retry_count,
                "queue_size": self._queue.get_queue_size(client_id),
                "last_activity": state.last_message_time,
                "is_timeout": state.is_timeout()
            }

        return stats

