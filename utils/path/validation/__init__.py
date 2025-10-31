"""
Path validation utilities - Re-exports for easy access.

This module provides centralized path validation for Docker and application-aware contexts.

Phase 1 Path Consolidation (2025-10-31):
- Created as part of utils/path/validation/ subdirectory structure
- Re-exports all validation functions for backward compatibility
- Follows config/ pattern (subdirectory with re-exports)

Architecture:
- docker.py: Docker-specific validation (validate_upload_path, validate_universal_upload_path)
- application.py: Application-aware validation (ApplicationAwarePathValidator)
- helpers.py: Helper functions and backward compatibility (validate_file_path)
"""

# Re-export Docker validation functions
from .docker import (
    validate_upload_path,
    validate_universal_upload_path,
    get_path_validation_examples,
)

# Re-export Application validation class
from .application import ApplicationAwarePathValidator

# Re-export helper functions
from .helpers import validate_file_path, default_validator

__all__ = [
    # Docker validation
    'validate_upload_path',
    'validate_universal_upload_path',
    'get_path_validation_examples',
    # Application validation
    'ApplicationAwarePathValidator',
    # Helpers
    'validate_file_path',
    'default_validator',
]

