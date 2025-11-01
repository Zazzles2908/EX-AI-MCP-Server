"""
Unit tests for Event Classifier

Tests classification logic, heuristics, and metrics tracking.

Date: 2025-11-01
Phase: Phase 2.6.1 - Event Classification System
"""

import pytest
from src.monitoring.event_classifier import EventCategory, EventClassifier


class TestEventCategory:
    """Test EventCategory enum."""
    
    def test_event_category_values(self):
        """Test that all event categories have correct values."""
        assert EventCategory.CRITICAL.value == "critical"
        assert EventCategory.PERFORMANCE.value == "performance"
        assert EventCategory.USER_ACTIVITY.value == "user_activity"
        assert EventCategory.SYSTEM.value == "system"
        assert EventCategory.DEBUG.value == "debug"
    
    def test_event_category_count(self):
        """Test that all expected categories exist."""
        categories = list(EventCategory)
        assert len(categories) == 5


class TestEventClassifierTypeRules:
    """Test classification by event type rules."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        EventClassifier.reset_metrics()
    
    def test_classify_critical_events(self):
        """Test classification of critical events."""
        critical_types = [
            'health_check',
            'circuit_breaker_open',
            'circuit_breaker_close',
            'error',
            'failure',
        ]
        
        for event_type in critical_types:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.CRITICAL, f"Failed for {event_type}"
    
    def test_classify_performance_events(self):
        """Test classification of performance events."""
        performance_types = [
            'cache_metrics',
            'semaphore_metrics',
            'response_time',
            'latency',
        ]
        
        for event_type in performance_types:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.PERFORMANCE, f"Failed for {event_type}"
    
    def test_classify_user_activity_events(self):
        """Test classification of user activity events."""
        activity_types = [
            'session_metrics',
            'user_activity',
            'session_start',
            'session_end',
        ]
        
        for event_type in activity_types:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.USER_ACTIVITY, f"Failed for {event_type}"
    
    def test_classify_system_events(self):
        """Test classification of system events."""
        system_types = [
            'connection_status',
            'websocket_health',
            'initial_stats',
            'stats',
            'export_complete',
        ]
        
        for event_type in system_types:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.SYSTEM, f"Failed for {event_type}"
    
    def test_classify_debug_events(self):
        """Test classification of debug events."""
        debug_types = [
            'test_event',
            'debug',
        ]
        
        for event_type in debug_types:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.DEBUG, f"Failed for {event_type}"


class TestEventClassifierHeuristics:
    """Test classification by heuristics for unknown types."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        EventClassifier.reset_metrics()
    
    def test_heuristic_critical_keywords(self):
        """Test heuristic classification with critical keywords."""
        critical_keywords = [
            'unknown_error',
            'system_failure',
            'critical_alert',
            'CRITICAL_ISSUE',
        ]
        
        for event_type in critical_keywords:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.CRITICAL, f"Failed for {event_type}"
    
    def test_heuristic_performance_keywords(self):
        """Test heuristic classification with performance keywords."""
        performance_keywords = [
            'custom_cache_metric',
            'performance_data',
            'latency_measurement',
            'metric_update',
        ]
        
        for event_type in performance_keywords:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.PERFORMANCE, f"Failed for {event_type}"
    
    def test_heuristic_user_activity_keywords(self):
        """Test heuristic classification with user activity keywords."""
        activity_keywords = [
            'user_login',
            'session_update',
            'activity_log',
        ]
        
        for event_type in activity_keywords:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.USER_ACTIVITY, f"Failed for {event_type}"
    
    def test_heuristic_debug_keywords(self):
        """Test heuristic classification with debug keywords."""
        debug_keywords = [
            'test_run',
            'debug_info',
            'dev_event',
        ]
        
        for event_type in debug_keywords:
            category = EventClassifier.classify(event_type)
            assert category == EventCategory.DEBUG, f"Failed for {event_type}"
    
    def test_heuristic_data_structure(self):
        """Test heuristic classification based on data structure."""
        # Error in data
        category = EventClassifier.classify('unknown_event', {'error': 'something failed'})
        assert category == EventCategory.CRITICAL
        
        # Metrics in data
        category = EventClassifier.classify('unknown_event', {'metrics': {'value': 100}})
        assert category == EventCategory.PERFORMANCE
    
    def test_heuristic_default_to_system(self):
        """Test that unknown events default to SYSTEM category."""
        category = EventClassifier.classify('completely_unknown_event_xyz')
        assert category == EventCategory.SYSTEM


class TestEventClassifierMetrics:
    """Test metrics tracking."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        EventClassifier.reset_metrics()
    
    def test_metrics_total_classified(self):
        """Test that total_classified metric is incremented."""
        assert EventClassifier.get_metrics()['total_classified'] == 0
        
        EventClassifier.classify('cache_metrics')
        assert EventClassifier.get_metrics()['total_classified'] == 1
        
        EventClassifier.classify('session_metrics')
        assert EventClassifier.get_metrics()['total_classified'] == 2
    
    def test_metrics_category_distribution(self):
        """Test that category distribution is tracked."""
        EventClassifier.classify('cache_metrics')  # PERFORMANCE
        EventClassifier.classify('session_metrics')  # USER_ACTIVITY
        EventClassifier.classify('cache_metrics')  # PERFORMANCE
        
        metrics = EventClassifier.get_metrics()
        distribution = metrics['category_distribution']
        
        assert distribution['performance'] == 2
        assert distribution['user_activity'] == 1
    
    def test_metrics_classification_errors(self):
        """Test that classification errors are tracked."""
        # Simulate an error by mocking (for now, just verify structure)
        metrics = EventClassifier.get_metrics()
        assert 'classification_errors' in metrics
        assert metrics['classification_errors'] == 0
    
    def test_metrics_reset(self):
        """Test that metrics can be reset."""
        EventClassifier.classify('cache_metrics')
        assert EventClassifier.get_metrics()['total_classified'] == 1
        
        EventClassifier.reset_metrics()
        assert EventClassifier.get_metrics()['total_classified'] == 0
        assert EventClassifier.get_metrics()['category_distribution'] == {}


class TestEventClassifierEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        EventClassifier.reset_metrics()
    
    def test_classify_empty_event_type(self):
        """Test classification with empty event type."""
        category = EventClassifier.classify('')
        assert category == EventCategory.SYSTEM
    
    def test_classify_none_data(self):
        """Test classification with None data."""
        category = EventClassifier.classify('unknown_event', None)
        assert category == EventCategory.SYSTEM
    
    def test_classify_empty_data(self):
        """Test classification with empty data dict."""
        category = EventClassifier.classify('unknown_event', {})
        assert category == EventCategory.SYSTEM
    
    def test_classify_case_insensitive(self):
        """Test that classification is case-insensitive."""
        category1 = EventClassifier.classify('CACHE_METRICS')
        category2 = EventClassifier.classify('cache_metrics')
        category3 = EventClassifier.classify('Cache_Metrics')
        
        # All should be classified as PERFORMANCE (via heuristics)
        assert category1 == EventCategory.PERFORMANCE
        assert category2 == EventCategory.PERFORMANCE
        assert category3 == EventCategory.PERFORMANCE
    
    def test_classify_with_special_characters(self):
        """Test classification with special characters."""
        category = EventClassifier.classify('event-with-dashes_and_underscores')
        assert category in list(EventCategory)
    
    def test_classify_very_long_event_type(self):
        """Test classification with very long event type."""
        long_type = 'a' * 1000
        category = EventClassifier.classify(long_type)
        assert category == EventCategory.SYSTEM


class TestEventClassifierIntegration:
    """Integration tests for event classifier."""
    
    def setup_method(self):
        """Reset metrics before each test."""
        EventClassifier.reset_metrics()
    
    def test_classify_multiple_events_sequence(self):
        """Test classifying a sequence of events."""
        events = [
            ('cache_metrics', {'hits': 100}),
            ('session_metrics', {'active': 5}),
            ('health_check', {'status': 'ok'}),
            ('test_event', {'data': 'test'}),
        ]
        
        categories = []
        for event_type, data in events:
            category = EventClassifier.classify(event_type, data)
            categories.append(category)
        
        assert categories[0] == EventCategory.PERFORMANCE
        assert categories[1] == EventCategory.USER_ACTIVITY
        assert categories[2] == EventCategory.CRITICAL
        assert categories[3] == EventCategory.DEBUG
    
    def test_metrics_after_multiple_classifications(self):
        """Test metrics after classifying multiple events."""
        for _ in range(10):
            EventClassifier.classify('cache_metrics')
        
        for _ in range(5):
            EventClassifier.classify('session_metrics')
        
        metrics = EventClassifier.get_metrics()
        assert metrics['total_classified'] == 15
        assert metrics['category_distribution']['performance'] == 10
        assert metrics['category_distribution']['user_activity'] == 5

