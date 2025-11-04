"""
Dashboard Broadcaster Module

Broadcasts monitoring events and metrics to all connected dashboard clients.
Handles real-time data distribution.

Split from monitoring_endpoint.py (2025-11-04) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Broadcast events to all clients
- Aggregate metrics from multiple sources
- Send periodic updates
- Handle broadcast failures gracefully
"""

import asyncio
import json
import logging
from typing import Dict, Any, Set, Callable, Optional
from aiohttp.web_ws import WebSocketResponse

logger = logging.getLogger(__name__)


class DashboardBroadcaster:
    """Broadcasts monitoring data to all connected dashboard clients"""

    def __init__(self):
        self.clients: Set[web.WebSocketResponse] = set()
        self.event_handlers: list[Callable] = []
        self._broadcast_lock = asyncio.Lock()

    def register_client(self, ws: web.WebSocketResponse):
        """
        Register a new dashboard client.

        Args:
            ws: WebSocket response
        """
        self.clients.add(ws)
        logger.debug(f"Dashboard client registered. Total clients: {len(self.clients)}")

    def unregister_client(self, ws: web.WebSocketResponse):
        """
        Unregister a dashboard client.

        Args:
            ws: WebSocket response
        """
        self.clients.discard(ws)
        logger.debug(f"Dashboard client unregistered. Total clients: {len(self.clients)}")

    async def broadcast_event(self, event_type: str, data: Dict[str, Any]):
        """
        Broadcast an event to all connected clients.

        Args:
            event_type: Type of event (e.g., 'metrics', 'alert', 'status')
            data: Event data
        """
        if not self.clients:
            return

        message = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }

        async with self._broadcast_lock:
            await self._broadcast_to_all(message)

    async def broadcast_metrics(self, metrics: Dict[str, Any]):
        """
        Broadcast metrics update to all clients.

        Args:
            metrics: Metrics dictionary
        """
        await self.broadcast_event("metrics_update", metrics)

    async def broadcast_alert(self, alert: Dict[str, Any]):
        """
        Broadcast an alert to all clients.

        Args:
            alert: Alert data
        """
        await self.broadcast_event("alert", alert)

    async def broadcast_status(self, status: Dict[str, Any]):
        """
        Broadcast system status to all clients.

        Args:
            status: Status data
        """
        await self.broadcast_event("status_update", status)

    async def _broadcast_to_all(self, message: Dict[str, Any]):
        """
        Internal method to broadcast message to all clients.

        Args:
            message: Message to broadcast
        """
        disconnected_clients = []

        for client in self.clients:
            try:
                await client.send_json(message)
            except Exception as e:
                logger.debug(f"Failed to send to client, marking for removal: {e}")
                disconnected_clients.append(client)

        # Cleanup disconnected clients
        for client in disconnected_clients:
            self.unregister_client(client)

    def add_event_handler(self, handler: Callable):
        """
        Add an event handler function.

        Args:
            handler: Async function that receives (event_type, data)
        """
        self.event_handlers.append(handler)

    async def _notify_handlers(self, event_type: str, data: Dict[str, Any]):
        """
        Notify all registered event handlers.

        Args:
            event_type: Type of event
            data: Event data
        """
        for handler in self.event_handlers:
            try:
                await handler(event_type, data)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")

    def get_client_count(self) -> int:
        """
        Get number of connected clients.

        Returns:
            Number of connected clients
        """
        return len(self.clients)


# Global broadcaster instance
_broadcaster_instance: Optional[DashboardBroadcaster] = None


def get_broadcaster() -> DashboardBroadcaster:
    """
    Get the global dashboard broadcaster instance.

    Returns:
        DashboardBroadcaster instance
    """
    global _broadcaster_instance
    if _broadcaster_instance is None:
        _broadcaster_instance = DashboardBroadcaster()
    return _broadcaster_instance
