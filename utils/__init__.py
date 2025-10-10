"""
Utility functions for EX MCP Server

Reorganized structure (Phase 1.C):
- utils/file/ - File operations and utilities
- utils/conversation/ - Conversation management
- utils/model/ - Model context and token utilities
- utils/config/ - Configuration utilities
- utils/progress_utils/ - Progress messages (renamed to avoid shadowing progress.py)
- utils/infrastructure/ - Infrastructure utilities

High-traffic files remain at root for easy imports:
- progress.py, observability.py, cache.py, client_info.py,
  tool_events.py, http_client.py, logging_unified.py
"""

# Re-export from subfolders for backward compatibility
from .file.types import CODE_EXTENSIONS, FILE_CATEGORIES, PROGRAMMING_EXTENSIONS, TEXT_EXTENSIONS
from .file.operations import expand_paths, read_file_content, read_files
from .config.security import EXCLUDED_DIRS
from .model.token_utils import check_token_limit, estimate_tokens
from .cache import get_session_cache, make_session_key, MemoryLRUTTL

# Re-export all subfolder modules for backward compatibility
from . import file
from . import conversation
from . import model
from . import config
from . import progress_utils
from . import infrastructure

__all__ = [
    "read_files",
    "read_file_content",
    "expand_paths",
    "CODE_EXTENSIONS",
    "PROGRAMMING_EXTENSIONS",
    "TEXT_EXTENSIONS",
    "FILE_CATEGORIES",
    "EXCLUDED_DIRS",
    "estimate_tokens",
    "check_token_limit",
    "get_session_cache",
    "make_session_key",
    "MemoryLRUTTL",
    # Submodules
    "file",
    "conversation",
    "model",
    "config",
    "progress_utils",
    "infrastructure",
]
