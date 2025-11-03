"""
File upload metrics for EX-AI-MCP-Server
Provides Prometheus-compatible metrics for file operations
"""
import logging
from prometheus_client import Counter, Histogram, Gauge
from typing import Optional

logger = logging.getLogger(__name__)

# File upload metrics
FILE_UPLOAD_ATTEMPTS = Counter(
    'mcp_file_upload_attempts_total',
    'Total file upload attempts',
    ['provider', 'user_id']
)

FILE_UPLOAD_BYTES = Counter(
    'mcp_file_upload_bytes_total',
    'Total bytes uploaded',
    ['provider', 'status']
)

FILE_UPLOAD_DURATION = Histogram(
    'mcp_file_upload_duration_seconds',
    'File upload duration in seconds',
    ['provider'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float('inf')]
)

ACTIVE_UPLOADS = Gauge(
    'mcp_file_active_uploads',
    'Number of active file uploads'
)

DEDUPLICATION_HITS = Counter(
    'mcp_file_deduplication_hits_total',
    'Total deduplication hits (files already uploaded)'
)

CIRCUIT_BREAKER_TRIPS = Counter(
    'mcp_file_circuit_breaker_trips_total',
    'Total circuit breaker trips',
    ['provider']
)

FILE_DELETIONS = Counter(
    'mcp_file_deletions_total',
    'Total file deletions',
    ['provider', 'reason']  # reason: expired, manual, orphaned
)

# Helper functions
def record_upload_attempt(provider: str, user_id: str) -> None:
    """Record a file upload attempt"""
    try:
        FILE_UPLOAD_ATTEMPTS.labels(provider=provider, user_id=user_id).inc()
        ACTIVE_UPLOADS.inc()
        logger.debug(f"Recorded upload attempt: provider={provider}, user_id={user_id}")
    except Exception as e:
        logger.error(f"Error recording upload attempt: {e}")

def record_upload_completion(provider: str, status: str, bytes_count: int, duration: float) -> None:
    """Record a completed file upload"""
    try:
        FILE_UPLOAD_BYTES.labels(provider=provider, status=status).inc(bytes_count)
        FILE_UPLOAD_DURATION.labels(provider=provider).observe(duration)
        ACTIVE_UPLOADS.dec()
        logger.debug(f"Recorded upload completion: provider={provider}, status={status}, bytes={bytes_count}, duration={duration:.2f}s")
    except Exception as e:
        logger.error(f"Error recording upload completion: {e}")

def record_deduplication_hit() -> None:
    """Record a deduplication hit (file already exists)"""
    try:
        DEDUPLICATION_HITS.inc()
        logger.debug("Recorded deduplication hit")
    except Exception as e:
        logger.error(f"Error recording deduplication hit: {e}")

def record_circuit_breaker_trip(provider: str) -> None:
    """Record a circuit breaker trip"""
    try:
        CIRCUIT_BREAKER_TRIPS.labels(provider=provider).inc()
        logger.warning(f"Recorded circuit breaker trip: provider={provider}")
    except Exception as e:
        logger.error(f"Error recording circuit breaker trip: {e}")

def record_file_deletion(provider: str, reason: str) -> None:
    """Record a file deletion"""
    try:
        FILE_DELETIONS.labels(provider=provider, reason=reason).inc()
        logger.debug(f"Recorded file deletion: provider={provider}, reason={reason}")
    except Exception as e:
        logger.error(f"Error recording file deletion: {e}")

def init_file_metrics() -> None:
    """
    Initialize file metrics (called during server startup)
    This ensures all metrics are registered with Prometheus
    """
    logger.info("File metrics initialized")
    logger.info(f"Registered metrics: FILE_UPLOAD_ATTEMPTS, FILE_UPLOAD_BYTES, "
                f"FILE_UPLOAD_DURATION, ACTIVE_UPLOADS, DEDUPLICATION_HITS, "
                f"CIRCUIT_BREAKER_TRIPS, FILE_DELETIONS")

