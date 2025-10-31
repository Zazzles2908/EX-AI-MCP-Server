"""
Core configuration for EX MCP Server

This module contains fundamental configuration that defines what the system IS:
- Version and metadata
- Model configuration and defaults
- Context engineering settings

Configuration values can be overridden by environment variables where appropriate.
"""

import os
import logging

logger = logging.getLogger(__name__)


def _parse_bool_env(key: str, default: str = "true") -> bool:
    """
    Parse boolean environment variable.

    Args:
        key: Environment variable name
        default: Default value if environment variable is not set

    Returns:
        Boolean value parsed from environment variable
    """
    return os.getenv(key, default).strip().lower() == "true"


# ============================================================================
# VERSION AND METADATA
# ============================================================================
# These values are used in server responses and for tracking releases
# IMPORTANT: This is the single source of truth for version and author info
# Semantic versioning: MAJOR.MINOR.PATCH
__version__: str = "2.0.0"
# Last update date in ISO format
__updated__: str = "2025-09-26"
# Primary maintainer
__author__: str = "Zazzles"
# Production-ready release with intelligent routing
__release_name__: str = "Production-Ready v2.0 - Intelligent Routing"


# ============================================================================
# MODEL CONFIGURATION
# ============================================================================
# DEFAULT_MODEL: The default model used for all AI operations
# This should be a stable, high-performance model suitable for code analysis
# Can be overridden by setting DEFAULT_MODEL environment variable
# Special value "auto" means the server will select an appropriate model for each task (client-agnostic)
DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "glm-4.5-flash")

# Auto mode detection - when DEFAULT_MODEL is "auto", the server selects the model (client-agnostic)
IS_AUTO_MODE: bool = DEFAULT_MODEL.lower() == "auto"

# Each provider (gemini.py, openai_provider.py, xai.py) defines its own SUPPORTED_MODELS
# with detailed descriptions. Tools use ModelProviderRegistry.get_available_model_names()
# to get models only from enabled providers (those with valid API keys).
#
# This architecture ensures:
# - No namespace collisions (models only appear when their provider is enabled)
# - API key-based filtering (prevents wrong models from being exposed to clients)
# - Proper provider routing (models route to the correct API endpoint)
# - Clean separation of concerns (providers own their model definitions)


# Temperature defaults for different tool types
# Temperature controls the randomness/creativity of model responses
# Lower values (0.0-0.3) produce more deterministic, focused responses
# Higher values (0.7-1.0) produce more creative, varied responses

# TEMPERATURE_ANALYTICAL: Used for tasks requiring precision and consistency
# Ideal for code review, debugging, and error analysis where accuracy is critical
TEMPERATURE_ANALYTICAL: float = 0.2  # For code review, debugging

# TEMPERATURE_BALANCED: Middle ground for general conversations
# Provides a good balance between consistency and helpful variety
TEMPERATURE_BALANCED: float = 0.5  # For general chat

# TEMPERATURE_CREATIVE: Higher temperature for exploratory tasks
# Used when brainstorming, exploring alternatives, or architectural discussions
TEMPERATURE_CREATIVE: float = 0.7  # For architecture, deep thinking

# Thinking Mode Defaults
# DEFAULT_THINKING_MODE_THINKDEEP: Default thinking depth for extended reasoning tool
# Higher modes use more computational budget but provide deeper analysis
DEFAULT_THINKING_MODE_THINKDEEP: str = os.getenv("DEFAULT_THINKING_MODE_THINKDEEP", "high")

# Feature flags
# THINK_ROUTING_ENABLED: enable aliasing/rerouting and deterministic model selection for thinking tools
# Default: true
THINK_ROUTING_ENABLED: bool = _parse_bool_env("THINK_ROUTING_ENABLED", "true")

# Production-Ready v2.0 Configuration
# Intelligent Routing System
INTELLIGENT_ROUTING_ENABLED: bool = _parse_bool_env("INTELLIGENT_ROUTING_ENABLED", "true")
AI_MANAGER_MODEL: str = os.getenv("AI_MANAGER_MODEL", "glm-4.5-flash")
WEB_SEARCH_PROVIDER: str = os.getenv("WEB_SEARCH_PROVIDER", "glm")
FILE_PROCESSING_PROVIDER: str = os.getenv("FILE_PROCESSING_PROVIDER", "kimi")
COST_AWARE_ROUTING: bool = _parse_bool_env("COST_AWARE_ROUTING", "true")

# Expert Analysis Configuration
# DEFAULT_USE_ASSISTANT_MODEL: Controls whether workflow tools use expert analysis by default
# When true, tools like thinkdeep, debug, analyze will call expert models for validation
# When false, tools rely only on their own analysis (faster but less comprehensive)
# Can be overridden per-tool with TOOLNAME_USE_ASSISTANT_MODEL_DEFAULT env vars
DEFAULT_USE_ASSISTANT_MODEL: bool = _parse_bool_env("DEFAULT_USE_ASSISTANT_MODEL", "true")


# ============================================================================
# CONTEXT ENGINEERING CONFIGURATION
# ============================================================================
# Phase 1: Defense-in-Depth History Stripping
# Prevents recursive embedding of conversation history that causes token explosion
# STRIP_EMBEDDED_HISTORY: Enable/disable history stripping (default: True)
# DETECTION_MODE: "conservative" (high confidence markers) or "aggressive" (broader detection)
# DRY_RUN_MODE: Test without making changes (default: False)
# LOG_STRIPPING: Log when history stripping occurs (default: True)
# MIN_TOKEN_THRESHOLD: Only strip if content exceeds this token count (default: 100)
CONTEXT_ENGINEERING = {
    "strip_embedded_history": _parse_bool_env("STRIP_EMBEDDED_HISTORY", "true"),
    "detection_mode": os.getenv("DETECTION_MODE", "conservative"),
    "dry_run": _parse_bool_env("DRY_RUN_MODE", "false"),
    "log_stripping": _parse_bool_env("LOG_STRIPPING", "true"),
    "min_token_threshold": int(os.getenv("MIN_TOKEN_THRESHOLD", "100")),
}

