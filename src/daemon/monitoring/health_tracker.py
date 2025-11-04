"""
Health Tracker Module

Tracks WebSocket connection health metrics for monitoring dashboard.

Split from monitoring_endpoint.py (2025-11-03) to eliminate god object.
Originally part of 1,467-line monitoring_endpoint.py file.

Responsibilities:
- Track ping/pong latency
- Track connection uptime
- Track reconnection events
- Track timeout warnings
- Provide health metrics
"""

import time
from typing import Dict, Optional


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
            min_latency = min(latencies) if latencies else 0
            max_latency = max(latencies) if latencies else 0

            metrics[port] = {
                'connected_at': conn['connected_at'],
                'uptime_seconds': uptime_seconds,
                'uptime_hours': round(uptime_seconds / 3600, 2),
                'last_ping': conn['last_ping'],
                'ping_latency_ms': conn['ping_latency_ms'],
                'avg_latency_ms': round(avg_latency, 2),
                'min_latency_ms': round(min_latency, 2),
                'max_latency_ms': round(max_latency, 2),
                'ping_count': len(latencies),
                'reconnection_count': conn['reconnection_count'],
                'timeout_warnings': conn['timeout_warnings']
            }

        return metrics


# Global health tracker instance
_health_tracker = WebSocketHealthTracker()


def get_health_tracker() -> WebSocketHealthTracker:
    """Get the global health tracker instance"""
    return _health_tracker
