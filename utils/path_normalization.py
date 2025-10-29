"""
Universal path normalization for cross-platform file access.

Handles path conversion between Windows host and Linux Docker container,
enabling file uploads from ANY location on the filesystem.
"""

import os
import platform
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PathNormalizer:
    """Environment-aware path normalization for universal file access"""
    
    def __init__(self):
        self.current_env = "windows" if platform.system() == "Windows" else "linux"

        # Better Docker detection: check if we're actually IN the container
        # On Windows, /mnt/project might exist as a WSL mount, but we're not in Docker
        # In Docker, we'd be on Linux AND have /mnt/project
        self.in_docker = (self.current_env == "linux" and os.path.exists("/mnt/project"))

        logger.info(f"[PATH_NORMALIZER] Environment: {self.current_env}, In Docker: {self.in_docker}")
    
    def normalize_for_docker(self, file_path: str) -> Tuple[bool, str, str]:
        """
        Normalize any file path for Docker container access.
        
        Args:
            file_path: Input file path (Windows or Linux format)
        
        Returns:
            Tuple of (success, normalized_path, method)
            - success: Whether normalization succeeded
            - normalized_path: Path usable in Docker container
            - method: How the file will be accessed ("mounted", "stream", "temp_copy")
        """
        # Convert to absolute path
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, file_path, "error:file_not_found"
        
        # Determine access method based on location
        if self.current_env == "windows":
            return self._normalize_windows_path(file_path)
        else:
            return self._normalize_linux_path(file_path)
    
    def _normalize_windows_path(self, file_path: str) -> Tuple[bool, str, str]:
        """Normalize Windows path for Docker access"""
        
        # Check if file is under c:\Project\ (mounted directory)
        if file_path.lower().startswith("c:\\project\\"):
            # Convert to Linux mount path
            linux_path = file_path.replace("C:\\Project\\", "/mnt/project/")
            linux_path = linux_path.replace("c:\\Project\\", "/mnt/project/")
            linux_path = linux_path.replace("\\", "/")
            return True, linux_path, "mounted"
        
        # File is outside mounted directory - needs streaming or temp copy
        file_size = os.path.getsize(file_path)
        
        # For files > 50MB, use temp copy; otherwise stream
        if file_size > 50 * 1024 * 1024:  # 50MB threshold
            temp_path = self._create_temp_copy(file_path)
            if temp_path:
                return True, temp_path, "temp_copy"
            else:
                return False, file_path, "error:temp_copy_failed"
        else:
            # Return original path with stream method
            # The upload tool will handle streaming
            return True, file_path, "stream"
    
    def _normalize_linux_path(self, file_path: str) -> Tuple[bool, str, str]:
        """Normalize Linux path for Docker access"""
        
        # If already in /mnt/project/, it's mounted
        if file_path.startswith("/mnt/project/"):
            return True, file_path, "mounted"
        
        # If in Docker, check if path is accessible
        if self.in_docker:
            if os.path.exists(file_path):
                return True, file_path, "direct"
            else:
                return False, file_path, "error:not_accessible"
        
        # Outside Docker on Linux - needs streaming or temp copy
        file_size = os.path.getsize(file_path)
        
        if file_size > 50 * 1024 * 1024:
            temp_path = self._create_temp_copy(file_path)
            if temp_path:
                return True, temp_path, "temp_copy"
            else:
                return False, file_path, "error:temp_copy_failed"
        else:
            return True, file_path, "stream"
    
    def _create_temp_copy(self, file_path: str) -> Optional[str]:
        """Create temporary copy in mounted directory for large files"""
        import shutil
        import uuid
        
        try:
            # Determine temp directory based on environment
            if self.current_env == "windows":
                temp_dir = "c:\\Project\\EX-AI-MCP-Server\\temp\\uploads"
            else:
                temp_dir = "/mnt/project/EX-AI-MCP-Server/temp/uploads"
            
            os.makedirs(temp_dir, exist_ok=True)
            
            # Generate unique temp filename
            original_name = os.path.basename(file_path)
            temp_filename = f"{uuid.uuid4().hex}_{original_name}"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Copy file
            logger.info(f"[PATH_NORMALIZER] Creating temp copy: {file_path} -> {temp_path}")
            shutil.copy2(file_path, temp_path)
            
            # Convert to Linux path if on Windows
            if self.current_env == "windows":
                temp_path = temp_path.replace("c:\\Project\\", "/mnt/project/")
                temp_path = temp_path.replace("C:\\Project\\", "/mnt/project/")
                temp_path = temp_path.replace("\\", "/")
            
            return temp_path
            
        except Exception as e:
            logger.error(f"[PATH_NORMALIZER] Failed to create temp copy: {e}")
            return None
    
    def convert_windows_to_linux(self, windows_path: str) -> str:
        """
        Convert Windows path to Linux container path.
        
        Args:
            windows_path: Windows path (e.g., C:\\Project\\file.txt)
        
        Returns:
            Linux path (e.g., /mnt/project/file.txt)
        """
        if not ('\\' in windows_path or ':' in windows_path):
            # Already Linux format
            return windows_path
        
        # Convert C:\Project\... to /mnt/project/...
        linux_path = windows_path.replace("C:\\Project\\", "/mnt/project/")
        linux_path = linux_path.replace("c:\\Project\\", "/mnt/project/")
        linux_path = linux_path.replace("\\", "/")
        
        return linux_path
    
    def convert_linux_to_windows(self, linux_path: str) -> str:
        """
        Convert Linux container path to Windows path.
        
        Args:
            linux_path: Linux path (e.g., /mnt/project/file.txt)
        
        Returns:
            Windows path (e.g., C:\\Project\\file.txt)
        """
        if not linux_path.startswith('/mnt/'):
            # Already Windows format or not a mount path
            return linux_path
        
        # Convert /mnt/project/... to C:\Project\...
        windows_path = linux_path.replace("/mnt/project/", "C:\\Project\\")
        windows_path = windows_path.replace("/", "\\")
        
        return windows_path


# Global instance
_normalizer = None

def get_normalizer() -> PathNormalizer:
    """Get global PathNormalizer instance"""
    global _normalizer
    if _normalizer is None:
        _normalizer = PathNormalizer()
    return _normalizer


def normalize_path(file_path: str) -> Tuple[bool, str, str]:
    """
    Normalize any file path for Docker container access.
    
    Convenience function that uses the global normalizer instance.
    
    Args:
        file_path: Input file path (Windows or Linux format)
    
    Returns:
        Tuple of (success, normalized_path, method)
    """
    return get_normalizer().normalize_for_docker(file_path)


def convert_to_linux_path(windows_path: str) -> str:
    """Convert Windows path to Linux container path"""
    return get_normalizer().convert_windows_to_linux(windows_path)


def convert_to_windows_path(linux_path: str) -> str:
    """Convert Linux container path to Windows path"""
    return get_normalizer().convert_linux_to_windows(linux_path)

