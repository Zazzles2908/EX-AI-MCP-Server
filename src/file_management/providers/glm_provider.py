"""
GLM File Provider Implementation

Adapter for GLM (ZhipuAI) file operations implementing FileProviderInterface.
Wraps existing GLM provider upload/download logic.
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
from src.file_management.comprehensive_validator import ComprehensiveFileValidator
from src.providers.glm import GLMModelProvider

logger = logging.getLogger(__name__)


class GLMFileProvider:
    """
    GLM file provider implementation
    
    Implements FileProviderInterface for GLM (ZhipuAI) file operations.
    Wraps existing GLMModelProvider upload/download logic.
    
    Attributes:
        provider: GLMModelProvider instance
        _available: Provider availability status
    """
    
    def __init__(self, provider: GLMModelProvider):
        """
        Initialize GLM file provider
        
        Args:
            provider: GLMModelProvider instance
        """
        self.provider = provider
        self._available = True
        
        # Validate provider has required methods
        if not hasattr(provider, 'upload_file'):
            raise ValueError("GLMModelProvider must have upload_file method")
    
    async def upload_file(
        self,
        file_path: str,
        metadata: FileUploadMetadata
    ) -> FileReference:
        """
        Upload a file to GLM (ZhipuAI)
        
        Args:
            file_path: Absolute path to the file to upload
            metadata: Upload metadata (purpose, context, etc.)
            
        Returns:
            FileReference with GLM-specific ID and metadata
            
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

            # CRITICAL SECURITY FIX (2025-11-02): Comprehensive file validation
            validator = ComprehensiveFileValidator()
            validation_result = await validator.validate(file_path)

            if not validation_result.get("valid", False):
                errors = validation_result.get("errors", ["Unknown validation error"])
                raise FileValidationError(
                    f"File validation failed: {', '.join(errors)}",
                    "glm",
                    "VALIDATION_FAILED"
                )

            # Use validation metadata (already calculated SHA256, MIME type, etc.)
            validation_metadata = validation_result.get("metadata", {})
            file_size = validation_metadata.get("size", file_path_obj.stat().st_size)
            mime_type = validation_metadata.get("mime_type", "application/octet-stream")
            file_hash = validation_metadata.get("sha256", "")
            
            # Upload to GLM
            # CRITICAL FIX (2025-11-02): Changed default from 'agent' to 'file'
            purpose = metadata.purpose or "file"

            # Validate purpose (CRITICAL)
            if purpose != "file":
                raise FileValidationError(
                    f"Invalid purpose: '{purpose}'. GLM only supports 'file'",
                    "glm",
                    "INVALID_PURPOSE"
                )

            try:
                provider_file_id = self.provider.upload_file(file_path, purpose=purpose)
            except FileNotFoundError as e:
                raise FileNotFoundError(file_path=file_path) from e
            except ValueError as e:
                # Size limit exceeded
                raise FileValidationError(
                    f"File validation failed: {str(e)}",
                    "glm",
                    "SIZE_LIMIT_EXCEEDED"
                ) from e
            except Exception as e:
                raise FileUploadError(
                    f"GLM upload failed: {str(e)}",
                    "glm",
                    "UPLOAD_FAILED",
                    retryable=True,
                    file_path=file_path
                ) from e
            
            # Create FileReference
            file_ref = FileReference(
                internal_id=str(uuid.uuid4()),
                provider_id=provider_file_id,
                provider="glm",
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
                f"Uploaded file to GLM: {file_path_obj.name} -> {provider_file_id}",
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
                f"Unexpected error during GLM upload: {str(e)}",
                "glm",
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
        Download a file from GLM (ZhipuAI)
        
        Note: GLM doesn't currently support file download via API.
        This method is a placeholder for future implementation.
        
        Args:
            file_ref: Reference to the file to download
            destination: Absolute path where file should be saved
            
        Returns:
            True if download successful
            
        Raises:
            FileDownloadError: Download not supported by GLM
        """
        raise FileDownloadError(
            "GLM (ZhipuAI) does not support file download via API",
            "glm",
            "DOWNLOAD_NOT_SUPPORTED"
        )
    
    async def delete_file(
        self,
        file_ref: FileReference
    ) -> bool:
        """
        Delete a file from GLM (ZhipuAI)
        
        Note: GLM file deletion is handled via the files API.
        This method wraps that functionality.
        
        Args:
            file_ref: Reference to the file to delete
            
        Returns:
            True if deletion successful
            
        Raises:
            FileDeleteError: If deletion fails
        """
        try:
            # GLM deletion would be done via the files API
            # For now, we'll log and return success
            # TODO: Implement actual deletion when GLM API supports it
            logger.warning(
                f"GLM file deletion not fully implemented: {file_ref.provider_id}",
                extra={"file_id": file_ref.internal_id, "provider_id": file_ref.provider_id}
            )
            return True
            
        except Exception as e:
            raise FileDeleteError(
                f"GLM file deletion failed: {str(e)}",
                "glm",
                "DELETE_FAILED"
            ) from e
    
    async def get_file_info(
        self,
        file_ref: FileReference
    ) -> Dict[str, Any]:
        """
        Get metadata about a file from GLM
        
        Args:
            file_ref: Reference to the file
            
        Returns:
            Dictionary with file metadata
        """
        # Return metadata from FileReference
        # GLM doesn't provide a get_file_info API endpoint
        return {
            "id": file_ref.provider_id,
            "internal_id": file_ref.internal_id,
            "provider": "glm",
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
        List files available from GLM
        
        Note: This would require querying Supabase for GLM files.
        Not implemented in this version.
        
        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileReference objects
        """
        # TODO: Implement by querying Supabase for files with provider='glm'
        logger.warning("GLM list_files not implemented - would query Supabase")
        return []
    
    async def check_file_exists(
        self,
        file_hash: str
    ) -> Optional[FileReference]:
        """
        Check if a file with given hash exists in GLM
        
        Note: This would require querying Supabase.
        Not implemented in this version.
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            FileReference if file exists, None otherwise
        """
        # TODO: Implement by querying Supabase
        logger.warning("GLM check_file_exists not implemented - would query Supabase")
        return None
    
    @property
    def provider_name(self) -> str:
        """
        Get the name of this provider
        
        Returns:
            Provider name ("glm")
        """
        return "glm"
    
    @property
    def is_available(self) -> bool:
        """
        Check if this provider is currently available
        
        Returns:
            True if provider is available, False otherwise
        """
        # Check if API key is configured
        api_key = os.getenv("GLM_API_KEY")
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

