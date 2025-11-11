"""Kimi provider - Minimal implementation."""

import os
import logging
from typing import Any, List, Dict, Optional
from src.providers.base import ProviderType, ModelCapabilities, ModelResponse

logger = logging.getLogger(__name__)


class KimiProvider:
    """Minimal Kimi provider implementation."""

    # List of supported models
    SUPPORTED_MODELS = {
        "moonshot-v1-8k": ModelCapabilities(),
        "moonshot-v1-32k": ModelCapabilities(),
        "moonshot-v1-128k": ModelCapabilities(),
        "moonshot-v1-8k-vision": ModelCapabilities(),
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # Use provided api_key or fall back to environment
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        # Use provided base_url or fall back to environment or default
        self.base_url = base_url or os.getenv("KIMI_API_URL") or os.getenv("MOONSHOT_API_URL") or "https://api.moonshot.cn/v1/"
        self.client = None

        if self.api_key:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.KIMI

    def validate_model_name(self, model_name: str) -> bool:
        """Check if the model is supported by this provider."""
        return model_name in self.SUPPORTED_MODELS

    def list_models(self, respect_restrictions: bool = True) -> List[str]:
        """List all supported models."""
        return list(self.SUPPORTED_MODELS.keys())

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a model."""
        return self.SUPPORTED_MODELS.get(model_name, ModelCapabilities())

    def supports_streaming(self, model_name: str) -> bool:
        """Check if model supports streaming."""
        return True

    def supports_thinking_mode(self, model_name: str) -> bool:
        """Check if model supports thinking mode."""
        return False

    def supports_images(self, model_name: str) -> bool:
        """Check if model supports image input."""
        return "vision" in model_name.lower()

    async def generate_content(
        self,
        prompt: str,
        model_name: str = "moonshot-v1-8k",
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate content using chat completions."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return await self.chat_completions_create(
            messages=messages,
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    async def chat_completions_create(
        self,
        messages: List[Dict[str, str]],
        model: str = "moonshot-v1-8k",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Create chat completion.

        Args:
            messages: List of messages
            model: Model name
            temperature: Temperature
            max_tokens: Max tokens
            **kwargs: Additional parameters

        Returns:
            Generated ModelResponse
        """
        if not self.client:
            return ModelResponse(
                content="Error: KIMI API key not configured",
                model_name=model,
                provider=self.get_provider_type()
            )

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return ModelResponse(
                content=response.choices[0].message.content,
                usage=response.usage.dict() if hasattr(response.usage, 'dict') else {},
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
