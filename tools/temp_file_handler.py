"""
Temporary File Handler for External Applications

Handles copying files from external applications to accessible temporary locations
for processing through the Supabase Universal File Hub.
"""

import os
import shutil
import tempfile
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class TempFileHandler:
    """Handles temporary file operations for external application files"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize temp file handler
        
        Args:
            temp_dir: Optional custom temp directory. Defaults to system temp.
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        logger.info(f"TempFileHandler initialized with temp_dir: {self.temp_dir}")
        
    def copy_to_temp(
        self, 
        source_path: str, 
        application_id: Optional[str] = None
    ) -> Tuple[str, bool, str]:
        """
        Copy external file to accessible temporary location.
        
        Args:
            source_path: Path to source file
            application_id: Optional application identifier for namespacing
            
        Returns:
            Tuple of (temp_path, success, error_message)
        """
        try:
            # Validate source exists
            if not os.path.exists(source_path):
                error_msg = f"Source file does not exist: {source_path}"
                logger.error(error_msg)
                return "", False, error_msg
            
            # Generate safe temp filename
            safe_filename = self._get_safe_filename(source_path)
            
            # Add application namespace if provided
            if application_id:
                safe_filename = f"app_{application_id}_{safe_filename}"
            else:
                safe_filename = f"temp_{safe_filename}"
            
            temp_path = os.path.join(self.temp_dir, safe_filename)
            
            # Copy file
            shutil.copy2(source_path, temp_path)
            logger.info(f"Copied file to temp: {source_path} -> {temp_path}")
            
            return temp_path, True, ""
            
        except Exception as e:
            error_msg = f"Failed to copy file to temp: {str(e)}"
            logger.error(error_msg)
            return "", False, error_msg
    
    def cleanup_temp_file(self, temp_path: str) -> bool:
        """
        Clean up temporary file
        
        Args:
            temp_path: Path to temporary file
            
        Returns:
            True if cleanup successful, False otherwise
        """
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.debug(f"Cleaned up temp file: {temp_path}")
                return True
            return True  # Already cleaned up
        except Exception as e:
            logger.error(f"Failed to cleanup temp file {temp_path}: {str(e)}")
            return False
    
    def _get_safe_filename(self, original_path: str) -> str:
        """
        Generate safe filename for temporary storage
        
        Args:
            original_path: Original file path
            
        Returns:
            Safe filename with dangerous characters removed
        """
        import re
        
        path_obj = Path(original_path)
        filename = path_obj.name
        
        # Remove any path traversal and dangerous characters
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return safe_filename


# Global handler instance
temp_handler = TempFileHandler()

