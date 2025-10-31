"""
Async Upload Feature Flag Configuration

Controls async vs sync behavior for file upload operations.
Supports gradual rollout with percentage-based traffic distribution.

Environment Variables:
- ASYNC_UPLOAD_ENABLED: Enable/disable async uploads (default: false)
- ASYNC_UPLOAD_ROLLOUT: Percentage of traffic to route to async (0-100, default: 0)
- ASYNC_UPLOAD_FALLBACK: Fall back to sync on async errors (default: true)
- ASYNC_UPLOAD_MAX_RETRIES: Max retry attempts for async operations (default: 2)
- ASYNC_UPLOAD_TIMEOUT: Timeout in seconds for async operations (default: 30)

Usage:
    config = AsyncUploadConfig.from_env()
    if config.enabled and config.should_use_async():
        # Use async implementation
    else:
        # Use sync implementation
"""

import os
import hashlib
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AsyncUploadConfig:
    """Configuration for async upload feature flags"""
    
    enabled: bool = False
    rollout_percentage: int = 0
    fallback_on_error: bool = True
    max_retries: int = 2
    timeout_seconds: int = 30
    
    @classmethod
    def from_env(cls) -> "AsyncUploadConfig":
        """Load configuration from environment variables"""
        return cls(
            enabled=os.getenv("ASYNC_UPLOAD_ENABLED", "false").lower() == "true",
            rollout_percentage=int(os.getenv("ASYNC_UPLOAD_ROLLOUT", "0")),
            fallback_on_error=os.getenv("ASYNC_UPLOAD_FALLBACK", "true").lower() == "true",
            max_retries=int(os.getenv("ASYNC_UPLOAD_MAX_RETRIES", "2")),
            timeout_seconds=int(os.getenv("ASYNC_UPLOAD_TIMEOUT", "30"))
        )
    
    def should_use_async(self, request_id: Optional[str] = None) -> bool:
        """
        Determine if this request should use async based on rollout percentage.
        
        Uses hash-based consistent selection for stable rollout distribution.
        
        Args:
            request_id: Optional request identifier for consistent hashing.
                       If not provided, uses a random UUID.
        
        Returns:
            True if this request should use async, False otherwise
        """
        if not self.enabled:
            return False
        
        if self.rollout_percentage >= 100:
            return True
        
        if self.rollout_percentage <= 0:
            return False
        
        # Hash-based consistent selection for stable rollout
        if request_id is None:
            import uuid
            request_id = str(uuid.uuid4())
        
        # Use MD5 hash for consistent distribution
        hash_value = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
        return (hash_value % 100) < self.rollout_percentage
    
    def log_config(self):
        """Log current configuration"""
        logger.info(
            f"AsyncUploadConfig: enabled={self.enabled}, "
            f"rollout={self.rollout_percentage}%, "
            f"fallback={self.fallback_on_error}, "
            f"max_retries={self.max_retries}, "
            f"timeout={self.timeout_seconds}s"
        )


# Global config instance
_config: Optional[AsyncUploadConfig] = None


def get_config() -> AsyncUploadConfig:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = AsyncUploadConfig.from_env()
        _config.log_config()
    return _config


def reset_config():
    """Reset global config (useful for testing)"""
    global _config
    _config = None

