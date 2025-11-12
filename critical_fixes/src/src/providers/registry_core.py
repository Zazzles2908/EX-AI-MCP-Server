"""
Provider Registry Core Implementation
Centralized model provider management system for EX-AI-MCP-Server
"""

import os
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
import json

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


class ModelCapability(Enum):
    """Model capabilities for routing decisions"""
    FAST_RESPONSE = "fast_response"
    EXTENDED_REASONING = "extended_reasoning"
    CODE_GENERATION = "code_generation"
    MULTIMODAL = "multimodal"
    BALANCED = "balanced"


class ModelProvider:
    """Represents a single model provider configuration"""
    
    def __init__(
        self,
        name: str,
        provider_type: ProviderType,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        capabilities: List[ModelCapability] = None,
        metadata: Dict[str, Any] = None
    ):
        self.name = name
        self.provider_type = provider_type
        self.model_id = model_id
        self.api_key = api_key or os.getenv(f"{provider_type.value.upper()}_API_KEY")
        self.base_url = base_url
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.enabled = True
        self.last_used = None
        self.error_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert provider to dictionary representation"""
        return {
            'name': self.name,
            'provider_type': self.provider_type.value,
            'model_id': self.model_id,
            'capabilities': [cap.value for cap in self.capabilities],
            'enabled': self.enabled,
            'has_api_key': bool(self.api_key),
            'base_url': self.base_url,
            'metadata': self.metadata,
            'last_used': self.last_used,
            'error_count': self.error_count
        }
    
    def is_available(self) -> bool:
        """Check if this provider is available for use"""
        return self.enabled and bool(self.api_key)


class ModelRegistry:
    """Central registry for all model providers"""
    
    def __init__(self):
        self._providers: Dict[str, ModelProvider] = {}
        self._provider_capabilities: Dict[ProviderType, List[ModelCapability]] = {
            ProviderType.OPENAI: [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.EXTENDED_REASONING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.BALANCED
            ],
            ProviderType.ANTHROPIC: [
                ModelCapability.EXTENDED_REASONING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.BALANCED
            ],
            ProviderType.MINIMAX: [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.EXTENDED_REASONING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.BALANCED
            ],
            ProviderType.DEEPSEEK: [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.CODE_GENERATION,
                ModelCapability.BALANCED
            ],
            ProviderType.OPENROUTER: [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.EXTENDED_REASONING,
                ModelCapability.BALANCED
            ],
            ProviderType.OLLAMA: [
                ModelCapability.CODE_GENERATION,
                ModelCapability.BALANCED
            ],
            ProviderType.VLLM: [
                ModelCapability.FAST_RESPONSE,
                ModelCapability.BALANCED
            ]
        }
        self._initialize_default_providers()
    
    def _initialize_default_providers(self):
        """Initialize the registry with default provider configurations"""
        default_providers = [
            # MiniMax providers (high priority)
            ModelProvider(
                name="minimax-pro",
                provider_type=ProviderType.MINIMAX,
                model_id="abab6.5s-chat",
                capabilities=[ModelCapability.EXTENDED_REASONING, ModelCapability.BALANCED],
                base_url="https://api.minimax.chat/v1"
            ),
            ModelProvider(
                name="minimax-turbo",
                provider_type=ProviderType.MINIMAX,
                model_id="abab6.5g-chat",
                capabilities=[ModelCapability.FAST_RESPONSE, ModelCapability.BALANCED],
                base_url="https://api.minimax.chat/v1"
            ),
            
            # OpenAI providers
            ModelProvider(
                name="gpt-4-turbo",
                provider_type=ProviderType.OPENAI,
                model_id="gpt-4-turbo-preview",
                capabilities=[ModelCapability.EXTENDED_REASONING, ModelCapability.BALANCED],
                base_url="https://api.openai.com/v1"
            ),
            ModelProvider(
                name="gpt-3.5-turbo",
                provider_type=ProviderType.OPENAI,
                model_id="gpt-3.5-turbo",
                capabilities=[ModelCapability.FAST_RESPONSE, ModelCapability.BALANCED],
                base_url="https://api.openai.com/v1"
            ),
            
            # Anthropic providers
            ModelProvider(
                name="claude-3-opus",
                provider_type=ProviderType.ANTHROPIC,
                model_id="claude-3-opus-20240229",
                capabilities=[ModelCapability.EXTENDED_REASONING, ModelCapability.BALANCED],
                base_url="https://api.anthropic.com/v1"
            ),
            ModelProvider(
                name="claude-3-haiku",
                provider_type=ProviderType.ANTHROPIC,
                model_id="claude-3-haiku-20240307",
                capabilities=[ModelCapability.FAST_RESPONSE, ModelCapability.BALANCED],
                base_url="https://api.anthropic.com/v1"
            ),
            
            # DeepSeek providers
            ModelProvider(
                name="deepseek-coder",
                provider_type=ProviderType.DEEPSEEK,
                model_id="deepseek-chat",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.BALANCED],
                base_url="https://api.deepseek.com/v1"
            ),
            
            # OpenRouter providers
            ModelProvider(
                name="openrouter-mixtral",
                provider_type=ProviderType.OPENROUTER,
                model_id="mistralai/mixtral-8x7b-instruct-v0.1",
                capabilities=[ModelCapability.FAST_RESPONSE, ModelCapability.BALANCED],
                base_url="https://openrouter.ai/api/v1"
            ),
            
            # Local providers
            ModelProvider(
                name="ollama-llama",
                provider_type=ProviderType.OLLAMA,
                model_id="llama2",
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.BALANCED],
                base_url="http://localhost:11434"
            ),
        ]
        
        for provider in default_providers:
            self.register_provider(provider)
        
        logger.info(f"Initialized {len(default_providers)} default providers")
    
    def register_provider(self, provider: ModelProvider) -> bool:
        """Register a new provider in the registry"""
        try:
            self._providers[provider.name] = provider
            logger.debug(f"Registered provider: {provider.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to register provider {provider.name}: {e}")
            return False
    
    def get_provider(self, name: str) -> Optional[ModelProvider]:
        """Get a provider by name"""
        return self._providers.get(name)
    
    def get_providers_by_capability(self, capability: ModelCapability) -> List[ModelProvider]:
        """Get all providers that support a specific capability"""
        return [
            provider for provider in self._providers.values()
            if provider.is_available() and capability in provider.capabilities
        ]
    
    def get_providers_by_type(self, provider_type: ProviderType) -> List[ModelProvider]:
        """Get all providers of a specific type"""
        return [
            provider for provider in self._providers.values()
            if provider.is_available() and provider.provider_type == provider_type
        ]
    
    def get_all_providers(self) -> Dict[str, ModelProvider]:
        """Get all registered providers"""
        return self._providers.copy()
    
    def get_available_providers(self) -> Dict[str, ModelProvider]:
        """Get all available (enabled and configured) providers"""
        return {
            name: provider for name, provider in self._providers.items()
            if provider.is_available()
        }
    
    def update_provider_status(self, name: str, success: bool):
        """Update provider status based on success/failure"""
        provider = self._providers.get(name)
        if provider:
            if success:
                provider.error_count = 0
                provider.last_used = "success"
            else:
                provider.error_count += 1
                provider.last_used = "failure"
                
                # Disable provider if too many consecutive failures
                if provider.error_count >= 5:
                    provider.enabled = False
                    logger.warning(f"Disabled provider {name} due to too many failures")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert registry to dictionary representation"""
        return {
            'total_providers': len(self._providers),
            'available_providers': len(self.get_available_providers()),
            'providers': {
                name: provider.to_dict() 
                for name, provider in self._providers.items()
            }
        }
    
    def save_to_file(self, filepath: str):
        """Save registry configuration to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            logger.info(f"Registry saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save registry to {filepath}: {e}")
    
    def load_from_file(self, filepath: str):
        """Load registry configuration from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self._providers = {}
            for name, provider_data in data.get('providers', {}).items():
                provider = ModelProvider(
                    name=provider_data['name'],
                    provider_type=ProviderType(provider_data['provider_type']),
                    model_id=provider_data['model_id'],
                    api_key=provider_data.get('api_key'),
                    base_url=provider_data.get('base_url'),
                    capabilities=[
                        ModelCapability(cap) for cap in provider_data.get('capabilities', [])
                    ],
                    metadata=provider_data.get('metadata', {})
                )
                provider.enabled = provider_data.get('enabled', True)
                provider.error_count = provider_data.get('error_count', 0)
                self._providers[name] = provider
            
            logger.info(f"Loaded {len(self._providers)} providers from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load registry from {filepath}: {e}")


# Global registry instance
_registry_instance: Optional[ModelRegistry] = None


def get_registry_instance() -> ModelRegistry:
    """Get the global registry instance (singleton pattern)"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ModelRegistry()
        logger.info("Initialized global model registry")
    return _registry_instance


def reset_registry():
    """Reset the global registry instance (for testing)"""
    global _registry_instance
    _registry_instance = None
    logger.info("Reset global model registry")


# Export main classes and functions
__all__ = [
    'ProviderType',
    'ModelCapability', 
    'ModelProvider',
    'ModelRegistry',
    'get_registry_instance',
    'reset_registry'
]