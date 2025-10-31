"""
Cache Metrics Collector
Date: 2025-10-31
Purpose: Week 2-3 Monitoring Phase - Collect and send cache metrics to Supabase
EXAI Consultation ID: c78bd85e-470a-4abb-8d0e-aeed72fab0a0

This module:
1. Collects cache metrics from SemanticCache operations
2. Batches metrics for efficient transmission
3. Sends metrics to Supabase Edge Function for aggregation
4. Provides local fallback when Supabase unavailable
"""

import asyncio
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Literal
from threading import Lock

import httpx
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Configuration from environment
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
METRICS_BATCH_SIZE = int(os.getenv('CACHE_METRICS_BATCH_SIZE', '100'))
METRICS_FLUSH_INTERVAL = int(os.getenv('CACHE_METRICS_FLUSH_INTERVAL', '60'))  # seconds
METRICS_ENABLED = os.getenv('CACHE_METRICS_ENABLED', 'true').lower() == 'true'


@dataclass
class CacheMetricEvent:
    """Individual cache metric event."""
    cache_key: str
    operation_type: Literal['hit', 'miss', 'set', 'evict', 'error']
    implementation_type: Literal['legacy', 'new']
    response_time_ms: Optional[int] = None
    cache_size: Optional[int] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class CacheMetricsCollector:
    """
    Collects cache metrics and sends them to Supabase for aggregation.
    
    Features:
    - Batching for efficient transmission
    - Automatic flushing on interval or batch size
    - Local fallback when Supabase unavailable
    - Thread-safe metric collection
    """

    def __init__(
        self,
        supabase_url: str = SUPABASE_URL,
        supabase_key: str = SUPABASE_KEY,
        batch_size: int = METRICS_BATCH_SIZE,
        flush_interval: int = METRICS_FLUSH_INTERVAL,
        enabled: bool = METRICS_ENABLED
    ):
        """
        Initialize cache metrics collector.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
            batch_size: Number of metrics to batch before sending
            flush_interval: Seconds between automatic flushes
            enabled: Whether metrics collection is enabled
        """
        self.enabled = enabled
        self.batch_size = batch_size
        self.flush_interval = flush_interval

        # Metrics buffer
        self._buffer: deque = deque(maxlen=10000)  # Max 10k metrics in buffer
        self._buffer_lock = Lock()

        # Store Supabase credentials
        self._supabase_url = supabase_url
        self._supabase_key = supabase_key

        # Supabase client
        self._supabase: Optional[Client] = None
        if enabled and supabase_url and supabase_key:
            try:
                self._supabase = create_client(supabase_url, supabase_key)
                logger.info("[CACHE_METRICS] Supabase client initialized")
            except Exception as e:
                logger.error(f"[CACHE_METRICS] Failed to initialize Supabase client: {e}")
        
        # HTTP client for Edge Function calls
        # EXAI Fix (2025-11-01): Increased timeout from 10s to 30s for Supabase Edge Function
        self._http_client = httpx.AsyncClient(timeout=30.0)
        
        # Background flush task
        self._flush_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Statistics
        self._stats = {
            'total_collected': 0,
            'total_sent': 0,
            'total_failed': 0,
            'last_flush': None
        }

    async def start(self):
        """Start background flush task."""
        if not self.enabled:
            logger.info("[CACHE_METRICS] Metrics collection disabled")
            return
        
        if self._running:
            logger.warning("[CACHE_METRICS] Already running")
            return
        
        self._running = True
        self._flush_task = asyncio.create_task(self._background_flush())
        logger.info(f"[CACHE_METRICS] Started (batch_size={self.batch_size}, flush_interval={self.flush_interval}s)")

    async def stop(self):
        """Stop background flush task and flush remaining metrics."""
        if not self._running:
            return
        
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining metrics
        await self.flush()
        
        # Close HTTP client
        await self._http_client.aclose()
        
        logger.info("[CACHE_METRICS] Stopped")

    def record_metric(self, event: CacheMetricEvent):
        """
        Record a cache metric event.
        
        Args:
            event: Cache metric event to record
        """
        if not self.enabled:
            return
        
        with self._buffer_lock:
            self._buffer.append(event)
            self._stats['total_collected'] += 1
        
        # Trigger flush if batch size reached
        if len(self._buffer) >= self.batch_size:
            asyncio.create_task(self.flush())

    async def flush(self):
        """Flush buffered metrics to Supabase with exponential backoff retry."""
        if not self.enabled or not self._supabase:
            return

        # Get metrics from buffer
        with self._buffer_lock:
            if not self._buffer:
                return

            metrics = list(self._buffer)
            self._buffer.clear()

        # EXAI Fix (2025-11-01): Implement exponential backoff retry for transient failures
        max_retries = 3
        base_delay = 1.0  # Start with 1 second

        for attempt in range(max_retries):
            try:
                # Convert to dict format
                metrics_data = [asdict(m) for m in metrics]

                # Send to Supabase Edge Function
                edge_function_url = f"{self._supabase_url}/functions/v1/cache-metrics-aggregator"

                logger.debug(f"[CACHE_METRICS] Flushing {len(metrics)} metrics (attempt {attempt + 1}/{max_retries})")

                response = await self._http_client.post(
                    edge_function_url,
                    json={'metrics': metrics_data},
                    headers={
                        'Authorization': f'Bearer {self._supabase_key}',
                        'Content-Type': 'application/json'
                    }
                )

                if response.status_code == 200:
                    self._stats['total_sent'] += len(metrics)
                    self._stats['last_flush'] = datetime.utcnow().isoformat()
                    logger.info(f"[CACHE_METRICS] Successfully flushed {len(metrics)} metrics to Supabase")
                    return  # Success - exit retry loop
                else:
                    self._stats['total_failed'] += len(metrics)
                    logger.error(f"[CACHE_METRICS] Failed to flush metrics: {response.status_code} {response.text}")

                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return

                    # Retry on server errors (5xx) or timeouts
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"[CACHE_METRICS] Retrying in {delay}s...")
                        await asyncio.sleep(delay)

            except (httpx.TimeoutException, httpx.ConnectError, asyncio.TimeoutError) as e:
                # Transient network errors - retry with backoff
                logger.warning(f"[CACHE_METRICS] Transient error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}")

                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"[CACHE_METRICS] Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    # All retries exhausted
                    self._stats['total_failed'] += len(metrics)
                    logger.error(f"[CACHE_METRICS] All retries exhausted for metrics flush: {e}")

                    # Re-add to buffer for next flush cycle
                    with self._buffer_lock:
                        for metric in metrics[:1000]:
                            if len(self._buffer) < self._buffer.maxlen:
                                self._buffer.append(metric)
                    return

            except Exception as e:
                import traceback
                self._stats['total_failed'] += len(metrics)
                logger.error(f"[CACHE_METRICS] Error flushing metrics: {e}")
                logger.error(f"[CACHE_METRICS] Traceback: {traceback.format_exc()}")

                # Re-add to buffer for retry
                with self._buffer_lock:
                    for metric in metrics[:1000]:
                        if len(self._buffer) < self._buffer.maxlen:
                            self._buffer.append(metric)
                return

    async def _background_flush(self):
        """Background task to flush metrics periodically."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self.flush()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[CACHE_METRICS] Error in background flush: {e}")

    def get_stats(self) -> Dict:
        """Get collector statistics."""
        with self._buffer_lock:
            buffer_size = len(self._buffer)
        
        return {
            **self._stats,
            'buffer_size': buffer_size,
            'enabled': self.enabled
        }


# Global collector instance
_collector: Optional[CacheMetricsCollector] = None


def get_collector() -> CacheMetricsCollector:
    """Get global cache metrics collector instance."""
    global _collector
    if _collector is None:
        _collector = CacheMetricsCollector()
    return _collector


async def start_collector():
    """Start global cache metrics collector."""
    collector = get_collector()
    await collector.start()


async def stop_collector():
    """Stop global cache metrics collector."""
    collector = get_collector()
    await collector.stop()


def record_cache_hit(
    cache_key: str,
    implementation_type: Literal['legacy', 'new'],
    response_time_ms: int,
    cache_size: Optional[int] = None
):
    """Record a cache hit event."""
    collector = get_collector()
    collector.record_metric(CacheMetricEvent(
        cache_key=cache_key,
        operation_type='hit',
        implementation_type=implementation_type,
        response_time_ms=response_time_ms,
        cache_size=cache_size
    ))


def record_cache_miss(
    cache_key: str,
    implementation_type: Literal['legacy', 'new'],
    response_time_ms: int,
    cache_size: Optional[int] = None
):
    """Record a cache miss event."""
    collector = get_collector()
    collector.record_metric(CacheMetricEvent(
        cache_key=cache_key,
        operation_type='miss',
        implementation_type=implementation_type,
        response_time_ms=response_time_ms,
        cache_size=cache_size
    ))


def record_cache_set(
    cache_key: str,
    implementation_type: Literal['legacy', 'new'],
    response_time_ms: int,
    cache_size: Optional[int] = None
):
    """Record a cache set event."""
    collector = get_collector()
    collector.record_metric(CacheMetricEvent(
        cache_key=cache_key,
        operation_type='set',
        implementation_type=implementation_type,
        response_time_ms=response_time_ms,
        cache_size=cache_size
    ))


def record_cache_error(
    cache_key: str,
    implementation_type: Literal['legacy', 'new'],
    error_type: str,
    error_message: str
):
    """Record a cache error event."""
    collector = get_collector()
    collector.record_metric(CacheMetricEvent(
        cache_key=cache_key,
        operation_type='error',
        implementation_type=implementation_type,
        error_type=error_type,
        error_message=error_message
    ))

