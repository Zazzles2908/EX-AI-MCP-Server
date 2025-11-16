"""MiniMax provider implementation.

MiniMax provides advanced AI models (MiniMax-M2 and MiniMax-M2-Stable) through Anthropic-compatible API.
Key features include interleaved thinking, function calling, streaming, and tool use.

API Base URL: https://api.minimax.io/anthropic

Key Features:
- Interleaved thinking process with reasoning content
- Full function calling and tool use support  
- Streaming response support
- OpenAI SDK compatibility with reasoning_split parameter
- No image/document input support yet

Reference: https://platform.minimax.io/docs/api-reference/text-anthropic-api
"""

import logging
import os
from typing import Any, Optional, Dict

from .base import ModelProvider, ModelCapabilities, ModelResponse, ProviderType
from utils.http_client import HttpClient
from config import TimeoutConfig

# Optional import - anthropic package may not be installed
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    Anthropic = None
    ANTHROPIC_AVAILABLE = False
    logging.warning("anthropic package not available - MiniMax provider disabled")

logger = logging.getLogger(__name__)


class MiniMaxModelProvider(ModelProvider):
    """Provider implementation for MiniMax models."""
    
    DEFAULT_BASE_URL = os.getenv("MINIMAX_API_URL", "https://api.minimax.io/anthropic")
    
    # MiniMax model capabilities - Updated with official documentation
    # Reference: https://platform.minimax.io/docs/api-reference/text-anthropic-api
    SUPPORTED_MODELS = {
        "MiniMax-M2": ModelCapabilities(
            provider=ProviderType.MINIMAX,
            model_name="MiniMax-M2",
            friendly_name="MiniMax M2",
            context_window=8192,  # Anthropic-compatible context window
            max_output_tokens=4096,  # Per documentation examples
            supports_function_calling=True,  # FULLY SUPPORTED per docs
            supports_streaming=True,  # FULLY SUPPORTED per docs
            supports_images=False,  # NOT SUPPORTED per docs
            supports_extended_thinking=True,  # FULLY SUPPORTED - key feature!
            aliases=["minimax-m2", "m2"],
        ),
        "MiniMax-M2-Stable": ModelCapabilities(
            provider=ProviderType.MINIMAX,
            model_name="MiniMax-M2-Stable",
            friendly_name="MiniMax M2 Stable",
            context_window=8192,  # Anthropic-compatible context window
            max_output_tokens=4096,  # Per documentation examples
            supports_function_calling=True,  # FULLY SUPPORTED per docs
            supports_streaming=True,  # FULLY SUPPORTED per docs
            supports_images=False,  # NOT SUPPORTED per docs
            supports_extended_thinking=True,  # FULLY SUPPORTED - key feature!
            aliases=["minimax-m2-stable", "m2-stable"],
        ),
        "abab6.5s-chat": ModelCapabilities(
            provider=ProviderType.MINIMAX,
            model_name="abab6.5s-chat",
            friendly_name="ABAB 6.5s Chat",
            context_window=8192,  # Standard context for chat models
            max_output_tokens=4096,
            supports_function_calling=True,  # FULLY SUPPORTED per docs
            supports_streaming=True,  # FULLY SUPPORTED per docs
            supports_images=False,  # NOT SUPPORTED per docs
            supports_extended_thinking=True,  # FULLY SUPPORTED - key feature!
            aliases=["abab6.5s", "6.5s-chat"],
        ),
        "abab6.5g-chat": ModelCapabilities(
            provider=ProviderType.MINIMAX,
            model_name="abab6.5g-chat",
            friendly_name="ABAB 6.5g Chat",
            context_window=8192,  # Standard context for chat models
            max_output_tokens=4096,
            supports_function_calling=True,  # FULLY SUPPORTED per docs
            supports_streaming=True,  # FULLY SUPPORTED per docs
            supports_images=False,  # NOT SUPPORTED per docs
            supports_extended_thinking=True,  # FULLY SUPPORTED - key feature!
            aliases=["abab6.5g", "6.5g-chat"],
        ),
    }

    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        """Initialize MiniMax provider."""
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        # Check if anthropic package is available
        if not ANTHROPIC_AVAILABLE:
            logger.warning("anthropic package not available - MiniMax provider disabled")
            self.client = None
            return
            
        # Initialize Anthropic client with MiniMax configuration
        try:
            # Get timeout with fallback if MINIMAX_TIMEOUT_SECS doesn't exist
            try:
                timeout_secs = TimeoutConfig.MINIMAX_TIMEOUT_SECS
            except AttributeError:
                timeout_secs = 30  # Default fallback
                
            self.client = Anthropic(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=timeout_secs,
                max_retries=3,
            )
            logger.info(f"MiniMax provider initialized with base_url={self.base_url}")
            logger.info(f"Available models: {list(self.SUPPORTED_MODELS.keys())}")
            logger.info(f"MiniMax features: thinking, function calling, streaming, tool use")
        except Exception as e:
            logger.error(f"Failed to initialize MiniMax client: {e}")
            self.client = None

    def get_provider_type(self) -> ProviderType:
        return ProviderType.MINIMAX

    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported."""
        resolved = self._resolve_model_name(model_name)
        return resolved in self.SUPPORTED_MODELS

    def supports_thinking_mode(self, model_name: str) -> bool:
        """Check if the model supports thinking mode."""
        # MiniMax models have FULL thinking support (interleaved thinking)
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        return bool(capabilities and capabilities.supports_extended_thinking)

    def supports_images(self, model_name: str) -> bool:
        """MiniMax does not support image inputs."""
        return False

    def supports_streaming(self, model_name: str) -> bool:
        """MiniMax has limited streaming capabilities."""
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        return bool(capabilities and capabilities.supports_streaming)

    def list_models(self, respect_restrictions: bool = True):
        """List available MiniMax models."""
        return super().list_models(respect_restrictions=respect_restrictions)

    def get_model_configurations(self) -> Dict[str, ModelCapabilities]:
        """Get all supported model configurations."""
        return self.SUPPORTED_MODELS

    def get_all_model_aliases(self) -> Dict[str, list[str]]:
        """Get all model aliases."""
        aliases = {}
        for model_name, capabilities in self.SUPPORTED_MODELS.items():
            if capabilities.aliases:
                aliases[model_name] = capabilities.aliases
        return aliases

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        resolved = self._resolve_model_name(model_name)
        return self.SUPPORTED_MODELS.get(resolved, self.SUPPORTED_MODELS["MiniMax-M2"])

    def count_tokens(self, text: str, model_name: str) -> int:
        """Estimate token count for text."""
        # Simple estimation - approximately 4 characters per token
        # TODO: Implement proper token counting if needed
        return len(text) // 4

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model name, handling aliases."""
        # Check if it's already a base model name
        if model_name in self.SUPPORTED_MODELS:
            return model_name
            
        # Check aliases case-insensitively
        model_name_lower = model_name.lower()
        for base_model, capabilities in self.SUPPORTED_MODELS.items():
            if capabilities.aliases:
                for alias in capabilities.aliases:
                    if alias.lower() == model_name_lower:
                        return base_model
                        
        # If not found, return as-is
        return model_name

    def get_effective_temperature(self, model_name: str, temperature: float) -> float:
        """Get effective temperature for model (with constraints)."""
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        if capabilities and hasattr(capabilities, 'temperature_range'):
            min_temp, max_temp = capabilities.temperature_range
            return max(min_temp, min(temperature, max_temp))
        return temperature

    def chat_completions_create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[Any]] = None,
        tool_choice: Optional[Any] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> dict:
        """
        Create chat completion using MiniMax M2.
        
        Note: MiniMax does not support function calling, so tools and tool_choice
        will be ignored.
        """
        if not self.client:
            raise RuntimeError("MiniMax client not available")
            
        resolved = self._resolve_model_name(model)
        effective_temp = self.get_effective_temperature(resolved, temperature)
        
        # Remove unsupported parameters if any exist (MiniMax supports tools and tool_choice)
        if tools is not None:
            logger.debug("MiniMax supports tools - proceeding with function calling")
            
        try:
            response = self.client.messages.create(
                model=resolved,
                max_tokens=min(kwargs.get('max_tokens', 1000), 4096),  # Cap at 4096
                messages=messages,
                temperature=effective_temp,
                # MiniMax supports tools and tool_choice (per official docs)
                tools=tools,  # FULLY SUPPORTED
                tool_choice=tool_choice,  # FULLY SUPPORTED
            )
            
            # Parse response to extract thinking and answer
            thinking_content = ""
            final_answer = ""
            
            for content_block in response.content:
                if hasattr(content_block, 'thinking'):
                    thinking_content = str(content_block.thinking)
                elif hasattr(content_block, 'text'):
                    final_answer = content_block.text
            
            return {
                "provider": "minimax",
                "model": resolved,
                "content": final_answer,
                "thinking": thinking_content if thinking_content else None,
                "usage": {
                    "input_tokens": getattr(response.usage, 'input_tokens', 0),
                    "output_tokens": getattr(response.usage, 'output_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0)
                },
                "stop_reason": getattr(response, 'stop_reason', 'unknown'),
                "metadata": {
                    "thinking_enabled": bool(thinking_content),
                    "model_name": resolved,
                    "supports_tools": True,  # MiniMax supports tools
                    "supports_streaming": True,  # MiniMax supports streaming
                }
            }
            
        except Exception as e:
            logger.error(f"MiniMax chat completion failed: {e}")
            raise

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """
        Generate content using MiniMax M2.
        
        This method converts the simple prompt-based interface to the
        messages format required by MiniMax API.
        """
        if not self.client:
            raise RuntimeError("MiniMax client not available")
            
        resolved = self._resolve_model_name(model_name)
        effective_temp = self.get_effective_temperature(resolved, temperature)
        
        # Convert to messages format
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
            
        messages.append({
            "role": "user", 
            "content": prompt
        })
        
        # Set max tokens
        max_tokens = max_output_tokens or 1000
        if max_tokens > 4096:
            max_tokens = 4096
            logger.warning("MiniMax max_tokens capped at 4096")
            
        try:
            response = self.client.messages.create(
                model=resolved,
                max_tokens=max_tokens,
                messages=messages,
                temperature=effective_temp,
            )
            
            # Parse response
            thinking_content = ""
            final_answer = ""
            
            for content_block in response.content:
                if hasattr(content_block, 'thinking'):
                    thinking_content = str(content_block.thinking)
                elif hasattr(content_block, 'text'):
                    final_answer = content_block.text
            
            return ModelResponse(
                content=final_answer,
                provider=self.get_provider_type(),
                model=resolved,
                usage={
                    "input_tokens": getattr(response.usage, 'input_tokens', 0),
                    "output_tokens": getattr(response.usage, 'output_tokens', 0),
                    "total_tokens": getattr(response.usage, 'total_tokens', 0)
                },
                metadata={
                    "thinking": thinking_content,  # MiniMax thinking process
                    "thinking_enabled": bool(thinking_content),
                    "stop_reason": getattr(response, 'stop_reason', 'unknown'),
                    "supports_tools": True,  # MiniMax supports tools
                    "supports_streaming": True,  # MiniMax supports streaming
                }
            )
            
        except Exception as e:
            logger.error(f"MiniMax content generation failed: {e}")
            raise

    def upload_file(self, file_path: str, purpose: str = "agent") -> str:
        """MiniMax does not support file uploads."""
        raise NotImplementedError("MiniMax provider does not support file uploads")
