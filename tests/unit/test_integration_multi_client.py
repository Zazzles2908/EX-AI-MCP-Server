"""
Integration Test: Multi-Client Concurrent Access

Tests concurrent access with multiple clients:
- Multiple clients connecting simultaneously
- Per-client metrics tracking
- Deduplication across clients
- Memory cleanup for disconnected clients
- Circuit breaker behavior with multiple clients

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Phase 1 (Integration Tests)
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.monitoring.resilient_websocket import ResilientWebSocketManager


async def simulate_client(manager, client_id: str, num_messages: int):
    """Simulate a client sending messages."""
    # Connect
    if manager.metrics:
        manager.metrics.record_connection(client_id)
    
    # Send messages
    for i in range(num_messages):
        message = {"type": "test", "client": client_id, "seq": i}
        message_id = manager._get_message_id(message)
        
        # Check deduplication
        is_dup = manager._is_duplicate_message(message_id)
        
        # Track metrics
        if manager.metrics:
            manager.metrics.record_message_sent(client_id, latency_ms=5.0 + i)
        
        # Small delay to simulate real traffic
        await asyncio.sleep(0.01)
    
    # Disconnect
    if manager.metrics:
        manager.metrics.record_disconnection(client_id)
    
    return client_id


async def test_multi_client():
    """Test multiple clients with concurrent access."""
    print("\n" + "="*60)
    print("Integration Test: Multi-Client Concurrent Access")
    print("="*60)
    
    # Initialize WebSocket manager
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    num_clients = 10
    messages_per_client = 5
    
    print(f"\n[1/5] Testing {num_clients} concurrent clients...")
    
    # Create tasks for all clients
    tasks = [
        simulate_client(manager, f"client-{i}", messages_per_client)
        for i in range(num_clients)
    ]
    
    # Run all clients concurrently
    results = await asyncio.gather(*tasks)
    
    print(f"✅ All {len(results)} clients completed")
    
    print("\n[2/5] Verifying per-client metrics...")
    if manager.metrics:
        # Check total connections
        assert manager.metrics.total_connections == num_clients, \
            f"Expected {num_clients} connections, got {manager.metrics.total_connections}"
        
        # Check all clients disconnected
        assert manager.metrics.active_connections == 0, \
            f"Expected 0 active connections, got {manager.metrics.active_connections}"
        
        # Check total messages
        expected_messages = num_clients * messages_per_client
        assert manager.metrics.messages_sent == expected_messages, \
            f"Expected {expected_messages} messages, got {manager.metrics.messages_sent}"
        
        # Check per-client metrics exist
        assert len(manager.metrics.client_metrics) == num_clients, \
            f"Expected {num_clients} client metrics, got {len(manager.metrics.client_metrics)}"
        
        print(f"✅ Per-client metrics tracked correctly")
        print(f"   Total connections: {manager.metrics.total_connections}")
        print(f"   Total messages: {manager.metrics.messages_sent}")
        print(f"   Client metrics: {len(manager.metrics.client_metrics)}")
    
    print("\n[3/5] Testing deduplication across clients...")
    # Send same message from different clients
    test_message = {"type": "shared", "data": "test"}
    
    for i in range(3):
        client_id = f"dedup-client-{i}"
        if manager.metrics:
            manager.metrics.record_connection(client_id)
        
        message_id = manager._get_message_id(test_message)
        is_dup = manager._is_duplicate_message(message_id)
        
        if i == 0:
            assert not is_dup, "First client should not see duplicate"
        else:
            assert is_dup, f"Client {i} should see duplicate"
        
        if manager.metrics:
            manager.metrics.record_disconnection(client_id)
    
    print("✅ Deduplication works across clients")
    
    print("\n[4/5] Testing memory cleanup for disconnected clients...")
    if manager.metrics:
        # Set short TTL for testing
        manager.metrics.client_metrics_ttl = 1
        
        # Wait for TTL to expire
        await asyncio.sleep(1.5)
        
        # Run cleanup
        removed = manager.metrics.cleanup_inactive_clients()
        
        print(f"✅ Cleaned up {removed} inactive clients")
        assert removed >= num_clients, f"Expected at least {num_clients} removed, got {removed}"
    
    print("\n[5/5] Testing circuit breaker with multiple clients...")
    if manager._circuit_breaker:
        # Import CircuitState
        from src.monitoring.circuit_breaker import CircuitState

        # Reset circuit breaker
        await manager._circuit_breaker._change_state(CircuitState.CLOSED)

        # Simulate failures from multiple clients
        for i in range(5):
            await manager._circuit_breaker._on_failure()

        # Circuit should be OPEN
        assert manager._circuit_breaker.state == CircuitState.OPEN, \
            "Circuit should be OPEN after failures"

        print(f"✅ Circuit breaker opened (state: {manager._circuit_breaker.state})")
    
    # Print final metrics
    if manager.metrics:
        print("\n" + "-"*60)
        print("Final Metrics:")
        print("-"*60)
        metrics = manager.metrics.to_dict()
        print(f"Total Connections: {metrics['connections']['total']}")
        print(f"Failed Connections: {metrics['connections']['failed']}")
        print(f"Messages Sent: {metrics['messages']['sent']}")
        print(f"Messages Deduplicated: {metrics['messages']['deduplicated']}")
        print(f"Average Latency: {metrics['latency']['average_send_ms']:.2f}ms")
    
    print("\n" + "="*60)
    print("✅ MULTI-CLIENT TEST PASSED")
    print("="*60)
    return True


async def main():
    """Run the integration test."""
    try:
        success = await test_multi_client()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

