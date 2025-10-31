"""
Monitoring event validation framework.

Provides comprehensive validation for monitoring events with:
- Structural validation (required fields, data types)
- Business logic validation
- Data quality checks
- Metrics tracking
- Dead-letter queue for invalid events
"""

from .base import ValidationRule, ValidationResult
from .event_validator import EventValidator
from .metrics import ValidationMetrics

__all__ = [
    'ValidationRule',
    'ValidationResult',
    'EventValidator',
    'ValidationMetrics',
]

