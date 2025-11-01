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
    get_checksum_manager,
)
from .mismatch_handler import (
    MismatchHandler,
    MismatchRecord,
    MismatchStats,
    MismatchSeverity,
    get_mismatch_handler,
)

__all__ = [
    'ValidationRule',
    'ValidationResult',
    'EventValidator',
    'ValidationMetrics',
    'ChecksumManager',
    'ChecksumAlgorithm',
    'ChecksumResult',
    'get_checksum_manager',
    'MismatchHandler',
    'MismatchRecord',
    'MismatchStats',
    'MismatchSeverity',
    'get_mismatch_handler',
]

