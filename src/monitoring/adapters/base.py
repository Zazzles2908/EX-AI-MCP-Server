"""
Base Monitoring Adapter Interface

Defines the abstract interface for monitoring adapters (WebSocket, Realtime, etc.)

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class UnifiedMonitoringEvent:
    """
    Unified monitoring event model.

    Both WebSocket and Realtime adapters normalize their events to this format.
    This ensures the dashboard code remains unchanged during migration.

    Phase 2.6.1 Enhancement:
    - Added category field for event classification
    - Added sequence_id for reconciliation and ordering
    """
    event_type: str
    timestamp: datetime
    source: str  # 'websocket', 'realtime', 'redis', etc.
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: Optional[str] = None  # EventCategory.value (e.g., 'critical', 'performance')
    sequence_id: Optional[int] = None  # For reconciliation and ordering

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'data': self.data,
            'metadata': self.metadata,
        }

        # Include category and sequence_id if present
        if self.category:
            result['category'] = self.category
        if self.sequence_id is not None:
            result['sequence_id'] = self.sequence_id

        return result


@dataclass
class Connection:
    """Represents an active monitoring connection."""
    connection_id: str
    adapter_type: str
    connected_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class MonitoringAdapter(ABC):
    """
    Abstract base class for monitoring adapters.
    
    Adapters implement different transport mechanisms (WebSocket, Realtime, etc.)
    while maintaining a consistent interface for the monitoring system.
    """
    
    def __init__(self, adapter_type: str):
        """
        Initialize adapter.
        
        Args:
            adapter_type: Type of adapter ('websocket', 'realtime', etc.)
        """
        self.adapter_type = adapter_type
        self.logger = logging.getLogger(f"{__name__}.{adapter_type}")
    
    @abstractmethod
    async def connect(self, dashboard_id: str) -> Connection:
        """
        Establish a monitoring connection.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
            
        Returns:
            Connection object representing the established connection
            
        Raises:
            ConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def disconnect(self, dashboard_id: str) -> None:
        """
        Close a monitoring connection.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
        """
        pass
    
    @abstractmethod
    async def broadcast_event(self, event: UnifiedMonitoringEvent) -> None:
        """
        Broadcast a monitoring event to all connected clients.
        
        Args:
            event: Unified monitoring event to broadcast
            
        Raises:
            BroadcastError: If broadcast fails
        """
        pass
    
    @abstractmethod
    async def broadcast_batch(self, events: List[UnifiedMonitoringEvent]) -> None:
        """
        Broadcast multiple monitoring events efficiently.
        
        Args:
            events: List of unified monitoring events to broadcast
            
        Raises:
            BroadcastError: If broadcast fails
        """
        pass
    
    @abstractmethod
    async def get_connection_count(self) -> int:
        """
        Get the number of active connections.
        
        Returns:
            Number of connected clients
        """
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get adapter metrics and statistics.
        
        Returns:
            Dictionary containing adapter metrics
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the adapter is healthy and operational.
        
        Returns:
            True if healthy, False otherwise
        """
        pass
    
    def _normalize_event(self, raw_event: Dict[str, Any]) -> UnifiedMonitoringEvent:
        """
        Normalize adapter-specific event to unified format.
        
        Subclasses should override this method to implement their specific
        normalization logic.
        
        Args:
            raw_event: Raw event from the adapter
            
        Returns:
            Normalized UnifiedMonitoringEvent
        """
        return UnifiedMonitoringEvent(
            event_type=raw_event.get('type', 'unknown'),
            timestamp=datetime.fromisoformat(raw_event.get('timestamp', datetime.utcnow().isoformat())),
            source=self.adapter_type,
            data=raw_event.get('data', raw_event),
            metadata={'adapter': self.adapter_type}
        )

