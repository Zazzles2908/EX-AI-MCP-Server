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
from typing import Set, Dict, Optional
from pathlib import Path
from aiohttp import web
from collections import defaultdict

from utils.monitoring import get_monitor
from utils.timezone_helper import log_timestamp
from src.daemon.middleware.semaphores import get_port_semaphore_manager
import time

logger = logging.getLogger(__name__)

# Connected dashboard clients
_dashboard_clients: Set[web.WebSocketResponse] = set()

# PHASE 2.4 ENHANCEMENT (2025-10-26): WebSocket health tracking
class WebSocketHealthTracker:
    """
    Track WebSocket connection health metrics for monitoring dashboard.

    Tracks:
    - Ping/pong latency
    - Connection uptime
    - Reconnection events
    - Timeout warnings
    """

    def __init__(self):
        self.connections: Dict[int, Dict] = {}  # port -> connection metrics

    def register_connection(self, port: int) -> None:
        """Register a new WebSocket connection"""
        self.connections[port] = {
            'connected_at': time.time(),
            'last_ping': None,
            'ping_latency_ms': 0,
            'ping_latencies': [],  # Last 10 pings
            'reconnection_count': 0,
            'timeout_warnings': 0
        }

    def record_ping(self, port: int, latency_ms: float) -> None:
        """Record a ping/pong latency measurement"""
        if port not in self.connections:
            self.register_connection(port)

        conn = self.connections[port]
        conn['last_ping'] = time.time()
        conn['ping_latency_ms'] = latency_ms

        # Keep last 10 latencies for statistics
        conn['ping_latencies'].append(latency_ms)
        if len(conn['ping_latencies']) > 10:
            conn['ping_latencies'].pop(0)

    def record_reconnection(self, port: int) -> None:
        """Record a reconnection event"""
        if port not in self.connections:
            self.register_connection(port)
        self.connections[port]['reconnection_count'] += 1

    def record_timeout_warning(self, port: int) -> None:
        """Record a timeout warning"""
        if port not in self.connections:
            self.register_connection(port)
        self.connections[port]['timeout_warnings'] += 1

    def get_metrics(self) -> dict:
        """
        Get WebSocket health metrics for monitoring dashboard.

        Returns:
            Dictionary with WebSocket health metrics
        """
        metrics = {}

        for port, conn in self.connections.items():
            uptime_seconds = time.time() - conn['connected_at']
            latencies = conn['ping_latencies']

            # Calculate statistics
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) >= 2 else avg_latency

            metrics[port] = {
                'uptime_seconds': int(uptime_seconds),
                'uptime_formatted': self._format_uptime(uptime_seconds),
                'current_ping_ms': conn['ping_latency_ms'],
                'avg_ping_ms': round(avg_latency, 2),
                'p95_ping_ms': round(p95_latency, 2),
                'reconnection_count': conn['reconnection_count'],
                'timeout_warnings': conn['timeout_warnings'],
                'status': 'connected' if conn['last_ping'] and (time.time() - conn['last_ping']) < 60 else 'stale'
            }

        return metrics

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime in human-readable format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


# Global instances
_ws_health_tracker = WebSocketHealthTracker()


# PHASE 3.5 (2025-10-23): Session Tracking for Conversation Metrics
class SessionTracker:
    """
    Track session and conversation metrics for the monitoring dashboard.

    Tracks:
    - Conversation chains (conversation_id -> message_count)
    - Model usage (session_id -> current_model)
    - Token usage (conversation_id -> tokens_used/max_tokens)
    - Active sessions and their metadata
    """

    def __init__(self):
        self.conversation_chains: Dict[str, int] = defaultdict(int)  # conversation_id -> message_count
        self.model_usage: Dict[str, str] = {}  # session_id -> current_model
        self.token_usage: Dict[str, Dict[str, int]] = {}  # conversation_id -> {used, max}
        self.active_sessions: Dict[str, Dict] = {}  # session_id -> metadata
        self.last_activity: Dict[str, str] = {}  # session_id -> timestamp

    def update_from_event(self, event_data: dict) -> None:
        """
        Update session metrics from a monitoring event.

        Args:
            event_data: Monitoring event data
        """
        # Extract metadata
        metadata = event_data.get("metadata", {})
        connection_type = event_data.get("connection_type", "")

        # Track conversation chains (from continuation_id or conversation_id)
        conversation_id = metadata.get("continuation_id") or metadata.get("conversation_id")
        if conversation_id:
            self.conversation_chains[conversation_id] += 1

        # Track model usage (from Kimi/GLM events)
        if connection_type in ["kimi", "glm"]:
            model = metadata.get("model")
            if model:
                # Use conversation_id as session_id for now
                session_id = conversation_id or "default"
                self.model_usage[session_id] = model

                # Update last activity
                self.last_activity[session_id] = event_data.get("timestamp", log_timestamp())

        # Track token usage (from API responses)
        tokens = metadata.get("tokens")
        if tokens and conversation_id:
            if conversation_id not in self.token_usage:
                # Initialize with default max tokens (will be updated based on model)
                self.token_usage[conversation_id] = {"used": 0, "max": 128000}

            # Update tokens used
            self.token_usage[conversation_id]["used"] = tokens

            # Update max tokens based on model
            model = metadata.get("model", "")
            if "128k" in model.lower():
                self.token_usage[conversation_id]["max"] = 128000
            elif "32k" in model.lower():
                self.token_usage[conversation_id]["max"] = 32000
            elif "8k" in model.lower():
                self.token_usage[conversation_id]["max"] = 8000

    def get_metrics(self) -> dict:
        """
        Get current session metrics for dashboard.

        Returns:
            Dictionary with session metrics
        """
        # Get most recent conversation
        recent_conversation_id = None
        recent_timestamp = None
        for session_id, timestamp in self.last_activity.items():
            if recent_timestamp is None or timestamp > recent_timestamp:
                recent_timestamp = timestamp
                recent_conversation_id = session_id

        # Get metrics for most recent conversation
        conversation_length = 0
        current_model = "--"
        context_tokens_used = 0
        context_tokens_max = 128000

        if recent_conversation_id:
            conversation_length = self.conversation_chains.get(recent_conversation_id, 0)
            current_model = self.model_usage.get(recent_conversation_id, "--")

            if recent_conversation_id in self.token_usage:
                context_tokens_used = self.token_usage[recent_conversation_id]["used"]
                context_tokens_max = self.token_usage[recent_conversation_id]["max"]

        return {
            "active_sessions": len(_dashboard_clients),
            "total_sessions": len(self.active_sessions),
            "conversation_length": conversation_length,
            "current_model": current_model,
            "context_tokens_used": context_tokens_used,
            "context_tokens_max": context_tokens_max,
        }

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Clean up old session data to prevent memory leaks.

        Args:
            max_age_hours: Maximum age of sessions to keep (default 24 hours)
        """
        # TODO: Implement cleanup based on last_activity timestamps
        pass


# Global session tracker instance
_session_tracker = SessionTracker()

# Track last broadcast metrics for change detection
_last_broadcast_metrics: Optional[dict] = None


async def _broadcast_session_metrics(metrics: dict) -> None:
    """
    Broadcast session metrics to all connected dashboard clients.

    Args:
        metrics: Session metrics dictionary from SessionTracker.get_metrics()
    """
    if not _dashboard_clients:
        return

    session_metrics_update = {
        "type": "session_metrics",
        "data": metrics,
        "timestamp": log_timestamp(),
    }

    # Log metrics broadcast for debugging
    logger.debug(f"Broadcasting session metrics: active_sessions={metrics.get('active_sessions')}, "
                f"conversation_length={metrics.get('conversation_length')}, "
                f"current_model={metrics.get('current_model')}")

    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(session_metrics_update))
        except Exception as e:
            logger.debug(f"Failed to send session metrics to client: {e}")


async def _broadcast_semaphore_metrics() -> None:
    """
    Broadcast semaphore health metrics to all connected dashboard clients.

    PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended semaphore monitoring
    """
    if not _dashboard_clients:
        return

    semaphore_manager = get_port_semaphore_manager()
    metrics = semaphore_manager.get_metrics()

    event = {
        "type": "semaphore_metrics",
        "data": metrics,
        "timestamp": log_timestamp()
    }

    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(event))
        except Exception as e:
            logger.debug(f"Failed to send semaphore metrics to dashboard client: {e}")


async def _broadcast_websocket_health() -> None:
    """
    Broadcast WebSocket health metrics to all connected dashboard clients.

    PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended WebSocket health monitoring
    """
    if not _dashboard_clients:
        return

    metrics = _ws_health_tracker.get_metrics()

    event = {
        "type": "websocket_health",
        "data": metrics,
        "timestamp": log_timestamp()
    }

    for client in _dashboard_clients:
        try:
            await client.send_str(json.dumps(event))
        except Exception as e:
            logger.debug(f"Failed to send WebSocket health to dashboard client: {e}")


def _should_broadcast_metrics_change(current: dict, last: Optional[dict]) -> bool:
    """
    Determine if session metrics have changed enough to warrant broadcasting.

    Args:
        current: Current session metrics
        last: Last broadcast session metrics (None if first broadcast)

    Returns:
        True if metrics should be broadcast
    """
    if last is None:
        return True  # Always broadcast first time

    # Check for meaningful changes
    if current.get("conversation_length") != last.get("conversation_length"):
        return True
    if current.get("current_model") != last.get("current_model"):
        return True
    if current.get("active_sessions") != last.get("active_sessions"):
        return True

    # Check for significant token usage change (>10%)
    current_tokens = current.get("context_tokens_used", 0)
    last_tokens = last.get("context_tokens_used", 0)
    if last_tokens > 0:
        change_pct = abs(current_tokens - last_tokens) / last_tokens
        if change_pct > 0.1:  # 10% change
            return True

    return False


async def broadcast_monitoring_event(event_data: dict) -> None:
    """
    Broadcast monitoring event to all connected dashboard clients.

    Args:
        event_data: Event data to broadcast
    """
    global _last_broadcast_metrics

    # CRITICAL FIX (2025-10-23): Change to DEBUG level to reduce log spam
    # BUG: These INFO logs were creating excessive noise in production logs
    logger.debug(f"[BROADCAST_DEBUG] Function called with event_data keys: {list(event_data.keys())}")
    logger.debug(f"[BROADCAST_DEBUG] Dashboard clients connected: {len(_dashboard_clients)}")

    if not _dashboard_clients:
        logger.debug(f"[BROADCAST_DEBUG] No dashboard clients, skipping broadcast")
        return

    # PHASE 3.5 (2025-10-23): Update session tracker from event
    _session_tracker.update_from_event(event_data)

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

    # PHASE 4 (2025-10-23): Hybrid session metrics broadcasting (EXAI consultation: 6f02b31b-865d-4077-898f-dea9445b3c4a)
    # Development mode: send immediately when continuation_id detected
    # Production mode: send only on meaningful changes
    if len(_dashboard_clients) > 0:
        import os
        dev_mode = os.getenv('EXAI_DEV_MODE', 'true').lower() == 'true'  # Default to dev mode

        current_metrics = _session_tracker.get_metrics()

        # Check if this event has continuation_id
        metadata = event_data.get("metadata", {})
        has_continuation_id = bool(metadata.get("continuation_id") or metadata.get("conversation_id"))

        should_broadcast = False
        if dev_mode and has_continuation_id:
            # Development: immediate updates when continuation_id present
            should_broadcast = True
            logger.debug(f"[DEV MODE] Broadcasting session metrics immediately (continuation_id detected)")
        elif not dev_mode and _should_broadcast_metrics_change(current_metrics, _last_broadcast_metrics):
            # Production: only on meaningful changes
            should_broadcast = True
            logger.debug(f"[PROD MODE] Broadcasting session metrics (change detected)")

        if should_broadcast:
            await _broadcast_session_metrics(current_metrics)
            _last_broadcast_metrics = current_metrics.copy()


def prepare_stats_for_dashboard(stats_dict):
    """
    Add computed fields for dashboard display.

    Args:
        stats_dict: Statistics dictionary from ConnectionMonitor

    Returns:
        Enhanced statistics dictionary with computed fields
    """
    if stats_dict:
        # PHASE 3 (2025-10-23): Add total_bytes as sum of sent and received
        stats_dict['total_bytes'] = (
            (stats_dict.get('total_sent_bytes') or 0) +
            (stats_dict.get('total_received_bytes') or 0)
        )
    return stats_dict


async def event_ingestion_handler(request: web.Request) -> web.WebSocketResponse:
    """
    Handle event ingestion from test generators (2025-10-27).

    This endpoint receives test events and broadcasts them to the monitoring system.
    Used for testing AI Auditor and monitoring dashboard functionality.

    Args:
        request: aiohttp request object

    Returns:
        WebSocket response
    """
    ws = web.WebSocketResponse(
        timeout=3600.0,         # 1 hour overall timeout for long-running tests
        heartbeat=30.0,         # Ping interval (30 seconds)
        receive_timeout=3600.0  # Explicit receive timeout for long connections
    )
    await ws.prepare(request)

    logger.info(f"[EVENT_INGESTION] Test generator connected from {request.remote}")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                try:
                    event_data = json.loads(msg.data)

                    # Broadcast event to all connected dashboard clients
                    await broadcast_monitoring_event({
                        "type": "test_event",
                        "event": event_data,
                        "timestamp": log_timestamp()
                    })

                    # Send acknowledgment
                    await ws.send_str(json.dumps({"status": "received", "event_type": event_data.get("type")}))

                    logger.debug(f"[EVENT_INGESTION] Received and broadcast event: {event_data.get('type')}")

                except json.JSONDecodeError as e:
                    logger.warning(f"[EVENT_INGESTION] Invalid JSON: {e}")
                    await ws.send_str(json.dumps({"status": "error", "message": "Invalid JSON"}))
                except Exception as e:
                    logger.error(f"[EVENT_INGESTION] Error processing event: {e}")
                    await ws.send_str(json.dumps({"status": "error", "message": str(e)}))

            elif msg.type == web.WSMsgType.CLOSE:
                logger.info(f"[EVENT_INGESTION] WebSocket closed by client")
                break

            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"[EVENT_INGESTION] WebSocket error: {ws.exception()}")

    except Exception as e:
        logger.error(f"[EVENT_INGESTION] Connection error: {e}")
    finally:
        logger.info(f"[EVENT_INGESTION] Test generator disconnected")

    return ws



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

        # PHASE 3.5 (2025-10-23): Get session/conversation metrics from tracker
        session_metrics = _session_tracker.get_metrics()

        # PHASE 2.4 (2025-10-26): Get semaphore and WebSocket health metrics
        semaphore_manager = get_port_semaphore_manager()
        semaphore_metrics = semaphore_manager.get_metrics()
        websocket_health = _ws_health_tracker.get_metrics()

        initial_stats = {
            "type": "initial_stats",
            "stats": {
                "websocket": prepare_stats_for_dashboard(monitor.get_stats("websocket")),
                "redis": prepare_stats_for_dashboard(monitor.get_stats("redis")),
                "supabase": prepare_stats_for_dashboard(monitor.get_stats("supabase")),
                "kimi": prepare_stats_for_dashboard(monitor.get_stats("kimi")),
                "glm": prepare_stats_for_dashboard(monitor.get_stats("glm")),
            },
            "session_metrics": session_metrics,
            "semaphore_metrics": semaphore_metrics,
            "websocket_health": websocket_health,
            "recent_events": monitor.get_recent_events(limit=50),
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
                        stats = prepare_stats_for_dashboard(monitor.get_stats(connection_type))
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
                        # PHASE 3.1 (2025-10-23): get_recent_events returns dicts, not objects
                        # Events are already in dict format from to_dict(), so use them directly
                        await ws.send_str(json.dumps({
                            "type": "recent_events",
                            "connection_type": connection_type,
                            "events": events,  # Already dicts from get_recent_events()
                            "timestamp": log_timestamp(),
                        }))

                    elif command == "get_historical_data":
                        # PHASE 3.1 (2025-10-23): Get historical data from Redis
                        connection_type = data.get("connection_type")
                        hours = data.get("hours", 1)  # Default to last hour

                        historical_data = monitor.get_historical_data(connection_type, hours)
                        await ws.send_str(json.dumps({
                            "type": "historical_data",
                            "connection_type": connection_type,
                            "hours": hours,
                            "data": historical_data,
                            "timestamp": log_timestamp(),
                        }))

                    elif command == "get_time_series":
                        # PHASE 3.1 (2025-10-23): Get time-series aggregated data
                        connection_type = data.get("connection_type")
                        interval_minutes = data.get("interval_minutes", 5)
                        hours = data.get("hours", 1)

                        time_series_data = monitor.get_time_series_data(
                            connection_type, interval_minutes, hours
                        )
                        await ws.send_str(json.dumps({
                            "type": "time_series_data",
                            "connection_type": connection_type,
                            "interval_minutes": interval_minutes,
                            "hours": hours,
                            "data": time_series_data,
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


async def get_auditor_observations(request: web.Request) -> web.Response:
    """
    Get recent auditor observations from Supabase.

    Query params:
        limit: Number of observations to return (default: 50)
        severity: Filter by severity (critical, warning, info)
        category: Filter by category
        acknowledged: Filter by acknowledged status (true/false)

    Args:
        request: aiohttp request object

    Returns:
        JSON response with observations
    """
    try:
        from src.storage.supabase_client import get_storage_manager

        # Get query parameters
        limit = int(request.query.get('limit', 50))
        severity = request.query.get('severity')
        category = request.query.get('category')
        acknowledged = request.query.get('acknowledged')

        # FIXED (2025-10-24): Use singleton to avoid re-initializing client on every request
        supabase = get_storage_manager()
        client = supabase.get_client()

        # Build query
        query = client.table("auditor_observations").select("*")

        # Apply filters
        if severity:
            query = query.eq("severity", severity)
        if category:
            query = query.eq("category", category)
        if acknowledged is not None:
            query = query.eq("acknowledged", acknowledged.lower() == 'true')

        # Order by timestamp descending and limit
        query = query.order("timestamp", desc=True).limit(limit)

        # Execute query (Supabase client is sync, so run in thread pool)
        result = await asyncio.to_thread(lambda: query.execute())

        return web.json_response({
            "observations": result.data,
            "count": len(result.data),
            "timestamp": log_timestamp()
        })

    except Exception as e:
        logger.error(f"[MONITORING] Error fetching auditor observations: {e}")
        return web.json_response({
            "error": str(e),
            "observations": [],
            "count": 0
        }, status=500)


async def acknowledge_observation(request: web.Request) -> web.Response:
    """
    Acknowledge an auditor observation.

    Args:
        request: aiohttp request object with observation_id in path

    Returns:
        JSON response
    """
    try:
        from src.storage.supabase_client import get_storage_manager
        import asyncio

        observation_id = request.match_info['observation_id']

        # FIXED (2025-10-24): Use singleton to avoid re-initializing client on every request
        supabase = get_storage_manager()
        client = supabase.get_client()

        # Update observation (run in thread pool since Supabase client is sync)
        await asyncio.to_thread(
            lambda: client.table("auditor_observations").update({
                "acknowledged": True,
                "acknowledged_at": log_timestamp(),
                "acknowledged_by": "dashboard_user"  # TODO: Get actual user from auth
            }).eq("id", observation_id).execute()
        )

        return web.json_response({
            "success": True,
            "observation_id": observation_id,
            "timestamp": log_timestamp()
        })

    except Exception as e:
        logger.error(f"[MONITORING] Error acknowledging observation: {e}")
        return web.json_response({
            "error": str(e),
            "success": False
        }, status=500)


async def get_current_metrics(request: web.Request) -> web.Response:
    """
    Get current system metrics for testing baseline comparison.

    Phase 0.4 (2025-10-24): Testing Dashboard Support
    """
    try:
        # Calculate current metrics from recent events
        # For now, return mock data - will be replaced with actual metrics
        metrics = {
            "latency_p95": 150.0,  # ms
            "memory_mb": 85.0,     # MB
            "success_rate": 98.5,  # %
            "timestamp": log_timestamp()
        }

        return web.json_response(metrics)

    except Exception as e:
        logger.error(f"[MONITORING] Error fetching current metrics: {e}")
        return web.json_response({
            "error": str(e),
            "latency_p95": 0,
            "memory_mb": 0,
            "success_rate": 0
        }, status=500)


async def periodic_metrics_broadcast():
    """
    Periodically broadcast semaphore and WebSocket health metrics to dashboard.

    PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended periodic monitoring
    Broadcasts every 5 seconds to keep dashboard updated with latest metrics.
    """
    while True:
        try:
            await asyncio.sleep(5)  # Broadcast every 5 seconds

            if _dashboard_clients:
                # Broadcast semaphore metrics
                await _broadcast_semaphore_metrics()

                # Broadcast WebSocket health
                await _broadcast_websocket_health()

        except Exception as e:
            logger.error(f"Error in periodic metrics broadcast: {e}")


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

    # AI Auditor API routes (2025-10-24)
    app.router.add_get('/api/auditor/observations', get_auditor_observations)
    app.router.add_post('/api/auditor/observations/{observation_id}/acknowledge', acknowledge_observation)

    # Testing API routes (Phase 0.4 - 2025-10-24)
    app.router.add_get('/api/metrics/current', get_current_metrics)

    # Event ingestion endpoint for testing (2025-10-27)
    app.router.add_get('/events', event_ingestion_handler)
    logger.info("[MONITORING] Registered /events endpoint for test event ingestion")

    # Semaphore monitor (added 2025-10-21)
    static_dir = Path(__file__).parent.parent.parent / "static"
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

        # Schedule broadcast (non-blocking) - THREAD-SAFE for sync contexts
        if _dashboard_clients:
            try:
                # Try to get running loop (async context)
                loop = asyncio.get_running_loop()
                loop.create_task(broadcast_monitoring_event(event_data))
            except RuntimeError:
                # No running loop (sync context) - use thread pool
                from concurrent.futures import ThreadPoolExecutor
                import threading

                # Use a shared thread pool executor
                if not hasattr(broadcast_wrapper, '_executor'):
                    broadcast_wrapper._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="monitoring_broadcast")

                # Submit async task to thread pool
                def run_async_broadcast():
                    asyncio.run(broadcast_monitoring_event(event_data))

                broadcast_wrapper._executor.submit(run_async_broadcast)

    monitor.record_event = broadcast_wrapper
    logger.info("[MONITORING] Broadcast hook installed")

