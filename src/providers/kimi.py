"Kimi provider - Minimal implementation."

import os
import logging
from typing import Any, List, Dict, Optional
from src.providers.base import ProviderType, ModelCapabilities, ModelResponse, ModelProvider
from .kimi_config import SUPPORTED_MODELS as KIMI_CONFIG_MODELS

logger = logging.getLogger(__name__)


class KimiProvider(ModelProvider):
    """Minimal Kimi provider implementation."""
    
    # Use K2 models from kimi_config
    SUPPORTED_MODELS = KIMI_CONFIG_MODELS
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """Initialize Kimi provider.
        
        Args:
            api_key: Kimi API key
            base_url: Optional base URL (defaults to environment variable)
        """
        self.api_key = api_key
        self.base_url = base_url or os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1")
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
        except ImportError:
            self.client = None
            logger.error("OpenAI package not installed")
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.KIMI
    
    def get_model_capabilities(self, model_name: str) -> Optional[ModelCapabilities]:
        """Get model capabilities."""
        return self.SUPPORTED_MODELS.get(model_name)
    
    def list_models(self, respect_restrictions: bool = True):
        """List all supported models."""
        return list(self.SUPPORTED_MODELS.keys())
    
    def get_model_configurations(self) -> Dict[str, ModelCapabilities]:
        """Get all model configurations with capabilities."""
        return self.SUPPORTED_MODELS
    
    def validate_model_name(self, model_name: str) -> bool:
        """Check if the model is supported by this provider."""
        return model_name in self.SUPPORTED_MODELS
    
    def supports_streaming(self, model_name: str) -> bool:
        """Check if model supports streaming."""
        return True
    
    def supports_thinking_mode(self, model_name: str) -> bool:
        """Check if model supports thinking mode."""
        capabilities = self.SUPPORTED_MODELS.get(model_name)
        return capabilities.supports_extended_thinking if capabilities else False
    
    async def chat_completions_create(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Create chat completion.

        Args:
            messages: List of messages
            model: Model name (uses KIMI_DEFAULT_MODEL from env if not specified)
            temperature: Temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            Generated ModelResponse
        """
        # Use environment default if no model specified
        if model is None:
            model = os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0905-preview")

        if not self.client:
            return ModelResponse(
                content="Error: KIMI API key not configured",
                model_name=model,
                provider=self.get_provider_type()
            )

        try:
            # Remove unsupported parameters from kwargs
            # on_chunk is an OpenAI SDK parameter not supported by Kimi API
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop("on_chunk", None)

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs_copy
            )
            return ModelResponse(
                content=response.choices[0].message.content,
                usage=response.usage.dict() if hasattr(response.usage, "dict") else {},
                model_name=model,
                provider=self.get_provider_type()
            )

        except Exception as e:
            logger.error(f"KIMI API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                model_name=model,
                provider=self.get_provider_type()
            )


# Alias for backward compatibility
KimiModelProvider = KimiProvider

