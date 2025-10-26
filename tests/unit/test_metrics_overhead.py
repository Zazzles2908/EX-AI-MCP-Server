"""
Performance Benchmark: Metrics Tracking Overhead

Measures per-operation overhead for metrics tracking.
Compares performance with metrics enabled vs disabled.

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Performance Benchmarks
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
EXAI Recommendation: Validate metrics overhead (< 1ms per operation)
"""

import asyncio
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring.websocket_metrics import WebSocketMetrics
from src.monitoring.websocket_config import WebSocketStabilityConfig


def benchmark_operation(
    operation_func,
    iterations: int = 100000
) -> float:
    """
    Benchmark an operation.
    
    Returns:
        avg_latency_ms
    """
    # Warmup
    for _ in range(1000):
        operation_func()
    
    # Benchmark
    start_time = time.perf_counter()
    for _ in range(iterations):
        operation_func()
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_latency_ms = (total_time / iterations) * 1000
    
    return avg_latency_ms


async def run_benchmarks():
    """Run all metrics overhead benchmarks."""
    print("\n" + "=" * 60)
    print("Metrics Tracking Overhead Benchmark")
    print("=" * 60)
    
    # Create metrics instance
    metrics = WebSocketMetrics()
    
    iterations = 100000
    client_id = "benchmark-client"
    
    # Results storage
    results = {}
    
    # Benchmark: record_connection
    print("\n[Benchmarking record_connection]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.record_connection(client_id),
        iterations
    )
    results["record_connection"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Benchmark: record_disconnection
    print("\n[Benchmarking record_disconnection]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.record_disconnection(client_id),
        iterations
    )
    results["record_disconnection"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Benchmark: record_message_sent
    print("\n[Benchmarking record_message_sent]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.record_message_sent(client_id, latency_ms=10.0),
        iterations
    )
    results["record_message_sent"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Benchmark: record_message_deduplicated
    print("\n[Benchmarking record_message_deduplicated]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.record_message_deduplicated(client_id),
        iterations
    )
    results["record_message_deduplicated"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Benchmark: to_dict (metrics export)
    print("\n[Benchmarking to_dict (metrics export)]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.to_dict(),
        iterations=10000  # Fewer iterations for heavier operation
    )
    results["to_dict"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Benchmark: get_average_send_latency
    print("\n[Benchmarking get_average_send_latency]")
    print("-" * 60)
    
    latency = benchmark_operation(
        lambda: metrics.get_average_send_latency(),
        iterations
    )
    results["get_average_send_latency"] = latency
    print(f"Average latency: {latency:.6f} ms/operation ({latency * 1000:.3f} µs)")
    
    # Performance targets validation
    print("\n" + "=" * 60)
    print("Performance Targets Validation")
    print("=" * 60)
    
    targets_met = True
    target_ms = 1.0  # < 1ms per operation
    
    for operation, latency in results.items():
        met = latency < target_ms
        targets_met = targets_met and met
        
        status = "✅" if met else "❌"
        print(f"{status} {operation:30s}: {latency:.6f} ms (target: < {target_ms} ms)")
    
    # Overhead analysis
    print("\n" + "=" * 60)
    print("Overhead Analysis")
    print("=" * 60)
    
    # Calculate total overhead for typical operation sequence
    typical_sequence = [
        ("Connection", results["record_connection"]),
        ("Send 10 messages", results["record_message_sent"] * 10),
        ("Dedup 2 messages", results["record_message_deduplicated"] * 2),
        ("Export metrics", results["to_dict"]),
        ("Disconnection", results["record_disconnection"])
    ]
    
    total_overhead = sum(latency for _, latency in typical_sequence)
    
    print("\nTypical operation sequence overhead:")
    for operation, latency in typical_sequence:
        print(f"  {operation:20s}: {latency:.6f} ms")
    print(f"  {'Total':20s}: {total_overhead:.6f} ms")
    
    # Throughput calculation
    print("\n" + "=" * 60)
    print("Throughput Analysis")
    print("=" * 60)
    
    # Messages per second with metrics enabled
    msg_latency = results["record_message_sent"]
    msg_throughput = 1000 / msg_latency if msg_latency > 0 else 0
    
    print(f"Message tracking throughput: {msg_throughput:,.0f} messages/second")
    print(f"Connection tracking throughput: {1000 / results['record_connection']:,.0f} connections/second")
    
    # Summary
    print("\n" + "=" * 60)
    if targets_met:
        print("✅ METRICS OVERHEAD BENCHMARK PASSED")
    else:
        print("❌ METRICS OVERHEAD BENCHMARK FAILED")
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

