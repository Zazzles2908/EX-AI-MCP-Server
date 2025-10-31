"""
Monitoring utilities for EXAI MCP Server

Provides centralized connection monitoring and metrics collection.
Date: 2025-10-31 - Added cache metrics collection
"""

from .connection_monitor import (
    ConnectionMonitor,
    get_monitor,
    record_websocket_event,
    record_redis_event,
    record_supabase_event,
    record_kimi_event,
    record_glm_event,
)

from .cache_metrics_collector import (
    CacheMetricsCollector,
    CacheMetricEvent,
    get_collector,
    start_collector,
    stop_collector,
    record_cache_hit,
    record_cache_miss,
    record_cache_set,
    record_cache_error
)

__all__ = [
    "ConnectionMonitor",
    "get_monitor",
    "record_websocket_event",
    "record_redis_event",
    "record_supabase_event",
    "record_kimi_event",
    "record_glm_event",
    "CacheMetricsCollector",
    "CacheMetricEvent",
    "get_collector",
    "start_collector",
    "stop_collector",
    "record_cache_hit",
    "record_cache_miss",
    "record_cache_set",
    "record_cache_error"
]

