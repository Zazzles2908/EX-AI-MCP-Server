"""
File Handling Utilities for EXAI MCP Server

Provides seamless file handling with automatic embed vs. upload decision.
Supports both Windows and Linux paths with automatic normalization.

Phase 5 Implementation (2025-10-19): Seamless file handling
- Automatic file size detection
- Path normalization (Windows ↔ Docker)
- Transparent upload mechanism
- Multi-factor decision logic
"""

from .smart_handler import smart_file_handler, SmartFileHandler
from typing import List, Dict, Any

__all__ = ['smart_file_handler', 'SmartFileHandler', 'handle_files']


async def handle_files(
    file_paths: List[str], 
    context: str = "", 
    force_embed: bool = False, 
    force_upload: bool = False
) -> Dict[str, Any]:
    """
    Convenience function for seamless file handling.
    
    Automatically decides whether to embed or upload files based on:
    - File size (>5KB → upload)
    - File type (binary/documents → upload, code → embed)
    - Estimated tokens (>1000 → upload)
    
    Args:
        file_paths: List of file paths (Windows or Linux format)
        context: Optional context for decision making
        force_embed: Force embedding even for large files
        force_upload: Force upload even for small files
        
    Returns:
        Dictionary with:
        - embedded_content: List of embedded file contents
        - file_ids: List of uploaded file IDs
        - metadata: List of file metadata
        - errors: List of errors encountered
        
    Example:
        >>> results = await handle_files(['C:\\Project\\file.py', '/path/to/doc.pdf'])
        >>> print(results['embedded_content'])  # file.py content
        >>> print(results['file_ids'])  # doc.pdf file_id
    """
    return await smart_file_handler.handle_files(
        file_paths, context, force_embed, force_upload
    )

