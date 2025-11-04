"""
File Management Package

Cross-platform file management system with registry capabilities and error recovery.
"""

from .registry.file_registry import (
    FileRegistry,
    FileMetadata,
    FileType,
    CrossPlatformPath
)

from .recovery import (
    ErrorRecoveryManager,
    ErrorType,
    RecoveryStrategy,
    recovery_operation
)

from . import audit

__all__ = [
    'FileRegistry',
    'FileMetadata', 
    'FileType',
    'CrossPlatformPath',
    'ErrorRecoveryManager',
    'ErrorType',
    'RecoveryStrategy',
    'recovery_operation',
    'audit'
]

__version__ = '1.0.0'