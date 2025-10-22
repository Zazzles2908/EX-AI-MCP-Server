"""
Base file provider interface

Defines the protocol that all file providers must implement for
consistent file operations across different backends.
"""

from typing import Protocol, Dict, Any, Optional
from src.file_management.models import FileReference, FileUploadMetadata


class FileProviderInterface(Protocol):
    """
    Protocol for file provider implementations
    
    All file providers (Kimi, GLM, local storage, etc.) must implement
    this interface to ensure consistent behavior across the system.
    
    This uses Python's Protocol for structural subtyping, allowing
    existing classes to implement the interface without explicit inheritance.
    """
    
    async def upload_file(
        self,
        file_path: str,
        metadata: FileUploadMetadata
    ) -> FileReference:
        """
        Upload a file to the provider
        
        Args:
            file_path: Absolute path to the file to upload
            metadata: Upload metadata (purpose, context, etc.)
            
        Returns:
            FileReference with provider-specific ID and metadata
            
        Raises:
            FileUploadError: If upload fails
            FileValidationError: If file validation fails
        """
        ...
    
    async def download_file(
        self,
        file_ref: FileReference,
        destination: str
    ) -> bool:
        """
        Download a file from the provider
        
        Args:
            file_ref: Reference to the file to download
            destination: Absolute path where file should be saved
            
        Returns:
            True if download successful, False otherwise
            
        Raises:
            FileDownloadError: If download fails
            FileNotFoundError: If file doesn't exist
        """
        ...
    
    async def delete_file(
        self,
        file_ref: FileReference
    ) -> bool:
        """
        Delete a file from the provider
        
        Args:
            file_ref: Reference to the file to delete
            
        Returns:
            True if deletion successful, False otherwise
            
        Raises:
            FileDeleteError: If deletion fails
            FileNotFoundError: If file doesn't exist
        """
        ...
    
    async def get_file_info(
        self,
        file_ref: FileReference
    ) -> Dict[str, Any]:
        """
        Get metadata about a file from the provider
        
        Args:
            file_ref: Reference to the file
            
        Returns:
            Dictionary with file metadata (size, mime_type, etc.)
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        ...
    
    async def list_files(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> list[FileReference]:
        """
        List files available from this provider
        
        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List of FileReference objects
        """
        ...
    
    async def check_file_exists(
        self,
        file_hash: str
    ) -> Optional[FileReference]:
        """
        Check if a file with given hash exists
        
        Args:
            file_hash: SHA256 hash of the file
            
        Returns:
            FileReference if file exists, None otherwise
        """
        ...
    
    @property
    def provider_name(self) -> str:
        """
        Get the name of this provider
        
        Returns:
            Provider name (e.g., "kimi", "glm", "local")
        """
        ...
    
    @property
    def is_available(self) -> bool:
        """
        Check if this provider is currently available
        
        Returns:
            True if provider is available, False otherwise
        """
        ...

