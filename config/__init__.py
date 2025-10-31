"""
Configuration package for EX MCP Server

This package consolidates all configuration settings into logical modules:
- core.py: Version, metadata, model configuration, context engineering
- operations.py: Production settings, performance, security, MCP limits
- timeouts.py: Timeout configuration and hierarchy
- migration.py: File management migration configuration
- file_handling.py: File handling guidance constants

All configuration values are re-exported here for backward compatibility.
"""

# Re-export everything from core module
from .core import (
    __version__,
    __updated__,
    __author__,
    __release_name__,
    DEFAULT_MODEL,
    IS_AUTO_MODE,
    TEMPERATURE_ANALYTICAL,
    TEMPERATURE_BALANCED,
    TEMPERATURE_CREATIVE,
    DEFAULT_THINKING_MODE_THINKDEEP,
    THINK_ROUTING_ENABLED,
    INTELLIGENT_ROUTING_ENABLED,
    AI_MANAGER_MODEL,
    WEB_SEARCH_PROVIDER,
    FILE_PROCESSING_PROVIDER,
    COST_AWARE_ROUTING,
    DEFAULT_USE_ASSISTANT_MODEL,
    CONTEXT_ENGINEERING,
)

# Re-export everything from operations module
from .operations import (
    LOG_LEVEL,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    ENABLE_FALLBACK,
    MCP_WEBSOCKET_ENABLED,
    MCP_WEBSOCKET_PORT,
    MCP_WEBSOCKET_HOST,
    MAX_CONCURRENT_REQUESTS,
    RATE_LIMIT_PER_MINUTE,
    CACHE_ENABLED,
    CACHE_TTL,
    USE_ASYNC_SUPABASE,
    ENABLE_SUPABASE_WRITE_CACHING,
    CONVERSATION_QUEUE_SIZE,
    CONVERSATION_QUEUE_WARNING_THRESHOLD,
    VALIDATE_API_KEYS,
    SECURE_INPUTS_ENFORCED,
    ACTIVITY_SINCE_UNTIL_ENABLED,
    ACTIVITY_STRUCTURED_OUTPUT_ENABLED,
    DEFAULT_CONSENSUS_TIMEOUT,
    DEFAULT_CONSENSUS_MAX_INSTANCES_PER_COMBINATION,
    MCP_PROMPT_SIZE_LIMIT,
    DEFAULT_MAX_OUTPUT_TOKENS,
    KIMI_MAX_OUTPUT_TOKENS,
    GLM_MAX_OUTPUT_TOKENS,
    ENFORCE_MAX_TOKENS,
    LOCALE,
)

# Re-export TimeoutConfig class
from .timeouts import TimeoutConfig

# Re-export MigrationConfig class
from .migration import MigrationConfig

# Re-export file handling guidance (if it exists)
try:
    from .file_handling import FILE_PATH_GUIDANCE, FILE_UPLOAD_GUIDANCE
except ImportError:
    # file_handling.py might not exist yet
    FILE_PATH_GUIDANCE = None
    FILE_UPLOAD_GUIDANCE = None

# Backward compatibility: Import config helper
try:
    from utils.config.helpers import get_auggie_config_path
except ImportError:
    # utils.config.helpers might not exist
    get_auggie_config_path = None


__all__ = [
    # Version and metadata
    "__version__",
    "__updated__",
    "__author__",
    "__release_name__",
    
    # Model configuration
    "DEFAULT_MODEL",
    "IS_AUTO_MODE",
    "TEMPERATURE_ANALYTICAL",
    "TEMPERATURE_BALANCED",
    "TEMPERATURE_CREATIVE",
    "DEFAULT_THINKING_MODE_THINKDEEP",
    "THINK_ROUTING_ENABLED",
    "INTELLIGENT_ROUTING_ENABLED",
    "AI_MANAGER_MODEL",
    "WEB_SEARCH_PROVIDER",
    "FILE_PROCESSING_PROVIDER",
    "COST_AWARE_ROUTING",
    "DEFAULT_USE_ASSISTANT_MODEL",
    
    # Context engineering
    "CONTEXT_ENGINEERING",
    
    # Production settings
    "LOG_LEVEL",
    "MAX_RETRIES",
    "REQUEST_TIMEOUT",
    "ENABLE_FALLBACK",
    
    # MCP WebSocket
    "MCP_WEBSOCKET_ENABLED",
    "MCP_WEBSOCKET_PORT",
    "MCP_WEBSOCKET_HOST",
    
    # Performance
    "MAX_CONCURRENT_REQUESTS",
    "RATE_LIMIT_PER_MINUTE",
    "CACHE_ENABLED",
    "CACHE_TTL",
    "USE_ASYNC_SUPABASE",
    "ENABLE_SUPABASE_WRITE_CACHING",
    "CONVERSATION_QUEUE_SIZE",
    "CONVERSATION_QUEUE_WARNING_THRESHOLD",
    
    # Security
    "VALIDATE_API_KEYS",
    "SECURE_INPUTS_ENFORCED",
    
    # Feature flags
    "ACTIVITY_SINCE_UNTIL_ENABLED",
    "ACTIVITY_STRUCTURED_OUTPUT_ENABLED",
    "DEFAULT_CONSENSUS_TIMEOUT",
    "DEFAULT_CONSENSUS_MAX_INSTANCES_PER_COMBINATION",
    
    # MCP Protocol limits
    "MCP_PROMPT_SIZE_LIMIT",
    "DEFAULT_MAX_OUTPUT_TOKENS",
    "KIMI_MAX_OUTPUT_TOKENS",
    "GLM_MAX_OUTPUT_TOKENS",
    "ENFORCE_MAX_TOKENS",
    "LOCALE",
    
    # Configuration classes
    "TimeoutConfig",
    "MigrationConfig",
    
    # File handling
    "FILE_PATH_GUIDANCE",
    "FILE_UPLOAD_GUIDANCE",
    
    # Helpers
    "get_auggie_config_path",
]

