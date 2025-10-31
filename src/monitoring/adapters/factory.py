"""
Monitoring Adapter Factory

Creates and manages monitoring adapter instances based on configuration.

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

import logging
import os
from typing import Optional

from .base import MonitoringAdapter
from .websocket_adapter import WebSocketAdapter
from .realtime_adapter import RealtimeAdapter

logger = logging.getLogger(__name__)


class MonitoringAdapterFactory:
    """
    Factory for creating monitoring adapters.
    
    Supports creating adapters based on environment configuration
    and provides singleton instances for each adapter type.
    """
    
    _instances = {}
    
    @staticmethod
    def create_adapter(adapter_type: str = 'auto') -> MonitoringAdapter:
        """
        Create or retrieve a monitoring adapter instance.
        
        Args:
            adapter_type: Type of adapter to create:
                - 'websocket': Use WebSocket adapter
                - 'realtime': Use Supabase Realtime adapter
                - 'auto': Auto-detect based on environment (default)
        
        Returns:
            MonitoringAdapter instance
        """
        # Return cached instance if available
        if adapter_type in MonitoringAdapterFactory._instances:
            return MonitoringAdapterFactory._instances[adapter_type]
        
        # Auto-detect based on environment
        if adapter_type == 'auto':
            use_realtime = os.getenv('MONITORING_USE_REALTIME', 'false').lower() == 'true'
            adapter_type = 'realtime' if use_realtime else 'websocket'
        
        # Create appropriate adapter
        if adapter_type == 'websocket':
            adapter = WebSocketAdapter()
        elif adapter_type == 'realtime':
            adapter = RealtimeAdapter()
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
        
        # Cache instance
        MonitoringAdapterFactory._instances[adapter_type] = adapter
        logger.info(f"Created {adapter_type} monitoring adapter")
        
        return adapter
    
    @staticmethod
    def create_dual_adapter() -> 'DualMonitoringAdapter':
        """
        Create a dual adapter that runs both WebSocket and Realtime in parallel.
        
        Used during the migration phase to validate data consistency.
        
        Returns:
            DualMonitoringAdapter instance
        """
        websocket_adapter = MonitoringAdapterFactory.create_adapter('websocket')
        realtime_adapter = MonitoringAdapterFactory.create_adapter('realtime')
        
        return DualMonitoringAdapter(websocket_adapter, realtime_adapter)
    
    @staticmethod
    def get_adapter(adapter_type: str = 'auto') -> Optional[MonitoringAdapter]:
        """
        Get a cached adapter instance without creating a new one.
        
        Args:
            adapter_type: Type of adapter to retrieve
        
        Returns:
            MonitoringAdapter instance or None if not cached
        """
        return MonitoringAdapterFactory._instances.get(adapter_type)
    
    @staticmethod
    def clear_cache() -> None:
        """Clear all cached adapter instances."""
        MonitoringAdapterFactory._instances.clear()
        logger.info("Cleared monitoring adapter cache")


class DualMonitoringAdapter(MonitoringAdapter):
    """
    Dual adapter that runs both WebSocket and Realtime in parallel.
    
    Used during migration phase to:
    - Validate data consistency between systems
    - Gradually migrate clients
    - Ensure no data loss during transition
    """
    
    def __init__(self, primary: MonitoringAdapter, secondary: MonitoringAdapter):
        """
        Initialize dual adapter.
        
        Args:
            primary: Primary adapter (usually WebSocket during migration)
            secondary: Secondary adapter (usually Realtime during migration)
        """
        super().__init__('dual')
        self.primary = primary
        self.secondary = secondary
        self._metrics = {
            'primary_events': 0,
            'secondary_events': 0,
            'primary_failures': 0,
            'secondary_failures': 0,
        }
    
    async def connect(self, dashboard_id: str):
        """Connect to both adapters."""
        try:
            primary_conn = await self.primary.connect(dashboard_id)
        except Exception as e:
            self.logger.error(f"Primary adapter connection failed: {e}")
            self._metrics['primary_failures'] += 1
            primary_conn = None
        
        try:
            secondary_conn = await self.secondary.connect(dashboard_id)
        except Exception as e:
            self.logger.error(f"Secondary adapter connection failed: {e}")
            self._metrics['secondary_failures'] += 1
            secondary_conn = None
        
        if not primary_conn and not secondary_conn:
            raise ConnectionError("Both adapters failed to connect")
        
        # Return primary connection (or secondary if primary failed)
        return primary_conn or secondary_conn
    
    async def disconnect(self, dashboard_id: str) -> None:
        """Disconnect from both adapters."""
        try:
            await self.primary.disconnect(dashboard_id)
        except Exception as e:
            self.logger.error(f"Primary adapter disconnect failed: {e}")
        
        try:
            await self.secondary.disconnect(dashboard_id)
        except Exception as e:
            self.logger.error(f"Secondary adapter disconnect failed: {e}")
    
    async def broadcast_event(self, event) -> None:
        """Broadcast to both adapters."""
        try:
            await self.primary.broadcast_event(event)
            self._metrics['primary_events'] += 1
        except Exception as e:
            self.logger.error(f"Primary broadcast failed: {e}")
            self._metrics['primary_failures'] += 1
        
        try:
            await self.secondary.broadcast_event(event)
            self._metrics['secondary_events'] += 1
        except Exception as e:
            self.logger.error(f"Secondary broadcast failed: {e}")
            self._metrics['secondary_failures'] += 1
    
    async def broadcast_batch(self, events) -> None:
        """Broadcast batch to both adapters."""
        try:
            await self.primary.broadcast_batch(events)
            self._metrics['primary_events'] += len(events)
        except Exception as e:
            self.logger.error(f"Primary batch broadcast failed: {e}")
            self._metrics['primary_failures'] += 1
        
        try:
            await self.secondary.broadcast_batch(events)
            self._metrics['secondary_events'] += len(events)
        except Exception as e:
            self.logger.error(f"Secondary batch broadcast failed: {e}")
            self._metrics['secondary_failures'] += 1
    
    async def get_connection_count(self) -> int:
        """Get connection count from primary adapter."""
        return await self.primary.get_connection_count()
    
    async def get_metrics(self):
        """Get metrics from both adapters."""
        return {
            'adapter_type': 'dual',
            'primary': await self.primary.get_metrics(),
            'secondary': await self.secondary.get_metrics(),
            'dual_metrics': self._metrics,
        }
    
    async def health_check(self) -> bool:
        """Check health of both adapters."""
        primary_health = await self.primary.health_check()
        secondary_health = await self.secondary.health_check()
        
        # Dual adapter is healthy if at least one adapter is healthy
        return primary_health or secondary_health

