"""
File Lifecycle Synchronization Package

This package provides comprehensive file lifecycle management with automated
state tracking, policy enforcement, and cloud storage synchronization.
"""

from .lifecycle_sync import (
    LifecycleSync,
    LifecycleScheduler,
    LifecycleState,
    FileType,
    LifecyclePolicy,
    FileMetadata,
    SyncOperation,
    load_config
)

__version__ = "1.0.0"
__all__ = [
    "LifecycleSync",
    "LifecycleScheduler", 
    "LifecycleState",
    "FileType",
    "LifecyclePolicy",
    "FileMetadata",
    "SyncOperation",
    "load_config"
]