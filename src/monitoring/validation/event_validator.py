"""
Event validator - orchestrates validation rules and tracks metrics.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import time

from .base import (
    ValidationRule,
    ValidationResult,
    RequiredFieldsRule,
    DataTypeValidationRule,
    EventTypeValidationRule,
    SourceValidationRule,
)
from .metrics import ValidationMetrics


class EventValidator:
    """Validates monitoring events using configurable rules."""
    
    def __init__(self, metrics: Optional[ValidationMetrics] = None):
        """
        Initialize event validator.
        
        Args:
            metrics: Optional ValidationMetrics instance for tracking
        """
        self.logger = logging.getLogger(__name__)
        self.metrics = metrics or ValidationMetrics()
        
        # Initialize default structural validation rules
        self.rules: List[ValidationRule] = [
            RequiredFieldsRule(),
            DataTypeValidationRule(),
            EventTypeValidationRule(),
            SourceValidationRule(),
        ]
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)
        self.logger.debug(f"Added validation rule: {rule.name}")
    
    def remove_rule(self, rule_name: str) -> None:
        """Remove a validation rule by name."""
        self.rules = [r for r in self.rules if r.name != rule_name]
        self.logger.debug(f"Removed validation rule: {rule_name}")
    
    def validate(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an event against all applicable rules.
        
        Args:
            event: Event data to validate
            
        Returns:
            Dictionary with:
            - is_valid: bool
            - errors: List of error ValidationResults
            - warnings: List of warning ValidationResults
            - validation_time_ms: float
        """
        start_time = time.time()
        event_type = event.get('event_type', 'unknown')
        
        errors = []
        warnings = []
        
        # Run all applicable rules
        for rule in self.rules:
            if not rule.applies_to(event_type):
                continue
            
            try:
                result = rule.validate(event)
                
                if not result.is_valid:
                    if result.severity == 'error':
                        errors.append(result)
                    elif result.severity == 'warning':
                        warnings.append(result)
                
            except Exception as e:
                self.logger.error(f"Error running validation rule {rule.name}: {e}")
                errors.append(ValidationResult(
                    is_valid=False,
                    rule_name=rule.name,
                    error_message=f"Validation rule error: {str(e)}"
                ))
        
        validation_time_ms = (time.time() - start_time) * 1000
        is_valid = not errors
        
        # Track metrics
        self.metrics.record_validation(
            event_type=event_type,
            is_valid=is_valid,
            validation_time_ms=validation_time_ms,
            error_count=len(errors),
            warning_count=len(warnings)
        )
        
        if not is_valid:
            self.logger.warning(
                f"Event validation failed for {event_type}: "
                f"{len(errors)} errors, {len(warnings)} warnings"
            )
        
        return {
            'is_valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'validation_time_ms': validation_time_ms,
            'timestamp': datetime.utcnow(),
        }
    
    def validate_batch(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of events.
        
        Args:
            events: List of events to validate
            
        Returns:
            Dictionary with batch validation results
        """
        start_time = time.time()
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for event in events:
            result = self.validate(event)
            results.append(result)
            
            if result['is_valid']:
                valid_count += 1
            else:
                invalid_count += 1
        
        validation_time_ms = (time.time() - start_time) * 1000
        
        return {
            'total_events': len(events),
            'valid_events': valid_count,
            'invalid_events': invalid_count,
            'results': results,
            'validation_time_ms': validation_time_ms,
            'timestamp': datetime.utcnow(),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics."""
        return self.metrics.get_metrics()
    
    def reset_metrics(self) -> None:
        """Reset validation metrics."""
        self.metrics.reset()

