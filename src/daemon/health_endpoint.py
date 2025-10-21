"""
Health Check HTTP Endpoint

Provides standardized health check endpoint for external monitoring systems
(Prometheus, Datadog, Kubernetes, etc.)

Created: 2025-10-18
EXAI Consultation: 30441b5d-87d0-4f31-864e-d40e8dcbcad2
Critical Gap #1: Health Check Endpoints (4 hours)
"""

import asyncio
import json
import logging
import os
import psutil
from datetime import datetime
from aiohttp import web
from typing import Dict, Any

from utils.timezone_helper import utc_now_iso, melbourne_now_iso

logger = logging.getLogger(__name__)


async def health_check_handler(request: web.Request) -> web.Response:
    """
    Health check endpoint handler.
    
    Returns:
        200 OK: All systems healthy
        503 Service Unavailable: One or more systems degraded
    """
    try:
        # Import here to avoid circular dependencies
        from utils.infrastructure.storage_backend import get_storage_backend
        from src.storage.supabase_client import get_storage_manager
        
        storage_backend = get_storage_backend()
        supabase_manager = get_storage_manager()
        
        # Build health status
        status = {
            "status": "healthy",
            "timestamp_utc": utc_now_iso(),
            "timestamp_melbourne": melbourne_now_iso(),
            "version": "1.0.0",
            "components": {}
        }
        
        # Check storage backend
        storage_status = await check_storage_health(storage_backend)
        status["components"]["storage"] = storage_status
        if storage_status["status"] != "healthy":
            status["status"] = "degraded"
        
        # Check Supabase
        supabase_status = await check_supabase_health(supabase_manager)
        status["components"]["supabase"] = supabase_status
        if supabase_status["status"] != "healthy" and supabase_status["enabled"]:
            status["status"] = "degraded"
        
        # Check memory
        memory_status = check_memory_health()
        status["components"]["memory"] = memory_status
        if memory_status["status"] != "healthy":
            status["status"] = "degraded"
        
        # Check disk
        disk_status = check_disk_health()
        status["components"]["disk"] = disk_status
        if disk_status["status"] != "healthy":
            status["status"] = "degraded"

        # Check semaphores (added 2025-10-21 per EXAI recommendations)
        semaphore_status = await check_semaphore_health_status()
        status["components"]["semaphores"] = semaphore_status
        if semaphore_status["status"] != "healthy":
            status["status"] = "degraded"

        # Return appropriate status code
        http_status = 200 if status["status"] == "healthy" else 503

        return web.json_response(status, status=http_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return web.json_response({
            "status": "unhealthy",
            "error": str(e),
            "timestamp_utc": utc_now_iso()
        }, status=503)


async def check_storage_health(storage_backend) -> Dict[str, Any]:
    """Check storage backend health"""
    try:
        # Determine storage type
        from utils.infrastructure.storage_backend import InMemoryStorage, RedisStorage
        
        if isinstance(storage_backend, InMemoryStorage):
            storage_type = "memory"
        elif isinstance(storage_backend, RedisStorage):
            storage_type = "redis"
        else:
            storage_type = "unknown"
        
        # Perform basic connectivity check
        test_key = "__health_check_test__"
        storage_backend.set_with_ttl(test_key, 5, "test_value")
        result = storage_backend.get(test_key)
        
        if result == "test_value":
            return {
                "status": "healthy",
                "type": storage_type,
                "message": "Storage backend responding normally"
            }
        else:
            return {
                "status": "degraded",
                "type": storage_type,
                "message": "Storage backend not returning expected values"
            }
            
    except Exception as e:
        return {
            "status": "unhealthy",
            "type": "unknown",
            "error": str(e)
        }


async def check_supabase_health(supabase_manager) -> Dict[str, Any]:
    """Check Supabase health"""
    if not supabase_manager.enabled:
        return {
            "status": "healthy",
            "enabled": False,
            "message": "Supabase not configured (optional)"
        }
    
    try:
        # Perform basic connectivity check
        client = supabase_manager.get_client()
        
        # Try to query a simple table (schema_version or any table)
        # This is a lightweight check
        result = client.table('conversations').select('id').limit(1).execute()
        
        return {
            "status": "healthy",
            "enabled": True,
            "message": "Supabase responding normally"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "enabled": True,
            "error": str(e)
        }


def check_memory_health() -> Dict[str, Any]:
    """
    Check memory usage using comprehensive memory monitor.
    Week 3 Fix #13 (2025-10-21): Enhanced with memory monitoring framework
    """
    try:
        from src.daemon.monitoring import get_memory_monitor, AlertLevel

        # Get memory monitor and collect current metrics
        monitor = get_memory_monitor()
        metrics = monitor.collect_metrics()

        # Check for alerts
        alert = monitor.check_alerts(metrics)

        # Map alert level to health status
        if alert:
            if alert.level == AlertLevel.CRITICAL or alert.level == AlertLevel.LEAK_DETECTED:
                status = "unhealthy"
            elif alert.level == AlertLevel.WARNING:
                status = "degraded"
            else:
                status = "healthy"
            message = alert.message
        else:
            status = "healthy"
            message = f"Memory usage normal: {metrics.rss_percent:.1f}%"

        return {
            "status": status,
            "message": message,
            "process_memory_mb": round(metrics.rss / (1024 * 1024), 2),
            "system_memory_percent": round(metrics.rss_percent, 2),
            "growth_rate_mb_per_hour": round(metrics.growth_rate_mb_per_hour, 2),
            "alert_level": alert.level.value if alert else "normal",
        }

    except Exception as e:
        logger.error(f"Memory health check failed: {e}")
        return {
            "status": "unknown",
            "error": str(e)
        }


def check_disk_health() -> Dict[str, Any]:
    """Check disk usage"""
    try:
        # Check disk usage for current directory
        disk_usage = psutil.disk_usage('.')
        disk_percent = disk_usage.percent
        
        # Thresholds
        WARNING_THRESHOLD = 85.0  # 85% disk usage
        CRITICAL_THRESHOLD = 95.0  # 95% disk usage
        
        if disk_percent >= CRITICAL_THRESHOLD:
            status = "unhealthy"
            message = f"Critical disk usage: {disk_percent:.1f}%"
        elif disk_percent >= WARNING_THRESHOLD:
            status = "degraded"
            message = f"High disk usage: {disk_percent:.1f}%"
        else:
            status = "healthy"
            message = f"Disk usage normal: {disk_percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "disk_percent": round(disk_percent, 2),
            "disk_free_gb": round(disk_usage.free / 1024 / 1024 / 1024, 2),
            "disk_total_gb": round(disk_usage.total / 1024 / 1024 / 1024, 2)
        }
        
    except Exception as e:
        return {
            "status": "unknown",
            "error": str(e)
        }


async def check_semaphore_health_status() -> dict:
    """
    Check semaphore health status.
    Added 2025-10-21 per EXAI monitoring recommendations.

    Returns:
        Dictionary with semaphore health status
    """
    try:
        # Import here to avoid circular dependencies
        from src.daemon.ws_server import (
            _global_sem,
            _provider_sems,
            GLOBAL_MAX_INFLIGHT,
            KIMI_MAX_INFLIGHT,
            GLM_MAX_INFLIGHT
        )

        status = {
            "status": "healthy",
            "global": {
                "current": _global_sem._value,
                "expected": GLOBAL_MAX_INFLIGHT,
                "utilization": (GLOBAL_MAX_INFLIGHT - _global_sem._value) / GLOBAL_MAX_INFLIGHT,
                "status": "healthy"
            },
            "providers": {}
        }

        # Check global semaphore
        if _global_sem._value <= 0:
            status["global"]["status"] = "exhausted"
            status["status"] = "critical"
        elif _global_sem._value != GLOBAL_MAX_INFLIGHT:
            status["global"]["status"] = "leak_detected"
            status["status"] = "degraded"
        elif _global_sem._value <= GLOBAL_MAX_INFLIGHT * 0.1:
            status["global"]["status"] = "high_utilization"
            status["status"] = "warning"

        # Check provider semaphores
        for provider, sem in _provider_sems.items():
            expected = {"KIMI": KIMI_MAX_INFLIGHT, "GLM": GLM_MAX_INFLIGHT}.get(provider, 0)
            current = sem._value
            utilization = (expected - current) / expected if expected > 0 else 0

            provider_status = {
                "current": current,
                "expected": expected,
                "utilization": utilization,
                "status": "healthy"
            }

            if current <= 0:
                provider_status["status"] = "exhausted"
                status["status"] = "critical"
            elif current != expected:
                provider_status["status"] = "leak_detected"
                if status["status"] == "healthy":
                    status["status"] = "degraded"
            elif current <= expected * 0.1:
                provider_status["status"] = "high_utilization"
                if status["status"] == "healthy":
                    status["status"] = "warning"

            status["providers"][provider.lower()] = provider_status

        return status

    except Exception as e:
        logger.error(f"Error checking semaphore health: {e}", exc_info=True)
        return {
            "status": "unknown",
            "error": str(e)
        }


async def semaphore_health_handler(request: web.Request) -> web.Response:
    """
    Dedicated semaphore health endpoint.
    Added 2025-10-21 per EXAI monitoring recommendations.

    Returns detailed semaphore status including:
    - Current and expected values
    - Utilization percentages
    - Leak detection
    - Exhaustion alerts
    """
    try:
        status = await check_semaphore_health_status()

        # Return appropriate status code
        http_status = 200
        if status["status"] == "critical":
            http_status = 503
        elif status["status"] in ["degraded", "warning"]:
            http_status = 200  # Still operational, just warning

        return web.json_response(status, status=http_status)

    except Exception as e:
        logger.error(f"Error in semaphore health handler: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e)
        }, status=500)


async def memory_health_handler(request: web.Request) -> web.Response:
    """
    Detailed memory health endpoint.
    Week 3 Fix #13 (2025-10-21): Comprehensive memory monitoring

    Returns detailed memory metrics, history, and alerts.
    """
    try:
        from src.daemon.monitoring import get_memory_monitor

        monitor = get_memory_monitor()
        current_metrics = monitor.collect_metrics()
        current_alert = monitor.check_alerts(current_metrics)

        # Build response
        response = {
            "status": "healthy",
            "timestamp_utc": utc_now_iso(),
            "current_metrics": current_metrics.to_dict(),
            "alert": {
                "level": current_alert.level.value if current_alert else "normal",
                "message": current_alert.message if current_alert else "No alerts",
                "threshold_exceeded": current_alert.threshold_exceeded if current_alert else None,
            },
            "thresholds": {
                "warning_percent": monitor.warning_threshold,
                "critical_percent": monitor.critical_threshold,
                "leak_mb_per_hour": monitor.leak_threshold,
            },
            "baseline": monitor.baseline_metrics.to_dict() if monitor.baseline_metrics else None,
            "history_size": len(monitor.metrics_history),
        }

        # Set status based on alert level
        if current_alert:
            from src.daemon.monitoring import AlertLevel
            if current_alert.level in (AlertLevel.CRITICAL, AlertLevel.LEAK_DETECTED):
                response["status"] = "unhealthy"
            elif current_alert.level == AlertLevel.WARNING:
                response["status"] = "degraded"

        http_status = 200 if response["status"] == "healthy" else 503
        return web.json_response(response, status=http_status)

    except Exception as e:
        logger.error(f"Memory health endpoint failed: {e}")
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp_utc": utc_now_iso()
        }, status=500)


async def start_health_server(host: str = "0.0.0.0", port: int = 8081) -> None:
    """
    Start health check HTTP server.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    app = web.Application()

    # Add CORS middleware for monitoring UI (2025-10-21)
    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    app.middlewares.append(cors_middleware)

    app.router.add_get('/health', health_check_handler)
    app.router.add_get('/healthz', health_check_handler)  # Kubernetes convention
    app.router.add_get('/health/live', health_check_handler)  # Liveness probe
    app.router.add_get('/health/ready', health_check_handler)  # Readiness probe
    app.router.add_get('/health/semaphores', semaphore_health_handler)  # Semaphore-specific health (added 2025-10-21)
    app.router.add_get('/health/memory', memory_health_handler)  # Memory-specific health (Week 3 Fix #13, 2025-10-21)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"[HEALTH] Health check server running on http://{host}:{port}/health")

    # Keep running
    await asyncio.Future()

