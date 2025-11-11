"""
Centralized Connection Monitoring System for EXAI MCP Server

Tracks all connection points and data flow for easier debugging:
- WebSocket connections (ws_server.py)
- Redis connections (storage_backend.py)
- Supabase connections (supabase_client.py)
- Kimi API connections (kimi provider)
- GLM API connections (glm provider)

Each connection point reports:
- Data sent/received
- Response times
- Error rates
- Connected script/function names (for debugging)

Created: 2025-10-18
Updated: 2025-10-23 - Added Redis persistence with dual-write pattern
Updated: 2025-10-23 - Added Melbourne/Australia timezone support
Purpose: Centralized monitoring for easier bug fixing with persistent storage
"""

import time
import logging
import os
import threading
import queue
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import deque, defaultdict
from threading import Lock
import json

from utils.timezone_helper import melbourne_now_iso, to_aedt, UTC_TZ

logger = logging.getLogger(__name__)


@dataclass
class ConnectionEvent:
    """Single connection event with timing and metadata"""
    timestamp: float
    connection_type: str  # websocket, redis, supabase, kimi, glm
    direction: str  # send, receive, error
    script_name: str  # e.g., "ws_server.py::_handle_message"
    function_name: str  # e.g., "_handle_message"
    data_size_bytes: int
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization with Melbourne/Australia timezone"""
        # PHASE 3.1 (2025-10-23): Convert timestamp to Melbourne timezone for display
        # Create UTC datetime from timestamp, then convert to Melbourne
        utc_dt = datetime.fromtimestamp(self.timestamp, tz=UTC_TZ)
        melb_dt = to_aedt(utc_dt)

        return {
            "timestamp": self.timestamp,
            "datetime": melb_dt.isoformat(),  # Melbourne timezone ISO format
            "connection_type": self.connection_type,
            "direction": self.direction,
            "script": self.script_name,
            "function": self.function_name,
            "data_size_bytes": self.data_size_bytes,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class ConnectionStats:
    """Aggregated statistics for a connection type"""
    connection_type: str
    total_events: int = 0
    total_sent_bytes: int = 0
    total_received_bytes: int = 0
    total_errors: int = 0
    avg_response_time_ms: float = 0.0
    last_event_timestamp: Optional[float] = None
    active_connections: int = 0


class ConnectionMonitor:
    """
    Centralized connection monitoring system with Redis persistence

    Thread-safe singleton that tracks all connection events across the system.
    Provides real-time metrics and historical data for debugging.

    Features:
    - Dual-write pattern: In-memory (fast) + Redis (persistent)
    - Background worker with batching (5s or 100 events)
    - Graceful degradation if Redis fails
    - Historical data recovery on startup
    - Circuit breaker pattern for resilience
    """

    _instance = None
    _lock = Lock()

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

        # In-memory storage (fast access)
        self._events: deque = deque(maxlen=10000)  # Keep last 10k events
        self._stats: Dict[str, ConnectionStats] = {}
        self._active_connections: Dict[str, int] = {}
        self._event_lock = Lock()

        # Redis persistence configuration
        self._redis_enabled = os.getenv('REDIS_PERSISTENCE_ENABLED', 'true').lower() == 'true'
        self._redis_batch_size = int(os.getenv('REDIS_BATCH_SIZE', '100'))
        self._redis_flush_interval = int(os.getenv('REDIS_FLUSH_INTERVAL', '5'))
        self._redis_queue_size = int(os.getenv('REDIS_QUEUE_SIZE', '1000'))
        self._redis_retention_hours = int(os.getenv('REDIS_RETENTION_HOURS', '24'))

        # Redis persistence components
        self._redis_queue: queue.Queue = queue.Queue(maxsize=self._redis_queue_size)
        self._redis_worker: Optional[threading.Thread] = None
        self._redis_shutdown = threading.Event()
        self._redis_storage = None

        # Circuit breaker for Redis failures
        self._redis_circuit_breaker = {
            'failures': 0,
            'last_failure': 0,
            'state': 'closed',  # closed, open, half-open
            'recovery_timer': None
        }

        logger.info(f"[CONNECTION_MONITOR] Initialized with 10k event buffer (Redis persistence: {self._redis_enabled})")

        # Initialize Redis persistence if enabled
        if self._redis_enabled:
            self._initialize_redis_persistence()

    def _initialize_redis_persistence(self) -> None:
        """Initialize Redis persistence components"""
        try:
            # Use direct Redis connection to avoid circular import with StorageBackend
            import redis

            # Get Redis configuration from environment
            # Try REDIS_URL first (includes password), then fall back to individual settings
            redis_url = os.getenv('REDIS_URL')

            if redis_url:
                # Parse Redis URL (format: redis://:password@host:port/db)
                self._redis_storage = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )
            else:
                # Fall back to individual settings
                redis_host = os.getenv('REDIS_HOST', 'localhost')
                redis_port = int(os.getenv('REDIS_PORT', '6379'))
                redis_password = os.getenv('REDIS_PASSWORD', '')
                redis_db = int(os.getenv('REDIS_DB', '0'))

                self._redis_storage = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password if redis_password else None,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

            # Test Redis connection
            self._redis_storage.ping()
            logger.info("[CONNECTION_MONITOR] Redis connection established")

            # Start background worker
            self._start_redis_worker()

            # Load historical data
            self._load_historical_data()

        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to initialize Redis persistence: {e}")
            self._redis_enabled = False
            self._redis_storage = None

    def _start_redis_worker(self) -> None:
        """Start background worker thread for Redis writes"""
        self._redis_worker = threading.Thread(
            target=self._redis_worker_loop,
            daemon=True,
            name="ConnectionMonitor-RedisWorker"
        )
        self._redis_worker.start()
        logger.info("[CONNECTION_MONITOR] Redis worker thread started")

    def _redis_worker_loop(self) -> None:
        """Background worker that batches Redis writes"""
        batch: List[Tuple[str, Dict[str, Any]]] = []
        last_flush = time.time()

        while not self._redis_shutdown.is_set():
            try:
                # Try to get event from queue with timeout
                try:
                    event_data = self._redis_queue.get(timeout=1.0)
                    batch.append(event_data)
                except queue.Empty:
                    pass

                # Flush if batch is full or time interval passed
                current_time = time.time()
                should_flush = (
                    len(batch) >= self._redis_batch_size or
                    (batch and current_time - last_flush >= self._redis_flush_interval)
                )

                if should_flush:
                    self._flush_to_redis(batch)
                    batch = []
                    last_flush = current_time

            except Exception as e:
                logger.error(f"[CONNECTION_MONITOR] Redis worker error: {e}")
                time.sleep(1)  # Back off on error

        # Flush remaining events on shutdown
        if batch:
            logger.info(f"[CONNECTION_MONITOR] Flushing {len(batch)} events on shutdown")
            self._flush_to_redis(batch)

    def _flush_to_redis(self, batch: List[Tuple[str, Dict[str, Any]]]) -> None:
        """Write batch of events to Redis"""
        if not self._redis_enabled or not batch or not self._redis_storage:
            return

        # Check circuit breaker
        if self._redis_circuit_breaker['state'] == 'open':
            logger.debug("[CONNECTION_MONITOR] Circuit breaker open - skipping Redis write")
            return

        try:
            pipe = self._redis_storage.pipeline()
            retention_seconds = self._redis_retention_hours * 3600

            for connection_type, event_data in batch:
                # Store event in sorted set (score = timestamp)
                event_key = f"connection_monitor:{connection_type}:events"
                score = event_data['timestamp']
                value = json.dumps(event_data)
                pipe.zadd(event_key, {value: score})
                pipe.expire(event_key, retention_seconds)

                # Update stats hash
                stats_key = f"connection_monitor:{connection_type}:stats"
                if 'stats' in event_data:
                    pipe.hset(stats_key, mapping=event_data['stats'])
                    pipe.expire(stats_key, retention_seconds)

            pipe.execute()

            # Reset circuit breaker on success
            if self._redis_circuit_breaker['failures'] > 0:
                logger.info("[CONNECTION_MONITOR] Redis connection recovered")
                self._redis_circuit_breaker['failures'] = 0
                self._redis_circuit_breaker['state'] = 'closed'

        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to write to Redis: {e}")
            self._handle_redis_error(e)

    def _handle_redis_error(self, error: Exception) -> None:
        """Handle Redis errors with circuit breaker pattern"""
        cb = self._redis_circuit_breaker
        cb['failures'] += 1
        cb['last_failure'] = time.time()

        if cb['failures'] >= 5:
            cb['state'] = 'open'
            logger.warning(f"[CONNECTION_MONITOR] Circuit breaker opened after {cb['failures']} failures")

            # Schedule recovery attempt
            if cb['recovery_timer']:
                cb['recovery_timer'].cancel()
            cb['recovery_timer'] = threading.Timer(30.0, self._attempt_redis_recovery)
            cb['recovery_timer'].daemon = True
            cb['recovery_timer'].start()

    def _attempt_redis_recovery(self) -> None:
        """Attempt to recover Redis connection"""
        try:
            if self._redis_storage:
                self._redis_storage.ping()
                self._redis_circuit_breaker['state'] = 'closed'
                self._redis_circuit_breaker['failures'] = 0
                logger.info("[CONNECTION_MONITOR] Redis connection recovered - circuit breaker closed")
        except Exception as e:
            logger.debug(f"[CONNECTION_MONITOR] Redis recovery failed: {e} - will retry later")
            # Schedule another retry
            timer = threading.Timer(30.0, self._attempt_redis_recovery)
            timer.daemon = True
            timer.start()
            self._redis_circuit_breaker['recovery_timer'] = timer

    def _load_historical_data(self) -> None:
        """Load last 24 hours of data from Redis on startup"""
        if not self._redis_enabled or not self._redis_storage:
            return

        try:
            cutoff_time = time.time() - (self._redis_retention_hours * 3600)
            loaded_count = 0

            for connection_type in ['websocket', 'redis', 'supabase', 'kimi', 'glm']:
                event_key = f"connection_monitor:{connection_type}:events"

                # Get events from last N hours
                events = self._redis_storage.zrangebyscore(
                    event_key, cutoff_time, '+inf', withscores=True
                )

                for event_json, timestamp in events:
                    try:
                        event_data = json.loads(event_json)
                        # Reconstruct ConnectionEvent object
                        event = ConnectionEvent(
                            timestamp=event_data.get('timestamp', timestamp),
                            connection_type=event_data.get('connection_type', connection_type),
                            direction=event_data.get('direction', 'unknown'),
                            script_name=event_data.get('script', 'unknown'),
                            function_name=event_data.get('function', 'unknown'),
                            data_size_bytes=event_data.get('data_size_bytes', 0),
                            response_time_ms=event_data.get('response_time_ms'),
                            error=event_data.get('error'),
                            metadata=event_data.get('metadata', {})
                        )

                        with self._event_lock:
                            self._events.append(event)
                            self._update_stats(event)

                        loaded_count += 1
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"[CONNECTION_MONITOR] Skipping invalid event: {e}")
                        continue

            logger.info(f"[CONNECTION_MONITOR] Loaded {loaded_count} historical events from Redis")

        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to load historical data: {e}")

    def _queue_for_redis(self, connection_type: str, event_data: Dict[str, Any]) -> None:
        """Queue event for Redis persistence"""
        if not self._redis_enabled:
            return

        try:
            # Add current stats to event data for Redis storage
            with self._event_lock:
                if connection_type in self._stats:
                    event_data['stats'] = asdict(self._stats[connection_type])

            self._redis_queue.put_nowait((connection_type, event_data))
        except queue.Full:
            logger.warning("[CONNECTION_MONITOR] Redis queue full - dropping event")
        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to queue event for Redis: {e}")

    def record_event(
        self,
        connection_type: str,
        direction: str,
        script_name: str,
        function_name: str,
        data_size_bytes: int,
        response_time_ms: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a connection event with dual-write to memory and Redis

        Args:
            connection_type: Type of connection (websocket, redis, supabase, kimi, glm)
            direction: Direction of data flow (send, receive, error)
            script_name: Name of the script (e.g., "ws_server.py")
            function_name: Name of the function (e.g., "_handle_message")
            data_size_bytes: Size of data in bytes
            response_time_ms: Response time in milliseconds (optional)
            error: Error message if any (optional)
            metadata: Additional metadata (optional)
        """
        event = ConnectionEvent(
            timestamp=time.time(),
            connection_type=connection_type,
            direction=direction,
            script_name=script_name,
            function_name=function_name,
            data_size_bytes=data_size_bytes,
            response_time_ms=response_time_ms,
            error=error,
            metadata=metadata or {}
        )

        # Write to in-memory storage (fast)
        with self._event_lock:
            self._events.append(event)
            self._update_stats(event)

        # Queue for Redis persistence (async)
        self._queue_for_redis(connection_type, event.to_dict())

        # Log the event for real-time monitoring
        if error:
            logger.error(
                f"[{connection_type.upper()}] ERROR in {script_name}::{function_name} - {error}"
            )
        else:
            logger.debug(
                f"[{connection_type.upper()}] {direction.upper()} "
                f"{script_name}::{function_name} "
                f"({data_size_bytes} bytes"
                f"{f', {response_time_ms:.2f}ms' if response_time_ms else ''})"
            )

    def record_duration(
        self,
        model: str,
        duration_ms: float,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        request_type: str = "text_only",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record model duration for adaptive timeout calculation.

        DAY 1 IMPLEMENTATION (2025-11-03): Adaptive Timeout Architecture
        K2 Decision: Extend existing kimi/glm events with adaptive timeout metadata

        This method reuses the existing record_event() infrastructure by detecting
        the provider from the model name and adding adaptive timeout metadata to
        the existing kimi/glm connection types.

        Args:
            model: Model name (e.g., "kimi-k2", "glm-4.6")
            duration_ms: Actual duration in milliseconds
            prompt_tokens: Number of prompt tokens (optional)
            completion_tokens: Number of completion tokens (optional)
            request_type: Type of request (text_only, file_based, file_reuse)
            metadata: Additional metadata (optional)
        """
        # Detect provider from model name
        model_lower = model.lower()
        if "kimi" in model_lower or "k2" in model_lower or "moonshot" in model_lower:
            provider = "kimi"
        elif "glm" in model_lower or "zhipu" in model_lower:
            provider = "glm"
        else:
            provider = "unknown"
            logger.warning(f"[ADAPTIVE_TIMEOUT] Unknown provider for model: {model}")

        # Calculate total tokens
        total_tokens = 0
        if prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        # Build adaptive timeout metadata
        adaptive_metadata = {
            "adaptive_timeout": True,
            "model": model,
            "request_type": request_type,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "adaptive_timeout_ms": duration_ms,
            **(metadata or {})
        }

        # Reuse existing record_event with adaptive timeout metadata
        self.record_event(
            connection_type=provider,
            direction="duration_recorded",
            script_name="adaptive_timeout.py",
            function_name="record_duration",
            data_size_bytes=total_tokens,  # Use tokens as data size
            response_time_ms=duration_ms,
            metadata=adaptive_metadata
        )

        logger.info(
            f"[ADAPTIVE_TIMEOUT] Recorded duration for {model}: "
            f"{duration_ms:.2f}ms ({total_tokens} tokens, {request_type})"
        )

    def _update_stats(self, event: ConnectionEvent) -> None:
        """Update aggregated statistics (called with lock held)"""
        conn_type = event.connection_type
        
        if conn_type not in self._stats:
            self._stats[conn_type] = ConnectionStats(connection_type=conn_type)
        
        stats = self._stats[conn_type]
        stats.total_events += 1
        stats.last_event_timestamp = event.timestamp
        
        if event.direction == "send":
            stats.total_sent_bytes += event.data_size_bytes
        elif event.direction == "receive":
            stats.total_received_bytes += event.data_size_bytes
        elif event.direction == "error":
            stats.total_errors += 1
        
        if event.response_time_ms is not None:
            # Update running average
            old_avg = stats.avg_response_time_ms
            old_count = stats.total_events - 1
            stats.avg_response_time_ms = (
                (old_avg * old_count + event.response_time_ms) / stats.total_events
            )
    
    def increment_active_connections(self, connection_type: str) -> None:
        """Increment active connection count for a connection type"""
        with self._event_lock:
            if connection_type not in self._active_connections:
                self._active_connections[connection_type] = 0
            self._active_connections[connection_type] += 1
            
            if connection_type in self._stats:
                self._stats[connection_type].active_connections = (
                    self._active_connections[connection_type]
                )
    
    def decrement_active_connections(self, connection_type: str) -> None:
        """Decrement active connection count for a connection type"""
        with self._event_lock:
            if connection_type in self._active_connections:
                self._active_connections[connection_type] = max(
                    0, self._active_connections[connection_type] - 1
                )
                
                if connection_type in self._stats:
                    self._stats[connection_type].active_connections = (
                        self._active_connections[connection_type]
                    )
    
    def get_stats(self, connection_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated statistics
        
        Args:
            connection_type: Specific connection type, or None for all
            
        Returns:
            Dictionary of statistics
        """
        with self._event_lock:
            if connection_type:
                stats = self._stats.get(connection_type)
                return asdict(stats) if stats else {}
            else:
                return {
                    conn_type: asdict(stats)
                    for conn_type, stats in self._stats.items()
                }
    
    def get_recent_events(
        self,
        connection_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent connection events
        
        Args:
            connection_type: Filter by connection type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        with self._event_lock:
            events = list(self._events)
        
        if connection_type:
            events = [e for e in events if e.connection_type == connection_type]
        
        # Return most recent events first
        events = events[-limit:]
        events.reverse()
        
        return [event.to_dict() for event in events]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all connection monitoring data"""
        with self._event_lock:
            return {
                "total_events": len(self._events),
                "connection_types": list(self._stats.keys()),
                "stats": self.get_stats(),
                "active_connections": dict(self._active_connections),
                "buffer_size": self._events.maxlen,
                "buffer_usage": len(self._events),
                "redis_enabled": self._redis_enabled,
                "redis_queue_size": self._redis_queue.qsize() if self._redis_enabled else 0,
                "redis_circuit_breaker": self._redis_circuit_breaker['state']
            }

    def get_historical_data(
        self,
        connection_type: str = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get historical data from Redis for a specific connection type or all types

        Args:
            connection_type: Type of connection to query (None = all types)
            hours: Number of hours of history to retrieve

        Returns:
            List of event dictionaries
        """
        if not self._redis_enabled or not self._redis_storage:
            logger.debug("[CONNECTION_MONITOR] Redis not enabled - returning empty historical data")
            return []

        try:
            cutoff_time = time.time() - (hours * 3600)

            # PHASE 3.1 (2025-10-23): Support connection_type=None for all services
            if connection_type is None:
                # Get events from all connection types
                all_events = []
                for conn_type in ['websocket', 'redis', 'supabase', 'kimi', 'glm']:
                    event_key = f"connection_monitor:{conn_type}:events"
                    events = self._redis_storage.zrangebyscore(
                        event_key, cutoff_time, '+inf', withscores=True
                    )
                    for event_json, timestamp in events:
                        try:
                            event_data = json.loads(event_json)
                            all_events.append(event_data)
                        except json.JSONDecodeError:
                            continue
                return all_events
            else:
                # Get events for specific connection type
                event_key = f"connection_monitor:{connection_type}:events"
                events = self._redis_storage.zrangebyscore(
                    event_key, cutoff_time, '+inf', withscores=True
                )

                result = []
                for event_json, timestamp in events:
                    try:
                        event_data = json.loads(event_json)
                        result.append(event_data)
                    except json.JSONDecodeError:
                        continue

                return result

        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to get historical data: {e}")
            return []

    def get_time_series_data(
        self,
        connection_type: str,
        interval_minutes: int = 5,
        hours: int = 24
    ) -> Dict[str, Dict[str, int]]:
        """
        Get time-series aggregated data for charts

        Args:
            connection_type: Type of connection to query
            interval_minutes: Time bucket size in minutes
            hours: Number of hours of history to retrieve

        Returns:
            Dictionary mapping timestamps to aggregated metrics
        """
        if not self._redis_enabled or not self._redis_storage:
            logger.debug("[CONNECTION_MONITOR] Redis not enabled - returning empty time-series data")
            return {}

        try:
            cutoff_time = time.time() - (hours * 3600)
            event_key = f"connection_monitor:{connection_type}:events"

            events = self._redis_storage.zrangebyscore(
                event_key, cutoff_time, '+inf', withscores=True
            )

            # Aggregate by time interval
            buckets = defaultdict(lambda: {
                'count': 0,
                'errors': 0,
                'total_bytes': 0,
                'avg_response_time': 0.0,
                'response_times': []
            })

            interval_seconds = interval_minutes * 60

            for event_json, timestamp in events:
                try:
                    event_data = json.loads(event_json)
                    bucket_time = int(timestamp // interval_seconds) * interval_seconds
                    bucket = buckets[bucket_time]

                    bucket['count'] += 1
                    bucket['total_bytes'] += event_data.get('data_size_bytes', 0)

                    if event_data.get('error'):
                        bucket['errors'] += 1

                    if event_data.get('response_time_ms') is not None:
                        bucket['response_times'].append(event_data['response_time_ms'])

                except json.JSONDecodeError:
                    continue

            # Calculate averages
            result = {}
            for bucket_time, bucket in buckets.items():
                if bucket['response_times']:
                    bucket['avg_response_time'] = sum(bucket['response_times']) / len(bucket['response_times'])
                del bucket['response_times']  # Remove raw data
                result[str(bucket_time)] = bucket

            return result

        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to get time-series data: {e}")
            return {}

    def shutdown(self) -> None:
        """Graceful shutdown - flush pending events and stop worker"""
        if self._redis_enabled and self._redis_worker:
            logger.info("[CONNECTION_MONITOR] Shutting down Redis worker...")
            self._redis_shutdown.set()
            self._redis_worker.join(timeout=10)
            logger.info("[CONNECTION_MONITOR] Redis worker stopped")

    def export_json(self, filepath: str) -> None:
        """Export monitoring data to JSON file"""
        try:
            data = {
                "summary": self.get_summary(),
                "recent_events": self.get_recent_events(limit=1000)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"[CONNECTION_MONITOR] Exported monitoring data to {filepath}")
        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to export data: {e}")


# Global singleton instance
_monitor = ConnectionMonitor()


def get_monitor() -> ConnectionMonitor:
    """Get the global connection monitor instance"""
    return _monitor


# Convenience functions for common operations
def record_websocket_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a WebSocket event"""
    _monitor.record_event(
        connection_type="websocket",
        direction=direction,
        script_name="ws_server.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_redis_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Redis event"""
    _monitor.record_event(
        connection_type="redis",
        direction=direction,
        script_name="storage_backend.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_supabase_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Supabase event"""
    _monitor.record_event(
        connection_type="supabase",
        direction=direction,
        script_name="supabase_client.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_kimi_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Kimi API event"""
    _monitor.record_event(
        connection_type="kimi",
        direction=direction,
        script_name="kimi_provider",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_glm_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a GLM API event"""
    _monitor.record_event(
        connection_type="glm",
        direction=direction,
        script_name="glm_provider",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )

