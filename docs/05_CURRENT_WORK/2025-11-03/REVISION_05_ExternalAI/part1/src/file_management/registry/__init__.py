"""
File Registry Package

Cross-platform file registry implementation with metadata management,
search capabilities, and storage provider integration.
"""

from .file_registry import (
    FileRegistry,
    FileMetadata,
    FileType,
    CrossPlatformPath
)

__all__ = [
    'FileRegistry',
    'FileMetadata',
    'FileType', 
    'CrossPlatformPath'
]