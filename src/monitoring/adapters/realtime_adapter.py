"""
Supabase Realtime Monitoring Adapter

Implements monitoring via Supabase Realtime subscriptions.

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from supabase import create_client, Client

from .base import Connection, MonitoringAdapter, UnifiedMonitoringEvent
from ..validation import EventValidator, ValidationMetrics

logger = logging.getLogger(__name__)


class RealtimeAdapter(MonitoringAdapter):
    """
    Adapter for Supabase Realtime monitoring.
    
    Broadcasts monitoring events via Supabase Realtime subscriptions,
    allowing for scalable, persistent monitoring infrastructure.
    """
    
    def __init__(self):
        """Initialize Supabase Realtime adapter."""
        super().__init__('realtime')

        # Initialize Supabase client
        self.supabase_url = os.getenv('SUPABASE_URL', '')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

        self._supabase: Optional[Client] = None
        self._connections: Dict[str, Connection] = {}
        self._subscriptions: Dict[str, Any] = {}

        # Initialize validation framework
        self._validation_metrics = ValidationMetrics()
        self._validator = EventValidator(metrics=self._validation_metrics)
        self._enable_validation = os.getenv('MONITORING_ENABLE_VALIDATION', 'true').lower() == 'true'

        self._metrics = {
            'total_connections': 0,
            'active_connections': 0,
            'total_events_broadcast': 0,
            'failed_broadcasts': 0,
            'supabase_errors': 0,
            'validation_errors': 0,
        }
        
        self._initialize_supabase()
    
    def _initialize_supabase(self) -> None:
        """Initialize Supabase client."""
        if not self.supabase_url or not self.supabase_key:
            self.logger.warning("Supabase credentials not configured")
            return
        
        try:
            self._supabase = create_client(self.supabase_url, self.supabase_key)
            self.logger.info("Supabase Realtime adapter initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Supabase client: {e}")
            self._metrics['supabase_errors'] += 1
    
    async def connect(self, dashboard_id: str) -> Connection:
        """
        Establish a Realtime subscription for a dashboard.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
            
        Returns:
            Connection object
        """
        if not self._supabase:
            raise ConnectionError("Supabase client not initialized")
        
        try:
            # Create a subscription to the monitoring_events table in monitoring schema
            subscription = self._supabase.realtime.on(
                'postgres_changes',
                {
                    'event': '*',
                    'schema': 'monitoring',
                    'table': 'monitoring_events',
                },
                lambda payload: self._handle_realtime_event(dashboard_id, payload)
            ).subscribe()
            
            self._subscriptions[dashboard_id] = subscription
            
            connection = Connection(
                connection_id=dashboard_id,
                adapter_type='realtime',
                connected_at=datetime.utcnow(),
                metadata={'dashboard_id': dashboard_id, 'subscription_id': id(subscription)}
            )
            
            self._connections[dashboard_id] = connection
            self._metrics['total_connections'] += 1
            self._metrics['active_connections'] = len(self._connections)
            
            self.logger.info(f"Realtime connection established: {dashboard_id}")
            return connection
            
        except Exception as e:
            self.logger.error(f"Failed to establish Realtime connection: {e}")
            self._metrics['supabase_errors'] += 1
            raise ConnectionError(f"Realtime connection failed: {e}")
    
    async def disconnect(self, dashboard_id: str) -> None:
        """
        Close a Realtime subscription.
        
        Args:
            dashboard_id: Unique identifier for the dashboard client
        """
        try:
            if dashboard_id in self._subscriptions:
                subscription = self._subscriptions[dashboard_id]
                self._supabase.realtime.unsubscribe(subscription)
                del self._subscriptions[dashboard_id]
            
            if dashboard_id in self._connections:
                del self._connections[dashboard_id]
                self._metrics['active_connections'] = len(self._connections)
            
            self.logger.info(f"Realtime connection closed: {dashboard_id}")
            
        except Exception as e:
            self.logger.error(f"Error closing Realtime connection: {e}")
            self._metrics['supabase_errors'] += 1
    
    async def broadcast_event(self, event: UnifiedMonitoringEvent) -> None:
        """
        Broadcast a monitoring event via Realtime.

        Args:
            event: Unified monitoring event to broadcast
        """
        if not self._supabase:
            self.logger.warning("Supabase client not initialized, skipping broadcast")
            return

        try:
            # Prepare event data
            event_data = {
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'source': event.source,
                'data': event.data,
                'metadata': event.metadata,
            }

            # Validate event if validation is enabled
            if self._enable_validation:
                validation_result = self._validator.validate(event_data)
                if not validation_result['is_valid']:
                    self.logger.warning(
                        f"Event validation failed for {event.event_type}: "
                        f"{len(validation_result['errors'])} errors"
                    )
                    self._metrics['validation_errors'] += 1
                    # Continue anyway - don't block on validation errors
                    # In production, you might want to send to dead-letter queue

            # Try multiple approaches to insert into monitoring schema
            # Approach 1: Try RPC function (if it exists)
            try:
                result = self._supabase.rpc(
                    'insert_monitoring_event',
                    event_data
                ).execute()
                self._metrics['total_events_broadcast'] += 1
                self.logger.debug(f"[REALTIME] Event broadcast via RPC: {event.event_type}")
                return
            except Exception as rpc_error:
                # RPC function doesn't exist, try next approach
                pass

            # Approach 2: Try public view (if it exists)
            try:
                result = self._supabase.table('monitoring_events_view').insert(event_data).execute()
                self._metrics['total_events_broadcast'] += 1
                self.logger.debug(f"[REALTIME] Event broadcast via view: {event.event_type}")
                return
            except Exception as view_error:
                # View doesn't exist, try next approach
                pass

            # Approach 3: Direct insert to monitoring_events table (fallback)
            # This will fail but log the error for debugging
            try:
                result = self._supabase.table('monitoring_events').insert(event_data).execute()
                self._metrics['total_events_broadcast'] += 1
                self.logger.debug(f"[REALTIME] Event broadcast direct: {event.event_type}")
                return
            except Exception as direct_error:
                # All approaches failed
                self.logger.error(f"All broadcast approaches failed:")
                self.logger.error(f"  RPC: {str(rpc_error)[:100]}")
                self.logger.error(f"  View: {str(view_error)[:100]}")
                self.logger.error(f"  Direct: {str(direct_error)[:100]}")
                self._metrics['failed_broadcasts'] += 1
                self._metrics['supabase_errors'] += 1

        except Exception as e:
            self.logger.error(f"Error broadcasting Realtime event: {e}")
            self._metrics['failed_broadcasts'] += 1
            self._metrics['supabase_errors'] += 1
    
    async def broadcast_batch(self, events: List[UnifiedMonitoringEvent]) -> None:
        """
        Broadcast multiple events efficiently.

        Args:
            events: List of unified monitoring events
        """
        if not self._supabase:
            return

        try:
            # Prepare batch data
            batch_data = [
                {
                    'event_type': event.event_type,
                    'timestamp': event.timestamp.isoformat(),
                    'source': event.source,
                    'data': event.data,
                    'metadata': event.metadata,
                }
                for event in events
            ]

            # Validate batch if validation is enabled
            if self._enable_validation:
                validation_result = self._validator.validate_batch(batch_data)
                if validation_result['invalid_events'] > 0:
                    self.logger.warning(
                        f"Batch validation: {validation_result['valid_events']} valid, "
                        f"{validation_result['invalid_events']} invalid out of "
                        f"{validation_result['total_events']} events"
                    )
                    self._metrics['validation_errors'] += validation_result['invalid_events']
                    # Continue anyway - don't block on validation errors

            # Try multiple approaches
            # Approach 1: Try RPC batch function
            try:
                result = self._supabase.rpc(
                    'insert_monitoring_events_batch',
                    {'p_events': batch_data}
                ).execute()
                self._metrics['total_events_broadcast'] += len(events)
                self.logger.debug(f"[REALTIME] Batch broadcast via RPC: {len(events)} events")
                return
            except Exception:
                pass

            # Approach 2: Try public view
            try:
                result = self._supabase.table('monitoring_events_view').insert(batch_data).execute()
                self._metrics['total_events_broadcast'] += len(events)
                self.logger.debug(f"[REALTIME] Batch broadcast via view: {len(events)} events")
                return
            except Exception:
                pass

            # Approach 3: Direct insert (fallback)
            try:
                result = self._supabase.table('monitoring_events').insert(batch_data).execute()
                self._metrics['total_events_broadcast'] += len(events)
                self.logger.debug(f"[REALTIME] Batch broadcast direct: {len(events)} events")
                return
            except Exception as e:
                self.logger.error(f"Error broadcasting Realtime batch: {e}")
                self._metrics['failed_broadcasts'] += 1
                self._metrics['supabase_errors'] += 1

        except Exception as e:
            self.logger.error(f"Error preparing batch: {e}")
            self._metrics['failed_broadcasts'] += 1
            self._metrics['supabase_errors'] += 1
    
    async def get_connection_count(self) -> int:
        """Get the number of active Realtime connections."""
        return len(self._connections)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get Realtime adapter metrics."""
        return {
            'adapter_type': 'realtime',
            'total_connections': self._metrics['total_connections'],
            'active_connections': self._metrics['active_connections'],
            'total_events_broadcast': self._metrics['total_events_broadcast'],
            'failed_broadcasts': self._metrics['failed_broadcasts'],
            'supabase_errors': self._metrics['supabase_errors'],
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    async def health_check(self) -> bool:
        """Check if Realtime adapter is healthy."""
        if not self._supabase:
            return False

        try:
            # Try a simple RPC call to verify connection to monitoring schema
            self._supabase.rpc('get_monitoring_events', {'p_limit': 1}).execute()
            return True
        except Exception as e:
            self.logger.warning(f"Realtime health check failed: {e}")
            return False
    
    def _handle_realtime_event(self, dashboard_id: str, payload: Dict[str, Any]) -> None:
        """
        Handle incoming Realtime events.
        
        Args:
            dashboard_id: Dashboard that received the event
            payload: Realtime event payload
        """
        self.logger.debug(f"Received Realtime event for {dashboard_id}: {payload.get('type')}")

