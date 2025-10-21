"""
Environment Variable Validation Framework

Week 3 Fix #12 (2025-10-21): Comprehensive environment variable validation
with type-specific validators, clear error messages, and hybrid error handling.

This module provides a production-ready framework for validating environment
variables with fail-fast behavior for critical variables and graceful degradation
for non-critical ones.
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

# Set up logging
logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation errors."""
    CRITICAL = "critical"  # Application cannot start
    WARNING = "warning"    # Use default and continue


@dataclass
class ValidationResult:
    """Result of an environment variable validation."""
    is_valid: bool
    value: Any
    error_message: Optional[str] = None
    severity: ValidationSeverity = ValidationSeverity.WARNING
    suggestion: Optional[str] = None


class EnvironmentVariableError(Exception):
    """Base exception for environment variable validation errors."""
    pass


class CriticalEnvironmentVariableError(EnvironmentVariableError):
    """Exception for critical environment variable validation errors."""
    pass


class Validator(ABC):
    """Base class for all validators."""
    
    def __init__(self, name: str, default: Any = None, 
                 severity: ValidationSeverity = ValidationSeverity.WARNING, 
                 description: str = ""):
        self.name = name
        self.default = default
        self.severity = severity
        self.description = description
    
    @abstractmethod
    def validate(self, value: str) -> ValidationResult:
        """Validate the provided value."""
        pass
    
    def get_env_value(self) -> str:
        """Get the environment variable value."""
        return os.getenv(self.name, "")
    
    def validate_env_var(self) -> ValidationResult:
        """Validate the environment variable."""
        env_value = self.get_env_value()
        
        # If the environment variable is not set and we have a default, use the default
        if not env_value and self.default is not None:
            logger.info(f"Environment variable {self.name} not set, using default: {self.default}")
            return ValidationResult(is_valid=True, value=self.default)
        
        # If the environment variable is not set and we don't have a default, it's an error
        if not env_value:
            error_msg = f"Environment variable {self.name} is not set"
            suggestion = f"Set {self.name} in your environment or configuration"
            if self.severity == ValidationSeverity.CRITICAL:
                return ValidationResult(is_valid=False, value=None, error_message=error_msg, 
                                      severity=self.severity, suggestion=suggestion)
            else:
                logger.warning(f"{error_msg}, using default: {self.default}")
                return ValidationResult(is_valid=True, value=self.default, error_message=error_msg, 
                                      severity=self.severity, suggestion=suggestion)
        
        # Validate the provided value
        result = self.validate(env_value)
        
        if not result.is_valid:
            if self.severity == ValidationSeverity.CRITICAL:
                logger.error(f"Critical validation error for {self.name}: {result.error_message}")
                return result
            else:
                logger.warning(f"Validation error for {self.name}: {result.error_message}, using default: {self.default}")
                return ValidationResult(is_valid=True, value=self.default, error_message=result.error_message, 
                                      severity=self.severity, suggestion=result.suggestion)
        
        return result


class PortValidator(Validator):
    """Validator for port numbers."""
    
    def __init__(self, name: str, default: int = 8080, avoid_privileged: bool = True, 
                 severity: ValidationSeverity = ValidationSeverity.WARNING, description: str = ""):
        self.avoid_privileged = avoid_privileged
        super().__init__(name, default, severity, description)
    
    def validate(self, value: str) -> ValidationResult:
        try:
            port = int(value)
            if port < 1 or port > 65535:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Port must be between 1 and 65535, got {port}",
                    suggestion="Use a port within the valid range (1-65535)"
                )
            
            if self.avoid_privileged and 1 <= port <= 1023:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Port {port} is in privileged range (1-1023)",
                    suggestion="Use a non-privileged port (1024-65535)"
                )
            
            return ValidationResult(is_valid=True, value=port)
        except ValueError:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"Port must be an integer, got '{value}'",
                suggestion="Provide a valid integer port number"
            )


class SizeValidator(Validator):
    """Validator for size values (in bytes)."""
    
    def __init__(self, name: str, default: int = 1024, min_size: int = 1, max_size: Optional[int] = None,
                 severity: ValidationSeverity = ValidationSeverity.WARNING, description: str = ""):
        self.min_size = min_size
        self.max_size = max_size
        super().__init__(name, default, severity, description)
    
    def validate(self, value: str) -> ValidationResult:
        try:
            size = int(value)
            if size < self.min_size:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Size must be at least {self.min_size} bytes, got {size}",
                    suggestion=f"Use a size of at least {self.min_size} bytes"
                )
            
            if self.max_size is not None and size > self.max_size:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Size exceeds maximum of {self.max_size} bytes, got {size}",
                    suggestion=f"Use a size of at most {self.max_size} bytes"
                )
            
            return ValidationResult(is_valid=True, value=size)
        except ValueError:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"Size must be an integer, got '{value}'",
                suggestion="Provide a valid integer size in bytes"
            )


class StringValidator(Validator):
    """Validator for string values."""
    
    def __init__(self, name: str, default: str = "", min_length: int = 0, max_length: Optional[int] = None,
                 allow_empty: bool = True, severity: ValidationSeverity = ValidationSeverity.WARNING, 
                 description: str = ""):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_empty = allow_empty
        super().__init__(name, default, severity, description)
    
    def validate(self, value: str) -> ValidationResult:
        if not self.allow_empty and not value:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"String cannot be empty",
                suggestion="Provide a non-empty string value"
            )
        
        if len(value) < self.min_length:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"String must be at least {self.min_length} characters, got {len(value)}",
                suggestion=f"Use a string with at least {self.min_length} characters"
            )
        
        if self.max_length is not None and len(value) > self.max_length:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"String exceeds maximum length of {self.max_length} characters, got {len(value)}",
                suggestion=f"Use a string with at most {self.max_length} characters"
            )
        
        return ValidationResult(is_valid=True, value=value)


class IntegerValidator(Validator):
    """Validator for integer values."""
    
    def __init__(self, name: str, default: int = 0, min_value: Optional[int] = None, max_value: Optional[int] = None,
                 severity: ValidationSeverity = ValidationSeverity.WARNING, description: str = ""):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(name, default, severity, description)
    
    def validate(self, value: str) -> ValidationResult:
        try:
            int_value = int(value)
            
            if self.min_value is not None and int_value < self.min_value:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Value must be at least {self.min_value}, got {int_value}",
                    suggestion=f"Use a value of at least {self.min_value}"
                )
            
            if self.max_value is not None and int_value > self.max_value:
                return ValidationResult(
                    is_valid=False, 
                    value=None, 
                    error_message=f"Value exceeds maximum of {self.max_value}, got {int_value}",
                    suggestion=f"Use a value of at most {self.max_value}"
                )
            
            return ValidationResult(is_valid=True, value=int_value)
        except ValueError:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"Value must be an integer, got '{value}'",
                suggestion="Provide a valid integer value"
            )


class TimeoutValidator(Validator):
    """Validator for timeout values (in seconds). Accepts both int and float."""

    def __init__(self, name: str, default: float = 30.0, min_value: float = 1.0, max_value: float = 3600.0,
                 severity: ValidationSeverity = ValidationSeverity.WARNING, description: str = ""):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(name, default, severity, description)

    def validate(self, value: str) -> ValidationResult:
        try:
            # Accept both int and float
            timeout_value = float(value)

            if timeout_value < self.min_value:
                return ValidationResult(
                    is_valid=False,
                    value=None,
                    error_message=f"Timeout must be at least {self.min_value}s, got {timeout_value}s",
                    suggestion=f"Use a timeout of at least {self.min_value}s"
                )

            if timeout_value > self.max_value:
                return ValidationResult(
                    is_valid=False,
                    value=None,
                    error_message=f"Timeout exceeds maximum of {self.max_value}s, got {timeout_value}s",
                    suggestion=f"Use a timeout of at most {self.max_value}s"
                )

            return ValidationResult(is_valid=True, value=timeout_value)
        except ValueError:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Timeout must be a number, got '{value}'",
                suggestion="Provide a valid numeric timeout value"
            )


class BooleanValidator(Validator):
    """Validator for boolean values."""
    
    def __init__(self, name: str, default: bool = False, 
                 severity: ValidationSeverity = ValidationSeverity.WARNING, description: str = ""):
        super().__init__(name, default, severity, description)
    
    def validate(self, value: str) -> ValidationResult:
        normalized = value.lower().strip()
        
        if normalized in ('true', '1', 'yes', 'on', 'y', 't'):
            return ValidationResult(is_valid=True, value=True)
        elif normalized in ('false', '0', 'no', 'off', 'n', 'f'):
            return ValidationResult(is_valid=True, value=False)
        else:
            return ValidationResult(
                is_valid=False, 
                value=None, 
                error_message=f"Boolean must be 'true'/'false', 'yes'/'no', '1'/'0', etc., got '{value}'",
                suggestion="Use true/false, yes/no, 1/0, on/off, y/n, or t/f"
            )


class CustomValidator(Validator):
    """Validator that uses a custom validation function."""

    def __init__(self, name: str, validation_func: Callable[[str], ValidationResult],
                 default: Any = None, severity: ValidationSeverity = ValidationSeverity.WARNING,
                 description: str = ""):
        self.validation_func = validation_func
        super().__init__(name, default, severity, description)

    def validate(self, value: str) -> ValidationResult:
        return self.validation_func(value)


@dataclass
class ValidationConfig:
    """Configuration for the validation framework."""
    fail_fast_on_critical: bool = True
    log_warnings: bool = True
    log_info: bool = True


class EnvironmentValidationFramework:
    """Framework for validating environment variables."""

    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.validators: Dict[str, Validator] = {}
        self.results: Dict[str, ValidationResult] = {}
        self.critical_errors: List[str] = []

    def register_validator(self, validator: Validator) -> None:
        """Register a validator for an environment variable."""
        self.validators[validator.name] = validator

    def register_validators(self, validators: List[Validator]) -> None:
        """Register multiple validators."""
        for validator in validators:
            self.register_validator(validator)

    def validate_all(self) -> Dict[str, ValidationResult]:
        """Validate all registered environment variables."""
        self.results = {}
        self.critical_errors = []

        for name, validator in self.validators.items():
            result = validator.validate_env_var()
            self.results[name] = result

            if not result.is_valid and result.severity == ValidationSeverity.CRITICAL:
                self.critical_errors.append(name)

                if self.config.fail_fast_on_critical:
                    logger.error(f"Critical validation error for {name}: {result.error_message}")
                    if result.suggestion:
                        logger.error(f"Suggestion: {result.suggestion}")
                    raise CriticalEnvironmentVariableError(
                        f"Critical validation error for {name}: {result.error_message}"
                    )

        if self.critical_errors:
            error_msg = f"Critical validation errors for: {', '.join(self.critical_errors)}"
            raise CriticalEnvironmentVariableError(error_msg)

        return self.results

    def get_validated_value(self, name: str, default: Any = None) -> Any:
        """Get a validated value for a specific environment variable."""
        if name in self.results:
            return self.results[name].value

        if name in self.validators:
            result = self.validators[name].validate_env_var()
            self.results[name] = result
            return result.value

        return default

    def get_all_validated_values(self) -> Dict[str, Any]:
        """Get all validated values as a dictionary."""
        if not self.results:
            self.validate_all()

        return {name: result.value for name, result in self.results.items()}

    def print_validation_summary(self) -> None:
        """Print a summary of the validation results."""
        if not self.results:
            logger.info("No validation results available. Run validate_all() first.")
            return

        critical_count = sum(
            1 for r in self.results.values()
            if not r.is_valid and r.severity == ValidationSeverity.CRITICAL
        )
        warning_count = sum(
            1 for r in self.results.values()
            if not r.is_valid and r.severity == ValidationSeverity.WARNING
        )
        valid_count = sum(1 for r in self.results.values() if r.is_valid)

        logger.info(
            f"Validation Summary: {valid_count} valid, {warning_count} warnings, "
            f"{critical_count} critical errors"
        )

        if critical_count > 0:
            logger.error("Critical Errors:")
            for name, result in self.results.items():
                if not result.is_valid and result.severity == ValidationSeverity.CRITICAL:
                    logger.error(f"  {name}: {result.error_message}")
                    if result.suggestion:
                        logger.error(f"    Suggestion: {result.suggestion}")

        if warning_count > 0 and self.config.log_warnings:
            logger.warning("Warnings:")
            for name, result in self.results.items():
                if not result.is_valid and result.severity == ValidationSeverity.WARNING:
                    logger.warning(f"  {name}: {result.error_message}")
                    if result.suggestion:
                        logger.warning(f"    Suggestion: {result.suggestion}")


# Create a singleton instance for the application
validation_framework = EnvironmentValidationFramework()


# Register the top 10 critical variables
def register_critical_variables() -> None:
    """Register the top 10 critical environment variables."""

    # 1. EXAI_WS_PORT (port: 1-65535, avoid privileged 1-1023)
    validation_framework.register_validator(
        PortValidator(
            name="EXAI_WS_PORT",
            default=8079,
            avoid_privileged=True,
            severity=ValidationSeverity.CRITICAL,
            description="WebSocket server port (avoid privileged ports 1-1023)"
        )
    )

    # 2. EXAI_WS_MAX_BYTES (size: positive, max 1GB)
    validation_framework.register_validator(
        SizeValidator(
            name="EXAI_WS_MAX_BYTES",
            default=32 * 1024 * 1024,  # 32MB
            min_size=1,
            max_size=1073741824,  # 1GB
            severity=ValidationSeverity.CRITICAL,
            description="Maximum WebSocket message size in bytes (max 1GB)"
        )
    )

    # 3. EXAI_WS_TOKEN (string: min 16 chars if not empty)
    validation_framework.register_validator(
        StringValidator(
            name="EXAI_WS_TOKEN",
            default="",
            min_length=16,
            allow_empty=True,
            severity=ValidationSeverity.WARNING,
            description="WebSocket authentication token (min 16 chars if provided)"
        )
    )

    # 4. EXAI_WS_SESSION_MAX_INFLIGHT (int: positive, reasonable max)
    validation_framework.register_validator(
        IntegerValidator(
            name="EXAI_WS_SESSION_MAX_INFLIGHT",
            default=8,
            min_value=1,
            max_value=1000,
            severity=ValidationSeverity.CRITICAL,
            description="Maximum in-flight requests per WebSocket session"
        )
    )

    # 5. EXAI_WS_GLOBAL_MAX_INFLIGHT (int: positive, > session max)
    def validate_global_max_inflight(value: str) -> ValidationResult:
        # First check if it's a valid positive integer
        int_validator = IntegerValidator("temp", min_value=1, max_value=10000)
        result = int_validator.validate(value)
        if not result.is_valid:
            return result

        # Get the session max value
        session_max = validation_framework.get_validated_value("EXAI_WS_SESSION_MAX_INFLIGHT", 8)

        # Check if global max is greater than session max
        if result.value <= session_max:
            return ValidationResult(
                is_valid=False,
                value=None,
                error_message=f"Global max in-flight ({result.value}) must be greater than session max ({session_max})",
                suggestion=f"Set a value greater than {session_max}"
            )

        return result

    validation_framework.register_validator(
        CustomValidator(
            name="EXAI_WS_GLOBAL_MAX_INFLIGHT",
            validation_func=validate_global_max_inflight,
            default=24,
            severity=ValidationSeverity.CRITICAL,
            description="Maximum global in-flight requests (must be > session max)"
        )
    )

    # 6. KIMI_CHAT_TOOL_TIMEOUT_SECS (timeout: positive, max 3600)
    validation_framework.register_validator(
        TimeoutValidator(
            name="KIMI_CHAT_TOOL_TIMEOUT_SECS",
            default=180,
            min_value=1,
            max_value=3600,
            severity=ValidationSeverity.WARNING,
            description="Timeout for Kimi chat tool calls in seconds (max 3600)"
        )
    )

    # 7. TOOL_CALL_MAX_SIZE (size: positive, max 100MB)
    validation_framework.register_validator(
        SizeValidator(
            name="TOOL_CALL_MAX_SIZE",
            default=10485760,  # 10MB
            min_size=1,
            max_size=104857600,  # 100MB
            severity=ValidationSeverity.WARNING,
            description="Maximum tool call size in bytes (max 100MB)"
        )
    )

    # 8. EXAI_WS_PING_TIMEOUT (timeout: positive, max 60)
    validation_framework.register_validator(
        TimeoutValidator(
            name="EXAI_WS_PING_TIMEOUT",
            default=10,
            min_value=1,
            max_value=60,
            severity=ValidationSeverity.WARNING,
            description="WebSocket ping timeout in seconds (max 60)"
        )
    )

    # 9. EXAI_WS_CLOSE_TIMEOUT (timeout: positive, max 30)
    validation_framework.register_validator(
        TimeoutValidator(
            name="EXAI_WS_CLOSE_TIMEOUT",
            default=1.0,
            min_value=1,
            max_value=30,
            severity=ValidationSeverity.WARNING,
            description="WebSocket close timeout in seconds (max 30)"
        )
    )

    # 10. USE_PER_SESSION_SEMAPHORES (boolean: true/false)
    validation_framework.register_validator(
        BooleanValidator(
            name="USE_PER_SESSION_SEMAPHORES",
            default=True,
            severity=ValidationSeverity.WARNING,
            description="Whether to use per-session semaphores for request limiting"
        )
    )


# Initialize the framework with critical variables
register_critical_variables()


# Configuration loader function
def load_and_validate_environment() -> Dict[str, Any]:
    """
    Load and validate all environment variables.

    Returns:
        Dictionary of validated environment variables.

    Raises:
        CriticalEnvironmentVariableError: If any critical environment variables are invalid.
    """
    try:
        results = validation_framework.validate_all()
        validation_framework.print_validation_summary()
        return validation_framework.get_all_validated_values()
    except CriticalEnvironmentVariableError as e:
        logger.error(f"Failed to validate environment variables: {e}")
        raise


# Convenience function to get a specific validated value
def get_env_var(name: str, default: Any = None) -> Any:
    """
    Get a validated environment variable value.

    Args:
        name: Name of the environment variable.
        default: Default value if the variable is not registered.

    Returns:
        The validated value or default.
    """
    return validation_framework.get_validated_value(name, default)


# Function to add additional validators for the remaining 20 variables
def register_additional_validators(validators: List[Validator]) -> None:
    """
    Register additional validators for the remaining environment variables.

    Args:
        validators: List of validators to register.
    """
    validation_framework.register_validators(validators)

