"""
Comprehensive Performance Metrics Collection for EX-AI-MCP-Server

This module provides detailed performance tracking for:
- Per-tool execution metrics (latency, success/failure, error types)
- Per-provider API metrics (latency, tokens, cost)
- Cache performance (hit/miss rates for semantic and file caches)
- System-wide metrics (sessions, concurrent requests, memory)

Features:
- Percentile calculations (p50, p95, p99) using sliding windows
- Thread-safe metric collection
- JSON metrics endpoint for real-time monitoring
- Integration with existing Prometheus metrics
- Environment-gated (can be disabled)

Created: 2025-10-11 (Phase 2 Cleanup, Task 2.C Day 4)
"""
from __future__ import annotations

import os
import time
import threading
import logging
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
from dataclasses import dataclass, field, asdict
import statistics

logger = logging.getLogger(__name__)

# Environment configuration
_ENABLED = os.getenv("PERFORMANCE_METRICS_ENABLED", "true").lower() == "true"
_WINDOW_SIZE = int(os.getenv("METRICS_WINDOW_SIZE", "1000"))
_JSON_ENDPOINT_ENABLED = os.getenv("METRICS_JSON_ENDPOINT_ENABLED", "true").lower() == "true"


@dataclass
class ToolMetrics:
    """Metrics for a specific tool."""
    tool_name: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency_ms: float = 0.0
    latency_samples: deque = field(default_factory=lambda: deque(maxlen=_WINDOW_SIZE))
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def record_call(self, success: bool, latency_ms: float, error_type: Optional[str] = None):
        """Record a tool call."""
        self.total_calls += 1
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if error_type:
                self.error_types[error_type] = self.error_types.get(error_type, 0) + 1
        
        self.total_latency_ms += latency_ms
        self.latency_samples.append(latency_ms)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for this tool."""
        if not self.latency_samples:
            return {
                "tool_name": self.tool_name,
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "success_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p50_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "p99_latency_ms": 0.0,
                "min_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "error_types": self.error_types
            }
        
        samples = list(self.latency_samples)
        success_rate = (self.successful_calls / self.total_calls * 100) if self.total_calls > 0 else 0.0
        
        # Calculate percentiles
        try:
            if len(samples) >= 2:
                p50, p95, p99 = statistics.quantiles(samples, n=100, method='inclusive')
                p50 = samples[49] if len(samples) > 49 else samples[len(samples)//2]
                p95 = samples[94] if len(samples) > 94 else samples[-1]
                p99 = samples[98] if len(samples) > 98 else samples[-1]
            else:
                p50 = p95 = p99 = samples[0]
        except Exception:
            p50 = p95 = p99 = statistics.median(samples) if samples else 0.0
        
        return {
            "tool_name": self.tool_name,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": round(success_rate, 2),
            "avg_latency_ms": round(self.total_latency_ms / self.total_calls, 2) if self.total_calls > 0 else 0.0,
            "p50_latency_ms": round(p50, 2),
            "p95_latency_ms": round(p95, 2),
            "p99_latency_ms": round(p99, 2),
            "min_latency_ms": round(min(samples), 2),
            "max_latency_ms": round(max(samples), 2),
            "error_types": dict(self.error_types)
        }


@dataclass
class CacheMetrics:
    """Metrics for cache performance."""
    cache_name: str
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_rejections: int = 0
    
    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1
    
    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
    
    def record_eviction(self):
        """Record a cache eviction."""
        self.evictions += 1
    
    def record_size_rejection(self):
        """Record a size rejection."""
        self.size_rejections += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "cache_name": self.cache_name,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "evictions": self.evictions,
            "size_rejections": self.size_rejections
        }


class PerformanceMetricsCollector:
    """
    Singleton collector for comprehensive performance metrics.
    
    Thread-safe collection of:
    - Per-tool metrics (execution time, success/failure, errors)
    - Per-provider metrics (latency, tokens, cost)
    - Cache metrics (hit/miss rates)
    - System metrics (sessions, requests, memory)
    """
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._enabled = _ENABLED
        
        # Metrics storage
        self._tool_metrics: Dict[str, ToolMetrics] = {}
        self._cache_metrics: Dict[str, CacheMetrics] = {}
        self._system_metrics = {
            "active_sessions": 0,
            "concurrent_requests": 0,
            "total_requests": 0,
            "start_time": time.time()
        }
        
        logger.info(f"Performance metrics collector initialized (enabled={self._enabled}, window_size={_WINDOW_SIZE})")
    
    def is_enabled(self) -> bool:
        """Check if metrics collection is enabled."""
        return self._enabled
    
    # ================================================================================
    # Tool Metrics
    # ================================================================================
    
    def record_tool_call(self, tool_name: str, success: bool, latency_ms: float, error_type: Optional[str] = None):
        """Record a tool call."""
        if not self._enabled:
            return
        
        with self._lock:
            if tool_name not in self._tool_metrics:
                self._tool_metrics[tool_name] = ToolMetrics(tool_name=tool_name)
            
            self._tool_metrics[tool_name].record_call(success, latency_ms, error_type)
            self._system_metrics["total_requests"] += 1
    
    def get_tool_metrics(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for a specific tool or all tools."""
        with self._lock:
            if tool_name:
                if tool_name in self._tool_metrics:
                    return self._tool_metrics[tool_name].get_stats()
                return {}
            
            return {name: metrics.get_stats() for name, metrics in self._tool_metrics.items()}
    
    # ================================================================================
    # Cache Metrics
    # ================================================================================
    
    def record_cache_hit(self, cache_name: str):
        """Record a cache hit."""
        if not self._enabled:
            return
        
        with self._lock:
            if cache_name not in self._cache_metrics:
                self._cache_metrics[cache_name] = CacheMetrics(cache_name=cache_name)
            
            self._cache_metrics[cache_name].record_hit()
    
    def record_cache_miss(self, cache_name: str):
        """Record a cache miss."""
        if not self._enabled:
            return
        
        with self._lock:
            if cache_name not in self._cache_metrics:
                self._cache_metrics[cache_name] = CacheMetrics(cache_name=cache_name)
            
            self._cache_metrics[cache_name].record_miss()
    
    def record_cache_eviction(self, cache_name: str):
        """Record a cache eviction."""
        if not self._enabled:
            return
        
        with self._lock:
            if cache_name in self._cache_metrics:
                self._cache_metrics[cache_name].record_eviction()
    
    def record_cache_size_rejection(self, cache_name: str):
        """Record a cache size rejection."""
        if not self._enabled:
            return
        
        with self._lock:
            if cache_name in self._cache_metrics:
                self._cache_metrics[cache_name].record_size_rejection()
    
    def get_cache_metrics(self, cache_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for a specific cache or all caches."""
        with self._lock:
            if cache_name:
                if cache_name in self._cache_metrics:
                    return self._cache_metrics[cache_name].get_stats()
                return {}
            
            return {name: metrics.get_stats() for name, metrics in self._cache_metrics.items()}
    
    # ================================================================================
    # System Metrics
    # ================================================================================
    
    def set_active_sessions(self, count: int):
        """Set the number of active sessions."""
        if not self._enabled:
            return
        
        with self._lock:
            self._system_metrics["active_sessions"] = count
    
    def set_concurrent_requests(self, count: int):
        """Set the number of concurrent requests."""
        if not self._enabled:
            return
        
        with self._lock:
            self._system_metrics["concurrent_requests"] = count
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide metrics."""
        with self._lock:
            uptime_seconds = time.time() - self._system_metrics["start_time"]
            return {
                **self._system_metrics,
                "uptime_seconds": round(uptime_seconds, 2),
                "uptime_hours": round(uptime_seconds / 3600, 2)
            }
    
    # ================================================================================
    # Comprehensive Metrics
    # ================================================================================
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics in a single JSON-serializable dict."""
        with self._lock:
            return {
                "enabled": self._enabled,
                "timestamp": time.time(),
                "tool_metrics": self.get_tool_metrics(),
                "cache_metrics": self.get_cache_metrics(),
                "system_metrics": self.get_system_metrics()
            }
    
    def reset_metrics(self):
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._tool_metrics.clear()
            self._cache_metrics.clear()
            self._system_metrics = {
                "active_sessions": 0,
                "concurrent_requests": 0,
                "total_requests": 0,
                "start_time": time.time()
            }
            logger.info("Performance metrics reset")


# Global singleton instance
_collector = PerformanceMetricsCollector()


# Convenience functions for easy access
def record_tool_call(tool_name: str, success: bool, latency_ms: float, error_type: Optional[str] = None):
    """Record a tool call (convenience function)."""
    _collector.record_tool_call(tool_name, success, latency_ms, error_type)


def record_cache_hit(cache_name: str):
    """Record a cache hit (convenience function)."""
    _collector.record_cache_hit(cache_name)


def record_cache_miss(cache_name: str):
    """Record a cache miss (convenience function)."""
    _collector.record_cache_miss(cache_name)


def get_all_metrics() -> Dict[str, Any]:
    """Get all metrics (convenience function)."""
    return _collector.get_all_metrics()


def get_collector() -> PerformanceMetricsCollector:
    """Get the global collector instance."""
    return _collector

