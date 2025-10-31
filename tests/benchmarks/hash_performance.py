"""
Hash Algorithm Performance Benchmark.

Compares xxhash vs SHA256 for message deduplication.
Target: xxhash should be 3-5x faster than SHA256.

Created: 2025-10-28
Phase: 2.4 Week 1.5 - Performance Benchmarks
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import hashlib
import json
import time
import statistics
from typing import Dict, List, Tuple

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False
    print("WARNING: xxhash not available, will only benchmark SHA256")


def generate_test_messages(count: int, size_kb: int) -> List[str]:
    """Generate test messages of specified size."""
    messages = []
    base_data = "x" * (size_kb * 1024)
    
    for i in range(count):
        message = {
            "type": "test",
            "sequence": i,
            "data": base_data,
            "timestamp": time.time()
        }
        messages.append(json.dumps(message))
    
    return messages


def benchmark_sha256(messages: List[str], iterations: int = 1) -> Dict:
    """Benchmark SHA256 hashing."""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        
        for message in messages:
            hashlib.sha256(message.encode('utf-8')).hexdigest()
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    return {
        "algorithm": "SHA256",
        "iterations": iterations,
        "message_count": len(messages),
        "avg_ms": statistics.mean(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
        "avg_per_message_us": (statistics.mean(times) * 1000) / len(messages)  # microseconds
    }


def benchmark_xxhash(messages: List[str], iterations: int = 1) -> Dict:
    """Benchmark xxhash hashing."""
    if not XXHASH_AVAILABLE:
        return {"error": "xxhash not available"}
    
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        
        for message in messages:
            xxhash.xxh64(message.encode('utf-8')).hexdigest()
        
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
        times.append(elapsed)
    
    return {
        "algorithm": "xxhash",
        "iterations": iterations,
        "message_count": len(messages),
        "avg_ms": statistics.mean(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0.0,
        "avg_per_message_us": (statistics.mean(times) * 1000) / len(messages)  # microseconds
    }


def run_benchmark(message_size_kb: int = 1, message_count: int = 1000, iterations: int = 10) -> Dict:
    """
    Run hash performance benchmark.
    
    Args:
        message_size_kb: Size of each message in KB
        message_count: Number of messages to hash
        iterations: Number of iterations for averaging
    
    Returns:
        Benchmark results dictionary
    """
    print(f"\n{'='*60}")
    print(f"Hash Performance Benchmark")
    print(f"{'='*60}")
    print(f"Message size: {message_size_kb} KB")
    print(f"Message count: {message_count}")
    print(f"Iterations: {iterations}")
    print(f"{'='*60}\n")
    
    # Generate test messages
    print("Generating test messages...")
    messages = generate_test_messages(message_count, message_size_kb)
    total_data_mb = (len(messages) * message_size_kb) / 1024
    print(f"Generated {len(messages)} messages ({total_data_mb:.2f} MB total)\n")
    
    # Benchmark SHA256
    print("Benchmarking SHA256...")
    sha256_results = benchmark_sha256(messages, iterations)
    print(f"  Average: {sha256_results['avg_ms']:.3f} ms")
    print(f"  Per message: {sha256_results['avg_per_message_us']:.2f} μs")
    print(f"  Throughput: {(total_data_mb / (sha256_results['avg_ms'] / 1000)):.2f} MB/s\n")
    
    # Benchmark xxhash
    xxhash_results = None
    speedup = None
    
    if XXHASH_AVAILABLE:
        print("Benchmarking xxhash...")
        xxhash_results = benchmark_xxhash(messages, iterations)
        print(f"  Average: {xxhash_results['avg_ms']:.3f} ms")
        print(f"  Per message: {xxhash_results['avg_per_message_us']:.2f} μs")
        print(f"  Throughput: {(total_data_mb / (xxhash_results['avg_ms'] / 1000)):.2f} MB/s\n")
        
        # Calculate speedup
        speedup = sha256_results['avg_ms'] / xxhash_results['avg_ms']
        print(f"{'='*60}")
        print(f"Speedup: {speedup:.2f}x (xxhash vs SHA256)")
        print(f"Target: 3-5x speedup")
        print(f"Status: {'✅ PASS' if 3.0 <= speedup <= 5.0 else '⚠️  OUTSIDE TARGET RANGE'}")
        print(f"{'='*60}\n")
    else:
        print("⚠️  xxhash not available - cannot compare\n")
    
    # Compile results
    results = {
        "benchmark_name": "hash_performance",
        "message_size_kb": message_size_kb,
        "message_count": message_count,
        "iterations": iterations,
        "total_data_mb": total_data_mb,
        "sha256": sha256_results,
        "xxhash": xxhash_results,
        "speedup": speedup,
        "target_speedup_min": 3.0,
        "target_speedup_max": 5.0,
        "passed": speedup is not None and 3.0 <= speedup <= 5.0
    }
    
    return results


def run_multiple_sizes() -> List[Dict]:
    """Run benchmarks with different message sizes."""
    sizes = [1, 10, 100, 1000]  # KB
    all_results = []
    
    print("\n" + "="*60)
    print("Running benchmarks with multiple message sizes")
    print("="*60)
    
    for size_kb in sizes:
        # Adjust message count based on size to keep total data reasonable
        if size_kb <= 10:
            message_count = 1000
        elif size_kb <= 100:
            message_count = 100
        else:
            message_count = 10
        
        results = run_benchmark(message_size_kb=size_kb, message_count=message_count, iterations=5)
        all_results.append(results)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY - Hash Performance Across Message Sizes")
    print("="*60)
    print(f"{'Size (KB)':<12} {'SHA256 (ms)':<15} {'xxhash (ms)':<15} {'Speedup':<10} {'Status'}")
    print("-"*60)
    
    for result in all_results:
        size = result['message_size_kb']
        sha256_time = result['sha256']['avg_ms']
        xxhash_time = result['xxhash']['avg_ms'] if result['xxhash'] and 'avg_ms' in result['xxhash'] else None
        speedup = result['speedup']
        status = "✅ PASS" if result['passed'] else "⚠️  FAIL"
        
        if xxhash_time:
            print(f"{size:<12} {sha256_time:<15.3f} {xxhash_time:<15.3f} {speedup:<10.2f} {status}")
        else:
            print(f"{size:<12} {sha256_time:<15.3f} {'N/A':<15} {'N/A':<10} N/A")
    
    print("="*60 + "\n")
    
    return all_results


if __name__ == "__main__":
    # Run single benchmark
    single_result = run_benchmark(message_size_kb=10, message_count=1000, iterations=10)
    
    # Run multiple sizes
    all_results = run_multiple_sizes()
    
    # Export results
    import json
    output = {
        "single_benchmark": single_result,
        "multiple_sizes": all_results,
        "timestamp": time.time()
    }
    
    with open("benchmarks/results_hash_performance.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("Results saved to: benchmarks/results_hash_performance.json")

