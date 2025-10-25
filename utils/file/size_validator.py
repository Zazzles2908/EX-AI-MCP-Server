"""File size validation and recommendations for optimal file handling.

PHASE 2.3 ENHANCEMENT (2025-10-25): EXAI Recommendation #1
Implements file size validation with automatic suggestions for optimal file handling.

Rationale:
- Files >5KB should use kimi_upload_files workflow for 70-80% token savings
- Files <5KB can use files parameter for direct embedding
- Automatic warnings prevent token waste and improve agent usability
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# File size threshold for upload recommendation (5KB)
FILE_SIZE_THRESHOLD_KB = 5
FILE_SIZE_THRESHOLD_BYTES = FILE_SIZE_THRESHOLD_KB * 1024


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
            f"💡 RECOMMENDATION: Use kimi_upload_files workflow for 70-80% token savings:\n"
            f"\n"
            f"# Step 1: Upload files\n"
            f"upload_result = kimi_upload_files(files=[\n"
            f"    # Your {len(large_files)} large file(s)\n"
            f"])\n"
            f"\n"
            f"# Step 2: Chat with uploaded files\n"
            f"kimi_chat_with_files(\n"
            f"    prompt=\"Your question here\",\n"
            f"    file_ids=upload_result['file_ids'],\n"
            f"    model=\"kimi-k2-0905-preview\"\n"
            f")\n"
            f"\n"
            f"This approach saves tokens and enables multi-turn file analysis."
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

