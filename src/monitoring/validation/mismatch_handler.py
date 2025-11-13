"""
Mismatch handler for dual-write validation failures.

Handles checksum mismatches, logs failures, and triggers circuit breaker logic.
"""

import logging
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


logger = logging.getLogger(__name__)


class MismatchSeverity(Enum):
    """Severity levels for mismatches."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MismatchRecord:
    """Record of a checksum mismatch."""
    
    timestamp: datetime
    event_type: str
    sequence_id: Optional[int]
    adapter: str
    expected_checksum: str
    actual_checksum: str
    category: str
    severity: MismatchSeverity
    error_message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'sequence_id': self.sequence_id,
            'adapter': self.adapter,
            'expected_checksum': self.expected_checksum,
            'actual_checksum': self.actual_checksum,
            'category': self.category,
            'severity': self.severity.value,
            'error_message': self.error_message,
        }


@dataclass
class MismatchStats:
    """Statistics for mismatches."""
    
    total_mismatches: int = 0
    mismatches_by_adapter: Dict[str, int] = field(default_factory=dict)
    mismatches_by_category: Dict[str, int] = field(default_factory=dict)
    mismatches_by_severity: Dict[str, int] = field(default_factory=dict)
    recent_mismatches: List[MismatchRecord] = field(default_factory=list)
    last_mismatch_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_mismatches': self.total_mismatches,
            'mismatches_by_adapter': self.mismatches_by_adapter.copy(),
            'mismatches_by_category': self.mismatches_by_category.copy(),
            'mismatches_by_severity': self.mismatches_by_severity.copy(),
            'recent_mismatches': [m.to_dict() for m in self.recent_mismatches[-10:]],
            'last_mismatch_time': self.last_mismatch_time.isoformat() if self.last_mismatch_time else None,
        }


class MismatchHandler:
    """Handles checksum mismatches and validation failures.

    REFACTORED: Removed singleton pattern - now uses dependency injection
    for better testability and maintainability.
    """

    def __init__(self):
        """Initialize MismatchHandler."""
        self._lock = threading.Lock()
        self._stats = MismatchStats()
        self._max_recent_records = 100
        self._severity_thresholds = {
            'critical': 0.01,      # 1% mismatch rate triggers alert
            'performance': 0.05,   # 5% mismatch rate triggers alert
            'user_activity': 0.03, # 3% mismatch rate triggers alert
            'system': 0.02,        # 2% mismatch rate triggers alert
            'debug': 0.10,         # 10% mismatch rate triggers alert
        }
    
    def record_mismatch(
        self,
        event_type: str,
        sequence_id: Optional[int],
        adapter: str,
        expected_checksum: str,
        actual_checksum: str,
        category: str,
        error_message: str,
    ) -> MismatchRecord:
        """
        Record a checksum mismatch.
        
        Args:
            event_type: Type of event
            sequence_id: Sequence ID of event
            adapter: Adapter that reported mismatch
            expected_checksum: Expected checksum
            actual_checksum: Actual checksum
            category: Event category
            error_message: Error message
            
        Returns:
            MismatchRecord
        """
        severity = self._determine_severity(category)
        
        record = MismatchRecord(
            timestamp=datetime.utcnow(),
            event_type=event_type,
            sequence_id=sequence_id,
            adapter=adapter,
            expected_checksum=expected_checksum,
            actual_checksum=actual_checksum,
            category=category,
            severity=severity,
            error_message=error_message,
        )
        
        # Update statistics
        self._stats.total_mismatches += 1
        self._stats.mismatches_by_adapter[adapter] = \
            self._stats.mismatches_by_adapter.get(adapter, 0) + 1
        self._stats.mismatches_by_category[category] = \
            self._stats.mismatches_by_category.get(category, 0) + 1
        self._stats.mismatches_by_severity[severity.value] = \
            self._stats.mismatches_by_severity.get(severity.value, 0) + 1
        self._stats.last_mismatch_time = datetime.utcnow()
        
        # Keep recent records
        self._stats.recent_mismatches.append(record)
        if len(self._stats.recent_mismatches) > self._max_recent_records:
            self._stats.recent_mismatches.pop(0)
        
        # Log mismatch
        self._log_mismatch(record)
        
        return record
    
    def _determine_severity(self, category: str) -> MismatchSeverity:
        """Determine severity based on category."""
        if category == 'critical':
            return MismatchSeverity.CRITICAL
        elif category == 'performance':
            return MismatchSeverity.HIGH
        elif category == 'user_activity':
            return MismatchSeverity.MEDIUM
        else:
            return MismatchSeverity.LOW
    
    def _log_mismatch(self, record: MismatchRecord) -> None:
        """Log mismatch record."""
        log_level = {
            MismatchSeverity.CRITICAL: logging.ERROR,
            MismatchSeverity.HIGH: logging.WARNING,
            MismatchSeverity.MEDIUM: logging.INFO,
            MismatchSeverity.LOW: logging.DEBUG,
        }[record.severity]
        
        logger.log(
            log_level,
            f"Checksum mismatch: event_type={record.event_type}, "
            f"adapter={record.adapter}, category={record.category}, "
            f"severity={record.severity.value}, "
            f"expected={record.expected_checksum}, "
            f"actual={record.actual_checksum}"
        )
    
    def should_trigger_circuit_breaker(self, adapter: str) -> bool:
        """
        Determine if circuit breaker should be triggered for adapter.
        
        Args:
            adapter: Adapter name
            
        Returns:
            True if circuit breaker should be triggered
        """
        if adapter not in self._stats.mismatches_by_adapter:
            return False
        
        adapter_mismatches = self._stats.mismatches_by_adapter[adapter]
        total_mismatches = self._stats.total_mismatches
        
        if total_mismatches == 0:
            return False
        
        mismatch_rate = adapter_mismatches / total_mismatches
        
        # Trigger if mismatch rate exceeds 10%
        return mismatch_rate > 0.10
    
    def get_stats(self) -> MismatchStats:
        """Get mismatch statistics."""
        return self._stats
    
    def get_stats_dict(self) -> Dict[str, Any]:
        """Get mismatch statistics as dictionary."""
        return self._stats.to_dict()
    
    def reset_stats(self) -> None:
        """Reset statistics (for testing)."""
        self._stats = MismatchStats()
    
    def get_adapter_mismatch_rate(self, adapter: str) -> float:
        """
        Get mismatch rate for adapter.
        
        Args:
            adapter: Adapter name
            
        Returns:
            Mismatch rate (0.0 to 1.0)
        """
        if self._stats.total_mismatches == 0:
            return 0.0
        
        adapter_mismatches = self._stats.mismatches_by_adapter.get(adapter, 0)
        return adapter_mismatches / self._stats.total_mismatches
    
    def get_category_mismatch_rate(self, category: str) -> float:
        """
        Get mismatch rate for category.
        
        Args:
            category: Event category
            
        Returns:
            Mismatch rate (0.0 to 1.0)
        """
        if self._stats.total_mismatches == 0:
            return 0.0
        
        category_mismatches = self._stats.mismatches_by_category.get(category, 0)
        return category_mismatches / self._stats.total_mismatches


# DEPRECATED: Factory function replaced with direct instantiation
# Use: mismatch_handler = MismatchHandler() instead of get_mismatch_handler()
