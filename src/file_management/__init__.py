"""
Unified File Management Layer

This module provides a centralized file management system that:
- Provides single entry point for all file operations
- Manages deduplication across providers
- Integrates comprehensive logging
- Supports multiple AI providers (Kimi, GLM, etc.)
- Maintains backward compatibility with existing code

Architecture:
    Tool Layer → Unified File Manager → Provider Abstraction → Storage Layer

Components:
    - UnifiedFileManager: Orchestrates all file operations
    - FileProviderInterface: Common interface for providers
    - FileReference: Provider-agnostic file references
    - Custom exceptions for error handling

Usage:
    from src.file_management import UnifiedFileManager, FileReference
    from src.logging import get_file_logger
    from src.storage.supabase_client import SupabaseStorageManager
    
    # Initialize manager
    storage = SupabaseStorageManager()
    logger = get_file_logger()
    providers = {...}  # Provider instances
    
    manager = UnifiedFileManager(storage, logger, providers)
    
    # Upload file
    file_ref = await manager.upload_file_async("/path/to/file.txt", metadata={})
    
    # Or use sync wrapper
    file_ref = manager.upload_file("/path/to/file.txt", metadata={})
"""

from src.file_management.models import FileReference, FileUploadMetadata, FileOperationResult
from src.file_management.exceptions import (
    FileManagementError,
    FileUploadError,
    FileDuplicateError,
    FileNotFoundError,
    FileDownloadError,
    FileDeleteError,
    FileValidationError,
    ProviderNotFoundError
)
from src.file_management.manager import UnifiedFileManager
from src.file_management.providers import KimiFileProvider, GLMFileProvider

__all__ = [
    "UnifiedFileManager",
    "FileReference",
    "FileUploadMetadata",
    "FileOperationResult",
    "KimiFileProvider",
    "GLMFileProvider",
    "FileManagementError",
    "FileUploadError",
    "FileDuplicateError",
    "FileNotFoundError",
    "FileDownloadError",
    "FileDeleteError",
    "FileValidationError",
    "ProviderNotFoundError"
]

