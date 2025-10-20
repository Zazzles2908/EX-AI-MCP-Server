"""
Cross-platform path handling for Docker environments.

This module handles path validation and normalization for scenarios where
Windows host paths need to be mapped to Linux container paths.
"""

import os
import re
from pathlib import PureWindowsPath, PurePosixPath
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CrossPlatformPathHandler:
    """
    Handles cross-platform path validation and normalization for Docker environments
    where Windows host paths are mapped to Linux container paths.
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
        self.drive_mappings = drive_mappings or {'C:': '/app'}
        self.allowed_prefixes = allowed_prefixes or ['/app']
        
        # Regex to detect Windows absolute paths
        self.windows_path_pattern = re.compile(r'^[a-zA-Z]:[\\/]')
        
        # Regex to detect UNC paths (\\server\share)
        self.unc_path_pattern = re.compile(r'^\\\\[^\\]+\\[^\\]+')
    
    def normalize_path(self, file_path: str) -> Tuple[str, bool, Optional[str]]:
        """
        Normalize a cross-platform path to Linux format.
        
        Args:
            file_path: Input path in Windows or Linux format
            
        Returns:
            Tuple of (normalized_path, was_converted, error_message)
            - normalized_path: Path normalized to Linux format
            - was_converted: True if conversion occurred
            - error_message: Error message if validation fails, None otherwise
        """
        if not file_path or not isinstance(file_path, str):
            return file_path, False, "Error: Empty or invalid path provided"

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
        normalized = os.path.normpath(file_path)
        
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
        """Convert a Windows path to Linux path using drive mappings."""
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

        # Combine with Linux prefix
        # If linux_prefix is "/app" and path is "Project/EX-AI-MCP-Server/file.py"
        # Result should be "/app" (since the Windows path C:\Project\EX-AI-MCP-Server is mounted at /app)
        # We need to strip the common prefix

        # For now, assume the entire Windows path maps to the Linux prefix
        # This means C:\Project\EX-AI-MCP-Server\utils\file.py -> /app/utils/file.py
        # We need to find where the mount point is

        # Simple approach: if the path contains the project directory, strip it
        # C:\Project\EX-AI-MCP-Server\utils\file.py -> utils/file.py -> /app/utils/file.py
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
        normalized_path = os.path.normpath(normalized_path)

        # Validate the converted path
        normalized_path, _, error = self._validate_linux_path(normalized_path)
        if error:
            return normalized_path, True, error

        return normalized_path, True, None


# Singleton instance
_path_handler_instance = None


def get_path_handler() -> CrossPlatformPathHandler:
    """
    Factory function to create a configured path handler.
    Uses singleton pattern to avoid re-parsing environment variables.
    """
    global _path_handler_instance
    
    if _path_handler_instance is not None:
        return _path_handler_instance
    
    # Default mappings
    drive_mappings = {'C:': '/app'}
    
    # Try to get additional mappings from environment
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
    allowed_prefixes_str = os.getenv('EX_ALLOWED_EXTERNAL_PREFIXES', '/app')
    allowed_prefixes = [p.strip() for p in allowed_prefixes_str.split(',') if p.strip()]
    
    _path_handler_instance = CrossPlatformPathHandler(drive_mappings, allowed_prefixes)
    logger.debug(f"Initialized path handler with drive mappings: {drive_mappings}, allowed prefixes: {allowed_prefixes}")
    
    return _path_handler_instance


__all__ = ['CrossPlatformPathHandler', 'get_path_handler']

