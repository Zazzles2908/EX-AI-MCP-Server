"""
File reading utilities with directory support and token management

This module provides secure file access functionality for the MCP server.
It implements critical security measures to prevent unauthorized file access
and manages token limits to ensure efficient API usage.

Key Features:
- Path validation and sandboxing to prevent directory traversal attacks
- Support for both individual files and recursive directory reading
- Token counting and management to stay within API limits
- Automatic file type detection and filtering
- Comprehensive error handling with informative messages

Security Model:
- All file access is restricted to PROJECT_ROOT and its subdirectories
- Absolute paths are required to prevent ambiguity
- Symbolic links are resolved to ensure they stay within bounds

CONVERSATION MEMORY INTEGRATION:
This module works with the conversation memory system to support efficient
multi-turn file handling:

1. DEDUPLICATION SUPPORT:
   - File reading functions are called by conversation-aware tools
   - Supports newest-first file prioritization by providing accurate token estimation
   - Enables efficient file content caching and token budget management

2. TOKEN BUDGET OPTIMIZATION:
   - Provides accurate token estimation for file content before reading
   - Supports the dual prioritization strategy by enabling precise budget calculations
   - Enables tools to make informed decisions about which files to include

3. CROSS-TOOL FILE PERSISTENCE:
   - File reading results are used across different tools in conversation chains
   - Consistent file access patterns support conversation continuation scenarios
   - Error handling preserves conversation flow when files become unavailable
"""

# Import all functions from specialized modules
from .file_utils_security import (
    _is_builtin_custom_models_config,
    is_mcp_directory,
    get_user_home_directory,
    is_home_directory_root,
    resolve_and_validate_path,
)

from .file_utils_reading import (
    detect_file_type,
    should_add_line_numbers,
    read_file_content,
    read_files,
)

from .file_utils_expansion import expand_paths

from .file_utils_tokens import (
    estimate_file_tokens,
    check_files_size_limit,
    check_total_file_size,
)

from .file_utils_json import (
    read_json_file,
    write_json_file,
)

from .file_utils_helpers import (
    get_file_size,
    ensure_directory_exists,
    is_text_file,
    read_file_safely,
)

# Re-export all public functions for backward compatibility
__all__ = [
    # Security
    "_is_builtin_custom_models_config",
    "is_mcp_directory",
    "get_user_home_directory",
    "is_home_directory_root",
    "resolve_and_validate_path",
    # Reading
    "detect_file_type",
    "should_add_line_numbers",
    "read_file_content",
    "read_files",
    # Expansion
    "expand_paths",
    # Tokens
    "estimate_file_tokens",
    "check_files_size_limit",
    "check_total_file_size",
    # JSON
    "read_json_file",
    "write_json_file",
    # Helpers
    "get_file_size",
    "ensure_directory_exists",
    "is_text_file",
    "read_file_safely",
]
