"""
WebSocket Background Tasks - Background task management.

This module provides background task management for WebSocket operations
including message retry, cleanup, and connection timeout detection.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""

import asyncio
import logging
import time
import random
from typing import Dict, Optional, Callable
from src.monitoring.websocket_models import ConnectionState, QueuedMessage
from src.monitoring.message_queue import MessageQueue
from src.monitoring.circuit_breaker import CircuitBreaker
from src.monitoring.websocket_metrics import WebSocketMetrics


logger = logging.getLogger(__name__)

# Configuration constants
RETRY_CHECK_INTERVAL = 5.0  # Check for retries every 5 seconds
CLEANUP_INTERVAL = 60.0  # Cleanup expired messages every 60 seconds
CONNECTION_TIMEOUT = 120.0  # 2 minutes
MAX_RETRY_ATTEMPTS = 5
BASE_RETRY_DELAY = 1.0  # 1 second
MAX_RETRY_DELAY = 60.0  # 1 minute


class BackgroundTaskManager:
    """
    Manages background tasks for WebSocket resilience.

    This class handles:
    - Retrying pending messages for disconnected clients
    - Cleaning up expired messages
    - Detecting connection timeouts
    - Managing async task lifecycle
    """

    def __init__(
        self,
        queue: MessageQueue,
        connections: Dict[str, ConnectionState],
        lock: asyncio.Lock,
        metrics: Optional[WebSocketMetrics] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        on_timeout: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize background task manager.

        Args:
            queue: Message queue instance
            connections: Dictionary of connection states
            lock: Async lock for thread-safe operations
            metrics: Optional WebSocketMetrics instance
            circuit_breaker: Optional CircuitBreaker instance
            on_timeout: Optional callback for connection timeouts
        """
        self._queue = queue
        self._connections = connections
        self._lock = lock
        self._metrics = metrics
        self._circuit_breaker = circuit_breaker
        self._on_timeout = on_timeout

        self._retry_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start background tasks."""
        if self._running:
            logger.warning("Background tasks already running")
            return

        self._running = True
        logger.info("Starting background tasks")

        # Start retry task
        if self._retry_task is None or self._retry_task.done():
            self._retry_task = asyncio.create_task(self._retry_pending_messages())
            logger.info("Started retry background task")

        # Start cleanup task
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_expired_messages())
            logger.info("Started cleanup background task")

    async def stop(self):
        """Stop background tasks."""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping background tasks")

        # Cancel retry task
        if self._retry_task and not self._retry_task.done():
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped retry background task")

        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped cleanup background task")

    async def _retry_pending_messages(self):
        """
        Background task to retry pending messages for disconnected clients.

        This task:
        1. Checks every 5 seconds for clients with pending messages
        2. Attempts to send queued messages
        3. Re-queues messages that fail
        4. Stops retrying after max attempts (5)
        """
        logger.info("Starting pending message retry task")

        while self._running:
            try:
                await asyncio.sleep(RETRY_CHECK_INTERVAL)

                # Get list of clients with pending messages
                async with self._lock:
                    client_ids = list(self._connections.keys())

                for client_id in client_ids:
                    await self._retry_client_messages(client_id)

            except Exception as e:
                logger.error(f"Error in retry task: {e}", exc_info=True)
                await asyncio.sleep(10)  # Back off on error

    async def _retry_client_messages(self, client_id: str):
        """
        Retry messages for a specific client.

        Args:
            client_id: Client identifier
        """
        # Try to send pending messages
        while True:
            queued_msg = await self._queue.dequeue(client_id)
            if queued_msg is None:
                break  # No more messages

            # Get connection state
            async with self._lock:
                if client_id not in self._connections:
                    logger.debug(
                        f"Client {client_id} no longer connected, discarding message"
                    )
                    break

                conn_state = self._connections[client_id]
                if not conn_state.is_connected:
                    # Re-queue and wait for reconnection
                    await self._queue.enqueue(client_id, queued_msg.message)
                    break

            # Try to send
            try:
                import json
                message_json = json.dumps(queued_msg.message)
                await conn_state.websocket.send(message_json)
                logger.info(f"Successfully sent queued message to {client_id}")

                conn_state.update_activity()
                conn_state.retry_count = 0

                if self._metrics:
                    self._metrics.record_message_sent(client_id, 0.0)

            except Exception as e:
                logger.error(f"Error retrying message for {client_id}: {e}")

                # Re-queue with incremented retry count
                queued_msg.retry_count += 1
                if queued_msg.retry_count < MAX_RETRY_ATTEMPTS:
                    await self._queue.enqueue(client_id, queued_msg.message)
                    logger.debug(
                        f"Re-queued message for {client_id}, "
                        f"retry {queued_msg.retry_count}"
                    )
                else:
                    logger.warning(
                        f"Discarding message for {client_id} "
                        f"after {queued_msg.retry_count} retries"
                    )
                break

    async def _cleanup_expired_messages(self):
        """
        Background task to cleanup expired messages and timeouts.

        This task:
        1. Cleans up expired messages from queues every minute
        2. Detects and handles connection timeouts
        3. Updates connection state for timed-out clients
        """
        logger.info("Starting expired message cleanup task")

        while self._running:
            try:
                await asyncio.sleep(CLEANUP_INTERVAL)

                # Cleanup expired messages
                removed = await self._queue.cleanup_expired()
                if removed > 0:
                    logger.info(f"Cleaned up {removed} expired messages")

                # Check for timed-out connections
                timed_out = []
                async with self._lock:
                    for client_id, state in self._connections.items():
                        if state.is_timeout(CONNECTION_TIMEOUT):
                            timed_out.append(client_id)

                # Handle timeouts
                for client_id in timed_out:
                    logger.warning(f"Connection timeout detected for {client_id}")

                    if self._on_timeout:
                        self._on_timeout(client_id)

                    async with self._lock:
                        if client_id in self._connections:
                            self._connections[client_id].is_connected = False

                    if self._metrics:
                        self._metrics.record_timeout(client_id)

            except Exception as e:
                logger.error(f"Error in cleanup task: {e}", exc_info=True)
                await asyncio.sleep(60)

    def _get_retry_delay(self, retry_count: int) -> float:
        """
        Calculate retry delay with exponential backoff and jitter.

        Args:
            retry_count: Number of retry attempts

        Returns:
            Delay in seconds
        """
        delay = min(BASE_RETRY_DELAY * (2 ** retry_count), MAX_RETRY_DELAY)
        jitter = random.uniform(0, 0.1 * delay)
        return delay + jitter


__all__ = [
    "BackgroundTaskManager"
]
