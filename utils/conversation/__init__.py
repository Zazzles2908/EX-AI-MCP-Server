"""
Conversation utilities - conversation threading and memory management.

This module provides conversation memory, threading, and models
for managing multi-turn conversations.

BUG FIX #14 (2025-10-20): Removed legacy history module import
- DELETED: from .history import * (module no longer exists)
- Modern approach: Use message arrays via storage_factory

Backward compatibility: All exports are re-exported at utils level.
"""

# Re-export all conversation utilities for backward compatibility
from .memory import *
from .models import *
from .threads import *

__all__ = [
    # Exports will be populated based on actual module contents
]

