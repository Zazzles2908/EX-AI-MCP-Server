"""
Real-Time Monitoring WebSocket Endpoint

Streams monitoring events to the dashboard for real-time visualization.
Provides connection status, performance metrics, and error tracking.

Created: 2025-10-18
EXAI Consultation: 89cc866c-7d88-4339-93de-d8ae08921310
Architecture: aiohttp with WebSocket + HTTP file serving (EXAI recommended)
Updated: 2025-10-18 - Added HTTP file serving for dashboard
"""

import asyncio
import json
import logging
from typing import Set
from pathlib import Path
from aiohttp import web

from utils.monitoring import get_monitor
from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)

# Connected dashboard clients
_dashboard_clients: Set[web.WebSocketResponse] = set()


async def broadcast_monitoring_event(event_data: dict) -> None:
    """
    Broadcast monitoring event to all connected dashboard clients.

    Args:
        event_data: Event data to broadcast
    """
    if not _dashboard_clients:
        return

    # Add timestamp
    event_data["broadcast_time"] = log_timestamp()

    # Broadcast to all clients
    disconnected = set()
    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(event_data))
        except Exception as e:
            logger.debug(f"Failed to send to dashboard client: {e}")
            disconnected.add(client)

    # Remove disconnected clients
    _dashboard_clients.difference_update(disconnected)


async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """
    Handle dashboard WebSocket connection (aiohttp version).

    Args:
        request: aiohttp request object

    Returns:
        WebSocket response
    """
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    logger.info(f"[MONITORING] Dashboard connected from {request.remote}")
    _dashboard_clients.add(ws)

    try:
        # Send initial stats
        monitor = get_monitor()
        initial_stats = {
            "type": "initial_stats",
            "stats": {
                "websocket": monitor.get_stats("websocket"),
                "redis": monitor.get_stats("redis"),
                "supabase": monitor.get_stats("supabase"),
                "kimi": monitor.get_stats("kimi"),
                "glm": monitor.get_stats("glm"),
            },
            "recent_events": [
                {
                    "timestamp": e.timestamp,
                    "connection_type": e.connection_type,
                    "direction": e.direction,
                    "script_name": e.script_name,
                    "function_name": e.function_name,
                    "data_size_bytes": e.data_size_bytes,
                    "response_time_ms": e.response_time_ms,
                    "error": e.error,
                }
                for e in monitor.get_recent_events(limit=50)
            ],
            "timestamp": log_timestamp(),
        }
        await ws.send_str(json.dumps(initial_stats))

        # Keep connection alive and handle client messages
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    data = json.loads(msg.data)
                    command = data.get("command")

                    if command == "get_stats":
                        # Send current stats
                        connection_type = data.get("connection_type")
                        stats = monitor.get_stats(connection_type)
                        await ws.send_str(json.dumps({
                            "type": "stats",
                            "connection_type": connection_type,
                            "stats": stats,
                            "timestamp": log_timestamp(),
                        }))

                    elif command == "get_recent_events":
                        # Send recent events
                        connection_type = data.get("connection_type")
                        limit = data.get("limit", 100)
                        events = monitor.get_recent_events(connection_type, limit)
                        await ws.send_str(json.dumps({
                            "type": "recent_events",
                            "connection_type": connection_type,
                            "events": [
                                {
                                    "timestamp": e.timestamp,
                                    "connection_type": e.connection_type,
                                    "direction": e.direction,
                                    "script_name": e.script_name,
                                    "function_name": e.function_name,
                                    "data_size_bytes": e.data_size_bytes,
                                    "response_time_ms": e.response_time_ms,
                                    "error": e.error,
                                }
                                for e in events
                            ],
                            "timestamp": log_timestamp(),
                        }))

                    elif command == "export":
                        # Export monitoring data
                        filepath = data.get("filepath", "monitoring_export.json")
                        monitor.export_json(filepath)
                        await ws.send_str(json.dumps({
                            "type": "export_complete",
                            "filepath": filepath,
                            "timestamp": log_timestamp(),
                        }))

                except json.JSONDecodeError:
                    logger.warning(f"[MONITORING] Invalid JSON from dashboard: {msg.data}")
                except Exception as e:
                    logger.error(f"[MONITORING] Error handling dashboard message: {e}")

            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"[MONITORING] WebSocket error: {ws.exception()}")

    finally:
        _dashboard_clients.discard(ws)
        logger.info(f"[MONITORING] Dashboard disconnected")

    return ws


async def serve_dashboard(request: web.Request) -> web.Response:
    """
    Serve the monitoring dashboard HTML file.

    Args:
        request: aiohttp request object

    Returns:
        HTML response
    """
    dashboard_path = Path(__file__).parent.parent.parent / "static" / "monitoring_dashboard.html"

    if not dashboard_path.exists():
        logger.error(f"[MONITORING] Dashboard not found at {dashboard_path}")
        return web.Response(text="Dashboard not found", status=404)

    try:
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return web.Response(body=content, content_type='text/html')
    except Exception as e:
        logger.error(f"[MONITORING] Error serving dashboard: {e}")
        return web.Response(text=f"Error loading dashboard: {e}", status=500)


async def status_handler(request: web.Request) -> web.Response:
    """
    Simple status endpoint.

    Args:
        request: aiohttp request object

    Returns:
        JSON status response
    """
    return web.json_response({
        "status": "ok",
        "service": "monitoring",
        "clients_connected": len(_dashboard_clients),
        "timestamp": log_timestamp(),
    })


async def start_monitoring_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """
    Start monitoring server with both WebSocket and HTTP file serving.

    Args:
        host: Host to bind to
        port: Port to bind to
    """
    logger.info(f"[MONITORING] Starting monitoring server on {host}:{port}")

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
    app.router.add_get('/ws', websocket_handler)
    app.router.add_get('/monitoring_dashboard.html', serve_dashboard)
    app.router.add_get('/status', status_handler)
    app.router.add_get('/', serve_dashboard)  # Default route

    # Add static file handler for assets (if needed in future)
    static_dir = Path(__file__).parent.parent.parent / "static"
    if static_dir.exists():
        app.router.add_static('/static', static_dir, name='static')

    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()

    logger.info(f"[MONITORING] Monitoring server running on ws://{host}:{port}")
    logger.info(f"[MONITORING] Dashboard available at http://{host}:{port}/monitoring_dashboard.html")

    # Keep running
    await asyncio.Future()


# Hook for monitoring system to broadcast events
def setup_monitoring_broadcast() -> None:
    """
    Setup monitoring system to broadcast events to dashboard.
    Call this during server initialization.
    """
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
        
        # Schedule broadcast (non-blocking)
        if _dashboard_clients:
            asyncio.create_task(broadcast_monitoring_event(event_data))
    
    monitor.record_event = broadcast_wrapper
    logger.info("[MONITORING] Broadcast hook installed")

