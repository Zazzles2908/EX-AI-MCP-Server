"""
Circuit Breaker Latency Benchmark.

Measures circuit breaker state check latency.
Target: <0.1ms per state check.

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

from src.monitoring.circuit_breaker import CircuitBreaker, CircuitBreakerConfig


async def benchmark_state_checks(check_count: int, iterations: int = 10) -> Dict:
    """
    Benchmark circuit breaker state checks.
    
    Args:
        check_count: Number of state checks per iteration
        iterations: Number of iterations for averaging
    
    Returns:
        Benchmark results dictionary
    """
    times = []
    
    for _ in range(iterations):
        # Create circuit breaker
        cb = CircuitBreaker(
            name="benchmark_cb",
            config=CircuitBreakerConfig(
                failure_threshold=5,
                success_threshold=2,
                timeout_seconds=60.0
            )
        )
        
        # Measure state check time
        start = time.perf_counter()
        
        for _ in range(check_count):
            _ = cb.is_open
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    time_per_check_us = (avg_time * 1000) / check_count  # microseconds
    
    return {
        "check_count": check_count,
        "iterations": iterations,
        "avg_total_ms": avg_time,
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
        "time_per_check_us": time_per_check_us,
        "time_per_check_ms": time_per_check_us / 1000,
        "checks_per_second": check_count / (avg_time / 1000) if avg_time > 0 else 0
    }


async def benchmark_failure_recording(operation_count: int, iterations: int = 10) -> Dict:
    """Benchmark failure recording performance."""
    times = []
    
    for _ in range(iterations):
        # Create circuit breaker
        cb = CircuitBreaker(
            name="benchmark_cb",
            config=CircuitBreakerConfig(
                failure_threshold=operation_count + 10,  # High threshold to avoid opening
                success_threshold=2,
                timeout_seconds=60.0
            )
        )
        
        # Measure failure recording time
        start = time.perf_counter()
        
        for _ in range(operation_count):
            await cb._on_failure()
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    avg_time = statistics.mean(times)
    time_per_op_us = (avg_time * 1000) / operation_count  # microseconds
    
    return {
        "operation_count": operation_count,
        "iterations": iterations,
        "avg_total_ms": avg_time,
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
        "time_per_operation_us": time_per_op_us,
        "operations_per_second": operation_count / (avg_time / 1000) if avg_time > 0 else 0
    }


async def run_benchmark() -> Dict:
    """Run circuit breaker latency benchmark."""
    print(f"\n{'='*60}")
    print(f"Circuit Breaker Latency Benchmark")
    print(f"{'='*60}\n")
    
    # Benchmark 1: State checks
    print("Benchmarking state checks...")
    check_counts = [1000, 10000, 100000]
    state_check_results = []
    
    for count in check_counts:
        result = await benchmark_state_checks(count, iterations=10)
        state_check_results.append(result)
        print(f"  {count:,} checks: {result['time_per_check_us']:.3f} μs per check")
    
    print()
    
    # Benchmark 2: Failure recording
    print("Benchmarking failure recording...")
    operation_counts = [100, 1000, 10000]
    failure_recording_results = []
    
    for count in operation_counts:
        result = await benchmark_failure_recording(count, iterations=10)
        failure_recording_results.append(result)
        print(f"  {count:,} operations: {result['time_per_operation_us']:.3f} μs per operation")
    
    print()
    
    # Summary
    print("="*60)
    print("SUMMARY - Circuit Breaker Latency")
    print("="*60)
    print("\nState Check Performance:")
    print(f"{'Checks':<12} {'Per Check (μs)':<18} {'Per Check (ms)':<18} {'Status'}")
    print("-"*60)
    
    target_ms = 0.1  # Target: <0.1ms per check
    
    for result in state_check_results:
        count = result['check_count']
        per_check_us = result['time_per_check_us']
        per_check_ms = result['time_per_check_ms']
        status = "✅ PASS" if per_check_ms < target_ms else "⚠️  FAIL"
        
        print(f"{count:<12,} {per_check_us:<18.3f} {per_check_ms:<18.6f} {status}")
    
    print("\nFailure Recording Performance:")
    print(f"{'Operations':<12} {'Per Op (μs)':<18} {'Ops/sec':<18}")
    print("-"*60)
    
    for result in failure_recording_results:
        count = result['operation_count']
        per_op_us = result['time_per_operation_us']
        ops_per_sec = result['operations_per_second']
        
        print(f"{count:<12,} {per_op_us:<18.3f} {ops_per_sec:<18,.0f}")
    
    print("="*60)
    print(f"Target: <{target_ms} ms per state check")
    print("="*60 + "\n")
    
    # Compile final results
    passed = all(r['time_per_check_ms'] < target_ms for r in state_check_results)
    
    return {
        "benchmark_name": "circuit_breaker_latency",
        "target_per_check_ms": target_ms,
        "state_check_results": state_check_results,
        "failure_recording_results": failure_recording_results,
        "passed": passed
    }


if __name__ == "__main__":
    results = asyncio.run(run_benchmark())
    
    # Export results
    import json
    output = {
        "benchmark": results,
        "timestamp": time.time()
    }
    
    with open("benchmarks/results_circuit_breaker_latency.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: benchmarks/results_circuit_breaker_latency.json")

