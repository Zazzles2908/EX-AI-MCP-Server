"""
GLM Provider - Minimal Implementation

Simplified GLM provider for chat completions.
"""

import os
import logging
from typing import Any, List, Dict, Optional
from openai import AsyncOpenAI
from src.providers.base import ProviderType, ModelCapabilities, ModelResponse

logger = logging.getLogger(__name__)


def build_payload(
    prompt: str,
    system_prompt: Optional[str],
    model_name: str,
    temperature: float,
    max_output_tokens: Optional[int],
    tools: Optional[list] = None,
    tool_choice: Optional[Any] = None,
    **kwargs
) -> dict:
    """
    Build a payload for GLM chat completions API.

    Args:
        prompt: User prompt
        system_prompt: System prompt (optional)
        model_name: Model name
        temperature: Temperature setting
        max_output_tokens: Maximum output tokens (optional)
        tools: Optional tools list
        tool_choice: Optional tool choice
        **kwargs: Additional parameters (e.g., response_format)

    Returns:
        Dict payload for API call
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model_name,
        "messages": messages,
    }

    if temperature is not None:
        payload["temperature"] = temperature

    if max_output_tokens is not None:
        payload["max_tokens"] = max_output_tokens

    if tools:
        payload["tools"] = tools

    if tool_choice is not None:
        payload["tool_choice"] = tool_choice

    # Handle additional kwargs (e.g., response_format for structured output)
    for key, value in kwargs.items():
        if key not in payload:
            payload[key] = value

    return payload


def chat_completions_create(
    messages: List[Dict[str, str]],
    model: str = "glm-4.5-flash",
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> ModelResponse:
    """
    Standalone chat completions function for backward compatibility.

    Args:
        messages: List of messages
        model: Model name
        temperature: Temperature
        max_tokens: Max tokens
        api_key: API key (optional, uses env var if not provided)
        base_url: Base URL (optional, uses env var if not provided)
        **kwargs: Additional parameters

    Returns:
        ModelResponse
    """
    provider = GLMProvider(api_key=api_key, base_url=base_url)
    import asyncio
    return asyncio.run(provider.chat_completions_create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    ))


def generate_content(
    prompt: str,
    model_name: str = "glm-4.5-flash",
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: Optional[int] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> ModelResponse:
    """
    Standalone generate content function for backward compatibility.

    Args:
        prompt: User prompt
        model_name: Model name
        system_prompt: System prompt (optional)
        temperature: Temperature
        max_tokens: Max tokens
        api_key: API key (optional, uses env var if not provided)
        base_url: Base URL (optional, uses env var if not provided)
        **kwargs: Additional parameters

    Returns:
        ModelResponse
    """
    provider = GLMProvider(api_key=api_key, base_url=base_url)
    import asyncio
    return asyncio.run(provider.generate_content(
        prompt=prompt,
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    ))


class GLMProvider:
    """Minimal GLM provider implementation."""

    # List of supported models
    SUPPORTED_MODELS = {
        "glm-4": ModelCapabilities(),
        "glm-4.5": ModelCapabilities(),
        "glm-4.5-flash": ModelCapabilities(),
        "glm-4.6": ModelCapabilities(),
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        # Use provided api_key or fall back to environment
        self.api_key = api_key or os.getenv("GLM_API_KEY")
        # Use provided base_url or fall back to default
        self.base_url = base_url or os.getenv("GLM_API_URL") or "https://open.bigmodel.cn/api/paas/v4/"
        self.client = None

        if self.api_key:
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )

    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.GLM

    def validate_model_name(self, model_name: str) -> bool:
        """Check if the model is supported by this provider."""
        return model_name in self.SUPPORTED_MODELS

    def list_models(self, respect_restrictions: bool = True) -> List[str]:
        """List all supported models."""
        return list(self.SUPPORTED_MODELS.keys())

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a model."""
        return self.SUPPORTED_MODELS.get(model_name, ModelCapabilities())

    def get_model_configurations(self) -> dict[str, ModelCapabilities]:
        """Get all model configurations with capabilities."""
        return self.SUPPORTED_MODELS

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
        model_name: str = "glm-4.5-flash",
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
        model: str = "glm-4.5-flash",
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
                content="Error: GLM API key not configured",
                model_name=model,
                provider=self.get_provider_type()
            )

        try:
            # Remove unsupported parameters from kwargs
            # on_chunk is an OpenAI SDK parameter not supported by GLM API
            kwargs_copy = kwargs.copy()
            kwargs_copy.pop('on_chunk', None)

            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs_copy
            )
            return ModelResponse(
                content=response.choices[0].message.content,
                usage=response.usage.dict() if hasattr(response.usage, 'dict') else {},
                model_name=model,
                provider=self.get_provider_type()
            )

        except Exception as e:
            logger.error(f"GLM API error: {e}")
            return ModelResponse(
                content=f"Error: {str(e)}",
                model_name=model,
                provider=self.get_provider_type()
            )
