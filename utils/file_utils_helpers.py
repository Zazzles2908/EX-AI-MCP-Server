"""
General file utility helper functions.

This module provides miscellaneous file operations like size checking,
directory creation, and safe file reading.
"""

import os
from typing import Optional


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes with proper error handling.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes, or 0 if file doesn't exist or error
    """
    try:
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return os.path.getsize(file_path)
        return 0
    except OSError:
        return 0


def ensure_directory_exists(file_path: str) -> bool:
    """
    Ensure the parent directory of a file path exists.

    Args:
        file_path: Path to file (directory will be created for parent)

    Returns:
        True if directory exists or was created, False on error
    """
    try:
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        return True
    except OSError:
        return False


def is_text_file(file_path: str) -> bool:
    """
    Check if a file is likely a text file based on extension and content.

    Args:
        file_path: Path to the file

    Returns:
        True if file appears to be text, False otherwise
    """
    from .file_types import is_text_file as check_text_type

    return check_text_type(file_path)


def read_file_safely(file_path: str, max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    Read a file with size limits and encoding handling.

    Args:
        file_path: Path to the file
        max_size: Maximum file size in bytes (default 10MB)

    Returns:
        File content as string, or None if file too large or unreadable
    """
    try:
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return None

        file_size = os.path.getsize(file_path)
        if file_size > max_size:
            return None

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return None

