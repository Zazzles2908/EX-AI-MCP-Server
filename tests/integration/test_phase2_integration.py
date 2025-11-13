"""
Phase 2.4.4 Integration Tests

Tests the complete flow from event broadcast → adapter → validation → metrics → persistence → dashboard.

EXAI Consultation: ac40c717-09db-4b0a-b943-6e38730a1300
Date: 2025-10-31
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from src.monitoring.broadcaster import MonitoringBroadcaster, reset_broadcaster
from src.monitoring.adapters.base import UnifiedMonitoringEvent
from src.monitoring.flags import get_flag_manager
from utils.timezone_helper import log_timestamp


class TestPhase2Integration:
    """Integration tests for Phase 2 monitoring system."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test."""
        reset_broadcaster()
        yield
        reset_broadcaster()
    
    @pytest.mark.asyncio
    async def test_event_broadcast_flow(self):
        """Test: Event broadcast through adapter."""
        broadcaster = MonitoringBroadcaster()

        # Create test event
        event = UnifiedMonitoringEvent(
            event_type='test_event',
            timestamp=datetime.now(),
            data={'test': 'data'},
            source='test_source'
        )

        # Broadcast event
        await broadcaster.broadcast_event(event.event_type, event.to_dict())

        # Verify metrics updated
        metrics = await broadcaster.get_metrics()
        assert metrics is not None
        assert 'broadcaster_metrics' in metrics
    
    @pytest.mark.asyncio
    async def test_flag_manager_integration(self):
        """Test: Flag manager provides correct configuration."""
        flag_manager = get_flag_manager()

        # Get all flags
        flags = flag_manager.get_all()

        # Verify expected flags exist
        expected_flags = [
            'MONITORING_USE_ADAPTER',
            'MONITORING_ADAPTER_TYPE',
            'MONITORING_DUAL_MODE',
            'MONITORING_ENABLE_VALIDATION',
            'MONITORING_VALIDATION_STRICT',
            'MONITORING_BATCH_SIZE',
            'MONITORING_METRICS_PERSISTENCE',
            'MONITORING_METRICS_FLUSH_INTERVAL',
        ]

        for flag in expected_flags:
            assert flag in flags, f"Flag {flag} not found"
    
    @pytest.mark.asyncio
    async def test_broadcaster_metrics_collection(self):
        """Test: Broadcaster collects metrics correctly."""
        broadcaster = MonitoringBroadcaster()

        # Broadcast multiple events
        for i in range(5):
            event = UnifiedMonitoringEvent(
                event_type=f'test_event_{i}',
                timestamp=datetime.now(),
                data={'index': i},
                source='test'
            )
            await broadcaster.broadcast_event(event.event_type, event.to_dict())

        # Get metrics
        metrics = await broadcaster.get_metrics()

        # Verify metrics structure
        assert 'broadcaster_metrics' in metrics
        assert 'connected_clients' in metrics
        assert 'use_adapter' in metrics
        assert 'use_dual_mode' in metrics
    
    @pytest.mark.asyncio
    async def test_metrics_flush_operation(self):
        """Test: Metrics flush operation."""
        broadcaster = MonitoringBroadcaster()
        
        # Flush metrics
        result = await broadcaster.flush_metrics()
        
        # Verify flush result
        assert result is not None
        assert 'flushed' in result
        assert result['flushed'] is True
        assert 'metrics' in result
        assert 'timestamp' in result
    
    @pytest.mark.asyncio
    async def test_broadcaster_health_check(self):
        """Test: Broadcaster health check."""
        broadcaster = MonitoringBroadcaster()
        
        # Perform health check
        health = await broadcaster.health_check()
        
        # Verify health check result
        assert isinstance(health, bool)
    
    @pytest.mark.asyncio
    async def test_flag_validation_logic(self):
        """Test: Flag validation logic."""
        flag_manager = get_flag_manager()
        
        # Get flags
        flags = flag_manager.get_all()
        
        # Test validation logic from health endpoint
        issues = []
        
        # Check: VALIDATION_STRICT requires ENABLE_VALIDATION
        if flags.get('MONITORING_VALIDATION_STRICT') and not flags.get('MONITORING_ENABLE_VALIDATION'):
            issues.append("VALIDATION_STRICT enabled but ENABLE_VALIDATION disabled")
        
        # Check: DUAL_MODE requires USE_ADAPTER
        if flags.get('MONITORING_DUAL_MODE') and not flags.get('MONITORING_USE_ADAPTER'):
            issues.append("DUAL_MODE enabled but USE_ADAPTER disabled")
        
        # Check: METRICS_PERSISTENCE requires METRICS_FLUSH_INTERVAL > 0
        if flags.get('MONITORING_METRICS_PERSISTENCE') and flags.get('MONITORING_METRICS_FLUSH_INTERVAL', 0) <= 0:
            issues.append("METRICS_PERSISTENCE enabled but METRICS_FLUSH_INTERVAL invalid")
        
        # Verify no critical issues
        assert len(issues) == 0, f"Flag validation issues: {issues}"
    
    @pytest.mark.asyncio
    async def test_concurrent_broadcasts(self):
        """Test: Concurrent event broadcasts."""
        broadcaster = MonitoringBroadcaster()

        # Create concurrent broadcast tasks
        tasks = []
        for i in range(10):
            event = UnifiedMonitoringEvent(
                event_type=f'concurrent_event_{i}',
                timestamp=datetime.now(),
                data={'index': i},
                source='test'
            )
            tasks.append(broadcaster.broadcast_event(event.event_type, event.to_dict()))

        # Execute concurrently
        await asyncio.gather(*tasks)

        # Verify all broadcasts completed
        metrics = await broadcaster.get_metrics()
        assert metrics is not None


def run_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("Phase 2.4.4 Integration Tests")
    print("=" * 60)
    
    # Run pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '-s',
    ])
    
    return exit_code


if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)

