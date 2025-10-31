"""
WebSocket Monitoring Adapter

Wraps the existing WebSocket monitoring system into the adapter interface.

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .base import Connection, MonitoringAdapter, UnifiedMonitoringEvent

logger = logging.getLogger(__name__)


class WebSocketAdapter(MonitoringAdapter):
    """
    Adapter for the existing WebSocket monitoring system.
    
    This adapter wraps the current WebSocket implementation and provides
    the standard adapter interface for use during the migration to Realtime.
    """
    
    def __init__(self):
        """Initialize WebSocket adapter."""
        super().__init__('websocket')
        self._connections: Dict[str, Connection] = {}
        self._dashboard_clients: Set[Any] = set()
        self._metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'total_events_broadcast': 0,
            'failed_broadcasts': 0,
        }
    
    async def connect(self, dashboard_id: str) -> Connection:
        """
        Register a new WebSocket connection.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
            
        Returns:
            Connection object
        """
        connection = Connection(
            connection_id=dashboard_id,
            adapter_type='websocket',
            connected_at=datetime.utcnow(),
            metadata={'dashboard_id': dashboard_id}
        )
        
        self._connections[dashboard_id] = connection
        self._metrics['total_connections'] += 1
        self._metrics['active_connections'] = len(self._connections)
        
        self.logger.info(f"WebSocket connection established: {dashboard_id}")
        return connection
    
    async def disconnect(self, dashboard_id: str) -> None:
        """
        Close a WebSocket connection.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
        """
        if dashboard_id in self._connections:
            del self._connections[dashboard_id]
            self._metrics['active_connections'] = len(self._connections)
            self.logger.info(f"WebSocket connection closed: {dashboard_id}")
    
    async def broadcast_event(self, event: UnifiedMonitoringEvent) -> None:
        """
        Broadcast a monitoring event to all connected WebSocket clients.
        
        Args:
            event: Unified monitoring event to broadcast
        """
        if not self._dashboard_clients:
            return
        
        try:
            event_data = event.to_dict()
            disconnected = set()
            
            for client in self._dashboard_clients:
                try:
                    await client.send_str(json.dumps(event_data))
                except Exception as e:
                    self.logger.debug(f"Failed to send to WebSocket client: {e}")
                    disconnected.add(client)
            
            # Remove disconnected clients
            self._dashboard_clients.difference_update(disconnected)
            
            self._metrics['total_events_broadcast'] += 1
            
        except Exception as e:
            self.logger.error(f"Error broadcasting WebSocket event: {e}")
            self._metrics['failed_broadcasts'] += 1
    
    async def broadcast_batch(self, events: List[UnifiedMonitoringEvent]) -> None:
        """
        Broadcast multiple events efficiently.
        
        Args:
            events: List of unified monitoring events
        """
        for event in events:
            await self.broadcast_event(event)
    
    async def get_connection_count(self) -> int:
        """Get the number of active WebSocket connections."""
        return len(self._connections)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get WebSocket adapter metrics."""
        return {
            'adapter_type': 'websocket',
            'total_connections': self._metrics['total_connections'],
            'active_connections': self._metrics['active_connections'],
            'total_events_broadcast': self._metrics['total_events_broadcast'],
            'failed_broadcasts': self._metrics['failed_broadcasts'],
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    async def health_check(self) -> bool:
        """Check if WebSocket adapter is healthy."""
        # WebSocket adapter is healthy if it can track connections
        return True
    
    def register_client(self, client: Any) -> None:
        """
        Register a WebSocket client for broadcasting.
        
        Args:
            client: WebSocket client object
        """
        self._dashboard_clients.add(client)
        self.logger.debug(f"Registered WebSocket client, total: {len(self._dashboard_clients)}")
    
    def unregister_client(self, client: Any) -> None:
        """
        Unregister a WebSocket client.
        
        Args:
            client: WebSocket client object
        """
        self._dashboard_clients.discard(client)
        self.logger.debug(f"Unregistered WebSocket client, total: {len(self._dashboard_clients)}")

