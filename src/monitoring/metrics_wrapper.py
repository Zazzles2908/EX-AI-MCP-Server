"""
Backward-Compatible Metrics Wrapper.

Provides a drop-in replacement for WebSocketMetrics that uses the new
ProductionMetrics system under the hood.

Created: 2025-10-28
Phase: Emergency Metrics Redesign
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import os
import logging
from typing import Optional

from src.monitoring.production_metrics import (
    ProductionMetrics,
    MetricsConfig,
    MetricType
)
from src.monitoring.websocket_metrics import CircuitBreakerState

logger = logging.getLogger(__name__)


class MetricsWrapper:
    """
    Backward-compatible wrapper for ProductionMetrics.
    
    This class provides the same interface as WebSocketMetrics but uses
    the new high-performance ProductionMetrics system internally.
    
    Usage:
        # Drop-in replacement
        metrics = MetricsWrapper()
        metrics.record_connection("client_1")
        metrics.record_message_sent("client_1", latency_ms=10.0)
    """
    
    def __init__(self, config: Optional[MetricsConfig] = None):
        self.production_metrics = ProductionMetrics(config)
        self.production_metrics.start()
        
        # Track state for compatibility
        self.active_connections = 0
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
        self.start_time = self.production_metrics.start_time
    
    def record_connection(self, client_id: str):
        """Record a new connection."""
        self.production_metrics.record_metric(
            MetricType.CONNECTION,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
        self.active_connections += 1
    
    def record_disconnection(self, client_id: str):
        """Record a disconnection."""
        self.production_metrics.record_metric(
            MetricType.DISCONNECTION,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
        self.active_connections = max(0, self.active_connections - 1)
    
    def record_message_sent(self, client_id: str, latency_ms: float = 0.0):
        """Record a successfully sent message."""
        self.production_metrics.record_metric(
            MetricType.MESSAGE_SENT,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
    
    def record_message_queued(self, client_id: str, queue_size: int):
        """Record a queued message."""
        self.production_metrics.record_metric(
            MetricType.MESSAGE_QUEUED,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
    
    def record_message_failed(self, client_id: str):
        """Record a failed message."""
        self.production_metrics.record_metric(
            MetricType.MESSAGE_FAILED,
            value=1.0,
            client_id=client_id,
            is_critical=True  # Failures are critical
        )
    
    def record_retry_attempt(self, client_id: str):
        """Record a retry attempt."""
        self.production_metrics.record_metric(
            MetricType.RETRY_ATTEMPT,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
    
    def record_retry_success(self, client_id: str):
        """Record a successful retry."""
        self.production_metrics.record_metric(
            MetricType.RETRY_SUCCESS,
            value=1.0,
            client_id=client_id,
            is_critical=False
        )
    
    def record_retry_failure(self, client_id: str):
        """Record a failed retry."""
        self.production_metrics.record_metric(
            MetricType.RETRY_FAILURE,
            value=1.0,
            client_id=client_id,
            is_critical=True  # Failures are critical
        )
    
    def record_circuit_breaker_open(self):
        """Record circuit breaker opening."""
        self.production_metrics.record_metric(
            MetricType.CIRCUIT_BREAKER_OPEN,
            value=1.0,
            is_critical=True  # State changes are critical
        )
        self.circuit_breaker_state = CircuitBreakerState.OPEN
    
    def record_circuit_breaker_close(self):
        """Record circuit breaker closing."""
        self.production_metrics.record_metric(
            MetricType.CIRCUIT_BREAKER_CLOSE,
            value=1.0,
            is_critical=True  # State changes are critical
        )
        self.circuit_breaker_state = CircuitBreakerState.CLOSED
    
    def get_retry_success_rate(self) -> float:
        """Calculate retry success rate."""
        metrics = self.production_metrics.get_metrics()
        attempts = metrics.get('retry_attempts', 0)
        successes = metrics.get('retry_successes', 0)
        
        if attempts == 0:
            return 0.0
        
        return successes / attempts
    
    def get_uptime_seconds(self) -> float:
        """Get uptime in seconds."""
        metrics = self.production_metrics.get_metrics()
        return metrics.get('uptime_seconds', 0.0)
    
    def to_dict(self) -> dict:
        """Export metrics to dictionary format."""
        metrics = self.production_metrics.get_metrics()
        
        return {
            'connections': {
                'total': int(metrics.get('connections', 0)),
                'active': self.active_connections,
                'failed': 0,  # Not tracked in new system
                'reconnections': 0,  # Not tracked in new system
                'timeouts': 0  # Not tracked in new system
            },
            'messages': {
                'sent': int(metrics.get('messages_sent', 0)),
                'queued': int(metrics.get('messages_queued', 0)),
                'failed': int(metrics.get('messages_failed', 0)),
                'expired': 0,  # Not tracked in new system
                'deduplicated': 0  # Not tracked in new system
            },
            'queue': {
                'current_size': 0,  # Not tracked in new system
                'max_size': 0,  # Not tracked in new system
                'overflows': 0  # Not tracked in new system
            },
            'retry': {
                'attempts': int(metrics.get('retry_attempts', 0)),
                'successes': int(metrics.get('retry_successes', 0)),
                'failures': int(metrics.get('retry_failures', 0)),
                'success_rate': self.get_retry_success_rate()
            },
            'circuit_breaker': {
                'state': self.circuit_breaker_state.value,
                'opens': int(metrics.get('circuit_breaker_opens', 0)),
                'half_opens': 0,  # Not tracked in new system
                'closes': int(metrics.get('circuit_breaker_closes', 0))
            },
            'latency': {
                'avg_send_ms': 0.0  # Not tracked in new system (too expensive)
            },
            'uptime_seconds': metrics.get('uptime_seconds', 0.0),
            'meta_metrics': metrics.get('meta', {}) if 'meta' in metrics else None
        }
    
    def stop_background_tasks(self):
        """Stop background tasks (for compatibility)."""
        self.production_metrics.stop()
    
    async def stop_background_tasks_async(self):
        """Async version of stop_background_tasks."""
        self.production_metrics.stop()


def create_production_metrics(enable_production: Optional[bool] = None) -> MetricsWrapper:
    """
    Factory function to create metrics instance.
    
    Args:
        enable_production: If True, use ProductionMetrics. If None, check env var.
    
    Returns:
        MetricsWrapper instance
    """
    if enable_production is None:
        enable_production = os.getenv('USE_PRODUCTION_METRICS', 'true').lower() == 'true'
    
    if enable_production:
        logger.info("Using ProductionMetrics (high-performance mode)")
        return MetricsWrapper()
    else:
        logger.warning("Using legacy WebSocketMetrics (not recommended)")
        from src.monitoring.websocket_metrics import WebSocketMetrics
        return WebSocketMetrics()

