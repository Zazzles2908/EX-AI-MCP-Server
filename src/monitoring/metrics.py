"""
Centralized Metrics Collection

Provides Prometheus-compatible metrics for monitoring and alerting.
Aggregates metrics from all system components.

Created: 2025-10-18
EXAI Consultation: 30441b5d-87d0-4f31-864e-d40e8dcbcad2
Critical Gap #2: Centralized Metrics Collection (8 hours)
"""

import logging
import os
from prometheus_client import Counter, Histogram, Gauge, start_http_server, REGISTRY
from typing import Optional

logger = logging.getLogger(__name__)

# ============================================================================
# REQUEST METRICS
# ============================================================================

REQUEST_COUNT = Counter(
    'mcp_requests_total',
    'Total MCP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'mcp_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float('inf')]
)

ACTIVE_CONNECTIONS = Gauge(
    'mcp_active_connections',
    'Number of active WebSocket connections'
)

# ============================================================================
# CACHE METRICS
# ============================================================================

CACHE_OPERATIONS = Counter(
    'mcp_cache_operations_total',
    'Cache operations',
    ['operation', 'result']  # operation: get/set/delete, result: hit/miss/error
)

CACHE_HIT_RATIO = Gauge(
    'mcp_cache_hit_ratio',
    'Cache hit ratio (0.0 to 1.0)'
)

# ============================================================================
# STORAGE METRICS
# ============================================================================

STORAGE_OPERATIONS = Counter(
    'mcp_storage_operations_total',
    'Storage operations',
    ['operation', 'backend', 'result']  # backend: redis/memory/supabase
)

STORAGE_LATENCY = Histogram(
    'mcp_storage_latency_seconds',
    'Storage operation latency',
    ['operation', 'backend'],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, float('inf')]
)

STORAGE_ERRORS = Counter(
    'mcp_storage_errors_total',
    'Storage operation errors',
    ['backend', 'error_type']
)

# ============================================================================
# API PROVIDER METRICS
# ============================================================================

API_CALLS = Counter(
    'mcp_api_calls_total',
    'External API calls',
    ['provider', 'model', 'status']  # provider: kimi/glm, status: success/error/timeout
)

API_LATENCY = Histogram(
    'mcp_api_latency_seconds',
    'API call latency',
    ['provider', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')]
)

API_ERRORS = Counter(
    'mcp_api_errors_total',
    'API call errors',
    ['provider', 'model', 'error_type']
)

TOKEN_USAGE = Counter(
    'mcp_tokens_total',
    'Token usage',
    ['provider', 'model', 'type']  # type: input/output/total
)

TOKEN_COST = Counter(
    'mcp_token_cost_total',
    'Estimated token cost in USD',
    ['provider', 'model']
)

# ============================================================================
# SYSTEM METRICS
# ============================================================================

MEMORY_USAGE = Gauge(
    'mcp_memory_usage_bytes',
    'Process memory usage in bytes'
)

CPU_USAGE = Gauge(
    'mcp_cpu_usage_percent',
    'Process CPU usage percentage'
)

DISK_USAGE = Gauge(
    'mcp_disk_usage_percent',
    'Disk usage percentage'
)

# ============================================================================
# CONCURRENCY & SEMAPHORE METRICS (Added 2025-10-19)
# ============================================================================

SEMAPHORE_LEAKS_DETECTED = Counter(
    'mcp_semaphore_leaks_detected_total',
    'Total semaphore leaks detected',
    ['semaphore_type']  # type: global/provider/session
)

SEMAPHORE_RECOVERIES = Counter(
    'mcp_semaphore_recoveries_total',
    'Total semaphore recovery operations',
    ['semaphore_type', 'status']  # status: success/partial/failed
)

SEMAPHORE_CURRENT_VALUE = Gauge(
    'mcp_semaphore_current_value',
    'Current semaphore value',
    ['semaphore_type', 'provider']  # provider: global/kimi/glm
)

SEMAPHORE_EXPECTED_VALUE = Gauge(
    'mcp_semaphore_expected_value',
    'Expected semaphore value',
    ['semaphore_type', 'provider']
)

CONCURRENT_REQUESTS = Gauge(
    'mcp_concurrent_requests',
    'Current number of concurrent requests',
    ['provider']  # provider: global/kimi/glm
)

SEMAPHORE_WAIT_TIME = Histogram(
    'mcp_semaphore_wait_seconds',
    'Time spent waiting for semaphore acquisition',
    ['semaphore_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0, float('inf')]
)

SEMAPHORE_ACQUISITION_FAILURES = Counter(
    'mcp_semaphore_acquisition_failures_total',
    'Total semaphore acquisition failures (OVER_CAPACITY)',
    ['semaphore_type', 'provider']
)

SEMAPHORE_QUEUE_DEPTH = Gauge(
    'mcp_semaphore_queue_depth',
    'Number of requests waiting for semaphore acquisition',
    ['semaphore_type', 'provider']
)

SEMAPHORE_ACQUISITIONS = Counter(
    'mcp_semaphore_acquisitions_total',
    'Total semaphore acquisitions',
    ['semaphore_type', 'provider']
)

SEMAPHORE_RELEASES = Counter(
    'mcp_semaphore_releases_total',
    'Total semaphore releases',
    ['semaphore_type', 'provider']
)

SEMAPHORE_EXHAUSTION_EVENTS = Counter(
    'mcp_semaphore_exhaustion_events_total',
    'Total semaphore exhaustion events (0 permits available)',
    ['semaphore_type', 'provider']
)

# ============================================================================
# ERROR METRICS
# ============================================================================

ERROR_COUNT = Counter(
    'mcp_errors_total',
    'Total errors',
    ['component', 'error_type', 'severity']  # severity: warning/error/critical
)

# ============================================================================
# BUSINESS METRICS
# ============================================================================

CONVERSATION_COUNT = Counter(
    'mcp_conversations_total',
    'Total conversations created'
)

MESSAGE_COUNT = Counter(
    'mcp_messages_total',
    'Total messages processed',
    ['role']  # role: user/assistant/system
)

FILE_UPLOADS = Counter(
    'mcp_file_uploads_total',
    'Total file uploads',
    ['file_type', 'status']  # status: success/error
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def record_request(method: str, endpoint: str, status: str, duration: float) -> None:
    """Record a request with metrics"""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
    REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)


def record_cache_operation(operation: str, result: str) -> None:
    """Record a cache operation"""
    CACHE_OPERATIONS.labels(operation=operation, result=result).inc()


def record_storage_operation(
    operation: str,
    backend: str,
    result: str,
    latency: Optional[float] = None
) -> None:
    """Record a storage operation"""
    STORAGE_OPERATIONS.labels(operation=operation, backend=backend, result=result).inc()
    if latency is not None:
        STORAGE_LATENCY.labels(operation=operation, backend=backend).observe(latency)


def record_storage_error(backend: str, error_type: str) -> None:
    """Record a storage error"""
    STORAGE_ERRORS.labels(backend=backend, error_type=error_type).inc()


def record_api_call(
    provider: str,
    model: str,
    status: str,
    latency: Optional[float] = None
) -> None:
    """Record an API call"""
    API_CALLS.labels(provider=provider, model=model, status=status).inc()
    if latency is not None:
        API_LATENCY.labels(provider=provider, model=model).observe(latency)


def record_api_error(provider: str, model: str, error_type: str) -> None:
    """Record an API error"""
    API_ERRORS.labels(provider=provider, model=model, error_type=error_type).inc()


def record_token_usage(provider: str, model: str, input_tokens: int, output_tokens: int) -> None:
    """Record token usage"""
    TOKEN_USAGE.labels(provider=provider, model=model, type='input').inc(input_tokens)
    TOKEN_USAGE.labels(provider=provider, model=model, type='output').inc(output_tokens)
    TOKEN_USAGE.labels(provider=provider, model=model, type='total').inc(input_tokens + output_tokens)


def record_error(component: str, error_type: str, severity: str = 'error') -> None:
    """Record an error"""
    ERROR_COUNT.labels(component=component, error_type=error_type, severity=severity).inc()


# ============================================================================
# SEMAPHORE METRICS HELPERS (Added 2025-10-19)
# ============================================================================

def record_semaphore_leak(semaphore_type: str, expected: int, actual: int) -> None:
    """Record a semaphore leak detection"""
    SEMAPHORE_LEAKS_DETECTED.labels(semaphore_type=semaphore_type).inc()
    logger.warning(f"Semaphore leak detected: {semaphore_type} expected={expected}, actual={actual}")


def record_semaphore_recovery(semaphore_type: str, status: str, recovered_count: int) -> None:
    """Record a semaphore recovery operation"""
    SEMAPHORE_RECOVERIES.labels(semaphore_type=semaphore_type, status=status).inc()
    logger.info(f"Semaphore recovery: {semaphore_type} status={status}, recovered={recovered_count}")


def update_semaphore_values(semaphore_type: str, provider: str, current: int, expected: int) -> None:
    """Update current and expected semaphore values"""
    SEMAPHORE_CURRENT_VALUE.labels(semaphore_type=semaphore_type, provider=provider).set(current)
    SEMAPHORE_EXPECTED_VALUE.labels(semaphore_type=semaphore_type, provider=provider).set(expected)


def record_semaphore_wait(semaphore_type: str, wait_time: float) -> None:
    """Record time spent waiting for semaphore acquisition"""
    SEMAPHORE_WAIT_TIME.labels(semaphore_type=semaphore_type).observe(wait_time)


def record_semaphore_acquisition_failure(semaphore_type: str, provider: str) -> None:
    """Record a semaphore acquisition failure (OVER_CAPACITY)"""
    SEMAPHORE_ACQUISITION_FAILURES.labels(semaphore_type=semaphore_type, provider=provider).inc()
    logger.warning(f"Semaphore acquisition failed: {semaphore_type} provider={provider}")


def update_concurrent_requests(provider: str, count: int) -> None:
    """Update current concurrent request count"""
    CONCURRENT_REQUESTS.labels(provider=provider).set(count)


def update_semaphore_queue_depth(semaphore_type: str, provider: str, depth: int) -> None:
    """Update semaphore queue depth (number of waiting requests)"""
    SEMAPHORE_QUEUE_DEPTH.labels(semaphore_type=semaphore_type, provider=provider).set(depth)


def record_semaphore_acquisition(semaphore_type: str, provider: str) -> None:
    """Record a semaphore acquisition"""
    SEMAPHORE_ACQUISITIONS.labels(semaphore_type=semaphore_type, provider=provider).inc()


def record_semaphore_release(semaphore_type: str, provider: str) -> None:
    """Record a semaphore release"""
    SEMAPHORE_RELEASES.labels(semaphore_type=semaphore_type, provider=provider).inc()


def record_semaphore_exhaustion(semaphore_type: str, provider: str) -> None:
    """Record a semaphore exhaustion event (0 permits available)"""
    SEMAPHORE_EXHAUSTION_EVENTS.labels(semaphore_type=semaphore_type, provider=provider).inc()
    logger.critical(f"ALERT: Semaphore exhausted! {semaphore_type} provider={provider} - Immediate attention required")


def update_system_metrics() -> None:
    """Update system metrics (call periodically)"""
    try:
        import psutil
        process = psutil.Process()
        
        # Memory
        memory_info = process.memory_info()
        MEMORY_USAGE.set(memory_info.rss)
        
        # CPU
        cpu_percent = process.cpu_percent(interval=0.1)
        CPU_USAGE.set(cpu_percent)
        
        # Disk
        disk_usage = psutil.disk_usage('.')
        DISK_USAGE.set(disk_usage.percent)
        
    except Exception as e:
        logger.error(f"Failed to update system metrics: {e}")


def calculate_cache_hit_ratio() -> None:
    """Calculate and update cache hit ratio"""
    try:
        # Get cache hit/miss counts from Prometheus registry
        hits = 0
        misses = 0
        
        for metric in REGISTRY.collect():
            if metric.name == 'mcp_cache_operations_total':
                for sample in metric.samples:
                    if sample.labels.get('result') == 'hit':
                        hits += sample.value
                    elif sample.labels.get('result') == 'miss':
                        misses += sample.value
        
        total = hits + misses
        if total > 0:
            ratio = hits / total
            CACHE_HIT_RATIO.set(ratio)
        
    except Exception as e:
        logger.error(f"Failed to calculate cache hit ratio: {e}")


def init_metrics_server(port: int = 8000) -> None:
    """
    Start Prometheus metrics server.
    
    Args:
        port: Port to bind to (default: 8000)
    """
    try:
        start_http_server(port)
        logger.info(f"[METRICS] Prometheus metrics server started on port {port}")
        logger.info(f"[METRICS] Metrics available at http://localhost:{port}/metrics")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")
        raise


# ============================================================================
# PERIODIC UPDATES
# ============================================================================

async def start_periodic_updates(interval: int = 60) -> None:
    """
    Start periodic metric updates.
    
    Args:
        interval: Update interval in seconds (default: 60)
    """
    import asyncio
    
    logger.info(f"[METRICS] Starting periodic updates (interval: {interval}s)")
    
    while True:
        try:
            update_system_metrics()
            calculate_cache_hit_ratio()
        except Exception as e:
            logger.error(f"Error in periodic metric update: {e}")
        
        await asyncio.sleep(interval)

