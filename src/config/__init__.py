#!/usr/bin/env python3
"""
EX-AI MCP Server - Centralized Configuration System
Prevents configuration drift with environment validation and smart defaults.
"""

import os
from .settings import Config, get_config
from .drift_detector import check_config_drift
from .secrets_manager import SecretsManager

__all__ = ['Config', 'get_config', 'check_config_drift', 'SecretsManager', 'DEFAULT_MODEL']

# Global config instance
config = get_config()

# Default model for the system
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "glm-4.5-flash")
