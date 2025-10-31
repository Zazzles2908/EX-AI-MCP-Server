"""
Operational configuration for EX MCP Server

This module contains configuration that defines how the system RUNS:
- Production settings (logging, retries, timeouts)
- Performance settings (concurrency, rate limiting, caching)
- Security settings (API key validation, input security)
- MCP protocol limits and token budgets

Configuration values can be overridden by environment variables where appropriate.
"""

import os


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
# PRODUCTION SETTINGS
# ============================================================================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
ENABLE_FALLBACK: bool = _parse_bool_env("ENABLE_FALLBACK", "true")


# ============================================================================
# MCP WEBSOCKET CONFIGURATION
# ============================================================================
MCP_WEBSOCKET_ENABLED: bool = _parse_bool_env("MCP_WEBSOCKET_ENABLED", "true")
MCP_WEBSOCKET_PORT: int = int(os.getenv("MCP_WEBSOCKET_PORT", "8080"))
MCP_WEBSOCKET_HOST: str = os.getenv("MCP_WEBSOCKET_HOST", "0.0.0.0")


# ============================================================================
# PERFORMANCE SETTINGS
# ============================================================================
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


# ============================================================================
# SECURITY SETTINGS
# ============================================================================
VALIDATE_API_KEYS: bool = _parse_bool_env("VALIDATE_API_KEYS", "true")

# Input Security (CHANGED 2025-10-16: Default TRUE for security-by-default)
# Prevents path traversal attacks and validates file paths
# SECURE_INPUTS_ENFORCED: Validates file paths to prevent directory traversal
SECURE_INPUTS_ENFORCED: bool = _parse_bool_env("SECURE_INPUTS_ENFORCED", "true")


# ============================================================================
# FEATURE FLAGS
# ============================================================================
# Activity tool feature flags (default OFF)
ACTIVITY_SINCE_UNTIL_ENABLED: bool = _parse_bool_env("ACTIVITY_SINCE_UNTIL_ENABLED", "false")
ACTIVITY_STRUCTURED_OUTPUT_ENABLED: bool = _parse_bool_env("ACTIVITY_STRUCTURED_OUTPUT_ENABLED", "false")

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

