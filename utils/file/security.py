"""
Security and path validation utilities for file operations.

This module centralizes all security-related file access logic including:
- Path validation and sandboxing
- MCP directory detection
- Home directory protection
- Dangerous path filtering
"""

import logging
from pathlib import Path
from typing import Optional

from utils.config.security import is_dangerous_path

logger = logging.getLogger(__name__)


def _is_builtin_custom_models_config(path_str: str) -> bool:
    """
    Check if path points to the server's built-in custom_models.json config file.

    This only matches the server's internal config, not user-specified CUSTOM_MODELS_CONFIG_PATH.
    We identify the built-in config by checking if it resolves to the server's conf directory.

    Args:
        path_str: Path to check

    Returns:
        True if this is the server's built-in custom_models.json config file
    """
    try:
        path = Path(path_str)

        # Get the server root by going up from this file: utils/file_utils_security.py -> server_root
        server_root = Path(__file__).parent.parent
        builtin_config = server_root / "conf" / "custom_models.json"

        # Check if the path resolves to the same file as our built-in config
        # This handles both relative and absolute paths to the same file
        return path.resolve() == builtin_config.resolve()

    except Exception:
        # If path resolution fails, it's not our built-in config
        return False


def is_mcp_directory(path: Path) -> bool:
    """
    Check if a directory is the MCP server's own directory.

    This prevents the MCP from including its own code when scanning projects
    where the MCP has been cloned as a subdirectory.

    Args:
        path: Directory path to check

    Returns:
        True if this is the MCP server directory or a subdirectory
    """
    if not path.is_dir():
        return False

    # Get the directory where the MCP server is running from
    # __file__ is utils/file_utils_security.py, so parent.parent is the MCP root
    mcp_server_dir = Path(__file__).parent.parent.resolve()

    # Check if the given path is the MCP server directory or a subdirectory
    try:
        path.resolve().relative_to(mcp_server_dir)
        logger.info(f"Detected MCP server directory at {path}, will exclude from scanning")
        return True
    except ValueError:
        # Not a subdirectory of MCP server
        return False


def get_user_home_directory() -> Optional[Path]:
    """
    Get the user's home directory.

    Returns:
        User's home directory path
    """
    return Path.home()


def is_home_directory_root(path: Path) -> bool:
    """
    Check if the given path is the user's home directory root.

    This prevents scanning the entire home directory which could include
    sensitive data and non-project files.

    Args:
        path: Directory path to check

    Returns:
        True if this is the home directory root
    """
    user_home = get_user_home_directory()
    if not user_home:
        return False

    try:
        resolved_path = path.resolve()
        resolved_home = user_home.resolve()

        # Check if this is exactly the home directory
        if resolved_path == resolved_home:
            logger.warning(
                f"Attempted to scan user home directory root: {path}. Please specify a subdirectory instead."
            )
            return True

        # Also check common home directory patterns
        path_str = str(resolved_path).lower()
        home_patterns = [
            "/users/",  # macOS
            "/home/",  # Linux
            "c:\\users\\",  # Windows
            "c:/users/",  # Windows with forward slashes
        ]

        for pattern in home_patterns:
            if pattern in path_str:
                # Extract the user directory path
                # e.g., /Users/fahad or /home/username
                parts = path_str.split(pattern)
                if len(parts) > 1:
                    # Get the part after the pattern
                    after_pattern = parts[1]
                    # Check if we're at the user's root (no subdirectories)
                    if "/" not in after_pattern and "\\" not in after_pattern:
                        logger.warning(
                            f"Attempted to scan user home directory root: {path}. "
                            f"Please specify a subdirectory instead."
                        )
                        return True

    except Exception as e:
        logger.debug(f"Error checking if path is home directory: {e}")

    return False


def resolve_and_validate_path(path_str: str) -> Path:
    """
    Resolves and validates a path against security policies.

    This function ensures safe file access by:
    1. Requiring absolute paths (no ambiguity)
    2. Resolving symlinks to prevent deception
    3. Blocking access to dangerous system directories

    Args:
        path_str: Path string (must be absolute)

    Returns:
        Resolved Path object that is safe to access

    Raises:
        ValueError: If path is not absolute or otherwise invalid
        PermissionError: If path is in a dangerous location
    """
    # Step 1: Create a Path object
    user_path = Path(path_str)

    # Step 2: Security Policy - Require absolute paths
    # Relative paths could be interpreted differently depending on working directory
    if not user_path.is_absolute():
        raise ValueError(f"Relative paths are not supported. Please provide an absolute path.\nReceived: {path_str}")

    # Step 3: Resolve the absolute path (follows symlinks, removes .. and .)
    # This is critical for security as it reveals the true destination of symlinks
    resolved_path = user_path.resolve()

    # Step 4: Check against dangerous paths
    if is_dangerous_path(resolved_path):
        logger.warning(f"Access denied - dangerous path: {resolved_path}")
        raise PermissionError(f"Access to system directory denied: {path_str}")

    # Step 5: Check if it's the home directory root
    if is_home_directory_root(resolved_path):
        raise PermissionError(
            f"Cannot scan entire home directory: {path_str}\n" f"Please specify a subdirectory within your home folder."
        )

    return resolved_path

