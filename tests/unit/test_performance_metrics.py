"""
Unit tests for performance metrics system.

Tests:
- ToolMetrics percentile calculations
- CacheMetrics hit rate calculations
- PerformanceMetricsCollector thread safety
- Metrics recording and retrieval
- Environment configuration

Created: 2025-10-11 (Phase 2 Cleanup, Task 2.C Day 5)
"""

import pytest
import time
import threading
from utils.infrastructure.performance_metrics import (
    PerformanceMetricsCollector,
    ToolMetrics,
    CacheMetrics,
    record_tool_call,
    record_cache_hit,
    record_cache_miss,
    get_all_metrics
)


class TestToolMetrics:
    """Test ToolMetrics dataclass."""
    
    def test_record_successful_call(self):
        """Test recording a successful tool call."""
        metrics = ToolMetrics(tool_name="test_tool")
        metrics.record_call(success=True, latency_ms=100.0)
        
        assert metrics.total_calls == 1
        assert metrics.successful_calls == 1
        assert metrics.failed_calls == 0
        assert metrics.total_latency_ms == 100.0
        assert len(metrics.latency_samples) == 1
    
    def test_record_failed_call(self):
        """Test recording a failed tool call."""
        metrics = ToolMetrics(tool_name="test_tool")
        metrics.record_call(success=False, latency_ms=50.0, error_type="ValueError")
        
        assert metrics.total_calls == 1
        assert metrics.successful_calls == 0
        assert metrics.failed_calls == 1
        assert metrics.error_types["ValueError"] == 1
    
    def test_percentile_calculations(self):
        """Test percentile calculations with various sample sizes."""
        metrics = ToolMetrics(tool_name="test_tool")
        
        # Add 100 samples with known distribution
        for i in range(100):
            metrics.record_call(success=True, latency_ms=float(i * 10))
        
        stats = metrics.get_stats()
        
        assert stats["total_calls"] == 100
        assert stats["success_rate"] == 100.0
        assert stats["min_latency_ms"] == 0.0
        assert stats["max_latency_ms"] == 990.0
        assert 400.0 <= stats["p50_latency_ms"] <= 600.0  # Median around 500
        assert 900.0 <= stats["p95_latency_ms"] <= 990.0  # 95th percentile
        assert 980.0 <= stats["p99_latency_ms"] <= 990.0  # 99th percentile
    
    def test_success_rate_calculation(self):
        """Test success rate percentage calculation."""
        metrics = ToolMetrics(tool_name="test_tool")
        
        # 80 successful, 20 failed
        for _ in range(80):
            metrics.record_call(success=True, latency_ms=100.0)
        for _ in range(20):
            metrics.record_call(success=False, latency_ms=100.0)
        
        stats = metrics.get_stats()
        assert stats["success_rate"] == 80.0
    
    def test_empty_metrics(self):
        """Test metrics with no samples."""
        metrics = ToolMetrics(tool_name="test_tool")
        stats = metrics.get_stats()
        
        assert stats["total_calls"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["avg_latency_ms"] == 0.0


class TestCacheMetrics:
    """Test CacheMetrics dataclass."""
    
    def test_record_hit(self):
        """Test recording cache hits."""
        metrics = CacheMetrics(cache_name="test_cache")
        metrics.record_hit()
        metrics.record_hit()
        
        assert metrics.hits == 2
        assert metrics.misses == 0
    
    def test_record_miss(self):
        """Test recording cache misses."""
        metrics = CacheMetrics(cache_name="test_cache")
        metrics.record_miss()
        
        assert metrics.hits == 0
        assert metrics.misses == 1
    
    def test_hit_rate_calculation(self):
        """Test hit rate percentage calculation."""
        metrics = CacheMetrics(cache_name="test_cache")
        
        # 70 hits, 30 misses = 70% hit rate
        for _ in range(70):
            metrics.record_hit()
        for _ in range(30):
            metrics.record_miss()
        
        stats = metrics.get_stats()
        assert stats["hit_rate"] == 70.0
        assert stats["total_requests"] == 100
    
    def test_evictions_and_rejections(self):
        """Test eviction and size rejection tracking."""
        metrics = CacheMetrics(cache_name="test_cache")
        metrics.record_eviction()
        metrics.record_eviction()
        metrics.record_size_rejection()
        
        stats = metrics.get_stats()
        assert stats["evictions"] == 2
        assert stats["size_rejections"] == 1


class TestPerformanceMetricsCollector:
    """Test PerformanceMetricsCollector singleton."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        collector = PerformanceMetricsCollector()
        collector.reset_metrics()
    
    def test_singleton_pattern(self):
        """Test that collector is a singleton."""
        collector1 = PerformanceMetricsCollector()
        collector2 = PerformanceMetricsCollector()
        
        assert collector1 is collector2
    
    def test_record_tool_call(self):
        """Test recording tool calls."""
        collector = PerformanceMetricsCollector()
        
        collector.record_tool_call("test_tool", success=True, latency_ms=100.0)
        collector.record_tool_call("test_tool", success=True, latency_ms=200.0)
        collector.record_tool_call("test_tool", success=False, latency_ms=50.0, error_type="ValueError")
        
        metrics = collector.get_tool_metrics("test_tool")
        
        assert metrics["total_calls"] == 3
        assert metrics["successful_calls"] == 2
        assert metrics["failed_calls"] == 1
        assert metrics["error_types"]["ValueError"] == 1
    
    def test_record_cache_metrics(self):
        """Test recording cache metrics."""
        collector = PerformanceMetricsCollector()
        
        collector.record_cache_hit("test_cache")
        collector.record_cache_hit("test_cache")
        collector.record_cache_miss("test_cache")
        
        metrics = collector.get_cache_metrics("test_cache")
        
        assert metrics["hits"] == 2
        assert metrics["misses"] == 1
        assert metrics["hit_rate"] == pytest.approx(66.67, rel=0.01)
    
    def test_system_metrics(self):
        """Test system metrics tracking."""
        collector = PerformanceMetricsCollector()
        
        collector.set_active_sessions(5)
        collector.set_concurrent_requests(3)
        
        metrics = collector.get_system_metrics()
        
        assert metrics["active_sessions"] == 5
        assert metrics["concurrent_requests"] == 3
        assert "uptime_seconds" in metrics
        assert "uptime_hours" in metrics
    
    def test_get_all_metrics(self):
        """Test getting all metrics at once."""
        collector = PerformanceMetricsCollector()
        
        collector.record_tool_call("tool1", success=True, latency_ms=100.0)
        collector.record_cache_hit("cache1")
        collector.set_active_sessions(2)
        
        all_metrics = collector.get_all_metrics()
        
        assert "enabled" in all_metrics
        assert "timestamp" in all_metrics
        assert "tool_metrics" in all_metrics
        assert "cache_metrics" in all_metrics
        assert "system_metrics" in all_metrics
        assert "tool1" in all_metrics["tool_metrics"]
        assert "cache1" in all_metrics["cache_metrics"]
    
    def test_thread_safety(self):
        """Test thread-safe concurrent access."""
        collector = PerformanceMetricsCollector()
        
        def record_calls():
            for _ in range(100):
                collector.record_tool_call("concurrent_tool", success=True, latency_ms=100.0)
        
        # Create 10 threads recording concurrently
        threads = [threading.Thread(target=record_calls) for _ in range(10)]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        metrics = collector.get_tool_metrics("concurrent_tool")
        assert metrics["total_calls"] == 1000  # 10 threads * 100 calls each


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        collector = PerformanceMetricsCollector()
        collector.reset_metrics()
    
    def test_record_tool_call_function(self):
        """Test record_tool_call convenience function."""
        record_tool_call("test_tool", success=True, latency_ms=100.0)
        
        metrics = get_all_metrics()
        assert "test_tool" in metrics["tool_metrics"]
    
    def test_record_cache_functions(self):
        """Test cache recording convenience functions."""
        record_cache_hit("test_cache")
        record_cache_miss("test_cache")
        
        metrics = get_all_metrics()
        assert "test_cache" in metrics["cache_metrics"]
        assert metrics["cache_metrics"]["test_cache"]["hits"] == 1
        assert metrics["cache_metrics"]["test_cache"]["misses"] == 1


class TestPerformanceOverhead:
    """Test performance overhead of metrics collection."""
    
    def test_recording_overhead(self):
        """Test that metrics recording has minimal overhead."""
        collector = PerformanceMetricsCollector()
        
        # Measure time to record 10,000 tool calls
        start = time.time()
        for i in range(10000):
            collector.record_tool_call("perf_test", success=True, latency_ms=100.0)
        duration = time.time() - start
        
        # Should complete in less than 1 second (< 0.1ms per call)
        assert duration < 1.0
        
        # Verify all calls were recorded
        metrics = collector.get_tool_metrics("perf_test")
        assert metrics["total_calls"] == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

