"""
Metrics Collection Overhead Benchmark.

Measures CPU and memory overhead of metrics tracking.
Target: <1% CPU overhead, <100KB memory per 10K metrics.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Performance Benchmarks
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import time
import statistics
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.resilient_websocket import ResilientWebSocketManager


def get_memory_usage_mb() -> float:
    """Get current memory usage in MB."""
    import psutil
    import os
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


async def benchmark_with_metrics(operation_count: int, duration_seconds: float = 5.0) -> Dict:
    """Benchmark with metrics enabled."""
    manager = ResilientWebSocketManager(
        enable_metrics=True,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Measure initial memory
    initial_memory = get_memory_usage_mb()
    
    # Perform operations
    start = time.perf_counter()
    operations_completed = 0
    
    while (time.perf_counter() - start) < duration_seconds:
        # Simulate metric recording
        manager.metrics.record_connection(f"client_{operations_completed}")
        manager.metrics.record_message_sent(f"client_{operations_completed}", latency_ms=10.0)
        operations_completed += 1
    
    elapsed = time.perf_counter() - start
    
    # Measure final memory
    final_memory = get_memory_usage_mb()
    memory_increase = final_memory - initial_memory
    
    # Calculate metrics
    ops_per_second = operations_completed / elapsed
    memory_per_10k_ops = (memory_increase / operations_completed) * 10000 if operations_completed > 0 else 0
    
    # Cleanup
    await manager.stop_background_tasks()
    
    return {
        "metrics_enabled": True,
        "operations_completed": operations_completed,
        "duration_seconds": elapsed,
        "ops_per_second": ops_per_second,
        "initial_memory_mb": initial_memory,
        "final_memory_mb": final_memory,
        "memory_increase_mb": memory_increase,
        "memory_per_10k_ops_kb": memory_per_10k_ops * 1024
    }


async def benchmark_without_metrics(operation_count: int, duration_seconds: float = 5.0) -> Dict:
    """Benchmark with metrics disabled."""
    manager = ResilientWebSocketManager(
        enable_metrics=False,
        enable_circuit_breaker=False,
        enable_deduplication=False
    )
    
    # Measure initial memory
    initial_memory = get_memory_usage_mb()
    
    # Perform operations (no metrics recorded)
    start = time.perf_counter()
    operations_completed = 0
    
    while (time.perf_counter() - start) < duration_seconds:
        # Simulate operations without metrics
        operations_completed += 1
    
    elapsed = time.perf_counter() - start
    
    # Measure final memory
    final_memory = get_memory_usage_mb()
    memory_increase = final_memory - initial_memory
    
    # Calculate metrics
    ops_per_second = operations_completed / elapsed
    
    # Cleanup
    await manager.stop_background_tasks()
    
    return {
        "metrics_enabled": False,
        "operations_completed": operations_completed,
        "duration_seconds": elapsed,
        "ops_per_second": ops_per_second,
        "initial_memory_mb": initial_memory,
        "final_memory_mb": final_memory,
        "memory_increase_mb": memory_increase
    }


async def run_benchmark(duration_seconds: float = 5.0, iterations: int = 3) -> Dict:
    """Run metrics overhead benchmark."""
    print(f"\n{'='*60}")
    print(f"Metrics Overhead Benchmark")
    print(f"{'='*60}")
    print(f"Duration per iteration: {duration_seconds} seconds")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}\n")
    
    with_metrics_results = []
    without_metrics_results = []
    
    for i in range(iterations):
        print(f"Iteration {i+1}/{iterations}...")
        
        # Benchmark with metrics
        print("  Running with metrics enabled...")
        with_result = await benchmark_with_metrics(0, duration_seconds)
        with_metrics_results.append(with_result)
        
        # Small delay between tests
        await asyncio.sleep(0.5)
        
        # Benchmark without metrics
        print("  Running with metrics disabled...")
        without_result = await benchmark_without_metrics(0, duration_seconds)
        without_metrics_results.append(without_result)
        
        print(f"  With metrics: {with_result['ops_per_second']:,.0f} ops/sec")
        print(f"  Without metrics: {without_result['ops_per_second']:,.0f} ops/sec\n")
        
        # Small delay between iterations
        await asyncio.sleep(0.5)
    
    # Calculate averages
    avg_with_ops = statistics.mean([r['ops_per_second'] for r in with_metrics_results])
    avg_without_ops = statistics.mean([r['ops_per_second'] for r in without_metrics_results])
    avg_memory_per_10k = statistics.mean([r['memory_per_10k_ops_kb'] for r in with_metrics_results])
    
    # Calculate overhead
    cpu_overhead_percent = ((avg_without_ops - avg_with_ops) / avg_without_ops) * 100 if avg_without_ops > 0 else 0
    
    # Summary
    print("="*60)
    print("SUMMARY - Metrics Overhead")
    print("="*60)
    print(f"With metrics:    {avg_with_ops:,.0f} ops/sec")
    print(f"Without metrics: {avg_without_ops:,.0f} ops/sec")
    print(f"CPU overhead:    {cpu_overhead_percent:.2f}%")
    print(f"Memory per 10K:  {avg_memory_per_10k:.2f} KB")
    print("="*60)
    print(f"Target CPU overhead: <1%")
    print(f"Target memory: <100 KB per 10K metrics")
    print(f"CPU Status: {'✅ PASS' if cpu_overhead_percent < 1.0 else '⚠️  FAIL'}")
    print(f"Memory Status: {'✅ PASS' if avg_memory_per_10k < 100 else '⚠️  FAIL'}")
    print("="*60 + "\n")
    
    return {
        "benchmark_name": "metrics_overhead",
        "duration_seconds": duration_seconds,
        "iterations": iterations,
        "with_metrics": {
            "avg_ops_per_second": avg_with_ops,
            "results": with_metrics_results
        },
        "without_metrics": {
            "avg_ops_per_second": avg_without_ops,
            "results": without_metrics_results
        },
        "cpu_overhead_percent": cpu_overhead_percent,
        "memory_per_10k_ops_kb": avg_memory_per_10k,
        "target_cpu_overhead_percent": 1.0,
        "target_memory_per_10k_kb": 100.0,
        "cpu_passed": cpu_overhead_percent < 1.0,
        "memory_passed": avg_memory_per_10k < 100.0,
        "passed": cpu_overhead_percent < 1.0 and avg_memory_per_10k < 100.0
    }


if __name__ == "__main__":
    results = asyncio.run(run_benchmark(duration_seconds=5.0, iterations=3))
    
    # Export results
    import json
    output = {
        "benchmark": results,
        "timestamp": time.time()
    }
    
    with open("benchmarks/results_metrics_overhead.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: benchmarks/results_metrics_overhead.json")

