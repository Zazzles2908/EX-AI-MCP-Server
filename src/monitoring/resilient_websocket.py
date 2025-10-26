"""
Resilient WebSocket Manager for handling connection failures and message queuing.

This module provides a robust WebSocket communication layer with:
- Pending message queue for disconnected clients
- Automatic retry with exponential backoff
- Connection timeout detection
- Message TTL (300s for pending messages)
- Metrics integration (Prometheus/OpenTelemetry compatible)
- Circuit breaker pattern for graceful degradation
- Message deduplication

Created: 2025-10-19
Updated: 2025-10-26 (Task 2 Week 1 - EXAI Enhancements)
Phase: Week 1 Day 1-2 - WebSocket Resilience
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

import asyncio
import json
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any, Set
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
    - Metrics integration (Prometheus/OpenTelemetry compatible)
    - Circuit breaker pattern for graceful degradation
    - Message deduplication

    EXAI-Enhanced (2025-10-26):
    - Added comprehensive metrics tracking
    - Integrated circuit breaker for connection failures
    - Message deduplication to prevent duplicates during reconnection
    """

    def __init__(
        self,
        fallback_send: Optional[Callable] = None,
        queue: Optional[MessageQueue] = None,
        enable_metrics: bool = True,
        enable_circuit_breaker: bool = True,
        enable_deduplication: bool = True
    ):
        """
        Initialize the resilient WebSocket manager.

        Args:
            fallback_send: Optional fallback send function (for gradual migration)
            queue: Optional custom message queue implementation (defaults to in-memory)
            enable_metrics: Enable metrics tracking (default: True)
            enable_circuit_breaker: Enable circuit breaker pattern (default: True)
            enable_deduplication: Enable message deduplication (default: True)
        """
        self._fallback_send = fallback_send
        self._queue = queue or InMemoryMessageQueue()
        self._connections: Dict[str, ConnectionState] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._retry_task: Optional[asyncio.Task] = None

        # EXAI Enhancement: Metrics integration
        self.metrics = None
        if enable_metrics:
            try:
                from src.monitoring.websocket_metrics import WebSocketMetrics
                self.metrics = WebSocketMetrics()
                # EXAI QA Fix #2: Start automatic periodic cleanup
                self.metrics.start_automatic_cleanup()
                logger.info("WebSocket metrics enabled with automatic cleanup")
            except ImportError:
                logger.warning("WebSocket metrics module not available")

        # EXAI Enhancement: Circuit breaker
        self._circuit_breaker = None
        if enable_circuit_breaker:
            try:
                from src.monitoring.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
                self._circuit_breaker = CircuitBreaker(
                    name="websocket_connections",
                    config=CircuitBreakerConfig(
                        failure_threshold=5,
                        success_threshold=2,
                        timeout_seconds=60.0
                    ),
                    on_state_change=self._on_circuit_state_change
                )
                logger.info("WebSocket circuit breaker enabled")
            except ImportError:
                logger.warning("Circuit breaker module not available")

        # EXAI Enhancement: Message deduplication
        self._enable_deduplication = enable_deduplication
        self._sent_message_ids: Set[str] = set()  # Track sent message IDs
        self._message_id_ttl = 300  # 5 minutes TTL for message IDs
        self._message_id_timestamps: Dict[str, float] = {}
        if enable_deduplication:
            logger.info("Message deduplication enabled")

    def _on_circuit_state_change(self, old_state, new_state):
        """Callback for circuit breaker state changes."""
        logger.warning(f"Circuit breaker state changed: {old_state.value} → {new_state.value}")
        if self.metrics:
            self.metrics.set_circuit_breaker_state(new_state)
    
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

    def _get_message_id(self, message: dict) -> Optional[str]:
        """
        Generate unique message ID for deduplication.

        EXAI QA Fix #1: Replaced MD5 with faster hash() for performance.
        EXAI QA Fix #2: Replaced hash() with xxhash for consistency across restarts.
        EXAI QA Fix #3 (2025-10-27): Include connection ID in deduplication key to prevent
        cross-connection interference. This fixes the issue where identical messages from
        different connections (e.g., hello_ack) were incorrectly marked as duplicates.

        Uses xxhash (fast + consistent) with SHA256 fallback if xxhash unavailable.
        Built-in hash() is NOT used because it's randomized per-process (security feature),
        causing false negatives in deduplication after server restarts.
        """
        if not self._enable_deduplication:
            return None

        # Use message ID if present, otherwise generate from content
        if "id" in message:
            return str(message["id"])

        # Generate ID from message content + connection ID for connection-scoped deduplication
        # CRITICAL FIX (2025-10-27): Include client_id to prevent cross-connection deduplication
        content = json.dumps(message, sort_keys=True)

        # Get client_id from the connection (stored during send)
        # If not available, fall back to content-only hash (backward compatibility)
        client_id = getattr(self, '_current_client_id', None)
        if client_id:
            content = f"{client_id}:{content}"

        # Try xxhash first (fastest + consistent)
        try:
            import xxhash
            return xxhash.xxh64(content).hexdigest()
        except ImportError:
            # Fallback to SHA256 (slower but consistent)
            import hashlib
            return hashlib.sha256(content.encode()).hexdigest()

    def _is_duplicate_message(self, message_id: Optional[str]) -> bool:
        """Check if message was recently sent (deduplication)."""
        if not message_id or not self._enable_deduplication:
            return False

        # Clean up expired message IDs
        current_time = time.time()
        expired_ids = [
            mid for mid, timestamp in self._message_id_timestamps.items()
            if current_time - timestamp > self._message_id_ttl
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

    async def send(self, websocket: WebSocketServerProtocol, message: dict, critical: bool = False) -> bool:
        """
        Send message with resilience, metrics, circuit breaker, and deduplication.

        EXAI-Enhanced (2025-10-26):
        - Added metrics tracking for latency and success/failure
        - Circuit breaker protection for failing connections
        - Message deduplication to prevent duplicates during reconnection

        Args:
            websocket: WebSocket connection
            message: Message dict to send
            critical: If True, queue message on failure for retry

        Returns:
            True if sent successfully, False if queued for retry
        """
        client_id = self._get_client_id(websocket)
        start_time = time.time()

        # CRITICAL DEBUG (2025-10-27): Log EVERY send attempt
        logger.info(f"[RESILIENT_SEND_START] client_id={client_id}, op={message.get('op')}")

        # EXAI Enhancement: Message deduplication
        # CRITICAL FIX (2025-10-27): Set client_id for connection-scoped deduplication
        self._current_client_id = client_id
        message_id = self._get_message_id(message)
        logger.info(f"[RESILIENT_SEND_DEDUP_CHECK] message_id={message_id}, checking...")
        if self._is_duplicate_message(message_id):
            # CRITICAL DEBUG (2025-10-27): Log duplicate detection
            logger.warning(f"[DEDUP] Skipping duplicate message {message_id} for {client_id}, op={message.get('op')}")
            logger.warning(f"[DEDUP] Message content: {str(message)[:200]}...")
            if self.metrics:
                self.metrics.record_message_deduplicated(client_id)
            return True  # Already sent, consider success
        logger.info(f"[RESILIENT_SEND_DEDUP_CHECK] Not a duplicate, proceeding...")

        # EXAI Enhancement: Circuit breaker protection
        if self._circuit_breaker and self._circuit_breaker.is_open:
            logger.warning(f"[RESILIENT_SEND_CIRCUIT_BREAKER] Circuit breaker OPEN for {client_id}, queueing message")
            if critical:
                queued = await self._queue.enqueue(client_id, message)
                if queued and self.metrics:
                    queue_size = self._queue.get_queue_size(client_id)
                    self.metrics.record_message_queued(client_id, queue_size)
            return False
        logger.info(f"[RESILIENT_SEND_CIRCUIT_BREAKER] Circuit breaker OK, proceeding...")

        try:
            # Try direct send first
            message_json = json.dumps(message)
            msg_size = len(message_json.encode('utf-8'))

            # CRITICAL DEBUG (2025-10-27): Log EVERY WebSocket send
            logger.info(f"[RESILIENT_WS_SEND] About to call websocket.send() for {client_id}, op={message.get('op')}, size={msg_size}")
            await websocket.send(message_json)
            logger.info(f"[RESILIENT_WS_SEND] websocket.send() completed for {client_id}, op={message.get('op')}")

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Update connection state
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].update_activity()
                    self._connections[client_id].retry_count = 0  # Reset on success

            # EXAI Enhancement: Record metrics
            if self.metrics:
                self.metrics.record_message_sent(client_id, latency_ms)

            # EXAI Enhancement: Circuit breaker success
            if self._circuit_breaker:
                await self._circuit_breaker._on_success()

            logger.debug(f"Successfully sent message to {client_id} ({latency_ms:.2f}ms)")
            return True

        except ConnectionClosed as e:
            logger.warning(f"Connection closed for {client_id}: {e}")

            # EXAI Enhancement: Record metrics
            if self.metrics:
                self.metrics.record_message_failed(client_id)

            # EXAI Enhancement: Circuit breaker failure
            if self._circuit_breaker:
                await self._circuit_breaker._on_failure()

            # Queue for retry if critical
            if critical:
                queued = await self._queue.enqueue(client_id, message)
                if queued:
                    queue_size = self._queue.get_queue_size(client_id)
                    logger.info(f"Queued critical message for {client_id}, queue size: {queue_size}")
                    if self.metrics:
                        self.metrics.record_message_queued(client_id, queue_size)
                else:
                    logger.error(f"Failed to queue message for {client_id}")
                    if self.metrics:
                        self.metrics.record_queue_overflow(client_id)

            # Update connection state
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].is_connected = False

            return False

        except Exception as e:
            logger.error(f"Unexpected error sending to {client_id}: {e}")

            # EXAI Enhancement: Record metrics
            if self.metrics:
                self.metrics.record_message_failed(client_id)

            # EXAI Enhancement: Circuit breaker failure
            if self._circuit_breaker:
                await self._circuit_breaker._on_failure()

            return False

    async def register_connection(self, websocket: WebSocketServerProtocol):
        """
        Register a new WebSocket connection.

        EXAI-Enhanced (2025-10-26): Added metrics tracking
        """
        client_id = self._get_client_id(websocket)
        async with self._lock:
            self._connections[client_id] = ConnectionState(websocket=websocket)

        # EXAI Enhancement: Record metrics
        if self.metrics:
            self.metrics.record_connection(client_id)

        logger.info(f"Registered connection for {client_id}")

    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        """
        Unregister a WebSocket connection.

        EXAI-Enhanced (2025-10-26): Added metrics tracking
        """
        client_id = self._get_client_id(websocket)
        async with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]

        # EXAI Enhancement: Record metrics
        if self.metrics:
            self.metrics.record_disconnection(client_id)

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

    async def graceful_shutdown(
        self,
        timeout: float = 30.0,
        flush_pending: bool = True,
        close_connections: bool = True
    ) -> dict:
        """
        Perform graceful shutdown of WebSocket manager.

        This method ensures all resources are properly cleaned up:
        1. Stop accepting new messages
        2. Flush pending messages (optional)
        3. Close all active connections (optional)
        4. Stop background tasks
        5. Cleanup metrics and circuit breaker

        Args:
            timeout: Maximum time to wait for pending messages (seconds)
            flush_pending: Whether to attempt sending pending messages
            close_connections: Whether to close active WebSocket connections

        Returns:
            dict: Shutdown statistics including:
                - pending_messages_flushed: Number of messages sent during shutdown
                - pending_messages_dropped: Number of messages that couldn't be sent
                - connections_closed: Number of connections closed
                - background_tasks_stopped: Number of background tasks stopped
                - metrics_cleaned: Whether metrics were cleaned up
                - duration_seconds: Total shutdown duration

        Example:
            >>> manager = ResilientWebSocketManager()
            >>> # ... use manager ...
            >>> stats = await manager.graceful_shutdown(timeout=30.0)
            >>> print(f"Shutdown complete: {stats['connections_closed']} connections closed")

        Created: 2025-10-26 (Week 1.5 Validation)
        """
        start_time = time.time()
        stats = {
            "pending_messages_flushed": 0,
            "pending_messages_dropped": 0,
            "connections_closed": 0,
            "background_tasks_stopped": 0,
            "metrics_cleaned": False,
            "duration_seconds": 0.0
        }

        logger.info(
            f"Starting graceful shutdown (timeout={timeout}s, "
            f"flush_pending={flush_pending}, close_connections={close_connections})"
        )

        try:
            # Step 1: Flush pending messages if requested
            if flush_pending:
                logger.info("Flushing pending messages...")
                flush_start = time.time()
                flush_timeout = min(timeout * 0.7, 20.0)  # Use 70% of timeout or 20s max

                try:
                    async with asyncio.timeout(flush_timeout):
                        for client_id in list(self._connections.keys()):
                            queue_size = self._queue.get_queue_size(client_id)
                            if queue_size > 0:
                                logger.debug(
                                    f"Flushing {queue_size} pending messages for {client_id}"
                                )

                                # Try to send pending messages
                                flushed = 0
                                while True:
                                    msg = await self._queue.dequeue(client_id)
                                    if msg is None:
                                        break

                                    try:
                                        # Attempt to send message
                                        state = self._connections.get(client_id)
                                        if state and state.websocket and state.is_connected:
                                            # Convert message dict to JSON string for sending
                                            message_str = json.dumps(msg.message) if isinstance(msg.message, dict) else str(msg.message)
                                            await state.websocket.send(message_str)
                                            flushed += 1
                                            stats["pending_messages_flushed"] += 1
                                        else:
                                            stats["pending_messages_dropped"] += 1
                                    except Exception as e:
                                        logger.warning(
                                            f"Failed to flush message for {client_id}: {e}"
                                        )
                                        stats["pending_messages_dropped"] += 1

                                if flushed > 0:
                                    logger.info(
                                        f"Flushed {flushed} messages for {client_id}"
                                    )

                except asyncio.TimeoutError:
                    logger.warning(
                        f"Flush timeout after {flush_timeout}s, "
                        f"dropping remaining messages"
                    )
                    # Count remaining messages as dropped
                    for client_id in self._connections.keys():
                        remaining = self._queue.get_queue_size(client_id)
                        stats["pending_messages_dropped"] += remaining

                flush_duration = time.time() - flush_start
                logger.info(
                    f"Flush complete in {flush_duration:.2f}s: "
                    f"{stats['pending_messages_flushed']} sent, "
                    f"{stats['pending_messages_dropped']} dropped"
                )

            # Step 2: Close active connections if requested
            if close_connections:
                logger.info("Closing active connections...")
                async with self._lock:
                    for client_id, state in list(self._connections.items()):
                        if state.websocket and state.is_connected:
                            try:
                                await state.websocket.close(
                                    code=1001,  # Going Away
                                    reason="Server shutting down"
                                )
                                stats["connections_closed"] += 1
                                logger.debug(f"Closed connection for {client_id}")
                            except Exception as e:
                                logger.warning(
                                    f"Error closing connection for {client_id}: {e}"
                                )

                logger.info(f"Closed {stats['connections_closed']} connections")

            # Step 3: Stop background tasks
            logger.info("Stopping background tasks...")
            await self.stop_background_tasks()
            stats["background_tasks_stopped"] = 2  # retry + cleanup tasks

            # Step 4: Cleanup metrics
            if self.metrics:
                logger.info("Cleaning up metrics...")
                try:
                    # Stop automatic cleanup task (synchronous method)
                    if hasattr(self.metrics, 'stop_automatic_cleanup'):
                        self.metrics.stop_automatic_cleanup()

                    # Final cleanup of inactive clients
                    if hasattr(self.metrics, 'cleanup_inactive_clients'):
                        cleaned = self.metrics.cleanup_inactive_clients()
                        logger.debug(f"Cleaned up {cleaned} inactive client metrics")

                    stats["metrics_cleaned"] = True
                except Exception as e:
                    logger.warning(f"Error cleaning up metrics: {e}")

            # Step 5: Clear internal state
            logger.info("Clearing internal state...")
            async with self._lock:
                self._connections.clear()
                self._sent_message_ids.clear()
                self._message_id_timestamps.clear()

            stats["duration_seconds"] = time.time() - start_time
            logger.info(
                f"Graceful shutdown complete in {stats['duration_seconds']:.2f}s: "
                f"{stats['connections_closed']} connections closed, "
                f"{stats['pending_messages_flushed']} messages flushed, "
                f"{stats['pending_messages_dropped']} messages dropped"
            )

            return stats

        except Exception as e:
            stats["duration_seconds"] = time.time() - start_time
            logger.error(f"Error during graceful shutdown: {e}", exc_info=True)
            raise

    def get_stats(self) -> dict:
        """
        Get statistics about connections and queues.

        EXAI-Enhanced (2025-10-26): Added metrics and circuit breaker status
        """
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

        # EXAI Enhancement: Add metrics if available
        if self.metrics:
            stats["metrics"] = self.metrics.to_dict()

        # EXAI Enhancement: Add circuit breaker status if available
        if self._circuit_breaker:
            stats["circuit_breaker"] = self._circuit_breaker.get_stats()

        return stats

