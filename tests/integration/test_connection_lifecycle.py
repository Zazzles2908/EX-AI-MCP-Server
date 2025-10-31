"""
Integration Test: WebSocket Connection Lifecycle.

Tests the full lifecycle of WebSocket connections including:
- Connection establishment
- Message sending and receiving
- Metrics tracking throughout lifecycle
- Graceful disconnection
- Resource cleanup

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import pytest
import logging
from typing import List

# Import test framework
from framework.websocket_test_utils import create_mock_websocket, MockWebSocket
from framework.metrics_test_utils import MetricsCollector, assert_metric_value

# Import system under test
from src.monitoring.resilient_websocket import ResilientWebSocketManager
from src.monitoring.websocket_metrics import WebSocketMetrics

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_single_connection_lifecycle():
    """Test complete lifecycle of a single WebSocket connection."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,  # Disable for basic lifecycle test
        enable_deduplication=False
    )
    
    metrics_collector = MetricsCollector(manager.metrics)
    
    # Take initial snapshot
    initial_snapshot = metrics_collector.take_snapshot("initial")
    
    # Create mock WebSocket
    ws = create_mock_websocket("test_client_1", latency_ms=10.0)
    
    # Test 1: Connection establishment
    await manager.register_connection(ws, "test_client_1")
    
    # Verify connection metrics
    after_connect = metrics_collector.take_snapshot("after_connect")
    assert_metric_value(manager.metrics, "connections.total", 1)
    assert_metric_value(manager.metrics, "connections.active", 1)
    
    # Test 2: Send messages
    messages_to_send = 10
    for i in range(messages_to_send):
        message = {"type": "test", "sequence": i, "data": f"message_{i}"}
        success = await manager.send(ws, message, critical=False)
        assert success, f"Failed to send message {i}"
    
    # Verify message metrics
    after_send = metrics_collector.take_snapshot("after_send")
    assert_metric_value(manager.metrics, "messages.sent", messages_to_send)
    
    # Verify latency tracking
    avg_latency = manager.metrics.get_average_send_latency()
    assert avg_latency > 0, "Average latency should be tracked"
    assert avg_latency >= 10.0, f"Expected latency >= 10ms, got {avg_latency}ms"
    
    # Test 3: Graceful disconnection
    await manager.unregister_connection("test_client_1")
    
    # Verify disconnection metrics
    after_disconnect = metrics_collector.take_snapshot("after_disconnect")
    assert_metric_value(manager.metrics, "connections.active", 0)
    
    # Test 4: Verify metrics progression
    differences = metrics_collector.compare_snapshots(0, -1)
    logger.info(f"Metrics changes: {differences}")
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Single connection lifecycle test passed")


@pytest.mark.asyncio
async def test_multiple_concurrent_connections():
    """Test multiple concurrent WebSocket connections."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create multiple mock clients
    num_clients = 10
    clients: List[MockWebSocket] = []
    
    for i in range(num_clients):
        ws = create_mock_websocket(f"client_{i}", latency_ms=5.0)
        clients.append(ws)
        await manager.register_connection(ws, f"client_{i}")
    
    # Verify all connections registered
    assert_metric_value(manager.metrics, "connections.total", num_clients)
    assert_metric_value(manager.metrics, "connections.active", num_clients)
    
    # Send messages from all clients concurrently
    messages_per_client = 5
    
    async def send_messages_for_client(ws: MockWebSocket, client_id: str):
        for i in range(messages_per_client):
            message = {"type": "test", "client": client_id, "seq": i}
            await manager.send(ws, message, critical=False)
    
    # Send messages concurrently
    tasks = [
        send_messages_for_client(ws, f"client_{i}")
        for i, ws in enumerate(clients)
    ]
    await asyncio.gather(*tasks)
    
    # Verify message count
    expected_messages = num_clients * messages_per_client
    assert_metric_value(manager.metrics, "messages.sent", expected_messages)
    
    # Disconnect all clients
    for i in range(num_clients):
        await manager.unregister_connection(f"client_{i}")
    
    # Verify all disconnected
    assert_metric_value(manager.metrics, "connections.active", 0)
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info(f"✅ Multiple concurrent connections test passed ({num_clients} clients)")


@pytest.mark.asyncio
async def test_connection_with_graceful_shutdown():
    """Test graceful shutdown during active connections."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    await manager.start_background_tasks()
    
    # Create active connections
    num_clients = 5
    clients: List[MockWebSocket] = []
    
    for i in range(num_clients):
        ws = create_mock_websocket(f"client_{i}")
        clients.append(ws)
        await manager.register_connection(ws, f"client_{i}")
    
    # Queue some messages
    for i, ws in enumerate(clients):
        message = {"type": "test", "client": f"client_{i}"}
        await manager.send(ws, message, critical=True)
    
    # Perform graceful shutdown
    shutdown_stats = await manager.graceful_shutdown(
        timeout=10.0,
        flush_pending=True,
        close_connections=True
    )
    
    # Verify shutdown statistics
    assert shutdown_stats["connections_closed"] == num_clients, \
        f"Expected {num_clients} connections closed, got {shutdown_stats['connections_closed']}"
    
    assert shutdown_stats["background_tasks_stopped"] == 2, \
        "Expected 2 background tasks stopped (retry + cleanup)"
    
    assert shutdown_stats["metrics_cleaned"] is True, \
        "Metrics should be cleaned up"
    
    assert shutdown_stats["duration_seconds"] < 10.0, \
        f"Shutdown took {shutdown_stats['duration_seconds']}s, expected <10s"
    
    logger.info(f"✅ Graceful shutdown test passed: {shutdown_stats}")


@pytest.mark.asyncio
async def test_metrics_accuracy_during_lifecycle():
    """Test that metrics accurately track connection lifecycle events."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    metrics_collector = MetricsCollector(manager.metrics)
    
    # Test sequence: connect → send → disconnect → reconnect
    ws = create_mock_websocket("test_client")
    
    # Step 1: Initial connection
    initial = metrics_collector.take_snapshot("initial")
    await manager.register_connection(ws, "test_client")
    after_connect = metrics_collector.take_snapshot("after_connect")
    
    metrics_collector.assert_metric_increased("connections.total", min_increase=1, before_index=0, after_index=1)
    metrics_collector.assert_metric_increased("connections.active", min_increase=1, before_index=0, after_index=1)
    
    # Step 2: Send messages
    for i in range(5):
        await manager.send(ws, {"seq": i}, critical=False)
    
    after_send = metrics_collector.take_snapshot("after_send")
    metrics_collector.assert_metric_increased("messages.sent", min_increase=5, before_index=1, after_index=2)
    
    # Step 3: Disconnect
    await manager.unregister_connection("test_client")
    after_disconnect = metrics_collector.take_snapshot("after_disconnect")
    
    # Active connections should decrease
    assert after_disconnect.get("connections.active") == 0, \
        "Active connections should be 0 after disconnect"
    
    # Step 4: Reconnect
    ws2 = create_mock_websocket("test_client")
    await manager.register_connection(ws2, "test_client")
    after_reconnect = metrics_collector.take_snapshot("after_reconnect")
    
    # Total connections should increase again
    metrics_collector.assert_metric_increased("connections.total", min_increase=1, before_index=3, after_index=4)
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Metrics accuracy test passed")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_single_connection_lifecycle())
    asyncio.run(test_multiple_concurrent_connections())
    asyncio.run(test_connection_with_graceful_shutdown())
    asyncio.run(test_metrics_accuracy_during_lifecycle())
    
    print("\n" + "="*60)
    print("✅ ALL CONNECTION LIFECYCLE TESTS PASSED")
    print("="*60)

