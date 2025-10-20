"""
Centralized Connection Monitoring System for EXAI MCP Server

Tracks all connection points and data flow for easier debugging:
- WebSocket connections (ws_server.py)
- Redis connections (storage_backend.py)
- Supabase connections (supabase_client.py)
- Kimi API connections (kimi provider)
- GLM API connections (glm provider)

Each connection point reports:
- Data sent/received
- Response times
- Error rates
- Connected script/function names (for debugging)

Created: 2025-10-18
Purpose: Centralized monitoring for easier bug fixing
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import deque
from threading import Lock
import json

logger = logging.getLogger(__name__)


@dataclass
class ConnectionEvent:
    """Single connection event with timing and metadata"""
    timestamp: float
    connection_type: str  # websocket, redis, supabase, kimi, glm
    direction: str  # send, receive, error
    script_name: str  # e.g., "ws_server.py::_handle_message"
    function_name: str  # e.g., "_handle_message"
    data_size_bytes: int
    response_time_ms: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
            "connection_type": self.connection_type,
            "direction": self.direction,
            "script": self.script_name,
            "function": self.function_name,
            "data_size_bytes": self.data_size_bytes,
            "response_time_ms": self.response_time_ms,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class ConnectionStats:
    """Aggregated statistics for a connection type"""
    connection_type: str
    total_events: int = 0
    total_sent_bytes: int = 0
    total_received_bytes: int = 0
    total_errors: int = 0
    avg_response_time_ms: float = 0.0
    last_event_timestamp: Optional[float] = None
    active_connections: int = 0


class ConnectionMonitor:
    """
    Centralized connection monitoring system
    
    Thread-safe singleton that tracks all connection events across the system.
    Provides real-time metrics and historical data for debugging.
    """
    
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._initialized = True
        self._events: deque = deque(maxlen=10000)  # Keep last 10k events
        self._stats: Dict[str, ConnectionStats] = {}
        self._active_connections: Dict[str, int] = {}
        self._event_lock = Lock()
        
        logger.info("[CONNECTION_MONITOR] Initialized with 10k event buffer")
    
    def record_event(
        self,
        connection_type: str,
        direction: str,
        script_name: str,
        function_name: str,
        data_size_bytes: int,
        response_time_ms: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a connection event
        
        Args:
            connection_type: Type of connection (websocket, redis, supabase, kimi, glm)
            direction: Direction of data flow (send, receive, error)
            script_name: Name of the script (e.g., "ws_server.py")
            function_name: Name of the function (e.g., "_handle_message")
            data_size_bytes: Size of data in bytes
            response_time_ms: Response time in milliseconds (optional)
            error: Error message if any (optional)
            metadata: Additional metadata (optional)
        """
        event = ConnectionEvent(
            timestamp=time.time(),
            connection_type=connection_type,
            direction=direction,
            script_name=script_name,
            function_name=function_name,
            data_size_bytes=data_size_bytes,
            response_time_ms=response_time_ms,
            error=error,
            metadata=metadata or {}
        )
        
        with self._event_lock:
            self._events.append(event)
            self._update_stats(event)
        
        # Log the event for real-time monitoring
        if error:
            logger.error(
                f"[{connection_type.upper()}] ERROR in {script_name}::{function_name} - {error}"
            )
        else:
            logger.debug(
                f"[{connection_type.upper()}] {direction.upper()} "
                f"{script_name}::{function_name} "
                f"({data_size_bytes} bytes"
                f"{f', {response_time_ms:.2f}ms' if response_time_ms else ''})"
            )
    
    def _update_stats(self, event: ConnectionEvent) -> None:
        """Update aggregated statistics (called with lock held)"""
        conn_type = event.connection_type
        
        if conn_type not in self._stats:
            self._stats[conn_type] = ConnectionStats(connection_type=conn_type)
        
        stats = self._stats[conn_type]
        stats.total_events += 1
        stats.last_event_timestamp = event.timestamp
        
        if event.direction == "send":
            stats.total_sent_bytes += event.data_size_bytes
        elif event.direction == "receive":
            stats.total_received_bytes += event.data_size_bytes
        elif event.direction == "error":
            stats.total_errors += 1
        
        if event.response_time_ms is not None:
            # Update running average
            old_avg = stats.avg_response_time_ms
            old_count = stats.total_events - 1
            stats.avg_response_time_ms = (
                (old_avg * old_count + event.response_time_ms) / stats.total_events
            )
    
    def increment_active_connections(self, connection_type: str) -> None:
        """Increment active connection count for a connection type"""
        with self._event_lock:
            if connection_type not in self._active_connections:
                self._active_connections[connection_type] = 0
            self._active_connections[connection_type] += 1
            
            if connection_type in self._stats:
                self._stats[connection_type].active_connections = (
                    self._active_connections[connection_type]
                )
    
    def decrement_active_connections(self, connection_type: str) -> None:
        """Decrement active connection count for a connection type"""
        with self._event_lock:
            if connection_type in self._active_connections:
                self._active_connections[connection_type] = max(
                    0, self._active_connections[connection_type] - 1
                )
                
                if connection_type in self._stats:
                    self._stats[connection_type].active_connections = (
                        self._active_connections[connection_type]
                    )
    
    def get_stats(self, connection_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregated statistics
        
        Args:
            connection_type: Specific connection type, or None for all
            
        Returns:
            Dictionary of statistics
        """
        with self._event_lock:
            if connection_type:
                stats = self._stats.get(connection_type)
                return asdict(stats) if stats else {}
            else:
                return {
                    conn_type: asdict(stats)
                    for conn_type, stats in self._stats.items()
                }
    
    def get_recent_events(
        self,
        connection_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get recent connection events
        
        Args:
            connection_type: Filter by connection type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of event dictionaries
        """
        with self._event_lock:
            events = list(self._events)
        
        if connection_type:
            events = [e for e in events if e.connection_type == connection_type]
        
        # Return most recent events first
        events = events[-limit:]
        events.reverse()
        
        return [event.to_dict() for event in events]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all connection monitoring data"""
        with self._event_lock:
            return {
                "total_events": len(self._events),
                "connection_types": list(self._stats.keys()),
                "stats": self.get_stats(),
                "active_connections": dict(self._active_connections),
                "buffer_size": self._events.maxlen,
                "buffer_usage": len(self._events)
            }
    
    def export_json(self, filepath: str) -> None:
        """Export monitoring data to JSON file"""
        try:
            data = {
                "summary": self.get_summary(),
                "recent_events": self.get_recent_events(limit=1000)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"[CONNECTION_MONITOR] Exported monitoring data to {filepath}")
        except Exception as e:
            logger.error(f"[CONNECTION_MONITOR] Failed to export data: {e}")


# Global singleton instance
_monitor = ConnectionMonitor()


def get_monitor() -> ConnectionMonitor:
    """Get the global connection monitor instance"""
    return _monitor


# Convenience functions for common operations
def record_websocket_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a WebSocket event"""
    _monitor.record_event(
        connection_type="websocket",
        direction=direction,
        script_name="ws_server.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_redis_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Redis event"""
    _monitor.record_event(
        connection_type="redis",
        direction=direction,
        script_name="storage_backend.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_supabase_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Supabase event"""
    _monitor.record_event(
        connection_type="supabase",
        direction=direction,
        script_name="supabase_client.py",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_kimi_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a Kimi API event"""
    _monitor.record_event(
        connection_type="kimi",
        direction=direction,
        script_name="kimi_provider",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )


def record_glm_event(direction: str, function_name: str, data_size: int, **kwargs):
    """Record a GLM API event"""
    _monitor.record_event(
        connection_type="glm",
        direction=direction,
        script_name="glm_provider",
        function_name=function_name,
        data_size_bytes=data_size,
        **kwargs
    )

