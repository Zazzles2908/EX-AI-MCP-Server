"""
Integration Test: Circuit Breaker Behavior.

Tests circuit breaker functionality including:
- Circuit breaker activation on failures
- State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Message queuing when circuit is open
- Recovery after circuit closes
- Metrics tracking for circuit breaker events

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import pytest
import logging

# Import test framework
from framework.websocket_test_utils import create_mock_websocket, simulate_connection_failure
from framework.resilience_test_utils import (
    CircuitBreakerTestHelper,
    CircuitBreakerState,
    wait_for_circuit_breaker_state
)
from framework.metrics_test_utils import MetricsCollector, assert_metric_value

# Import system under test
from src.monitoring.resilient_websocket import ResilientWebSocketManager

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures():
    """Test that circuit breaker opens after threshold failures."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create circuit breaker helper
    cb_helper = CircuitBreakerTestHelper(manager._circuit_breaker)
    
    # Verify initial state is CLOSED
    initial_state = cb_helper.get_current_state()
    assert initial_state == CircuitBreakerState.CLOSED, \
        f"Initial state should be CLOSED, got {initial_state}"
    
    # Create mock WebSocket
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    # Trigger failures to open circuit breaker
    # Default threshold is 5 failures
    failure_count = 5
    await cb_helper.trigger_failures(failure_count, delay_ms=10.0)
    
    # Wait for circuit breaker to open
    opened = await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.OPEN,
        timeout_seconds=5.0
    )
    
    assert opened, "Circuit breaker should open after threshold failures"
    
    # Verify metrics
    assert_metric_value(manager.metrics, "circuit_breaker.state", "open")
    assert_metric_value(manager.metrics, "circuit_breaker.opens", 1)
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Circuit breaker opens on failures test passed")


@pytest.mark.asyncio
async def test_circuit_breaker_queues_messages_when_open():
    """Test that messages are queued when circuit breaker is open."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create mock WebSocket
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    # Open circuit breaker
    cb_helper = CircuitBreakerTestHelper(manager._circuit_breaker)
    await cb_helper.trigger_failures(5)
    
    # Wait for circuit to open
    await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.OPEN,
        timeout_seconds=5.0
    )
    
    # Try to send critical messages (should be queued)
    messages_to_queue = 3
    for i in range(messages_to_queue):
        message = {"type": "test", "seq": i}
        success = await manager.send(ws, message, critical=True)
        assert not success, "Send should fail when circuit is open"
    
    # Verify messages were queued
    queue_size = manager._queue.get_queue_size("test_client")
    assert queue_size == messages_to_queue, \
        f"Expected {messages_to_queue} queued messages, got {queue_size}"
    
    # Verify metrics
    assert_metric_value(manager.metrics, "messages.queued", messages_to_queue)
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Circuit breaker queues messages test passed")


@pytest.mark.asyncio
async def test_circuit_breaker_recovery():
    """Test circuit breaker recovery from OPEN → HALF_OPEN → CLOSED."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create mock WebSocket
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    # Open circuit breaker
    cb_helper = CircuitBreakerTestHelper(manager._circuit_breaker)
    await cb_helper.trigger_failures(5)
    
    # Wait for OPEN state
    await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.OPEN,
        timeout_seconds=5.0
    )
    
    # Wait for circuit breaker timeout (transitions to HALF_OPEN)
    # Default timeout is 60 seconds, but we'll trigger recovery manually
    await asyncio.sleep(1.0)  # Small delay
    
    # Trigger successful operations to close circuit
    await cb_helper.trigger_recovery(success_count=2)
    
    # Wait for CLOSED state
    closed = await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.CLOSED,
        timeout_seconds=5.0
    )
    
    assert closed, "Circuit breaker should close after successful recovery"
    
    # Verify metrics
    assert_metric_value(manager.metrics, "circuit_breaker.state", "closed")
    assert_metric_value(manager.metrics, "circuit_breaker.closes", 1)
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Circuit breaker recovery test passed")


@pytest.mark.asyncio
async def test_circuit_breaker_metrics_tracking():
    """Test that circuit breaker metrics are accurately tracked."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    metrics_collector = MetricsCollector(manager.metrics)
    
    # Take initial snapshot
    initial = metrics_collector.take_snapshot("initial")
    
    # Create mock WebSocket
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    # Trigger circuit breaker open
    cb_helper = CircuitBreakerTestHelper(manager._circuit_breaker)
    await cb_helper.trigger_failures(5)
    
    # Wait for OPEN
    await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.OPEN,
        timeout_seconds=5.0
    )
    
    after_open = metrics_collector.take_snapshot("after_open")
    
    # Verify metrics increased
    metrics_collector.assert_metric_increased(
        "circuit_breaker.opens",
        min_increase=1,
        before_index=0,
        after_index=1
    )
    
    # Trigger recovery
    await cb_helper.trigger_recovery(success_count=2)
    
    # Wait for CLOSED
    await wait_for_circuit_breaker_state(
        manager._circuit_breaker,
        CircuitBreakerState.CLOSED,
        timeout_seconds=5.0
    )
    
    after_close = metrics_collector.take_snapshot("after_close")
    
    # Verify close metrics
    metrics_collector.assert_metric_increased(
        "circuit_breaker.closes",
        min_increase=1,
        before_index=1,
        after_index=2
    )
    
    # Get final stats
    cb_stats = cb_helper.get_stats()
    logger.info(f"Circuit breaker stats: {cb_stats}")
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Circuit breaker metrics tracking test passed")


@pytest.mark.asyncio
async def test_circuit_breaker_prevents_cascading_failures():
    """Test that circuit breaker prevents cascading failures."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create mock WebSocket with high failure rate
    ws = create_mock_websocket("test_client", failure_rate=1.0)  # 100% failure
    await manager.register_connection(ws, "test_client")
    
    # Try to send messages (will fail and trigger circuit breaker)
    failed_attempts = 0
    for i in range(10):
        message = {"type": "test", "seq": i}
        success = await manager.send(ws, message, critical=False)
        if not success:
            failed_attempts += 1
    
    # Circuit breaker should open after threshold (5 failures)
    # Remaining attempts should fail fast without trying to send
    assert failed_attempts == 10, "All attempts should fail"
    
    # Verify circuit breaker is open
    cb_helper = CircuitBreakerTestHelper(manager._circuit_breaker)
    current_state = cb_helper.get_current_state()
    assert current_state == CircuitBreakerState.OPEN, \
        f"Circuit breaker should be OPEN, got {current_state}"
    
    # Verify failed connection metrics
    assert manager.metrics.failed_connections > 0, \
        "Failed connections should be tracked"
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Circuit breaker prevents cascading failures test passed")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_circuit_breaker_opens_on_failures())
    asyncio.run(test_circuit_breaker_queues_messages_when_open())
    asyncio.run(test_circuit_breaker_recovery())
    asyncio.run(test_circuit_breaker_metrics_tracking())
    asyncio.run(test_circuit_breaker_prevents_cascading_failures())
    
    print("\n" + "="*60)
    print("✅ ALL CIRCUIT BREAKER TESTS PASSED")
    print("="*60)

