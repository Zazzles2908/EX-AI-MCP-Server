"""
Model-specific configuration for token limits and capabilities.

This module provides centralized configuration for different AI models,
including context window sizes, max output tokens, and default settings.

Created: 2025-10-21 (Phase 2.1.1.1)
Purpose: Replace hardcoded provider-level limits with model-specific limits
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Model-specific token limits
# Based on official documentation from Moonshot AI and Z.ai
# Sources:
# - Moonshot: https://platform.moonshot.ai/docs/pricing/chat
# - Z.ai: https://github.com/zai-org/GLM-4.5 (README.md)
# - User corrections: 2025-10-21
MODEL_TOKEN_LIMITS = {
    # ============================================================================
    # Moonshot/Kimi Models
    # ============================================================================
    'moonshot-v1-8k': {
        'max_context_tokens': 8192,
        'max_output_tokens': 7168,  # context - safety margin
        'default_output_tokens': 4096,
        'provider': 'kimi'
    },
    'moonshot-v1-32k': {
        'max_context_tokens': 32768,
        'max_output_tokens': 28672,
        'default_output_tokens': 8192,
        'provider': 'kimi'
    },
    'moonshot-v1-128k': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    # K2 models (per official docs and user correction)
    'kimi-k2-0905-preview': {
        'max_context_tokens': 262144,  # 256K
        'max_output_tokens': 229376,  # 256K - safety margin
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    'kimi-k2-0711-preview': {
        'max_context_tokens': 131072,  # 128K (NOT 256K!)
        'max_output_tokens': 114688,
        'default_output_tokens': 8192,
        'provider': 'kimi'
    },
    'kimi-k2-turbo-preview': {
        'max_context_tokens': 262144,  # 256K
        'max_output_tokens': 229376,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    # K2 Thinking Models (PREMIUM - 256K with extended thinking)
    'kimi-k2-thinking': {
        'max_context_tokens': 262144,  # 256K
        'max_output_tokens': 229376,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    'kimi-k2-thinking-turbo': {
        'max_context_tokens': 262144,  # 256K
        'max_output_tokens': 229376,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    # Thinking model - 128K context (per official docs)
    'kimi-thinking-preview': {
        'max_context_tokens': 131072,  # 128K
        'max_output_tokens': 114688,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    # Latest variants
    'kimi-latest': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },
    'kimi-latest-8k': {
        'max_context_tokens': 8192,
        'max_output_tokens': 7168,
        'default_output_tokens': 4096,
        'provider': 'kimi'
    },
    'kimi-latest-32k': {
        'max_context_tokens': 32768,
        'max_output_tokens': 28672,
        'default_output_tokens': 8192,
        'provider': 'kimi'
    },
    'kimi-latest-128k': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 16384,
        'provider': 'kimi'
    },

    # ============================================================================
    # GLM Models (Z.ai)
    # ============================================================================
    # GLM-4.6 - 200K context (per user correction and GitHub README)
    'glm-4.6': {
        'max_context_tokens': 204800,  # 200K
        'max_output_tokens': 180224,  # 200K - safety margin
        'default_output_tokens': 16384,
        'provider': 'glm'
    },
    # GLM-4.5 series - 128K context (per official docs)
    'glm-4.5': {
        'max_context_tokens': 131072,  # 128K
        'max_output_tokens': 114688,
        'default_output_tokens': 16384,
        'provider': 'glm'
    },
    'glm-4.5-flash': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 8192,  # Lower default for faster model
        'provider': 'glm'
    },
    'glm-4.5-air': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 4096,  # Lower default for lightweight model
        'provider': 'glm'
    },
    'glm-4.5-airx': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 4096,
        'provider': 'glm'
    },
    'glm-4.5v': {
        'max_context_tokens': 131072,
        'max_output_tokens': 114688,
        'default_output_tokens': 8192,  # Vision model
        'provider': 'glm'
    },

    # ============================================================================
    # MiniMax Models (Z.ai)
    # ============================================================================
    # Based on official MiniMax API documentation
    # Reference: https://platform.minimax.io/docs/api-reference/text-anthropic-api
    'MiniMax-M2': {
        'max_context_tokens': 8192,   # Anthropic-compatible context window
        'max_output_tokens': 4096,    # Per documentation examples
        'default_output_tokens': 2048,
        'provider': 'minimax'
    },
    'MiniMax-M2-Stable': {
        'max_context_tokens': 8192,   # Anthropic-compatible context window  
        'max_output_tokens': 4096,    # Per documentation examples
        'default_output_tokens': 2048,
        'provider': 'minimax'
    },
    'abab6.5s-chat': {
        'max_context_tokens': 8192,   # Standard context for chat models
        'max_output_tokens': 4096,
        'default_output_tokens': 2048,
        'provider': 'minimax'
    },
    'abab6.5g-chat': {
        'max_context_tokens': 8192,   # Standard context for chat models
        'max_output_tokens': 4096,
        'default_output_tokens': 2048,
        'provider': 'minimax'
    },
}


def get_model_token_limits(model_name: str) -> Dict[str, int]:
    """
    Get token limits for a specific model with intelligent fallback.
    
    Args:
        model_name: The model identifier (e.g., 'moonshot-v1-8k', 'glm-4.6')
    
    Returns:
        Dictionary with keys:
        - max_context_tokens: Maximum total context window
        - max_output_tokens: Maximum tokens for output
        - default_output_tokens: Recommended default for output
        - provider: Provider name ('kimi' or 'glm')
    """
    # Direct lookup
    if model_name in MODEL_TOKEN_LIMITS:
        return MODEL_TOKEN_LIMITS[model_name].copy()
    
    # Fallback logic based on model name patterns
    logger.debug(f"Model '{model_name}' not in MODEL_TOKEN_LIMITS, using fallback logic")
    
    # Check for context size hints in model name
    if '8k' in model_name.lower():
        return {
            'max_context_tokens': 8192,
            'max_output_tokens': 7168,
            'default_output_tokens': 4096,
            'provider': 'unknown'
        }
    elif '32k' in model_name.lower():
        return {
            'max_context_tokens': 32768,
            'max_output_tokens': 28672,
            'default_output_tokens': 8192,
            'provider': 'unknown'
        }
    elif '128k' in model_name.lower():
        return {
            'max_context_tokens': 131072,
            'max_output_tokens': 114688,
            'default_output_tokens': 16384,
            'provider': 'unknown'
        }
    
    # Safe conservative default for unknown models
    logger.warning(
        f"Unknown model '{model_name}', using conservative defaults. "
        f"Consider adding to MODEL_TOKEN_LIMITS for optimal performance."
    )
    return {
        'max_context_tokens': 8192,
        'max_output_tokens': 4096,
        'default_output_tokens': 2048,
        'provider': 'unknown'
    }


def validate_max_tokens(
    model_name: str,
    requested_max_tokens: Optional[int],
    input_tokens: int = 0,
    enforce_limits: bool = True
) -> Optional[int]:
    """
    Validate and adjust max_tokens based on model capabilities.
    
    Args:
        model_name: The model identifier
        requested_max_tokens: User requested max tokens (None = use default)
        input_tokens: Number of tokens in the input prompt (for context limit check)
        enforce_limits: Whether to enforce limits (from ENFORCE_MAX_TOKENS config)
    
    Returns:
        Validated max_tokens value, or None if no limit should be set
    """
    if not enforce_limits and requested_max_tokens is None:
        # No enforcement and no explicit request = no limit
        return None
    
    model_config = get_model_token_limits(model_name)
    max_output_limit = model_config['max_output_tokens']
    max_context_limit = model_config['max_context_tokens']
    default_output = model_config['default_output_tokens']
    
    # If no explicit request, use default
    if requested_max_tokens is None:
        if enforce_limits:
            logger.debug(f"Using default max_tokens={default_output} for model {model_name}")
            return default_output
        return None
    
    # Validate type and convert
    try:
        tokens = int(requested_max_tokens)
    except (ValueError, TypeError):
        logger.warning(
            f"Invalid max_output_tokens type: {type(requested_max_tokens)}. "
            f"Using default {default_output}"
        )
        return default_output if enforce_limits else None
    
    # Check for negative or zero
    if tokens <= 0:
        logger.warning(f"Invalid max_output_tokens={tokens}, must be positive. Using default {default_output}")
        return default_output if enforce_limits else None
    
    # Calculate available tokens for output (if input_tokens provided)
    if input_tokens > 0:
        available_output_tokens = max_context_limit - input_tokens
        effective_max = min(max_output_limit, available_output_tokens)
        
        if tokens > effective_max:
            logger.warning(
                f"Requested max_tokens ({tokens}) exceeds available tokens for model {model_name} "
                f"(max_output={max_output_limit}, available={available_output_tokens}). "
                f"Adjusting to {effective_max}"
            )
            return effective_max
    else:
        # No input token count, just check against max_output_limit
        if tokens > max_output_limit:
            logger.warning(
                f"Requested max_tokens ({tokens}) exceeds model {model_name} limit "
                f"({max_output_limit}). Adjusting to {max_output_limit}"
            )
            return max_output_limit
    
    # Ensure minimum reasonable output
    min_output = 256  # Minimum tokens for meaningful response
    if tokens < min_output:
        logger.info(f"Requested max_tokens ({tokens}) is low. Using {tokens} as requested.")
        # Don't override - user might want short responses
    
    return tokens


def get_default_max_tokens(model_name: str) -> int:
    """
    Get the recommended default max_tokens for a model.
    
    Args:
        model_name: The model identifier
    
    Returns:
        Recommended default max_tokens value
    """
    model_config = get_model_token_limits(model_name)
    return model_config['default_output_tokens']


def get_max_output_tokens(model_name: str) -> int:
    """
    Get the maximum output tokens for a model.
    
    Args:
        model_name: The model identifier
    
    Returns:
        Maximum output tokens value
    """
    model_config = get_model_token_limits(model_name)
    return model_config['max_output_tokens']

