"""
Docker-specific path validation for container environment.

This module provides validation utilities for Docker environment file uploads:
- Validates paths are in /mnt/project/ mount point
- Prevents path traversal attacks
- Provides detailed error messages for common mistakes
- Supports universal file access with automatic normalization

Phase 1 Path Consolidation (2025-10-31):
- Extracted from validation.py (lines 21-207)
- Part of utils/path/validation/ subdirectory structure
"""

import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


def validate_universal_upload_path(path: str) -> Tuple[bool, str, str]:
    """
    Universal path validation with automatic normalization.

    Accepts files from ANY location and normalizes them for Docker access.
    Supports three access methods:
    1. mounted - File is in /mnt/project/ (direct access)
    2. stream - File will be streamed from host
    3. temp_copy - Large file copied to temp directory

    Args:
        path: File path (Windows or Linux format, any location)

    Returns:
        Tuple of (is_valid, normalized_path_or_error, access_method)
        - is_valid: Whether the path is valid and accessible
        - normalized_path_or_error: Normalized path if valid, error message if not
        - access_method: How the file will be accessed ("mounted", "stream", "temp_copy")
    """
    try:
        # Import PathNormalizer from parent module
        from ..normalizer import PathNormalizer

        normalizer = PathNormalizer()
        # Normalize path for Docker access
        success, normalized_path, method = normalizer.normalize_for_docker(path)

        if not success:
            return False, f"❌ PATH NORMALIZATION FAILED\n{normalized_path}\nMethod: {method}", method

        logger.info(f"[UNIVERSAL_VALIDATION] Path: {path} -> {normalized_path} (method: {method})")

        # For mounted and temp_copy methods, validate the normalized path
        if method in ["mounted", "temp_copy"]:
            # Use standard validation for mounted paths
            is_valid, error_msg = validate_upload_path(normalized_path)
            if not is_valid:
                return False, error_msg, method

        # For stream method, path is valid as-is (will be read on host)
        return True, normalized_path, method

    except Exception as e:
        logger.error(f"[UNIVERSAL_VALIDATION] Error: {e}")
        return False, f"❌ VALIDATION ERROR\n{str(e)}", "error"


def validate_upload_path(path: str) -> Tuple[bool, str]:
    """
    Validate path for Docker environment upload.
    
    This function performs comprehensive validation to ensure:
    1. No Windows paths (contains : or \\)
    2. No relative paths (must start with /)
    3. Path is within /mnt/project/ mount point
    4. No path traversal attempts (../)
    5. Path length is reasonable (<4096 chars)
    6. No empty/null paths
    
    Args:
        path: The file path to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if path is valid, False otherwise
        - error_message: Empty string if valid, detailed error message if invalid
        
    Examples:
        >>> validate_upload_path("/mnt/project/EX-AI-MCP-Server/file.txt")
        (True, "")
        
        >>> validate_upload_path("c:\\Project\\file.txt")
        (False, "❌ PATH FORMAT ERROR\\nDetected Windows path...")
        
        >>> validate_upload_path("/mnt/project/../../../etc/passwd")
        (False, "❌ SECURITY ERROR\\nPath traversal detected...")
    """
    # Check for empty/null paths
    if not path or not path.strip():
        return (False, 
            "❌ PATH FORMAT ERROR\n"
            "Empty or null path provided\n\n"
            "✅ CORRECT FORMAT:\n"
            "/mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
            "🐳 DOCKER ENVIRONMENT:\n"
            "This system runs in Docker. Only files under c:\\Project\\ are accessible at /mnt/project/ in the container."
        )
    
    # Check path length (Linux typically supports up to 4096)
    if len(path) > 4096:
        return (False,
            f"❌ PATH FORMAT ERROR\n"
            f"Path too long: {len(path)} characters (max 4096)\n\n"
            f"Path: {path[:100]}...\n\n"
            f"Please use a shorter path."
        )
    
    # Check for Windows paths (contains : or backslashes)
    if ':' in path or '\\' in path:
        return (False,
            f"❌ PATH FORMAT ERROR\n"
            f"Detected Windows path: {path}\n\n"
            f"✅ CORRECT FORMAT:\n"
            f"/mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
            f"🐳 WHY THIS HAPPENS:\n"
            f"This system runs in Docker. Windows paths are converted to /app/ which doesn't contain your files.\n\n"
            f"📁 ACCESSIBLE FILES:\n"
            f"Only files under c:\\Project\\ are available at /mnt/project/ in the container.\n\n"
            f"🔧 QUICK FIX:\n"
            f"Replace 'c:\\Project\\' with '/mnt/project/'"
        )
    
    # Check for relative paths
    if not path.startswith('/'):
        return (False,
            f"❌ PATH FORMAT ERROR\n"
            f"Detected relative path: {path}\n\n"
            f"✅ CORRECT FORMAT:\n"
            f"/mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
            f"🐳 WHY THIS HAPPENS:\n"
            f"Relative paths don't work because the container's working directory is different.\n\n"
            f"🔧 QUICK FIX:\n"
            f"Use absolute Linux container path starting with /mnt/project/"
        )
    
    # Check for correct mount point
    if not path.startswith('/mnt/project/'):
        return (False,
            f"❌ PATH FORMAT ERROR\n"
            f"Path must start with /mnt/project/\n"
            f"Got: {path}\n\n"
            f"✅ CORRECT FORMAT:\n"
            f"/mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
            f"📁 ACCESSIBLE DIRECTORIES:\n"
            f"- /mnt/project/EX-AI-MCP-Server/\n"
            f"- /mnt/project/Personal_AI_Agent/\n\n"
            f"Only files under c:\\Project\\ are mounted to /mnt/project/ in the container."
        )
    
    # Normalize path and check for path traversal
    # CRITICAL: Use posixpath.normpath() instead of os.normpath()
    # to avoid Windows backslash conversion when running on Windows host
    try:
        import posixpath

        # Resolve the path to its canonical form using POSIX path rules
        # This ensures forward slashes are preserved regardless of host OS
        normalized = posixpath.normpath(path)

        # Check if normalized path still starts with /mnt/project/
        # This catches path traversal attempts like /mnt/project/../../../etc/passwd
        if not normalized.startswith('/mnt/project/'):
            return (False,
                f"❌ SECURITY ERROR\n"
                f"Path traversal detected\n"
                f"Original: {path}\n"
                f"Normalized: {normalized}\n\n"
                f"⚠️ SECURITY VIOLATION:\n"
                f"Attempted to access files outside /mnt/project/ mount point.\n\n"
                f"✅ CORRECT FORMAT:\n"
                f"/mnt/project/EX-AI-MCP-Server/filename.ext\n\n"
                f"Only files within /mnt/project/ are accessible."
            )
        
        # Additional check: ensure no .. components remain after normalization
        path_parts = Path(normalized).parts
        if '..' in path_parts:
            return (False,
                f"❌ SECURITY ERROR\n"
                f"Path contains '..' components: {path}\n\n"
                f"⚠️ SECURITY VIOLATION:\n"
                f"Path traversal attempts are not allowed.\n\n"
                f"✅ CORRECT FORMAT:\n"
                f"/mnt/project/EX-AI-MCP-Server/filename.ext"
            )
            
    except (ValueError, OSError) as e:
        return (False,
            f"❌ PATH VALIDATION ERROR\n"
            f"Invalid path: {path}\n"
            f"Error: {str(e)}\n\n"
            f"✅ CORRECT FORMAT:\n"
            f"/mnt/project/EX-AI-MCP-Server/filename.ext"
        )
    
    # All checks passed
    return (True, "")


def get_path_validation_examples() -> str:
    """
    Get examples of valid and invalid paths for documentation.
    
    Returns:
        Formatted string with examples
    """
    return """
PATH VALIDATION EXAMPLES:

✅ VALID PATHS:
- /mnt/project/EX-AI-MCP-Server/file.txt
- /mnt/project/Personal_AI_Agent/data.json
- /mnt/project/EX-AI-MCP-Server/docs/readme.md

❌ INVALID PATHS:
- c:\\Project\\file.txt (Windows path)
- C:/Project/file.txt (Windows path with forward slashes)
- ./file.txt (relative path)
- file.txt (relative path)
- /app/file.txt (wrong mount point)
- /mnt/project/../../../etc/passwd (path traversal)
- /mnt/project/EX-AI-MCP-Server/../../etc/passwd (path traversal)

🐳 DOCKER ENVIRONMENT:
- Windows host: c:\\Project\\
- Linux container: /mnt/project/
- Only files under c:\\Project\\ are accessible
"""

