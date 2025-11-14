#!/usr/bin/env python3
"""
Centralized configuration settings for EX-AI MCP Server
All scripts should import from here to prevent configuration drift
"""

import os
from typing import Optional
from pathlib import Path
from dataclasses import dataclass, field
from datetime import timedelta

# Import shared utilities
try:
    from src.utils.logging_unified import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda x: logging.getLogger(x)


@dataclass
class Config:
    """
    Centralized configuration for all EX-AI MCP Server scripts and services.
    This is the SINGLE SOURCE OF TRUTH for all configuration values.
    """

    # ========================================================================
    # WEBSOCKET CONFIGURATION
    # ========================================================================
    # Host where WebSocket daemon is accessible (host machine)
    ws_host: str = field(default_factory=lambda: os.getenv("EXAI_WS_HOST", "127.0.0.1"))

    # Port on host machine (DOCKER maps 3000:8079, scripts connect to 3000)
    ws_port: int = field(default_factory=lambda: int(os.getenv("EXAI_WS_PORT", "3000")))

    # Token for WebSocket authentication
    ws_token: str = field(default_factory=lambda: os.getenv("EXAI_WS_TOKEN", "test-token-12345"))

    # Docker internal port (8079) - DO NOT USE in scripts, use ws_port instead
    _docker_internal_port: int = 8079

    # ========================================================================
    # API PROVIDERS CONFIGURATION
    # ========================================================================
    kimi_api_key: str = field(default_factory=lambda: os.getenv("KIMI_API_KEY", ""))
    glm_api_key: str = field(default_factory=lambda: os.getenv("GLM_API_KEY", ""))

    # Model defaults (K2-0905 has 256K context, better than k2-0711 with 128K)
    kimi_default_model: str = field(default_factory=lambda: os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview"))
    glm_default_model: str = field(default_factory=lambda: os.getenv("GLM_DEFAULT_MODEL", "glm-4.5-flash"))

    # ========================================================================
    # SUPABASE CONFIGURATION
    # ========================================================================
    supabase_url: str = field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    supabase_anon_key: str = field(default_factory=lambda: os.getenv("SUPABASE_ANON_KEY", ""))
    supabase_service_key: str = field(default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))

    # ========================================================================
    # SECURITY CONFIGURATION
    # ========================================================================
    jwt_secret_key: str = field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_issuer: str = field(default_factory=lambda: os.getenv("JWT_ISSUER", "exai-mcp-server"))
    jwt_audience: str = field(default_factory=lambda: os.getenv("JWT_AUDIENCE", "exai-mcp-client"))

    # Claude JWT Token (stored in Supabase or environment)
    claude_jwt_token: str = field(default_factory=lambda: os.getenv("EXAI_JWT_TOKEN_CLAUDE", ""))

    # ========================================================================
    # TIMEOUT CONFIGURATION
    # ========================================================================
    simple_tool_timeout: int = field(default_factory=lambda: int(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "60")))
    workflow_tool_timeout: int = field(default_factory=lambda: int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "120")))
    expert_analysis_timeout: int = field(default_factory=lambda: int(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "90")))
    glm_timeout: int = field(default_factory=lambda: int(os.getenv("GLM_TIMEOUT_SECS", "90")))
    kimi_timeout: int = field(default_factory=lambda: int(os.getenv("KIMI_TIMEOUT_SECS", "120")))
    kimi_websearch_timeout: int = field(default_factory=lambda: int(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "150")))

    # ========================================================================
    # WEBSOCKET CONNECTION TIMEOUT
    # ========================================================================
    ws_connect_timeout: int = field(default_factory=lambda: int(os.getenv("WS_CONNECT_TIMEOUT", "10")))
    ws_max_size: int = field(default_factory=lambda: int(os.getenv("WS_MAX_SIZE", str(20 * 1024 * 1024))))  # 20MB

    # ========================================================================
    # LOGGING CONFIGURATION
    # ========================================================================
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_dir: Path = field(default_factory=lambda: Path(os.getenv("LOG_DIR", "logs")))

    # ========================================================================
    # SESSION CONFIGURATION
    # ========================================================================
    session_scope_strict: bool = field(default_factory=lambda: os.getenv("EX_SESSION_SCOPE_STRICT", "true").lower() == "true")
    session_scope_allow_cross: bool = field(default_factory=lambda: os.getenv("EX_SESSION_SCOPE_ALLOW_CROSS_SESSION", "false").lower() == "true")

    # ========================================================================
    # SECURITY FLAGS
    # ========================================================================
    secure_inputs_enforced: bool = field(default_factory=lambda: os.getenv("SECURE_INPUTS_ENFORCED", "true").lower() == "true")
    strict_file_size_rejection: bool = field(default_factory=lambda: os.getenv("STRICT_FILE_SIZE_REJECTION", "true").lower() == "true")

    # ========================================================================
    # REDIS CONFIGURATION (Optional)
    # ========================================================================
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_config()
        self._log_config_status()

    def _validate_config(self):
        """Validate critical configuration values"""
        errors = []

        # Validate port
        if not (1024 <= self.ws_port <= 65535):
            errors.append(f"WebSocket port {self.ws_port} is out of valid range (1024-65535)")

        # Validate timeouts
        if self.simple_tool_timeout < 10:
            errors.append("Simple tool timeout should be at least 10 seconds")
        if self.workflow_tool_timeout < 30:
            errors.append("Workflow tool timeout should be at least 30 seconds")

        # Validate API keys (warn if missing)
        if not self.kimi_api_key or self.kimi_api_key == "your-kimi-api-key-here":
            get_logger("config").warning("KIMI_API_KEY is not set or using placeholder value")

        if not self.glm_api_key or self.glm_api_key == "your-glm-api-key-here":
            get_logger("config").warning("GLM_API_KEY is not set or using placeholder value")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    def _log_config_status(self):
        """Log configuration status"""
        logger = get_logger("config")
        logger.info(f"✓ Configuration loaded successfully")
        logger.info(f"  WebSocket: {self.ws_host}:{self.ws_port}")
        logger.info(f"  API Providers: Kimi={bool(self.kimi_api_key)}, GLM={bool(self.glm_api_key)}")
        logger.info(f"  Supabase: {bool(self.supabase_url)}")
        logger.info(f"  Log Level: {self.log_level}")

    def get_websocket_uri(self) -> str:
        """Get WebSocket URI for connections"""
        return f"ws://{self.ws_host}:{self.ws_port}"

    def is_production_ready(self) -> bool:
        """Check if configuration is production-ready"""
        required = [
            self.kimi_api_key and self.kimi_api_key != "your-kimi-api-key-here",
            self.glm_api_key and self.glm_api_key != "your-glm-api-key-here",
            self.jwt_secret_key,
        ]
        return all(required)

    def to_dict(self) -> dict:
        """Convert to dictionary (redacts sensitive values)"""
        return {
            "ws_host": self.ws_host,
            "ws_port": self.ws_port,
            "kimi_api_key": "***" if self.kimi_api_key else "",
            "glm_api_key": "***" if self.glm_api_key else "",
            "supabase_url": self.supabase_url,
            "simple_tool_timeout": self.simple_tool_timeout,
            "workflow_tool_timeout": self.workflow_tool_timeout,
            "log_level": self.log_level,
        }


# Global config instance (singleton)
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """
    Get global config instance (singleton pattern)

    Usage:
        from src.config import get_config

        config = get_config()
        port = config.ws_port
        uri = config.get_websocket_uri()
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config() -> Config:
    """Reload configuration (useful for testing)"""
    global _config_instance
    _config_instance = None
    return get_config()
