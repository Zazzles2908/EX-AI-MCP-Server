"""
Path validation helper functions and backward compatibility.

This module provides:
- Global validator instance for convenience
- Backward compatibility function for application-aware validation
- Helper utilities for path validation

Phase 1 Path Consolidation (2025-10-31):
- Extracted from validation.py (lines 351-370)
- Part of utils/path/validation/ subdirectory structure
"""

from typing import Tuple, Optional
from .application import ApplicationAwarePathValidator


# Global validator instance for convenience
default_validator = ApplicationAwarePathValidator()


def validate_file_path(
    file_path: str,
    application_id: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Backward compatibility function for application-aware validation.

    Args:
        file_path: Path to validate
        application_id: Optional application identifier

    Returns:
        Tuple of (is_valid, error_message)
    """
    return default_validator.validate_path(file_path, application_id)

