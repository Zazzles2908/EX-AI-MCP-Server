"""
Configuration Helper Functions

This module provides helper functions for configuration management.
Separated from config.py to maintain clean separation between constants and functions.
"""

import os
from pathlib import Path
from typing import Optional


def get_auggie_config_path() -> Optional[str]:
    """
    Return the discovered auggie-config.json path or None if not found.

    Priority: env AUGGIE_CONFIG, else auggie-config.json next to config.py module.
    
    Returns:
        Path to auggie-config.json if found, None otherwise
    """
    env_path = os.getenv("AUGGIE_CONFIG")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Look for auggie-config.json in the project root (parent of utils/)
    default_path = Path(__file__).parent.parent / "auggie-config.json"
    return str(default_path) if default_path.exists() else None

