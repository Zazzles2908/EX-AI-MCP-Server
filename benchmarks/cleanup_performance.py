"""
Connection Cleanup Performance Benchmark.

Measures cleanup overhead for inactive client metrics.
Target: <10ms per 1000 connections.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Performance Benchmarks
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import time
import statistics
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.websocket_metrics import WebSocketMetrics


def create_mock_client_metrics(count: int, metrics: WebSocketMetrics) -> None:
    """Create mock client metrics."""
    for i in range(count):
        client_id = f"client_{i}"
        metrics.record_connection(client_id)
        metrics.record_message_sent(client_id, latency_ms=10.0)


def benchmark_cleanup(client_count: int, iterations: int = 10) -> Dict:
    """
    Benchmark cleanup performance.

    Args:
        client_count: Number of clients to create
        iterations: Number of iterations for averaging

    Returns:
        Benchmark results dictionary
    """
    times = []

    for _ in range(iterations):
        # Create fresh metrics instance
        metrics = WebSocketMetrics()

        # Create mock clients
        create_mock_client_metrics(client_count, metrics)

        # Small delay to ensure clients are "inactive"
        time.sleep(0.001)  # 1ms delay

        # Measure cleanup time
        start = time.perf_counter()
        cleaned = metrics.cleanup_inactive_clients(ttl_seconds=0)  # Clean all older than 0s
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        times.append(elapsed)

        # Verify all were cleaned
        assert cleaned == client_count, f"Expected {client_count} cleaned, got {cleaned}"
    
    avg_time = statistics.mean(times)
    time_per_1000 = (avg_time / client_count) * 1000
    
    return {
        "client_count": client_count,
        "iterations": iterations,
        "avg_ms": avg_time,
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
        "time_per_1000_clients_ms": time_per_1000,
        "clients_per_second": client_count / (avg_time / 1000) if avg_time > 0 else 0
    }


def run_benchmark() -> Dict:
    """Run cleanup performance benchmark."""
    print(f"\n{'='*60}")
    print(f"Cleanup Performance Benchmark")
    print(f"{'='*60}\n")
    
    # Test different client counts
    client_counts = [100, 1000, 10000, 100000]
    results = []
    
    for count in client_counts:
        print(f"Benchmarking cleanup for {count:,} clients...")
        
        # Adjust iterations based on client count
        if count <= 1000:
            iterations = 10
        elif count <= 10000:
            iterations = 5
        else:
            iterations = 3
        
        result = benchmark_cleanup(count, iterations)
        results.append(result)
        
        print(f"  Average: {result['avg_ms']:.3f} ms")
        print(f"  Per 1000 clients: {result['time_per_1000_clients_ms']:.3f} ms")
        print(f"  Throughput: {result['clients_per_second']:,.0f} clients/sec\n")
    
    # Summary
    print("="*60)
    print("SUMMARY - Cleanup Performance")
    print("="*60)
    print(f"{'Clients':<12} {'Total (ms)':<15} {'Per 1000 (ms)':<15} {'Status'}")
    print("-"*60)
    
    target_per_1000 = 10.0  # Target: <10ms per 1000 connections
    
    for result in results:
        count = result['client_count']
        total_time = result['avg_ms']
        per_1000 = result['time_per_1000_clients_ms']
        status = "✅ PASS" if per_1000 < target_per_1000 else "⚠️  FAIL"
        
        print(f"{count:<12,} {total_time:<15.3f} {per_1000:<15.3f} {status}")
    
    print("="*60)
    print(f"Target: <{target_per_1000} ms per 1000 clients")
    print("="*60 + "\n")
    
    # Compile final results
    passed = all(r['time_per_1000_clients_ms'] < target_per_1000 for r in results)
    
    return {
        "benchmark_name": "cleanup_performance",
        "target_per_1000_ms": target_per_1000,
        "results": results,
        "passed": passed
    }


if __name__ == "__main__":
    results = run_benchmark()
    
    # Export results
    import json
    output = {
        "benchmark": results,
        "timestamp": time.time()
    }
    
    with open("benchmarks/results_cleanup_performance.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: benchmarks/results_cleanup_performance.json")

