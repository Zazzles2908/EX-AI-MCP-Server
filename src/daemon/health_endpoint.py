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
    """Check memory usage"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Get system memory
        system_memory = psutil.virtual_memory()
        memory_percent = system_memory.percent
        
        # Thresholds
        WARNING_THRESHOLD = 80.0  # 80% system memory
        CRITICAL_THRESHOLD = 90.0  # 90% system memory
        
        if memory_percent >= CRITICAL_THRESHOLD:
            status = "unhealthy"
            message = f"Critical memory usage: {memory_percent:.1f}%"
        elif memory_percent >= WARNING_THRESHOLD:
            status = "degraded"
            message = f"High memory usage: {memory_percent:.1f}%"
        else:
            status = "healthy"
            message = f"Memory usage normal: {memory_percent:.1f}%"
        
        return {
            "status": status,
            "message": message,
            "process_memory_mb": round(memory_mb, 2),
            "system_memory_percent": round(memory_percent, 2),
            "system_memory_available_mb": round(system_memory.available / 1024 / 1024, 2)
        }
        
    except Exception as e:
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


async def start_health_server(host: str = "0.0.0.0", port: int = 8081) -> None:
    """
    Start health check HTTP server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    app = web.Application()
    app.router.add_get('/health', health_check_handler)
    app.router.add_get('/healthz', health_check_handler)  # Kubernetes convention
    app.router.add_get('/health/live', health_check_handler)  # Liveness probe
    app.router.add_get('/health/ready', health_check_handler)  # Readiness probe
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    site = web.TCPSite(runner, host, port)
    await site.start()
    
    logger.info(f"[HEALTH] Health check server running on http://{host}:{port}/health")
    
    # Keep running
    await asyncio.Future()

