"""
Base configuration classes for EX-AI-MCP-Server
Provides common utilities for environment variable parsing
"""
from abc import ABC
from typing import Dict, Any, Optional, List
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseConfig(ABC):
    """Base configuration with common utilities"""
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Parse boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    @classmethod
    def get_int(cls, key: str, default: int) -> int:
        """Parse integer environment variable with fallback"""
        try:
            return int(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float) -> float:
        """Parse float environment variable with fallback"""
        try:
            return float(os.getenv(key, str(default)))
        except ValueError:
            logger.warning(f"Invalid float value for {key}, using default: {default}")
            return default
    
    @classmethod
    def get_str(cls, key: str, default: str = "") -> str:
        """Get string environment variable"""
        return os.getenv(key, default)
    
    @classmethod
    def get_list(cls, key: str, default: str = "", separator: str = ",") -> List[str]:
        """Parse comma-separated list from environment variable"""
        value = os.getenv(key, default)
        if not value:
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration values
        Returns True if valid, raises ValueError if invalid
        Override in subclasses to add specific validation
        """
        return True

