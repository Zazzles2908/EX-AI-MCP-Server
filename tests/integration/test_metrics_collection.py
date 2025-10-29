"""
Integration Test: Metrics Collection and Accuracy.

Tests metrics collection functionality including:
- Metrics accuracy across different scenarios
- Snapshot comparison
- Automatic cleanup of inactive clients
- Memory management
- Metrics export

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Integration Tests
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import pytest
import logging
import time

# Import test framework
from framework.websocket_test_utils import create_mock_websocket, create_multiple_mock_clients
from framework.metrics_test_utils import MetricsCollector, assert_metrics_recorded, get_metric_snapshot

# Import system under test
from src.monitoring.resilient_websocket import ResilientWebSocketManager
from src.monitoring.websocket_metrics import WebSocketMetrics

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_metrics_accuracy():
    """Test that metrics accurately reflect system state."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Test metrics accuracy for various operations
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    # Send 10 messages
    for i in range(10):
        await manager.send(ws, {"seq": i}, critical=False)
    
    # Verify exact counts
    assert_metrics_recorded(manager.metrics, {
        "connections.total": 1,
        "connections.active": 1,
        "messages.sent": 10,
        "messages.failed": 0
    })
    
    # Disconnect
    await manager.unregister_connection("test_client")
    
    # Verify disconnection metrics
    assert_metrics_recorded(manager.metrics, {
        "connections.active": 0
    })
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Metrics accuracy test passed")


@pytest.mark.asyncio
async def test_snapshot_comparison():
    """Test metrics snapshot comparison functionality."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    metrics_collector = MetricsCollector(manager.metrics)
    
    # Take initial snapshot
    snapshot1 = metrics_collector.take_snapshot("initial")
    
    # Perform operations
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    for i in range(5):
        await manager.send(ws, {"seq": i}, critical=False)
    
    # Take second snapshot
    snapshot2 = metrics_collector.take_snapshot("after_operations")
    
    # Compare snapshots
    differences = snapshot1.compare_to(snapshot2)
    
    # Verify expected changes
    assert "connections.total" in differences, "Total connections should have changed"
    assert differences["connections.total"]["delta"] == 1, "Should have 1 new connection"
    
    assert "messages.sent" in differences, "Messages sent should have changed"
    assert differences["messages.sent"]["delta"] == 5, "Should have sent 5 messages"
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Snapshot comparison test passed")


@pytest.mark.asyncio
async def test_automatic_cleanup():
    """Test automatic cleanup of inactive client metrics."""
    # Setup with short TTL for testing
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Configure short TTL for testing
    manager.metrics.client_metrics_ttl = 2  # 2 seconds
    manager.metrics.cleanup_interval = 1  # 1 second
    
    # Start automatic cleanup
    manager.metrics.start_automatic_cleanup()
    
    # Create and disconnect multiple clients
    num_clients = 5
    for i in range(num_clients):
        ws = create_mock_websocket(f"client_{i}")
        await manager.register_connection(ws, f"client_{i}")
        await manager.send(ws, {"test": i}, critical=False)
        await manager.unregister_connection(f"client_{i}")
    
    # Verify all clients have metrics
    assert len(manager.metrics.client_metrics) == num_clients, \
        f"Expected {num_clients} client metrics, got {len(manager.metrics.client_metrics)}"
    
    # Wait for cleanup (TTL + cleanup interval + buffer)
    await asyncio.sleep(4.0)
    
    # Verify inactive clients were cleaned up
    remaining_clients = len(manager.metrics.client_metrics)
    assert remaining_clients < num_clients, \
        f"Expected cleanup to remove some clients, still have {remaining_clients}/{num_clients}"
    
    # Stop cleanup
    manager.metrics.stop_automatic_cleanup()
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info(f"✅ Automatic cleanup test passed (cleaned {num_clients - remaining_clients} clients)")


@pytest.mark.asyncio
async def test_memory_management():
    """Test that metrics don't cause memory leaks with many clients."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create many clients
    num_clients = 100
    clients = await create_multiple_mock_clients(num_clients, latency_range=(0.0, 10.0))
    
    # Register all clients
    for i, ws in enumerate(clients):
        await manager.register_connection(ws, f"client_{i}")
    
    # Send messages from all clients
    for i, ws in enumerate(clients):
        for j in range(10):
            await manager.send(ws, {"client": i, "seq": j}, critical=False)
    
    # Verify metrics tracked all clients
    assert len(manager.metrics.client_metrics) == num_clients, \
        f"Expected {num_clients} client metrics"
    
    # Disconnect all clients
    for i in range(num_clients):
        await manager.unregister_connection(f"client_{i}")
    
    # Manual cleanup
    cleaned = manager.metrics.cleanup_inactive_clients(ttl_seconds=0)
    
    # Verify cleanup removed all inactive clients
    assert cleaned == num_clients, \
        f"Expected to clean {num_clients} clients, cleaned {cleaned}"
    
    assert len(manager.metrics.client_metrics) == 0, \
        "All client metrics should be cleaned up"
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info(f"✅ Memory management test passed ({num_clients} clients)")


@pytest.mark.asyncio
async def test_metrics_export():
    """Test metrics export to dictionary format."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    # Perform some operations
    ws = create_mock_websocket("test_client")
    await manager.register_connection(ws, "test_client")
    
    for i in range(5):
        await manager.send(ws, {"seq": i}, critical=False)
    
    # Export metrics
    metrics_dict = manager.metrics.to_dict()
    
    # Verify structure
    assert "connections" in metrics_dict, "Should have connections section"
    assert "messages" in metrics_dict, "Should have messages section"
    assert "queue" in metrics_dict, "Should have queue section"
    assert "retry" in metrics_dict, "Should have retry section"
    assert "circuit_breaker" in metrics_dict, "Should have circuit_breaker section"
    assert "latency" in metrics_dict, "Should have latency section"
    assert "uptime_seconds" in metrics_dict, "Should have uptime"
    
    # Verify values
    assert metrics_dict["connections"]["total"] == 1
    assert metrics_dict["connections"]["active"] == 1
    assert metrics_dict["messages"]["sent"] == 5
    assert metrics_dict["uptime_seconds"] > 0
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Metrics export test passed")


@pytest.mark.asyncio
async def test_per_client_metrics():
    """Test per-client metrics tracking."""
    # Setup
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create multiple clients with different activity levels
    clients_data = [
        ("client_1", 10),  # 10 messages
        ("client_2", 5),   # 5 messages
        ("client_3", 15),  # 15 messages
    ]
    
    for client_id, message_count in clients_data:
        ws = create_mock_websocket(client_id)
        await manager.register_connection(ws, client_id)
        
        for i in range(message_count):
            await manager.send(ws, {"seq": i}, critical=False)
    
    # Verify per-client metrics
    for client_id, expected_count in clients_data:
        client_metrics = manager.metrics.client_metrics.get(client_id)
        assert client_metrics is not None, f"Client {client_id} should have metrics"
        assert client_metrics.messages_sent == expected_count, \
            f"Client {client_id} should have sent {expected_count} messages, got {client_metrics.messages_sent}"
    
    # Cleanup
    await manager.stop_background_tasks()
    
    logger.info("✅ Per-client metrics test passed")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_metrics_accuracy())
    asyncio.run(test_snapshot_comparison())
    asyncio.run(test_automatic_cleanup())
    asyncio.run(test_memory_management())
    asyncio.run(test_metrics_export())
    asyncio.run(test_per_client_metrics())
    
    print("\n" + "="*60)
    print("✅ ALL METRICS COLLECTION TESTS PASSED")
    print("="*60)

