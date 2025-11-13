"""
Configuration module for the MCP server.
Supports environment-specific configurations with validation and sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """
    Configuration class for MCP server.

    Uses dataclasses for simplicity (no external dependencies like pydantic).
    Implements singleton pattern through module-level instance.
    Validates on initialization (fail-fast approach).
    """

    # Supabase Configuration
    supabase_url: Optional[str] = field(default=None)
    supabase_key: Optional[str] = field(default=None)
    supabase_project_id: Optional[str] = field(default=None)
    
    # Timeout Configuration (Coordinated Hierarchy)
    http_client_timeout_secs: int = field(default=30)
    tool_timeout_secs: int = field(default=180)
    daemon_timeout_secs: int = field(default=270)
    
    # WebSocket Configuration
    ws_max_msg_bytes: int = field(default=33554432)  # 32MB
    exai_ws_host: str = field(default="127.0.0.1")
    exai_ws_port: int = field(default=8079)
    
    # Circuit Breaker Configuration
    circuit_breaker_enabled: bool = field(default=True)
    circuit_breaker_threshold: int = field(default=5)
    circuit_breaker_timeout_secs: int = field(default=60)
    fallback_to_websocket: bool = field(default=True)
    
    # Environment
    environment: str = field(default="development")
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate()
    
    def _validate(self):
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration is invalid.
        """
        # Validate Supabase URL format
        if not self.supabase_url.startswith(("http://", "https://")):
            raise ValueError(
                f"SUPABASE_URL must start with http:// or https://, got: {self.supabase_url}"
            )

        # Validate timeout hierarchy
        if self.tool_timeout_secs >= self.daemon_timeout_secs:
            logger.warning(
                f"TOOL_TIMEOUT_SECS ({self.tool_timeout_secs}) should be less than "
                f"DAEMON_TIMEOUT_SECS ({self.daemon_timeout_secs}) to allow proper timeout handling"
            )
        
        # Validate positive values
        if self.ws_max_msg_bytes <= 0:
            raise ValueError(f"WS_MAX_MSG_BYTES must be positive, got: {self.ws_max_msg_bytes}")
        
        if self.exai_ws_port <= 0 or self.exai_ws_port > 65535:
            raise ValueError(f"EXAI_WS_PORT must be between 1 and 65535, got: {self.exai_ws_port}")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment.lower() == "testing"


def _load_from_env() -> Config:
    """
    Load configuration from environment variables.
    
    Supports both .env and .env.testing files.
    Environment variables take precedence over .env files.
    
    Returns:
        Config: Loaded and validated configuration.
        
    Raises:
        ValueError: If configuration is invalid.
    """
    # Helper to get boolean from env
    def get_bool(key: str, default: bool) -> bool:
        value = os.getenv(key, str(default)).strip().lower()
        return value in ("true", "1", "yes", "on")
    
    # Helper to get int from env
    def get_int(key: str, default: int) -> int:
        value = os.getenv(key, str(default)).strip()
        try:
            return int(value)
        except ValueError:
            logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
            return default
    
    # Helper to get string from env
    def get_str(key: str, default: str) -> str:
        return os.getenv(key, default).strip()
    
    # Helper to get optional string from env
    def get_optional_str(key: str) -> Optional[str]:
        value = os.getenv(key)
        return value.strip() if value else None
    
    try:
        config = Config(
            # Supabase
            supabase_url=get_optional_str("SUPABASE_URL"),
            supabase_key=get_optional_str("SUPABASE_KEY"),
            supabase_project_id=get_optional_str("SUPABASE_PROJECT_ID"),
            
            # Timeouts
            http_client_timeout_secs=get_int("HTTP_CLIENT_TIMEOUT_SECS", 30),
            tool_timeout_secs=get_int("TOOL_TIMEOUT_SECS", 180),
            daemon_timeout_secs=get_int("DAEMON_TIMEOUT_SECS", 270),
            
            # WebSocket
            ws_max_msg_bytes=get_int("WS_MAX_MSG_BYTES", 33554432),
            exai_ws_host=get_str("EXAI_WS_HOST", "127.0.0.1"),
            exai_ws_port=get_int("EXAI_WS_PORT", 8079),
            
            # Circuit Breaker
            circuit_breaker_enabled=get_bool("CIRCUIT_BREAKER_ENABLED", True),
            circuit_breaker_threshold=get_int("CIRCUIT_BREAKER_THRESHOLD", 5),
            circuit_breaker_timeout_secs=get_int("CIRCUIT_BREAKER_TIMEOUT_SECS", 60),
            fallback_to_websocket=get_bool("FALLBACK_TO_WEBSOCKET", True),
            
            # Environment
            environment=get_str("ENVIRONMENT", "development"),
        )
        
        logger.info("Configuration loaded successfully")
        logger.debug(f"Environment: {config.environment}")
        logger.debug(f"WebSocket: {config.exai_ws_host}:{config.exai_ws_port}")
        
        return config
        
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


# DEPRECATED: Singleton pattern removed
# Use: config = Config() directly, or load_from_env() for fresh config
# For testing: config = Config() to get defaults, or load_from_env() to load from env


def load_from_env() -> Config:
    """
    Public API to load configuration from environment variables.

    Returns:
        Config: Loaded and validated configuration.
    """
    return _load_from_env()


def get_config() -> Config:
    """
    DEPRECATED: Use load_from_env() instead.
    Kept for backward compatibility.

    Returns:
        Config: Loaded and validated configuration.
    """
    return load_from_env()


# Export public API
__all__ = [
    "Config",
    "load_from_env",
    "get_config",  # DEPRECATED: kept for backward compatibility
]

