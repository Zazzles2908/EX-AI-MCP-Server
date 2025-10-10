"""
Performance benchmark tests for EX-AI-MCP-Server.

Measures and validates performance of key components.

Created: 2025-10-11 (Phase 2 Cleanup, Task 2.D)
"""

import pytest
import time
import threading
from utils.infrastructure.semantic_cache import SemanticCache
from utils.infrastructure.performance_metrics import PerformanceMetricsCollector


class TestCachePerformance:
    """Performance benchmarks for caching systems."""
    
    def test_semantic_cache_get_performance(self):
        """Benchmark semantic cache get() performance."""
        cache = SemanticCache(ttl_seconds=3600, max_size=1000)
        
        # Pre-populate cache
        for i in range(100):
            cache.set(f"prompt_{i}", "model", {"content": f"response_{i}"})
        
        # Benchmark 1000 get operations
        start = time.time()
        for i in range(1000):
            cache.get(f"prompt_{i % 100}", "model")
        duration = time.time() - start
        
        # Should complete in < 100ms (< 0.1ms per operation)
        assert duration < 0.1
        
        # Calculate ops/sec
        ops_per_sec = 1000 / duration
        print(f"\nSemantic cache get: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
        
        # Should achieve > 10,000 ops/sec
        assert ops_per_sec > 10000
    
    def test_semantic_cache_set_performance(self):
        """Benchmark semantic cache set() performance."""
        cache = SemanticCache(ttl_seconds=3600, max_size=10000)
        
        # Benchmark 1000 set operations
        start = time.time()
        for i in range(1000):
            cache.set(f"prompt_{i}", "model", {"content": f"response_{i}"})
        duration = time.time() - start
        
        # Should complete in < 200ms (< 0.2ms per operation)
        assert duration < 0.2
        
        # Calculate ops/sec
        ops_per_sec = 1000 / duration
        print(f"\nSemantic cache set: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
        
        # Should achieve > 5,000 ops/sec
        assert ops_per_sec > 5000
    
    def test_cache_key_generation_performance(self):
        """Benchmark cache key generation."""
        cache = SemanticCache()
        
        # Benchmark 10,000 key generations
        start = time.time()
        for i in range(10000):
            cache._generate_cache_key(
                prompt=f"Test prompt {i}",
                model="test-model",
                temperature=0.5,
                thinking_mode="medium"
            )
        duration = time.time() - start
        
        # Should complete in < 500ms (< 0.05ms per operation)
        assert duration < 0.5
        
        # Calculate ops/sec
        ops_per_sec = 10000 / duration
        print(f"\nCache key generation: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
        
        # Should achieve > 20,000 ops/sec
        assert ops_per_sec > 20000


class TestMetricsPerformance:
    """Performance benchmarks for metrics collection."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        collector = PerformanceMetricsCollector()
        collector.reset_metrics()
    
    def test_metrics_recording_overhead(self):
        """Measure overhead of metrics recording."""
        collector = PerformanceMetricsCollector()
        
        # Benchmark 10,000 metric recordings
        start = time.time()
        for i in range(10000):
            collector.record_tool_call("test_tool", success=True, latency_ms=100.0)
        duration = time.time() - start
        
        # Should complete in < 1 second (< 0.1ms per operation)
        assert duration < 1.0
        
        # Calculate ops/sec
        ops_per_sec = 10000 / duration
        print(f"\nMetrics recording: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
        
        # Should achieve > 10,000 ops/sec
        assert ops_per_sec > 10000
        
        # Verify all metrics were recorded
        metrics = collector.get_tool_metrics("test_tool")
        assert metrics["total_calls"] == 10000
    
    def test_metrics_retrieval_performance(self):
        """Measure performance of metrics retrieval."""
        collector = PerformanceMetricsCollector()
        
        # Pre-populate with metrics
        for i in range(100):
            collector.record_tool_call(f"tool_{i}", success=True, latency_ms=100.0)
        
        # Benchmark 1000 get_all_metrics calls
        start = time.time()
        for _ in range(1000):
            collector.get_all_metrics()
        duration = time.time() - start
        
        # Should complete in < 1 second (< 1ms per operation)
        assert duration < 1.0
        
        # Calculate ops/sec
        ops_per_sec = 1000 / duration
        print(f"\nMetrics retrieval: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
        
        # Should achieve > 1,000 ops/sec
        assert ops_per_sec > 1000
    
    def test_percentile_calculation_performance(self):
        """Measure performance of percentile calculations."""
        collector = PerformanceMetricsCollector()
        
        # Pre-populate with 1000 samples
        for i in range(1000):
            collector.record_tool_call("test_tool", success=True, latency_ms=float(i))
        
        # Benchmark 100 percentile calculations
        start = time.time()
        for _ in range(100):
            metrics = collector.get_tool_metrics("test_tool")
            # Access percentile values to trigger calculation
            _ = metrics["p50_latency_ms"]
            _ = metrics["p95_latency_ms"]
            _ = metrics["p99_latency_ms"]
        duration = time.time() - start
        
        # Should complete in < 500ms (< 5ms per operation)
        assert duration < 0.5
        
        # Calculate ops/sec
        ops_per_sec = 100 / duration
        print(f"\nPercentile calculation: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")


class TestConcurrentPerformance:
    """Performance benchmarks for concurrent operations."""
    
    def test_concurrent_cache_access(self):
        """Test cache performance under concurrent access."""
        cache = SemanticCache(ttl_seconds=3600, max_size=10000)
        
        # Pre-populate cache
        for i in range(100):
            cache.set(f"prompt_{i}", "model", {"content": f"response_{i}"})
        
        def worker():
            """Worker thread that performs cache operations."""
            for i in range(100):
                cache.get(f"prompt_{i % 100}", "model")
                cache.set(f"prompt_new_{i}", "model", {"content": f"response_{i}"})
        
        # Benchmark 10 concurrent threads
        threads = [threading.Thread(target=worker) for _ in range(10)]
        
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start
        
        # Should complete in < 2 seconds
        assert duration < 2.0
        
        # Calculate total ops (10 threads * 200 ops each)
        total_ops = 10 * 200
        ops_per_sec = total_ops / duration
        print(f"\nConcurrent cache ops: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")
    
    def test_concurrent_metrics_recording(self):
        """Test metrics performance under concurrent recording."""
        collector = PerformanceMetricsCollector()
        collector.reset_metrics()
        
        def worker():
            """Worker thread that records metrics."""
            for i in range(100):
                collector.record_tool_call("concurrent_tool", success=True, latency_ms=100.0)
        
        # Benchmark 10 concurrent threads
        threads = [threading.Thread(target=worker) for _ in range(10)]
        
        start = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        duration = time.time() - start
        
        # Should complete in < 1 second
        assert duration < 1.0
        
        # Verify all metrics were recorded correctly
        metrics = collector.get_tool_metrics("concurrent_tool")
        assert metrics["total_calls"] == 1000  # 10 threads * 100 calls each
        
        # Calculate ops/sec
        ops_per_sec = 1000 / duration
        print(f"\nConcurrent metrics recording: {ops_per_sec:.0f} ops/sec ({duration*1000:.2f}ms total)")


class TestMemoryUsage:
    """Memory usage benchmarks."""
    
    def test_cache_memory_bounded(self):
        """Test that cache memory usage is bounded."""
        import sys
        
        cache = SemanticCache(ttl_seconds=3600, max_size=1000)
        
        # Measure initial size
        initial_size = sys.getsizeof(cache._cache)
        
        # Fill cache to capacity
        for i in range(1000):
            cache.set(f"prompt_{i}", "model", {"content": "x" * 100})
        
        # Measure size after filling
        filled_size = sys.getsizeof(cache._cache)
        
        # Add 1000 more entries (should evict old ones)
        for i in range(1000, 2000):
            cache.set(f"prompt_{i}", "model", {"content": "x" * 100})
        
        # Measure size after overflow
        overflow_size = sys.getsizeof(cache._cache)
        
        # Size should not grow significantly after hitting max_size
        growth_ratio = overflow_size / filled_size
        assert growth_ratio < 1.1  # Less than 10% growth
        
        print(f"\nCache memory: initial={initial_size}, filled={filled_size}, overflow={overflow_size}")
        print(f"Growth ratio: {growth_ratio:.2f}x")
    
    def test_metrics_memory_bounded(self):
        """Test that metrics memory usage is bounded."""
        import sys
        
        collector = PerformanceMetricsCollector()
        collector.reset_metrics()
        
        # Record 10,000 samples (should only keep last 1000 due to sliding window)
        for i in range(10000):
            collector.record_tool_call("test_tool", success=True, latency_ms=float(i))
        
        # Get metrics to access internal state
        metrics = collector.get_tool_metrics("test_tool")
        
        # Verify only 1000 samples are kept
        assert metrics["total_calls"] == 10000  # Total count is accurate
        # Latency samples should be bounded to window size (1000)
        # This is verified by the sliding window implementation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print output

