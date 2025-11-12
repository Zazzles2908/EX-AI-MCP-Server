"""
Configuration and constants for EX MCP Server

DEPRECATED: This module is now a compatibility shim.
All configuration has been moved to the config/ package for better organization.

Import from config package instead:
    from config import DEFAULT_MODEL, TimeoutConfig, MigrationConfig

This file re-exports everything from config/ for backward compatibility.
"""

# Re-export everything from config package
from config import *  # noqa: F401, F403

# Backward compatibility: Keep logger for any code that imports it
import logging
logger = logging.getLogger(__name__)
