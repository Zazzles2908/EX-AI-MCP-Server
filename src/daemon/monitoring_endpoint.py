"""
Real-Time Monitoring WebSocket Endpoint - Orchestrator

Streams monitoring events to the dashboard for real-time visualization.
Provides connection status, performance metrics, and error tracking.

This is the main orchestrator that delegates to specialized modules:
- websocket_handler: WebSocket connections and health tracking
- metrics_broadcaster: Metrics collection and broadcasting  
- health_tracker: Health check and tracking
- http_endpoints: HTTP API endpoints
- session_monitor: Session lifecycle management

Created: 2025-10-18
Updated: 2025-11-06 - Refactored into modular architecture
"""

import asyncio
import logging
from pathlib import Path
from aiohttp import web

from .monitoring.websocket_handler import (
    websocket_handler as ws_websocket_handler,
    event_ingestion_handler,
    periodic_metrics_broadcast,
    get_dashboard_clients,
    add_dashboard_client,
    remove_dashboard_client,
)
from .monitoring.http_endpoints import (
    serve_dashboard,
    get_validation_metrics,
    get_adapter_metrics,
    get_flags_status,
    post_metrics_flush,
    get_auditor_observations,
    acknowledge_observation,
    get_cache_metrics,
    get_current_metrics,
    handle_timeout_estimate,
)
from .monitoring.health_tracker import (
    monitoring_health_handler,
    get_health_flags,
    status_handler as health_status_handler,
)
from .monitoring.session_monitor import get_session_tracker
from .monitoring.metrics_broadcaster import broadcast_monitoring_event

logger = logging.getLogger(__name__)


async def start_monitoring_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """
    Start monitoring server with both WebSocket and HTTP file serving.

    PHASE 2.4.6: Integrated graceful shutdown support

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"[MONITORING] Starting monitoring server on {host}:{port}")

    # PHASE 2.4.6: Initialize graceful shutdown handler
    try:
        from src.monitoring.persistence.graceful_shutdown import get_shutdown_handler
        shutdown_handler = get_shutdown_handler()
        logger.info("[MONITORING] Graceful shutdown handler initialized")
    except Exception as e:
        logger.warning(f"[MONITORING] Failed to initialize graceful shutdown: {e}")
        shutdown_handler = None

    # Create aiohttp application
    app = web.Application()

    # Add CORS middleware
    @web.middleware
    async def cors_middleware(request: web.Request, handler):
        response = await handler(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    app.middlewares.append(cors_middleware)

    # Add routes
    app.router.add_get('/ws', ws_websocket_handler)
    app.router.add_get('/monitoring_dashboard.html', serve_dashboard)
    app.router.add_get('/status', health_status_handler)

    # Phase 2.4.3: Dashboard Endpoints for Feature Flags and Metrics (2025-11-01)
    app.router.add_get('/metrics/validation', get_validation_metrics)
    app.router.add_get('/metrics/adapter', get_adapter_metrics)
    app.router.add_get('/flags/status', get_flags_status)
    app.router.add_post('/metrics/flush', post_metrics_flush)
    app.router.add_get('/health/flags', get_health_flags)

    # PHASE 1 FIX (2025-11-01): Add /health endpoint to monitoring port
    app.router.add_get('/health', monitoring_health_handler)

    # AI Auditor API routes (2025-10-24)
    app.router.add_get('/api/auditor/observations', get_auditor_observations)
    app.router.add_post('/api/auditor/observations/{observation_id}/acknowledge', acknowledge_observation)

    # Cache Metrics API routes (Week 2-3 Monitoring Phase - 2025-10-31)
    app.router.add_get('/api/cache-metrics', get_cache_metrics)

    # Adaptive Timeout API routes (Day 1 - 2025-11-03)
    app.router.add_post('/api/v1/timeout/estimate', handle_timeout_estimate)

    # Testing API routes (Phase 0.4 - 2025-10-24)
    app.router.add_get('/api/metrics/current', get_current_metrics)

    # Event ingestion endpoint for testing (2025-10-27)
    app.router.add_get('/events', event_ingestion_handler)
    logger.info("[MONITORING] Registered /events endpoint for test event ingestion")

    # Semaphore monitor (added 2025-10-21)
    static_dir = Path(__file__).parent.parent / "static"
    async def serve_semaphore_monitor(request):
        return web.FileResponse(static_dir / "semaphore_monitor.html")

    app.router.add_get('/semaphore_monitor.html', serve_semaphore_monitor)
    app.router.add_get('/', serve_semaphore_monitor)  # Default to semaphore monitor

    # Add static file handler for assets (if needed in future)
    if static_dir.exists():
        app.router.add_static('/static', static_dir, name='static')

    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"[MONITORING] Monitoring server running on ws://{host}:{port}")
    logger.info(f"[MONITORING] 🔍 Semaphore Monitor: http://{host}:{port}/semaphore_monitor.html")
    logger.info(f"[MONITORING] 📊 Full Dashboard: http://{host}:{port}/monitoring_dashboard.html")

    # PHASE 2.4 (2025-10-26): Start periodic metrics broadcast task
    broadcast_task = asyncio.create_task(periodic_metrics_broadcast())
    logger.info(f"[MONITORING] Started periodic metrics broadcast (every 5s)")

    # Keep running
    try:
        await asyncio.Future()
    finally:
        broadcast_task.cancel()

        # PHASE 2.4.6: Execute graceful shutdown
        if shutdown_handler:
            logger.info("[MONITORING] Executing graceful shutdown sequence...")
            shutdown_handler.execute_shutdown()
            logger.info("[MONITORING] Graceful shutdown completed")


# Hook for monitoring system to broadcast events
def setup_monitoring_broadcast() -> None:
    """
    Setup monitoring system to broadcast events to dashboard.
    Call this during server initialization.
    """
    from utils.monitoring import get_monitor
    
    monitor = get_monitor()

    # Override record_event to broadcast
    original_record_event = monitor.record_event

    def broadcast_wrapper(*args, **kwargs):
        # Call original
        original_record_event(*args, **kwargs)

        # Broadcast to dashboards
        event_data = {
            "type": "event",
            "connection_type": args[0] if args else kwargs.get("connection_type"),
            "direction": args[1] if len(args) > 1 else kwargs.get("direction"),
            "script_name": args[2] if len(args) > 2 else kwargs.get("script_name"),
            "function_name": args[3] if len(args) > 3 else kwargs.get("function_name"),
            "data_size_bytes": args[4] if len(args) > 4 else kwargs.get("data_size_bytes"),
            "response_time_ms": kwargs.get("response_time_ms"),
            "error": kwargs.get("error"),
            "metadata": kwargs.get("metadata", {}),
        }

        # Schedule broadcast (non-blocking) - THREAD-SAFE for sync contexts
        _dashboard_clients = get_dashboard_clients()
        if _dashboard_clients:
            try:
                # Try to get running loop (async context)
                loop = asyncio.get_running_loop()
                loop.create_task(broadcast_monitoring_event(event_data, _dashboard_clients, get_session_tracker()))
            except RuntimeError:
                # No running loop (sync context) - use thread pool
                from concurrent.futures import ThreadPoolExecutor
                import threading

                # Use a shared thread pool executor
                if not hasattr(broadcast_wrapper, '_executor
