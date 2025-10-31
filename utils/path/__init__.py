"""
Path utilities - Pure path handling and validation.

This module provides path normalization, validation, and conversion utilities
for cross-platform path handling (Windows ↔ Linux/Docker).

Phase 1 Consolidation (2025-10-31):
- Consolidated path-specific utilities into dedicated subdirectory
- Separated pure path logic from file operations
- Maintained backward compatibility through re-exports
- Split validation.py into validation/ subdirectory (follows config/ pattern)

Architecture:
- normalizer.py: PathNormalizer for Windows ↔ Docker path conversion
- validation/: Path validation subdirectory
  - docker.py: Docker-specific validation
  - application.py: Application-aware validation
  - helpers.py: Helper functions and backward compatibility
"""

# Re-export path normalizer
from .normalizer import PathNormalizer

# Re-export all validation utilities from validation subdirectory
from .validation import (
    validate_upload_path,
    validate_universal_upload_path,
    get_path_validation_examples,
    ApplicationAwarePathValidator,
    validate_file_path,
    default_validator,
)

__all__ = [
    # Normalization
    'PathNormalizer',
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

