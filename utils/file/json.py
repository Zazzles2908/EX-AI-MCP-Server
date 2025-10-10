"""
JSON file operations utilities.

This module provides simple JSON read/write operations with proper error handling.
"""

import json
import os
from typing import Optional


def read_json_file(file_path: str) -> Optional[dict]:
    """
    Read and parse a JSON file with proper error handling.

    Args:
        file_path: Path to the JSON file

    Returns:
        Parsed JSON data as dict, or None if file doesn't exist or invalid
    """
    try:
        if not os.path.exists(file_path):
            return None

        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def write_json_file(file_path: str, data: dict, indent: int = 2) -> bool:
    """
    Write data to a JSON file with proper formatting.

    Args:
        file_path: Path to write the JSON file
        data: Dictionary data to serialize
        indent: JSON indentation level

    Returns:
        True if successful, False otherwise
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (OSError, TypeError):
        return False

