"""
Centralized configuration modules for EXAI tools.

This package provides shared configuration and guidance across all tools,
preventing duplication and providing single sources of truth.

Created: 2025-10-26
Purpose: Centralize file handling guidance and other shared configurations
"""

from .file_handling_guidance import FILE_PATH_GUIDANCE, FILE_UPLOAD_GUIDANCE

__all__ = ['FILE_PATH_GUIDANCE', 'FILE_UPLOAD_GUIDANCE']

