"""
Edge case validation tests for EventClassifier.

Tests for:
- Malformed events (missing/invalid fields)
- Ambiguous event types (could fit multiple categories)
- High-frequency classification (performance under load)
- Boundary conditions and error handling
"""

import pytest
from src.monitoring.event_classifier import EventClassifier, EventCategory


class TestMalformedEvents:
    """Test classification of malformed or invalid events."""

    def test_classify_empty_event_type_string(self):
        """Test classification with empty event type."""
        category = EventClassifier.classify("", {})
        assert category == EventCategory.SYSTEM

    def test_classify_none_event_type(self):
        """Test classification with None event type."""
        # Should handle gracefully
        try:
            category = EventClassifier.classify(None, {})
            # If it doesn't raise, should default to SYSTEM
            assert category == EventCategory.SYSTEM
        except (TypeError, AttributeError):
            # Acceptable to raise for None input
            pass

    def test_classify_whitespace_only_event_type(self):
        """Test classification with whitespace-only event type."""
        category = EventClassifier.classify("   ", {})
        assert category == EventCategory.SYSTEM

    def test_classify_with_none_data(self):
        """Test classification with None data dict."""
        category = EventClassifier.classify("cache_metrics", None)
        assert category == EventCategory.PERFORMANCE

    def test_classify_with_empty_data(self):
        """Test classification with empty data dict."""
        category = EventClassifier.classify("cache_metrics", {})
        assert category == EventCategory.PERFORMANCE

    def test_classify_with_invalid_data_types(self):
        """Test classification with non-dict data."""
        # Should handle gracefully
        try:
            category = EventClassifier.classify("cache_metrics", "invalid")
            assert category == EventCategory.PERFORMANCE
        except (TypeError, AttributeError):
            # Acceptable to raise for invalid data type
            pass


class TestAmbiguousEventTypes:
    """Test classification of ambiguous event types."""

    def test_classify_cache_error(self):
        """Test classification of cache_error (could be PERFORMANCE or CRITICAL)."""
        # Should classify as CRITICAL due to 'error' keyword
        category = EventClassifier.classify("cache_error", {})
        assert category == EventCategory.CRITICAL

    def test_classify_cache_error_with_error_field(self):
        """Test cache_error with error field in data."""
        category = EventClassifier.classify("cache_error", {"error": "timeout"})
        assert category == EventCategory.CRITICAL

    def test_classify_semaphore_timeout(self):
        """Test classification of semaphore_timeout."""
        # Should classify as CRITICAL due to 'timeout' (failure indicator)
        category = EventClassifier.classify("semaphore_timeout", {})
        # Could be PERFORMANCE or CRITICAL - verify consistent behavior
        assert category in [EventCategory.CRITICAL, EventCategory.PERFORMANCE]

    def test_classify_connection_error(self):
        """Test classification of connection_error."""
        # Should classify as CRITICAL due to 'error' keyword
        category = EventClassifier.classify("connection_error", {})
        assert category == EventCategory.CRITICAL

    def test_classify_session_error(self):
        """Test classification of session_error."""
        # Should classify as CRITICAL due to 'error' keyword
        category = EventClassifier.classify("session_error", {})
        assert category == EventCategory.CRITICAL

    def test_classify_performance_alert(self):
        """Test classification of performance_alert."""
        # Should classify as CRITICAL due to 'alert' keyword
        category = EventClassifier.classify("performance_alert", {})
        assert category == EventCategory.CRITICAL

    def test_classify_metrics_error(self):
        """Test classification of metrics_error."""
        # Should classify as CRITICAL due to 'error' keyword
        category = EventClassifier.classify("metrics_error", {})
        assert category == EventCategory.CRITICAL


class TestHighFrequencyClassification:
    """Test performance under high-frequency classification."""

    def test_classify_1000_events_performance(self):
        """Test classification of 1000 events for performance."""
        import time

        EventClassifier.reset_metrics()
        start = time.time()

        for i in range(1000):
            event_type = f"event_{i % 10}"
            data = {"index": i, "value": i * 2}
            EventClassifier.classify(event_type, data)

        elapsed = time.time() - start

        # Should complete in reasonable time (< 1 second for 1000 events)
        assert elapsed < 1.0, f"Classification took {elapsed}s for 1000 events"

        # Verify metrics
        metrics = EventClassifier.get_metrics()
        assert metrics["total_classified"] == 1000

    def test_classify_10000_events_performance(self):
        """Test classification of 10000 events for performance."""
        import time

        EventClassifier.reset_metrics()
        start = time.time()

        for i in range(10000):
            event_type = f"event_{i % 100}"
            data = {"index": i}
            EventClassifier.classify(event_type, data)

        elapsed = time.time() - start

        # Should complete in reasonable time (< 5 seconds for 10000 events)
        assert elapsed < 5.0, f"Classification took {elapsed}s for 10000 events"

        # Verify metrics
        metrics = EventClassifier.get_metrics()
        assert metrics["total_classified"] == 10000

    def test_classify_mixed_categories_performance(self):
        """Test classification of mixed event types."""
        EventClassifier.reset_metrics()

        event_types = [
            "health_check",
            "cache_metrics",
            "session_metrics",
            "connection_status",
            "test_event",
            "error",
            "failure",
            "performance_alert",
            "user_activity",
            "debug",
        ]

        for _ in range(100):
            for event_type in event_types:
                EventClassifier.classify(event_type, {})

        metrics = EventClassifier.get_metrics()
        assert metrics["total_classified"] == 1000
        assert metrics["classification_errors"] == 0


class TestBoundaryConditions:
    """Test boundary conditions and limits."""

    def test_classify_very_long_event_type(self):
        """Test classification with very long event type."""
        long_type = "a" * 10000
        category = EventClassifier.classify(long_type, {})
        assert category == EventCategory.SYSTEM

    def test_classify_special_characters_in_type(self):
        """Test classification with special characters."""
        special_types = [
            "event-with-dashes",
            "event_with_underscores",
            "event.with.dots",
            "event/with/slashes",
            "event@with#symbols",
        ]

        for event_type in special_types:
            category = EventClassifier.classify(event_type, {})
            # Should not raise, should classify to SYSTEM
            assert category == EventCategory.SYSTEM

    def test_classify_unicode_event_type(self):
        """Test classification with unicode characters."""
        unicode_types = [
            "événement_français",
            "事件_中文",
            "событие_русский",
            "イベント_日本語",
        ]

        for event_type in unicode_types:
            category = EventClassifier.classify(event_type, {})
            # Should not raise, should classify to SYSTEM
            assert category == EventCategory.SYSTEM

    def test_classify_with_large_data_dict(self):
        """Test classification with large data dictionary."""
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        category = EventClassifier.classify("cache_metrics", large_data)
        assert category == EventCategory.PERFORMANCE

    def test_classify_with_nested_data_structure(self):
        """Test classification with deeply nested data."""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "error": "deep error"
                            }
                        }
                    }
                }
            }
        }
        category = EventClassifier.classify("unknown_event", nested_data)
        # Should still classify based on heuristics
        assert category in [EventCategory.CRITICAL, EventCategory.SYSTEM]


class TestSequenceIDPersistence:
    """Test sequence ID behavior and persistence strategy."""

    def test_sequence_id_increments_correctly(self):
        """Test that sequence IDs increment correctly."""
        # This test documents the current behavior
        # Sequence IDs are per-broadcaster instance, not global
        from src.monitoring.broadcaster import MonitoringBroadcaster

        broadcaster = MonitoringBroadcaster()
        assert broadcaster._sequence_counter == 0

        # After creating events, counter should increment
        # (This is tested in test_broadcaster_integration.py)

    def test_sequence_id_overflow_handling(self):
        """Test sequence ID overflow handling (documentation test)."""
        # Document the overflow strategy
        # Current implementation uses int, which in Python has arbitrary precision
        # No overflow risk, but document this assumption
        max_int = 2**63 - 1  # Max 64-bit signed int
        # Python ints can exceed this, so no practical overflow risk
        assert True  # Documentation test


class TestClassificationConsistency:
    """Test consistency of classification across multiple calls."""

    def test_same_event_type_always_same_category(self):
        """Test that same event type always produces same category."""
        event_type = "cache_metrics"
        categories = [EventClassifier.classify(event_type, {}) for _ in range(100)]
        assert all(c == EventCategory.PERFORMANCE for c in categories)

    def test_classification_deterministic(self):
        """Test that classification is deterministic."""
        event_type = "session_metrics"
        data = {"active": 5, "total": 100}

        categories = [
            EventClassifier.classify(event_type, data.copy()) for _ in range(50)
        ]

        assert all(c == EventCategory.USER_ACTIVITY for c in categories)

    def test_metrics_consistency_across_classifications(self):
        """Test that metrics remain consistent."""
        EventClassifier.reset_metrics()

        for i in range(100):
            EventClassifier.classify("cache_metrics", {})

        metrics1 = EventClassifier.get_metrics()
        metrics2 = EventClassifier.get_metrics()

        assert metrics1 == metrics2
        assert metrics1["total_classified"] == 100

