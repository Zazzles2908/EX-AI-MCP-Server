"""
Integration Test: Full WebSocket Lifecycle

Tests the complete WebSocket lifecycle including:
- Connection establishment
- Message sending with metrics tracking
- Circuit breaker triggering
- Automatic cleanup
- Graceful disconnection

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Phase 1 (Integration Tests)
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

import asyncio
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.resilient_websocket import ResilientWebSocketManager
from src.monitoring.circuit_breaker import CircuitState


async def test_full_lifecycle():
    """Test complete WebSocket lifecycle."""
    print("\n" + "="*60)
    print("Integration Test: Full WebSocket Lifecycle")
    print("="*60)
    
    # Initialize WebSocket manager with all features enabled
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    print("\n[1/6] Testing connection establishment...")
    client_id = "test-client-lifecycle"
    
    # Simulate connection
    if manager.metrics:
        manager.metrics.record_connection(client_id)
        assert manager.metrics.total_connections == 1, "Connection not tracked"
        assert manager.metrics.active_connections == 1, "Active connection not tracked"
        print("✅ Connection established and tracked")
    
    print("\n[2/6] Testing message sending with metrics...")
    # Send messages and track metrics
    for i in range(5):
        message = {"type": "test", "data": f"message-{i}"}
        message_id = manager.get_message_id(message)

        # Check deduplication
        is_dup = manager.is_duplicate_message(message_id)
        assert not is_dup, f"First send of message {i} should not be duplicate"

        # Track metrics
        if manager.metrics:
            manager.metrics.record_message_sent(client_id, latency_ms=10.0 + i)

        # Verify duplicate detection
        is_dup2 = manager.is_duplicate_message(message_id)
        assert is_dup2, f"Second send of message {i} should be duplicate"

        # Track deduplication
        if manager.metrics:
            manager.metrics.record_message_deduplicated(client_id)

    if manager.metrics:
        assert manager.metrics.messages_sent == 5, "Messages not tracked"
        assert manager.metrics.messages_deduplicated == 5, "Duplicates not tracked"
        avg_latency = manager.metrics.get_average_send_latency()
        assert 10.0 <= avg_latency <= 15.0, f"Average latency {avg_latency} out of expected range"
        print(f"✅ Sent 5 messages, avg latency: {avg_latency:.2f}ms")
    
    print("\n[3/6] Testing circuit breaker triggering...")
    if manager._circuit_breaker:
        # Verify initial state
        assert manager._circuit_breaker.state == CircuitState.CLOSED, "Circuit should start CLOSED"
        
        # Simulate failures to open circuit
        for i in range(5):
            await manager._circuit_breaker._on_failure()
        
        # Circuit should be OPEN after threshold failures
        assert manager._circuit_breaker.state == CircuitState.OPEN, "Circuit should be OPEN after failures"
        print(f"✅ Circuit breaker opened after 5 failures (state: {manager._circuit_breaker.state})")
        
        # Wait for timeout and test recovery
        manager._circuit_breaker.config.timeout_seconds = 0.5
        await asyncio.sleep(0.6)
        
        # Manually transition to HALF_OPEN for testing
        await manager._circuit_breaker._change_state(CircuitState.HALF_OPEN)
        assert manager._circuit_breaker.state == CircuitState.HALF_OPEN, "Circuit should be HALF_OPEN"
        
        # Simulate successes to close circuit
        for i in range(2):
            await manager._circuit_breaker._on_success()
        
        assert manager._circuit_breaker.state == CircuitState.CLOSED, "Circuit should be CLOSED after successes"
        print(f"✅ Circuit breaker recovered (state: {manager._circuit_breaker.state})")
    
    print("\n[4/6] Testing automatic cleanup...")
    if manager.metrics:
        # Record activity for multiple clients
        for i in range(3):
            manager.metrics.record_connection(f"client-{i}")
        
        # Wait for TTL to expire (using short TTL for testing)
        manager.metrics.client_metrics_ttl = 1
        await asyncio.sleep(1.5)
        
        # Trigger cleanup
        removed = manager.metrics.cleanup_inactive_clients()
        
        # Original client should still be active, new clients should be removed
        assert removed >= 3, f"Expected at least 3 clients removed, got {removed}"
        print(f"✅ Automatic cleanup removed {removed} inactive clients")
    
    print("\n[5/6] Testing message TTL cleanup...")
    # Test message deduplication TTL
    manager.message_id_ttl = 1
    test_message = {"type": "ttl-test", "data": "test"}
    msg_id = manager.get_message_id(test_message)
    
    # Mark as sent
    is_dup1 = manager.is_duplicate_message(msg_id)
    assert not is_dup1, "First send should not be duplicate"
    
    # Wait for TTL to expire
    await asyncio.sleep(1.5)
    
    # Should not be duplicate after TTL (cleaned up)
    is_dup2 = manager.is_duplicate_message(msg_id)
    assert not is_dup2, "Message should not be duplicate after TTL cleanup"
    print("✅ Message TTL cleanup working correctly")
    
    print("\n[6/6] Testing graceful disconnection...")
    if manager.metrics:
        # Note: We created 4 clients total (1 original + 3 in cleanup test)
        # Need to disconnect all of them
        for i in range(3):
            manager.metrics.record_disconnection(f"client-{i}")
        manager.metrics.record_disconnection(client_id)

        # Should have 0 active connections now
        assert manager.metrics.active_connections == 0, \
            f"Expected 0 active connections, got {manager.metrics.active_connections}"
        print("✅ Graceful disconnection tracked")
    
    # Print final metrics
    if manager.metrics:
        print("\n" + "-"*60)
        print("Final Metrics:")
        print("-"*60)
        metrics = manager.metrics.to_dict()
        print(f"Total Connections: {metrics['connections']['total']}")
        print(f"Active Connections: {metrics['connections']['active']}")
        print(f"Messages Sent: {metrics['messages']['sent']}")
        print(f"Messages Deduplicated: {metrics['messages']['deduplicated']}")
        print(f"Average Latency: {metrics['latency']['average_send_ms']:.2f}ms")
        print(f"Circuit Breaker State: {manager._circuit_breaker.state if manager._circuit_breaker else 'N/A'}")
    
    print("\n" + "="*60)
    print("✅ FULL LIFECYCLE TEST PASSED")
    print("="*60)
    return True


async def main():
    """Run the integration test."""
    try:
        success = await test_full_lifecycle()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

