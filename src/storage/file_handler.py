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

logger = logging.getLogger(__name__)


class FileHandler:
    """
    Handles file operations for EXAI tools with Supabase Storage.
    
    Features:
    - Immediate file upload to Supabase
    - Local path fallback
    - File metadata tracking
    - Context-based organization
    """
    
    def __init__(self):
        """Initialize file handler with storage manager"""
        self.storage = get_storage_manager()
        self.upload_immediately = os.getenv("UPLOAD_FILES_IMMEDIATELY", "true").lower() == "true"
    
    def process_files(
        self,
        file_paths: List[str],
        context_id: str,
        upload_immediately: Optional[bool] = None
    ) -> List[Dict[str, str]]:
        """
        Process files and return storage information
        
        Args:
            file_paths: List of absolute file paths
            context_id: Context identifier (continuation_id or tool name)
            upload_immediately: Override default upload behavior
        
        Returns:
            List of dicts with 'original_path', 'storage_path', 'file_id'
        """
        if upload_immediately is None:
            upload_immediately = self.upload_immediately
        
        processed_files = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            file_info = {
                'original_path': file_path,
                'storage_path': None,
                'file_id': None
            }
            
            if upload_immediately and self.storage.enabled:
                # Upload to Supabase storage
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # Generate storage path
                    file_name = os.path.basename(file_path)
                    storage_path = f"contexts/{context_id}/{file_name}"
                    
                    # Upload file
                    file_id = self.storage.upload_file(
                        file_path=storage_path,
                        file_data=file_data,
                        original_name=file_name,
                        file_type="user_upload"
                    )
                    
                    if file_id:
                        file_info['storage_path'] = storage_path
                        file_info['file_id'] = file_id
                        logger.info(f"Uploaded file: {file_name} -> {file_id}")
                    else:
                        logger.warning(f"Failed to upload file: {file_name}")
                
                except Exception as e:
                    logger.error(f"Error uploading file {file_path}: {e}")
            
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

