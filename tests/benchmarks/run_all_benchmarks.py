"""
Master Benchmark Runner.

Runs all performance benchmarks and generates comprehensive report.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Performance Benchmarks
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import asyncio
import json
import time
from datetime import datetime

# Import benchmark modules
import hash_performance
import cleanup_performance
import metrics_overhead
import circuit_breaker_latency


async def run_all_benchmarks() -> dict:
    """Run all performance benchmarks."""
    print("\n" + "="*80)
    print(" "*20 + "PERFORMANCE BENCHMARK SUITE")
    print(" "*25 + "Phase 2.4 Week 1.5")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AEDT')}")
    print("="*80 + "\n")
    
    start_time = time.time()
    results = {}
    
    # Benchmark 1: Hash Performance
    print("\n" + "▶"*40)
    print("BENCHMARK 1/4: Hash Performance (xxhash vs SHA256)")
    print("▶"*40)
    try:
        results['hash_performance'] = hash_performance.run_benchmark(
            message_size_kb=10,
            message_count=1000,
            iterations=10
        )
        print("✅ Hash performance benchmark completed\n")
    except Exception as e:
        print(f"❌ Hash performance benchmark failed: {e}\n")
        results['hash_performance'] = {"error": str(e)}
    
    # Benchmark 2: Cleanup Performance
    print("\n" + "▶"*40)
    print("BENCHMARK 2/4: Cleanup Performance")
    print("▶"*40)
    try:
        results['cleanup_performance'] = cleanup_performance.run_benchmark()
        print("✅ Cleanup performance benchmark completed\n")
    except Exception as e:
        print(f"❌ Cleanup performance benchmark failed: {e}\n")
        results['cleanup_performance'] = {"error": str(e)}
    
    # Benchmark 3: Metrics Overhead
    print("\n" + "▶"*40)
    print("BENCHMARK 3/4: Metrics Overhead")
    print("▶"*40)
    try:
        results['metrics_overhead'] = await metrics_overhead.run_benchmark(
            duration_seconds=5.0,
            iterations=3
        )
        print("✅ Metrics overhead benchmark completed\n")
    except Exception as e:
        print(f"❌ Metrics overhead benchmark failed: {e}\n")
        results['metrics_overhead'] = {"error": str(e)}
    
    # Benchmark 4: Circuit Breaker Latency
    print("\n" + "▶"*40)
    print("BENCHMARK 4/4: Circuit Breaker Latency")
    print("▶"*40)
    try:
        results['circuit_breaker_latency'] = await circuit_breaker_latency.run_benchmark()
        print("✅ Circuit breaker latency benchmark completed\n")
    except Exception as e:
        print(f"❌ Circuit breaker latency benchmark failed: {e}\n")
        results['circuit_breaker_latency'] = {"error": str(e)}
    
    # Calculate total time
    total_time = time.time() - start_time
    
    # Generate summary
    print("\n" + "="*80)
    print(" "*30 + "FINAL SUMMARY")
    print("="*80)
    
    # Check pass/fail for each benchmark
    benchmarks_status = []
    
    # Hash Performance
    hash_result = results.get('hash_performance', {})
    if 'error' not in hash_result:
        hash_passed = hash_result.get('passed', False)
        speedup = hash_result.get('speedup')
        if speedup is not None:
            detail = f"Speedup: {speedup:.2f}x (target: 3-5x)"
        else:
            detail = "xxhash not available - cannot measure speedup"
        benchmarks_status.append({
            "name": "Hash Performance",
            "passed": hash_passed,
            "detail": detail
        })
    else:
        benchmarks_status.append({
            "name": "Hash Performance",
            "passed": False,
            "detail": f"Error: {hash_result['error']}"
        })
    
    # Cleanup Performance
    cleanup_result = results.get('cleanup_performance', {})
    if 'error' not in cleanup_result:
        cleanup_passed = cleanup_result.get('passed', False)
        benchmarks_status.append({
            "name": "Cleanup Performance",
            "passed": cleanup_passed,
            "detail": "Target: <10ms per 1000 clients"
        })
    else:
        benchmarks_status.append({
            "name": "Cleanup Performance",
            "passed": False,
            "detail": f"Error: {cleanup_result['error']}"
        })
    
    # Metrics Overhead
    metrics_result = results.get('metrics_overhead', {})
    if 'error' not in metrics_result:
        metrics_passed = metrics_result.get('passed', False)
        cpu_overhead = metrics_result.get('cpu_overhead_percent', 0)
        memory_per_10k = metrics_result.get('memory_per_10k_ops_kb', 0)
        benchmarks_status.append({
            "name": "Metrics Overhead",
            "passed": metrics_passed,
            "detail": f"CPU: {cpu_overhead:.2f}%, Memory: {memory_per_10k:.2f} KB/10K"
        })
    else:
        benchmarks_status.append({
            "name": "Metrics Overhead",
            "passed": False,
            "detail": f"Error: {metrics_result['error']}"
        })
    
    # Circuit Breaker Latency
    cb_result = results.get('circuit_breaker_latency', {})
    if 'error' not in cb_result:
        cb_passed = cb_result.get('passed', False)
        benchmarks_status.append({
            "name": "Circuit Breaker Latency",
            "passed": cb_passed,
            "detail": "Target: <0.1ms per check"
        })
    else:
        benchmarks_status.append({
            "name": "Circuit Breaker Latency",
            "passed": False,
            "detail": f"Error: {cb_result['error']}"
        })
    
    # Print summary table
    print(f"\n{'Benchmark':<30} {'Status':<10} {'Details'}")
    print("-"*80)
    for status in benchmarks_status:
        status_icon = "✅ PASS" if status['passed'] else "❌ FAIL"
        print(f"{status['name']:<30} {status_icon:<10} {status['detail']}")
    
    print("\n" + "="*80)
    total_passed = sum(1 for s in benchmarks_status if s['passed'])
    total_benchmarks = len(benchmarks_status)
    print(f"Overall: {total_passed}/{total_benchmarks} benchmarks passed")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S AEDT')}")
    print("="*80 + "\n")
    
    # Compile final results
    final_results = {
        "timestamp": time.time(),
        "datetime": datetime.now().isoformat(),
        "total_time_seconds": total_time,
        "benchmarks": results,
        "summary": {
            "total_benchmarks": total_benchmarks,
            "passed": total_passed,
            "failed": total_benchmarks - total_passed,
            "pass_rate": (total_passed / total_benchmarks) * 100 if total_benchmarks > 0 else 0,
            "status": benchmarks_status
        }
    }
    
    return final_results


if __name__ == "__main__":
    # Run all benchmarks
    results = asyncio.run(run_all_benchmarks())
    
    # Save results
    output_file = "benchmarks/results_all_benchmarks.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Complete results saved to: {output_file}")
    print("\n" + "="*80)
    print("✅ ALL BENCHMARKS COMPLETE")
    print("="*80)

