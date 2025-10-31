"""
Monitoring Adapters - Phase 2 Supabase Realtime Migration

This package provides adapter implementations for different monitoring backends:
- WebSocket adapter (current system)
- Supabase Realtime adapter (new system)

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Supabase Realtime Migration
"""

from .base import MonitoringAdapter, UnifiedMonitoringEvent
from .websocket_adapter import WebSocketAdapter
from .realtime_adapter import RealtimeAdapter
from .factory import MonitoringAdapterFactory

__all__ = [
    'MonitoringAdapter',
    'UnifiedMonitoringEvent',
    'WebSocketAdapter',
    'RealtimeAdapter',
    'MonitoringAdapterFactory',
]

