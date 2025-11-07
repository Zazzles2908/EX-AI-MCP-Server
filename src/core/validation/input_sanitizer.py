"""
Centralized input validation and sanitization for all user inputs.

This module provides comprehensive validation for:
- File paths (prevent directory traversal)
- User queries (prevent injection)
- Configuration values (type and range validation)
- API parameters (sanitization and bounds checking)

Security fixes to address input validation gaps that could lead to injection attacks.
"""

from __future__ import annotations

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Centralized input sanitization and validation."""

    # Dangerous patterns that could indicate attacks
    DANGEROUS_PATTERNS = [
        r'\.\./',  # Directory traversal
        r'[<>:"|?*]',  # Invalid filename characters on Windows
        r'[\x00-\x1f]',  # Control characters
        r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])$',  # Windows reserved names
        r'^\s*$',  # Whitespace only
    ]

    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize sanitizer with repository root for path validation."""
        self.repo_root = repo_root or Path.cwd().resolve()
        self._compiled_patterns = [re.compile(p) for p in self.DANGEROUS_PATTERNS]

    def sanitize_file_path(self, file_path: str, max_length: int = 4096) -> tuple[bool, str, Optional[Path]]:
        """
        Sanitize and validate a file path.

        Args:
            file_path: Path to validate
            max_length: Maximum allowed path length

        Returns:
            Tuple of (is_valid, error_message, normalized_path)
        """
        if not file_path or not isinstance(file_path, str):
            return False, "File path must be a non-empty string", None

        # Check length
        if len(file_path) > max_length:
            return False, f"File path exceeds maximum length of {max_length} characters", None

        # Check for dangerous patterns
        for pattern in self._compiled_patterns:
            if pattern.search(file_path):
                return False, f"File path contains dangerous pattern: {pattern.pattern}", None

        try:
            # Normalize path
            # If it's an absolute path, check if it's within repo root
            # If it's relative, make it relative to repo root
            path_obj = Path(file_path)

            # If absolute path, ensure it's within repo root
            if path_obj.is_absolute():
                resolved = path_obj.resolve()
                if not str(resolved).startswith(str(self.repo_root)):
                    # Allow explicitly allowlisted external paths
                    if not self._is_allowlisted_external(resolved):
                        return False, f"Path escapes repository root: {file_path}", None
                normalized = resolved
            else:
                # Relative path - resolve against repo root
                normalized = (self.repo_root / file_path).resolve()

            # Final security check
            if not str(normalized).startswith(str(self.repo_root)):
                if not self._is_allowlisted_external(normalized):
                    return False, f"Path escapes repository root after normalization: {file_path}", None

            return True, "", normalized

        except Exception as e:
            return False, f"Invalid file path format: {str(e)}", None

    def sanitize_query(self, query: str, max_length: int = 10000) -> tuple[bool, str, str]:
        """
        Sanitize a user query string.

        Args:
            query: Query to sanitize
            max_length: Maximum allowed query length

        Returns:
            Tuple of (is_valid, error_message, sanitized_query)
        """
        if not query or not isinstance(query, str):
            return False, "Query must be a non-empty string", ""

        # Check length
        if len(query) > max_length:
            return False, f"Query exceeds maximum length of {max_length} characters", ""

        # Remove control characters
        sanitized = ''.join(char for char in query if ord(char) >= 32 or char in '\t\n\r')

        # Check for SQL injection patterns (basic)
        sql_patterns = [
            r'(\bunion\b\s+select\b)',
            r'(\bdrop\s+table\b)',
            r'(\bdelete\s+from\b)',
            r'(\binsert\s+into\b)',
            r'(\bupdate\b\s+\w+\s+set\b)',
            r'(--|\#|\/\*)',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                return False, f"Query contains potentially dangerous SQL pattern: {pattern}", ""

        return True, "", sanitized

    def sanitize_config_value(self, value: Any, value_type: type, max_length: Optional[int] = None) -> tuple[bool, str, Any]:
        """
        Sanitize and validate a configuration value.

        Args:
            value: Value to sanitize
            value_type: Expected type
            max_length: Maximum length for string values

        Returns:
            Tuple of (is_valid, error_message, sanitized_value)
        """
        if value_type == str:
            if not isinstance(value, str):
                return False, f"Expected string value", None
            if max_length and len(value) > max_length:
                return False, f"Value exceeds maximum length of {max_length} characters", None
            # Remove control characters
            sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\t\n\r')
            return True, "", sanitized

        elif value_type == int:
            try:
                sanitized = int(value)
                return True, "", sanitized
            except (ValueError, TypeError):
                return False, f"Expected integer value", None

        elif value_type == float:
            try:
                sanitized = float(value)
                return True, "", sanitized
            except (ValueError, TypeError):
                return False, f"Expected float value", None

        elif value_type == bool:
            if isinstance(value, bool):
                return True, "", value
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes', 'on'):
                    return True, "", True
                if value.lower() in ('false', '0', 'no', 'off'):
                    return True, "", False
            return False, f"Expected boolean value (true/false)", None

        elif value_type == list:
            if not isinstance(value, list):
                return False, f"Expected list value", None
            return True, "", value

        elif value_type == dict:
            if not isinstance(value, dict):
                return False, f"Expected dict value", None
            return True, "", value

        else:
            # For other types, just return as-is with type check
            if not isinstance(value, value_type):
                return False, f"Expected {value_type.__name__} value", None
            return True, "", value

    def sanitize_api_params(self, params: Dict[str, Any], schema: Dict[str, Dict]) -> tuple[bool, str, Dict[str, Any]]:
        """
        Sanitize API parameters based on a schema.

        Args:
            params: Parameters to sanitize
            schema: Schema defining expected parameters
                   Format: {param_name: {"type": type, "required": bool, "max_length": int}}

        Returns:
            Tuple of (is_valid, error_message, sanitized_params)
        """
        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary", {}

        sanitized = {}
        for param_name, constraints in schema.items():
            param_type = constraints.get("type", str)
            is_required = constraints.get("required", False)
            max_length = constraints.get("max_length")

            # Check if required parameter is missing
            if is_required and param_name not in params:
                return False, f"Missing required parameter: {param_name}", {}

            # Skip if optional parameter is not provided
            if param_name not in params:
                continue

            # Sanitize the value
            is_valid, error, sanitized_value = self.sanitize_config_value(
                params[param_name], param_type, max_length
            )

            if not is_valid:
                return False, f"Invalid parameter '{param_name}': {error}", {}

            sanitized[param_name] = sanitized_value

        return True, "", sanitized

    def _is_allowlisted_external(self, path: Path) -> bool:
        """Check if a path is in the allowlist for external absolute paths."""
        allow_external = os.getenv("EX_ALLOW_EXTERNAL_PATHS", "false").lower() == "true"
        if not allow_external:
            return False

        allowed_prefixes = os.getenv("EX_ALLOWED_EXTERNAL_PREFIXES", "")
        for prefix_str in [p.strip() for p in allowed_prefixes.split(",") if p.strip()]:
            try:
                prefix = Path(prefix_str).resolve()
                if str(path).startswith(str(prefix)):
                    return True
            except Exception:
                continue

        return False


# Global sanitizer instance
_sanitizer_instance: Optional[InputSanitizer] = None


def get_sanitizer(repo_root: Optional[Path] = None) -> InputSanitizer:
    """Get or create global sanitizer instance."""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = InputSanitizer(repo_root)
    return _sanitizer_instance


def validate_upload_path(file_path: str) -> tuple[bool, str]:
    """
    Convenience function to validate upload paths.

    Args:
        file_path: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    sanitizer = get_sanitizer()
    is_valid, error, _ = sanitizer.sanitize_file_path(file_path)
    return is_valid, error


def validate_query(query: str) -> tuple[bool, str]:
    """
    Convenience function to validate user queries.

    Args:
        query: Query to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    sanitizer = get_sanitizer()
    is_valid, error, _ = sanitizer.sanitize_query(query)
    return is_valid, error
