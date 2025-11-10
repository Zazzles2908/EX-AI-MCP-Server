"""Async GLM (ZhipuAI) provider implementation using zhipuai.async_client.AsyncZhipuAI."""

import logging
import os
from typing import Optional
import httpx

from .async_base import AsyncModelProvider, AsyncProviderConfig
from .base import ModelCapabilities, ModelResponse, ProviderType
from . import glm_config
from . import async_glm_chat
from config import TimeoutConfig

# Import error handling framework
from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)


class AsyncGLMProvider(AsyncModelProvider):
    """Async provider implementation for GLM models (ZhipuAI)."""
    
    DEFAULT_BASE_URL = os.getenv("GLM_API_URL", "https://api.z.ai/api/paas/v4")
    
    # Use model configurations from glm_config module
    SUPPORTED_MODELS: dict[str, ModelCapabilities] = glm_config.SUPPORTED_MODELS
    
    def __init__(
        self, 
        api_key: str, 
        base_url: Optional[str] = None,
        config: Optional[AsyncProviderConfig] = None,
        **kwargs
    ):
        """Initialize async GLM provider.
        
        Args:
            api_key: GLM API key
            base_url: Optional base URL (defaults to z.ai proxy)
            config: Optional async provider configuration
            **kwargs: Additional configuration
        """
        super().__init__(api_key, config, **kwargs)
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        # NOTE: zhipuai SDK does NOT have async support (no AsyncZhipuAI or async_client)
        # We use the sync ZhipuAI client and wrap calls with asyncio.to_thread()
        try:
            from zhipuai import ZhipuAI

            # Create HTTP client with timeout configuration
            # TRACK 2 FIX (2025-10-16): Add timeout and retry logic to prevent indefinite hangs
            http_client = httpx.Client(
                timeout=TimeoutConfig.GLM_TIMEOUT_SECS,
                transport=httpx.HTTPTransport(retries=3)
            )

            # Use sync client with timeout configuration - we'll wrap calls with asyncio.to_thread()
            self._sdk_client = ZhipuAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=TimeoutConfig.GLM_TIMEOUT_SECS,
                max_retries=3,
                http_client=http_client,
            )
            self._http_client = http_client  # Store for cleanup

            logger.info(
                f"Async GLM provider initialized with sync SDK + asyncio.to_thread() "
                f"(base_url={self.base_url}, timeout={TimeoutConfig.GLM_TIMEOUT_SECS}s, max_retries=3)"
            )

        except ImportError as e:
            log_error(ErrorCode.PROVIDER_ERROR, "zhipuai not available", exc_info=True)
            raise ProviderError("GLM", Exception("zhipuai not available. Install with: pip install zhipuai>=2.1.0")) from e
        except Exception as e:
            log_error(ErrorCode.PROVIDER_ERROR, f"Failed to initialize async GLM provider: {e}", exc_info=True)
            raise ProviderError("GLM", e) from e
    
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.GLM
    
    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported."""
        resolved = self._resolve_model_name(model_name, self.SUPPORTED_MODELS)
        return resolved in self.SUPPORTED_MODELS
    
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        return glm_config.get_capabilities(
            model_name,
            self.SUPPORTED_MODELS,
            lambda name: self._resolve_model_name(name, self.SUPPORTED_MODELS)
        )
    
    async def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 1.0,
        top_p: float = 0.95,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate content asynchronously using GLM model.
        
        Args:
            prompt: User prompt to send to the model
            model_name: Name of the model to use
            system_prompt: Optional system prompt for model behavior
            temperature: Sampling temperature (0-2), default 1.0 for GLM 4.6
            top_p: Nucleus sampling parameter, default 0.95 for GLM 4.6
            max_output_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Returns:
            ModelResponse with generated content and metadata
        """
        # Resolve model name and get effective temperature
        resolved = self._resolve_model_name(model_name, self.SUPPORTED_MODELS)
        effective_temp = self.get_effective_temperature(resolved, temperature)

        # CRITICAL FIX (2025-10-17): Pass http_client and use_sdk to async chat module
        # This fixes the signature mismatch error that was causing fallback to sync provider
        # Delegate to async chat module
        return await async_glm_chat.generate_content_async(
            sdk_client=self._sdk_client,
            http_client=self._http_client,
            prompt=prompt,
            model_name=resolved,
            system_prompt=system_prompt,
            temperature=effective_temp,
            max_output_tokens=max_output_tokens,
            use_sdk=True,  # We always use SDK in async provider
            **kwargs
        )
    
    async def health_check(self) -> bool:
        """Check if the provider is healthy.

        Returns:
            True if provider can make requests, False otherwise
        """
        try:
            # Simple health check: try to generate minimal content
            response = await self.generate_content(
                prompt="test",
                model_name="glm-4.5-flash",  # Use fastest model for health check
                max_output_tokens=5,
            )
            return bool(response.content)
        except Exception as e:
            logger.warning(f"Async GLM health check failed: {e}")
            return False

    async def chat_completions_create(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 1.0,
        top_p: float = 0.95,
        thinking_mode: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """Create chat completion using message arrays (for expert_analysis compatibility).

        Args:
            model: Model name to use
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0-2), default 1.0 for GLM 4.6
            top_p: Nucleus sampling parameter, default 0.95 for GLM 4.6
            thinking_mode: Optional thinking mode for supported models
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with 'content', 'model', 'usage' keys (compatible with expert_analysis)
        """
        # Delegate to async_glm_chat module which returns ModelResponse
        response = await async_glm_chat.chat_completions_create_async(
            client=self._sdk_client,
            model=model,
            messages=messages,
            temperature=temperature,
            thinking_mode=thinking_mode,
            **kwargs
        )

        # Convert ModelResponse to dict format expected by expert_analysis
        return {
            "content": response.content,
            "model": response.model_name,
            "usage": response.usage or {},
        }
    
    async def close(self):
        """Clean up resources."""
        await super().close()
        # Close HTTP client if it exists
        if self._http_client:
            self._http_client.close()

