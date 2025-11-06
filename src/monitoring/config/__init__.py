"""
Monitoring Configuration Module

Provides configuration management for dual-write system.
"""

from src.monitoring.config.dual_write_config import (
    DualWriteConfig,
    CategoryConfig,
    AdapterHealthConfig,
    AdapterType,
)
from src.monitoring.config.config_manager import (
    ConfigManager,
    # DEPRECATED: get_config_manager removed - use dependency injection
)

__all__ = [
    'DualWriteConfig',
    'CategoryConfig',
    'AdapterHealthConfig',
    'AdapterType',
    'ConfigManager',
    # DEPRECATED: 'get_config_manager' - use ConfigManager() instead
]

