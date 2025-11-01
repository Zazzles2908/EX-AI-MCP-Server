"""
Unified Metrics Collector
Replaces CacheMetricsCollector with simpler Supabase-native approach

PHASE 4 IMPLEMENTATION (2025-11-01): Unified metrics collection
EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce

This collector provides a single source of truth for ALL metrics:
- Cache metrics (hits, misses, sets, errors)
- WebSocket metrics (connections, messages, health)
- Connection metrics (Redis, Supabase, Kimi, GLM)
- Performance metrics (response times, latency)

Key Features:
- Simple 50-item buffer (no complex batching)
- Direct Supabase RPC calls (no Edge Functions)
- Thread-safe operations
- Automatic flush on buffer full
- Minimal overhead

Architecture:
Event → UnifiedMetricsCollector → Supabase RPC → PostgreSQL
                                          ↓
Dashboard ← Supabase Realtime ← Realtime Broadcast
"""

import os
import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from supabase import create_client, Client

logger = logging.getLogger(__name__)


class UnifiedMetricsCollector:
    """
    Single source of truth for all metrics collection.
    
    Replaces multiple redundant collectors with one simple, effective system.
    """
    
    def __init__(self):
        """Initialize unified metrics collector."""
        # PHASE 1 FIX (2025-11-01): Use centralized singleton
        try:
            from src.storage.supabase_singleton import get_supabase_client
            self._supabase = get_supabase_client(use_admin=True)
            logger.info("[UNIFIED_COLLECTOR] Initialized with Supabase persistence (singleton)")
        except Exception as e:
            logger.error(f"[UNIFIED_COLLECTOR] Failed to initialize Supabase client: {e}")
            self._supabase = None
        
        self._buffer: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._buffer_size = int(os.getenv('METRICS_BUFFER_SIZE', '50'))
        
        # Metrics
        self._total_recorded = 0
        self._total_flushed = 0
        self._flush_errors = 0
        
        logger.info(f"[UNIFIED_COLLECTOR] Initialized (buffer_size={self._buffer_size})")
    
    async def record_metric(self, metric_type: str, data: Dict[str, Any]) -> None:
        """
        Record any metric type (cache, websocket, connection, performance).
        
        Args:
            metric_type: Type of metric (cache_hit, cache_miss, websocket_health, etc.)
            data: Metric data dictionary
        """
        with self._lock:
            self._buffer.append({
                'type': metric_type,
                'data': data,
                'timestamp': datetime.utcnow().isoformat()
            })
            self._total_recorded += 1
            
            # Simple buffer management - no complex batching
            if len(self._buffer) >= self._buffer_size:
                await self._flush_internal()
    
    async def flush(self) -> None:
        """Manually flush metrics to Supabase."""
        with self._lock:
            await self._flush_internal()
    
    async def _flush_internal(self) -> None:
        """
        Internal flush implementation (must be called with lock held).

        PHASE 3 FIX (2025-11-01): Added retry logic to prevent data loss on flush failures.
        
        Sends buffered metrics to Supabase via RPC function.
        """
        if not self._buffer:
            return
        
        if not self._supabase:
            logger.debug("[UNIFIED_COLLECTOR] Supabase not configured - discarding metrics")
            self._buffer.clear()
            return
        
        metrics_to_send = self._buffer.copy()
        self._buffer.clear()
        
        try:
            # Call PostgreSQL RPC function for aggregation
            # This replaces the Edge Function approach
            await asyncio.to_thread(
                self._supabase.rpc,
                'aggregate_metrics',
                {'metrics': metrics_to_send}
            )

            self._total_flushed += len(metrics_to_send)
            logger.debug(f"[UNIFIED_COLLECTOR] Flushed {len(metrics_to_send)} metrics to Supabase")

        except Exception as e:
            self._flush_errors += 1
            logger.error(f"[UNIFIED_COLLECTOR] Failed to flush metrics: {e}")
            # PHASE 3 FIX: Re-add failed metrics to buffer for retry
            with self._lock:
                self._buffer.extend(metrics_to_send)
                logger.warning(f"[UNIFIED_COLLECTOR] Re-queued {len(metrics_to_send)} metrics for retry")
            # Don't re-add to buffer - accept data loss on error
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get collector statistics.
        
        Returns:
            Dictionary with collector metrics
        """
        with self._lock:
            return {
                "total_recorded": self._total_recorded,
                "total_flushed": self._total_flushed,
                "flush_errors": self._flush_errors,
                "buffer_size": len(self._buffer),
                "buffer_capacity": self._buffer_size
            }


# Global singleton instance
_collector: Optional[UnifiedMetricsCollector] = None
_collector_lock = threading.Lock()


def get_collector() -> UnifiedMetricsCollector:
    """
    Get the global unified metrics collector instance.
    
    Returns:
        UnifiedMetricsCollector singleton
    """
    global _collector
    
    if _collector is None:
        with _collector_lock:
            if _collector is None:
                _collector = UnifiedMetricsCollector()
    
    return _collector


# Convenience functions for common metric types

async def record_cache_hit(cache_key: str, implementation_type: str, response_time_ms: int, cache_size: int) -> None:
    """Record a cache hit event."""
    collector = get_collector()
    await collector.record_metric('cache_hit', {
        'cache_key': cache_key,
        'implementation': implementation_type,
        'response_time_ms': response_time_ms,
        'cache_size': cache_size
    })


async def record_cache_miss(cache_key: str, implementation_type: str, response_time_ms: int, cache_size: int) -> None:
    """Record a cache miss event."""
    collector = get_collector()
    await collector.record_metric('cache_miss', {
        'cache_key': cache_key,
        'implementation': implementation_type,
        'response_time_ms': response_time_ms,
        'cache_size': cache_size
    })


async def record_cache_set(cache_key: str, implementation_type: str, response_time_ms: int, cache_size: int) -> None:
    """Record a cache set event."""
    collector = get_collector()
    await collector.record_metric('cache_set', {
        'cache_key': cache_key,
        'implementation': implementation_type,
        'response_time_ms': response_time_ms,
        'cache_size': cache_size
    })


async def record_cache_error(cache_key: str, implementation_type: str, error_type: str, error_message: str) -> None:
    """Record a cache error event."""
    collector = get_collector()
    await collector.record_metric('cache_error', {
        'cache_key': cache_key,
        'implementation': implementation_type,
        'error_type': error_type,
        'error_message': error_message
    })


async def record_websocket_health(active_connections: int, total_messages: int, error_count: int) -> None:
    """Record WebSocket health metrics."""
    collector = get_collector()
    await collector.record_metric('websocket_health', {
        'active_connections': active_connections,
        'total_messages': total_messages,
        'error_count': error_count
    })


async def record_connection_event(service: str, event_type: str, details: Dict[str, Any]) -> None:
    """Record a connection event (Redis, Supabase, Kimi, GLM)."""
    collector = get_collector()
    await collector.record_metric('connection_event', {
        'service': service,
        'event_type': event_type,
        **details
    })


async def record_performance_metric(operation: str, duration_ms: int, success: bool, details: Optional[Dict[str, Any]] = None) -> None:
    """Record a performance metric."""
    collector = get_collector()
    await collector.record_metric('performance', {
        'operation': operation,
        'duration_ms': duration_ms,
        'success': success,
        **(details or {})
    })

