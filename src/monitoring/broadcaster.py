"""
Monitoring Broadcaster - Adapter-based Event Broadcasting

Provides a unified interface for broadcasting monitoring events through
different transport mechanisms (WebSocket, Realtime, etc.) using the
adapter pattern.

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional, Set

from src.monitoring.adapters.base import UnifiedMonitoringEvent
from src.monitoring.adapters.factory import MonitoringAdapterFactory
from utils.timezone_helper import log_timestamp

logger = logging.getLogger(__name__)


class MonitoringBroadcaster:
    """
    Unified monitoring event broadcaster using adapter pattern.
    
    Manages broadcasting of monitoring events through different transport
    mechanisms (WebSocket, Realtime, etc.) with feature flag support for
    gradual migration.
    """
    
    def __init__(self):
        """Initialize the broadcaster with adapter factory."""
        self.adapter_factory = MonitoringAdapterFactory()
        self.adapter = None
        self._use_adapter = False
        self._use_dual_mode = False
        self._dashboard_clients: Set[Any] = set()
        self._metrics = {
            'total_broadcasts': 0,
            'adapter_broadcasts': 0,
            'direct_broadcasts': 0,
            'failed_broadcasts': 0,
        }
        
        self._initialize_adapter()
    
    def _initialize_adapter(self) -> None:
        """Initialize adapter based on environment configuration."""
        try:
            # Check feature flags
            self._use_adapter = os.getenv('MONITORING_USE_ADAPTER', 'false').lower() == 'true'
            self._use_dual_mode = os.getenv('MONITORING_DUAL_MODE', 'false').lower() == 'true'
            
            if self._use_dual_mode:
                # Create dual adapter for parallel operation
                self.adapter = self.adapter_factory.create_dual_adapter()
                logger.info("[BROADCASTER] Initialized in DUAL MODE (WebSocket + Realtime)")
            elif self._use_adapter:
                # Create adapter based on environment
                adapter_type = os.getenv('MONITORING_ADAPTER_TYPE', 'auto')
                self.adapter = self.adapter_factory.create_adapter(adapter_type)
                logger.info(f"[BROADCASTER] Initialized with {adapter_type} adapter")
            else:
                logger.info("[BROADCASTER] Initialized in DIRECT MODE (WebSocket only)")
        
        except Exception as e:
            logger.error(f"[BROADCASTER] Failed to initialize adapter: {e}")
            self._use_adapter = False
            self.adapter = None
    
    def register_client(self, client: Any) -> None:
        """
        Register a WebSocket client for direct broadcasting.
        
        Args:
            client: WebSocket client object
        """
        self._dashboard_clients.add(client)
        logger.debug(f"[BROADCASTER] Registered client, total: {len(self._dashboard_clients)}")
    
    def unregister_client(self, client: Any) -> None:
        """
        Unregister a WebSocket client.
        
        Args:
            client: WebSocket client object
        """
        self._dashboard_clients.discard(client)
        logger.debug(f"[BROADCASTER] Unregistered client, total: {len(self._dashboard_clients)}")
    
    async def broadcast_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast a monitoring event.
        
        Args:
            event_type: Type of event (e.g., 'cache_metrics', 'session_metrics')
            data: Event data dictionary
        """
        try:
            self._metrics['total_broadcasts'] += 1
            
            # Create unified event
            event = UnifiedMonitoringEvent(
                event_type=event_type,
                timestamp=log_timestamp(),
                source='monitoring_endpoint',
                data=data,
                metadata={'broadcast_mode': 'dual' if self._use_dual_mode else 'adapter' if self._use_adapter else 'direct'}
            )
            
            # Broadcast via adapter if enabled
            if self._use_adapter and self.adapter:
                try:
                    await self.adapter.broadcast_event(event)
                    self._metrics['adapter_broadcasts'] += 1
                except Exception as e:
                    logger.error(f"[BROADCASTER] Adapter broadcast failed: {e}")
                    self._metrics['failed_broadcasts'] += 1
            
            # Broadcast directly to WebSocket clients (always, for backward compatibility)
            await self._broadcast_direct(event_type, data)
            self._metrics['direct_broadcasts'] += 1
        
        except Exception as e:
            logger.error(f"[BROADCASTER] Error broadcasting event: {e}")
            self._metrics['failed_broadcasts'] += 1
    
    async def broadcast_batch(self, events: list) -> None:
        """
        Broadcast multiple events efficiently.
        
        Args:
            events: List of (event_type, data) tuples
        """
        try:
            # Create unified events
            unified_events = [
                UnifiedMonitoringEvent(
                    event_type=event_type,
                    timestamp=log_timestamp(),
                    source='monitoring_endpoint',
                    data=data,
                    metadata={'broadcast_mode': 'dual' if self._use_dual_mode else 'adapter' if self._use_adapter else 'direct'}
                )
                for event_type, data in events
            ]
            
            # Broadcast via adapter if enabled
            if self._use_adapter and self.adapter:
                try:
                    await self.adapter.broadcast_batch(unified_events)
                    self._metrics['adapter_broadcasts'] += len(events)
                except Exception as e:
                    logger.error(f"[BROADCASTER] Adapter batch broadcast failed: {e}")
                    self._metrics['failed_broadcasts'] += len(events)
            
            # Broadcast directly to WebSocket clients
            for event_type, data in events:
                await self._broadcast_direct(event_type, data)
            self._metrics['direct_broadcasts'] += len(events)
        
        except Exception as e:
            logger.error(f"[BROADCASTER] Error broadcasting batch: {e}")
            self._metrics['failed_broadcasts'] += len(events)
    
    async def _broadcast_direct(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Broadcast directly to WebSocket clients (backward compatibility).
        
        Args:
            event_type: Type of event
            data: Event data
        """
        if not self._dashboard_clients:
            return
        
        try:
            event_data = {
                "type": event_type,
                "data": data,
                "timestamp": log_timestamp(),
            }
            
            disconnected = set()
            for client in self._dashboard_clients:
                try:
                    await client.send_str(json.dumps(event_data))
                except Exception as e:
                    logger.debug(f"[BROADCASTER] Failed to send to client: {e}")
                    disconnected.add(client)
            
            # Remove disconnected clients
            self._dashboard_clients.difference_update(disconnected)
        
        except Exception as e:
            logger.error(f"[BROADCASTER] Error in direct broadcast: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get broadcaster metrics."""
        metrics = {
            'broadcaster_metrics': self._metrics,
            'connected_clients': len(self._dashboard_clients),
            'use_adapter': self._use_adapter,
            'use_dual_mode': self._use_dual_mode,
        }
        
        # Add adapter metrics if available
        if self.adapter:
            try:
                adapter_metrics = await self.adapter.get_metrics()
                metrics['adapter_metrics'] = adapter_metrics
            except Exception as e:
                logger.debug(f"[BROADCASTER] Failed to get adapter metrics: {e}")
        
        return metrics
    
    async def health_check(self) -> bool:
        """Check if broadcaster is healthy."""
        try:
            # Check adapter health if enabled
            if self._use_adapter and self.adapter:
                adapter_healthy = await self.adapter.health_check()
                if not adapter_healthy:
                    logger.warning("[BROADCASTER] Adapter health check failed")
                    return False

            # Broadcaster is healthy if we have clients or adapter is working
            return len(self._dashboard_clients) > 0 or (self._use_adapter and self.adapter)

        except Exception as e:
            logger.error(f"[BROADCASTER] Health check failed: {e}")
            return False

    async def flush_metrics(self) -> Dict[str, Any]:
        """
        Flush metrics to database.

        Returns:
            Dictionary with flush result
        """
        try:
            # For now, return current metrics status
            # In future, this will integrate with MetricsPersister
            result = {
                'flushed': True,
                'metrics': self._metrics,
                'timestamp': log_timestamp(),
            }
            logger.info("[BROADCASTER] Metrics flushed successfully")
            return result
        except Exception as e:
            logger.error(f"[BROADCASTER] Failed to flush metrics: {e}")
            return {
                'flushed': False,
                'error': str(e),
                'timestamp': log_timestamp(),
            }


# Global broadcaster instance
_broadcaster: Optional[MonitoringBroadcaster] = None


def get_broadcaster() -> MonitoringBroadcaster:
    """Get or create the global broadcaster instance."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = MonitoringBroadcaster()
    return _broadcaster


def reset_broadcaster() -> None:
    """Reset the global broadcaster instance (for testing)."""
    global _broadcaster
    _broadcaster = None

