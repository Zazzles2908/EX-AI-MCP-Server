"""
Integration Tests for WebSocket Stability Enhancements

Tests the complete lifecycle of WebSocket stability features:
1. Full connection lifecycle (connect → send → disconnect → reconnect)
2. Multi-client scenarios (concurrent connections)
3. Failure recovery (network failures, timeouts)
4. Memory cleanup validation (metrics, deduplication cache)
5. Circuit breaker integration
6. Message deduplication across reconnections

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Integration Testing
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.resilient_websocket import ResilientWebSocketManager, ConnectionState
from src.monitoring.websocket_config import WebSocketStabilityConfig


class MockWebSocket:
    """Mock WebSocket for integration testing."""
    
    def __init__(self, client_id: str, fail_after: int = -1):
        self.client_id = client_id
        self.remote_address = ("127.0.0.1", int(client_id.split(":")[-1]))
        self.closed = False
        self.sent_messages = []
        self.fail_after = fail_after  # Fail after N sends (-1 = never fail)
        self.send_count = 0
    
    async def send(self, message: str):
        """Mock send with optional failure."""
        self.send_count += 1
        if self.fail_after > 0 and self.send_count > self.fail_after:
            raise Exception(f"Mock connection failure after {self.fail_after} sends")
        self.sent_messages.append(message)
        await asyncio.sleep(0.01)  # Simulate network delay
    
    async def close(self, code: int = 1000, reason: str = ""):
        """Mock close."""
        self.closed = True
        await asyncio.sleep(0.01)


async def test_full_lifecycle():
    """Test complete connection lifecycle."""
    print("\n[Test 1] Full Connection Lifecycle")
    print("-" * 60)
    
    config = WebSocketStabilityConfig.testing()
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    # Step 1: Register connection
    ws = MockWebSocket("client:9001")
    manager._connections["client:9001"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Step 2: Send messages
    for i in range(5):
        await manager.send(
            client_id="client:9001",
            message={"type": "test", "data": f"message_{i}"}
        )
    
    # Step 3: Verify messages sent
    assert len(ws.sent_messages) == 5, f"Expected 5 messages, got {len(ws.sent_messages)}"
    
    # Step 4: Disconnect
    manager._connections["client:9001"].is_connected = False
    
    # Step 5: Queue messages while disconnected
    for i in range(3):
        await manager.send(
            client_id="client:9001",
            message={"type": "test", "data": f"queued_{i}"}
        )
    
    # Step 6: Verify messages queued
    queue_size = manager._queue.get_queue_size("client:9001")
    assert queue_size == 3, f"Expected 3 queued messages, got {queue_size}"
    
    # Step 7: Reconnect
    manager._connections["client:9001"].is_connected = True
    manager._connections["client:9001"].websocket = ws
    
    # Step 8: Process queued messages
    await manager._process_pending_messages("client:9001")
    
    # Step 9: Verify all messages sent
    assert len(ws.sent_messages) == 8, f"Expected 8 total messages, got {len(ws.sent_messages)}"
    
    # Step 10: Graceful shutdown
    stats = await manager.graceful_shutdown()
    assert stats["connections_closed"] == 1
    
    print(f"✅ PASS: Full lifecycle completed")
    print(f"  - Messages sent: {len(ws.sent_messages)}")
    print(f"  - Queue processed: {queue_size}")
    print(f"  - Shutdown duration: {stats['duration_seconds']:.2f}s")
    return True


async def test_multi_client_concurrent():
    """Test concurrent multi-client connections."""
    print("\n[Test 2] Multi-Client Concurrent Connections")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create 10 concurrent clients
    clients = []
    for i in range(10):
        client_id = f"client:900{i}"
        ws = MockWebSocket(client_id)
        manager._connections[client_id] = ConnectionState(
            websocket=ws,
            is_connected=True,
            retry_count=0,
            last_message_time=time.time()
        )
        clients.append((client_id, ws))
    
    # Send messages concurrently from all clients
    async def send_messages(client_id: str, count: int):
        for i in range(count):
            await manager.send(
                client_id=client_id,
                message={"type": "test", "data": f"msg_{i}"}
            )
    
    # Send 5 messages from each client concurrently
    tasks = [send_messages(client_id, 5) for client_id, _ in clients]
    await asyncio.gather(*tasks)
    
    # Verify all messages sent
    total_sent = sum(len(ws.sent_messages) for _, ws in clients)
    assert total_sent == 50, f"Expected 50 messages, got {total_sent}"
    
    # Verify metrics
    if manager.metrics:
        assert manager.metrics.messages_sent == 50
        assert manager.metrics.active_connections == 10
    
    # Shutdown
    stats = await manager.graceful_shutdown()
    assert stats["connections_closed"] == 10
    
    print(f"✅ PASS: Multi-client test completed")
    print(f"  - Total messages sent: {total_sent}")
    print(f"  - Connections closed: {stats['connections_closed']}")
    return True


async def test_failure_recovery():
    """Test failure recovery with circuit breaker."""
    print("\n[Test 3] Failure Recovery with Circuit Breaker")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=False
    )
    
    # Create client that fails after 3 sends
    ws = MockWebSocket("client:9010", fail_after=3)
    manager._connections["client:9010"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Send messages until failure
    success_count = 0
    failure_count = 0
    
    for i in range(10):
        try:
            await manager.send(
                client_id="client:9010",
                message={"type": "test", "data": f"msg_{i}"}
            )
            success_count += 1
        except Exception:
            failure_count += 1
    
    # Verify some succeeded and some failed
    assert success_count > 0, "Expected some messages to succeed"
    assert failure_count > 0, "Expected some messages to fail"
    
    # Verify circuit breaker state
    if manager._circuit_breaker:
        stats = manager._circuit_breaker.get_stats()
        print(f"  - Circuit breaker state: {stats['state']}")
        print(f"  - Failure count: {stats['failure_count']}")
    
    # Shutdown
    await manager.graceful_shutdown()
    
    print(f"✅ PASS: Failure recovery completed")
    print(f"  - Successful sends: {success_count}")
    print(f"  - Failed sends: {failure_count}")
    return True


async def test_memory_cleanup():
    """Test memory cleanup for metrics and deduplication cache."""
    print("\n[Test 4] Memory Cleanup Validation")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=True
    )
    
    # Create multiple clients
    for i in range(5):
        client_id = f"client:901{i}"
        ws = MockWebSocket(client_id)
        manager._connections[client_id] = ConnectionState(
            websocket=ws,
            is_connected=True,
            retry_count=0,
            last_message_time=time.time()
        )
    
    # Send messages to create metrics
    for i in range(5):
        client_id = f"client:901{i}"
        await manager.send(
            client_id=client_id,
            message={"type": "test", "data": "message"}
        )
    
    # Verify metrics created
    if manager.metrics:
        initial_client_count = len(manager.metrics.client_metrics)
        assert initial_client_count == 5, f"Expected 5 client metrics, got {initial_client_count}"
    
    # Simulate time passing (make clients inactive)
    for client_id in list(manager._connections.keys()):
        manager._connections[client_id].last_message_time = time.time() - 7200  # 2 hours ago
    
    # Trigger cleanup
    if manager.metrics:
        cleaned = manager.metrics.cleanup_inactive_clients(ttl=3600)  # 1 hour TTL
        assert cleaned == 5, f"Expected 5 clients cleaned, got {cleaned}"
        
        # Verify cleanup worked
        remaining = len(manager.metrics.client_metrics)
        assert remaining == 0, f"Expected 0 remaining clients, got {remaining}"
    
    # Shutdown
    await manager.graceful_shutdown()
    
    print(f"✅ PASS: Memory cleanup validated")
    print(f"  - Initial clients: {initial_client_count}")
    print(f"  - Cleaned clients: {cleaned}")
    print(f"  - Remaining clients: {remaining}")
    return True


async def test_message_deduplication_across_reconnection():
    """Test message deduplication prevents duplicates during reconnection."""
    print("\n[Test 5] Message Deduplication Across Reconnection")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=False,
        enable_circuit_breaker=False,
        enable_deduplication=True
    )
    
    # Create client
    ws = MockWebSocket("client:9020")
    manager._connections["client:9020"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Send same message multiple times
    message = {"type": "test", "data": "duplicate_test"}
    
    for i in range(5):
        await manager.send(
            client_id="client:9020",
            message=message
        )
    
    # Verify only 1 message sent (others deduplicated)
    assert len(ws.sent_messages) == 1, f"Expected 1 message (deduplicated), got {len(ws.sent_messages)}"
    
    # Disconnect and reconnect
    manager._connections["client:9020"].is_connected = False
    await asyncio.sleep(0.1)
    manager._connections["client:9020"].is_connected = True
    
    # Try sending same message again after reconnection
    await manager.send(
        client_id="client:9020",
        message=message
    )
    
    # Should still be deduplicated (within TTL)
    assert len(ws.sent_messages) == 1, f"Expected 1 message (still deduplicated), got {len(ws.sent_messages)}"
    
    # Shutdown
    await manager.graceful_shutdown()
    
    print(f"✅ PASS: Message deduplication validated")
    print(f"  - Messages sent: {len(ws.sent_messages)}")
    print(f"  - Deduplication working: Yes")
    return True


async def main():
    """Run all integration tests."""
    print("=" * 60)
    print("WebSocket Stability Integration Tests - Week 1.5")
    print("=" * 60)
    
    tests = [
        test_full_lifecycle,
        test_multi_client_concurrent,
        test_failure_recovery,
        test_memory_cleanup,
        test_message_deduplication_across_reconnection
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ FAIL: {test.__name__} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Integration Test Results: {passed}/{len(tests)} passed, {failed}/{len(tests)} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

