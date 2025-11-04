"""
WebSocket Handler Module

Handles WebSocket connections for the monitoring dashboard.
Provides real-time bidirectional communication.

Split from monitoring_endpoint.py (2025-11-04) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Accept WebSocket connections
- Send real-time monitoring data
- Handle client messages
- Track connection health
"""

import asyncio
import json
import logging
from typing import Set, Dict
from aiohttp import web
from aiohttp.web_ws import WebSocketResponse

from src.daemon.monitoring.health_tracker import WebSocketHealthTracker

logger = logging.getLogger(__name__)


class MonitoringWebSocketHandler:
    """Handles WebSocket connections for monitoring dashboard"""

    def __init__(self):
        self.clients: Set[web.WebSocketResponse] = set()
        self.health_tracker = WebSocketHealthTracker()
        self.connected_since: Dict[web.WebSocketResponse, float] = {}

    async def handle_connection(self, request: web.Request) -> web.WebSocketResponse:
        """
        Handle a new WebSocket connection request.

        Args:
            request: The aiohttp request

        Returns:
            WebSocket response
        """
        ws = web.WebSocketResponse(heartbeat=20)
        await ws.prepare(request)

        # Register client
        self.clients.add(ws)
        self.connected_since[ws] = asyncio.get_event_loop().time()

        # Get port for health tracking
        port = request.host.split(':')[-1] if ':' in request.host else '80'
        try:
            port = int(port)
        except ValueError:
            port = 80

        self.health_tracker.register_connection(port)

        client_id = f"{request.remote}:{port}"
        logger.info(f"Monitoring dashboard connected: {client_id}")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await self._handle_message(msg.data, ws)
                elif msg.type == web.WSMsgType.ERROR:
                    logger.error(f'WebSocket error for {client_id}: {ws.exception()}')
        except Exception as e:
            logger.error(f"WebSocket handler error for {client_id}: {e}")
        finally:
            # Cleanup
            if ws in self.clients:
                self.clients.remove(ws)
            if ws in self.connected_since:
                del self.connected_since[ws]

            logger.info(f"Monitoring dashboard disconnected: {client_id}")

        return ws

    async def _handle_message(self, message: str, ws: WebSocketResponse):
        """
        Handle incoming messages from dashboard clients.

        Args:
            message: JSON message string
            ws: WebSocket response
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "ping":
                await ws.send_json({"type": "pong", "timestamp": asyncio.get_event_loop().time()})
            elif msg_type == "request_metrics":
                await self._send_current_metrics(ws)
            else:
                logger.debug(f"Unknown message type from dashboard: {msg_type}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON from dashboard: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def _send_current_metrics(self, ws: WebSocketResponse):
        """
        Send current system metrics to a specific client.

        Args:
            ws: WebSocket response to send to
        """
        metrics = {
            "type": "metrics_update",
            "timestamp": asyncio.get_event_loop().time(),
            "data": {
                "active_connections": len(self.clients),
                "uptime": self._calculate_uptime(ws)
            }
        }

        try:
            await ws.send_json(metrics)
        except Exception as e:
            logger.error(f"Error sending metrics: {e}")

    def _calculate_uptime(self, ws: WebSocketResponse) -> float:
        """
        Calculate connection uptime in seconds.

        Args:
            ws: WebSocket response

        Returns:
            Uptime in seconds
        """
        if ws in self.connected_since:
            return asyncio.get_event_loop().time() - self.connected_since[ws]
        return 0

    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)

    def get_all_clients(self) -> Set[web.WebSocketResponse]:
        """Get set of all connected clients (read-only)"""
        return self.clients.copy()
