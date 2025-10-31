"""
Base validation rule classes and interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ValidationResult:
    """Result of a validation check."""
    
    is_valid: bool
    rule_name: str
    error_message: Optional[str] = None
    severity: str = 'error'  # 'error', 'warning', 'info'
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class ValidationRule(ABC):
    """Base class for validation rules."""
    
    def __init__(self, name: str, event_type: str = None, severity: str = 'error'):
        """
        Initialize validation rule.
        
        Args:
            name: Rule name
            event_type: Event type this rule applies to (None = all types)
            severity: 'error', 'warning', or 'info'
        """
        self.name = name
        self.event_type = event_type
        self.severity = severity
    
    @abstractmethod
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        """
        Validate an event.
        
        Args:
            event: Event data to validate
            
        Returns:
            ValidationResult with validation outcome
        """
        pass
    
    def applies_to(self, event_type: str) -> bool:
        """Check if this rule applies to the given event type."""
        return self.event_type is None or self.event_type == event_type


class StructuralValidationRule(ValidationRule):
    """Base class for structural validation rules."""
    
    def __init__(self, name: str, event_type: str = None):
        super().__init__(name, event_type, severity='error')


class BusinessLogicValidationRule(ValidationRule):
    """Base class for business logic validation rules."""
    
    def __init__(self, name: str, event_type: str = None):
        super().__init__(name, event_type, severity='warning')


class DataQualityValidationRule(ValidationRule):
    """Base class for data quality validation rules."""
    
    def __init__(self, name: str, event_type: str = None):
        super().__init__(name, event_type, severity='info')


# Built-in structural validation rules

class RequiredFieldsRule(StructuralValidationRule):
    """Validate that required fields are present."""
    
    REQUIRED_FIELDS = ['event_type', 'timestamp', 'source', 'data']
    
    def __init__(self):
        super().__init__('required_fields')
    
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        missing_fields = [f for f in self.REQUIRED_FIELDS if f not in event]
        
        if missing_fields:
            return ValidationResult(
                is_valid=False,
                rule_name=self.name,
                error_message=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        return ValidationResult(
            is_valid=True,
            rule_name=self.name
        )


class DataTypeValidationRule(StructuralValidationRule):
    """Validate data types of event fields."""
    
    EXPECTED_TYPES = {
        'event_type': str,
        'timestamp': (str, datetime),
        'source': str,
        'data': dict,
        'metadata': dict,
    }
    
    def __init__(self):
        super().__init__('data_types')
    
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        for field, expected_type in self.EXPECTED_TYPES.items():
            if field in event:
                value = event[field]
                if not isinstance(value, expected_type):
                    return ValidationResult(
                        is_valid=False,
                        rule_name=self.name,
                        error_message=f"Field '{field}' has invalid type. Expected {expected_type}, got {type(value).__name__}"
                    )
        
        return ValidationResult(
            is_valid=True,
            rule_name=self.name
        )


class EventTypeValidationRule(StructuralValidationRule):
    """Validate event type is non-empty."""
    
    def __init__(self):
        super().__init__('event_type_format')
    
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        event_type = event.get('event_type', '')
        
        if not event_type or not isinstance(event_type, str):
            return ValidationResult(
                is_valid=False,
                rule_name=self.name,
                error_message="event_type must be a non-empty string"
            )
        
        if len(event_type) > 50:
            return ValidationResult(
                is_valid=False,
                rule_name=self.name,
                error_message="event_type must be 50 characters or less"
            )
        
        return ValidationResult(
            is_valid=True,
            rule_name=self.name
        )


class SourceValidationRule(StructuralValidationRule):
    """Validate source field is non-empty."""
    
    def __init__(self):
        super().__init__('source_format')
    
    def validate(self, event: Dict[str, Any]) -> ValidationResult:
        source = event.get('source', '')
        
        if not source or not isinstance(source, str):
            return ValidationResult(
                is_valid=False,
                rule_name=self.name,
                error_message="source must be a non-empty string"
            )
        
        if len(source) > 100:
            return ValidationResult(
                is_valid=False,
                rule_name=self.name,
                error_message="source must be 100 characters or less"
            )
        
        return ValidationResult(
            is_valid=True,
            rule_name=self.name
        )

