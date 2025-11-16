"""
Provider Registry Core Functionality

This module provides the core ModelProviderRegistry class for managing model providers.
It handles provider registration, initialization, model discovery, and telemetry.

Key Components:
- ModelProviderRegistry class (singleton)
- Provider registration and initialization
- Model discovery and availability checking
- Telemetry recording and retrieval
- Helper methods for specific providers (Kimi, GLM)

For model selection and fallback logic, see src/router/hybrid_router.py
For configuration and health monitoring, see registry_config.py
"""

import logging
import os
import threading
from typing import Any, Optional, TYPE_CHECKING

from src.providers.base import ModelProvider, ProviderType
from src.providers.registry_config import (
    HealthWrappedProvider,
    _cb_enabled,
    _get_health_manager,
    _health_enabled,
)

if TYPE_CHECKING:
    from tools.models import ToolModelCategory

from utils.infrastructure.health import CircuitState


# ================================================================================
# Model Provider Registry (Core)
# ================================================================================


class ModelProviderRegistry:
    """
    Registry for managing model providers.

    REFACTORED: Removed singleton pattern - now uses dependency injection
    for better testability and maintainability.

    This class manages provider registration, initialization, and model discovery.
    It provides the core infrastructure for the provider system.
    """

    def __init__(self):
        """Initialize ModelProviderRegistry."""
        # In-memory telemetry (lightweight). Structure:
        # telemetry = {
        #   "model_name": {"success": int, "failure": int, "latency_ms": [..], "input_tokens": int, "output_tokens": int}
        # }
        self._telemetry: dict[str, dict[str, Any]] = {}
        self._telemetry_lock = threading.RLock()

        # PHASE 2 FIX (2025-11-01): Cache for get_available_models to prevent redundant calls
        # EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce
        self._models_cache: Optional[dict[str, ProviderType]] = None
        self._models_cache_timestamp: Optional[float] = None
        self._models_cache_ttl: int = int(os.getenv("REGISTRY_CACHE_TTL", "300"))  # 5 minutes default, env override
        self._models_cache_lock = threading.RLock()

        # Instance dictionaries
        self._providers: dict[str, ModelProvider] = {}
        self._initialized_providers: dict[str, bool] = {}

        # Provider priority order for model selection
        # Native APIs first (prioritize Kimi/GLM per project usage), then custom endpoints, then catch-all providers
        self.PROVIDER_PRIORITY_ORDER = [
            ProviderType.KIMI,  # Direct Kimi/Moonshot access (preferred)
            ProviderType.GLM,  # Direct GLM/Z.ai access (preferred)
            ProviderType.CUSTOM,  # Local/self-hosted models
            ProviderType.OPENROUTER,  # Catch-all for cloud models (optional)
        ]

    # ================================================================================
    # Provider Management
    # ================================================================================

    
    def _invalidate_models_cache(self) -> None:
        """
        Invalidate the models cache.
        Called when providers are registered/deregistered.

        PHASE 2 FIX (2025-11-01): Cache invalidation for get_available_models
        """
        with self._models_cache_lock:
            self._models_cache = None
            self._models_cache_timestamp = None
            logging.debug("REGISTRY_CACHE: Models cache invalidated")

    
    def register_provider(self, provider_type: ProviderType, provider_class: type[ModelProvider]) -> None:
        """
        Register a new provider class.

        Args:
            provider_type: Type of the provider (e.g., ProviderType.GOOGLE)
            provider_class: Class that implements ModelProvider interface
        """
                # Instance already available as self
        self._providers[provider_type] = provider_class
        logging.debug(f"Registered provider {provider_type.name} (total: {len(self._providers)})")
        # PHASE 2 FIX: Invalidate cache when provider registered
        self._invalidate_models_cache()

    
    def get_provider(self, provider_type: ProviderType, force_new: bool = False) -> Optional[ModelProvider]:
        """
        Get an initialized provider instance.

        Args:
            provider_type: Type of provider to get
            force_new: Force creation of new instance instead of using cached

        Returns:
            Initialized ModelProvider instance or None if not available
        """
                # Instance already available as self

        # Enforce allowlist if configured (security hardening)
        allowed = os.getenv("ALLOWED_PROVIDERS", "").strip()
        if allowed:
            allow = {p.strip().upper() for p in allowed.split(",") if p.strip()}
            if provider_type.name not in allow:
                logging.debug("Provider %s skipped by ALLOWED_PROVIDERS", provider_type.name)
                return None

        # Return cached instance if available and not forcing new
        if not force_new and provider_type in self._initialized_providers:
            return self._initialized_providers[provider_type]

        # Check if provider class is registered
        if provider_type not in self._providers:
            return None

        # Get API key from environment
        api_key = self._get_api_key_for_provider(provider_type)

        # Get provider class or factory function
        provider_class = self._providers[provider_type]

        # Defensive: transient init protection
        try:
            # For custom providers, handle special initialization requirements
            if provider_type == ProviderType.CUSTOM:
                # Check if it's a factory function (callable but not a class)
                if callable(provider_class) and not isinstance(provider_class, type):
                    # Factory function - call it with api_key parameter
                    provider = provider_class(api_key=api_key)
                else:
                    # Regular class - need to handle URL requirement
                    custom_url = os.getenv("CUSTOM_API_URL", "")
                    if not custom_url:
                        if api_key:  # Key is set but URL is missing
                            logging.warning(
                                "CUSTOM_API_KEY set but CUSTOM_API_URL missing – skipping Custom provider"
                            )
                        return None
                    # Use empty string as API key for custom providers that don't need auth (e.g., Ollama)
                    # This allows the provider to be created even without CUSTOM_API_KEY being set
                    api_key = api_key or ""
                    # Initialize custom provider with both API key and base URL
                    provider = provider_class(api_key=api_key, base_url=custom_url)
            else:
                if not api_key:
                    return None
                # Initialize non-custom provider with API key and optional base_url from env for specific providers
                if provider_type in (ProviderType.KIMI, ProviderType.GLM, ProviderType.MINIMAX):
                    # Support canonical and vendor-specific environment variable names
                    # KIMI: prefer KIMI_API_URL, fallback to MOONSHOT_API_URL
                    # GLM:  prefer ZAI_API_KEY,  fallback to GLM_API_KEY
                    # MINIMAX: use MINIMAX_M2_KEY
                    if provider_type == ProviderType.KIMI:
                        base_url = os.getenv("KIMI_API_URL") or os.getenv("MOONSHOT_API_URL")
                    elif provider_type == ProviderType.GLM:
                        base_url = os.getenv("GLM_API_URL") or os.getenv("ZAI_BASE_URL")
                    else:  # MINIMAX
                        base_url = os.getenv("MINIMAX_API_URL") or "https://api.minimax.io/anthropic"
                    if base_url:
                        provider = provider_class(api_key=api_key, base_url=base_url)
                    else:
                        provider = provider_class(api_key=api_key)
                else:
                    provider = provider_class(api_key=api_key)
        except Exception as e:
            # Failed to create provider (transient or misconfig). Do not raise here.
            logging.warning("Provider %s initialization failed: %s", provider_type, e)
            return None

        # Wrap with health if enabled
        if _health_enabled():
            provider = HealthWrappedProvider(provider)

        # Cache the instance
        self._initialized_providers[provider_type] = provider

        return provider

    
    def get_provider_for_model(self, model_name: str) -> Optional[ModelProvider]:
        """
        Get provider instance for a specific model name.

        Provider priority order:
        1. Native APIs (KIMI, GLM) - Most direct and efficient
        2. CUSTOM - For local/private models with specific endpoints
        3. OPENROUTER - Catch-all for cloud models via unified API

        Args:
            model_name: Name of the model (e.g., "gemini-2.5-flash", "gpt5")

        Returns:
            ModelProvider instance that supports this model
        """
        logging.debug(f"REGISTRY_DEBUG: get_provider_for_model called with model_name='{model_name}'")

        # Check providers in priority order
        # Instance already available as self
        logging.debug(f"REGISTRY_DEBUG: Registry instance: {self}, _providers={self._providers}")
        logging.debug(f"REGISTRY_DEBUG: PROVIDER_PRIORITY_ORDER: {self.PROVIDER_PRIORITY_ORDER}")

        for provider_type in self.PROVIDER_PRIORITY_ORDER:
            logging.debug(f"REGISTRY_DEBUG: Checking provider_type {provider_type}")
            if provider_type in self._providers:
                logging.debug(f"REGISTRY_DEBUG: Found {provider_type} in registry")

                # Health gating: skip if circuit is OPEN (only when enabled and not log-only)
                if _health_enabled() and _cb_enabled():
                    health = _get_health_manager().get(provider_type.value)
                    if health.breaker.state == CircuitState.OPEN:
                        logging.warning("Skipping provider %s due to OPEN circuit", provider_type)
                        continue

                # Get or create provider instance
                provider = self.get_provider(provider_type)
                logging.debug(f"REGISTRY_DEBUG: Got provider instance: {provider}")
                if provider:
                    validates = provider.validate_model_name(model_name)
                    logging.debug(f"REGISTRY_DEBUG: Provider {provider_type} validate_model_name('{model_name}') = {validates}")
                    if validates:
                        logging.debug(f"REGISTRY_DEBUG: Returning provider {provider_type} for model {model_name}")
                        return provider
                else:
                    logging.debug(f"REGISTRY_DEBUG: get_provider returned None for {provider_type}")
            else:
                logging.debug(f"REGISTRY_DEBUG: {provider_type} not found in registry")

        logging.debug(f"REGISTRY_DEBUG: No provider found for model {model_name}")
        return None

    @staticmethod
    def _get_api_key_for_provider(provider_type: ProviderType) -> Optional[str]:
        """
        Get API key for provider from environment variables.

        Args:
            provider_type: Type of provider

        Returns:
            API key string or None if not found
        """
        # Map provider types to their environment variable names
        key_map = {
            ProviderType.KIMI: ["KIMI_API_KEY", "MOONSHOT_API_KEY"],
            ProviderType.GLM: ["ZAI_API_KEY", "GLM_API_KEY"],
            ProviderType.MINIMAX: ["MINIMAX_M2_KEY", "MINIMAX_API_KEY"],
            ProviderType.CUSTOM: ["CUSTOM_API_KEY"],
            ProviderType.OPENROUTER: ["OPENROUTER_API_KEY"],
        }

        # Get possible key names for this provider
        key_names = key_map.get(provider_type, [])

        # Try each key name in order
        for key_name in key_names:
            api_key = os.getenv(key_name)
            if api_key:
                return api_key

        return None

    # ================================================================================
    # Model Discovery
    # ================================================================================

    
    def get_available_providers(self) -> list[ProviderType]:
        """Get list of registered provider types."""
                # Use self for instance data
        providers = list(self._providers.keys())
        allowed = os.getenv("ALLOWED_PROVIDERS", "").strip()
        if allowed:
            allow = {p.strip().upper() for p in allowed.split(",") if p.strip()}
            providers = [p for p in providers if p.name in allow]
        return providers

    
    def get_available_models(self, respect_restrictions: bool = True) -> dict[str, ProviderType]:
        """
        Get mapping of all available models to their providers.

        PHASE 2 FIX (2025-11-01): Implements caching with TTL to prevent redundant calls
        EXAI Consultation: 63c00b70-364b-4351-bf6c-5a105e553dce

        Args:
            respect_restrictions: If True, filter out models not allowed by restrictions

        Returns:
            Dict mapping model names to provider types
        """
        import time

        # PHASE 2 FIX: Check cache first
        with self._models_cache_lock:
            if self._models_cache is not None and self._models_cache_timestamp is not None:
                cache_age = time.time() - self._models_cache_timestamp
                if cache_age < self._models_cache_ttl:
                    logging.debug(f"REGISTRY_CACHE: Returning cached models (age={cache_age:.1f}s, ttl={self._models_cache_ttl}s)")
                    return self._models_cache.copy()
                else:
                    logging.debug(f"REGISTRY_CACHE: Cache expired (age={cache_age:.1f}s, ttl={self._models_cache_ttl}s)")

        # Import here to avoid circular imports
        from utils.model.restrictions import get_restriction_service
        import inspect
        import traceback

        restriction_service = get_restriction_service() if respect_restrictions else None
        models: dict[str, ProviderType] = {}

        # CRITICAL DEBUG (2025-10-24): Log registry state and caller info
        caller_frame = inspect.stack()[1]
        caller_info = f"{caller_frame.filename}:{caller_frame.lineno} in {caller_frame.function}"
        logging.debug(f"REGISTRY_DEBUG: get_available_models called from {caller_info}")
        logging.debug(f"REGISTRY_DEBUG: registry id={id(self)}, _providers={self._providers}")
        logging.debug(f"REGISTRY_CACHE: Cache miss - fetching models from providers")

        for provider_type in self._providers:
            logging.debug(f"REGISTRY_DEBUG: Processing provider {provider_type.name}")
            provider = self.get_provider(provider_type)
            if not provider:
                logging.debug(f"REGISTRY_DEBUG: get_provider returned None for {provider_type.name}")
                continue

            logging.debug(f"REGISTRY_DEBUG: Got provider instance for {provider_type.name}: {provider}")

            try:
                available = provider.list_models(respect_restrictions=respect_restrictions)
                logging.debug(f"REGISTRY_DEBUG: Provider {provider_type.name} returned {len(available)} models: {available}")
            except NotImplementedError:
                logging.warning("Provider %s does not implement list_models", provider_type)
                continue
            except Exception as e:
                logging.error(f"REGISTRY_DEBUG: Provider {provider_type.name} list_models() failed: {e}", exc_info=True)
                continue

            for model_name in available:
                # =====================================================================================
                # CRITICAL: Prevent double restriction filtering (Fixed Issue #98)
                # =====================================================================================
                # Previously, both the provider AND registry applied restrictions, causing
                # double-filtering that resulted in "no models available" errors.
                #
                # Logic: If respect_restrictions=True, provider already filtered models,
                # so registry should NOT filter them again.
                # TEST COVERAGE: tests/test_provider_routing_bugs.py::TestOpenRouterAliasRestrictions
                # =====================================================================================
                logging.debug(f"REGISTRY_DEBUG: Checking model {model_name}, restriction_service={restriction_service}, respect_restrictions={respect_restrictions}")
                if (
                    restriction_service
                    and not respect_restrictions  # Only filter if provider didn't already filter
                    and not restriction_service.is_allowed(provider_type, model_name)
                ):
                    logging.debug(f"REGISTRY_DEBUG: Model {model_name} filtered by restrictions")
                    continue
                logging.debug(f"REGISTRY_DEBUG: Adding model {model_name} to registry")
                models[model_name] = provider_type

        # PHASE 2 FIX: Update cache with fresh data
        with self._models_cache_lock:
            self._models_cache = models.copy()
            self._models_cache_timestamp = time.time()
            logging.debug(f"REGISTRY_CACHE: Cache updated with {len(models)} models")

        logging.debug(f"REGISTRY_DEBUG: Returning {len(models)} models: {list(models.keys())}")
        return models

    @classmethod
    def get_available_models_static(cls, respect_restrictions: bool = True) -> dict[str, ProviderType]:
        """
        Get mapping of all available models to their providers.

        DEPRECATED: Use instance method instead.
        Use: registry = ModelProviderRegistry(); registry.get_available_models()

        Args:
            respect_restrictions: If True, filter out models not allowed by restrictions

        Returns:
            Dict mapping model names to provider types
        """
        registry = cls()
        return registry.get_available_models(respect_restrictions=respect_restrictions)

    def get_available_model_names(self, provider_type: Optional[ProviderType] = None) -> list[str]:
        """
        Get list of available model names, optionally filtered by provider.

        This respects model restrictions automatically.

        Args:
            provider_type: Optional provider to filter by

        Returns:
            List of available model names
        """
        available_models = self.get_available_models(respect_restrictions=True)

        if provider_type:
            # Filter by specific provider
            return [name for name, ptype in available_models.items() if ptype == provider_type]
        else:
            # Return all available models
            return list(available_models.keys())

    
    def list_available_models(self, provider_type: Optional[ProviderType] = None) -> list[str]:
        """
        Alias maintained for backward compatibility with server.py.
        Returns list of available model names, optionally filtered by provider.
        """
        return self.get_available_model_names(provider_type=provider_type)

    def is_provider_available(self, provider_type: ProviderType) -> bool:
        """
        Check if provider is available (registered and initialized).

        Args:
            provider_type: Provider to check

        Returns:
            True if provider is available and initialized
        """
        return (provider_type in self._providers and
                provider_type in self._initialized_providers and
                self._initialized_providers[provider_type] is not None)

    def get_debug_info(self) -> dict[str, Any]:
        """
        Get debug information about the registry state.

        Returns:
            Dict with debug information
        """
        with self._models_cache_lock:
            return {
                "providers_registered": list(self._providers.keys()),
                "providers_initialized": list(self._initialized_providers.keys()),
                "cache_valid": self._models_cache is not None,
                "singleton_id": id(self),
                "_providers_count": len(self._providers),
                "_initialized_count": len(self._initialized_providers),
                "models_cache_size": len(self._models_cache) if self._models_cache else 0
            }

    def get_available_providers_with_keys(self) -> list[ProviderType]:
        """
        Return providers that can be initialized with current env keys.
        Used by server diagnostics. Does not throw on init errors.
        """
                # Use self for instance data
        result: list[ProviderType] = []
        for ptype in list(self._providers.keys()):
            try:
                if self.get_provider(ptype) is not None:
                    result.append(ptype)
            except Exception:
                # Be permissive for diagnostics
                continue
        return result

    # ================================================================================
    # Helper Methods
    # ================================================================================

    
    def get_kimi_provider(self) -> Optional[ModelProvider]:
        """
        Helper to get Kimi provider with graceful fallback to GLM if configured.

        Fallback sequence:
        1) KIMI (if initialized)
        2) If Kimi unavailable, return None here; routing code should fallback to GLM/DEFAULT_MODEL
        """
        kimi_provider = self.get_provider(ProviderType.KIMI)
        if kimi_provider:
            return kimi_provider
        return None

    
    def get_glm_provider(self) -> Optional[ModelProvider]:
        """Helper to get GLM provider."""
        return self.get_provider(ProviderType.GLM)

    def get_minimax_provider(self) -> Optional[ModelProvider]:
        """Helper to get MiniMax provider."""
        return self.get_provider(ProviderType.MINIMAX)

    # ================================================================================
    # Telemetry
    # ================================================================================


    @classmethod
    def record_telemetry(
        cls,
        model_name: str,
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float | None = None,
    ) -> None:
        """Record telemetry for a model call."""
        # Get the singleton registry instance
        instance = get_registry_instance()
        with instance._telemetry_lock:
            rec = instance._telemetry.setdefault(
                model_name,
                {"success": 0, "failure": 0, "latency_ms": [], "input_tokens": 0, "output_tokens": 0},
            )
            if success:
                rec["success"] += 1
            else:
                rec["failure"] += 1
            rec["input_tokens"] += max(0, input_tokens)
            rec["output_tokens"] += max(0, output_tokens)
            if latency_ms is not None:
                rec["latency_ms"].append(float(latency_ms))
        # Best-effort JSONL observability for token usage
        try:
            from utils.observability import record_token_usage

            provider = "unknown"
            try:
                prov = instance.get_provider_for_model(model_name)
                if prov:
                    ptype = prov.get_provider_type()
                    provider = getattr(ptype, "value", getattr(ptype, "name", "unknown"))
            except Exception:
                provider = "unknown"
            if input_tokens or output_tokens:
                record_token_usage(str(provider), model_name, int(input_tokens), int(output_tokens))
        except Exception:
            pass

    
    def get_telemetry(self) -> dict[str, Any]:
        """Return a copy of telemetry data."""
        with self._telemetry_lock:
            # Shallow copy is sufficient for reporting
            return {k: dict(v) for k, v in self._telemetry.items()}

    
    def clear_telemetry(self) -> None:
        """Clear all telemetry data."""
        with self._telemetry_lock:
            self._telemetry.clear()

    # ================================================================================
    # Model Selection and Fallback
    # ================================================================================
    # DELEGATED TO HYBRID ROUTER (see src/router/hybrid_router.py)
    # - Uses MiniMax M2 for intelligent routing when available
    # - Falls back to RouterService for reliability
    # This replaces the old registry_selection.py module


# DEPRECATED: Singleton pattern removed
# Use: registry = ModelProviderRegistry() instead of class methods


# DEPRECATED: All backward compatibility functions removed
# The singleton pattern has been completely removed from this module
# 
# MIGRATION GUIDE:
# Old: ModelProviderRegistry.get_available_models()
# New: registry = ModelProviderRegistry()
#      models = registry.get_available_models()
#
# Old: get_registry_instance()
# New: registry = ModelProviderRegistry()
#
# All registry operations now require creating an instance first

# ================================================================================
# SINGLETON REGISTRY INSTANCE
# ================================================================================
# PHASE 5 FIX (2025-11-07): Restore singleton pattern to fix provider registration
# Registry instance that persists across all calls within the same process

_registry_instance: Optional[ModelProviderRegistry] = None


def get_registry_instance() -> ModelProviderRegistry:
    """
    Get the singleton ModelProviderRegistry instance.

    FIXED: Now returns the same instance every time within a process.
    This restores the singleton pattern that was removed in Phase 2 but is
    needed for provider registration to work correctly.

    Returns:
        ModelProviderRegistry: The singleton registry instance
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModelProviderRegistry()
    return _registry_instance


# ================================================================================
# BACKWARD COMPATIBILITY LAYER
# ================================================================================
# These wrapper functions maintain backward compatibility for code that was
# calling static methods on ModelProviderRegistry before the singleton removal.

def _get_available_models(respect_restrictions: bool = True) -> dict[str, ProviderType]:
    """
    Get mapping of all available models to their providers.

    DEPRECATED: This creates a new instance each time.
    Use ModelProviderRegistry().get_available_models() instead.

    Args:
        respect_restrictions: If True, filter out models not allowed by restrictions

    Returns:
        Dict mapping model names to provider types
    """
    registry = get_registry_instance()
    return registry.get_available_models(respect_restrictions=respect_restrictions)


# ================================================================================
# MODULE-LEVEL WRAPPER FUNCTIONS FOR BACKWARD COMPATIBILITY
# ================================================================================
# These functions maintain backward compatibility by delegating to a new
# ModelProviderRegistry instance. This avoids needing to modify all calling code.

def get_provider(provider_type: ProviderType, force_new: bool = False):
    """
    Get an initialized provider instance.

    DEPRECATED: Creates a new instance each time.
    Use: registry = ModelProviderRegistry(); registry.get_provider(provider_type)

    Args:
        provider_type: Type of provider to get
        force_new: Force creation of new instance instead of using cached

    Returns:
        Initialized ModelProvider instance or None if not available
    """
    registry = get_registry_instance()
    return registry.get_provider(provider_type, force_new=force_new)


def get_available_providers_with_keys() -> list[ProviderType]:
    """
    Get list of provider types that have API keys configured.

    DEPRECATED: Creates a new instance each time.
    Use: registry = ModelProviderRegistry(); registry.get_available_providers_with_keys()

    Returns:
        List of provider types with available API keys
    """
    registry = get_registry_instance()
    return registry.get_available_providers_with_keys()


def get_available_model_names(provider_type: Optional[ProviderType] = None) -> list[str]:
    """
    Get list of available model names, optionally filtered by provider.

    DEPRECATED: Creates a new instance each time.
    Use: registry = ModelProviderRegistry(); registry.get_available_model_names()

    Args:
        provider_type: Optional provider to filter by

    Returns:
        List of available model names
    """
    registry = get_registry_instance()
    return registry.get_available_model_names(provider_type=provider_type)


