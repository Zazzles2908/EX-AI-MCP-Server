"""
Performance Benchmark: Hash Function Performance

Compares xxhash vs SHA256 vs MD5 speed for message deduplication.
Tests with various message sizes to validate hash function selection.

Created: 2025-10-26
Phase: Task 2 Week 1.5 - Performance Benchmarks
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
EXAI Recommendation: Validate hash performance meets targets (xxhash > 10,000 msg/s)
"""

import asyncio
import time
import hashlib
import json
from typing import Dict, List, Tuple

try:
    import xxhash
    XXHASH_AVAILABLE = True
except ImportError:
    XXHASH_AVAILABLE = False
    print("⚠️  xxhash not available, will test SHA256 and MD5 only")


def generate_message(size_bytes: int) -> dict:
    """Generate a test message of specified size."""
    # Create message with data field of specified size
    data = "x" * size_bytes
    return {"type": "test", "data": data, "timestamp": time.time()}


def hash_xxhash(message: dict) -> str:
    """Hash message using xxhash."""
    if not XXHASH_AVAILABLE:
        return ""
    message_str = json.dumps(message, sort_keys=True)
    return xxhash.xxh64(message_str.encode()).hexdigest()


def hash_sha256(message: dict) -> str:
    """Hash message using SHA256."""
    message_str = json.dumps(message, sort_keys=True)
    return hashlib.sha256(message_str.encode()).hexdigest()


def hash_md5(message: dict) -> str:
    """Hash message using MD5."""
    message_str = json.dumps(message, sort_keys=True)
    return hashlib.md5(message_str.encode()).hexdigest()


def benchmark_hash_function(
    hash_func,
    func_name: str,
    message_size: int,
    iterations: int = 10000
) -> Tuple[float, float]:
    """
    Benchmark a hash function.
    
    Returns:
        (throughput_msg_per_sec, avg_latency_ms)
    """
    message = generate_message(message_size)
    
    # Warmup
    for _ in range(100):
        hash_func(message)
    
    # Benchmark
    start_time = time.perf_counter()
    for _ in range(iterations):
        hash_func(message)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    throughput = iterations / total_time
    avg_latency_ms = (total_time / iterations) * 1000
    
    return throughput, avg_latency_ms


async def run_benchmarks():
    """Run all hash performance benchmarks."""
    print("\n" + "=" * 60)
    print("Hash Function Performance Benchmark")
    print("=" * 60)
    
    # Test configurations
    message_sizes = [
        (100, "100B"),
        (1024, "1KB"),
        (10240, "10KB"),
        (102400, "100KB")
    ]
    
    iterations = 10000
    
    # Results storage
    results = {}
    
    # Test each hash function with each message size
    for size_bytes, size_label in message_sizes:
        print(f"\n[Testing with {size_label} messages, {iterations} iterations]")
        print("-" * 60)
        
        results[size_label] = {}
        
        # Test xxhash
        if XXHASH_AVAILABLE:
            throughput, latency = benchmark_hash_function(
                hash_xxhash, "xxhash", size_bytes, iterations
            )
            results[size_label]["xxhash"] = {
                "throughput": throughput,
                "latency": latency
            }
            print(f"xxhash:  {throughput:>10,.0f} msg/s  |  {latency:>8.4f} ms/msg")
        
        # Test SHA256
        throughput, latency = benchmark_hash_function(
            hash_sha256, "SHA256", size_bytes, iterations
        )
        results[size_label]["SHA256"] = {
            "throughput": throughput,
            "latency": latency
        }
        print(f"SHA256:  {throughput:>10,.0f} msg/s  |  {latency:>8.4f} ms/msg")
        
        # Test MD5
        throughput, latency = benchmark_hash_function(
            hash_md5, "MD5", size_bytes, iterations
        )
        results[size_label]["MD5"] = {
            "throughput": throughput,
            "latency": latency
        }
        print(f"MD5:     {throughput:>10,.0f} msg/s  |  {latency:>8.4f} ms/msg")
    
    # Performance targets validation
    print("\n" + "=" * 60)
    print("Performance Targets Validation")
    print("=" * 60)
    
    targets_met = True
    
    # Target: xxhash > 10,000 msg/s for 1KB messages
    if XXHASH_AVAILABLE:
        xxhash_1kb = results["1KB"]["xxhash"]["throughput"]
        xxhash_target = 10000
        xxhash_met = xxhash_1kb > xxhash_target
        targets_met = targets_met and xxhash_met
        
        status = "✅" if xxhash_met else "❌"
        print(f"{status} xxhash (1KB): {xxhash_1kb:,.0f} msg/s (target: > {xxhash_target:,} msg/s)")
    
    # Target: SHA256 > 1,000 msg/s for 1KB messages
    sha256_1kb = results["1KB"]["SHA256"]["throughput"]
    sha256_target = 1000
    sha256_met = sha256_1kb > sha256_target
    targets_met = targets_met and sha256_met
    
    status = "✅" if sha256_met else "❌"
    print(f"{status} SHA256 (1KB): {sha256_1kb:,.0f} msg/s (target: > {sha256_target:,} msg/s)")
    
    # Speedup comparison
    if XXHASH_AVAILABLE:
        print("\n" + "=" * 60)
        print("Speedup Analysis (vs SHA256)")
        print("=" * 60)
        
        for size_label in ["100B", "1KB", "10KB", "100KB"]:
            xxhash_throughput = results[size_label]["xxhash"]["throughput"]
            sha256_throughput = results[size_label]["SHA256"]["throughput"]
            speedup = xxhash_throughput / sha256_throughput
            
            print(f"{size_label:>6}: xxhash is {speedup:.1f}x faster than SHA256")
    
    # Summary
    print("\n" + "=" * 60)
    if targets_met:
        print("✅ HASH PERFORMANCE BENCHMARK PASSED")
    else:
        print("❌ HASH PERFORMANCE BENCHMARK FAILED")
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

