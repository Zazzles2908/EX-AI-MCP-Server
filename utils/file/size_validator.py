"""File size validation and recommendations for optimal file handling.

PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI Comprehensive Recommendation
Implements file size validation with automatic suggestions for optimal file handling.

Based on EXAI consultation with kimi-thinking-preview (high thinking mode, web search enabled)
Continuation ID: c90cdeec-48bb-4d10-b075-925ebbf39c8a

Rationale:
- Files <50KB should use files parameter for direct embedding (updated from 5KB)
- Files 0.5MB-10MB should use kimi_upload_files for 70-80% token savings
- Files 0.5MB-5MB can use glm_upload_file for GLM-specific workflows
- Files >10MB should use Supabase storage for large file handling
- Automatic warnings prevent token waste and improve agent usability
"""

import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# PHASE 2.4 FIX (2025-10-26): EXAI COMPREHENSIVE FIX - Updated file size thresholds
# Based on EXAI consultation with kimi-thinking-preview
# Rationale: Optimize upload method selection for different file sizes

# File size thresholds (EXAI-recommended)
FILE_SIZE_EMBEDDING_KB = 50  # < 50KB: Use embedding (direct in prompt)
FILE_SIZE_EMBEDDING_BYTES = FILE_SIZE_EMBEDDING_KB * 1024

FILE_SIZE_KIMI_MIN_MB = 0.5  # 0.5MB-10MB: Use Kimi upload
FILE_SIZE_KIMI_MAX_MB = 10
FILE_SIZE_KIMI_MIN_BYTES = int(FILE_SIZE_KIMI_MIN_MB * 1024 * 1024)
FILE_SIZE_KIMI_MAX_BYTES = int(FILE_SIZE_KIMI_MAX_MB * 1024 * 1024)

FILE_SIZE_GLM_MIN_MB = 0.5  # 0.5MB-5MB: Use GLM upload
FILE_SIZE_GLM_MAX_MB = 5
FILE_SIZE_GLM_MIN_BYTES = int(FILE_SIZE_GLM_MIN_MB * 1024 * 1024)
FILE_SIZE_GLM_MAX_BYTES = int(FILE_SIZE_GLM_MAX_MB * 1024 * 1024)

FILE_SIZE_SUPABASE_MIN_MB = 10  # >10MB: Use Supabase storage
FILE_SIZE_SUPABASE_MIN_BYTES = int(FILE_SIZE_SUPABASE_MIN_MB * 1024 * 1024)

# Legacy threshold for backward compatibility
FILE_SIZE_THRESHOLD_KB = FILE_SIZE_EMBEDDING_KB
FILE_SIZE_THRESHOLD_BYTES = FILE_SIZE_EMBEDDING_BYTES


def get_file_size(file_path: str) -> Optional[int]:
    """Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes, or None if file doesn't exist or error occurs
    """
    try:
        if os.path.isfile(file_path):
            return os.path.getsize(file_path)
        return None
    except Exception as e:
        logger.debug(f"Failed to get size for {file_path}: {e}")
        return None


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 KB", "2.3 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def check_file_sizes(file_paths: list[str]) -> dict:
    """Check file sizes and generate recommendations.
    
    Args:
        file_paths: List of file paths to check
        
    Returns:
        Dictionary with:
        - total_size: Total size of all files in bytes
        - large_files: List of files exceeding threshold
        - warning_message: Optional warning message
        - recommendation: Optional recommendation message
    """
    total_size = 0
    large_files = []
    file_sizes = {}
    
    for file_path in file_paths:
        size = get_file_size(file_path)
        if size is not None:
            total_size += size
            file_sizes[file_path] = size
            
            if size > FILE_SIZE_THRESHOLD_BYTES:
                large_files.append({
                    "path": file_path,
                    "size": size,
                    "size_formatted": format_file_size(size)
                })
    
    result = {
        "total_size": total_size,
        "total_size_formatted": format_file_size(total_size),
        "large_files": large_files,
        "file_sizes": file_sizes,
        "warning_message": None,
        "recommendation": None
    }
    
    # Generate warnings and recommendations
    if large_files:
        file_list = "\n".join([
            f"  - {os.path.basename(f['path'])}: {f['size_formatted']}"
            for f in large_files
        ])

        result["warning_message"] = (
            f"⚠️  FILE SIZE WARNING: {len(large_files)} file(s) exceed {FILE_SIZE_THRESHOLD_KB}KB threshold:\n"
            f"{file_list}\n"
            f"Total size: {result['total_size_formatted']}"
        )

        result["recommendation"] = (
            f"💡 RECOMMENDATION: Use appropriate upload method based on file size:\n"
            f"\n"
            f"For files 0.5MB-10MB (recommended):\n"
            f"  1. upload_result = kimi_upload_files(files=[...])\n"
            f"  2. kimi_chat_with_files(prompt='...', file_ids=upload_result['file_ids'])\n"
            f"  → Saves 70-80% tokens\n"
            f"\n"
            f"For files 0.5MB-5MB (GLM workflows):\n"
            f"  file_id = glm_upload_file(file='...')\n"
            f"  → Alternative for GLM-specific use cases\n"
            f"\n"
            f"For files >10MB:\n"
            f"  → Use Supabase storage (contact administrator)\n"
            f"\n"
            f"Use select_upload_method(file_path) to get specific recommendations."
        )
    
    return result


def validate_and_warn(file_paths: list[str], tool_name: str = "unknown") -> Optional[str]:
    """Validate file sizes and return warning message if needed.
    
    This function is designed to be called by tools before processing files.
    It logs warnings and returns a message that can be included in tool responses.
    
    Args:
        file_paths: List of file paths to validate
        tool_name: Name of the tool calling this function
        
    Returns:
        Warning message if files exceed threshold, None otherwise
    """
    if not file_paths:
        return None
    
    result = check_file_sizes(file_paths)
    
    if result["large_files"]:
        # Log warning
        logger.warning(
            f"[FILE_SIZE] {tool_name}: {len(result['large_files'])} file(s) exceed {FILE_SIZE_THRESHOLD_KB}KB threshold. "
            f"Total size: {result['total_size_formatted']}. "
            f"Consider using kimi_upload_files for token savings."
        )
        
        # Return combined warning and recommendation
        return f"{result['warning_message']}\n\n{result['recommendation']}"
    
    return None


def should_recommend_upload(file_paths: list[str]) -> bool:
    """Check if file upload workflow should be recommended.

    Args:
        file_paths: List of file paths to check

    Returns:
        True if any file exceeds threshold, False otherwise
    """
    for file_path in file_paths:
        size = get_file_size(file_path)
        if size and size > FILE_SIZE_THRESHOLD_BYTES:
            return True
    return False


def select_upload_method(file_path: str) -> Dict[str, any]:
    """
    Select optimal upload method based on file size.

    PHASE 2.4 ENHANCEMENT (2025-10-26): EXAI-recommended upload method selection

    This function helps AI agents understand which upload method to use based on file size.
    It provides clear guidance and rationale for the selection.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with:
        - method: str - 'embedding', 'kimi_upload', 'glm_upload', 'supabase_storage', or 'error'
        - reason: str - Explanation for selection
        - size: int - File size in bytes
        - size_formatted: str - Human-readable size
        - recommendation: str - Detailed recommendation for agents

    Example:
        >>> result = select_upload_method("large_file.pdf")
        >>> print(result['method'])  # 'kimi_upload'
        >>> print(result['reason'])  # 'File size (2.5 MB) in range 0.5MB-10MB...'
        >>> print(result['recommendation'])  # 'Use kimi_upload_files tool...'
    """
    size = get_file_size(file_path)
    if size is None:
        return {
            'method': 'error',
            'reason': 'File not found or inaccessible',
            'size': 0,
            'size_formatted': '0 B',
            'recommendation': 'Check file path and permissions'
        }

    size_formatted = format_file_size(size)

    # < 50KB: Use embedding
    if size < FILE_SIZE_EMBEDDING_BYTES:
        return {
            'method': 'embedding',
            'reason': f'File size ({size_formatted}) < 50KB - optimal for direct embedding',
            'size': size,
            'size_formatted': size_formatted,
            'recommendation': (
                f"Use the 'files' parameter to embed this file directly in your prompt:\n"
                f"  files=['{file_path}']\n"
                f"This is the most efficient method for small files."
            )
        }

    # 5-20MB: Use Supabase gateway for GLM (pre-signed URLs)
    if 5 * 1024 * 1024 <= size <= 20 * 1024 * 1024:
        return {
            'method': 'supabase_gateway_glm',
            'reason': f'File size ({size_formatted}) in range 5-20MB - use Supabase gateway with pre-signed URLs for GLM',
            'size': size,
            'size_formatted': size_formatted,
            'recommendation': (
                f"Use Supabase gateway approach for GLM (EXAI-validated):\n"
                f"  from tools.providers.glm.glm_files import upload_via_supabase_gateway_glm\n"
                f"  from src.storage.supabase_client import get_storage_manager\n"
                f"  \n"
                f"  storage = get_storage_manager()\n"
                f"  result = await upload_via_supabase_gateway_glm('{file_path}', storage)\n"
                f"  glm_file_id = result['glm_file_id']\n"
                f"  \n"
                f"This approach:\n"
                f"  1. Uploads to Supabase Storage first\n"
                f"  2. Generates pre-signed URL (60s expiration)\n"
                f"  3. Downloads and uploads to GLM API\n"
                f"  4. Centralized tracking in Supabase\n"
                f"  \n"
                f"Source: EXAI Consultation c90cdeec-48bb-4d10-b075-925ebbf39c8a"
            )
        }

    # 5-100MB: Use Supabase gateway for Kimi (direct URL extraction)
    if 5 * 1024 * 1024 <= size <= 100 * 1024 * 1024:
        return {
            'method': 'supabase_gateway_kimi',
            'reason': f'File size ({size_formatted}) in range 5-100MB - use Supabase gateway with direct URL extraction for Kimi',
            'size': size,
            'size_formatted': size_formatted,
            'recommendation': (
                f"Use Supabase gateway approach for Kimi (EXAI-validated):\n"
                f"  from tools.providers.kimi.kimi_files import upload_via_supabase_gateway_kimi\n"
                f"  from src.storage.supabase_client import get_storage_manager\n"
                f"  \n"
                f"  storage = get_storage_manager()\n"
                f"  result = await upload_via_supabase_gateway_kimi('{file_path}', storage)\n"
                f"  kimi_file_id = result['kimi_file_id']\n"
                f"  \n"
                f"This approach:\n"
                f"  1. Uploads to Supabase Storage first\n"
                f"  2. Gets public URL from Supabase\n"
                f"  3. Kimi extracts file directly from URL (no download needed)\n"
                f"  4. Centralized tracking in Supabase\n"
                f"  \n"
                f"Kimi API endpoint: https://api.moonshot.cn/api/v1/files/upload_url\n"
                f"Source: EXAI Consultation c90cdeec-48bb-4d10-b075-925ebbf39c8a"
            )
        }

    # 0.5MB-5MB: Use direct upload (current approach - fast)
    if FILE_SIZE_KIMI_MIN_BYTES <= size <= FILE_SIZE_GLM_MAX_BYTES:
        return {
            'method': 'direct_upload',
            'reason': f'File size ({size_formatted}) in range 0.5-5MB - use direct upload (fastest)',
            'size': size,
            'size_formatted': size_formatted,
            'recommendation': (
                f"Use direct upload for optimal speed:\n"
                f"  \n"
                f"For Kimi:\n"
                f"  upload_result = kimi_upload_files(files=['{file_path}'])\n"
                f"  kimi_chat_with_files(prompt='...', file_ids=upload_result['file_ids'])\n"
                f"  → Saves 70-80% tokens\n"
                f"  \n"
                f"For GLM:\n"
                f"  file_id = glm_upload_file(file='{file_path}')\n"
                f"  → Alternative for GLM-specific workflows\n"
                f"  \n"
                f"Note: For 5-20MB files, consider Supabase gateway for centralized tracking."
            )
        }

    # >10MB: Use Supabase storage
    if size > FILE_SIZE_SUPABASE_MIN_BYTES:
        return {
            'method': 'supabase_storage',
            'reason': f'File size ({size_formatted}) > 10MB - use Supabase storage for large files',
            'size': size,
            'size_formatted': size_formatted,
            'recommendation': (
                f"Use Supabase storage for large file handling:\n"
                f"  This file exceeds API upload limits.\n"
                f"  Contact system administrator for large file handling."
            )
        }

    # Fallback: embedding (for files between 50KB and 0.5MB)
    return {
        'method': 'embedding',
        'reason': f'File size ({size_formatted}) - using embedding as fallback',
        'size': size,
        'size_formatted': size_formatted,
        'recommendation': (
            f"Use the 'files' parameter to embed this file:\n"
            f"  files=['{file_path}']\n"
            f"Note: File is larger than optimal embedding size but smaller than upload threshold."
        )
    }


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with sample files
    test_files = [
        "c:\\Project\\EX-AI-MCP-Server\\.env.docker",
        "c:\\Project\\EX-AI-MCP-Server\\config.py",
        "c:\\Project\\EX-AI-MCP-Server\\README.md"
    ]
    
    print("\nFile Size Validation Test")
    print("=" * 60)
    
    result = check_file_sizes(test_files)
    
    if result["warning_message"]:
        print(result["warning_message"])
        print()
        print(result["recommendation"])
    else:
        print(f"✅ All files are under {FILE_SIZE_THRESHOLD_KB}KB threshold")
        print(f"Total size: {result['total_size_formatted']}")

