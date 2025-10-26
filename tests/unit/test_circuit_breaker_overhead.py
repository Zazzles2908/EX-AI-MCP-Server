"""
Performance Benchmark: Circuit Breaker Overhead

Measures circuit breaker evaluation time and state transition performance.
Validates that circuit breaker adds minimal overhead to operations.

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Performance Benchmarks
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
EXAI Recommendation: Validate circuit breaker overhead (< 0.1ms per evaluation)
"""

import asyncio
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.monitoring.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState


async def benchmark_call_overhead(
    circuit_breaker: CircuitBreaker,
    iterations: int = 100000
) -> float:
    """
    Benchmark circuit breaker call overhead.
    
    Returns:
        avg_latency_ms
    """
    # Test function
    async def test_func():
        return "success"
    
    # Warmup
    for _ in range(1000):
        await circuit_breaker.call(test_func)
    
    # Benchmark
    start_time = time.perf_counter()
    for _ in range(iterations):
        await circuit_breaker.call(test_func)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_latency_ms = (total_time / iterations) * 1000
    
    return avg_latency_ms


async def benchmark_state_transition(
    circuit_breaker: CircuitBreaker,
    iterations: int = 10000
) -> dict:
    """
    Benchmark circuit breaker state transitions.
    
    Returns:
        dict with transition times
    """
    results = {}
    
    # Benchmark: CLOSED → OPEN
    await circuit_breaker._change_state(CircuitState.CLOSED)
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        await circuit_breaker._change_state(CircuitState.OPEN)
        await circuit_breaker._change_state(CircuitState.CLOSED)
    end_time = time.perf_counter()
    
    avg_latency_ms = ((end_time - start_time) / (iterations * 2)) * 1000
    results["closed_to_open"] = avg_latency_ms
    
    # Benchmark: OPEN → HALF_OPEN
    await circuit_breaker._change_state(CircuitState.OPEN)
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        await circuit_breaker._change_state(CircuitState.HALF_OPEN)
        await circuit_breaker._change_state(CircuitState.OPEN)
    end_time = time.perf_counter()
    
    avg_latency_ms = ((end_time - start_time) / (iterations * 2)) * 1000
    results["open_to_half_open"] = avg_latency_ms
    
    # Benchmark: HALF_OPEN → CLOSED
    await circuit_breaker._change_state(CircuitState.HALF_OPEN)
    
    start_time = time.perf_counter()
    for _ in range(iterations):
        await circuit_breaker._change_state(CircuitState.CLOSED)
        await circuit_breaker._change_state(CircuitState.HALF_OPEN)
    end_time = time.perf_counter()
    
    avg_latency_ms = ((end_time - start_time) / (iterations * 2)) * 1000
    results["half_open_to_closed"] = avg_latency_ms
    
    return results


async def run_benchmarks():
    """Run all circuit breaker performance benchmarks."""
    print("\n" + "=" * 60)
    print("Circuit Breaker Performance Benchmark")
    print("=" * 60)
    
    # Create circuit breaker
    config = CircuitBreakerConfig(
        failure_threshold=5,
        success_threshold=2,
        timeout_seconds=60.0
    )
    circuit_breaker = CircuitBreaker("benchmark", config)
    
    # Results storage
    results = {}
    
    # Benchmark: Call overhead (CLOSED state)
    print("\n[Benchmarking call overhead (CLOSED state)]")
    print("-" * 60)
    
    await circuit_breaker._change_state(CircuitState.CLOSED)
    latency = await benchmark_call_overhead(circuit_breaker, iterations=100000)
    results["call_overhead_closed"] = latency
    print(f"Average latency: {latency:.6f} ms/call ({latency * 1000:.3f} µs)")
    
    # Benchmark: Call overhead (HALF_OPEN state)
    print("\n[Benchmarking call overhead (HALF_OPEN state)]")
    print("-" * 60)
    
    await circuit_breaker._change_state(CircuitState.HALF_OPEN)
    latency = await benchmark_call_overhead(circuit_breaker, iterations=10000)
    results["call_overhead_half_open"] = latency
    print(f"Average latency: {latency:.6f} ms/call ({latency * 1000:.3f} µs)")
    
    # Benchmark: State transitions
    print("\n[Benchmarking state transitions]")
    print("-" * 60)
    
    transition_results = await benchmark_state_transition(circuit_breaker, iterations=10000)
    results.update(transition_results)
    
    for transition, latency in transition_results.items():
        print(f"{transition:25s}: {latency:.6f} ms ({latency * 1000:.3f} µs)")
    
    # Benchmark: Failure recording
    print("\n[Benchmarking failure recording]")
    print("-" * 60)
    
    await circuit_breaker._change_state(CircuitState.CLOSED)
    
    start_time = time.perf_counter()
    for _ in range(10000):
        await circuit_breaker._on_failure()
        # Reset to avoid opening circuit
        circuit_breaker._failure_count = 0
    end_time = time.perf_counter()
    
    latency = ((end_time - start_time) / 10000) * 1000
    results["failure_recording"] = latency
    print(f"Average latency: {latency:.6f} ms/failure ({latency * 1000:.3f} µs)")
    
    # Benchmark: Success recording
    print("\n[Benchmarking success recording]")
    print("-" * 60)
    
    await circuit_breaker._change_state(CircuitState.HALF_OPEN)
    
    start_time = time.perf_counter()
    for _ in range(10000):
        await circuit_breaker._on_success()
        # Reset to avoid closing circuit
        circuit_breaker._success_count = 0
    end_time = time.perf_counter()
    
    latency = ((end_time - start_time) / 10000) * 1000
    results["success_recording"] = latency
    print(f"Average latency: {latency:.6f} ms/success ({latency * 1000:.3f} µs)")
    
    # Performance targets validation
    print("\n" + "=" * 60)
    print("Performance Targets Validation")
    print("=" * 60)
    
    targets_met = True
    target_ms = 0.1  # < 0.1ms per evaluation
    
    # Check call overhead
    for key in ["call_overhead_closed", "call_overhead_half_open"]:
        latency = results[key]
        met = latency < target_ms
        targets_met = targets_met and met
        
        status = "✅" if met else "❌"
        print(f"{status} {key:30s}: {latency:.6f} ms (target: < {target_ms} ms)")
    
    # Throughput analysis
    print("\n" + "=" * 60)
    print("Throughput Analysis")
    print("=" * 60)
    
    call_latency = results["call_overhead_closed"]
    throughput = 1000 / call_latency if call_latency > 0 else 0
    
    print(f"Circuit breaker throughput: {throughput:,.0f} calls/second")
    print(f"Overhead per call: {call_latency * 1000:.3f} µs")
    
    # Summary
    print("\n" + "=" * 60)
    if targets_met:
        print("✅ CIRCUIT BREAKER OVERHEAD BENCHMARK PASSED")
    else:
        print("❌ CIRCUIT BREAKER OVERHEAD BENCHMARK FAILED")
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

