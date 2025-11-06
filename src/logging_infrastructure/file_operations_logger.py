"""
File Operations Logger for EXAI-MCP Server
===========================================

Specialized logger for file operations with structured metadata.

Date: 2025-10-22
Reference: EXAI consultation (Continuation: 32864286-932c-4b84-aefa-e5bd19c208bd)
"""

from datetime import datetime
from typing import Optional, Dict, Any
from .logging_manager import get_logger


class FileOperationsLogger:
    """
    Specialized logger for file operations.
    
    Provides structured logging for file lifecycle events:
    - Upload
    - Download
    - Delete
    - Access
    - Metadata changes
    
    All logs include:
    - Timestamp (ISO format)
    - Operation type
    - File path
    - User ID
    - Success/failure status
    - Error details (if applicable)
    - Additional metadata
    """
    
    def __init__(self):
        """Initialize file operations logger"""
        self.logger = get_logger("file_operations")
    
    def log_upload(
        self,
        file_path: str,
        file_size: int,
        user_id: str,
        success: bool,
        provider: Optional[str] = None,
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file upload operation.
        
        Args:
            file_path: Path to uploaded file
            file_size: File size in bytes
            user_id: User performing upload
            success: Whether upload succeeded
            provider: Storage provider (kimi, supabase, etc.)
            file_id: Provider-specific file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_upload",
            operation="upload",
            file_path=file_path,
            file_size=file_size,
            user_id=user_id,
            success=success,
            provider=provider,
            file_id=file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_download(
        self,
        file_path: str,
        user_id: str,
        success: bool,
        provider: Optional[str] = None,
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file download operation.
        
        Args:
            file_path: Path to downloaded file
            user_id: User performing download
            success: Whether download succeeded
            provider: Storage provider
            file_id: Provider-specific file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_download",
            operation="download",
            file_path=file_path,
            user_id=user_id,
            success=success,
            provider=provider,
            file_id=file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_delete(
        self,
        file_path: str,
        user_id: str,
        success: bool,
        provider: Optional[str] = None,
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file deletion operation.
        
        Args:
            file_path: Path to deleted file
            user_id: User performing deletion
            success: Whether deletion succeeded
            provider: Storage provider
            file_id: Provider-specific file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_delete",
            operation="delete",
            file_path=file_path,
            user_id=user_id,
            success=success,
            provider=provider,
            file_id=file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_access(
        self,
        file_path: str,
        user_id: str,
        access_type: str,
        success: bool = True,
        provider: Optional[str] = None,
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file access operation.
        
        Args:
            file_path: Path to accessed file
            user_id: User accessing file
            access_type: Type of access (read, write, metadata, etc.)
            success: Whether access succeeded
            provider: Storage provider
            file_id: Provider-specific file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_access",
            operation="access",
            file_path=file_path,
            user_id=user_id,
            access_type=access_type,
            success=success,
            provider=provider,
            file_id=file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_metadata_change(
        self,
        file_path: str,
        user_id: str,
        changes: Dict[str, Any],
        success: bool,
        provider: Optional[str] = None,
        file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file metadata change operation.
        
        Args:
            file_path: Path to file
            user_id: User making changes
            changes: Dictionary of metadata changes
            success: Whether change succeeded
            provider: Storage provider
            file_id: Provider-specific file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_metadata_change",
            operation="metadata_change",
            file_path=file_path,
            user_id=user_id,
            changes=changes,
            success=success,
            provider=provider,
            file_id=file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )
    
    def log_sync(
        self,
        file_path: str,
        source_provider: str,
        target_provider: str,
        success: bool,
        source_file_id: Optional[str] = None,
        target_file_id: Optional[str] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Log file synchronization operation.
        
        Args:
            file_path: Path to synchronized file
            source_provider: Source storage provider
            target_provider: Target storage provider
            success: Whether sync succeeded
            source_file_id: Source file identifier
            target_file_id: Target file identifier
            error: Error message if failed
            **kwargs: Additional metadata
        """
        self.logger.info(
            "file_sync",
            operation="sync",
            file_path=file_path,
            source_provider=source_provider,
            target_provider=target_provider,
            success=success,
            source_file_id=source_file_id,
            target_file_id=target_file_id,
            error=error,
            timestamp=datetime.utcnow().isoformat(),
            **kwargs
        )


# Global singleton instance
_file_logger: Optional[FileOperationsLogger] = None


def get_file_logger() -> FileOperationsLogger:
    """
    Get or create the global file operations logger instance.
    
    Returns:
        Global FileOperationsLogger instance
    """
    global _file_logger
    if _file_logger is None:
        _file_logger = FileOperationsLogger()
    return _file_logger

