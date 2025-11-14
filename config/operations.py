"""
Operational configuration for EX MCP Server

This module contains configuration that defines how the system RUNS:
- Production settings (logging, retries, timeouts)
- Performance settings (concurrency, rate limiting, caching)
- Security settings (API key validation, input security)
- MCP protocol limits and token budgets
- Timeout hierarchy (consolidated from config/timeouts.py)

Configuration values can be overridden by environment variables where appropriate.
"""

import os
import logging
from .base import BaseConfig

logger = logging.getLogger(__name__)


class OperationsConfig(BaseConfig):
    """Operational configuration with timeout hierarchy"""

    # ============================================================================
    # PRODUCTION SETTINGS
    # ============================================================================
    LOG_LEVEL: str = BaseConfig.get_str("LOG_LEVEL", "INFO")
    MAX_RETRIES: int = BaseConfig.get_int("MAX_RETRIES", 3)
    REQUEST_TIMEOUT: int = BaseConfig.get_int("REQUEST_TIMEOUT", 30)
    ENABLE_FALLBACK: bool = BaseConfig.get_bool("ENABLE_FALLBACK", True)

    # ============================================================================
    # MCP WEBSOCKET CONFIGURATION
    # ============================================================================
    MCP_WEBSOCKET_ENABLED: bool = BaseConfig.get_bool("MCP_WEBSOCKET_ENABLED", True)
    MCP_WEBSOCKET_PORT: int = BaseConfig.get_int("MCP_WEBSOCKET_PORT", 8080)
    MCP_WEBSOCKET_HOST: str = BaseConfig.get_str("MCP_WEBSOCKET_HOST", "0.0.0.0")

    # ============================================================================
    # PERFORMANCE SETTINGS
    # ============================================================================
    MAX_CONCURRENT_REQUESTS: int = BaseConfig.get_int("MAX_CONCURRENT_REQUESTS", 10)
    RATE_LIMIT_PER_MINUTE: int = BaseConfig.get_int("RATE_LIMIT_PER_MINUTE", 100)
    CACHE_ENABLED: bool = BaseConfig.get_bool("CACHE_ENABLED", True)
    CACHE_TTL: int = BaseConfig.get_int("CACHE_TTL", 300)

    # BUG FIX #11 (2025-10-19): Async Supabase operations for non-blocking conversation persistence
    # When enabled, Supabase writes use fire-and-forget pattern to avoid blocking responses
    # Reads remain synchronous (we need the data), but writes return immediately
    USE_ASYNC_SUPABASE: bool = BaseConfig.get_bool("USE_ASYNC_SUPABASE", True)
    ENABLE_SUPABASE_WRITE_CACHING: bool = BaseConfig.get_bool("ENABLE_SUPABASE_WRITE_CACHING", True)

    # BUG FIX #11 (2025-10-20): Conversation queue configuration for async write pattern
    # Replaces ThreadPoolExecutor with async queue to prevent resource exhaustion
    CONVERSATION_QUEUE_SIZE: int = BaseConfig.get_int("CONVERSATION_QUEUE_SIZE", 1000)
    CONVERSATION_QUEUE_WARNING_THRESHOLD: int = BaseConfig.get_int("CONVERSATION_QUEUE_WARNING_THRESHOLD", 500)

    # ============================================================================
    # SECURITY SETTINGS
    # ============================================================================
    VALIDATE_API_KEYS: bool = BaseConfig.get_bool("VALIDATE_API_KEYS", True)

    # Input Security (CHANGED 2025-10-16: Default TRUE for security-by-default)
    # Prevents path traversal attacks and validates file paths
    # SECURE_INPUTS_ENFORCED: Validates file paths to prevent directory traversal
    SECURE_INPUTS_ENFORCED: bool = BaseConfig.get_bool("SECURE_INPUTS_ENFORCED", True)


    # ============================================================================
    # TIMEOUT HIERARCHY (Consolidated from config/timeouts.py)
    # ============================================================================
    # Tool-level timeouts (primary)
    SIMPLE_TOOL_TIMEOUT_SECS: int = BaseConfig.get_int("SIMPLE_TOOL_TIMEOUT_SECS", 30)
    WORKFLOW_TOOL_TIMEOUT_SECS: int = BaseConfig.get_int("WORKFLOW_TOOL_TIMEOUT_SECS", 46)
    EXPERT_ANALYSIS_TIMEOUT_SECS: int = BaseConfig.get_int("EXPERT_ANALYSIS_TIMEOUT_SECS", 60)

    # Provider timeouts
    GLM_TIMEOUT_SECS: int = BaseConfig.get_int("GLM_TIMEOUT_SECS", 30)
    KIMI_TIMEOUT_SECS: int = BaseConfig.get_int("KIMI_TIMEOUT_SECS", 40)
    KIMI_WEB_SEARCH_TIMEOUT_SECS: int = BaseConfig.get_int("KIMI_WEB_SEARCH_TIMEOUT_SECS", 30)

    # Model-specific timeout multipliers
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
        """Get adaptive timeout for a specific model"""
        multiplier = cls.MODEL_TIMEOUT_MULTIPLIERS.get(model_name, 1.0)
        return base_timeout * multiplier

    @classmethod
    def get_daemon_timeout(cls) -> int:
        """Get daemon timeout (1.5x max tool timeout)"""
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 1.5)

    @classmethod
    def get_shim_timeout(cls) -> int:
        """Get shim timeout (2x max tool timeout)"""
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.0)

    @classmethod
    def get_client_timeout(cls) -> int:
        """Get client timeout (2.5x max tool timeout)"""
        return int(cls.WORKFLOW_TOOL_TIMEOUT_SECS * 2.5)

    # ============================================================================
    # FEATURE FLAGS
    # ============================================================================
    # Activity tool feature flags (default OFF)
    ACTIVITY_SINCE_UNTIL_ENABLED: bool = BaseConfig.get_bool("ACTIVITY_SINCE_UNTIL_ENABLED", False)
    ACTIVITY_STRUCTURED_OUTPUT_ENABLED: bool = BaseConfig.get_bool("ACTIVITY_STRUCTURED_OUTPUT_ENABLED", False)

    # Consensus timeout and rate limiting settings
    DEFAULT_CONSENSUS_TIMEOUT: float = 120.0  # 2 minutes per model
    DEFAULT_CONSENSUS_MAX_INSTANCES_PER_COMBINATION: int = 2

    # NOTE: Consensus tool now uses sequential processing for MCP compatibility
    # Concurrent processing was removed to avoid async pattern violations


    # ============================================================================
    # MCP PROTOCOL TRANSPORT LIMITS
    # ============================================================================
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

    @staticmethod
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

    MCP_PROMPT_SIZE_LIMIT: int = _calculate_mcp_prompt_limit.__func__()

    # ============================================================================
    # MODEL OUTPUT TOKEN LIMITS
    # ============================================================================
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
    DEFAULT_MAX_OUTPUT_TOKENS: int = BaseConfig.get_int("DEFAULT_MAX_OUTPUT_TOKENS", 8192)
    KIMI_MAX_OUTPUT_TOKENS: int = BaseConfig.get_int("KIMI_MAX_OUTPUT_TOKENS", 16384)
    GLM_MAX_OUTPUT_TOKENS: int = BaseConfig.get_int("GLM_MAX_OUTPUT_TOKENS", 8192)

    # Whether to enforce max_tokens even when not explicitly requested
    # Set to False to only use max_tokens when explicitly provided by the caller
    # Set to True to always enforce max_tokens using the defaults above
    ENFORCE_MAX_TOKENS: bool = BaseConfig.get_bool("ENFORCE_MAX_TOKENS", True)

    # Language/Locale Configuration
    # LOCALE: Language/locale specification for AI responses
    # When set, all AI tools will respond in the specified language while
    # maintaining their analytical capabilities
    # Examples: "fr-FR", "en-US", "zh-CN", "zh-TW", "ja-JP", "ko-KR", "es-ES",
    # "de-DE", "it-IT", "pt-PT"
    # Leave empty for default language (English)
    LOCALE: str = BaseConfig.get_str("LOCALE", "")

