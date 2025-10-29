"""
Integration Test Framework for WebSocket Resilience Testing.

This package provides shared utilities for testing WebSocket connections,
circuit breakers, metrics collection, and error recovery.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

from .websocket_test_utils import (
    MockWebSocket,
    MockWebSocketConnection,
    create_mock_websocket,
    simulate_connection_failure,
    simulate_network_latency
)

from .resilience_test_utils import (
    CircuitBreakerTestHelper,
    RetryTestHelper,
    simulate_circuit_breaker_failure,
    wait_for_circuit_breaker_state
)

from .metrics_test_utils import (
    MetricsCollector,
    assert_metrics_recorded,
    assert_metric_value,
    get_metric_snapshot
)

__all__ = [
    # WebSocket utilities
    'MockWebSocket',
    'MockWebSocketConnection',
    'create_mock_websocket',
    'simulate_connection_failure',
    'simulate_network_latency',
    
    # Resilience utilities
    'CircuitBreakerTestHelper',
    'RetryTestHelper',
    'simulate_circuit_breaker_failure',
    'wait_for_circuit_breaker_state',
    
    # Metrics utilities
    'MetricsCollector',
    'assert_metrics_recorded',
    'assert_metric_value',
    'get_metric_snapshot',
]

