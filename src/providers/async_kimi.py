"""Async Kimi (Moonshot) provider implementation using openai.AsyncOpenAI."""

import logging
import os
from typing import Optional
import httpx

from .async_base import AsyncModelProvider, AsyncProviderConfig
from .base import ModelCapabilities, ModelResponse, ProviderType
from . import kimi_config
from . import async_kimi_chat
from config import TimeoutConfig

logger = logging.getLogger(__name__)


class AsyncKimiProvider(AsyncModelProvider):
    """Async provider implementation for Kimi (Moonshot) models."""
    
    DEFAULT_BASE_URL = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1")
    
    # Use model configurations from kimi_config module
    SUPPORTED_MODELS: dict[str, ModelCapabilities] = kimi_config.SUPPORTED_MODELS
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        config: Optional[AsyncProviderConfig] = None,
        **kwargs
    ):
        """Initialize async Kimi provider.
        
        Args:
            api_key: Kimi API key
            base_url: Optional base URL (defaults to Moonshot API)
            config: Optional async provider configuration
            **kwargs: Additional configuration
        """
        super().__init__(api_key, config, **kwargs)
        self.base_url = base_url or self.DEFAULT_BASE_URL
        
        # Provider-specific timeout overrides via env
        try:
            rt = os.getenv("KIMI_READ_TIMEOUT_SECS", "").strip()
            ct = os.getenv("KIMI_CONNECT_TIMEOUT_SECS", "").strip()
            wt = os.getenv("KIMI_WRITE_TIMEOUT_SECS", "").strip()
            pt = os.getenv("KIMI_POOL_TIMEOUT_SECS", "").strip()
            
            if rt:
                self.config.read_timeout = float(rt)
            if ct:
                self.config.connect_timeout = float(ct)
            if wt:
                self.config.write_timeout = float(wt)
            if pt:
                self.config.pool_timeout = float(pt)

            # TRACK 2 FIX (2025-10-16): Use centralized timeout instead of hardcoded 300s
            # If no explicit read timeout is set, use TimeoutConfig.KIMI_TIMEOUT_SECS (30s)
            if not rt:
                self.config.read_timeout = TimeoutConfig.KIMI_TIMEOUT_SECS
                logger.info(f"Async Kimi provider using centralized timeout: {TimeoutConfig.KIMI_TIMEOUT_SECS}s")
        except Exception as e:
            logger.warning(f"Failed to parse Kimi timeout configuration: {e}", exc_info=True)
        
        # Initialize async OpenAI client
        try:
            from openai import AsyncOpenAI  # type: ignore
            
            # Configure HTTP client with timeouts and connection pooling
            http_client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_keepalive_connections=self.config.max_keepalive_connections,
                    max_connections=self.config.max_connections,
                    keepalive_expiry=self.config.keepalive_expiry,
                ),
                timeout=httpx.Timeout(
                    connect=self.config.connect_timeout,
                    read=self.config.read_timeout,
                    write=self.config.write_timeout,
                    pool=self.config.pool_timeout,
                ),
            )
            
            # Store HTTP client for cleanup
            self._http_client = http_client
            
            # Create async OpenAI client with custom HTTP client
            self._sdk_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=http_client,
            )
            
            logger.info(f"Async Kimi provider initialized with AsyncOpenAI (base_url={self.base_url})")
            
        except ImportError as e:
            raise RuntimeError(
                "openai AsyncOpenAI not available. "
                "Install with: pip install openai>=1.55.2"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to initialize async Kimi provider: {e}") from e
    
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        return ProviderType.KIMI
    
    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported."""
        resolved = self._resolve_model_name(model_name, self.SUPPORTED_MODELS)
        return resolved in self.SUPPORTED_MODELS
    
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        return kimi_config.get_capabilities(
            model_name,
            self.SUPPORTED_MODELS,
            lambda name: self._resolve_model_name(name, self.SUPPORTED_MODELS)
        )
    
    async def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate content asynchronously using Kimi model.
        
        Args:
            prompt: User prompt to send to the model
            model_name: Name of the model to use
            system_prompt: Optional system prompt for model behavior
            temperature: Sampling temperature (0-2)
            max_output_tokens: Maximum tokens to generate
            **kwargs: Provider-specific parameters
            
        Returns:
            ModelResponse with generated content and metadata
        """
        # Resolve model name and get effective temperature
        resolved = self._resolve_model_name(model_name, self.SUPPORTED_MODELS)
        effective_temp = self.get_effective_temperature(resolved, temperature)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Delegate to async chat module
        return await async_kimi_chat.chat_completions_create_async(
            client=self._sdk_client,
            model=resolved,
            messages=messages,
            temperature=effective_temp,
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
                model_name="kimi-k2-turbo-preview",  # Use fastest model for health check
                max_output_tokens=5,
            )
            return bool(response.content)
        except Exception as e:
            logger.warning(f"Async Kimi health check failed: {e}")
            return False
    
    async def close(self):
        """Clean up resources."""
        await super().close()
        # SDK client cleanup is handled by HTTP client closure in parent class

