"""
Test Graceful Shutdown for ResilientWebSocketManager

Tests the graceful shutdown implementation including:
1. Flushing pending messages
2. Closing active connections
3. Stopping background tasks
4. Cleaning up metrics
5. Timeout handling

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Validation
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.resilient_websocket import ResilientWebSocketManager, ConnectionState


class MockWebSocket:
    """Mock WebSocket for testing."""
    
    def __init__(self, client_id: str, should_fail: bool = False):
        self.client_id = client_id
        self.should_fail = should_fail
        self.remote_address = ("127.0.0.1", int(client_id.split(":")[-1]))
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.sent_messages = []
    
    async def send(self, message: str):
        """Mock send method."""
        if self.should_fail:
            raise Exception("Mock send failure")
        self.sent_messages.append(message)
        await asyncio.sleep(0.01)  # Simulate network delay
    
    async def close(self, code: int = 1000, reason: str = ""):
        """Mock close method."""
        self.closed = True
        self.close_code = code
        self.close_reason = reason
        await asyncio.sleep(0.01)


async def test_graceful_shutdown_basic():
    """Test basic graceful shutdown without pending messages."""
    print("\n[Test 1] Basic Graceful Shutdown")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    # Create mock connections
    ws1 = MockWebSocket("client:8001")
    ws2 = MockWebSocket("client:8002")
    
    # Register connections
    manager._connections["client:8001"] = ConnectionState(
        websocket=ws1,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    manager._connections["client:8002"] = ConnectionState(
        websocket=ws2,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Perform graceful shutdown
    stats = await manager.graceful_shutdown(
        timeout=5.0,
        flush_pending=True,
        close_connections=True
    )
    
    # Verify results
    assert stats["connections_closed"] == 2, f"Expected 2 connections closed, got {stats['connections_closed']}"
    assert stats["background_tasks_stopped"] == 2, f"Expected 2 tasks stopped, got {stats['background_tasks_stopped']}"
    assert stats["metrics_cleaned"] == True, "Expected metrics to be cleaned"
    assert ws1.closed and ws2.closed, "Expected all connections to be closed"
    assert ws1.close_code == 1001, f"Expected close code 1001, got {ws1.close_code}"
    assert "shutting down" in ws1.close_reason.lower(), f"Expected shutdown reason, got {ws1.close_reason}"
    
    print(f"✅ PASS: Basic shutdown completed in {stats['duration_seconds']:.2f}s")
    print(f"  - Connections closed: {stats['connections_closed']}")
    print(f"  - Background tasks stopped: {stats['background_tasks_stopped']}")
    print(f"  - Metrics cleaned: {stats['metrics_cleaned']}")
    return True


async def test_graceful_shutdown_with_pending_messages():
    """Test graceful shutdown with pending messages."""
    print("\n[Test 2] Graceful Shutdown with Pending Messages")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create mock connection
    ws = MockWebSocket("client:8003")
    manager._connections["client:8003"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Queue some messages
    for i in range(5):
        await manager._queue.enqueue(
            client_id="client:8003",
            message={"content": f"test_message_{i}"}
        )
    
    # Verify messages are queued
    queue_size = manager._queue.get_queue_size("client:8003")
    assert queue_size == 5, f"Expected 5 queued messages, got {queue_size}"
    
    # Perform graceful shutdown
    stats = await manager.graceful_shutdown(
        timeout=10.0,
        flush_pending=True,
        close_connections=True
    )
    
    # Verify results
    assert stats["pending_messages_flushed"] == 5, f"Expected 5 messages flushed, got {stats['pending_messages_flushed']}"
    assert stats["pending_messages_dropped"] == 0, f"Expected 0 messages dropped, got {stats['pending_messages_dropped']}"
    assert len(ws.sent_messages) == 5, f"Expected 5 sent messages, got {len(ws.sent_messages)}"
    assert ws.closed, "Expected connection to be closed"
    
    print(f"✅ PASS: Shutdown with pending messages completed in {stats['duration_seconds']:.2f}s")
    print(f"  - Messages flushed: {stats['pending_messages_flushed']}")
    print(f"  - Messages dropped: {stats['pending_messages_dropped']}")
    print(f"  - Messages sent: {len(ws.sent_messages)}")
    return True


async def test_graceful_shutdown_with_failed_flush():
    """Test graceful shutdown when message flush fails."""
    print("\n[Test 3] Graceful Shutdown with Failed Flush")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=False,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create mock connection that fails on send
    ws = MockWebSocket("client:8004", should_fail=True)
    manager._connections["client:8004"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Queue some messages
    for i in range(3):
        await manager._queue.enqueue(
            client_id="client:8004",
            message={"content": f"test_message_{i}"}
        )
    
    # Perform graceful shutdown
    stats = await manager.graceful_shutdown(
        timeout=5.0,
        flush_pending=True,
        close_connections=True
    )
    
    # Verify results - messages should be dropped due to send failures
    assert stats["pending_messages_flushed"] == 0, f"Expected 0 messages flushed, got {stats['pending_messages_flushed']}"
    assert stats["pending_messages_dropped"] == 3, f"Expected 3 messages dropped, got {stats['pending_messages_dropped']}"
    assert ws.closed, "Expected connection to be closed"
    
    print(f"✅ PASS: Shutdown with failed flush completed in {stats['duration_seconds']:.2f}s")
    print(f"  - Messages flushed: {stats['pending_messages_flushed']}")
    print(f"  - Messages dropped: {stats['pending_messages_dropped']}")
    return True


async def test_graceful_shutdown_timeout():
    """Test graceful shutdown with timeout."""
    print("\n[Test 4] Graceful Shutdown with Timeout")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=False,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create mock connection with slow send
    ws = MockWebSocket("client:8005")
    original_send = ws.send
    
    async def slow_send(message: str):
        await asyncio.sleep(2.0)  # Simulate slow send
        await original_send(message)
    
    ws.send = slow_send
    
    manager._connections["client:8005"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Queue many messages
    for i in range(10):
        await manager._queue.enqueue(
            client_id="client:8005",
            message={"content": f"test_message_{i}"}
        )
    
    # Perform graceful shutdown with short timeout
    stats = await manager.graceful_shutdown(
        timeout=3.0,  # Short timeout
        flush_pending=True,
        close_connections=True
    )
    
    # Verify results - some messages should be dropped due to timeout
    total_messages = stats["pending_messages_flushed"] + stats["pending_messages_dropped"]
    # Allow for race conditions - should be close to 10 messages
    assert total_messages >= 9 and total_messages <= 10, f"Expected 9-10 total messages, got {total_messages}"
    assert stats["pending_messages_dropped"] > 0, "Expected some messages to be dropped due to timeout"
    assert ws.closed, "Expected connection to be closed"
    
    print(f"✅ PASS: Shutdown with timeout completed in {stats['duration_seconds']:.2f}s")
    print(f"  - Messages flushed: {stats['pending_messages_flushed']}")
    print(f"  - Messages dropped: {stats['pending_messages_dropped']}")
    print(f"  - Total messages: {total_messages}")
    return True


async def test_graceful_shutdown_no_flush():
    """Test graceful shutdown without flushing pending messages."""
    print("\n[Test 5] Graceful Shutdown without Flush")
    print("-" * 60)
    
    manager = ResilientWebSocketManager(
        enable_metrics=False,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Create mock connection
    ws = MockWebSocket("client:8006")
    manager._connections["client:8006"] = ConnectionState(
        websocket=ws,
        is_connected=True,
        retry_count=0,
        last_message_time=time.time()
    )
    
    # Queue some messages
    for i in range(5):
        await manager._queue.enqueue(
            client_id="client:8006",
            message={"content": f"test_message_{i}"}
        )
    
    # Perform graceful shutdown without flushing
    stats = await manager.graceful_shutdown(
        timeout=5.0,
        flush_pending=False,  # Don't flush
        close_connections=True
    )
    
    # Verify results - no messages should be flushed
    assert stats["pending_messages_flushed"] == 0, f"Expected 0 messages flushed, got {stats['pending_messages_flushed']}"
    assert stats["pending_messages_dropped"] == 0, f"Expected 0 messages dropped, got {stats['pending_messages_dropped']}"
    assert len(ws.sent_messages) == 0, f"Expected 0 sent messages, got {len(ws.sent_messages)}"
    assert ws.closed, "Expected connection to be closed"
    
    print(f"✅ PASS: Shutdown without flush completed in {stats['duration_seconds']:.2f}s")
    print(f"  - Messages flushed: {stats['pending_messages_flushed']}")
    print(f"  - Connections closed: {stats['connections_closed']}")
    return True


async def main():
    """Run all graceful shutdown tests."""
    print("=" * 60)
    print("Graceful Shutdown Tests - Week 1.5 Validation")
    print("=" * 60)
    
    tests = [
        test_graceful_shutdown_basic,
        test_graceful_shutdown_with_pending_messages,
        test_graceful_shutdown_with_failed_flush,
        test_graceful_shutdown_timeout,
        test_graceful_shutdown_no_flush
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
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{len(tests)} passed, {failed}/{len(tests)} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

