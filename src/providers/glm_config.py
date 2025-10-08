"""GLM model configuration and validation."""

import logging
from typing import Optional

from .base import ModelCapabilities, ProviderType

logger = logging.getLogger(__name__)


# GLM Model Configurations
# NOTE: Only glm-4-plus and glm-4.6 support NATIVE web search via tools parameter
# Other models can still use web search via direct /web_search API endpoint
# See tools/providers/glm/glm_web_search.py for direct API implementation
SUPPORTED_MODELS: dict[str, ModelCapabilities] = {
    "glm-4-plus": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4-plus",
        friendly_name="GLM-4-Plus",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4 Plus - supports websearch",
    ),
    "glm-4-flash": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4-flash",
        friendly_name="GLM-4-Flash",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4 Flash - fast and cheap",
    ),
    "glm-4.6": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.6",
        friendly_name="GLM-4.6",
        context_window=200000,  # 200K context window
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4.6 flagship model with 200K context window - supports websearch",
    ),
    "glm-4.5-flash": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5-flash",
        friendly_name="GLM-4.5-Flash",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4.5 Flash - fast, does not support native web search tool calling (use direct API instead)",
    ),
    "glm-4.5": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5",
        friendly_name="GLM-4.5",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4.5 standard",
    ),
    "glm-4.5-air": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5-air",
        friendly_name="GLM-4.5-Air",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4.5 Air - lightweight",
        aliases=["glm-4.5-x"],  # GLM-4.5-X is an alias for glm-4.5-air
    ),
    "glm-4.5v": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5v",
        friendly_name="GLM-4.5V",
        context_window=65536,  # 64K = 65536 tokens
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="GLM 4.5V - Vision-language multimodal model with 64K context",
    ),
}


def get_all_model_aliases(supported_models: dict[str, ModelCapabilities]) -> dict[str, list[str]]:
    """Get all model aliases from supported models.
    
    Args:
        supported_models: Dictionary of supported model configurations
        
    Returns:
        Dictionary mapping model names to their aliases
    """
    result = {}
    for name, caps in supported_models.items():
        if caps.aliases:
            result[name] = caps.aliases
    return result


def get_capabilities(
    model_name: str,
    supported_models: dict[str, ModelCapabilities],
    resolve_func
) -> ModelCapabilities:
    """Get capabilities for a model.
    
    Args:
        model_name: Name of the model
        supported_models: Dictionary of supported model configurations
        resolve_func: Function to resolve model name (handles aliases)
        
    Returns:
        ModelCapabilities for the model
    """
    resolved = resolve_func(model_name)
    caps = supported_models.get(resolved)
    if not caps:
        # Return default capabilities for unknown models
        return ModelCapabilities(
            provider=ProviderType.GLM,
            model_name=resolved,
            friendly_name="GLM",
            context_window=8192,
            max_output_tokens=2048,
            supports_images=False,
            supports_function_calling=False,
            supports_streaming=True,
            supports_system_prompts=True,
            supports_extended_thinking=False,
        )
    return caps


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens with language-aware heuristics.
    
    GLM is often used with Chinese text, so this uses a language-aware
    heuristic: ~0.6 tokens/char for CJK, ~0.25 tokens/char for ASCII/Latin.
    
    Args:
        text: Text to count tokens for
        model_name: Model name (currently unused, for future model-specific logic)
        
    Returns:
        Estimated token count
    """
    if not text:
        return 1
    
    try:
        total = len(text)
        cjk = 0
        for ch in text:
            o = ord(ch)
            # CJK Unified Ideographs + Japanese Hiragana/Katakana ranges
            if (0x4E00 <= o <= 0x9FFF) or (0x3040 <= o <= 0x30FF) or (0x3400 <= o <= 0x4DBF):
                cjk += 1
        
        ratio = cjk / max(1, total)
        if ratio > 0.2:
            # Predominantly CJK text
            return max(1, int(total * 0.6))
        
        # ASCII/Latin heuristic
        return max(1, int(total / 4))
    except Exception:
        # Fallback to simple heuristic
        return max(1, len(text) // 4)


__all__ = [
    "SUPPORTED_MODELS",
    "get_all_model_aliases",
    "get_capabilities",
    "count_tokens",
]

