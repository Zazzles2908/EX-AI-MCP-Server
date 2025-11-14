"""
Path validator for secure file path operations.
"""

import os
from pathlib import Path
from typing import List, Optional


class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass


class PathValidator:
    """Validates file paths for security."""

    def __init__(self, allowed_paths: Optional[List[str]] = None):
        """Initialize validator.

        Args:
            allowed_paths: List of allowed base paths
        """
        self.allowed_paths = [Path(p).resolve() for p in (allowed_paths or [])]

    def validate(self, path: str) -> Path:
        """Validate a file path.

        Args:
            path: File path to validate

        Returns:
            Resolved Path object

        Raises:
            PathValidationError: If path is invalid or not allowed
        """
        # Resolve the path
        try:
            resolved_path = Path(path).resolve()
        except Exception as e:
            raise PathValidationError(f"Invalid path: {e}")

        # Check if path is within allowed directories
        if self.allowed_paths:
            if not any(resolved_path.is_relative_to(allowed) for allowed in self.allowed_paths):
                raise PathValidationError(f"Path not in allowed directories: {path}")

        # Check for path traversal attempts
        if ".." in path:
            raise PathValidationError(f"Path traversal not allowed: {path}")

        return resolved_path

    def is_safe_path(self, path: str) -> bool:
        """Check if path is safe.

        Args:
            path: File path to check

        Returns:
            True if path is safe, False otherwise
        """
        try:
            self.validate(path)
            return True
        except PathValidationError:
            return False


# Global validator instance
_global_validator: Optional[PathValidator] = None


def get_global_validator() -> PathValidator:
    """Get the global path validator instance.

    Returns:
        Global PathValidator instance
    """
    global _global_validator
    if _global_validator is None:
        # Create a default validator that allows common paths
        allowed = [
            "/tmp",
            "/var/tmp",
            os.path.expanduser("~"),
        ]
        _global_validator = PathValidator(allowed)
    return _global_validator


def set_global_validator(validator: PathValidator):
    """Set the global path validator.

    Args:
        validator: PathValidator to set as global
    """
    global _global_validator
    _global_validator = validator
