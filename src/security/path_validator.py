"""
Path Validator - Security Module for File Upload System

This module provides path validation to prevent path traversal attacks
and unauthorized file access. It implements a strict allowlist-based
approach where only explicitly allowed path prefixes are permitted.

BATCH 4.2 (2025-11-02): Path Traversal Vulnerability Fix
- Strict allowlist-based validation
- Path normalization and resolution
- Protection against path traversal attacks (../, symlinks, etc.)
- Integration with file upload system

Security Features:
- Resolves all paths to absolute canonical form
- Prevents directory traversal attacks
- Blocks access to unauthorized directories
- Validates against explicit allowlist only

Usage:
    from src.security.path_validator import PathValidator
    
    validator = PathValidator(["/app", "/mnt/project"])
    
    if validator.is_allowed("/mnt/project/file.txt"):
        # Safe to proceed
        pass
    else:
        # Reject access
        raise SecurityError("Path not allowed")
"""

import logging
import os
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class PathValidationError(Exception):
    """Raised when path validation fails."""
    pass


class PathValidator:
    """
    Validates file paths against an allowlist of permitted prefixes.
    
    This class provides security validation for file paths to prevent
    path traversal attacks and unauthorized file access.
    
    Attributes:
        allowed_prefixes: List of allowed path prefixes (resolved to absolute paths)
    """
    
    def __init__(self, allowed_prefixes: List[str]):
        """
        Initialize path validator with allowed prefixes.
        
        Args:
            allowed_prefixes: List of allowed path prefixes (e.g., ["/app", "/mnt/project"])
                             All paths will be resolved to absolute canonical form.
        
        Raises:
            ValueError: If allowed_prefixes is empty or contains invalid paths
        """
        if not allowed_prefixes:
            raise ValueError("allowed_prefixes cannot be empty")
        
        # Resolve all prefixes to absolute canonical paths
        self.allowed_prefixes: List[Path] = []
        for prefix in allowed_prefixes:
            try:
                # Resolve to absolute path (handles symlinks, .., etc.)
                resolved = Path(prefix).resolve()
                self.allowed_prefixes.append(resolved)
                logger.debug(f"[PATH_VALIDATOR] Added allowed prefix: {resolved}")
            except Exception as e:
                logger.warning(f"[PATH_VALIDATOR] Failed to resolve prefix '{prefix}': {e}")
                # Continue with other prefixes rather than failing completely
        
        if not self.allowed_prefixes:
            raise ValueError("No valid allowed_prefixes after resolution")
        
        logger.info(f"[PATH_VALIDATOR] Initialized with {len(self.allowed_prefixes)} allowed prefixes")
    
    def is_allowed(self, file_path: str) -> bool:
        """
        Check if a file path is allowed based on the allowlist.
        
        This method:
        1. Resolves the path to absolute canonical form
        2. Checks if it starts with any allowed prefix
        3. Returns True only if path is within allowed directories
        
        Args:
            file_path: Path to validate (can be relative or absolute)
        
        Returns:
            True if path is allowed, False otherwise
        
        Examples:
            >>> validator = PathValidator(["/app", "/mnt/project"])
            >>> validator.is_allowed("/mnt/project/file.txt")
            True
            >>> validator.is_allowed("/etc/passwd")
            False
            >>> validator.is_allowed("/mnt/project/../../../etc/passwd")
            False  # Path traversal blocked
        """
        try:
            # Resolve to absolute canonical path
            # This handles:
            # - Relative paths (./file, ../file)
            # - Symlinks
            # - Path traversal attempts (../)
            # - Redundant separators (//)
            resolved_path = Path(file_path).resolve()
            
            # Check if resolved path starts with any allowed prefix
            for prefix in self.allowed_prefixes:
                try:
                    # Use relative_to to check if path is under prefix
                    # This will raise ValueError if path is not under prefix
                    resolved_path.relative_to(prefix)
                    logger.debug(f"[PATH_VALIDATOR] Path allowed: {file_path} -> {resolved_path} (prefix: {prefix})")
                    return True
                except ValueError:
                    # Path is not under this prefix, try next one
                    continue
            
            # No prefix matched - path is not allowed
            logger.warning(f"[PATH_VALIDATOR] Path rejected: {file_path} -> {resolved_path} (no matching prefix)")
            return False
            
        except Exception as e:
            # Any error during validation = reject
            logger.error(f"[PATH_VALIDATOR] Error validating path '{file_path}': {e}")
            return False
    
    def validate(self, file_path: str) -> Path:
        """
        Validate a file path and return the resolved Path object.
        
        This is a stricter version of is_allowed() that raises an exception
        on validation failure instead of returning False.
        
        Args:
            file_path: Path to validate
        
        Returns:
            Resolved Path object if validation succeeds
        
        Raises:
            PathValidationError: If path is not allowed
        
        Examples:
            >>> validator = PathValidator(["/app"])
            >>> path = validator.validate("/app/file.txt")
            >>> print(path)
            /app/file.txt
            >>> validator.validate("/etc/passwd")
            PathValidationError: Path not allowed: /etc/passwd
        """
        if not self.is_allowed(file_path):
            raise PathValidationError(f"Path not allowed: {file_path}")
        
        # Return resolved path
        return Path(file_path).resolve()
    
    def get_allowed_prefixes(self) -> List[str]:
        """
        Get list of allowed path prefixes.
        
        Returns:
            List of allowed prefixes as strings
        """
        return [str(prefix) for prefix in self.allowed_prefixes]


def create_path_validator_from_env() -> Optional[PathValidator]:
    """
    Create PathValidator from environment variables.
    
    Reads configuration from:
    - EX_ALLOW_EXTERNAL_PATHS: Enable/disable external path validation
    - EX_ALLOWED_EXTERNAL_PREFIXES: Comma-separated list of allowed prefixes
    
    Returns:
        PathValidator instance if validation is enabled, None otherwise
    
    Examples:
        # .env.docker
        EX_ALLOW_EXTERNAL_PATHS=false
        EX_ALLOWED_EXTERNAL_PREFIXES=/app,/mnt/project
        
        # Python
        validator = create_path_validator_from_env()
        if validator and not validator.is_allowed(path):
            raise SecurityError("Path not allowed")
    """
    # Check if external path validation is enabled
    allow_external = os.getenv("EX_ALLOW_EXTERNAL_PATHS", "false").lower() in ("true", "1", "yes", "on")
    
    if allow_external:
        # External paths allowed - no validation needed
        logger.info("[PATH_VALIDATOR] External paths allowed (EX_ALLOW_EXTERNAL_PATHS=true) - validation disabled")
        return None
    
    # Get allowed prefixes from environment
    prefixes_str = os.getenv("EX_ALLOWED_EXTERNAL_PREFIXES", "")
    if not prefixes_str:
        logger.warning("[PATH_VALIDATOR] EX_ALLOWED_EXTERNAL_PREFIXES not set - using default: /app,/mnt/project")
        prefixes_str = "/app,/mnt/project"
    
    # Parse comma-separated prefixes
    prefixes = [p.strip() for p in prefixes_str.split(",") if p.strip()]
    
    if not prefixes:
        logger.error("[PATH_VALIDATOR] No valid prefixes found in EX_ALLOWED_EXTERNAL_PREFIXES")
        # Fail closed - create validator with minimal permissions
        prefixes = ["/app"]
    
    try:
        validator = PathValidator(prefixes)
        logger.info(f"[PATH_VALIDATOR] Created validator with prefixes: {validator.get_allowed_prefixes()}")
        return validator
    except Exception as e:
        logger.error(f"[PATH_VALIDATOR] Failed to create validator: {e}")
        # Fail closed - return validator with minimal permissions
        return PathValidator(["/app"])


# Global validator instance (lazy-initialized)
_global_validator: Optional[PathValidator] = None


def get_global_validator() -> Optional[PathValidator]:
    """
    Get global PathValidator instance (singleton).
    
    Returns:
        PathValidator instance or None if validation is disabled
    """
    global _global_validator
    if _global_validator is None:
        _global_validator = create_path_validator_from_env()
    return _global_validator


__all__ = [
    "PathValidator",
    "PathValidationError",
    "create_path_validator_from_env",
    "get_global_validator",
]

