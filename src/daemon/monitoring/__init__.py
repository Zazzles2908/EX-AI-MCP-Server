"""Monitoring module - decomposed from monitoring_endpoint.py

This module provides a cleaner, more maintainable structure for the monitoring
system by splitting functionality into focused, single-purpose components.

Components:
- WebSocketHandler: WebSocket connections and health tracking
- MetricsBroadcaster: Metrics collection and broadcasting
- HealthTracker: Health check and tracking
- HTTPEndpoints: HTTP API endpoints
- SessionMonitor: Session lifecycle management
"""

from .memory_monitor import get_memory_monitor, AlertLevel

__all__ = [
    'get_memory_monitor',
    'AlertLevel',
]
