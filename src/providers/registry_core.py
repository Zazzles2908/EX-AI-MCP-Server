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

For model selection and fallback logic, see registry_selection.py
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

    This is a singleton class that manages provider registration, initialization,
    and model discovery. It provides the core infrastructure for the provider system.
    """

    _instance = None
    # In-memory telemetry (lightweight). Structure:
    # telemetry = {
    #   "model_name": {"success": int, "failure": int, "latency_ms": [..], "input_tokens": int, "output_tokens": int}
    # }
    _telemetry: dict[str, dict[str, Any]] = {}
    _telemetry_lock = threading.RLock()

    # Provider priority order for model selection
    # Native APIs first (prioritize Kimi/GLM per project usage), then custom endpoints, then catch-all providers
    PROVIDER_PRIORITY_ORDER = [
        ProviderType.KIMI,  # Direct Kimi/Moonshot access (preferred)
        ProviderType.GLM,  # Direct GLM/ZhipuAI access (preferred)
        ProviderType.CUSTOM,  # Local/self-hosted models
        ProviderType.OPENROUTER,  # Catch-all for cloud models (optional)
    ]

    def __new__(cls):
        """Singleton pattern for registry."""
        if cls._instance is None:
            logging.debug("REGISTRY: Creating new registry instance")
            cls._instance = super().__new__(cls)
            # Initialize instance dictionaries on first creation
            cls._instance._providers = {}
            cls._instance._initialized_providers = {}
            logging.debug(f"REGISTRY: Created instance {cls._instance}")
        return cls._instance

    # ================================================================================
    # Provider Management
    # ================================================================================

    @classmethod
    def register_provider(cls, provider_type: ProviderType, provider_class: type[ModelProvider]) -> None:
        """
        Register a new provider class.

        Args:
            provider_type: Type of the provider (e.g., ProviderType.GOOGLE)
            provider_class: Class that implements ModelProvider interface
        """
        instance = cls()
        instance._providers[provider_type] = provider_class

    @classmethod
    def get_provider(cls, provider_type: ProviderType, force_new: bool = False) -> Optional[ModelProvider]:
        """
        Get an initialized provider instance.

        Args:
            provider_type: Type of provider to get
            force_new: Force creation of new instance instead of using cached

        Returns:
            Initialized ModelProvider instance or None if not available
        """
        instance = cls()

        # Enforce allowlist if configured (security hardening)
        allowed = os.getenv("ALLOWED_PROVIDERS", "").strip()
        if allowed:
            allow = {p.strip().upper() for p in allowed.split(",") if p.strip()}
            if provider_type.name not in allow:
                logging.debug("Provider %s skipped by ALLOWED_PROVIDERS", provider_type.name)
                return None

        # Return cached instance if available and not forcing new
        if not force_new and provider_type in instance._initialized_providers:
            return instance._initialized_providers[provider_type]

        # Check if provider class is registered
        if provider_type not in instance._providers:
            return None

        # Get API key from environment
        api_key = cls._get_api_key_for_provider(provider_type)

        # Get provider class or factory function
        provider_class = instance._providers[provider_type]

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
                if provider_type in (ProviderType.KIMI, ProviderType.GLM):
                    # Support canonical and vendor-specific environment variable names
                    # KIMI: prefer KIMI_API_URL, fallback to MOONSHOT_API_URL
                    # GLM:  prefer GLM_API_URL,  fallback to ZHIPUAI_API_URL
                    if provider_type == ProviderType.KIMI:
                        base_url = os.getenv("KIMI_API_URL") or os.getenv("MOONSHOT_API_URL")
                    else:
                        base_url = os.getenv("GLM_API_URL") or os.getenv("ZHIPUAI_API_URL")
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
        instance._initialized_providers[provider_type] = provider

        return provider

    @classmethod
    def get_provider_for_model(cls, model_name: str) -> Optional[ModelProvider]:
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
        logging.debug(f"get_provider_for_model called with model_name='{model_name}'")

        # Check providers in priority order
        instance = cls()
        logging.debug(f"Registry instance: {instance}")
        logging.debug(f"Available providers in registry: {list(instance._providers.keys())}")

        for provider_type in cls.PROVIDER_PRIORITY_ORDER:
            if provider_type in instance._providers:
                logging.debug(f"Found {provider_type} in registry")

                # Health gating: skip if circuit is OPEN (only when enabled and not log-only)
                if _health_enabled() and _cb_enabled():
                    health = _get_health_manager().get(provider_type.value)
                    if health.breaker.state == CircuitState.OPEN:
                        logging.warning("Skipping provider %s due to OPEN circuit", provider_type)
                        continue

                # Get or create provider instance
                provider = cls.get_provider(provider_type)
                if provider and provider.validate_model_name(model_name):
                    logging.debug(f"{provider_type} validates model {model_name}")
                    return provider
                else:
                    logging.debug(f"{provider_type} does not validate model {model_name}")
            else:
                logging.debug(f"{provider_type} not found in registry")

        logging.debug(f"No provider found for model {model_name}")
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
            ProviderType.GLM: ["GLM_API_KEY", "ZHIPUAI_API_KEY"],
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

    @classmethod
    def get_available_providers(cls) -> list[ProviderType]:
        """Get list of registered provider types."""
        instance = cls()
        providers = list(instance._providers.keys())
        allowed = os.getenv("ALLOWED_PROVIDERS", "").strip()
        if allowed:
            allow = {p.strip().upper() for p in allowed.split(",") if p.strip()}
            providers = [p for p in providers if p.name in allow]
        return providers

    @classmethod
    def get_available_models(cls, respect_restrictions: bool = True) -> dict[str, ProviderType]:
        """
        Get mapping of all available models to their providers.

        Args:
            respect_restrictions: If True, filter out models not allowed by restrictions

        Returns:
            Dict mapping model names to provider types
        """
        # Import here to avoid circular imports
        from utils.model.restrictions import get_restriction_service

        restriction_service = get_restriction_service() if respect_restrictions else None
        models: dict[str, ProviderType] = {}
        instance = cls()

        for provider_type in instance._providers:
            provider = cls.get_provider(provider_type)
            if not provider:
                continue

            try:
                available = provider.list_models(respect_restrictions=respect_restrictions)
            except NotImplementedError:
                logging.warning("Provider %s does not implement list_models", provider_type)
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
                if (
                    restriction_service
                    and not respect_restrictions  # Only filter if provider didn't already filter
                    and not restriction_service.is_allowed(provider_type, model_name)
                ):
                    logging.debug("Model %s filtered by restrictions", model_name)
                    continue
                models[model_name] = provider_type

        return models

    @classmethod
    def get_available_model_names(cls, provider_type: Optional[ProviderType] = None) -> list[str]:
        """
        Get list of available model names, optionally filtered by provider.

        This respects model restrictions automatically.

        Args:
            provider_type: Optional provider to filter by

        Returns:
            List of available model names
        """
        available_models = cls.get_available_models(respect_restrictions=True)

        if provider_type:
            # Filter by specific provider
            return [name for name, ptype in available_models.items() if ptype == provider_type]
        else:
            # Return all available models
            return list(available_models.keys())

    @classmethod
    def list_available_models(cls, provider_type: Optional[ProviderType] = None) -> list[str]:
        """
        Alias maintained for backward compatibility with server.py.
        Returns list of available model names, optionally filtered by provider.
        """
        return cls.get_available_model_names(provider_type=provider_type)

    @classmethod
    def get_available_providers_with_keys(cls) -> list[ProviderType]:
        """
        Return providers that can be initialized with current env keys.
        Used by server diagnostics. Does not throw on init errors.
        """
        instance = cls()
        result: list[ProviderType] = []
        for ptype in list(instance._providers.keys()):
            try:
                if cls.get_provider(ptype) is not None:
                    result.append(ptype)
            except Exception:
                # Be permissive for diagnostics
                continue
        return result

    # ================================================================================
    # Helper Methods
    # ================================================================================

    @classmethod
    def get_kimi_provider(cls) -> Optional[ModelProvider]:
        """
        Helper to get Kimi provider with graceful fallback to GLM if configured.

        Fallback sequence:
        1) KIMI (if initialized)
        2) If Kimi unavailable, return None here; routing code should fallback to GLM/DEFAULT_MODEL
        """
        kimi_provider = cls.get_provider(ProviderType.KIMI)
        if kimi_provider:
            return kimi_provider
        return None

    @classmethod
    def get_glm_provider(cls) -> Optional[ModelProvider]:
        """Helper to get GLM provider."""
        return cls.get_provider(ProviderType.GLM)

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
        with cls._telemetry_lock:
            rec = cls._telemetry.setdefault(
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
                prov = cls.get_provider_for_model(model_name)
                if prov:
                    ptype = prov.get_provider_type()
                    provider = getattr(ptype, "value", getattr(ptype, "name", "unknown"))
            except Exception:
                provider = "unknown"
            if input_tokens or output_tokens:
                record_token_usage(str(provider), model_name, int(input_tokens), int(output_tokens))
        except Exception:
            pass

    @classmethod
    def get_telemetry(cls) -> dict[str, Any]:
        """Return a copy of telemetry data."""
        with cls._telemetry_lock:
            # Shallow copy is sufficient for reporting
            return {k: dict(v) for k, v in cls._telemetry.items()}

    @classmethod
    def clear_telemetry(cls) -> None:
        """Clear all telemetry data."""
        with cls._telemetry_lock:
            cls._telemetry.clear()

    # ================================================================================
    # Model Selection and Fallback (Delegated to registry_selection.py)
    # ================================================================================

    @classmethod
    def get_preferred_fallback_model(cls, tool_category: Optional["ToolModelCategory"] = None) -> str:
        """Select a reasonable fallback model across providers."""
        from src.providers.registry_selection import get_preferred_fallback_model

        return get_preferred_fallback_model(cls(), tool_category)

    @classmethod
    def get_best_provider_for_category(
        cls, category: "ToolModelCategory", allowed_models: list[str]
    ) -> Optional[tuple[ModelProvider, str]]:
        """Select best provider and model for a functional category."""
        from src.providers.registry_selection import get_best_provider_for_category

        return get_best_provider_for_category(cls(), category, allowed_models)

    @classmethod
    def _get_allowed_models_for_provider(cls, provider: ModelProvider, provider_type: ProviderType) -> list[str]:
        """Return canonical model names supported by a provider after restriction filtering."""
        from src.providers.registry_selection import _get_allowed_models_for_provider

        return _get_allowed_models_for_provider(provider, provider_type)

    @classmethod
    def _auggie_fallback_chain(
        cls,
        category: Optional["ToolModelCategory"],
        hints: Optional[list[str]] = None,
    ) -> list[str]:
        """Return a prioritized list of candidate models for a category."""
        from src.providers.registry_selection import _auggie_fallback_chain

        return _auggie_fallback_chain(cls(), category, hints)

    @classmethod
    def call_with_fallback(
        cls,
        category: Optional["ToolModelCategory"],
        call_fn,
        hints: Optional[list[str]] = None,
    ):
        """Execute call_fn(model_name) over a category-aware fallback chain."""
        from src.providers.registry_selection import call_with_fallback

        return call_with_fallback(cls(), category, call_fn, hints)

