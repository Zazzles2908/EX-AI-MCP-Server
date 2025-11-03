"""
File management configuration for EX-AI-MCP-Server
Consolidates all file upload, validation, and lifecycle settings
"""
from .base import BaseConfig
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class FileManagementConfig(BaseConfig):
    """Configuration for file management operations"""

    # File size limits (in bytes)
    MAX_FILE_SIZE: int = BaseConfig.get_int("MAX_FILE_SIZE", 100 * 1024 * 1024)  # 100MB default
    MAX_FILE_SIZE_KIMI: int = BaseConfig.get_int("MAX_FILE_SIZE_KIMI", 100 * 1024 * 1024)  # 100MB
    MAX_FILE_SIZE_GLM: int = BaseConfig.get_int("MAX_FILE_SIZE_GLM", 20 * 1024 * 1024)  # 20MB

    # Allowed file types
    ALLOWED_EXTENSIONS: List[str] = BaseConfig.get_list(
        "ALLOWED_EXTENSIONS",
        "txt,pdf,doc,docx,xls,xlsx,ppt,pptx,jpg,jpeg,png,gif,zip,py,js,ts,json,yaml,yml,md"
    )

    # Upload configuration
    UPLOAD_TIMEOUT: int = BaseConfig.get_int("UPLOAD_TIMEOUT", 300)  # 5 minutes
    MAX_CONCURRENT_UPLOADS: int = BaseConfig.get_int("MAX_CONCURRENT_UPLOADS", 5)

    # Deduplication
    ENABLE_DEDUPLICATION: bool = BaseConfig.get_bool("ENABLE_DEDUPLICATION", True)

    # Provider preferences
    PREFERRED_PROVIDER: str = BaseConfig.get_str("PREFERRED_PROVIDER", "")  # empty = auto

    # Lifecycle management
    RETENTION_DAYS: int = BaseConfig.get_int("FILE_RETENTION_DAYS", 30)
    CLEANUP_INTERVAL_HOURS: int = BaseConfig.get_int("CLEANUP_INTERVAL_HOURS", 24)

    # User quotas
    DEFAULT_USER_QUOTA_GB: int = BaseConfig.get_int("DEFAULT_USER_QUOTA_GB", 10)
    MAX_FILE_SIZE_PER_USER: int = BaseConfig.get_int("MAX_FILE_SIZE_PER_USER", 512 * 1024 * 1024)  # 512MB

    @classmethod
    def get_provider_limits(cls) -> Dict[str, int]:
        """Get file size limits by provider"""
        return {
            "kimi": cls.MAX_FILE_SIZE_KIMI,
            "glm": cls.MAX_FILE_SIZE_GLM
        }

    @classmethod
    def is_extension_allowed(cls, filename: str) -> bool:
        """Check if file extension is allowed"""
        if not filename or "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def validate(cls) -> bool:
        """Validate file management configuration"""
        if cls.MAX_FILE_SIZE <= 0:
            raise ValueError("MAX_FILE_SIZE must be positive")
        if cls.RETENTION_DAYS < 1:
            raise ValueError("RETENTION_DAYS must be at least 1")
        if cls.CLEANUP_INTERVAL_HOURS < 1:
            raise ValueError("CLEANUP_INTERVAL_HOURS must be at least 1")
        if cls.MAX_FILE_SIZE_KIMI > 100 * 1024 * 1024:
            logger.warning("MAX_FILE_SIZE_KIMI exceeds Kimi's 100MB limit")
        if cls.MAX_FILE_SIZE_GLM > 20 * 1024 * 1024:
            logger.warning("MAX_FILE_SIZE_GLM exceeds GLM's 20MB limit")
        return True

