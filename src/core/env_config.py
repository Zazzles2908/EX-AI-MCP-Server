"""
Centralized environment variable configuration.

This module provides a single source of truth for all environment variable access,
replacing scattered os.getenv() calls throughout the codebase.
"""

import os
from typing import Optional


def _env_true(key: str, default: str = "false") -> bool:
    """Check if environment variable is set to a truthy value."""
    return os.getenv(key, default).strip().lower() in ("true", "1", "yes", "on")


def _get_int(key: str, default: int) -> int:
    """Get integer from environment variable with fallback."""
    try:
        return int(os.getenv(key, str(default)))
    except (ValueError, TypeError):
        return default


class ClientConfig:
    """Client-specific configuration (tool filtering, defaults, etc.)."""
    
    @staticmethod
    def get_tool_allowlist() -> str:
        """Get CLIENT_TOOL_ALLOWLIST."""
        return os.getenv("CLIENT_TOOL_ALLOWLIST", "")
    
    @staticmethod
    def get_tool_denylist() -> str:
        """Get CLIENT_TOOL_DENYLIST."""
        return os.getenv("CLIENT_TOOL_DENYLIST", "")
    
    @staticmethod
    def get_max_workflow_steps() -> int:
        """Get CLIENT_MAX_WORKFLOW_STEPS."""
        return _get_int("CLIENT_MAX_WORKFLOW_STEPS", 0)
    
    @staticmethod
    def defaults_use_websearch() -> bool:
        """Get CLIENT_DEFAULTS_USE_WEBSEARCH."""
        return _env_true("CLIENT_DEFAULTS_USE_WEBSEARCH")
    
    @staticmethod
    def get_default_thinking_mode() -> str:
        """Get CLIENT_DEFAULT_THINKING_MODE."""
        return os.getenv("CLIENT_DEFAULT_THINKING_MODE", "medium").strip().lower()


class ProviderConfig:
    """Provider-specific configuration (GLM, Kimi)."""
    
    # GLM Configuration
    @staticmethod
    def get_glm_api_key() -> str:
        """Get GLM_API_KEY."""
        return os.getenv("GLM_API_KEY", "").strip()
    
    @staticmethod
    def get_glm_base_url() -> str:
        """Get GLM_BASE_URL."""
        return os.getenv("GLM_BASE_URL", "https://api.z.ai").strip()
    
    @staticmethod
    def glm_web_browsing_enabled() -> bool:
        """Get GLM_ENABLE_WEB_BROWSING."""
        return _env_true("GLM_ENABLE_WEB_BROWSING")
    
    @staticmethod
    def glm_stream_enabled() -> bool:
        """Get GLM_STREAM_ENABLED."""
        return _env_true("GLM_STREAM_ENABLED")
    
    # Kimi Configuration
    @staticmethod
    def get_kimi_api_key() -> str:
        """Get KIMI_API_KEY."""
        return os.getenv("KIMI_API_KEY", "").strip()
    
    @staticmethod
    def get_kimi_base_url() -> str:
        """Get KIMI_BASE_URL."""
        return os.getenv("KIMI_BASE_URL", "https://api.moonshot.ai/v1").strip()
    
    @staticmethod
    def kimi_internet_search_enabled() -> bool:
        """Get KIMI_ENABLE_INTERNET_SEARCH."""
        return _env_true("KIMI_ENABLE_INTERNET_SEARCH")
    
    @staticmethod
    def get_test_files_dir() -> str:
        """Get TEST_FILES_DIR for file upload functionality."""
        return os.getenv("TEST_FILES_DIR", "").strip()


class SystemConfig:
    """System-wide configuration (timeouts, modes, etc.)."""
    
    @staticmethod
    def is_auto_mode() -> bool:
        """Get EX_AUTO_MODE."""
        return _env_true("EX_AUTO_MODE")
    
    @staticmethod
    def get_http_client_timeout() -> int:
        """Get HTTP_CLIENT_TIMEOUT_SECS."""
        return _get_int("HTTP_CLIENT_TIMEOUT_SECS", 30)
    
    @staticmethod
    def get_log_level() -> str:
        """Get LOG_LEVEL."""
        return os.getenv("LOG_LEVEL", "INFO").upper()


# Convenience exports for backward compatibility
def get_client_tool_allowlist() -> str:
    """Get CLIENT_TOOL_ALLOWLIST."""
    return ClientConfig.get_tool_allowlist()


def get_client_tool_denylist() -> str:
    """Get CLIENT_TOOL_DENYLIST."""
    return ClientConfig.get_tool_denylist()


def get_client_max_workflow_steps() -> int:
    """Get CLIENT_MAX_WORKFLOW_STEPS."""
    return ClientConfig.get_max_workflow_steps()


def client_defaults_use_websearch() -> bool:
    """Get CLIENT_DEFAULTS_USE_WEBSEARCH."""
    return ClientConfig.defaults_use_websearch()


def get_client_default_thinking_mode() -> str:
    """Get CLIENT_DEFAULT_THINKING_MODE."""
    return ClientConfig.get_default_thinking_mode()

