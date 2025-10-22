"""
Unified File Provider Interface

This module defines the abstract base class and data structures for file operations
across different AI providers (Kimi, GLM, etc.).

Design Principles:
- Async-first for I/O-bound operations
- Standardized error handling with error codes
- Support for both simple and chunked uploads
- Concurrency protection with file-level locking
- Provider-agnostic interface with extensibility
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import mimetypes
import os
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# Enums
# ============================================================================

class FilePurpose(Enum):
    """Standard file purpose types across providers."""
    FILE_EXTRACT = "file-extract"  # Kimi: text extraction
    AGENT = "agent"                # GLM: agent usage
    ASSISTANTS = "assistants"      # Kimi: assistant usage
    TRAINING = "training"          # Future: model training
    CUSTOM = "custom"              # Provider-specific


class FileErrorCode(Enum):
    """Standardized error codes for file operations."""
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    UPLOAD_FAILED = "UPLOAD_FAILED"
    DOWNLOAD_FAILED = "DOWNLOAD_FAILED"
    DELETE_FAILED = "DELETE_FAILED"
    LIST_FAILED = "LIST_FAILED"
    INVALID_FILE_PATH = "INVALID_FILE_PATH"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    CONCURRENT_UPLOAD = "CONCURRENT_UPLOAD"
    NETWORK_ERROR = "NETWORK_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    QUOTA_EXCEEDED = "QUOTA_EXCEEDED"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    UNSUPPORTED_OPERATION = "UNSUPPORTED_OPERATION"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class FileMetadata:
    """Metadata for a file stored with a provider."""
    file_id: str
    filename: str
    size_bytes: int
    mime_type: str
    purpose: FilePurpose
    provider: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    checksum_sha256: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data['purpose'] = self.purpose.value
        data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FileMetadata:
        """Create from dictionary."""
        data = data.copy()
        data['purpose'] = FilePurpose(data['purpose'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('updated_at'):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class UploadProgress:
    """Progress information for file uploads."""
    file_id: Optional[str]
    bytes_uploaded: int
    total_bytes: int
    chunk_number: Optional[int] = None
    total_chunks: Optional[int] = None

    @property
    def percentage(self) -> float:
        """Calculate upload percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.bytes_uploaded / self.total_bytes) * 100


@dataclass
class UploadResult:
    """Result of a file upload operation."""
    file_id: str
    metadata: FileMetadata
    chunks_uploaded: Optional[int] = None
    total_chunks: Optional[int] = None
    upload_duration_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_id': self.file_id,
            'metadata': self.metadata.to_dict(),
            'chunks_uploaded': self.chunks_uploaded,
            'total_chunks': self.total_chunks,
            'upload_duration_seconds': self.upload_duration_seconds
        }


# ============================================================================
# Exceptions
# ============================================================================

class FileOperationError(Exception):
    """Base exception for file operations."""
    
    def __init__(
        self,
        message: str,
        error_code: FileErrorCode,
        provider_error: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.provider_error = provider_error or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            'message': self.message,
            'error_code': self.error_code.value,
            'provider_error': self.provider_error
        }


class UploadError(FileOperationError):
    """Exception for upload failures."""
    pass


class DownloadError(FileOperationError):
    """Exception for download failures."""
    pass


class DeleteError(FileOperationError):
    """Exception for delete failures."""
    pass


class ConcurrencyError(FileOperationError):
    """Exception for concurrency conflicts."""
    pass


# ============================================================================
# Abstract Base Class
# ============================================================================

class BaseFileProvider(ABC):
    """
    Abstract base class for file provider implementations.
    
    This interface defines standard file operations that all providers must implement.
    Providers can extend this with provider-specific functionality.
    
    Design Features:
    - Async-first for I/O operations
    - File-level locking for concurrency protection
    - Support for chunked uploads (large files)
    - Standardized error handling
    - Progress callbacks for long operations
    """

    def __init__(self, provider_name: str):
        """
        Initialize the file provider.
        
        Args:
            provider_name: Name of the provider (e.g., "kimi", "glm")
        """
        self.provider_name = provider_name
        self._upload_locks: Dict[str, asyncio.Lock] = {}
        self.default_chunk_size = 50 * 1024 * 1024  # 50MB default

    # ========================================================================
    # Abstract Methods (Must be implemented by providers)
    # ========================================================================

    @abstractmethod
    async def upload_file(
        self,
        file_path: str,
        purpose: FilePurpose = FilePurpose.FILE_EXTRACT,
        chunk_size: Optional[int] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None,
        **provider_kwargs
    ) -> UploadResult:
        """
        Upload a file to the provider.
        
        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file (affects provider behavior)
            chunk_size: Size of chunks for large file uploads (None = provider default)
            progress_callback: Optional callback for upload progress
            **provider_kwargs: Provider-specific parameters (e.g., use_sdk for GLM)
            
        Returns:
            UploadResult with file_id and metadata
            
        Raises:
            UploadError: If upload fails
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too large or invalid
        """
        pass

    @abstractmethod
    async def download_file(
        self,
        file_id: str,
        local_path: str,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None
    ) -> FileMetadata:
        """
        Download a file from the provider.
        
        Args:
            file_id: Provider's file identifier
            local_path: Where to save the downloaded file
            progress_callback: Optional callback for download progress
            
        Returns:
            FileMetadata for the downloaded file
            
        Raises:
            DownloadError: If download fails
        """
        pass

    @abstractmethod
    async def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the provider.
        
        Args:
            file_id: Provider's file identifier
            
        Returns:
            True if deleted successfully
            
        Raises:
            DeleteError: If deletion fails
        """
        pass

    @abstractmethod
    async def list_files(
        self,
        purpose: Optional[FilePurpose] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[FileMetadata]:
        """
        List files stored with the provider.
        
        Args:
            purpose: Filter by purpose (None = all)
            limit: Maximum number of files to return
            offset: Offset for pagination
            
        Returns:
            List of FileMetadata objects
            
        Raises:
            FileOperationError: If listing fails
        """
        pass

    @abstractmethod
    async def get_file_metadata(self, file_id: str) -> FileMetadata:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: Provider's file identifier
            
        Returns:
            FileMetadata for the file
            
        Raises:
            FileOperationError: If metadata retrieval fails
        """
        pass

    # ========================================================================
    # Helper Methods (Provided by base class)
    # ========================================================================

    async def _get_upload_lock(self, file_path: str) -> asyncio.Lock:
        """
        Get or create a lock for concurrent upload protection.
        
        Args:
            file_path: Path to the file being uploaded
            
        Returns:
            asyncio.Lock for this file
        """
        if file_path not in self._upload_locks:
            self._upload_locks[file_path] = asyncio.Lock()
        return self._upload_locks[file_path]

    def _should_chunk_upload(
        self,
        file_size: int,
        chunk_threshold: Optional[int] = None
    ) -> bool:
        """
        Determine if file should be uploaded in chunks.
        
        Args:
            file_size: Size of file in bytes
            chunk_threshold: Threshold for chunking (None = use default)
            
        Returns:
            True if file should be chunked
        """
        threshold = chunk_threshold or self.default_chunk_size
        return file_size > threshold

    def _calculate_checksum(self, file_path: str) -> str:
        """
        Calculate SHA256 checksum of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hex string of SHA256 checksum
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_mime_type(self, file_path: str) -> str:
        """
        Get MIME type for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "application/octet-stream"

    def _handle_provider_error(
        self,
        error: Exception,
        operation: str
    ) -> FileOperationError:
        """
        Convert provider-specific errors to standardized format.
        
        Args:
            error: Original exception from provider
            operation: Operation that failed (e.g., "upload", "download")
            
        Returns:
            FileOperationError with standardized error code
        """
        # Map common exceptions to error codes
        if isinstance(error, FileNotFoundError):
            error_code = FileErrorCode.FILE_NOT_FOUND
        elif isinstance(error, ValueError):
            error_code = FileErrorCode.FILE_TOO_LARGE
        elif isinstance(error, PermissionError):
            error_code = FileErrorCode.AUTHENTICATION_ERROR
        else:
            error_code = FileErrorCode.PROVIDER_ERROR

        return FileOperationError(
            message=f"{operation} failed: {str(error)}",
            error_code=error_code,
            provider_error={
                "original_error": str(error),
                "error_type": type(error).__name__
            }
        )


__all__ = [
    "BaseFileProvider",
    "FilePurpose",
    "FileErrorCode",
    "FileMetadata",
    "UploadProgress",
    "UploadResult",
    "FileOperationError",
    "UploadError",
    "DownloadError",
    "DeleteError",
    "ConcurrencyError",
]

