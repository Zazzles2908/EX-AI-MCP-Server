"""
Integration tests for Broadcaster with Event Classifier

Tests that the broadcaster correctly integrates event classification
and that adapters handle the new fields.

Date: 2025-11-01
Phase: Phase 2.6.1 - Event Classification System
"""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.monitoring.broadcaster import MonitoringBroadcaster
from src.monitoring.adapters.base import UnifiedMonitoringEvent
from src.monitoring.event_classifier import EventCategory


@pytest.fixture
def broadcaster():
    """Create a broadcaster instance for testing."""
    return MonitoringBroadcaster()


class TestBroadcasterEventClassification:
    """Test broadcaster integration with event classifier."""
    
    @pytest.mark.asyncio
    async def test_broadcast_event_creates_classified_event(self, broadcaster):
        """Test that broadcast_event creates a classified event."""
        # Mock the adapter
        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True
        
        # Broadcast an event
        await broadcaster.broadcast_event('cache_metrics', {'hits': 100})
        
        # Verify adapter was called
        broadcaster.adapter.broadcast_event.assert_called_once()
        
        # Get the event that was passed
        call_args = broadcaster.adapter.broadcast_event.call_args
        event = call_args[0][0]
        
        # Verify event has classification
        assert isinstance(event, UnifiedMonitoringEvent)
        assert event.category == 'performance'
        assert event.sequence_id == 1
    
    @pytest.mark.asyncio
    async def test_broadcast_batch_creates_classified_events(self, broadcaster):
        """Test that broadcast_batch creates classified events."""
        # Mock the adapter
        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True
        
        # Broadcast batch
        events = [
            ('cache_metrics', {'hits': 100}),
            ('session_metrics', {'active': 5}),
            ('health_check', {'status': 'ok'}),
        ]
        await broadcaster.broadcast_batch(events)
        
        # Verify adapter was called
        broadcaster.adapter.broadcast_batch.assert_called_once()
        
        # Get the events that were passed
        call_args = broadcaster.adapter.broadcast_batch.call_args
        unified_events = call_args[0][0]
        
        # Verify all events have classification and sequence IDs
        assert len(unified_events) == 3
        assert unified_events[0].category == 'performance'
        assert unified_events[1].category == 'user_activity'
        assert unified_events[2].category == 'critical'
        
        # Verify sequence IDs are sequential
        assert unified_events[0].sequence_id == 1
        assert unified_events[1].sequence_id == 2
        assert unified_events[2].sequence_id == 3
    
    @pytest.mark.asyncio
    async def test_sequence_counter_increments(self, broadcaster):
        """Test that sequence counter increments correctly."""
        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True
        
        # Broadcast multiple events
        for i in range(5):
            await broadcaster.broadcast_event('test_event', {'index': i})
        
        # Verify sequence counter
        assert broadcaster._sequence_counter == 5
    
    @pytest.mark.asyncio
    async def test_classification_metrics_tracked(self, broadcaster):
        """Test that classification metrics are tracked."""
        # Reset metrics before test
        broadcaster._classifier.reset_metrics()

        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True

        # Broadcast events of different types
        await broadcaster.broadcast_event('cache_metrics', {})
        await broadcaster.broadcast_event('cache_metrics', {})
        await broadcaster.broadcast_event('session_metrics', {})

        # Get metrics
        metrics = await broadcaster.get_metrics()

        # Verify classification metrics
        assert 'classification_metrics' in metrics
        classification_metrics = metrics['classification_metrics']
        assert classification_metrics['total_classified'] == 3
        assert classification_metrics['category_distribution']['performance'] == 2
        assert classification_metrics['category_distribution']['user_activity'] == 1


class TestUnifiedMonitoringEventSerialization:
    """Test that UnifiedMonitoringEvent serializes correctly with new fields."""
    
    def test_event_to_dict_includes_category(self):
        """Test that to_dict includes category."""
        event = UnifiedMonitoringEvent(
            event_type='cache_metrics',
            timestamp=datetime.utcnow(),
            source='test',
            data={'hits': 100},
            category='performance',
            sequence_id=1
        )
        
        event_dict = event.to_dict()
        
        assert 'category' in event_dict
        assert event_dict['category'] == 'performance'
    
    def test_event_to_dict_includes_sequence_id(self):
        """Test that to_dict includes sequence_id."""
        event = UnifiedMonitoringEvent(
            event_type='cache_metrics',
            timestamp=datetime.utcnow(),
            source='test',
            data={'hits': 100},
            category='performance',
            sequence_id=42
        )
        
        event_dict = event.to_dict()
        
        assert 'sequence_id' in event_dict
        assert event_dict['sequence_id'] == 42
    
    def test_event_to_dict_without_category(self):
        """Test that to_dict works without category (backward compatibility)."""
        event = UnifiedMonitoringEvent(
            event_type='cache_metrics',
            timestamp=datetime.utcnow(),
            source='test',
            data={'hits': 100}
        )
        
        event_dict = event.to_dict()
        
        # Should not include category if None
        assert 'category' not in event_dict
    
    def test_event_to_dict_without_sequence_id(self):
        """Test that to_dict works without sequence_id (backward compatibility)."""
        event = UnifiedMonitoringEvent(
            event_type='cache_metrics',
            timestamp=datetime.utcnow(),
            source='test',
            data={'hits': 100}
        )
        
        event_dict = event.to_dict()
        
        # Should not include sequence_id if None
        assert 'sequence_id' not in event_dict


class TestAdapterCompatibility:
    """Test that adapters handle new event fields."""
    
    @pytest.mark.asyncio
    async def test_websocket_adapter_handles_classified_events(self):
        """Test that WebSocket adapter handles classified events."""
        from src.monitoring.adapters.websocket_adapter import WebSocketAdapter

        adapter = WebSocketAdapter()
        
        # Create a classified event
        event = UnifiedMonitoringEvent(
            event_type='cache_metrics',
            timestamp=datetime.utcnow(),
            source='test',
            data={'hits': 100},
            category='performance',
            sequence_id=1
        )
        
        # Mock a client
        mock_client = AsyncMock()
        adapter._dashboard_clients.add(mock_client)
        
        # Broadcast the event
        await adapter.broadcast_event(event)
        
        # Verify client received the event
        mock_client.send_str.assert_called_once()
        
        # Verify the event data includes classification
        call_args = mock_client.send_str.call_args
        import json
        event_data = json.loads(call_args[0][0])
        assert event_data['category'] == 'performance'
        assert event_data['sequence_id'] == 1
    
    @pytest.mark.asyncio
    async def test_realtime_adapter_handles_classified_events(self):
        """Test that Realtime adapter handles classified events."""
        from src.monitoring.adapters.realtime_adapter import RealtimeAdapter

        # Create adapter with mocked Supabase client
        with patch('src.monitoring.adapters.realtime_adapter.create_client'):
            adapter = RealtimeAdapter()
            adapter._supabase = MagicMock()
            
            # Create a classified event
            event = UnifiedMonitoringEvent(
                event_type='cache_metrics',
                timestamp=datetime.utcnow(),
                source='test',
                data={'hits': 100},
                category='performance',
                sequence_id=1
            )
            
            # Mock the RPC call
            adapter._supabase.rpc = MagicMock(return_value=MagicMock(execute=MagicMock()))
            
            # Broadcast the event
            await adapter.broadcast_event(event)
            
            # Verify RPC was called with event data including classification
            adapter._supabase.rpc.assert_called()


class TestBroadcasterMetrics:
    """Test broadcaster metrics collection."""
    
    @pytest.mark.asyncio
    async def test_get_classification_metrics(self, broadcaster):
        """Test get_classification_metrics method."""
        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True
        
        # Broadcast some events
        await broadcaster.broadcast_event('cache_metrics', {})
        await broadcaster.broadcast_event('session_metrics', {})
        
        # Get classification metrics
        metrics = broadcaster.get_classification_metrics()
        
        assert 'sequence_counter' in metrics
        assert 'classification_metrics' in metrics
        assert metrics['sequence_counter'] == 2
    
    @pytest.mark.asyncio
    async def test_flush_metrics_includes_classification(self, broadcaster):
        """Test that flush_metrics includes classification metrics."""
        broadcaster.adapter = AsyncMock()
        broadcaster._use_adapter = True
        
        # Broadcast an event
        await broadcaster.broadcast_event('cache_metrics', {})
        
        # Flush metrics
        result = await broadcaster.flush_metrics()
        
        assert result['flushed'] is True
        assert 'classification_metrics' in result
        assert 'broadcaster_metrics' in result

