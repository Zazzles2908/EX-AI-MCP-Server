"""
Configuration and constants for EX MCP Server

This module centralizes all configuration settings for the EX MCP Server.
It defines model configurations, token limits, temperature defaults, and other
constants used throughout the application.

Configuration values can be overridden by environment variables where appropriate.
"""

import os
from typing import Optional


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


# Version and metadata
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

# Model configuration
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

# Context Engineering Configuration (Phase 1: Defense-in-Depth History Stripping)
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

# Production Settings
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
ENABLE_FALLBACK: bool = _parse_bool_env("ENABLE_FALLBACK", "true")

# MCP WebSocket Configuration
MCP_WEBSOCKET_ENABLED: bool = _parse_bool_env("MCP_WEBSOCKET_ENABLED", "true")
MCP_WEBSOCKET_PORT: int = int(os.getenv("MCP_WEBSOCKET_PORT", "8080"))
MCP_WEBSOCKET_HOST: str = os.getenv("MCP_WEBSOCKET_HOST", "0.0.0.0")

# Performance Settings
MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
CACHE_ENABLED: bool = _parse_bool_env("CACHE_ENABLED", "true")
CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))

# BUG FIX #11 (2025-10-19): Async Supabase operations for non-blocking conversation persistence
# When enabled, Supabase writes use fire-and-forget pattern to avoid blocking responses
# Reads remain synchronous (we need the data), but writes return immediately
USE_ASYNC_SUPABASE: bool = _parse_bool_env("USE_ASYNC_SUPABASE", "true")
ENABLE_SUPABASE_WRITE_CACHING: bool = _parse_bool_env("ENABLE_SUPABASE_WRITE_CACHING", "true")

# BUG FIX #11 (2025-10-20): Conversation queue configuration for async write pattern
# Replaces ThreadPoolExecutor with async queue to prevent resource exhaustion
CONVERSATION_QUEUE_SIZE: int = int(os.getenv("CONVERSATION_QUEUE_SIZE", "1000"))
CONVERSATION_QUEUE_WARNING_THRESHOLD: int = int(os.getenv("CONVERSATION_QUEUE_WARNING_THRESHOLD", "500"))

# Security Settings
VALIDATE_API_KEYS: bool = _parse_bool_env("VALIDATE_API_KEYS", "true")

# Input Security (CHANGED 2025-10-16: Default TRUE for security-by-default)
# Prevents path traversal attacks and validates file paths
# SECURE_INPUTS_ENFORCED: Validates file paths to prevent directory traversal
SECURE_INPUTS_ENFORCED: bool = _parse_bool_env("SECURE_INPUTS_ENFORCED", "true")

# Activity tool feature flags (default OFF)
ACTIVITY_SINCE_UNTIL_ENABLED: bool = _parse_bool_env("ACTIVITY_SINCE_UNTIL_ENABLED", "false")
ACTIVITY_STRUCTURED_OUTPUT_ENABLED: bool = _parse_bool_env("ACTIVITY_STRUCTURED_OUTPUT_ENABLED", "false")

# Consensus timeout and rate limiting settings
DEFAULT_CONSENSUS_TIMEOUT: float = 120.0  # 2 minutes per model
DEFAULT_CONSENSUS_MAX_INSTANCES_PER_COMBINATION: int = 2

# NOTE: Consensus tool now uses sequential processing for MCP compatibility
# Concurrent processing was removed to avoid async pattern violations

# MCP Protocol Transport Limits
#
# IMPORTANT: This limit ONLY applies to the MCP Client ↔ MCP Server transport boundary.
# It does NOT limit internal MCP Server operations like system prompts, file embeddings,
# conversation history, or content sent to external models (Gemini/OpenAI/OpenRouter).
#
# MCP Protocol Architecture:
# MCP Client ←→ MCP Server ←→ External Model (Kimi/GLM/etc.)
#     ↑                              ↑
#     │                              │
# MCP transport                Internal processing
# (token limit from MAX_MCP_OUTPUT_TOKENS)    (No MCP limit - can be 1M+ tokens)
#
# MCP_PROMPT_SIZE_LIMIT: Maximum character size for USER INPUT crossing MCP transport
# The MCP protocol has a combined request+response limit controlled by MAX_MCP_OUTPUT_TOKENS.
# To ensure adequate space for MCP Server → client responses, we limit user input
# to roughly 60% of the total token budget converted to characters. Larger user prompts
# must be sent as prompt.txt files to bypass MCP's transport constraints.
#
# Token to character conversion ratio: ~4 characters per token (average for code/text)
# Default allocation: 60% of tokens for input, 40% for response
#
# What IS limited by this constant:
# - request.prompt field content (user input from MCP client)
# - prompt.txt file content (alternative user input method)
# - Any other direct user input fields
#
# What is NOT limited by this constant:
# - System prompts added internally by tools
# - File content embedded by tools
# - Conversation history loaded from storage
# - Web search instructions or other internal additions
# - Complete prompts sent to external models (managed by model-specific token limits)
#
# This ensures MCP transport stays within protocol limits while allowing internal
# processing to use full model context windows (200K-1M+ tokens).


def _calculate_mcp_prompt_limit() -> int:
    """
    Calculate MCP prompt size limit based on MAX_MCP_OUTPUT_TOKENS environment variable.

    Returns:
        Maximum character count for user input prompts
    """
    # Check for MAX_MCP_OUTPUT_TOKENS environment variable
    max_tokens_str = os.getenv("MAX_MCP_OUTPUT_TOKENS")

    if max_tokens_str:
        try:
            max_tokens = int(max_tokens_str)
            # Allocate 60% of tokens for input, convert to characters (~4 chars per token)
            input_token_budget = int(max_tokens * 0.6)
            character_limit = input_token_budget * 4
            return character_limit
        except (ValueError, TypeError):
            # Fall back to default if MAX_MCP_OUTPUT_TOKENS is not a valid integer
            pass

    # Default fallback: 60,000 characters (equivalent to ~15k tokens input of 25k total)
    return 60_000


MCP_PROMPT_SIZE_LIMIT: int = _calculate_mcp_prompt_limit()

# Model Output Token Limits
# Controls maximum response length from AI models
#
# IMPORTANT CONFIGURATION NOTES:
# 1. These values are DEFAULT maximums used when max_output_tokens is not explicitly provided
# 2. Setting these too high may waste tokens; too low may cause truncation
# 3. Official model limits (as of 2025-10-14):
#    - Kimi K2 models: 16384 tokens (official Moonshot AI limit)
#    - GLM models: 8192 tokens (official ZhipuAI limit)
# 4. Set to 0 or empty string to disable automatic max_tokens (let model use its default)
#
# USAGE:
# - When a tool/provider doesn't specify max_output_tokens, these defaults are used
# - When a tool/provider DOES specify max_output_tokens, that value takes precedence
# - To disable automatic max_tokens enforcement, set: DEFAULT_MAX_OUTPUT_TOKENS=0
#
# TROUBLESHOOTING:
# - If responses are truncated: Check if max_output_tokens is being set too low
# - If API errors occur: Some models may not support max_tokens parameter
# - If costs are high: Consider lowering these values for routine tasks
DEFAULT_MAX_OUTPUT_TOKENS: int = int(os.getenv("DEFAULT_MAX_OUTPUT_TOKENS", "8192"))
KIMI_MAX_OUTPUT_TOKENS: int = int(os.getenv("KIMI_MAX_OUTPUT_TOKENS", "16384"))
GLM_MAX_OUTPUT_TOKENS: int = int(os.getenv("GLM_MAX_OUTPUT_TOKENS", "8192"))

# Whether to enforce max_tokens even when not explicitly requested
# Set to False to only use max_tokens when explicitly provided by the caller
# Set to True to always enforce max_tokens using the defaults above
ENFORCE_MAX_TOKENS: bool = _parse_bool_env("ENFORCE_MAX_TOKENS", "true")

# Language/Locale Configuration
# LOCALE: Language/locale specification for AI responses
# When set, all AI tools will respond in the specified language while
# maintaining their analytical capabilities
# Examples: "fr-FR", "en-US", "zh-CN", "zh-TW", "ja-JP", "ko-KR", "es-ES",
# "de-DE", "it-IT", "pt-PT"
# Leave empty for default language (English)
LOCALE: str = os.getenv("LOCALE", "")

# Threading configuration
# Simple in-memory conversation threading for stateless MCP environment
# Conversations persist only during the connected client session

# Auggie config discovery (optional helper)
# Moved to utils/config_helpers.py for better separation of concerns
# Import here for backward compatibility
from utils.config.helpers import get_auggie_config_path


# =============================================================================
# TIMEOUT CONFIGURATION - Coordinated Hierarchy
# =============================================================================
# This section implements a coordinated timeout hierarchy to ensure proper
# timeout behavior across all layers of the application.
#
# Hierarchy (from inner to outer):
# 1. Tool Level (primary) - Tools set their own timeout based on complexity
# 2. Daemon Level (secondary) - Catches tools that don't implement timeout properly
# 3. Shim Level (tertiary) - Catches daemon failures
# 4. Client Level (final) - Prevents infinite hangs
#
# Rule: Each outer timeout = 1.5x inner timeout (50% buffer)
# =============================================================================


class TimeoutConfig:
    """Centralized timeout configuration with coordinated hierarchy.

    TRACK 2 FIX (2025-10-16): Updated defaults to 30s for MCP tools to prevent indefinite hangs.
    Previous defaults (90-150s) were too high and caused poor user experience.
    """

    # Tool-level timeouts (primary)
    SIMPLE_TOOL_TIMEOUT_SECS = int(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "30"))
    WORKFLOW_TOOL_TIMEOUT_SECS = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "45"))
    EXPERT_ANALYSIS_TIMEOUT_SECS = int(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "60"))

    # Provider timeouts
    GLM_TIMEOUT_SECS = int(os.getenv("GLM_TIMEOUT_SECS", "30"))
    KIMI_TIMEOUT_SECS = int(os.getenv("KIMI_TIMEOUT_SECS", "30"))
    KIMI_WEB_SEARCH_TIMEOUT_SECS = int(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "30"))

    @classmethod
    def get_daemon_timeout(cls) -> int:
        """
        Get daemon timeout (1.5x max tool timeout).

        Returns:
            int: Daemon timeout in seconds (default: 180s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 1.5)

    @classmethod
    def get_shim_timeout(cls) -> int:
        """
        Get shim timeout (2x max tool timeout).

        Returns:
            int: Shim timeout in seconds (default: 240s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.0)

    @classmethod
    def get_client_timeout(cls) -> int:
        """
        Get client timeout (2.5x max tool timeout).

        Returns:
            int: Client timeout in seconds (default: 300s)
        """
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.5)

    @classmethod
    def validate_hierarchy(cls) -> bool:
        """
        Validate that timeout hierarchy is correct.

        The hierarchy must follow: tool < daemon < shim < client
        Each outer timeout should be at least 1.5x the inner timeout.

        Returns:
            bool: True if hierarchy is valid

        Raises:
            ValueError: If timeout hierarchy is invalid
        """
        tool = cls.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = cls.get_daemon_timeout()
        shim = cls.get_shim_timeout()
        client = cls.get_client_timeout()

        # Check hierarchy: tool < daemon < shim < client
        if not (tool < daemon < shim < client):
            raise ValueError(
                f"Invalid timeout hierarchy: "
                f"tool={tool}s, daemon={daemon}s, shim={shim}s, client={client}s. "
                f"Expected: tool < daemon < shim < client"
            )

        # Check buffer ratios
        daemon_ratio = daemon / tool
        shim_ratio = shim / tool
        client_ratio = client / tool

        if daemon_ratio < 1.5:
            raise ValueError(
                f"Daemon timeout ratio too low: {daemon_ratio:.2f}x tool timeout. "
                f"Expected at least 1.5x"
            )

        if shim_ratio < 2.0:
            raise ValueError(
                f"Shim timeout ratio too low: {shim_ratio:.2f}x tool timeout. "
                f"Expected at least 2.0x"
            )

        if client_ratio < 2.5:
            raise ValueError(
                f"Client timeout ratio too low: {client_ratio:.2f}x tool timeout. "
                f"Expected at least 2.5x"
            )

        return True

    @classmethod
    def get_timeout_summary(cls) -> dict:
        """
        Get summary of all timeout values.

        Returns:
            dict: Dictionary containing all timeout values and ratios
        """
        tool = cls.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = cls.get_daemon_timeout()
        shim = cls.get_shim_timeout()
        client = cls.get_client_timeout()

        return {
            "tool_timeouts": {
                "simple": cls.SIMPLE_TOOL_TIMEOUT_SECS,
                "workflow": cls.WORKFLOW_TOOL_TIMEOUT_SECS,
                "expert_analysis": cls.EXPERT_ANALYSIS_TIMEOUT_SECS,
            },
            "infrastructure_timeouts": {
                "daemon": daemon,
                "shim": shim,
                "client": client,
            },
            "provider_timeouts": {
                "glm": cls.GLM_TIMEOUT_SECS,
                "kimi": cls.KIMI_TIMEOUT_SECS,
                "kimi_web_search": cls.KIMI_WEB_SEARCH_TIMEOUT_SECS,
            },
            "ratios": {
                "daemon_to_tool": round(daemon / tool, 2),
                "shim_to_tool": round(shim / tool, 2),
                "client_to_tool": round(client / tool, 2),
            },
            "hierarchy_valid": cls.validate_hierarchy(),
        }


# Validate timeout hierarchy on module import
try:
    TimeoutConfig.validate_hierarchy()
except ValueError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Timeout hierarchy validation failed: {e}")
    # Don't raise - allow module to load but log the warning
