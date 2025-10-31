"""
Event Classifier - Categorizes monitoring events by criticality and type

Implements event classification system for Phase 2.6.1 migration strategy.
Enables gradual rollout by categorizing events and applying per-category feature flags.

EXAI Consultation: d3e51bcb-c3ea-4122-834f-21e602a0a9b1
Date: 2025-11-01
Phase: Phase 2.6.1 - Event Classification System
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class EventCategory(Enum):
    """
    Event categories for classification and routing.
    
    Used to determine:
    - Which adapter receives the event
    - Validation window for data consistency
    - Feature flag eligibility
    - Retry and circuit breaker policies
    """
    
    CRITICAL = "critical"
    """
    Critical system events requiring immediate attention.
    Examples: Health check failures, system errors, circuit breaker triggers
    Validation: 5-minute windows, strict consistency checks
    """
    
    PERFORMANCE = "performance"
    """
    Performance metrics and monitoring data.
    Examples: Cache metrics, semaphore health, response times
    Validation: 5-minute windows, statistical consistency
    """
    
    USER_ACTIVITY = "user_activity"
    """
    User session and activity tracking.
    Examples: Session metrics, connection events
    Validation: 5-minute windows, event count consistency
    """
    
    SYSTEM = "system"
    """
    General system events and status updates.
    Examples: Connection status, WebSocket health, initial stats
    Validation: 5-minute windows, basic consistency
    """
    
    DEBUG = "debug"
    """
    Debug and test events.
    Examples: Test events, development metrics
    Validation: Minimal validation, for development only
    """


class EventClassifier:
    """
    Classifies monitoring events into categories.
    
    Classification rules:
    1. Check event_type against known patterns
    2. Inspect data structure for additional context
    3. Apply default category if no match
    4. Track classification metrics
    """
    
    # Classification rules: event_type -> category
    _TYPE_RULES = {
        # Critical events
        'health_check': EventCategory.CRITICAL,
        'circuit_breaker_open': EventCategory.CRITICAL,
        'circuit_breaker_close': EventCategory.CRITICAL,
        'error': EventCategory.CRITICAL,
        'failure': EventCategory.CRITICAL,
        
        # Performance events
        'cache_metrics': EventCategory.PERFORMANCE,
        'semaphore_metrics': EventCategory.PERFORMANCE,
        'response_time': EventCategory.PERFORMANCE,
        'latency': EventCategory.PERFORMANCE,
        
        # User activity events
        'session_metrics': EventCategory.USER_ACTIVITY,
        'user_activity': EventCategory.USER_ACTIVITY,
        'session_start': EventCategory.USER_ACTIVITY,
        'session_end': EventCategory.USER_ACTIVITY,
        
        # System events
        'connection_status': EventCategory.SYSTEM,
        'websocket_health': EventCategory.SYSTEM,
        'initial_stats': EventCategory.SYSTEM,
        'stats': EventCategory.SYSTEM,
        'export_complete': EventCategory.SYSTEM,
        
        # Debug events
        'test_event': EventCategory.DEBUG,
        'debug': EventCategory.DEBUG,
    }
    
    # Metrics tracking
    _metrics = {
        'total_classified': 0,
        'category_distribution': {},
        'classification_errors': 0,
    }
    
    @classmethod
    def classify(cls, event_type: str, data: Optional[Dict[str, Any]] = None) -> EventCategory:
        """
        Classify an event based on type and data.
        
        Args:
            event_type: Type of event (e.g., 'cache_metrics')
            data: Event data dictionary (optional, for context)
        
        Returns:
            EventCategory enum value
        """
        try:
            # Check type rules first
            if event_type in cls._TYPE_RULES:
                category = cls._TYPE_RULES[event_type]
            else:
                # Apply heuristics for unknown types
                category = cls._classify_by_heuristics(event_type, data)
            
            # Update metrics
            cls._metrics['total_classified'] += 1
            cls._metrics['category_distribution'][category.value] = \
                cls._metrics['category_distribution'].get(category.value, 0) + 1
            
            logger.debug(f"[CLASSIFIER] Event '{event_type}' classified as {category.value}")
            return category
        
        except Exception as e:
            logger.error(f"[CLASSIFIER] Classification error for '{event_type}': {e}")
            cls._metrics['classification_errors'] += 1
            # Default to SYSTEM for unknown events
            return EventCategory.SYSTEM
    
    @classmethod
    def _classify_by_heuristics(cls, event_type: str, data: Optional[Dict[str, Any]]) -> EventCategory:
        """
        Apply heuristics to classify unknown event types.
        
        Args:
            event_type: Type of event
            data: Event data
        
        Returns:
            EventCategory enum value
        """
        event_lower = event_type.lower()
        
        # Heuristic 1: Check for keywords in event_type
        if any(keyword in event_lower for keyword in ['error', 'fail', 'critical', 'alert']):
            return EventCategory.CRITICAL
        
        if any(keyword in event_lower for keyword in ['cache', 'metric', 'performance', 'latency']):
            return EventCategory.PERFORMANCE
        
        if any(keyword in event_lower for keyword in ['session', 'user', 'activity']):
            return EventCategory.USER_ACTIVITY
        
        if any(keyword in event_lower for keyword in ['test', 'debug', 'dev']):
            return EventCategory.DEBUG
        
        # Heuristic 2: Check data structure if available
        if data and isinstance(data, dict):
            if 'error' in data or 'exception' in data:
                return EventCategory.CRITICAL
            
            if 'metrics' in data or 'performance' in data:
                return EventCategory.PERFORMANCE
        
        # Default to SYSTEM
        return EventCategory.SYSTEM
    
    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Get classification metrics."""
        return {
            'total_classified': cls._metrics['total_classified'],
            'category_distribution': cls._metrics['category_distribution'],
            'classification_errors': cls._metrics['classification_errors'],
        }
    
    @classmethod
    def reset_metrics(cls) -> None:
        """Reset classification metrics."""
        cls._metrics = {
            'total_classified': 0,
            'category_distribution': {},
            'classification_errors': 0,
        }

