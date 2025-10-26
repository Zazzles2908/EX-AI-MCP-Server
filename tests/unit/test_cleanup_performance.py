"""
Performance Benchmark: Cleanup Performance

Measures cleanup time for various numbers of inactive clients.
Tests automatic cleanup overhead and validates performance targets.

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Performance Benchmarks
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
EXAI Recommendation: Validate cleanup performance (1000 clients in < 100ms)
"""

import asyncio
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring.websocket_metrics import WebSocketMetrics
from src.monitoring.websocket_config import WebSocketStabilityConfig


async def benchmark_manual_cleanup(
    num_clients: int,
    ttl_seconds: float = 0.1
) -> float:
    """
    Benchmark manual cleanup performance.
    
    Returns:
        cleanup_time_ms
    """
    # Create metrics instance
    metrics = WebSocketMetrics()
    
    # Create clients
    for i in range(num_clients):
        client_id = f"client-{i}"
        metrics.record_connection(client_id)
        metrics.record_disconnection(client_id)
    
    # Wait for TTL to expire
    await asyncio.sleep(ttl_seconds + 0.1)
    
    # Benchmark cleanup
    start_time = time.perf_counter()
    removed = metrics.cleanup_inactive_clients(ttl_seconds=ttl_seconds)
    end_time = time.perf_counter()
    
    cleanup_time_ms = (end_time - start_time) * 1000
    
    # Verify cleanup worked
    assert removed == num_clients, f"Expected {num_clients} removed, got {removed}"
    assert len(metrics.client_metrics) == 0, "Client metrics should be empty"
    
    return cleanup_time_ms


async def benchmark_automatic_cleanup(
    num_clients: int,
    cleanup_interval: float = 0.5,
    ttl_seconds: float = 0.2
) -> tuple[float, int]:
    """
    Benchmark automatic cleanup performance.
    
    Returns:
        (total_time_ms, clients_cleaned)
    """
    # Create metrics instance
    metrics = WebSocketMetrics()
    
    # Configure for fast cleanup
    metrics.cleanup_interval = cleanup_interval
    metrics.client_metrics_ttl = ttl_seconds
    
    # Create clients
    for i in range(num_clients):
        client_id = f"client-{i}"
        metrics.record_connection(client_id)
        metrics.record_disconnection(client_id)
    
    # Start automatic cleanup
    metrics.start_automatic_cleanup()
    
    # Wait for cleanup to run
    start_time = time.perf_counter()
    await asyncio.sleep(cleanup_interval + ttl_seconds + 0.5)
    end_time = time.perf_counter()
    
    # Stop automatic cleanup
    metrics.stop_automatic_cleanup()
    
    total_time_ms = (end_time - start_time) * 1000
    clients_cleaned = num_clients - len(metrics.client_metrics)
    
    return total_time_ms, clients_cleaned


async def run_benchmarks():
    """Run all cleanup performance benchmarks."""
    print("\n" + "=" * 60)
    print("Cleanup Performance Benchmark")
    print("=" * 60)
    
    # Test configurations
    client_counts = [100, 500, 1000, 5000, 10000]
    
    # Results storage
    results = {
        "manual": {},
        "automatic": {}
    }
    
    # Benchmark manual cleanup
    print("\n[Manual Cleanup Performance]")
    print("-" * 60)
    
    for num_clients in client_counts:
        cleanup_time_ms = await benchmark_manual_cleanup(num_clients)
        results["manual"][num_clients] = cleanup_time_ms
        
        per_client_us = (cleanup_time_ms * 1000) / num_clients
        print(f"{num_clients:>6} clients: {cleanup_time_ms:>8.2f} ms  "
              f"({per_client_us:>6.2f} µs/client)")
    
    # Benchmark automatic cleanup
    print("\n[Automatic Cleanup Performance]")
    print("-" * 60)
    
    for num_clients in [100, 500, 1000]:
        total_time_ms, clients_cleaned = await benchmark_automatic_cleanup(num_clients)
        results["automatic"][num_clients] = {
            "total_time_ms": total_time_ms,
            "clients_cleaned": clients_cleaned
        }
        
        cleanup_rate = (clients_cleaned / total_time_ms) * 1000 if total_time_ms > 0 else 0
        print(f"{num_clients:>6} clients: {total_time_ms:>8.2f} ms total  "
              f"({clients_cleaned} cleaned, {cleanup_rate:,.0f} clients/s)")
    
    # Performance targets validation
    print("\n" + "=" * 60)
    print("Performance Targets Validation")
    print("=" * 60)
    
    targets_met = True
    
    # Target: Cleanup 1000 clients in < 100ms
    cleanup_1000 = results["manual"][1000]
    target_1000 = 100.0
    target_1000_met = cleanup_1000 < target_1000
    targets_met = targets_met and target_1000_met
    
    status = "✅" if target_1000_met else "❌"
    print(f"{status} Manual cleanup (1000 clients): {cleanup_1000:.2f} ms (target: < {target_1000} ms)")
    
    # Target: Cleanup 10000 clients in < 1000ms
    cleanup_10000 = results["manual"][10000]
    target_10000 = 1000.0
    target_10000_met = cleanup_10000 < target_10000
    targets_met = targets_met and target_10000_met
    
    status = "✅" if target_10000_met else "❌"
    print(f"{status} Manual cleanup (10000 clients): {cleanup_10000:.2f} ms (target: < {target_10000} ms)")
    
    # Target: Automatic cleanup overhead < 10% of interval
    auto_1000 = results["automatic"][1000]
    cleanup_interval_ms = 500  # 0.5 seconds
    overhead_pct = (auto_1000["total_time_ms"] / cleanup_interval_ms) * 100
    overhead_target = 10.0
    overhead_met = overhead_pct < overhead_target
    
    status = "✅" if overhead_met else "❌"
    print(f"{status} Automatic cleanup overhead: {overhead_pct:.1f}% (target: < {overhead_target}%)")
    
    # Scalability analysis
    print("\n" + "=" * 60)
    print("Scalability Analysis")
    print("=" * 60)
    
    # Calculate per-client cleanup time
    for num_clients in client_counts:
        cleanup_time_ms = results["manual"][num_clients]
        per_client_us = (cleanup_time_ms * 1000) / num_clients
        
        # Check if linear scaling (per-client time should be roughly constant)
        if num_clients == 100:
            baseline_per_client = per_client_us
        else:
            scaling_factor = per_client_us / baseline_per_client
            status = "✅" if scaling_factor < 2.0 else "⚠️"
            print(f"{status} {num_clients:>6} clients: {per_client_us:>6.2f} µs/client "
                  f"({scaling_factor:.2f}x baseline)")
    
    # Summary
    print("\n" + "=" * 60)
    if targets_met:
        print("✅ CLEANUP PERFORMANCE BENCHMARK PASSED")
    else:
        print("❌ CLEANUP PERFORMANCE BENCHMARK FAILED")
    print("=" * 60)
    
    return targets_met


async def main():
    """Main entry point."""
    try:
        success = await run_benchmarks()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ BENCHMARK FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)

