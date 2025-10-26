"""
Provider Registration Module

Handles registration of detected providers with the ModelProviderRegistry.
Manages priority-based registration and factory functions.

Thread Safety:
- WEEK 1 FIX #5 (2025-10-21): Added thread safety for provider registration
- Uses double-checked locking pattern to prevent duplicate registration
- Safe for concurrent access after module initialization
"""

import logging
import os
import threading
from typing import Any, Callable

logger = logging.getLogger(__name__)

# WEEK 1 FIX #5 (2025-10-21): Thread safety for provider registration
# Double-checked locking pattern: fast path without lock, slow path with lock + double-check
_registration_lock = threading.Lock()
_registration_complete = False


def create_custom_provider_factory(custom_class: Any) -> Callable:
    """
    Create factory function for custom provider.
    
    Args:
        custom_class: Custom provider class
        
    Returns:
        Factory function that creates CustomProvider instances
    """
    def custom_provider_factory(api_key=None):
        """Factory function that creates CustomProvider with proper parameters."""
        # api_key is CUSTOM_API_KEY (can be empty for Ollama), base_url from CUSTOM_API_URL
        base_url = os.getenv("CUSTOM_API_URL", "")
        return custom_class(api_key=api_key or "", base_url=base_url)
    
    return custom_provider_factory


def register_providers(provider_config: dict) -> list[str]:
    """
    Register all detected providers with ModelProviderRegistry.

    Thread-safe with double-checked locking pattern.
    Prevents duplicate registration when called concurrently.

    Providers are registered in priority order:
    1. Native APIs (Kimi, GLM) - most direct and efficient
    2. Custom provider - for local/private models
    3. OpenRouter - catch-all for everything else

    Args:
        provider_config: Provider configuration dict from detect_all_providers()

    Returns:
        List of registered provider names
    """
    global _registration_complete

    # WEEK 1 FIX #5 (2025-10-21): Fast path - no lock needed if already registered
    if _registration_complete:
        logger.debug("Provider registration already complete, skipping")
        # Return empty list since we don't cache the registered list
        # (caller can query ModelProviderRegistry directly if needed)
        return []

    # WEEK 1 FIX #5 (2025-10-21): Slow path - acquire lock and double-check
    with _registration_lock:
        # Double-check inside lock (another thread may have registered while we waited)
        if _registration_complete:
            logger.debug("Provider registration already complete (confirmed in lock), skipping")
            return []

        logger.debug("Performing first-time provider registration")

        from src.providers.registry import ModelProviderRegistry
        from src.providers.base import ProviderType

        registered = []
        disabled_providers = provider_config['disabled_providers']

        # 1. Register native APIs first (most direct and efficient)
        if provider_config['has_native_apis']:
            # Register Kimi
            if provider_config['kimi']['available'] and "KIMI" not in disabled_providers:
                kimi_class = provider_config['kimi']['class']
                ModelProviderRegistry.register_provider(ProviderType.KIMI, kimi_class)
                registered.append("Kimi")
                logger.debug("Registered Kimi provider")

            # Register GLM
            if provider_config['glm']['available'] and "GLM" not in disabled_providers:
                glm_class = provider_config['glm']['class']
                ModelProviderRegistry.register_provider(ProviderType.GLM, glm_class)
                registered.append("GLM")
                logger.debug("Registered GLM provider")

        # 2. Register custom provider second (for local/private models)
        if provider_config['has_custom'] and "CUSTOM" not in disabled_providers:
            custom_class = provider_config['custom']['class']
            factory = create_custom_provider_factory(custom_class)
            ModelProviderRegistry.register_provider(ProviderType.CUSTOM, factory)
            registered.append("Custom")
            logger.debug("Registered Custom provider")

        # 3. Register OpenRouter last (catch-all for everything else)
        if provider_config['has_openrouter'] and "OPENROUTER" not in disabled_providers:
            # Note: OpenRouterProvider is not imported in detection module
            # We need to import it here if needed
            try:
                from src.providers.openrouter import OpenRouterProvider
                ModelProviderRegistry.register_provider(ProviderType.OPENROUTER, OpenRouterProvider)
                registered.append("OpenRouter")
                logger.debug("Registered OpenRouter provider")
            except ImportError as e:
                logger.warning(f"OpenRouter provider import failed: {e}")
            except (AttributeError, TypeError) as e:
                logger.warning(f"OpenRouter provider registration failed: {e}")

        _registration_complete = True
        logger.debug("Provider registration complete")

        return registered

