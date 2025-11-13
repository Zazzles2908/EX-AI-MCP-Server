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
from .checksum import (
    ChecksumManager,
    ChecksumAlgorithm,
    ChecksumResult,
    # DEPRECATED: get_checksum_manager removed - use ChecksumManager() instead
)
from .mismatch_handler import (
    MismatchHandler,
    MismatchRecord,
    MismatchStats,
    MismatchSeverity,
    # DEPRECATED: get_mismatch_handler removed - use MismatchHandler() instead
)

__all__ = [
    'ValidationRule',
    'ValidationResult',
    'EventValidator',
    'ValidationMetrics',
    'ChecksumManager',
    'ChecksumAlgorithm',
    'ChecksumResult',
    # DEPRECATED: 'get_checksum_manager' - use ChecksumManager() instead
    'MismatchHandler',
    'MismatchRecord',
    'MismatchStats',
    'MismatchSeverity',
    # DEPRECATED: 'get_mismatch_handler' - use MismatchHandler() instead
]

