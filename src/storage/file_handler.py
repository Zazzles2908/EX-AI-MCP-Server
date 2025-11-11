"""
File Handler for Supabase Storage

Handles file uploads, downloads, and management for EXAI tools.
Provides immediate upload capability with fallback to local paths.
"""

import os
import logging
from typing import List, Optional, Dict
from pathlib import Path
from .supabase_client import get_storage_manager
from utils.file.cross_platform import get_path_handler

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file operations for EXAI tools with Supabase Storage.

    Features:
    - Immediate file upload to Supabase
    - Local path fallback
    - File metadata tracking
    - Context-based organization
    - Cross-platform path normalization (Windows/Linux)
    """

    def __init__(self):
        """Initialize file handler with storage manager and path handler"""
        self.storage = get_storage_manager()
        self.upload_immediately = os.getenv("UPLOAD_FILES_IMMEDIATELY", "true").lower() == "true"
        self.path_handler = get_path_handler()  # Cross-platform path normalization
    
    def process_files(
        self,
        file_paths: List[str],
        context_id: str,
        upload_immediately: Optional[bool] = None
    ) -> List[Dict[str, str]]:
        """
        Process files and return storage information

        Args:
            file_paths: List of absolute file paths (Windows or Linux format)
            context_id: Context identifier (continuation_id or tool name)
            upload_immediately: Override default upload behavior

        Returns:
            List of dicts with 'original_path', 'normalized_path', 'storage_path', 'file_id', 'error'
        """
        if upload_immediately is None:
            upload_immediately = self.upload_immediately

        processed_files = []

        for file_path in file_paths:
            # CRITICAL FIX (2025-10-17): Normalize path for current environment (Windows -> Linux in Docker)
            normalized_path, was_converted, error_message = self.path_handler.normalize_path(file_path)

            if error_message:
                logger.error(f"Path normalization failed for {file_path}: {error_message}")
                processed_files.append({
                    'original_path': file_path,
                    'normalized_path': None,
                    'storage_path': None,
                    'file_id': None,
                    'error': error_message
                })
                continue

            # Log path conversion for debugging
            if was_converted:
                logger.info(f"Path converted: {file_path} -> {normalized_path}")

            # Check if file exists using normalized path
            # PHASE 2.4 FIX (2025-10-26): Make file handler more lenient for external applications
            # Files from other applications may not be mounted in Docker - this is expected behavior
            # Only log at DEBUG level instead of WARNING to reduce log noise
            if not os.path.exists(normalized_path):
                logger.debug(f"File not accessible in container: {normalized_path} (original: {file_path})")
                logger.debug("This is expected for files from external applications not mounted in Docker")
                processed_files.append({
                    'original_path': file_path,
                    'normalized_path': normalized_path,
                    'storage_path': None,
                    'file_id': None,
                    'error': 'File not accessible in container (not mounted)'
                })
                continue

            # CRITICAL FIX (2025-10-17): Filter out directories to prevent upload errors
            # Only process actual files, not directories
            if not os.path.isfile(normalized_path):
                logger.warning(f"Skipping non-file path: {normalized_path} (original: {file_path})")
                processed_files.append({
                    'original_path': file_path,
                    'normalized_path': normalized_path,
                    'storage_path': None,
                    'file_id': None,
                    'error': 'Path is not a file (directory or special file)'
                })
                continue

            file_info = {
                'original_path': file_path,
                'normalized_path': normalized_path,  # Track normalized path
                'storage_path': None,
                'file_id': None
            }
            
            if upload_immediately and self.storage.enabled:
                # Upload to Supabase storage using normalized path
                try:
                    # Use normalized_path for file operations
                    with open(normalized_path, 'rb') as f:
                        file_data = f.read()

                    # Generate storage path using original filename
                    file_name = os.path.basename(file_path)  # Use original path for filename
                    storage_path = f"contexts/{context_id}/{file_name}"

                    # Determine MIME type from file extension
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(normalized_path)
                    if mime_type is None:
                        mime_type = "application/octet-stream"  # Default fallback

                    # Upload file
                    file_id = self.storage.upload_file(
                        file_data=file_data,
                        original_name=file_name,
                        file_path=storage_path,
                        mime_type=mime_type
                    )

                    if file_id:
                        file_info['storage_path'] = storage_path
                        file_info['file_id'] = file_id
                        logger.info(f"Uploaded file: {file_name} -> {file_id}")
                    else:
                        logger.warning(f"Failed to upload file: {file_name}")
                        file_info['error'] = 'Upload failed'

                except Exception as e:
                    logger.error(f"Error uploading file {normalized_path}: {e}")
                    file_info['error'] = str(e)
            
            processed_files.append(file_info)
        
        return processed_files
    
    def download_file(self, file_id: str, output_path: Optional[str] = None) -> Optional[bytes]:
        """
        Download file from Supabase storage
        
        Args:
            file_id: UUID of the file
            output_path: Optional path to save file
        
        Returns:
            File content as bytes or None on error
        """
        if not self.storage.enabled:
            logger.debug("Supabase storage not enabled, skipping download")
            return None
        
        try:
            file_data = self.storage.download_file(file_id)
            
            if file_data and output_path:
                # Save to local file
                with open(output_path, 'wb') as f:
                    f.write(file_data)
                logger.info(f"Downloaded file {file_id} to {output_path}")
            
            return file_data
        
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            return None
    
    def get_file_paths(self, processed_files: List[Dict[str, str]]) -> List[str]:
        """
        Extract file paths from processed files
        
        Args:
            processed_files: List of processed file dicts
        
        Returns:
            List of file paths (storage paths if available, otherwise original paths)
        """
        paths = []
        for file_info in processed_files:
            # Prefer storage path, fallback to original path
            path = file_info.get('storage_path') or file_info.get('original_path')
            if path:
                paths.append(path)
        return paths


# Global instance
_file_handler: Optional[FileHandler] = None


def get_file_handler() -> FileHandler:
    """Get global file handler instance"""
    global _file_handler
    if _file_handler is None:
        _file_handler = FileHandler()
    return _file_handler

