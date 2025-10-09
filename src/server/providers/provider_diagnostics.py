"""
Provider Diagnostics Module

Handles logging, diagnostics, and snapshot generation for provider configuration.
"""

import json
import logging
from pathlib import Path
from time import time as _now
from typing import List

logger = logging.getLogger(__name__)


def log_provider_summary(valid_providers: List[str]):
    """
    Log summary of configured providers.
    
    Args:
        valid_providers: List of valid provider names
    """
    if not valid_providers:
        logger.warning("No valid providers configured")
        return
    
    logger.info(f"Available providers: {', '.join(valid_providers)}")
    
    # Diagnostic: summarize configured providers and model counts
    try:
        from src.providers.registry import ModelProviderRegistry
        from src.providers.base import ProviderType
        
        with_keys = [p.name for p in ModelProviderRegistry.get_available_providers_with_keys()]
        glm_models = ModelProviderRegistry.get_available_model_names(provider_type=ProviderType.GLM)
        kimi_models = ModelProviderRegistry.get_available_model_names(provider_type=ProviderType.KIMI)
        
        logger.info(
            "Providers configured: %s; GLM models: %d; Kimi models: %d",
            ", ".join(with_keys) if with_keys else "none",
            len(glm_models),
            len(kimi_models),
        )
    except Exception as e:
        logger.debug(f"Provider availability summary skipped: {e}")


def write_provider_snapshot():
    """
    Write provider registry snapshot to JSON file for diagnostics.

    Creates logs/provider_registry_snapshot.json with:
    - Timestamp
    - Registered providers
    - Initialized providers (with keys)
    - Available models with detailed capabilities
    """
    try:
        from src.providers.registry import ModelProviderRegistry
        from src.providers.base import ProviderType

        reg = ModelProviderRegistry()

        # Registered providers reflect classes known to the registry (post-registration)
        registered = [p.name for p in reg.get_available_providers()]

        # Initialized providers require keys and successful init
        with_keys_snapshot = [p.name for p in ModelProviderRegistry.get_available_providers_with_keys()]

        # Available models mapping (respects restrictions)
        models_map = ModelProviderRegistry.get_available_models(respect_restrictions=True)

        # Build detailed model info
        detailed_models = {}
        for model_name, provider_type in models_map.items():
            try:
                caps = ModelProviderRegistry.get_capabilities(model_name)
                detailed_models[model_name] = {
                    "provider": provider_type.name if hasattr(provider_type, "name") else str(provider_type),
                    "context_window": caps.context_window,
                    "max_output_tokens": caps.max_output_tokens,
                    "supports_function_calling": caps.supports_function_calling,
                    "supports_images": caps.supports_images,
                    "supports_streaming": caps.supports_streaming,
                    "supports_extended_thinking": caps.supports_extended_thinking,
                    "description": caps.description if hasattr(caps, "description") else "",
                }
            except Exception:
                # Fallback to simple provider name if capabilities lookup fails
                detailed_models[model_name] = {
                    "provider": provider_type.name if hasattr(provider_type, "name") else str(provider_type),
                }

        snapshot = {
            "timestamp": _now(),
            "registered_providers": registered,
            "initialized_providers": with_keys_snapshot,
            "models": detailed_models,
        }

        out = Path("logs") / "provider_registry_snapshot.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

        logger.debug("Provider registry snapshot written to %s", out)
    except Exception as e:
        logger.debug("Provider snapshot write skipped: %s", e)


def log_provider_priority(has_native_apis: bool, has_custom: bool, has_openrouter: bool):
    """
    Log provider priority information.
    
    Args:
        has_native_apis: Whether native APIs (Kimi, GLM) are available
        has_custom: Whether custom provider is available
        has_openrouter: Whether OpenRouter is available
    """
    priority_info = []
    
    if has_native_apis:
        priority_info.append("Native APIs (Kimi, GLM)")
    if has_custom:
        priority_info.append("Custom endpoints")
    if has_openrouter:
        priority_info.append("OpenRouter (catch-all)")
    
    if len(priority_info) > 1:
        logger.info(f"Provider priority: {' → '.join(priority_info)}")

