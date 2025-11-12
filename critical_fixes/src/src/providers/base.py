"""
Provider Base Module
Base types and classes for EX-AI-MCP-Server provider system
"""

import os
import logging
from typing import Dict, Any, Optional, List, Protocol, Union
from dataclasses import dataclass
from enum import Enum
import asyncio

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Provider types supported by the system"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    ZERONODE = "zeronode"
    OPENROUTER = "openrouter"
    MINIMAX = "minimax"
    OLLAMA = "ollama"
    VLLM = "vllm"
    KIMI = "kimi"
    GLM = "glm"


@dataclass
class ModelResponse:
    """Response from a model provider"""
    content: str
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ModelProvider(Protocol):
    """Protocol for model provider implementations"""
    
    def get_provider_type(self) -> ProviderType:
        """Get the provider type"""
        ...
    
    def list_models(self, respect_restrictions: bool = True) -> List[str]:
        """List available models"""
        ...
    
    def generate_content(
        self,
        prompt: str,
        model_name: str,
        max_output_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> ModelResponse:
        """Generate content using specified model"""
        ...
    
    def get_preferred_model(self, category: Any, available_models: List[str]) -> Optional[str]:
        """Get preferred model for a given category"""
        ...


class BaseModelProvider:
    """Base implementation for model providers"""
    
    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type
        self._api_key = os.getenv(f"{provider_type.value.upper()}_API_KEY")
        self._base_url = os.getenv(f"{provider_type.value.upper()}_API_URL")
        self._enabled = bool(self._api_key)
        
    def get_provider_type(self) -> ProviderType:
        """Get the provider type"""
        return self.provider_type
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return self._enabled and bool(self._api_key)
    
    def list_models(self, respect_restrictions: bool = True) -> List[str]:
        """Override in subclasses to return available models"""
        return []
    
    def generate_content(
        self,
        prompt: str,
        model_name: str,
        max_output_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> ModelResponse:
        """Override in subclasses to implement content generation"""
        raise NotImplementedError("Subclasses must implement generate_content")
    
    def get_preferred_model(self, category: Any, available_models: List[str]) -> Optional[str]:
        """Override in subclasses to implement model selection"""
        return available_models[0] if available_models else None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.provider_type.value}, available={self.is_available()})"


class ProviderRegistry:
    """Registry for managing model providers"""
    
    def __init__(self):
        self._providers: Dict[ProviderType, BaseModelProvider] = {}
        self._registered_models: Dict[str, ProviderType] = {}
        
    def register_provider(self, provider: BaseModelProvider):
        """Register a provider"""
        ptype = provider.get_provider_type()
        self._providers[ptype] = provider
        
        # Register available models
        try:
            models = provider.list_models(respect_restrictions=True)
            for model in models:
                self._registered_models[model] = ptype
        except Exception as e:
            logger.warning(f"Failed to list models for {ptype}: {e}")
    
    def get_provider(self, provider_type: ProviderType) -> Optional[BaseModelProvider]:
        """Get a provider by type"""
        return self._providers.get(provider_type)
    
    def get_provider_for_model(self, model_name: str) -> Optional[BaseModelProvider]:
        """Get provider that supports a specific model"""
        provider_type = self._registered_models.get(model_name)
        if provider_type:
            return self._providers.get(provider_type)
        return None
    
    def get_available_models(self, respect_restrictions: bool = True) -> Dict[str, ProviderType]:
        """Get all available models and their providers"""
        result = {}
        for provider in self._providers.values():
            if provider.is_available():
                try:
                    models = provider.list_models(respect_restrictions=respect_restrictions)
                    for model in models:
                        result[model] = provider.get_provider_type()
                except Exception as e:
                    logger.warning(f"Failed to get models from {provider}: {e}")
        return result
    
    def get_available_providers(self) -> List[BaseModelProvider]:
        """Get all available providers"""
        return [p for p in self._providers.values() if p.is_available()]
    
    def record_telemetry(
        self,
        model_name: str,
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float = 0.0
    ):
        """Record usage telemetry for a model (override in subclasses)"""
        # Default implementation - override for detailed telemetry
        pass


# Global registry instance
_registry_instance: Optional[ProviderRegistry] = None


def get_registry_instance() -> ProviderRegistry:
    """Get the global registry instance (singleton pattern)"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ProviderRegistry()
    return _registry_instance


def reset_registry():
    """Reset the global registry instance (for testing)"""
    global _registry_instance
    _registry_instance = None


# Export main classes and functions
__all__ = [
    'ProviderType',
    'ModelResponse',
    'ModelProvider',
    'BaseModelProvider', 
    'ProviderRegistry',
    'get_registry_instance',
    'reset_registry'
]