"""
Quick Metrics Performance Benchmark.

Validates that ProductionMetrics achieves <5% overhead target.

Created: 2025-10-28
Phase: Emergency Metrics Redesign - Validation
EXAI Consultation: b5ba9ff3-a1b2-4dab-af19-c3cc4ce1d8aa
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s'
)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.production_metrics import ProductionMetrics, MetricsConfig, MetricType


def monitor_threads():
    """Monitor thread status during benchmark."""
    print("\n=== THREAD MONITOR ===")
    for thread in threading.enumerate():
        print(f"  Thread: {thread.name}, Alive: {thread.is_alive()}, Daemon: {thread.daemon}")
    print("======================\n")


def benchmark_production_metrics(duration_seconds: float = 5.0) -> dict:
    """Benchmark ProductionMetrics performance."""
    print("\n[DEBUG] Creating MetricsConfig...")
    config = MetricsConfig()
    config.flush_interval = 0.5  # Faster flushing for benchmark
    config.buffer_size = 5000  # Larger buffer to avoid immediate fill
    config.enable_adaptive_sampling = False  # DISABLE adaptive sampling for debugging

    print(f"[DEBUG] Config: sample_rate={config.sample_rate:.1%}, buffer_size={config.buffer_size}, adaptive={config.enable_adaptive_sampling}")

    print("[DEBUG] Creating ProductionMetrics...")
    metrics = ProductionMetrics(config)

    print("[DEBUG] Starting metrics...")
    metrics.start()

    print("[DEBUG] Checking threads after start...")
    monitor_threads()

    print(f"Running benchmark with sample_rate={config.sample_rate:.1%}...")

    # Measure operations
    start = time.perf_counter()
    operations_completed = 0

    print("[DEBUG] Starting operation loop...")
    while (time.perf_counter() - start) < duration_seconds:
        # Simulate metric recording
        metrics.record_metric(MetricType.MESSAGE_SENT, value=1.0, client_id=f"client_{operations_completed % 100}")
        operations_completed += 1

        # Progress logging
        if operations_completed % 100000 == 0:
            print(f"[DEBUG] Completed {operations_completed:,} operations...")
            monitor_threads()

    elapsed = time.perf_counter() - start
    print(f"[DEBUG] Operation loop complete. Elapsed: {elapsed:.2f}s, Operations: {operations_completed:,}")

    # Stop metrics (will flush remaining)
    print("[DEBUG] Stopping metrics...")
    metrics.stop()
    print("[DEBUG] Metrics stopped")

    # Get results
    ops_per_second = operations_completed / elapsed
    final_metrics = metrics.get_metrics()

    print(f"[DEBUG] Final metrics retrieved: {final_metrics.keys()}")

    return {
        "operations_completed": operations_completed,
        "duration_seconds": elapsed,
        "ops_per_second": ops_per_second,
        "sample_rate": config.sample_rate,
        "metrics": final_metrics
    }


def benchmark_no_metrics(duration_seconds: float = 5.0) -> dict:
    """Benchmark with no metrics (baseline)."""
    print("Running baseline benchmark (no metrics)...")
    
    # Measure operations
    start = time.perf_counter()
    operations_completed = 0
    
    while (time.perf_counter() - start) < duration_seconds:
        # Just count operations
        operations_completed += 1
    
    elapsed = time.perf_counter() - start
    ops_per_second = operations_completed / elapsed
    
    return {
        "operations_completed": operations_completed,
        "duration_seconds": elapsed,
        "ops_per_second": ops_per_second
    }


def run_quick_benchmark():
    """Run quick benchmark comparison."""
    print("\n" + "="*60)
    print("QUICK METRICS PERFORMANCE BENCHMARK")
    print("="*60)
    print("Target: <5% CPU overhead")
    print("="*60 + "\n")
    
    # Benchmark with ProductionMetrics
    with_metrics = benchmark_production_metrics(duration_seconds=5.0)
    
    print()
    
    # Benchmark without metrics
    without_metrics = benchmark_no_metrics(duration_seconds=5.0)
    
    # Calculate overhead
    overhead_percent = ((without_metrics['ops_per_second'] - with_metrics['ops_per_second']) / 
                       without_metrics['ops_per_second']) * 100
    
    # Results
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"With ProductionMetrics:  {with_metrics['ops_per_second']:,.0f} ops/sec")
    print(f"Without metrics:         {without_metrics['ops_per_second']:,.0f} ops/sec")
    print(f"CPU Overhead:            {overhead_percent:.2f}%")
    print(f"Sample Rate:             {with_metrics['sample_rate']:.1%}")
    print("="*60)
    print(f"Target: <5% overhead")
    print(f"Status: {'✅ PASS' if overhead_percent < 5.0 else '⚠️  FAIL'}")
    print("="*60)
    
    # Meta-metrics
    if 'meta' in with_metrics['metrics']:
        meta = with_metrics['metrics']['meta']
        print("\nMeta-Metrics:")
        print(f"  Buffer fill ratio: {meta['buffer_fill_ratio']:.1%}")
        print(f"  Metrics added: {meta['metrics_added']:,}")
        print(f"  Metrics dropped: {meta['metrics_dropped']:,}")
        print(f"  Drop rate: {meta['drop_rate']:.2%}")
        print(f"  Flush count: {meta['flush_count']}")
        print(f"  Avg flush time: {meta['avg_flush_duration_ms']:.3f} ms")
    
    # Aggregated metrics
    print("\nAggregated Metrics:")
    print(f"  Messages sent (estimated): {with_metrics['metrics']['messages_sent']:,.0f}")
    print(f"  Uptime: {with_metrics['metrics']['uptime_seconds']:.2f} seconds")
    
    print("\n" + "="*60)
    
    return {
        "with_metrics": with_metrics,
        "without_metrics": without_metrics,
        "overhead_percent": overhead_percent,
        "passed": overhead_percent < 5.0
    }


if __name__ == "__main__":
    results = run_quick_benchmark()
    
    # Export results
    import json
    with open("benchmarks/results_quick_metrics_benchmark.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to: benchmarks/results_quick_metrics_benchmark.json")
    
    # Exit code
    sys.exit(0 if results['passed'] else 1)

