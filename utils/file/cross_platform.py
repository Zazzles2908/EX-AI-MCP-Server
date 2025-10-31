"""
Cross-platform path handling for Docker environments.

This module handles path validation and normalization for scenarios where
Windows host paths need to be mapped to Linux container paths.

PHASE 2.3.2 (2025-10-22): Enhanced with caching and dual mapping support
- Added LRU cache for performance
- Support for both Docker (/app/) and WSL (/mnt/c/) mappings
- Auto-detection of environment (Docker vs WSL)
- Project marker extraction (EX-AI-MCP-Server)
"""

import os
import re
from pathlib import PureWindowsPath, PurePosixPath
from typing import Tuple, Optional, Dict
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class CrossPlatformPathHandler:
    """
    Handles cross-platform path validation and normalization for Docker environments
    where Windows host paths are mapped to Linux container paths.

    PHASE 2.3.2 (2025-10-22): Enhanced with caching and environment detection
    """

    def __init__(self,
                 drive_mappings: Optional[Dict[str, str]] = None,
                 allowed_prefixes: Optional[list] = None):
        """
        Initialize with custom drive mappings and allowed prefixes.

        Args:
            drive_mappings: Dict mapping Windows drive letters to Linux paths
                           e.g., {'C:': '/app'}
            allowed_prefixes: List of allowed path prefixes in Linux format
        """
        # Auto-detect environment if no mappings provided
        if drive_mappings is None:
            drive_mappings = self._detect_environment_mappings()

        self.drive_mappings = drive_mappings
        # FILE UPLOAD FIX (2025-10-28): Added /mnt/project to allowed prefixes
        self.allowed_prefixes = allowed_prefixes or ['/app', '/mnt/c', '/mnt/project']

        # Regex to detect Windows absolute paths
        self.windows_path_pattern = re.compile(r'^[a-zA-Z]:[\\/]')

        # Regex to detect UNC paths (\\server\share)
        self.unc_path_pattern = re.compile(r'^\\\\[^\\]+\\[^\\]+')

        # Statistics tracking
        self._normalization_count = 0
        self._cache_hits = 0

    def _detect_environment_mappings(self) -> Dict[str, str]:
        """
        Auto-detect environment and return appropriate drive mappings.

        FILE UPLOAD FIX (2025-10-28): Updated to use /mnt/project for Docker
        This matches the new volume mount: c:\Project -> /mnt/project

        FIX (2025-10-30): When running on Windows host, default to /mnt/project
        since files will be accessed via Docker container with /mnt/project mount

        Returns:
            Dict mapping drive letters to Linux paths
        """
        import platform

        is_windows = platform.system() == "Windows"
        is_docker = os.path.exists('/app')
        is_wsl = os.path.exists('/mnt/c')
        is_project_mount = os.path.exists('/mnt/project')

        if is_docker and is_project_mount:
            logger.debug("Detected Docker environment with /mnt/project mount - using /mnt/project/ mappings")
            # FILE UPLOAD FIX: Map C: to /mnt/project for file upload support
            # This allows accessing files from c:\Project\... via /mnt/project/...
            return {'C:': '/mnt/project', 'D:': '/mnt/project', 'E:': '/mnt/project'}
        elif is_docker:
            logger.debug("Detected Docker environment - using /app/ mappings")
            return {'C:': '/app', 'D:': '/app', 'E:': '/app'}
        elif is_wsl:
            logger.debug("Detected WSL environment - using /mnt/ mappings")
            return {'C:': '/mnt/c', 'D:': '/mnt/d', 'E:': '/mnt/e'}
        elif is_windows:
            # FIX (2025-10-30): When running on Windows host, assume files will be
            # accessed via Docker container with /mnt/project mount
            logger.debug("Detected Windows host - using /mnt/project/ mappings for Docker access")
            return {'C:': '/mnt/project', 'D:': '/mnt/project', 'E:': '/mnt/project'}
        else:
            logger.debug("Unknown environment - defaulting to Docker /app/ mappings")
            return {'C:': '/app', 'D:': '/app', 'E:': '/app'}
    
    @lru_cache(maxsize=256)
    def normalize_path_cached(self, file_path: str) -> Tuple[str, bool, Optional[str]]:
        """
        Cached version of normalize_path for performance.

        PHASE 2.3.2 (2025-10-22): Added LRU cache for frequently accessed paths

        Args:
            file_path: Input path in Windows or Linux format

        Returns:
            Tuple of (normalized_path, was_converted, error_message)
        """
        self._cache_hits += 1
        return self.normalize_path(file_path)

    def normalize_path(self, file_path: str) -> Tuple[str, bool, Optional[str]]:
        """
        Normalize a cross-platform path to Linux format.

        PHASE 2.3.2 (2025-10-22): Enhanced with project marker extraction
        CRITICAL FIX (2025-10-23): Handle double-prefixed paths from workflow tools

        Args:
            file_path: Input path in Windows or Linux format

        Returns:
            Tuple of (normalized_path, was_converted, error_message)
            - normalized_path: Path normalized to Linux format
            - was_converted: True if conversion occurred
            - error_message: Error message if validation fails, None otherwise
        """
        self._normalization_count += 1

        if not file_path or not isinstance(file_path, str):
            return file_path, False, "Error: Empty or invalid path provided"

        # CRITICAL FIX (2025-10-23): Handle double-prefixed paths
        # Workflow tools sometimes pass paths like "/app/c:/Project/..." or "/app/c:\Project\..."
        # which are already partially normalized. Strip the incorrect /app/ prefix to get back to raw Windows path.
        # UPDATED: Handle both forward slashes (/app/c:/) and backslashes (/app/c:\)
        if file_path.startswith('/app/c:/') or file_path.startswith('/app/C:/') or \
           file_path.startswith('/app/c:\\') or file_path.startswith('/app/C:\\'):
            logger.warning(f"[PATH_FIX] Detected double-prefixed path, stripping /app/ prefix: {file_path}")
            file_path = file_path[5:]  # Remove '/app/' prefix (5 characters)
            logger.info(f"[PATH_FIX] Corrected path: {file_path}")

        # CRITICAL: Check Windows paths FIRST before os.path.isabs()
        # because os.path.isabs() returns True for Windows paths on Windows,
        # which would incorrectly route them to _validate_linux_path()

        # Check if it's a Windows absolute path with drive letter
        if self.windows_path_pattern.match(file_path):
            return self._convert_windows_path(file_path)

        # Check if it's a Windows UNC path
        if self.unc_path_pattern.match(file_path):
            return file_path, False, "Error: UNC paths are not supported in this environment"

        # Check if it's already a Linux absolute path
        if os.path.isabs(file_path):
            return self._validate_linux_path(file_path)
        
        # If we reach here, it's a relative path or unrecognized format
        return (
            file_path, 
            False, 
            f"Error: All file paths must be FULL absolute paths to real files / folders - DO NOT SHORTEN. "
            f"Received relative path: {file_path}\n"
            f"Please provide the full absolute path (Windows: C:\\..., Linux/Mac: /...)"
        )
    
    def _validate_linux_path(self, file_path: str) -> Tuple[str, bool, Optional[str]]:
        """Validate a Linux absolute path against allowed prefixes."""
        # Normalize the path to remove redundant components
        # FIX (2025-10-30): Use posixpath.normpath() to preserve forward slashes on Windows
        import posixpath
        normalized = posixpath.normpath(file_path)
        
        # Check if the path is within allowed prefixes
        is_allowed = any(normalized.startswith(prefix) for prefix in self.allowed_prefixes)
        
        if not is_allowed and os.getenv('EX_ALLOW_EXTERNAL_PATHS', 'false').lower() != 'true':
            return (
                normalized, 
                False, 
                f"Error: Path {normalized} is not within allowed prefixes: {', '.join(self.allowed_prefixes)}"
            )
        
        return normalized, False, None
    
    def _convert_windows_path(self, file_path: str) -> Tuple[str, bool, Optional[str]]:
        """
        Convert a Windows path to Linux path using drive mappings.

        FILE UPLOAD FIX (2025-10-28): Updated to handle /mnt/project mount
        - For /app mount: c:\Project\EX-AI-MCP-Server\src\file.py -> /app/src/file.py
        - For /mnt/project mount: c:\Project\EX-AI-MCP-Server\src\file.py -> /mnt/project/EX-AI-MCP-Server/src/file.py
        """
        # Extract drive letter (case insensitive)
        drive_letter = file_path[0:2].upper()

        # Get the corresponding Linux path
        if drive_letter not in self.drive_mappings:
            return (
                file_path,
                False,
                f"Error: Windows drive {drive_letter} is not mapped. Available mappings: {list(self.drive_mappings.keys())}"
            )

        linux_prefix = self.drive_mappings[drive_letter]

        # Convert Windows path to Linux path
        # Replace backslashes with forward slashes and remove drive letter
        path_without_drive = file_path[2:].replace('\\', '/')  # Remove "C:" and convert slashes

        # Remove leading slash if present (C:\path becomes /path, we want path)
        if path_without_drive.startswith('/'):
            path_without_drive = path_without_drive[1:]

        # FILE UPLOAD FIX (2025-10-28): Different logic for /mnt/project vs /app
        if linux_prefix == '/mnt/project':
            # For /mnt/project mount: keep full path after drive letter
            # c:\Project\EX-AI-MCP-Server\src\file.py -> /mnt/project/Project/EX-AI-MCP-Server/src/file.py
            # But we want: /mnt/project/EX-AI-MCP-Server/src/file.py
            # So strip "Project/" prefix if present
            if path_without_drive.startswith('Project/'):
                path_without_drive = path_without_drive[8:]  # Remove "Project/"

            normalized_path = linux_prefix + '/' + path_without_drive
        else:
            # For /app mount: strip project marker to get relative path
            # c:\Project\EX-AI-MCP-Server\src\file.py -> /app/src/file.py
            project_marker = "EX-AI-MCP-Server"
            if project_marker in path_without_drive:
                # Find the position after the project marker
                parts = path_without_drive.split('/')
                try:
                    marker_index = parts.index(project_marker)
                    # Take everything after the project marker
                    relative_parts = parts[marker_index + 1:]
                    path_without_drive = '/'.join(relative_parts)
                except ValueError:
                    pass  # Marker not found, use full path

            # Combine with Linux prefix
            if path_without_drive:
                normalized_path = linux_prefix + '/' + path_without_drive
            else:
                normalized_path = linux_prefix

        # Normalize the resulting path
        # FIX (2025-10-30): Use posixpath.normpath() instead of os.path.normpath()
        # to preserve forward slashes on Windows
        import posixpath
        normalized_path = posixpath.normpath(normalized_path)

        # Validate the converted path
        normalized_path, _, error = self._validate_linux_path(normalized_path)
        if error:
            return normalized_path, True, error

        return normalized_path, True, None

    def clear_cache(self) -> None:
        """
        Clear the path normalization cache.

        PHASE 2.3.2 (2025-10-22): Added cache management
        """
        self.normalize_path_cached.cache_clear()
        logger.debug("Path normalization cache cleared")

    def get_stats(self) -> Dict[str, any]:
        """
        Get normalization statistics.

        PHASE 2.3.2 (2025-10-22): Added statistics tracking

        Returns:
            Dict with normalization statistics
        """
        cache_info = self.normalize_path_cached.cache_info()
        return {
            'total_normalizations': self._normalization_count,
            'cache_hits': cache_info.hits,
            'cache_misses': cache_info.misses,
            'cache_size': cache_info.currsize,
            'cache_maxsize': cache_info.maxsize,
            'hit_rate': cache_info.hits / (cache_info.hits + cache_info.misses) if (cache_info.hits + cache_info.misses) > 0 else 0.0
        }


# Singleton instance
_path_handler_instance = None


def get_path_handler() -> CrossPlatformPathHandler:
    """
    Factory function to create a configured path handler.
    Uses singleton pattern to avoid re-parsing environment variables.

    FIX (2025-10-30): Use auto-detection instead of hardcoded defaults
    """
    global _path_handler_instance

    if _path_handler_instance is not None:
        return _path_handler_instance

    # FIX (2025-10-30): Create temporary instance to use auto-detection
    temp_handler = CrossPlatformPathHandler()
    drive_mappings = temp_handler._detect_environment_mappings()

    # Try to get additional mappings from environment (override auto-detection)
    # Format: C:/app,D:/data,E:/shared
    env_mappings = os.getenv('EX_DRIVE_MAPPINGS', '')
    if env_mappings:
        try:
            for mapping in env_mappings.split(','):
                if ':' in mapping and '/' in mapping:
                    parts = mapping.split('/', 1)
                    if len(parts) == 2:
                        drive = parts[0].strip().upper()
                        if not drive.endswith(':'):
                            drive += ':'
                        path = '/' + parts[1].strip()
                        drive_mappings[drive] = path
                        logger.debug(f"Added drive mapping: {drive} -> {path}")
        except Exception as e:
            # Log error but continue with default mappings
            logger.warning(f"Failed to parse drive mappings from EX_DRIVE_MAPPINGS: {e}")

    # Get allowed prefixes from environment
    # FIX (2025-10-30): Default to /mnt/project instead of /app
    allowed_prefixes_str = os.getenv('EX_ALLOWED_EXTERNAL_PREFIXES', '/app,/mnt/project')
    allowed_prefixes = [p.strip() for p in allowed_prefixes_str.split(',') if p.strip()]

    _path_handler_instance = CrossPlatformPathHandler(drive_mappings, allowed_prefixes)
    logger.debug(f"Initialized path handler with drive mappings: {drive_mappings}, allowed prefixes: {allowed_prefixes}")

    return _path_handler_instance


__all__ = ['CrossPlatformPathHandler', 'get_path_handler']

