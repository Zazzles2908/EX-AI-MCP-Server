"""
Health Tracker Module

Handles health checks, status monitoring, and health-related validation.
Extracted from monitoring_endpoint.py to improve maintainability.

Components:
- Health check endpoints
- Flag configuration validation
- Component health monitoring
"""

import asyncio
import logging
from aiohttp import web
from utils.timezone_helper import log_timestamp, utc_now_iso
from src.monitoring.flags import get_flag_manager

from src.daemon.error_handling import log_error, ErrorCode

logger = logging.getLogger(__name__)


async def monitoring_health_handler(request: web.Request) -> web.Response:
    """
    PHASE 1 FIX (2025-11-01): Health check endpoint for monitoring port.

    Returns:
        200 OK with basic health status
    """
    try:
        return web.json_response({
            'status': 'healthy',
            'timestamp_utc': utc_now_iso(),
            'port': 8080,
            'service': 'monitoring',
            'components': {
                'websocket': 'healthy',
                'dashboard': 'healthy',
                'metrics': 'healthy'
            }
        })
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error: {e}", exc_info=True)
        return web.json_response({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)


async def get_health_flags(request: web.Request) -> web.Response:
    """
    Get flag configuration health check.

    Validates flag configuration and returns health status.

    Args:
        request: aiohttp request object

    Returns:
        JSON response with health status
    """
    try:
        flag_manager = get_flag_manager()
        flags = flag_manager.get_all()

        # Validate flag combinations
        issues = []

        # Check: VALIDATION_STRICT requires ENABLE_VALIDATION
        if flags.get('MONITORING_VALIDATION_STRICT') and not flags.get('MONITORING_ENABLE_VALIDATION'):
            issues.append("VALIDATION_STRICT enabled but ENABLE_VALIDATION disabled")

        # Check: DUAL_MODE requires USE_ADAPTER
        if flags.get('MONITORING_DUAL_MODE') and not flags.get('MONITORING_USE_ADAPTER'):
            issues.append("DUAL_MODE enabled but USE_ADAPTER disabled")

        # Check: METRICS_PERSISTENCE requires METRICS_FLUSH_INTERVAL > 0
        if flags.get('MONITORING_METRICS_PERSISTENCE') and flags.get('MONITORING_METRICS_FLUSH_INTERVAL', 0) <= 0:
            issues.append("METRICS_PERSISTENCE enabled but METRICS_FLUSH_INTERVAL invalid")

        health_status = "healthy" if not issues else "degraded"

        return web.json_response({
            "status": "ok",
            "health": health_status,
            "issues": issues,
            "flags": flags,
            "timestamp": log_timestamp(),
        })
    except Exception as e:
        log_error(ErrorCode.INTERNAL_ERROR, f"Error checking flags health: {e}", exc_info=True)
        return web.json_response({
            "status": "error",
            "error": str(e),
            "timestamp": log_timestamp(),
        }, status=500)


async def status_handler(request: web.Request) -> web.Response:
    """
    Simple status endpoint.

    Args:
        request: aiohttp request object

    Returns:
        JSON status response
    """
    # Import here to avoid circular dependency
    from .websocket_handler import get_dashboard_clients
    
    return web.json_response({
        "status": "ok",
        "service": "monitoring",
        "clients_connected": len(get_dashboard_clients()),
        "timestamp": log_timestamp(),
    })


def check_component_health() -> dict:
    """
    Check health of all monitoring components.

    Returns:
        Dictionary with component health status
    """
    health_status = {
        "overall": "healthy",
        "components": {},
        "issues": []
    }

    try:
        # Check WebSocket health
        from .websocket_handler import get_dashboard_clients, get_websocket_health_tracker
        ws_clients = len(get_dashboard_clients())
        ws_health = get_websocket_health_tracker().get_metrics()
        
        health_status["components"]["websocket"] = {
            "status": "healthy" if ws_clients >= 0 else "unhealthy",
            "active_connections": ws_clients,
            "connection_details": ws_health
        }

        # Check session tracker health
        from .session_monitor import get_session_tracker
        session_tracker = get_session_tracker()
        session_metrics = session_tracker.get_metrics()
        
        health_status["components"]["session"] = {
            "status": "healthy",
            "active_sessions": session_metrics.get("active_sessions", 0)
        }

    except Exception as e:
        health_status["overall"] = "degraded"
        health_status["issues"].append(f"Component check failed: {e}")

    return health_status
