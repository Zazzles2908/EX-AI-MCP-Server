"""
Feature Flags Service for Monitoring System

Manages monitoring adapter configuration and behavior through feature flags.
Provides centralized flag management with validation and defaults.

EXAI Consultation: e50deb15-9773-4022-abec-bdb0dd64bc3b
Date: 2025-11-01
Phase: Phase 2.4 - Feature Flags Service
"""

from .manager import FlagManager, get_flag_manager
from .schema import FlagSchema, FlagDefinition

__all__ = [
    'FlagManager',
    'FlagSchema',
    'FlagDefinition',
    'get_flag_manager',
]

