"""
Integration Test: Memory Cleanup Under Load

Tests memory management under load:
- Create 100+ clients and disconnect them
- Verify automatic cleanup removes inactive clients
- Test memory usage doesn't grow unbounded
- Validate TTL-based cleanup works under load
- Test cleanup performance with large client counts

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


async def test_memory_cleanup():
    """Test memory cleanup under load."""
    print("\n" + "="*60)
    print("Integration Test: Memory Cleanup Under Load")
    print("="*60)
    
    # Initialize WebSocket manager
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=True,
        enable_deduplication=True
    )
    
    num_clients = 100
    
    print(f"\n[1/5] Creating {num_clients} clients...")
    
    # Create and connect many clients
    for i in range(num_clients):
        client_id = f"load-client-{i}"
        if manager.metrics:
            manager.metrics.record_connection(client_id)
            
            # Send a few messages per client
            for j in range(3):
                manager.metrics.record_message_sent(client_id, latency_ms=5.0)
    
    if manager.metrics:
        assert manager.metrics.total_connections == num_clients, \
            f"Expected {num_clients} connections, got {manager.metrics.total_connections}"
        assert manager.metrics.active_connections == num_clients, \
            f"Expected {num_clients} active connections, got {manager.metrics.active_connections}"
        
        print(f"✅ Created {num_clients} clients")
        print(f"   Total connections: {manager.metrics.total_connections}")
        print(f"   Active connections: {manager.metrics.active_connections}")
        print(f"   Client metrics tracked: {len(manager.metrics.client_metrics)}")
    
    print(f"\n[2/5] Disconnecting all {num_clients} clients...")
    
    # Disconnect all clients
    for i in range(num_clients):
        client_id = f"load-client-{i}"
        if manager.metrics:
            manager.metrics.record_disconnection(client_id)
    
    if manager.metrics:
        assert manager.metrics.active_connections == 0, \
            f"Expected 0 active connections, got {manager.metrics.active_connections}"
        
        print(f"✅ Disconnected all clients")
        print(f"   Active connections: {manager.metrics.active_connections}")
        print(f"   Client metrics still tracked: {len(manager.metrics.client_metrics)}")
    
    print("\n[3/5] Testing manual cleanup...")
    if manager.metrics:
        # Set short TTL for testing
        manager.metrics.client_metrics_ttl = 1
        
        # Wait for TTL to expire
        await asyncio.sleep(1.5)
        
        # Measure cleanup time
        start_time = time.time()
        removed = manager.metrics.cleanup_inactive_clients()
        cleanup_time_ms = (time.time() - start_time) * 1000
        
        print(f"✅ Manual cleanup completed")
        print(f"   Clients removed: {removed}")
        print(f"   Cleanup time: {cleanup_time_ms:.2f}ms")
        print(f"   Remaining client metrics: {len(manager.metrics.client_metrics)}")
        
        # Verify cleanup performance (should be < 100ms for 100 clients)
        assert cleanup_time_ms < 100, \
            f"Cleanup took {cleanup_time_ms:.2f}ms, expected < 100ms"
        
        # Verify all inactive clients removed
        assert removed >= num_clients, \
            f"Expected at least {num_clients} removed, got {removed}"
    
    print("\n[4/5] Testing automatic cleanup under load...")
    if manager.metrics:
        # Stop any existing automatic cleanup first
        if manager.metrics._cleanup_enabled:
            manager.metrics.stop_automatic_cleanup()

        # Create more clients
        for i in range(50):
            client_id = f"auto-cleanup-client-{i}"
            manager.metrics.record_connection(client_id)
            manager.metrics.record_disconnection(client_id)

        # Set short cleanup interval for testing
        manager.metrics.cleanup_interval = 1
        manager.metrics.client_metrics_ttl = 0.5  # Very short TTL for testing

        # Start automatic cleanup
        manager.metrics.start_automatic_cleanup()

        # Wait for automatic cleanup to run multiple times
        await asyncio.sleep(3.0)

        # Stop automatic cleanup
        manager.metrics.stop_automatic_cleanup()

        # Verify clients were cleaned up automatically
        remaining = len(manager.metrics.client_metrics)
        print(f"✅ Automatic cleanup completed")
        print(f"   Remaining client metrics: {remaining}")

        # Most clients should be cleaned up (allow some margin for timing)
        # Note: Some clients may remain if they were created very recently
        assert remaining < 20, \
            f"Expected < 20 remaining clients, got {remaining}"
    
    print("\n[5/5] Testing memory doesn't grow unbounded...")
    if manager.metrics:
        # Create and cleanup many clients in batches
        total_created = 0
        for batch in range(5):
            # Create batch of clients
            for i in range(20):
                client_id = f"batch-{batch}-client-{i}"
                manager.metrics.record_connection(client_id)
                manager.metrics.record_disconnection(client_id)
                total_created += 1
            
            # Cleanup after each batch
            manager.metrics.client_metrics_ttl = 0.1
            await asyncio.sleep(0.2)
            manager.metrics.cleanup_inactive_clients()
        
        # Verify memory didn't grow unbounded
        final_count = len(manager.metrics.client_metrics)
        print(f"✅ Memory management validated")
        print(f"   Total clients created: {total_created}")
        print(f"   Final client metrics: {final_count}")
        
        # Should have very few clients remaining
        assert final_count < 20, \
            f"Expected < 20 remaining clients after {total_created} created, got {final_count}"
    
    # Print final metrics
    if manager.metrics:
        print("\n" + "-"*60)
        print("Final Metrics:")
        print("-"*60)
        metrics = manager.metrics.to_dict()
        print(f"Total Connections: {metrics['connections']['total']}")
        print(f"Active Connections: {metrics['connections']['active']}")
        print(f"Messages Sent: {metrics['messages']['sent']}")
        print(f"Client Metrics Tracked: {len(manager.metrics.client_metrics)}")
    
    print("\n" + "="*60)
    print("✅ MEMORY CLEANUP TEST PASSED")
    print("="*60)
    return True


async def main():
    """Run the integration test."""
    try:
        success = await test_memory_cleanup()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

