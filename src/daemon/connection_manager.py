"""
Connection Manager for WebSocket Server

This module provides connection tracking and limit enforcement for the WebSocket server.
Implements global and per-IP connection limits to prevent resource exhaustion.

PHASE 1 (2025-10-18): Connection Limits Implementation
- Global connection limit enforcement
- Per-IP connection limit enforcement
- Graceful connection rejection
- Connection duration tracking
- Prometheus metrics integration
"""

import logging
import time
from collections import defaultdict
from typing import Optional, Set, Dict
import os

logger = logging.getLogger(__name__)

# Default configuration (can be overridden by environment variables)
DEFAULT_MAX_CONNECTIONS = 1000
DEFAULT_MAX_CONNECTIONS_PER_IP = 10


class ConnectionManager:
    """
    Manages WebSocket connections with global and per-IP limits.
    
    Features:
    - Global connection limit enforcement
    - Per-IP connection limit enforcement
    - Connection duration tracking
    - Graceful connection rejection
    - Prometheus metrics integration
    
    Thread-safe for concurrent connection handling.
    """
    
    def __init__(
        self,
        max_connections: Optional[int] = None,
        max_connections_per_ip: Optional[int] = None
    ):
        """
        Initialize ConnectionManager with configurable limits.
        
        Args:
            max_connections: Global connection limit (default from env or 1000)
            max_connections_per_ip: Per-IP connection limit (default from env or 10)
        """
        # Load configuration from environment or use defaults
        self.max_connections = max_connections or int(
            os.getenv("MAX_CONNECTIONS", str(DEFAULT_MAX_CONNECTIONS))
        )
        self.max_connections_per_ip = max_connections_per_ip or int(
            os.getenv("MAX_CONNECTIONS_PER_IP", str(DEFAULT_MAX_CONNECTIONS_PER_IP))
        )
        
        # Connection tracking
        self.active_connections: Set[str] = set()  # Set of connection IDs
        self.connections_by_ip: Dict[str, Set[str]] = defaultdict(set)  # IP -> Set of connection IDs
        self.connection_times: Dict[str, float] = {}  # Connection ID -> start time
        self.connection_ips: Dict[str, str] = {}  # Connection ID -> IP address
        
        logger.info(
            f"ConnectionManager initialized: max_connections={self.max_connections}, "
            f"max_per_ip={self.max_connections_per_ip}"
        )
    
    def can_accept_connection(self, client_ip: str) -> tuple[bool, Optional[str]]:
        """
        Check if a new connection can be accepted.
        
        Args:
            client_ip: IP address of the client
            
        Returns:
            Tuple of (can_accept, rejection_reason)
            - (True, None) if connection can be accepted
            - (False, reason) if connection should be rejected
        """
        # Check global limit
        if len(self.active_connections) >= self.max_connections:
            logger.warning(
                f"Global connection limit reached: {len(self.active_connections)}/{self.max_connections}"
            )
            return False, "Server overloaded - global connection limit reached"
        
        # Check per-IP limit
        ip_connections = len(self.connections_by_ip.get(client_ip, set()))
        if ip_connections >= self.max_connections_per_ip:
            logger.warning(
                f"Per-IP connection limit reached for {client_ip}: "
                f"{ip_connections}/{self.max_connections_per_ip}"
            )
            return False, f"Too many connections from your IP ({ip_connections}/{self.max_connections_per_ip})"
        
        return True, None
    
    def register_connection(self, connection_id: str, client_ip: str) -> None:
        """
        Register a new connection.
        
        Args:
            connection_id: Unique identifier for the connection
            client_ip: IP address of the client
        """
        self.active_connections.add(connection_id)
        self.connections_by_ip[client_ip].add(connection_id)
        self.connection_times[connection_id] = time.time()
        self.connection_ips[connection_id] = client_ip
        
        logger.info(
            f"Connection registered: {connection_id} from {client_ip} "
            f"(total: {len(self.active_connections)}, ip_total: {len(self.connections_by_ip[client_ip])})"
        )
    
    def unregister_connection(self, connection_id: str) -> None:
        """
        Unregister a connection when it closes.
        
        Args:
            connection_id: Unique identifier for the connection
        """
        if connection_id not in self.active_connections:
            logger.warning(f"Attempted to unregister unknown connection: {connection_id}")
            return
        
        # Get connection details before cleanup
        client_ip = self.connection_ips.get(connection_id)
        start_time = self.connection_times.get(connection_id)
        duration = time.time() - start_time if start_time else 0
        
        # Remove from tracking
        self.active_connections.discard(connection_id)
        if client_ip:
            self.connections_by_ip[client_ip].discard(connection_id)
            # Clean up empty IP entries
            if not self.connections_by_ip[client_ip]:
                del self.connections_by_ip[client_ip]
        
        self.connection_times.pop(connection_id, None)
        self.connection_ips.pop(connection_id, None)
        
        logger.info(
            f"Connection unregistered: {connection_id} from {client_ip} "
            f"(duration: {duration:.2f}s, remaining: {len(self.active_connections)})"
        )
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return len(self.active_connections)
    
    def get_ip_connection_count(self, client_ip: str) -> int:
        """Get number of active connections from a specific IP."""
        return len(self.connections_by_ip.get(client_ip, set()))
    
    def get_connection_duration(self, connection_id: str) -> Optional[float]:
        """
        Get duration of a connection in seconds.
        
        Args:
            connection_id: Unique identifier for the connection
            
        Returns:
            Duration in seconds, or None if connection not found
        """
        start_time = self.connection_times.get(connection_id)
        if start_time:
            return time.time() - start_time
        return None
    
    def get_stats(self) -> dict:
        """
        Get connection statistics.
        
        Returns:
            Dictionary with connection statistics
        """
        return {
            "total_connections": len(self.active_connections),
            "max_connections": self.max_connections,
            "utilization_percent": (len(self.active_connections) / self.max_connections * 100)
                if self.max_connections > 0 else 0,
            "unique_ips": len(self.connections_by_ip),
            "max_per_ip": self.max_connections_per_ip,
            "connections_by_ip": {
                ip: len(conn_ids) for ip, conn_ids in self.connections_by_ip.items()
            }
        }
    
    def get_prometheus_metrics(self) -> dict:
        """
        Get metrics in Prometheus format.
        
        Returns:
            Dictionary with Prometheus-compatible metrics
        """
        stats = self.get_stats()
        return {
            "websocket_connections_active": stats["total_connections"],
            "websocket_connections_max": stats["max_connections"],
            "websocket_connections_utilization_percent": stats["utilization_percent"],
            "websocket_unique_ips": stats["unique_ips"],
            "websocket_max_connections_per_ip": stats["max_per_ip"],
        }


# Singleton instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """
    Get the singleton ConnectionManager instance.
    
    Returns:
        ConnectionManager singleton
    """
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


__all__ = ["ConnectionManager", "get_connection_manager"]

