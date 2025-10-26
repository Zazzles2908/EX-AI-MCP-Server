"""
WebSocket Metrics Collection for Prometheus/OpenTelemetry Integration.

This module provides metrics tracking for WebSocket connections including:
- Connection counts (total, active, failed)
- Message throughput (sent, queued, failed, expired)
- Queue statistics (size, depth, overflow)
- Retry statistics (attempts, success rate)
- Circuit breaker state
- Connection health (timeouts, reconnections)

Created: 2025-10-26
Phase: Task 2 Week 1 - WebSocket Stability Enhancements
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass
class WebSocketMetrics:
    """
    Comprehensive WebSocket metrics tracking.
    
    This class provides in-memory metrics that can be exported to
    Prometheus, OpenTelemetry, or other monitoring systems.
    """
    
    # Connection metrics
    total_connections: int = 0
    active_connections: int = 0
    failed_connections: int = 0
    reconnections: int = 0
    timeouts: int = 0
    
    # Message metrics
    messages_sent: int = 0
    messages_queued: int = 0
    messages_failed: int = 0
    messages_expired: int = 0
    messages_deduplicated: int = 0
    
    # Queue metrics
    current_queue_size: int = 0
    max_queue_size: int = 0
    queue_overflows: int = 0
    
    # Retry metrics
    retry_attempts: int = 0
    retry_successes: int = 0
    retry_failures: int = 0
    
    # Circuit breaker metrics
    circuit_breaker_state: CircuitBreakerState = CircuitBreakerState.CLOSED
    circuit_breaker_opens: int = 0
    circuit_breaker_half_opens: int = 0
    circuit_breaker_closes: int = 0
    
    # Latency tracking (milliseconds)
    send_latency_sum: float = 0.0
    send_latency_count: int = 0
    
    # Per-client metrics
    client_metrics: Dict[str, 'ClientMetrics'] = field(default_factory=dict)
    
    # Timestamps
    start_time: float = field(default_factory=time.time)
    last_update: float = field(default_factory=time.time)

    # Cleanup configuration (EXAI QA Fix: Memory management)
    client_metrics_ttl: int = 3600  # 1 hour TTL for inactive clients
    cleanup_interval: int = 300  # 5 minutes cleanup interval
    _client_last_activity: Dict[str, float] = field(default_factory=dict)
    _cleanup_task: Optional[asyncio.Task] = field(default=None, init=False, repr=False)
    _cleanup_enabled: bool = field(default=False, init=False, repr=False)

    def record_connection(self, client_id: str):
        """Record a new connection."""
        self.total_connections += 1
        self.active_connections += 1
        self.last_update = time.time()

        if client_id not in self.client_metrics:
            self.client_metrics[client_id] = ClientMetrics(client_id=client_id)
        self.client_metrics[client_id].connections += 1
        self._client_last_activity[client_id] = time.time()  # Track activity
    
    def record_disconnection(self, client_id: str):
        """Record a disconnection."""
        self.active_connections = max(0, self.active_connections - 1)
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].disconnections += 1
    
    def record_failed_connection(self, client_id: str):
        """Record a failed connection."""
        self.failed_connections += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].failed_connections += 1
    
    def record_reconnection(self, client_id: str):
        """Record a reconnection."""
        self.reconnections += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].reconnections += 1
    
    def record_timeout(self, client_id: str):
        """Record a connection timeout."""
        self.timeouts += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].timeouts += 1
    
    def record_message_sent(self, client_id: str, latency_ms: float = 0.0):
        """Record a successfully sent message."""
        self.messages_sent += 1
        self.send_latency_sum += latency_ms
        self.send_latency_count += 1
        self.last_update = time.time()

        if client_id in self.client_metrics:
            self.client_metrics[client_id].messages_sent += 1
        self._client_last_activity[client_id] = time.time()  # Track activity
    
    def record_message_queued(self, client_id: str, queue_size: int):
        """Record a queued message."""
        self.messages_queued += 1
        self.current_queue_size = queue_size
        self.max_queue_size = max(self.max_queue_size, queue_size)
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].messages_queued += 1
    
    def record_message_failed(self, client_id: str):
        """Record a failed message."""
        self.messages_failed += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].messages_failed += 1
    
    def record_message_expired(self, client_id: str):
        """Record an expired message."""
        self.messages_expired += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].messages_expired += 1
    
    def record_message_deduplicated(self, client_id: str):
        """Record a deduplicated message."""
        self.messages_deduplicated += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].messages_deduplicated += 1
    
    def record_queue_overflow(self, client_id: str):
        """Record a queue overflow."""
        self.queue_overflows += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].queue_overflows += 1
    
    def record_retry_attempt(self, client_id: str):
        """Record a retry attempt."""
        self.retry_attempts += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].retry_attempts += 1
    
    def record_retry_success(self, client_id: str):
        """Record a successful retry."""
        self.retry_successes += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].retry_successes += 1
    
    def record_retry_failure(self, client_id: str):
        """Record a failed retry."""
        self.retry_failures += 1
        self.last_update = time.time()
        
        if client_id in self.client_metrics:
            self.client_metrics[client_id].retry_failures += 1
    
    def set_circuit_breaker_state(self, state: CircuitBreakerState):
        """Update circuit breaker state."""
        old_state = self.circuit_breaker_state
        self.circuit_breaker_state = state
        self.last_update = time.time()
        
        # Track state transitions
        if old_state != state:
            if state == CircuitBreakerState.OPEN:
                self.circuit_breaker_opens += 1
            elif state == CircuitBreakerState.HALF_OPEN:
                self.circuit_breaker_half_opens += 1
            elif state == CircuitBreakerState.CLOSED:
                self.circuit_breaker_closes += 1
    
    def get_average_send_latency(self) -> float:
        """Calculate average send latency in milliseconds."""
        if self.send_latency_count == 0:
            return 0.0
        return self.send_latency_sum / self.send_latency_count
    
    def get_retry_success_rate(self) -> float:
        """Calculate retry success rate (0.0 to 1.0)."""
        total_retries = self.retry_successes + self.retry_failures
        if total_retries == 0:
            return 0.0
        return self.retry_successes / total_retries
    
    def get_uptime_seconds(self) -> float:
        """Get uptime in seconds."""
        return time.time() - self.start_time

    def cleanup_inactive_clients(self, ttl_seconds: Optional[int] = None) -> int:
        """
        Remove metrics for inactive clients (EXAI QA Fix: Memory management).

        Args:
            ttl_seconds: Time-to-live for inactive clients (default: self.client_metrics_ttl)

        Returns:
            Number of clients removed
        """
        ttl = ttl_seconds or self.client_metrics_ttl
        current_time = time.time()
        removed_count = 0

        # Find inactive clients
        inactive_clients = [
            client_id for client_id, last_activity in self._client_last_activity.items()
            if current_time - last_activity > ttl
        ]

        # Remove inactive clients
        for client_id in inactive_clients:
            if client_id in self.client_metrics:
                del self.client_metrics[client_id]
            if client_id in self._client_last_activity:
                del self._client_last_activity[client_id]
            removed_count += 1

        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} inactive clients (TTL: {ttl}s)")

        return removed_count

    def start_automatic_cleanup(self):
        """
        Start automatic periodic cleanup (EXAI QA Fix #2: Automatic cleanup).

        Creates an asyncio background task that runs cleanup at configured interval.
        This ensures memory is managed consistently without manual intervention.
        """
        if self._cleanup_enabled:
            logger.warning("Automatic cleanup already started")
            return

        self._cleanup_enabled = True
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info(f"Started automatic cleanup (interval: {self.cleanup_interval}s, TTL: {self.client_metrics_ttl}s)")

    async def _periodic_cleanup(self):
        """Background task for periodic cleanup."""
        try:
            while self._cleanup_enabled:
                await asyncio.sleep(self.cleanup_interval)
                self.cleanup_inactive_clients()
        except asyncio.CancelledError:
            logger.info("Periodic cleanup task cancelled")
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")

    def stop_automatic_cleanup(self):
        """Stop automatic periodic cleanup."""
        if not self._cleanup_enabled:
            return

        self._cleanup_enabled = False
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
        logger.info("Stopped automatic cleanup")

    def to_dict(self) -> dict:
        """Export metrics as dictionary for JSON serialization."""
        return {
            "connections": {
                "total": self.total_connections,
                "active": self.active_connections,
                "failed": self.failed_connections,
                "reconnections": self.reconnections,
                "timeouts": self.timeouts
            },
            "messages": {
                "sent": self.messages_sent,
                "queued": self.messages_queued,
                "failed": self.messages_failed,
                "expired": self.messages_expired,
                "deduplicated": self.messages_deduplicated
            },
            "queue": {
                "current_size": self.current_queue_size,
                "max_size": self.max_queue_size,
                "overflows": self.queue_overflows
            },
            "retry": {
                "attempts": self.retry_attempts,
                "successes": self.retry_successes,
                "failures": self.retry_failures,
                "success_rate": self.get_retry_success_rate()
            },
            "circuit_breaker": {
                "state": self.circuit_breaker_state.value,
                "opens": self.circuit_breaker_opens,
                "half_opens": self.circuit_breaker_half_opens,
                "closes": self.circuit_breaker_closes
            },
            "latency": {
                "average_send_ms": self.get_average_send_latency()
            },
            "uptime_seconds": self.get_uptime_seconds(),
            "last_update": self.last_update
        }


@dataclass
class ClientMetrics:
    """Per-client metrics tracking."""
    client_id: str
    connections: int = 0
    disconnections: int = 0
    failed_connections: int = 0
    reconnections: int = 0
    timeouts: int = 0
    messages_sent: int = 0
    messages_queued: int = 0
    messages_failed: int = 0
    messages_expired: int = 0
    messages_deduplicated: int = 0
    queue_overflows: int = 0
    retry_attempts: int = 0
    retry_successes: int = 0
    retry_failures: int = 0

