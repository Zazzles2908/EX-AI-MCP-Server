"""
Unit Tests for Monitoring Broadcaster and Adapters

Tests the MonitoringBroadcaster class and adapter integration.

EXAI Consultation: 7355be09-5a88-4958-9293-6bf9391e6745
Date: 2025-11-01
Phase: Phase 2 - Testing & Validation
"""

import asyncio
import json
import os
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

# Import modules to test
from src.monitoring.broadcaster import MonitoringBroadcaster, get_broadcaster, reset_broadcaster
from src.monitoring.adapters.base import UnifiedMonitoringEvent, MonitoringAdapter
from src.monitoring.adapters.websocket_adapter import WebSocketAdapter
from src.monitoring.adapters.factory import MonitoringAdapterFactory


class TestMonitoringBroadcaster:
    """Test suite for MonitoringBroadcaster class."""
    
    @pytest.fixture
    def broadcaster(self):
        """Create a fresh broadcaster instance for each test."""
        reset_broadcaster()
        return get_broadcaster()
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock WebSocket client."""
        client = AsyncMock()
        client.send_str = AsyncMock()
        return client
    
    def test_broadcaster_initialization(self, broadcaster):
        """Test broadcaster initializes correctly."""
        assert broadcaster is not None
        assert broadcaster._dashboard_clients is not None
        assert isinstance(broadcaster._metrics, dict)
        assert broadcaster._metrics['total_broadcasts'] == 0
    
    def test_client_registration(self, broadcaster, mock_client):
        """Test client registration and unregistration."""
        # Register client
        broadcaster.register_client(mock_client)
        assert mock_client in broadcaster._dashboard_clients
        assert len(broadcaster._dashboard_clients) == 1
        
        # Unregister client
        broadcaster.unregister_client(mock_client)
        assert mock_client not in broadcaster._dashboard_clients
        assert len(broadcaster._dashboard_clients) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast_event_direct_mode(self, broadcaster, mock_client):
        """Test broadcasting in direct mode (WebSocket only)."""
        broadcaster.register_client(mock_client)
        
        # Broadcast event
        await broadcaster.broadcast_event('test_event', {'data': 'test'})
        
        # Verify client received event
        mock_client.send_str.assert_called_once()
        call_args = mock_client.send_str.call_args[0][0]
        event_data = json.loads(call_args)
        
        assert event_data['type'] == 'test_event'
        assert event_data['data']['data'] == 'test'
        assert 'timestamp' in event_data
    
    @pytest.mark.asyncio
    async def test_broadcast_event_with_disconnected_client(self, broadcaster, mock_client):
        """Test broadcasting handles disconnected clients gracefully."""
        broadcaster.register_client(mock_client)
        
        # Simulate client disconnection
        mock_client.send_str.side_effect = Exception("Connection closed")
        
        # Broadcast should not raise exception
        await broadcaster.broadcast_event('test_event', {'data': 'test'})
        
        # Client should be removed from set
        assert mock_client not in broadcaster._dashboard_clients
    
    @pytest.mark.asyncio
    async def test_broadcast_batch(self, broadcaster, mock_client):
        """Test batch broadcasting."""
        broadcaster.register_client(mock_client)
        
        events = [
            ('event1', {'data': 'test1'}),
            ('event2', {'data': 'test2'}),
            ('event3', {'data': 'test3'}),
        ]
        
        await broadcaster.broadcast_batch(events)
        
        # Verify all events were sent
        assert mock_client.send_str.call_count == 3
    
    @pytest.mark.asyncio
    async def test_metrics_tracking(self, broadcaster, mock_client):
        """Test metrics are tracked correctly."""
        broadcaster.register_client(mock_client)
        
        # Broadcast events
        await broadcaster.broadcast_event('event1', {'data': 'test1'})
        await broadcaster.broadcast_event('event2', {'data': 'test2'})
        
        # Check metrics
        assert broadcaster._metrics['total_broadcasts'] == 2
        assert broadcaster._metrics['direct_broadcasts'] == 2
        assert broadcaster._metrics['adapter_broadcasts'] == 0
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, broadcaster, mock_client):
        """Test metrics retrieval."""
        broadcaster.register_client(mock_client)
        
        await broadcaster.broadcast_event('test_event', {'data': 'test'})
        
        metrics = await broadcaster.get_metrics()
        
        assert 'broadcaster_metrics' in metrics
        assert 'connected_clients' in metrics
        assert metrics['connected_clients'] == 1
        assert metrics['broadcaster_metrics']['total_broadcasts'] == 1
    
    @pytest.mark.asyncio
    async def test_health_check(self, broadcaster, mock_client):
        """Test health check."""
        # No clients - should be unhealthy
        assert await broadcaster.health_check() == False
        
        # With client - should be healthy
        broadcaster.register_client(mock_client)
        assert await broadcaster.health_check() == True
    
    def test_feature_flag_initialization(self):
        """Test feature flag initialization."""
        reset_broadcaster()
        
        # Test with adapter disabled (default)
        with patch.dict(os.environ, {'MONITORING_USE_ADAPTER': 'false'}):
            broadcaster = get_broadcaster()
            assert broadcaster._use_adapter == False
        
        reset_broadcaster()
        
        # Test with adapter enabled
        with patch.dict(os.environ, {'MONITORING_USE_ADAPTER': 'true'}):
            broadcaster = get_broadcaster()
            assert broadcaster._use_adapter == True
    
    def test_dual_mode_initialization(self):
        """Test dual mode initialization."""
        reset_broadcaster()
        
        with patch.dict(os.environ, {'MONITORING_DUAL_MODE': 'true'}):
            broadcaster = get_broadcaster()
            assert broadcaster._use_dual_mode == True


class TestWebSocketAdapter:
    """Test suite for WebSocketAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Create a WebSocket adapter instance."""
        return WebSocketAdapter()
    
    @pytest.mark.asyncio
    async def test_adapter_connect(self, adapter):
        """Test adapter connection."""
        connection = await adapter.connect('dashboard_1')
        
        assert connection is not None
        assert connection.connection_id == 'dashboard_1'
        assert connection.adapter_type == 'websocket'
    
    @pytest.mark.asyncio
    async def test_adapter_disconnect(self, adapter):
        """Test adapter disconnection."""
        await adapter.connect('dashboard_1')
        await adapter.disconnect('dashboard_1')
        
        assert len(await adapter.get_connection_count()) == 0
    
    @pytest.mark.asyncio
    async def test_adapter_metrics(self, adapter):
        """Test adapter metrics."""
        metrics = await adapter.get_metrics()
        
        assert 'adapter_type' in metrics
        assert metrics['adapter_type'] == 'websocket'
        assert 'active_connections' in metrics
    
    @pytest.mark.asyncio
    async def test_adapter_health_check(self, adapter):
        """Test adapter health check."""
        health = await adapter.health_check()
        assert health == True


class TestUnifiedMonitoringEvent:
    """Test suite for UnifiedMonitoringEvent."""
    
    def test_event_creation(self):
        """Test event creation."""
        event = UnifiedMonitoringEvent(
            event_type='test',
            timestamp=datetime.utcnow(),
            source='test_source',
            data={'key': 'value'}
        )
        
        assert event.event_type == 'test'
        assert event.source == 'test_source'
        assert event.data == {'key': 'value'}
    
    def test_event_to_dict(self):
        """Test event serialization."""
        now = datetime.utcnow()
        event = UnifiedMonitoringEvent(
            event_type='test',
            timestamp=now,
            source='test_source',
            data={'key': 'value'}
        )
        
        event_dict = event.to_dict()
        
        assert event_dict['event_type'] == 'test'
        assert event_dict['source'] == 'test_source'
        assert event_dict['data'] == {'key': 'value'}
        assert 'timestamp' in event_dict


class TestAdapterFactory:
    """Test suite for MonitoringAdapterFactory."""
    
    def test_factory_create_websocket_adapter(self):
        """Test factory creates WebSocket adapter."""
        adapter = MonitoringAdapterFactory.create_adapter('websocket')
        assert isinstance(adapter, WebSocketAdapter)
    
    def test_factory_singleton(self):
        """Test factory returns singleton instances."""
        adapter1 = MonitoringAdapterFactory.create_adapter('websocket')
        adapter2 = MonitoringAdapterFactory.create_adapter('websocket')
        
        assert adapter1 is adapter2
    
    def test_factory_clear_cache(self):
        """Test factory cache clearing."""
        adapter1 = MonitoringAdapterFactory.create_adapter('websocket')
        MonitoringAdapterFactory.clear_cache()
        adapter2 = MonitoringAdapterFactory.create_adapter('websocket')
        
        assert adapter1 is not adapter2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

