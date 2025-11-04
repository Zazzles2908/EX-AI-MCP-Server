"""
Resilient WebSocket Manager - Core WebSocket resilience logic.

This module provides the main ResilientWebSocketManager class that
coordinates all WebSocket resilience features including queuing,
metrics, circuit breaker, and deduplication.

Created: 2025-11-04 (Refactoring from resilient_websocket.py)
Part of: God Object Refactoring Milestone
"""

import asyncio
import json
import logging
import time
from typing import Callable, Optional, Dict, Any
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

from src.monitoring.websocket_models import ConnectionState
from src.monitoring.message_queue import MessageQueue, InMemoryMessageQueue
from src.monitoring.websocket_deduplication import MessageDeduplicator
from src.monitoring.websocket_background_tasks import BackgroundTaskManager
from src.monitoring.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from src.monitoring.websocket_metrics import WebSocketMetrics


logger = logging.getLogger(__name__)


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

    This is the main orchestrator class that coordinates all resilience
    features through specialized components.
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
        # Core components
        self._fallback_send = fallback_send
        self._queue = queue or InMemoryMessageQueue()
        self._connections: Dict[str, ConnectionState] = {}
        self._lock = asyncio.Lock()

        # Initialize metrics
        self.metrics: Optional[WebSocketMetrics] = None
        if enable_metrics:
            try:
                self.metrics = WebSocketMetrics()
                self.metrics.start_automatic_cleanup()
                logger.info("WebSocket metrics enabled with automatic cleanup")
            except Exception as e:
                logger.warning(f"WebSocket metrics not available: {e}")

        # Initialize circuit breaker
        self._circuit_breaker: Optional[CircuitBreaker] = None
        if enable_circuit_breaker:
            try:
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
            except Exception as e:
                logger.warning(f"Circuit breaker not available: {e}")

        # Initialize deduplication
        self._deduplicator = MessageDeduplicator(enabled=enable_deduplication)
        if enable_deduplication:
            logger.info("Message deduplication enabled")

        # Initialize background task manager
        self._task_manager = BackgroundTaskManager(
            queue=self._queue,
            connections=self._connections,
            lock=self._lock,
            metrics=self.metrics,
            circuit_breaker=self._circuit_breaker,
            on_timeout=self._on_connection_timeout
        )

        logger.info("ResilientWebSocketManager initialized")

    def _on_circuit_state_change(self, old_state, new_state):
        """
        Callback for circuit breaker state changes.

        Args:
            old_state: Previous circuit breaker state
            new_state: New circuit breaker state
        """
        logger.warning(f"Circuit breaker state changed: {old_state.value} → {new_state.value}")
        if self.metrics:
            self.metrics.set_circuit_breaker_state(new_state)

    def _on_connection_timeout(self, client_id: str):
        """
        Handle connection timeout.

        Args:
            client_id: Client that timed out
        """
        logger.warning(f"Connection timeout for {client_id}")
        if self.metrics:
            self.metrics.record_timeout(client_id)

    def _get_client_id(self, websocket: WebSocketServerProtocol) -> str:
        """
        Generate unique client ID from websocket.

        Args:
            websocket: WebSocket connection

        Returns:
            Unique client identifier string
        """
        try:
            if hasattr(websocket, 'remote_address'):
                host, port = websocket.remote_address
                return f"{host}:{port}"
        except Exception:
            pass
        return str(id(websocket))

    async def send(
        self,
        websocket: WebSocketServerProtocol,
        message: dict,
        critical: bool = False
    ) -> bool:
        """
        Send message with resilience, metrics, circuit breaker, and deduplication.

        This method coordinates all resilience features:
        1. Message deduplication
        2. Circuit breaker protection
        3. Direct send attempt
        4. Queueing on failure (if critical)
        5. Metrics tracking
        6. Circuit breaker state updates

        Args:
            websocket: WebSocket connection
            message: Message dict to send
            critical: If True, queue message on failure for retry

        Returns:
            True if sent successfully, False if queued for retry
        """
        client_id = self._get_client_id(websocket)
        start_time = time.time()

        # Set client ID for connection-scoped deduplication
        self._deduplicator.set_current_client_id(client_id)

        # Check for duplicate message
        message_id = self._deduplicator.get_message_id(message)
        if self._deduplicator.is_duplicate(message_id):
            logger.debug(f"Skipping duplicate message {message_id} for {client_id}")
            if self.metrics:
                self.metrics.record_message_deduplicated(client_id)
            return True

        # Check circuit breaker
        if self._circuit_breaker and self._circuit_breaker.is_open:
            logger.warning(
                f"Circuit breaker OPEN for {client_id}, queueing message"
            )
            if critical:
                queued = await self._queue.enqueue(client_id, message)
                if queued and self.metrics:
                    queue_size = self._queue.get_queue_size(client_id)
                    self.metrics.record_message_queued(client_id, queue_size)
            return False

        try:
            # Try direct send
            message_json = json.dumps(message)
            await websocket.send(message_json)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Update connection state
            async with self._lock:
                if client_id in self._connections:
                    self._connections[client_id].update_activity()
                    self._connections[client_id].retry_count = 0

            # Record metrics
            if self.metrics:
                self.metrics.record_message_sent(client_id, latency_ms)

            # Circuit breaker success
            if self._circuit_breaker:
                await self._circuit_breaker._on_success()

            logger.debug(f"Successfully sent message to {client_id} ({latency_ms:.2f}ms)")
            return True

        except ConnectionClosed as e:
            logger.warning(f"Connection closed for {client_id}: {e}")

            # Record metrics
            if self.metrics:
                self.metrics.record_message_failed(client_id)

            # Circuit breaker failure
            if self._circuit_breaker:
                await self._circuit_breaker._on_failure()

            # Queue for retry if critical
            if critical:
                queued = await self._queue.enqueue(client_id, message)
                if queued:
                    queue_size = self._queue.get_queue_size(client_id)
                    logger.info(
                        f"Queued critical message for {client_id}, "
                        f"queue size: {queue_size}"
                    )
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
            logger.error(f"Unexpected error sending to {client_id}: {e}", exc_info=True)

            # Record metrics
            if self.metrics:
                self.metrics.record_message_failed(client_id)

            # Circuit breaker failure
            if self._circuit_breaker:
                await self._circuit_breaker._on_failure()

            return False

    async def register_connection(self, websocket: WebSocketServerProtocol):
        """
        Register a new WebSocket connection.

        Args:
            websocket: WebSocket connection to register
        """
        client_id = self._get_client_id(websocket)
        async with self._lock:
            self._connections[client_id] = ConnectionState(websocket=websocket)

        if self.metrics:
            self.metrics.record_connection(client_id)

        logger.info(f"Registered connection for {client_id}")

    async def unregister_connection(self, websocket: WebSocketServerProtocol):
        """
        Unregister a WebSocket connection.

        Args:
            websocket: WebSocket connection to unregister
        """
        client_id = self._get_client_id(websocket)
        async with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]

        if self.metrics:
            self.metrics.record_disconnection(client_id)

        logger.info(f"Unregistered connection for {client_id}")

    # Public methods for testing and external access

    def get_message_id(self, message: dict) -> Optional[str]:
        """
        Generate unique message ID for deduplication.

        This method is primarily for testing and debugging purposes.
        In normal operation, deduplication happens automatically during send().

        Args:
            message: Message dictionary

        Returns:
            Unique message ID string or None if deduplication is disabled
        """
        return self._deduplicator.get_message_id(message)

    def is_duplicate_message(self, message_id: Optional[str]) -> bool:
        """
        Check if message was recently sent (deduplication).

        This method is primarily for testing and debugging purposes.
        In normal operation, deduplication happens automatically during send().

        Args:
            message_id: Unique message ID to check

        Returns:
            True if message is a duplicate, False otherwise
        """
        return self._deduplicator.is_duplicate(message_id)

    @property
    def message_id_ttl(self) -> float:
        """
        Get the TTL for message deduplication in seconds.

        This is primarily for testing purposes.
        """
        return self._deduplicator._ttl_seconds

    @message_id_ttl.setter
    def message_id_ttl(self, value: float):
        """
        Set the TTL for message deduplication in seconds.

        This is primarily for testing purposes.
        """
        self._deduplicator._ttl_seconds = value

    async def start_background_tasks(self):
        """Start background tasks for retry and cleanup."""
        await self._task_manager.start()

    async def stop_background_tasks(self):
        """Stop background tasks."""
        await self._task_manager.stop()

    async def graceful_shutdown(
        self,
        timeout: float = 30.0,
        flush_pending: bool = True,
        close_connections: bool = True
    ) -> dict:
        """
        Perform graceful shutdown of WebSocket manager.

        This method ensures all resources are properly cleaned up:
        1. Flush pending messages (optional)
        2. Close all active connections (optional)
        3. Stop background tasks
        4. Cleanup metrics and circuit breaker

        Args:
            timeout: Maximum time to wait for pending messages (seconds)
            flush_pending: Whether to attempt sending pending messages
            close_connections: Whether to close active WebSocket connections

        Returns:
            dict: Shutdown statistics
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
            # Step 1: Flush pending messages
            if flush_pending:
                stats.update(await self._flush_pending_messages(timeout))

            # Step 2: Close active connections
            if close_connections:
                stats["connections_closed"] = await self._close_all_connections()

            # Step 3: Stop background tasks
            await self.stop_background_tasks()
            stats["background_tasks_stopped"] = 2

            # Step 4: Cleanup metrics
            if self.metrics:
                await self._cleanup_metrics()
                stats["metrics_cleaned"] = True

            # Step 5: Clear internal state
            async with self._lock:
                self._connections.clear()
                self._deduplicator.clear()

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

    async def _flush_pending_messages(self, timeout: float) -> dict:
        """Flush pending messages during shutdown."""
        stats = {
            "pending_messages_flushed": 0,
            "pending_messages_dropped": 0
        }

        logger.info("Flushing pending messages...")
        flush_timeout = min(timeout * 0.7, 20.0)

        try:
            async with asyncio.timeout(flush_timeout):
                async with self._lock:
                    client_ids = list(self._connections.keys())

                for client_id in client_ids:
                    queue_size = self._queue.get_queue_size(client_id)
                    if queue_size > 0:
                        logger.debug(
                            f"Flushing {queue_size} pending messages for {client_id}"
                        )

                        flushed = 0
                        while True:
                            msg = await self._queue.dequeue(client_id)
                            if msg is None:
                                break

                            try:
                                state = self._connections.get(client_id)
                                if state and state.websocket and state.is_connected:
                                    message_str = json.dumps(msg.message) if isinstance(msg.message, dict) else str(msg.message)
                                    await state.websocket.send(message_str)
                                    flushed += 1
                                    stats["pending_messages_flushed"] += 1
                                else:
                                    stats["pending_messages_dropped"] += 1
                            except Exception as e:
                                logger.warning(f"Failed to flush message for {client_id}: {e}")
                                stats["pending_messages_dropped"] += 1

                        if flushed > 0:
                            logger.info(f"Flushed {flushed} messages for {client_id}")

        except asyncio.TimeoutError:
            logger.warning(f"Flush timeout after {flush_timeout}s")
            for client_id in self._connections.keys():
                remaining = self._queue.get_queue_size(client_id)
                stats["pending_messages_dropped"] += remaining

        logger.info(
            f"Flush complete: {stats['pending_messages_flushed']} sent, "
            f"{stats['pending_messages_dropped']} dropped"
        )

        return stats

    async def _close_all_connections(self) -> int:
        """Close all active connections."""
        count = 0
        logger.info("Closing active connections...")

        async with self._lock:
            for client_id, state in list(self._connections.items()):
                if state.websocket and state.is_connected:
                    try:
                        await state.websocket.close(
                            code=1001,
                            reason="Server shutting down"
                        )
                        count += 1
                        logger.debug(f"Closed connection for {client_id}")
                    except Exception as e:
                        logger.warning(f"Error closing connection for {client_id}: {e}")

        logger.info(f"Closed {count} connections")
        return count

    async def _cleanup_metrics(self):
        """Cleanup metrics resources."""
        logger.info("Cleaning up metrics...")
        try:
            if hasattr(self.metrics, 'stop_automatic_cleanup'):
                self.metrics.stop_automatic_cleanup()
            if hasattr(self.metrics, 'cleanup_inactive_clients'):
                cleaned = self.metrics.cleanup_inactive_clients()
                logger.debug(f"Cleaned up {cleaned} inactive client metrics")
        except Exception as e:
            logger.warning(f"Error cleaning up metrics: {e}")

    def get_stats(self) -> dict:
        """
        Get statistics about connections and queues.

        Returns:
            Dictionary with connection and queue statistics
        """
        stats = {
            "total_connections": len(self._connections),
            "connected": sum(1 for c in self._connections.values() if c.is_connected),
            "disconnected": sum(1 for c in self._connections.values() if not c.is_connected),
            "total_queued_messages": self._queue.get_total_queue_size(),
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

        # Add metrics if available
        if self.metrics:
            stats["metrics"] = self.metrics.to_dict()

        # Add circuit breaker status if available
        if self._circuit_breaker:
            stats["circuit_breaker"] = self._circuit_breaker.get_stats()

        # Add deduplication stats
        stats["deduplication"] = self._deduplicator.get_stats()

        # Add queue stats
        stats["queue"] = self._queue.to_dict()

        return stats


__all__ = [
    "ResilientWebSocketManager"
]
