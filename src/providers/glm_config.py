"""GLM model configuration and validation.

Last Updated: 2025-11-08
Last Verified: 2025-11-08 (against z.ai official documentation)
NOTE: Using actual z.ai API model names as per https://docs.z.ai/
"""

import logging
from typing import Optional

from .base import ModelCapabilities, ProviderType

logger = logging.getLogger(__name__)


# GLM Model Configurations
# Last Updated: 2025-11-08
# Last Verified: 2025-11-08 against https://docs.z.ai/ guides
# NOTE: ALL GLM models support web search functionality
SUPPORTED_MODELS: dict[str, ModelCapabilities] = {
    "glm-4.6": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.6",
        friendly_name="GLM-4.6",
        context_window=200000,
        max_output_tokens=128000,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=True,
        supports_json_mode=True,
        description="GLM 4.6 flagship with 200K context, thinking mode, superior coding, structured output",
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
        supports_extended_thinking=True,
        supports_json_mode=True,
        description="GLM 4.5 hybrid reasoning model with thinking mode and structured output",
    ),
    "glm-4.5v": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5v",
        friendly_name="GLM-4.5V",
        context_window=65536,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=True,
        supports_json_mode=True,
        description="GLM 4.5V - Vision-language multimodal with thinking mode and structured output",
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
        supports_extended_thinking=True,
        supports_json_mode=True,
        description="GLM 4.5 Air - efficient hybrid reasoning with thinking mode and structured output",
    ),
    "glm-4.5-airx": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5-airx",
        friendly_name="GLM-4.5-AirX",
        context_window=128000,
        max_output_tokens=8192,
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=True,
        supports_json_mode=True,
        description="GLM 4.5 AirX - enhanced efficiency with thinking mode and structured output",
    ),
    "glm-4.5-flash": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4.5-flash",
        friendly_name="GLM-4.5-Flash",
        context_window=128000,
        max_output_tokens=98304,   # 96K (verified 2025-11-08 from z.ai docs)
        supports_images=True,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        supports_json_mode=True,
        description="GLM 4.5 Flash - fast and cost-effective with structured output (FREE)",
    ),
    "glm-4-32b": ModelCapabilities(
        provider=ProviderType.GLM,
        model_name="glm-4-32b-0414-128k",
        friendly_name="GLM-4-32B",
        context_window=131072,
        max_output_tokens=8192,
        supports_images=False,
        supports_function_calling=True,
        supports_streaming=True,
        supports_system_prompts=True,
        supports_extended_thinking=False,
        supports_json_mode=True,
        description="GLM 4-32B - 128K context with competitive pricing and structured output",
    ),
}


def get_all_model_aliases(supported_models: dict[str, ModelCapabilities]) -> dict[str, list[str]]:
    result = {}
    for name, caps in supported_models.items():
        if caps.aliases:
            result[name] = caps.aliases
    return result


def resolve_model_name_for_glm(model_name: str) -> str:
    if model_name in SUPPORTED_MODELS:
        return model_name

    model_name_lower = model_name.lower()
    for base_model in SUPPORTED_MODELS:
        if base_model.lower() == model_name_lower:
            return base_model

    all_aliases = get_all_model_aliases(SUPPORTED_MODELS)
    for base_model, aliases in all_aliases.items():
        if any(alias.lower() == model_name_lower for alias in aliases):
            return base_model

    return model_name


def get_capabilities(
    model_name: str,
    supported_models: dict[str, ModelCapabilities],
    resolve_func
) -> ModelCapabilities:
    resolved = resolve_func(model_name)
    caps = supported_models.get(resolved)
    if not caps:
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
            supports_json_mode=True,
        )
    return caps


def count_tokens(text: str, model_name: str) -> int:
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
