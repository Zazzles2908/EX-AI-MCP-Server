"""
WebSocket Handler Module

Handles WebSocket connections, health tracking, and periodic metrics broadcasting.
Extracted from monitoring_endpoint.py to improve maintainability.

Components:
- WebSocketHealthTracker: Track connection health and ping/pong latency
- WebSocket connection handlers
- Periodic metrics broadcasting
"""

import asyncio
import json
import logging
import time
from typing import Set, Dict, Optional
from aiohttp import web
from collections import defaultdict

from utils.monitoring import get_monitor
from utils.timezone_helper import log_timestamp
from src.daemon.middleware.semaphores import get_port_semaphore_manager
from src.monitoring.broadcaster import get_broadcaster

logger = logging.getLogger(__name__)

# Connected dashboard clients
_dashboard_clients: Set[web.WebSocketResponse] = set()

# PHASE 2 (2025-11-01): Monitoring broadcaster for adapter-based event distribution
_broadcaster = get_broadcaster()


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

                    # Import broadcast function from metrics_broadcaster
                    from .metrics_broadcaster import broadcast_monitoring_event

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


async def periodic_metrics_broadcast():
    """
    Periodically broadcast semaphore and WebSocket health metrics to dashboard.

    PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended periodic monitoring
    PHASE 1 DASHBOARD INTEGRATION (2025-10-31): Added cache metrics
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

                # PHASE 3 FIX (2025-11-01): Removed cache metrics broadcasting (redundant)

        except Exception as e:
            logger.error(f"Error in periodic metrics broadcast: {e}")


# Public API functions
def get_dashboard_clients() -> Set[web.WebSocketResponse]:
    """Get set of connected dashboard clients"""
    return _dashboard_clients


def add_dashboard_client(ws: web.WebSocketResponse) -> None:
    """Add a WebSocket client to the set"""
    _dashboard_clients.add(ws)


def remove_dashboard_client(ws: web.WebSocketResponse) -> None:
    """Remove a WebSocket client from the set"""
    _dashboard_clients.discard(ws)


def get_websocket_health_tracker() -> WebSocketHealthTracker:
    """Get the WebSocket health tracker instance"""
    return _ws_health_tracker
