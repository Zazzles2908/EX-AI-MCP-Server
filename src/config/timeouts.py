"""
Centralized timeout and retry configuration for EX-AI-MCP-Server.
Provides configurable defaults and environment variable overrides.
"""

import os
from typing import Dict, Any


class TimeoutConfig:
    """Centralized timeout configuration with environment variable support."""
    
    # Kimi-specific timeouts
    KIMI_FILES_FETCH_TIMEOUT_SECS = float(os.getenv("KIMI_FILES_FETCH_TIMEOUT_SECS", "120"))
    KIMI_FILES_FETCH_RETRIES = int(os.getenv("KIMI_FILES_FETCH_RETRIES", "5"))
    KIMI_FILES_FETCH_BASE_DELAY = float(os.getenv("KIMI_FILES_FETCH_BASE_DELAY", "1.0"))
    KIMI_FILES_FETCH_MAX_DELAY = float(os.getenv("KIMI_FILES_FETCH_MAX_DELAY", "60.0"))
    KIMI_FILES_FETCH_BACKOFF_FACTOR = float(os.getenv("KIMI_FILES_FETCH_BACKOFF_FACTOR", "2.0"))
    
    KIMI_CHAT_TOOL_TIMEOUT_SECS = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_SECS", "180"))
    KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS = float(os.getenv("KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS", "300"))
    KIMI_MF_CHAT_TIMEOUT_SECS = float(os.getenv("KIMI_MF_CHAT_TIMEOUT_SECS", "180"))
    
    # GLM-specific timeouts
    GLM_WEB_SEARCH_TIMEOUT_SECS = float(os.getenv("GLM_WEB_SEARCH_TIMEOUT_SECS", "60"))
    GLM_WEB_BROWSE_CHAT_TIMEOUT_SECS = float(os.getenv("GLM_WEB_BROWSE_CHAT_TIMEOUT_SECS", "120"))
    GLM_MF_CHAT_TIMEOUT_SECS = float(os.getenv("GLM_MF_CHAT_TIMEOUT_SECS", "60"))
    GLM_FILE_UPLOAD_TIMEOUT_SECS = float(os.getenv("GLM_FILE_UPLOAD_TIMEOUT_SECS", "120"))
    
    # General provider timeouts
    KIMI_READ_TIMEOUT_SECS = float(os.getenv("KIMI_READ_TIMEOUT_SECS", "300"))
    KIMI_CONNECT_TIMEOUT_SECS = float(os.getenv("KIMI_CONNECT_TIMEOUT_SECS", "30"))
    KIMI_DEFAULT_READ_TIMEOUT_SECS = float(os.getenv("KIMI_DEFAULT_READ_TIMEOUT_SECS", "300"))
    
    # Web search backend timeouts
    WEB_SEARCH_BASE_TIMEOUT = int(os.getenv("WEB_SEARCH_BASE_TIMEOUT", "20"))
    WEB_SEARCH_MAX_RETRIES = int(os.getenv("WEB_SEARCH_MAX_RETRIES", "3"))
    
    @classmethod
    def get_kimi_file_config(cls) -> Dict[str, Any]:
        """Get Kimi file operation configuration."""
        return {
            "fetch_timeout": cls.KIMI_FILES_FETCH_TIMEOUT_SECS,
            "max_retries": cls.KIMI_FILES_FETCH_RETRIES,
            "base_delay": cls.KIMI_FILES_FETCH_BASE_DELAY,
            "max_delay": cls.KIMI_FILES_FETCH_MAX_DELAY,
            "backoff_factor": cls.KIMI_FILES_FETCH_BACKOFF_FACTOR,
        }
    
    @classmethod
    def get_glm_web_config(cls) -> Dict[str, Any]:
        """Get GLM web operation configuration."""
        return {
            "search_timeout": cls.GLM_WEB_SEARCH_TIMEOUT_SECS,
            "browse_chat_timeout": cls.GLM_WEB_BROWSE_CHAT_TIMEOUT_SECS,
            "file_upload_timeout": cls.GLM_FILE_UPLOAD_TIMEOUT_SECS,
        }
    
    @classmethod
    def get_web_search_config(cls) -> Dict[str, Any]:
        """Get web search backend configuration."""
        return {
            "base_timeout": cls.WEB_SEARCH_BASE_TIMEOUT,
            "max_retries": cls.WEB_SEARCH_MAX_RETRIES,
        }


class RetryConfig:
    """Retry strategy configuration."""
    
    @staticmethod
    def exponential_backoff(attempt: int, base_delay: float = 1.0, 
                          max_delay: float = 60.0, backoff_factor: float = 2.0) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        delay = min(base_delay * (backoff_factor ** attempt), max_delay)
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    @staticmethod
    def should_retry_exception(exception: Exception) -> bool:
        """Determine if an exception should trigger a retry."""
        # Retry on network-related exceptions
        retry_exceptions = (
            ConnectionError,
            TimeoutError,
            OSError,  # Includes network errors
        )
        
        # Check for specific HTTP status codes that should be retried
        if hasattr(exception, 'response'):
            status_code = getattr(exception.response, 'status_code', None)
            if status_code in [429, 500, 502, 503, 504]:
                return True
        
        return isinstance(exception, retry_exceptions)


# Environment variable documentation
ENV_VARS_DOCS = {
    "KIMI_FILES_FETCH_TIMEOUT_SECS": "Overall timeout for Kimi file content retrieval (default: 120)",
    "KIMI_FILES_FETCH_RETRIES": "Number of retry attempts for Kimi file operations (default: 5)",
    "KIMI_FILES_FETCH_BASE_DELAY": "Base delay for exponential backoff in seconds (default: 1.0)",
    "KIMI_FILES_FETCH_MAX_DELAY": "Maximum delay between retries in seconds (default: 60.0)",
    "KIMI_FILES_FETCH_BACKOFF_FACTOR": "Exponential backoff multiplier (default: 2.0)",
    
    "GLM_WEB_SEARCH_TIMEOUT_SECS": "Timeout for GLM web search operations (default: 60)",
    "GLM_WEB_BROWSE_CHAT_TIMEOUT_SECS": "Timeout for GLM web browse chat (default: 120)",
    "GLM_FILE_UPLOAD_TIMEOUT_SECS": "Timeout for GLM file uploads (default: 120)",
    
    "WEB_SEARCH_BASE_TIMEOUT": "Base timeout for web search backends (default: 20)",
    "WEB_SEARCH_MAX_RETRIES": "Maximum retries for web search operations (default: 3)",
}
