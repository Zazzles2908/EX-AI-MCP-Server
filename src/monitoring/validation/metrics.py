"""
Validation metrics tracking - in-memory metrics with periodic persistence.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Optional
import threading
import time


class ValidationMetrics:
    """Tracks validation metrics in-memory with optional persistence."""
    
    def __init__(self, flush_interval_seconds: int = 60):
        """
        Initialize validation metrics.
        
        Args:
            flush_interval_seconds: Interval for flushing metrics to database
        """
        self.logger = logging.getLogger(__name__)
        self.flush_interval = flush_interval_seconds
        
        # In-memory metrics
        self._lock = threading.Lock()
        self._metrics = defaultdict(lambda: {
            'total_events': 0,
            'passed_events': 0,
            'failed_events': 0,
            'total_validation_time_ms': 0.0,
            'error_count': 0,
            'warning_count': 0,
            'last_updated': datetime.utcnow(),
        })
        
        # Flush tracking
        self._last_flush = datetime.utcnow()
        self._flush_thread = None
        self._stop_flush = False
    
    def record_validation(
        self,
        event_type: str,
        is_valid: bool,
        validation_time_ms: float,
        error_count: int = 0,
        warning_count: int = 0,
    ) -> None:
        """
        Record a validation result.
        
        Args:
            event_type: Type of event validated
            is_valid: Whether validation passed
            validation_time_ms: Time taken for validation
            error_count: Number of validation errors
            warning_count: Number of validation warnings
        """
        with self._lock:
            metrics = self._metrics[event_type]
            metrics['total_events'] += 1
            metrics['total_validation_time_ms'] += validation_time_ms
            metrics['error_count'] += error_count
            metrics['warning_count'] += warning_count
            metrics['last_updated'] = datetime.utcnow()
            
            if is_valid:
                metrics['passed_events'] += 1
            else:
                metrics['failed_events'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot."""
        with self._lock:
            result = {}
            
            for event_type, metrics in self._metrics.items():
                total = metrics['total_events']
                avg_time = (
                    metrics['total_validation_time_ms'] / total
                    if total > 0 else 0
                )
                
                result[event_type] = {
                    'total_events': metrics['total_events'],
                    'passed_events': metrics['passed_events'],
                    'failed_events': metrics['failed_events'],
                    'pass_rate': (
                        metrics['passed_events'] / total * 100
                        if total > 0 else 0
                    ),
                    'avg_validation_time_ms': avg_time,
                    'total_errors': metrics['error_count'],
                    'total_warnings': metrics['warning_count'],
                    'last_updated': metrics['last_updated'].isoformat(),
                }
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'by_event_type': result,
                'total_validations': sum(m['total_events'] for m in self._metrics.values()),
            }
    
    def get_event_type_metrics(self, event_type: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific event type."""
        with self._lock:
            if event_type not in self._metrics:
                return None
            
            metrics = self._metrics[event_type]
            total = metrics['total_events']
            avg_time = (
                metrics['total_validation_time_ms'] / total
                if total > 0 else 0
            )
            
            return {
                'event_type': event_type,
                'total_events': metrics['total_events'],
                'passed_events': metrics['passed_events'],
                'failed_events': metrics['failed_events'],
                'pass_rate': (
                    metrics['passed_events'] / total * 100
                    if total > 0 else 0
                ),
                'avg_validation_time_ms': avg_time,
                'total_errors': metrics['error_count'],
                'total_warnings': metrics['warning_count'],
                'last_updated': metrics['last_updated'].isoformat(),
            }
    
    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
            self._last_flush = datetime.utcnow()
        
        self.logger.info("Validation metrics reset")
    
    def reset_event_type(self, event_type: str) -> None:
        """Reset metrics for a specific event type."""
        with self._lock:
            if event_type in self._metrics:
                del self._metrics[event_type]
        
        self.logger.info(f"Validation metrics reset for {event_type}")
    
    def should_flush(self) -> bool:
        """Check if metrics should be flushed to database."""
        elapsed = (datetime.utcnow() - self._last_flush).total_seconds()
        return elapsed >= self.flush_interval
    
    def mark_flushed(self) -> None:
        """Mark metrics as flushed."""
        self._last_flush = datetime.utcnow()
    
    def get_flush_data(self) -> Dict[str, Any]:
        """Get metrics data for flushing to database."""
        with self._lock:
            flush_data = []
            
            for event_type, metrics in self._metrics.items():
                total = metrics['total_events']
                avg_time = (
                    metrics['total_validation_time_ms'] / total
                    if total > 0 else 0
                )
                
                flush_data.append({
                    'event_type': event_type,
                    'timestamp': datetime.utcnow(),
                    'total_events': metrics['total_events'],
                    'passed_events': metrics['passed_events'],
                    'failed_events': metrics['failed_events'],
                    'avg_validation_time_ms': avg_time,
                })
            
            return {
                'metrics': flush_data,
                'timestamp': datetime.utcnow(),
            }

