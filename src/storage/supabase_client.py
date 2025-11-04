"""
Supabase Storage Manager - Backward Compatibility Wrapper

This module provides backward compatibility for code importing from supabase_client.py.
All functionality has been refactored into focused modules:
- storage_exceptions.py: Custom exception types
- storage_progress.py: Progress tracking utilities
- storage_circuit_breaker.py: Circuit breaker and retry logic
- storage_telemetry.py: Performance tracking
- storage_manager.py: Main storage operations

The original supabase_client.py (1,386 lines) has been split into 5 focused modules.
New code should import directly from the specific modules.

For backwards compatibility, this wrapper re-exports all public APIs.
"""

# Re-export from refactored modules
from src.storage.storage_exceptions import RetryableError, NonRetryableError
from src.storage.storage_progress import ProgressTracker
from src.storage.storage_manager import (
    SupabaseStorageManager,
    get_storage_manager
)

# Re-export track_performance decorator from telemetry module
# Note: Importing directly to maintain original API
try:
    from src.storage.storage_telemetry import track_storage_performance as track_performance
except ImportError:
    # Fallback if telemetry not available
    def track_performance(func):
        return func

# Re-export circuit breaker functionality
from src.storage.storage_circuit_breaker import (
    StorageCircuitBreaker,
    with_circuit_breaker,
    with_retry
)

# For backward compatibility, maintain the original module docstring
__doc__ = """
Supabase Storage Manager for EXAI MCP Server
Handles persistent storage for conversations, messages, and files

PHASE 3 REFACTORING (2025-11-04):
This module has been refactored into focused components:
- storage_exceptions.py: Exception classes
- storage_progress.py: Progress tracking
- storage_circuit_breaker.py: Resilience patterns
- storage_telemetry.py: Performance monitoring
- storage_manager.py: Core storage operations

For new code, import directly from the specific modules.
"""

# Ensure all expected names are available for backward compatibility
__all__ = [
    # Exceptions
    'RetryableError',
    'NonRetryableError',

    # Classes
    'ProgressTracker',
    'SupabaseStorageManager',
    'StorageCircuitBreaker',

    # Decorators and functions
    'track_performance',
    'with_circuit_breaker',
    'with_retry',

    # Factory function
    'get_storage_manager',
]

# Maintain the original module structure for any code doing "from src.storage.supabase_client import X"
# All re-exported items above will be available
