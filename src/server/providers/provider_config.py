"""
Provider Configuration Module

Thin orchestrator that delegates to specialized helper modules.
Handles configuration and initialization of AI model providers.
"""

import logging
import atexit

logger = logging.getLogger(__name__)

# Import helper modules
from .provider_detection import detect_all_providers
from .provider_registration import register_providers
from .provider_diagnostics import log_provider_summary, write_provider_snapshot, log_provider_priority
from .provider_restrictions import validate_model_restrictions, validate_auto_mode


def configure_providers() -> None:
    """
    Configure and validate AI providers based on available API keys.

    NOTE: This function is called by src/bootstrap/singletons.ensure_providers_configured()
    to ensure idempotent provider initialization across both entry points (server.py, ws_server.py).

    Thin orchestrator that delegates to helper modules:
    1. Detect available providers
    2. Validate at least one provider exists
    3. Register providers with registry
    4. Log diagnostics and write snapshot
    5. Validate model restrictions
    6. Register cleanup function

    Raises:
        ValueError: If no valid API keys are found or conflicting configurations detected
    """
    # Step 1: Detect all available providers
    provider_config = detect_all_providers()
    
    # Step 2: Validate at least one provider exists
    if not provider_config['valid_providers']:
        raise ValueError(
            "At least one API configuration is required. Please set either:\n"
            "- KIMI_API_KEY for Moonshot Kimi models\n"
            "- GLM_API_KEY for ZhipuAI GLM models\n"
            "- OPENROUTER_API_KEY for OpenRouter (multiple models)\n"
            "- CUSTOM_API_URL for local models (Ollama, vLLM, etc.)"
        )
    
    # Step 3: Register providers with registry
    registered = register_providers(provider_config)
    
    # Step 4: Log diagnostics and write snapshot
    log_provider_summary(provider_config['valid_providers'])
    write_provider_snapshot()
    log_provider_priority(
        provider_config['has_native_apis'],
        provider_config['has_custom'],
        provider_config['has_openrouter']
    )
    
    # Step 5: Validate model restrictions
    validate_model_restrictions()
    validate_auto_mode()
    
    # Step 6: Register cleanup function for providers
    def cleanup_providers():
        """Clean up all registered providers on shutdown."""
        try:
            from src.providers.registry import ModelProviderRegistry
            from src.providers.registry_core import get_registry_instance
            registry = get_registry_instance()
            if hasattr(registry, "_initialized_providers"):
                for provider in list(registry._initialized_providers.items()):
                    try:
                        if provider and hasattr(provider, "close"):
                            provider.close()
                    except Exception:
                        # Logger might be closed during shutdown
                        pass
        except Exception:
            # Silently ignore any errors during cleanup
            pass
    
    atexit.register(cleanup_providers)


__all__ = ['configure_providers']
