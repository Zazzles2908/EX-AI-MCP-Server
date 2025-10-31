"""
Utility functions for EX MCP Server

Reorganized structure (Phase 1.C + Phase 1 Path Consolidation):
- utils/path/ - Path normalization and validation (NEW - 2025-10-31)
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

# Phase 1 Path Consolidation: Re-export path utilities for backward compatibility
from .path import (
    PathNormalizer,
    validate_upload_path,
    validate_universal_upload_path,
    get_path_validation_examples,
    ApplicationAwarePathValidator,
    validate_file_path,
    default_validator,
)

# Re-export all subfolder modules for backward compatibility
from . import file
from . import conversation
from . import model
from . import config
from . import progress_utils
from . import infrastructure
from . import path  # NEW - Phase 1 consolidation

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
    # Path utilities (Phase 1 consolidation)
    "PathNormalizer",
    "validate_upload_path",
    "validate_universal_upload_path",
    "get_path_validation_examples",
    "ApplicationAwarePathValidator",
    "validate_file_path",
    "default_validator",
    # Submodules
    "file",
    "conversation",
    "model",
    "config",
    "progress_utils",
    "infrastructure",
    "path",  # NEW - Phase 1 consolidation
]
