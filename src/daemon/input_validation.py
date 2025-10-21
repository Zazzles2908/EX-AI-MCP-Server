"""
Input Validation for EXAI MCP Server
Week 2 Fix #9 (2025-10-21): Validate all input parameters before processing

This module provides:
- Type validation (strings, integers, floats, booleans, lists, dicts)
- Range validation (min/max for numbers, length for strings/arrays)
- Format validation (model names, file paths, enum values)
- Clear validation error messages
- Lightweight validation without external dependencies

Usage:
    from src.daemon.input_validation import validate_tool_arguments, ValidationError
    
    try:
        validated_args = validate_tool_arguments(tool_name, arguments)
        result = await execute_tool(tool_name, validated_args)
    except ValidationError as e:
        # Handle validation error
        error_response = e.to_response(request_id)
"""

import os
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

logger = logging.getLogger(__name__)


# =============================================================================
# Validation Error
# =============================================================================

class ValidationError(Exception):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str, value: Any = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"Validation failed for '{field}': {message}")
    
    def to_response(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Convert to error response format."""
        from src.daemon.error_handling import create_error_response, ErrorCode
        
        details = {"field": self.field}
        if self.value is not None:
            details["value"] = str(self.value)
        
        return create_error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message=f"Validation failed for '{self.field}': {self.message}",
            request_id=request_id,
            details=details
        )


# =============================================================================
# Validation Rules
# =============================================================================

class ValidationRule:
    """Base class for validation rules."""
    
    def validate(self, value: Any, field_name: str) -> Any:
        """
        Validate a value and return the validated (possibly transformed) value.
        
        Args:
            value: Value to validate
            field_name: Name of the field being validated
        
        Returns:
            Validated value (possibly transformed)
        
        Raises:
            ValidationError: If validation fails
        """
        raise NotImplementedError


class TypeRule(ValidationRule):
    """Validate value type."""
    
    def __init__(self, expected_type: type, allow_none: bool = False):
        self.expected_type = expected_type
        self.allow_none = allow_none
    
    def validate(self, value: Any, field_name: str) -> Any:
        if value is None and self.allow_none:
            return None
        
        if not isinstance(value, self.expected_type):
            raise ValidationError(
                field_name,
                f"must be {self.expected_type.__name__}, got {type(value).__name__}",
                value
            )
        return value


class StringRule(ValidationRule):
    """Validate string with optional length constraints."""
    
    def __init__(
        self,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        allow_empty: bool = False,
        strip: bool = True
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_empty = allow_empty
        self.strip = strip
    
    def validate(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(field_name, f"must be string, got {type(value).__name__}", value)
        
        if self.strip:
            value = value.strip()
        
        if not self.allow_empty and not value:
            raise ValidationError(field_name, "cannot be empty", value)
        
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(
                field_name,
                f"must be at least {self.min_length} characters, got {len(value)}",
                value
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(
                field_name,
                f"must be at most {self.max_length} characters, got {len(value)}",
                value
            )
        
        return value


class NumberRule(ValidationRule):
    """Validate number with optional range constraints."""
    
    def __init__(
        self,
        number_type: type = float,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_none: bool = False
    ):
        self.number_type = number_type
        self.min_value = min_value
        self.max_value = max_value
        self.allow_none = allow_none
    
    def validate(self, value: Any, field_name: str) -> Union[int, float, None]:
        if value is None and self.allow_none:
            return None
        
        # Try to convert to number
        try:
            if self.number_type == int:
                value = int(value)
            else:
                value = float(value)
        except (ValueError, TypeError):
            raise ValidationError(
                field_name,
                f"must be {self.number_type.__name__}, got {type(value).__name__}",
                value
            )
        
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                field_name,
                f"must be at least {self.min_value}, got {value}",
                value
            )
        
        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                field_name,
                f"must be at most {self.max_value}, got {value}",
                value
            )
        
        return value


class EnumRule(ValidationRule):
    """Validate value is in allowed set."""
    
    def __init__(self, allowed_values: List[Any], case_sensitive: bool = True):
        self.allowed_values = allowed_values
        self.case_sensitive = case_sensitive
    
    def validate(self, value: Any, field_name: str) -> Any:
        if self.case_sensitive:
            if value not in self.allowed_values:
                raise ValidationError(
                    field_name,
                    f"must be one of {self.allowed_values}, got {value}",
                    value
                )
        else:
            # Case-insensitive comparison for strings
            if isinstance(value, str):
                value_lower = value.lower()
                allowed_lower = [str(v).lower() for v in self.allowed_values]
                if value_lower not in allowed_lower:
                    raise ValidationError(
                        field_name,
                        f"must be one of {self.allowed_values}, got {value}",
                        value
                    )
                # Return the canonical value
                idx = allowed_lower.index(value_lower)
                return self.allowed_values[idx]
            else:
                if value not in self.allowed_values:
                    raise ValidationError(
                        field_name,
                        f"must be one of {self.allowed_values}, got {value}",
                        value
                    )
        return value


class BooleanRule(ValidationRule):
    """Validate boolean value."""
    
    def validate(self, value: Any, field_name: str) -> bool:
        if isinstance(value, bool):
            return value
        
        # Try to convert string to boolean
        if isinstance(value, str):
            if value.lower() in ["true", "1", "yes", "on"]:
                return True
            elif value.lower() in ["false", "0", "no", "off"]:
                return False
        
        raise ValidationError(
            field_name,
            f"must be boolean, got {type(value).__name__}",
            value
        )


class FilePathRule(ValidationRule):
    """Validate file path exists and is accessible."""
    
    def __init__(self, must_exist: bool = True, must_be_file: bool = True):
        self.must_exist = must_exist
        self.must_be_file = must_be_file
    
    def validate(self, value: Any, field_name: str) -> str:
        if not isinstance(value, str):
            raise ValidationError(field_name, f"must be string, got {type(value).__name__}", value)
        
        path = Path(value)
        
        if self.must_exist and not path.exists():
            raise ValidationError(field_name, f"file not found: {value}", value)
        
        if self.must_be_file and path.exists() and not path.is_file():
            raise ValidationError(field_name, f"path is not a file: {value}", value)
        
        return str(path.absolute())


class ListRule(ValidationRule):
    """Validate list with optional length constraints and item validation."""
    
    def __init__(
        self,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        item_rule: Optional[ValidationRule] = None
    ):
        self.min_items = min_items
        self.max_items = max_items
        self.item_rule = item_rule
    
    def validate(self, value: Any, field_name: str) -> List[Any]:
        if not isinstance(value, list):
            raise ValidationError(field_name, f"must be list, got {type(value).__name__}", value)
        
        if self.min_items is not None and len(value) < self.min_items:
            raise ValidationError(
                field_name,
                f"must have at least {self.min_items} items, got {len(value)}",
                value
            )
        
        if self.max_items is not None and len(value) > self.max_items:
            raise ValidationError(
                field_name,
                f"must have at most {self.max_items} items, got {len(value)}",
                value
            )
        
        # Validate each item if item_rule is provided
        if self.item_rule:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = self.item_rule.validate(item, f"{field_name}[{i}]")
                    validated_items.append(validated_item)
                except ValidationError:
                    raise
            return validated_items
        
        return value


# =============================================================================
# Common Validation Schemas
# =============================================================================

# Common parameter validation rules
COMMON_VALIDATIONS = {
    "model": StringRule(min_length=1, max_length=100),
    "prompt": StringRule(min_length=1, max_length=100000, allow_empty=False),
    "temperature": NumberRule(number_type=float, min_value=0.0, max_value=1.0, allow_none=True),
    "max_tokens": NumberRule(number_type=int, min_value=1, max_value=100000, allow_none=True),
    "timeout": NumberRule(number_type=float, min_value=0.1, max_value=3600.0, allow_none=True),
    "thinking_mode": EnumRule(["minimal", "low", "medium", "high", "max"], case_sensitive=False),
    "use_websearch": BooleanRule(),
    "stream": BooleanRule(),
    "continuation_id": StringRule(min_length=1, max_length=200, allow_empty=True),
}


def validate_tool_arguments(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate tool arguments based on common validation rules.
    
    Args:
        tool_name: Name of the tool
        arguments: Arguments to validate
    
    Returns:
        Validated arguments (possibly transformed)
    
    Raises:
        ValidationError: If validation fails
    """
    validated = {}
    
    for key, value in arguments.items():
        # Skip None values for optional parameters
        if value is None:
            validated[key] = None
            continue
        
        # Apply validation rule if available
        if key in COMMON_VALIDATIONS:
            try:
                validated[key] = COMMON_VALIDATIONS[key].validate(value, key)
            except ValidationError:
                raise
        else:
            # No validation rule - pass through
            validated[key] = value
    
    return validated

