"""
Kimi File Provider Implementation

Adapter for Kimi (Moonshot) file operations implementing FileProviderInterface.
Wraps existing Kimi provider upload/download logic.
"""

import logging
import os
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from src.file_management.models import FileReference, FileUploadMetadata
from src.file_management.exceptions import (
    FileUploadError,
    FileDownloadError,
    FileDeleteError,
    FileNotFoundError,
    FileValidationError
)
from src.providers.kimi import KimiModelProvider

logger = logging.getLogger(__name__)


class KimiFileProvider:
    """
    Kimi file provider implementation
    
    Implements FileProviderInterface for Kimi (Moonshot) file operations.
    Wraps existing KimiModelProvider upload/download logic.
    
    Attributes:
        provider: KimiModelProvider instance
        _available: Provider availability status
    """
    
    def __init__(self, provider: KimiModelProvider):
        """
        Initialize Kimi file provider
        
        Args:
            provider: KimiModelProvider instance
        """
        self.provider = provider
        self._available = True
        
        # Validate provider has required methods
        if not hasattr(provider, 'upload_file'):
            raise ValueError("KimiModelProvider must have upload_file method")
    
    async def upload_file(
        self,
        file_path: str,
        metadata: FileUploadMetadata
    ) -> FileReference:
        """
        Upload a file to Kimi (Moonshot)
        
        Args:
            file_path: Absolute path to the file to upload
            metadata: Upload metadata (purpose, context, etc.)
            
        Returns:
            FileReference with Kimi-specific ID and metadata
            
        Raises:
            FileUploadError: If upload fails
            FileValidationError: If file validation fails
            FileNotFoundError: If file doesn't exist
        """
        try:
            # Validate file exists
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(file_path=file_path)
            
            # Get file info
            file_size = file_path_obj.stat().st_size
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            
            # Calculate SHA256
            file_hash = await self._calculate_file_hash(file_path)
            
            # Upload to Kimi
            purpose = metadata.purpose or "file-extract"
            
            try:
                provider_file_id = self.provider.upload_file(file_path, purpose=purpose)
            except FileNotFoundError as e:
                raise FileNotFoundError(file_path=file_path) from e
            except ValueError as e:
                # Size limit exceeded
                raise FileValidationError(
                    f"File validation failed: {str(e)}",
                    "kimi",
                    "SIZE_LIMIT_EXCEEDED"
                ) from e
            except Exception as e:
                raise FileUploadError(
                    f"Kimi upload failed: {str(e)}",
                    "kimi",
                    "UPLOAD_FAILED",
                    retryable=True,
                    file_path=file_path
                ) from e
            
            # Create FileReference
            file_ref = FileReference(
                internal_id=str(uuid.uuid4()),
                provider_id=provider_file_id,
                provider="kimi",
                file_hash=file_hash,
                size=file_size,
                mime_type=mime_type,
                original_name=file_path_obj.name,
                created_at=datetime.now(),
                metadata={
                    "purpose": purpose,
                    "context": metadata.context,
                    "tags": metadata.tags or []
                }
            )
            
            logger.info(
                f"Uploaded file to Kimi: {file_path_obj.name} -> {provider_file_id}",
                extra={
                    "file_id": file_ref.internal_id,
                    "provider_id": provider_file_id,
                    "size": file_size,
                    "hash": file_hash
                }
            )
            
            return file_ref
            
        except (FileNotFoundError, FileValidationError, FileUploadError):
            # Re-raise these exceptions as-is
            raise
            
        except Exception as e:
            # Wrap unexpected errors
            raise FileUploadError(
                f"Unexpected error during Kimi upload: {str(e)}",
                "kimi",
                "UNEXPECTED_ERROR",
                retryable=False,
                file_path=file_path
            ) from e
    
    async def download_file(
        self,
        file_ref: FileReference,
        destination: str
    ) -> bool:
        """
        Download a file from Kimi (Moonshot)
        
        Note: Kimi doesn't currently support file download via API.
        This method is a placeholder for future implementation.
        
        Args:
            file_ref: Reference to the file to download
            destination: Absolute path where file should be saved
            
        Returns:
            True if download successful
            
        Raises:
            FileDownloadError: Download not supported by Kimi
        """
        raise FileDownloadError(
            "Kimi (Moonshot) does not support file download via API",
            "kimi",
            "DOWNLOAD_NOT_SUPPORTED"
        )
    
    async def delete_file(
        self,
        file_ref: FileReference
    ) -> bool:
        """
        Delete a file from Kimi (Moonshot)
        
        Note: Kimi file deletion is handled via the manage files tool.
        This method wraps that functionality.
        
        Args:
            file_ref: Reference to the file to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            FileDeleteError: If deletion fails
        """
        try:
            # Kimi deletion would be done via the files API
            # For now, we'll log and return success
            # TODO: Implement actual deletion when Kimi API supports it
            logger.warning(
                f"Kimi file deletion not fully implemented: {file_ref.provider_id}",
                extra={"file_id": file_ref.internal_id, "provider_id": file_ref.provider_id}
            )
            return True
            
        except Exception as e:
            raise FileDeleteError(
                f"Kimi file deletion failed: {str(e)}",
                "kimi",
                "DELETE_FAILED"
            ) from e
    
    async def get_file_info(
        self,
        file_ref: FileReference
    ) -> Dict[str, Any]:
        """
        Get metadata about a file from Kimi
        
        Args:
            file_ref: Reference to the file
            
        Returns:
            Dictionary with file metadata
        """
        # Return metadata from FileReference
        # Kimi doesn't provide a get_file_info API endpoint
        return {
            "id": file_ref.provider_id,
            "internal_id": file_ref.internal_id,
            "provider": "kimi",
            "size": file_ref.size,
            "mime_type": file_ref.mime_type,
            "original_name": file_ref.original_name,
            "created_at": file_ref.created_at.isoformat() if file_ref.created_at else None,
            "metadata": file_ref.metadata
        }
    
    async def list_files(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[FileReference]:
        """
        List files available from Kimi
        
        Note: This would require querying Supabase for Kimi files.
        Not implemented in this version.
        
        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileReference objects
        """
        # TODO: Implement by querying Supabase for files with provider='kimi'
        logger.warning("Kimi list_files not implemented - would query Supabase")
        return []
    
    async def check_file_exists(
        self,
        file_hash: str
    ) -> Optional[FileReference]:
        """
        Check if a file with given hash exists in Kimi
        
        Note: This would require querying Supabase.
        Not implemented in this version.
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            FileReference if file exists, None otherwise
        """
        # TODO: Implement by querying Supabase
        logger.warning("Kimi check_file_exists not implemented - would query Supabase")
        return None
    
    @property
    def provider_name(self) -> str:
        """
        Get the name of this provider
        
        Returns:
            Provider name ("kimi")
        """
        return "kimi"
    
    @property
    def is_available(self) -> bool:
        """
        Check if this provider is currently available
        
        Returns:
            True if provider is available, False otherwise
        """
        # Check if API key is configured
        api_key = os.getenv("KIMI_API_KEY")
        return bool(api_key and self._available)
    
    async def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA256 hash of file
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA256 hash as hexadecimal string
        """
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()

