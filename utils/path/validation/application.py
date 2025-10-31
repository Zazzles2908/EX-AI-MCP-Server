"""
Application-aware path validation for Universal File Hub.

This module provides application-specific path validation:
- Validates paths based on application-specific policies
- Supports pattern matching with wildcards (*, **)
- Allows flexible path handling for external applications
- Provides safe filename generation for temporary storage

Phase 1 Path Consolidation (2025-10-31):
- Extracted from validation.py (lines 241-349)
- Part of utils/path/validation/ subdirectory structure
"""

import os
import re
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ApplicationAwarePathValidator:
    """
    Application-aware path validator for Universal File Hub.

    Validates paths based on application-specific policies rather than
    hardcoded path restrictions. Supports external applications with
    flexible path handling.
    """

    def __init__(self, app_config: Optional[Dict[str, Any]] = None):
        """
        Initialize validator with application configuration.

        Args:
            app_config: Optional application configuration dict with 'allowed_paths'
        """
        self.app_config = app_config or {}
        self.allowed_patterns = self.app_config.get('allowed_paths', [])

    def validate_path(
        self,
        file_path: str,
        application_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate path with application-aware rules.

        Args:
            file_path: Path to validate
            application_id: Optional application identifier

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(file_path)

            # Basic existence check
            if not os.path.exists(abs_path):
                return False, f"Path does not exist: {abs_path}"

            # If no application context, allow all paths (for system operations)
            if not application_id:
                logger.debug(f"[APP_VALIDATOR] System context - allowing path: {abs_path}")
                return True, ""

            # Check against application-specific allowed patterns
            if self.allowed_patterns:
                path_allowed = False
                for pattern in self.allowed_patterns:
                    if self._matches_pattern(abs_path, pattern):
                        path_allowed = True
                        logger.debug(f"[APP_VALIDATOR] Path {abs_path} matched pattern {pattern}")
                        break

                if not path_allowed:
                    error_msg = f"Path not allowed by application policy: {abs_path}"
                    logger.warning(f"[APP_VALIDATOR] {error_msg}")
                    return False, error_msg

            return True, ""

        except Exception as e:
            error_msg = f"Path validation error: {str(e)}"
            logger.error(f"[APP_VALIDATOR] {error_msg}")
            return False, error_msg

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if path matches allowed pattern (supports wildcards).

        Args:
            path: Path to check
            pattern: Pattern with wildcards (* and **)

        Returns:
            True if path matches pattern
        """
        # Normalize path separators
        path = path.replace('\\', '/')
        pattern = pattern.replace('\\', '/')

        # Convert wildcard pattern to regex
        # ** matches any number of directories
        # * matches any characters except /
        regex_pattern = pattern.replace('**', '__DOUBLE_STAR__')
        regex_pattern = regex_pattern.replace('*', '[^/]*')
        regex_pattern = regex_pattern.replace('__DOUBLE_STAR__', '.*')
        regex_pattern = f'^{regex_pattern}$'

        return bool(re.match(regex_pattern, path, re.IGNORECASE))

    def get_safe_filename(self, original_path: str) -> str:
        """
        Generate safe filename for temporary storage.

        Args:
            original_path: Original file path

        Returns:
            Safe filename with dangerous characters removed
        """
        path_obj = Path(original_path)
        filename = path_obj.name
        # Remove any path traversal characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        return safe_filename

