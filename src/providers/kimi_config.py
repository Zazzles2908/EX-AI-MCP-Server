"""Kimi model configuration and validation.

Last Updated: 2025-11-10
Last Verified: 2025-11-10 (against platform.moonshot.ai/docs/pricing/chat)
Added: kimi-k2-thinking, kimi-k2-thinking-turbo (official K2 thinking models)
"""

import logging
from typing import Optional

from .base import ModelCapabilities, ProviderType

logger = logging.getLogger(__name__)


# Kimi Model Configurations
# Last Verified: 2025-10-09 against https://platform.moonshot.ai/docs
SUPPORTED_MODELS: dict[str, ModelCapabilities] = {
    # Prioritize k2 preview models when allowed
    # Source: https://platform.moonshot.ai/docs/pricing/chat
    "kimi-k2-0905-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-k2-0905-preview",
        friendly_name="Kimi",
        context_window=262144,  # 256K = 262144 tokens (verified 2025-10-09 from platform.moonshot.ai)
        max_output_tokens=8192,
        supports_images=True,  # Supports vision
        max_image_size_mb=20.0,
        supports_function_calling=True,  # Supports ToolCalls
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        supports_json_mode=True,
        description="Kimi K2 2024-09 preview with 256K context, vision, and structured output",
        aliases=["kimi-k2-0905", "kimi-k2"],
    ),
    "kimi-k2-0711-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-k2-0711-preview",
        friendly_name="Kimi",
        context_window=131072,  # 128K = 131072 tokens (verified 2025-10-09 from platform.moonshot.ai/docs/pricing/chat)
        max_output_tokens=8192,
        supports_images=False,  # Does NOT support vision (verified 2025-10-09)
        max_image_size_mb=0.0,
        supports_function_calling=True,  # Supports ToolCalls
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        supports_json_mode=True,
        description="Kimi K2 2024-07 preview with 128K context (no vision) and structured output",
        aliases=["kimi-k2-0711"],
    ),
    # K2 Thinking models - Official models from https://platform.moonshot.ai/docs/pricing/chat
    "kimi-k2-thinking": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-k2-thinking",
        friendly_name="Kimi",
        context_window=262144,  # 256K = 262144 tokens (from official pricing page)
        max_output_tokens=8192,
        supports_images=True,  # Supports vision
        max_image_size_mb=20.0,
        supports_function_calling=True,  # Supports ToolCalls
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=True,  # ✅ Extended thinking support
        supports_json_mode=True,
        description="Kimi K2 model with extended thinking mode - 256K context with reasoning capabilities",
        aliases=["kimi-k2-thinking", "kimi-thinking-k2"],
    ),
    "kimi-k2-thinking-turbo": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-k2-thinking-turbo",
        friendly_name="Kimi",
        context_window=262144,  # 256K = 262144 tokens (from official pricing page)
        max_output_tokens=8192,
        supports_images=True,  # Supports vision
        max_image_size_mb=20.0,
        supports_function_calling=True,  # Supports ToolCalls
        supports_streaming=True,  # High-speed (60-100 tokens/sec)
        supports_system_prompts=True,
        supports_extended_thinking=True,  # ✅ Extended thinking support
        supports_json_mode=True,
        description="Kimi K2 Turbo model with extended thinking mode - 256K high-speed context with reasoning",
        aliases=["kimi-k2-thinking-turbo", "kimi-thinking-k2-turbo"],
    ),
    # Canonical moonshot v1 series
    "moonshot-v1-8k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-8k",
        friendly_name="Kimi",
        context_window=8192,
        max_output_tokens=2048,
        supports_images=False,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 8k",
    ),
    "moonshot-v1-32k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-32k",
        friendly_name="Kimi",
        context_window=32768,
        max_output_tokens=4096,
        supports_images=False,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 32k",
    ),
    # New models from Moonshot docs
    "kimi-k2-turbo-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-k2-turbo-preview",
        friendly_name="Kimi",
        context_window=262144,  # 256K = 262144 tokens (verified 2025-10-09)
        max_output_tokens=8192,
        supports_images=True,  # Supports vision
        max_image_size_mb=20.0,
        supports_function_calling=True,  # Supports ToolCalls
        supports_streaming=True,  # 60-100 tokens/sec
        supports_system_prompts=True,
        supports_extended_thinking=False,
        supports_json_mode=True,
        description="Kimi K2 Turbo high-speed 256K (60-100 tokens/sec) with structured output",
        aliases=["kimi-k2-turbo"],
    ),
    "moonshot-v1-128k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-128k",
        friendly_name="Kimi",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=False,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 128k",
    ),
    "moonshot-v1-8k-vision-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-8k-vision-preview",
        friendly_name="Kimi",
        context_window=8192,
        max_output_tokens=2048,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 8k vision preview",
    ),
    "moonshot-v1-32k-vision-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-32k-vision-preview",
        friendly_name="Kimi",
        context_window=32768,
        max_output_tokens=4096,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 32k vision preview",
    ),
    "moonshot-v1-128k-vision-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="moonshot-v1-128k-vision-preview",
        friendly_name="Kimi",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=False,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Moonshot v1 128k vision preview",
    ),
    "kimi-latest": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-latest",
        friendly_name="Kimi",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Kimi latest vision 128k",
    ),
    "kimi-latest-8k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-latest-8k",
        friendly_name="Kimi Latest 8K",
        context_window=8192,
        max_output_tokens=2048,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Kimi latest vision 8k",
    ),
    "kimi-latest-32k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-latest-32k",
        friendly_name="Kimi Latest 32K",
        context_window=32768,
        max_output_tokens=4096,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Kimi latest vision 32k",
    ),
    "kimi-latest-128k": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-latest-128k",
        friendly_name="Kimi Latest 128K",
        context_window=131072,  # 128K = 131072 tokens
        max_output_tokens=8192,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        description="Kimi latest vision 128k",
    ),
    "kimi-thinking-preview": ModelCapabilities(
        provider=ProviderType.KIMI,
        model_name="kimi-thinking-preview",
        friendly_name="Kimi Thinking",
        context_window=131072,  # 128K = 131072 tokens
        max_output_tokens=8192,
        supports_images=True,
        max_image_size_mb=20.0,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=True,  # ✅ KEEP: Model DOES support extended thinking
        supports_json_mode=True,
        description="Kimi multimodal reasoning 128k with extended thinking (reasoning_content field) and structured output",
        # ❌ REMOVED (2025-11-03): thinking_mode_config dict was fiction
        # External AI fact-check: X-Moonshot-Thinking header does NOT exist
        # Thinking mode works automatically - no special headers needed
        # Response field is 'reasoning_content' (returned automatically)
        aliases=["kimi-thinking"],
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
        # Default capability if unknown model (use safe defaults)
        return ModelCapabilities(
            provider=ProviderType.KIMI,
            model_name=resolved,
            friendly_name="Kimi",
            context_window=8192,
            max_output_tokens=2048,
            supports_images=False,
            supports_function_calling=False,
            supports_streaming=True,
            supports_system_prompts=True,
            supports_extended_thinking=False,
            supports_json_mode=True,
        )
    return caps


def count_tokens(text: str, model_name: str) -> int:
    """Count tokens with language-aware heuristics.
    
    Kimi is often used with Chinese text, so this uses a language-aware
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
            if (0x4E00 <= o <= 0x9FFF) or (0x3040 <= o <= 0x30FF) or (0x3400 <= o <= 0x4DBF):
                cjk += 1
        ratio = cjk / max(1, total)
        if ratio > 0.2:
            return max(1, int(total * 0.6))
        return max(1, int(total / 4))
    except Exception:
        return max(1, len(text) // 4)


__all__ = [
    "SUPPORTED_MODELS",
    "get_all_model_aliases",
    "get_capabilities",
    "count_tokens",
]

