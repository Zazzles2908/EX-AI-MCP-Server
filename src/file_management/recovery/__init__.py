"""
File Management Recovery Module

This module provides comprehensive error recovery mechanisms for file management systems.
"""

from .recovery_manager import (
    ErrorRecoveryManager,
    ErrorType,
    RecoveryStrategy,
    ErrorContext,
    CircuitBreaker,
    CircuitBreakerState,
    RetryConfig,
    FileOperationRollback,
    SupabaseErrorTracker,
    RecoveryStrategyManager,
    FallbackStorageManager,
    recovery_operation
)

__all__ = [
    "ErrorRecoveryManager",
    "ErrorType", 
    "RecoveryStrategy",
    "ErrorContext",
    "CircuitBreaker",
    "CircuitBreakerState",
    "RetryConfig",
    "FileOperationRollback", 
    "SupabaseErrorTracker",
    "RecoveryStrategyManager",
    "FallbackStorageManager",
    "recovery_operation"
]

__version__ = "1.0.0"