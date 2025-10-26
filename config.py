"""
Configuration and constants for EX MCP Server

This module centralizes all configuration settings for the EX MCP Server.
It defines model configurations, token limits, temperature defaults, and other
constants used throughout the application.

Configuration values can be overridden by environment variables where appropriate.
"""

import os
import logging
from typing import Optional

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

    EXAI INSIGHT (2025-10-21): Adaptive timeouts based on model complexity.
    Different models have different processing speeds and thinking depths.
    """

    # Tool-level timeouts (primary)
    SIMPLE_TOOL_TIMEOUT_SECS = int(os.getenv("SIMPLE_TOOL_TIMEOUT_SECS", "30"))
    WORKFLOW_TOOL_TIMEOUT_SECS = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "45"))
    EXPERT_ANALYSIS_TIMEOUT_SECS = int(os.getenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "60"))

    # Provider timeouts
    # PHASE 2.3 FIX (2025-10-25): Increased Kimi timeout from 30s to 40s
    # Root cause: Connection pool exhaustion + timeout too aggressive for non-cached requests
    GLM_TIMEOUT_SECS = int(os.getenv("GLM_TIMEOUT_SECS", "30"))
    KIMI_TIMEOUT_SECS = int(os.getenv("KIMI_TIMEOUT_SECS", "40"))  # Increased from 30s to 40s
    KIMI_WEB_SEARCH_TIMEOUT_SECS = int(os.getenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "30"))

    # EXAI INSIGHT (2025-10-21): Model-specific timeout multipliers
    # Based on observed performance during comprehensive testing
    MODEL_TIMEOUT_MULTIPLIERS = {
        # Thinking models need more time for deep reasoning
        "kimi-thinking-preview": 1.5,
        "glm-4.6": 1.3,
        "kimi-k2-0905-preview": 1.2,

        # Fast models can use less time
        "glm-4.5-flash": 0.7,
        "kimi-k2-turbo-preview": 0.8,
        "glm-4.5-air": 0.6,

        # Standard models use base timeout
        "glm-4.5": 1.0,
        "moonshot-v1-128k": 1.0,
        "moonshot-v1-32k": 1.0,
        "moonshot-v1-8k": 1.0,
    }

    @classmethod
    def get_model_timeout(cls, model_name: str, base_timeout: float) -> float:
        """
        Get adaptive timeout for a specific model.

        EXAI INSIGHT (2025-10-21): Different models need different timeouts.
        Thinking models need more time, fast models can use less.

        Args:
            model_name: Name of the model
            base_timeout: Base timeout in seconds

        Returns:
            Adjusted timeout based on model complexity

        Example:
            >>> TimeoutConfig.get_model_timeout("glm-4.6", 300)
            390.0  # 300 * 1.3 multiplier
            >>> TimeoutConfig.get_model_timeout("glm-4.5-flash", 300)
            210.0  # 300 * 0.7 multiplier
        """
        multiplier = cls.MODEL_TIMEOUT_MULTIPLIERS.get(model_name, 1.0)
        return base_timeout * multiplier

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
    def validate_all(cls) -> None:
        """
        Comprehensive timeout validation.
        Week 2 Fix #7 (2025-10-21): Validate all timeout configuration at startup.

        Validates:
        1. All timeout values are positive and reasonable
        2. Timeout hierarchy is maintained
        3. Provider timeouts are reasonable

        Raises:
            ValueError: If any validation fails
        """
        # 1. Validate individual timeout values
        cls._validate_timeout_values()

        # 2. Validate timeout hierarchy
        cls.validate_hierarchy()

        # 3. Log configuration for debugging
        cls._log_timeout_config()

    @classmethod
    def _validate_timeout_values(cls) -> None:
        """
        Validate individual timeout values are within reasonable bounds.
        Week 2 Fix #7 (2025-10-21): Ensure all timeouts are positive and reasonable.
        """
        timeouts = {
            "SIMPLE_TOOL_TIMEOUT_SECS": cls.SIMPLE_TOOL_TIMEOUT_SECS,
            "WORKFLOW_TOOL_TIMEOUT_SECS": cls.WORKFLOW_TOOL_TIMEOUT_SECS,
            "EXPERT_ANALYSIS_TIMEOUT_SECS": cls.EXPERT_ANALYSIS_TIMEOUT_SECS,
            "GLM_TIMEOUT_SECS": cls.GLM_TIMEOUT_SECS,
            "KIMI_TIMEOUT_SECS": cls.KIMI_TIMEOUT_SECS,
            "KIMI_WEB_SEARCH_TIMEOUT_SECS": cls.KIMI_WEB_SEARCH_TIMEOUT_SECS,
        }

        for name, value in timeouts.items():
            if value <= 0:
                raise ValueError(f"Timeout {name} must be positive, got {value}")

            # Set reasonable upper bounds (1 hour max for any timeout)
            if value > 3600:
                raise ValueError(f"Timeout {name} seems too large: {value} seconds (max: 3600)")

            # Warn about very short timeouts (< 5 seconds)
            if value < 5:
                logger.warning(f"Timeout {name} is very short: {value} seconds - may cause premature failures")

    @classmethod
    def _log_timeout_config(cls) -> None:
        """
        Log timeout configuration for debugging.
        Week 2 Fix #7 (2025-10-21): Log all timeout values at startup.
        """
        logger.info("=== TIMEOUT CONFIGURATION ===")
        logger.info(f"Tool Timeouts:")
        logger.info(f"  Simple Tool: {cls.SIMPLE_TOOL_TIMEOUT_SECS}s")
        logger.info(f"  Workflow Tool: {cls.WORKFLOW_TOOL_TIMEOUT_SECS}s")
        logger.info(f"  Expert Analysis: {cls.EXPERT_ANALYSIS_TIMEOUT_SECS}s")
        logger.info(f"Provider Timeouts:")
        logger.info(f"  GLM: {cls.GLM_TIMEOUT_SECS}s")
        logger.info(f"  Kimi: {cls.KIMI_TIMEOUT_SECS}s")
        logger.info(f"  Kimi Web Search: {cls.KIMI_WEB_SEARCH_TIMEOUT_SECS}s")
        logger.info(f"Calculated Timeouts:")
        logger.info(f"  Daemon: {cls.get_daemon_timeout()}s (1.5x workflow)")
        logger.info(f"  Shim: {cls.get_shim_timeout()}s (2.0x workflow)")
        logger.info(f"  Client: {cls.get_client_timeout()}s (2.5x workflow)")
        logger.info("=== END TIMEOUT CONFIGURATION ===")

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


# ============================================================================
# FILE MANAGEMENT MIGRATION CONFIGURATION
# ============================================================================
# Configuration for gradual migration from legacy file handlers to UnifiedFileManager
# Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)
# Date: 2025-10-22

class MigrationConfig:
    """
    Configuration for file management migration.

    This class controls the gradual rollout of the UnifiedFileManager,
    allowing safe migration from legacy file handlers with feature flags
    and percentage-based rollout.

    Rollout Strategy:
    - Shadow Mode: Run both implementations, compare results
    - 1%: Initial validation, monitor for errors
    - 10%: Expand to more users, gather performance data
    - 50%: Majority rollout, focus on edge cases
    - 100%: Full migration, decommission legacy
    """

    # ========================================================================
    # GLOBAL CONTROLS
    # ========================================================================

    # Master switch for unified file management
    # Set to False for emergency rollback to legacy handlers
    ENABLE_UNIFIED_MANAGER: bool = _parse_bool_env("ENABLE_UNIFIED_MANAGER", "false")

    # Enable automatic fallback to legacy on errors
    # Recommended: True during migration, False after full rollout
    ENABLE_FALLBACK_TO_LEGACY: bool = _parse_bool_env("ENABLE_FALLBACK_TO_LEGACY", "true")

    # Enable shadow mode (run both implementations and compare results)
    # Recommended: True during initial validation, False after confidence is established
    ENABLE_SHADOW_MODE: bool = _parse_bool_env("ENABLE_SHADOW_MODE", "false")

    # Shadow mode sampling rate (0.0 to 1.0)
    # 0.1 = 10% of operations run shadow mode comparison
    # Prevents overwhelming systems during high load
    SHADOW_MODE_SAMPLE_RATE: float = float(os.getenv("SHADOW_MODE_SAMPLE_RATE", "0.1"))

    # Shadow mode error threshold (0.0 to 1.0)
    # If shadow mode error rate exceeds this, auto-disable shadow mode
    # 0.05 = 5% error rate triggers circuit breaker
    SHADOW_MODE_ERROR_THRESHOLD: float = float(os.getenv("SHADOW_MODE_ERROR_THRESHOLD", "0.05"))

    # Minimum samples before evaluating error threshold
    # Prevents premature circuit breaker activation on small sample sizes
    SHADOW_MODE_MIN_SAMPLES: int = int(os.getenv("SHADOW_MODE_MIN_SAMPLES", "50"))

    # Maximum shadow mode operations per minute (rate limiting)
    # Prevents resource exhaustion during high load
    SHADOW_MODE_MAX_SAMPLES_PER_MINUTE: int = int(os.getenv("SHADOW_MODE_MAX_SAMPLES_PER_MINUTE", "100"))

    # Shadow mode duration limit in minutes (0 = unlimited)
    # Auto-disable shadow mode after this duration for safety
    SHADOW_MODE_DURATION_MINUTES: int = int(os.getenv("SHADOW_MODE_DURATION_MINUTES", "0"))

    # Cooldown period in minutes before shadow mode can be re-enabled
    # Prevents rapid on/off cycling
    SHADOW_MODE_COOLDOWN_MINUTES: int = int(os.getenv("SHADOW_MODE_COOLDOWN_MINUTES", "30"))

    # Include timing information in shadow mode comparisons
    # Useful for performance analysis
    SHADOW_MODE_INCLUDE_TIMING: bool = _parse_bool_env("SHADOW_MODE_INCLUDE_TIMING", "true")

    # Maximum retry attempts before giving up
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))

    # ========================================================================
    # PER-TOOL MIGRATION FLAGS
    # ========================================================================

    # Enable migration for KimiUploadFilesTool
    # This is the first tool to migrate (lowest risk)
    ENABLE_KIMI_MIGRATION: bool = _parse_bool_env("ENABLE_KIMI_MIGRATION", "false")

    # Enable migration for SmartFileHandler
    # Migrate after Kimi is stable (medium risk)
    ENABLE_SMART_HANDLER_MIGRATION: bool = _parse_bool_env("ENABLE_SMART_HANDLER_MIGRATION", "false")

    # Enable migration for SupabaseFileHandler
    # Migrate last (highest risk due to database integration)
    ENABLE_SUPABASE_MIGRATION: bool = _parse_bool_env("ENABLE_SUPABASE_MIGRATION", "false")

    # ========================================================================
    # ROLLOUT PERCENTAGES (0-100)
    # ========================================================================

    # Percentage of Kimi uploads to route through UnifiedFileManager
    # Start at 1%, increase gradually: 1 → 10 → 50 → 100
    KIMI_ROLLOUT_PERCENTAGE: int = int(os.getenv("KIMI_ROLLOUT_PERCENTAGE", "0"))

    # Percentage of SmartFileHandler operations to route through UnifiedFileManager
    SMART_HANDLER_ROLLOUT_PERCENTAGE: int = int(os.getenv("SMART_HANDLER_ROLLOUT_PERCENTAGE", "0"))

    # Percentage of Supabase operations to route through UnifiedFileManager
    SUPABASE_ROLLOUT_PERCENTAGE: int = int(os.getenv("SUPABASE_ROLLOUT_PERCENTAGE", "0"))

    # ========================================================================
    # MONITORING AND LOGGING
    # ========================================================================

    # Enable detailed logging for migration operations
    # Recommended: True during migration for debugging
    ENABLE_DETAILED_LOGGING: bool = _parse_bool_env("ENABLE_DETAILED_LOGGING", "true")

    # Sample rate for metrics collection (0.0 to 1.0)
    # 0.1 = 10% of operations are sampled for detailed metrics
    METRICS_SAMPLE_RATE: float = float(os.getenv("METRICS_SAMPLE_RATE", "0.1"))

    @classmethod
    def get_status(cls) -> dict:
        """
        Get current migration status.

        Returns:
            Dictionary with all migration configuration values
        """
        return {
            "global": {
                "unified_enabled": cls.ENABLE_UNIFIED_MANAGER,
                "fallback_enabled": cls.ENABLE_FALLBACK_TO_LEGACY,
                "shadow_mode_enabled": cls.ENABLE_SHADOW_MODE,
                "shadow_mode_sample_rate": cls.SHADOW_MODE_SAMPLE_RATE,
                "shadow_mode_error_threshold": cls.SHADOW_MODE_ERROR_THRESHOLD,
                "max_retries": cls.MAX_RETRY_ATTEMPTS
            },
            "per_tool_flags": {
                "kimi": cls.ENABLE_KIMI_MIGRATION,
                "smart_handler": cls.ENABLE_SMART_HANDLER_MIGRATION,
                "supabase": cls.ENABLE_SUPABASE_MIGRATION
            },
            "rollout_percentages": {
                "kimi": cls.KIMI_ROLLOUT_PERCENTAGE,
                "smart_handler": cls.SMART_HANDLER_ROLLOUT_PERCENTAGE,
                "supabase": cls.SUPABASE_ROLLOUT_PERCENTAGE
            },
            "monitoring": {
                "detailed_logging": cls.ENABLE_DETAILED_LOGGING,
                "metrics_sample_rate": cls.METRICS_SAMPLE_RATE
            }
        }

    @classmethod
    def validate_rollout_percentages(cls) -> bool:
        """
        Validate that all rollout percentages are within valid range (0-100).

        Returns:
            bool: True if all percentages are valid

        Raises:
            ValueError: If any percentage is out of range
        """
        percentages = {
            "KIMI_ROLLOUT_PERCENTAGE": cls.KIMI_ROLLOUT_PERCENTAGE,
            "SMART_HANDLER_ROLLOUT_PERCENTAGE": cls.SMART_HANDLER_ROLLOUT_PERCENTAGE,
            "SUPABASE_ROLLOUT_PERCENTAGE": cls.SUPABASE_ROLLOUT_PERCENTAGE
        }

        for name, value in percentages.items():
            if not (0 <= value <= 100):
                raise ValueError(
                    f"Invalid rollout percentage {name}={value}. "
                    f"Must be between 0 and 100."
                )

        return True

    @classmethod
    def validate_shadow_mode_config(cls) -> bool:
        """
        Validate shadow mode configuration parameters.

        Returns:
            bool: True if all shadow mode config is valid

        Raises:
            ValueError: If any configuration is invalid
        """
        # Validate sample rate (0.0 to 1.0)
        if not (0.0 <= cls.SHADOW_MODE_SAMPLE_RATE <= 1.0):
            raise ValueError(
                f"Invalid SHADOW_MODE_SAMPLE_RATE={cls.SHADOW_MODE_SAMPLE_RATE}. "
                f"Must be between 0.0 and 1.0."
            )

        # Validate error threshold (0.0 to 1.0)
        if not (0.0 <= cls.SHADOW_MODE_ERROR_THRESHOLD <= 1.0):
            raise ValueError(
                f"Invalid SHADOW_MODE_ERROR_THRESHOLD={cls.SHADOW_MODE_ERROR_THRESHOLD}. "
                f"Must be between 0.0 and 1.0."
            )

        # Validate minimum samples (must be positive)
        if cls.SHADOW_MODE_MIN_SAMPLES < 1:
            raise ValueError(
                f"Invalid SHADOW_MODE_MIN_SAMPLES={cls.SHADOW_MODE_MIN_SAMPLES}. "
                f"Must be at least 1."
            )

        # Validate max samples per minute (must be positive)
        if cls.SHADOW_MODE_MAX_SAMPLES_PER_MINUTE < 1:
            raise ValueError(
                f"Invalid SHADOW_MODE_MAX_SAMPLES_PER_MINUTE={cls.SHADOW_MODE_MAX_SAMPLES_PER_MINUTE}. "
                f"Must be at least 1."
            )

        # Validate duration (must be non-negative, 0 = unlimited)
        if cls.SHADOW_MODE_DURATION_MINUTES < 0:
            raise ValueError(
                f"Invalid SHADOW_MODE_DURATION_MINUTES={cls.SHADOW_MODE_DURATION_MINUTES}. "
                f"Must be non-negative (0 = unlimited)."
            )

        # Validate cooldown (must be non-negative)
        if cls.SHADOW_MODE_COOLDOWN_MINUTES < 0:
            raise ValueError(
                f"Invalid SHADOW_MODE_COOLDOWN_MINUTES={cls.SHADOW_MODE_COOLDOWN_MINUTES}. "
                f"Must be non-negative."
            )

        return True


# Validate migration configuration on module import
try:
    MigrationConfig.validate_rollout_percentages()
    MigrationConfig.validate_shadow_mode_config()
except ValueError as e:
    logger.warning(f"Migration configuration validation failed: {e}")
    # Don't raise - allow module to load but log the warning
