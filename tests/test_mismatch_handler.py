"""
Tests for Mismatch Handler

Tests for MismatchHandler, MismatchRecord, and mismatch tracking.
"""

import pytest
from src.monitoring.validation.mismatch_handler import (
    MismatchHandler,
    MismatchRecord,
    MismatchStats,
    MismatchSeverity,
    get_mismatch_handler,
)


class TestMismatchSeverity:
    """Test MismatchSeverity enum."""

    def test_severity_values(self):
        """Test severity enum values."""
        assert MismatchSeverity.LOW.value == "low"
        assert MismatchSeverity.MEDIUM.value == "medium"
        assert MismatchSeverity.HIGH.value == "high"
        assert MismatchSeverity.CRITICAL.value == "critical"


class TestMismatchHandler:
    """Test MismatchHandler functionality."""

    def setup_method(self):
        """Setup for each test."""
        MismatchHandler._instance = None

    def test_singleton_pattern(self):
        """Test MismatchHandler singleton pattern."""
        handler1 = MismatchHandler()
        handler2 = MismatchHandler()
        assert handler1 is handler2

    def test_get_mismatch_handler(self):
        """Test get_mismatch_handler function."""
        handler = get_mismatch_handler()
        assert isinstance(handler, MismatchHandler)

    def test_record_mismatch(self):
        """Test recording a mismatch."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc123',
            actual_checksum='def456',
            category='critical',
            error_message='Checksum mismatch',
        )
        
        assert record.event_type == 'test_event'
        assert record.sequence_id == 123
        assert record.adapter == 'websocket'
        assert record.expected_checksum == 'abc123'
        assert record.actual_checksum == 'def456'
        assert record.category == 'critical'
        assert record.severity == MismatchSeverity.CRITICAL

    def test_record_mismatch_updates_stats(self):
        """Test that recording mismatch updates statistics."""
        handler = MismatchHandler()
        
        handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc123',
            actual_checksum='def456',
            category='critical',
            error_message='Checksum mismatch',
        )
        
        stats = handler.get_stats()
        
        assert stats.total_mismatches == 1
        assert stats.mismatches_by_adapter['websocket'] == 1
        assert stats.mismatches_by_category['critical'] == 1
        assert stats.mismatches_by_severity['critical'] == 1

    def test_multiple_mismatches(self):
        """Test recording multiple mismatches."""
        handler = MismatchHandler()
        
        for i in range(5):
            handler.record_mismatch(
                event_type=f'event_{i}',
                sequence_id=i,
                adapter='websocket',
                expected_checksum=f'exp_{i}',
                actual_checksum=f'act_{i}',
                category='performance',
                error_message='Mismatch',
            )
        
        stats = handler.get_stats()
        
        assert stats.total_mismatches == 5
        assert stats.mismatches_by_adapter['websocket'] == 5
        assert stats.mismatches_by_category['performance'] == 5

    def test_mismatch_severity_critical(self):
        """Test mismatch severity for critical category."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=None,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='critical',
            error_message='Mismatch',
        )
        
        assert record.severity == MismatchSeverity.CRITICAL

    def test_mismatch_severity_performance(self):
        """Test mismatch severity for performance category."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=None,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='performance',
            error_message='Mismatch',
        )
        
        assert record.severity == MismatchSeverity.HIGH

    def test_mismatch_severity_user_activity(self):
        """Test mismatch severity for user_activity category."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=None,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='user_activity',
            error_message='Mismatch',
        )
        
        assert record.severity == MismatchSeverity.MEDIUM

    def test_mismatch_severity_system(self):
        """Test mismatch severity for system category."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=None,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='system',
            error_message='Mismatch',
        )
        
        assert record.severity == MismatchSeverity.LOW

    def test_should_trigger_circuit_breaker_no_mismatches(self):
        """Test circuit breaker trigger with no mismatches."""
        handler = MismatchHandler()
        
        result = handler.should_trigger_circuit_breaker('websocket')
        
        assert result is False

    def test_should_trigger_circuit_breaker_low_rate(self):
        """Test circuit breaker trigger with low mismatch rate."""
        handler = MismatchHandler()
        
        # Record 1 mismatch out of 100 total (1%)
        for i in range(100):
            handler.record_mismatch(
                event_type='test_event',
                sequence_id=i,
                adapter='websocket' if i == 0 else 'realtime',
                expected_checksum='abc',
                actual_checksum='def',
                category='performance',
                error_message='Mismatch',
            )
        
        result = handler.should_trigger_circuit_breaker('websocket')
        
        assert result is False

    def test_should_trigger_circuit_breaker_high_rate(self):
        """Test circuit breaker trigger with high mismatch rate."""
        handler = MismatchHandler()
        
        # Record 15 mismatches out of 100 total (15%)
        for i in range(100):
            handler.record_mismatch(
                event_type='test_event',
                sequence_id=i,
                adapter='websocket' if i < 15 else 'realtime',
                expected_checksum='abc',
                actual_checksum='def',
                category='performance',
                error_message='Mismatch',
            )
        
        result = handler.should_trigger_circuit_breaker('websocket')
        
        assert result is True

    def test_get_adapter_mismatch_rate(self):
        """Test getting adapter mismatch rate."""
        handler = MismatchHandler()
        
        # Record 10 mismatches for websocket, 5 for realtime
        for i in range(15):
            handler.record_mismatch(
                event_type='test_event',
                sequence_id=i,
                adapter='websocket' if i < 10 else 'realtime',
                expected_checksum='abc',
                actual_checksum='def',
                category='performance',
                error_message='Mismatch',
            )
        
        websocket_rate = handler.get_adapter_mismatch_rate('websocket')
        realtime_rate = handler.get_adapter_mismatch_rate('realtime')
        
        assert websocket_rate == pytest.approx(10/15)
        assert realtime_rate == pytest.approx(5/15)

    def test_get_category_mismatch_rate(self):
        """Test getting category mismatch rate."""
        handler = MismatchHandler()
        
        # Record 8 critical, 7 performance mismatches
        for i in range(15):
            handler.record_mismatch(
                event_type='test_event',
                sequence_id=i,
                adapter='websocket',
                expected_checksum='abc',
                actual_checksum='def',
                category='critical' if i < 8 else 'performance',
                error_message='Mismatch',
            )
        
        critical_rate = handler.get_category_mismatch_rate('critical')
        performance_rate = handler.get_category_mismatch_rate('performance')
        
        assert critical_rate == pytest.approx(8/15)
        assert performance_rate == pytest.approx(7/15)

    def test_get_stats(self):
        """Test getting statistics."""
        handler = MismatchHandler()
        
        handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='critical',
            error_message='Mismatch',
        )
        
        stats = handler.get_stats()
        
        assert isinstance(stats, MismatchStats)
        assert stats.total_mismatches == 1

    def test_get_stats_dict(self):
        """Test getting statistics as dictionary."""
        handler = MismatchHandler()
        
        handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='critical',
            error_message='Mismatch',
        )
        
        stats_dict = handler.get_stats_dict()
        
        assert isinstance(stats_dict, dict)
        assert stats_dict['total_mismatches'] == 1
        assert 'mismatches_by_adapter' in stats_dict
        assert 'mismatches_by_category' in stats_dict

    def test_reset_stats(self):
        """Test resetting statistics."""
        handler = MismatchHandler()
        
        handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc',
            actual_checksum='def',
            category='critical',
            error_message='Mismatch',
        )
        
        handler.reset_stats()
        
        stats = handler.get_stats()
        assert stats.total_mismatches == 0

    def test_recent_mismatches_limit(self):
        """Test that recent mismatches are limited."""
        handler = MismatchHandler()
        
        # Record 150 mismatches (exceeds default limit of 100)
        for i in range(150):
            handler.record_mismatch(
                event_type='test_event',
                sequence_id=i,
                adapter='websocket',
                expected_checksum='abc',
                actual_checksum='def',
                category='performance',
                error_message='Mismatch',
            )
        
        stats = handler.get_stats()
        
        # Should keep only last 100
        assert len(stats.recent_mismatches) == 100

    def test_mismatch_record_to_dict(self):
        """Test MismatchRecord to_dict conversion."""
        handler = MismatchHandler()
        
        record = handler.record_mismatch(
            event_type='test_event',
            sequence_id=123,
            adapter='websocket',
            expected_checksum='abc123',
            actual_checksum='def456',
            category='critical',
            error_message='Checksum mismatch',
        )
        
        record_dict = record.to_dict()
        
        assert record_dict['event_type'] == 'test_event'
        assert record_dict['sequence_id'] == 123
        assert record_dict['adapter'] == 'websocket'
        assert record_dict['expected_checksum'] == 'abc123'
        assert record_dict['actual_checksum'] == 'def456'
        assert record_dict['category'] == 'critical'
        assert record_dict['severity'] == 'critical'

