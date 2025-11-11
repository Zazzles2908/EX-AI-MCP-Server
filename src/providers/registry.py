"""Minimal provider registry after 98% reduction."""

from typing import Any, Dict, Optional


class ModelProviderRegistry:
    """Minimal provider registry."""

    def __init__(self):
        self.providers = {}
        self._register_default_providers()

    def _register_default_providers(self):
        """Register default providers."""
        from .glm_provider import GLMProvider
        from .kimi import KimiProvider

        self.providers["GLM"] = GLMProvider()
        self.providers["KIMI"] = KimiProvider()

    def get_provider(self, name: str) -> Optional[Any]:
        """Get provider by name."""
        return self.providers.get(name)

    def get_provider_for_model(self, model: str) -> Optional[Any]:
        """Get provider for model."""
        model_lower = model.lower()
        if "glm" in model_lower:
            return self.providers.get("GLM")
        elif "kimi" in model_lower or "moonshot" in model_lower:
            return self.providers.get("KIMI")
        return self.providers.get("GLM")

    def get_available_models(self) -> Dict[str, str]:
        """Get mapping of available models to provider names."""
        models = {}
        for provider_name, provider in self.providers.items():
            try:
                if hasattr(provider, 'list_models'):
                    for model in provider.list_models():
                        models[model] = provider_name
            except Exception:
                # Skip providers that don't have list_models
                pass
        return models

    @classmethod
    def call_with_fallback(cls, category, call_fn, hints=None):
        """Execute call_fn with fallback logic."""
        # Get the global registry instance
        registry = get_registry()
        # Define fallback models to try in order
        fallback_models = ["glm-4.5-flash", "moonshot-v1-8k"]
        last_error = None

        for model_name in fallback_models:
            try:
                # Check if this model is available
                provider = registry.get_provider_for_model(model_name)
                if provider:
                    result = call_fn(model_name)
                    return result
            except Exception as e:
                last_error = e
                continue

        # If all providers failed, raise the last error
        if last_error:
            raise last_error


# Global registry instance
_registry = None


def get_registry() -> ModelProviderRegistry:
    """Get global registry instance."""
    global _registry
    if _registry is None:
        _registry = ModelProviderRegistry()
    return _registry
