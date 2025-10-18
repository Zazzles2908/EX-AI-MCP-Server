"""Async base model provider interface and data classes."""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from .base import ModelCapabilities, ModelResponse, ProviderType
from config import TimeoutConfig

logger = logging.getLogger(__name__)


@dataclass
class AsyncProviderConfig:
    """Configuration for async providers.

    TRACK 2 FIX (2025-10-16): Use centralized TimeoutConfig for consistency.
    """

    # HTTP client timeouts (in seconds)
    # TRACK 2 FIX: Use TimeoutConfig.KIMI_TIMEOUT_SECS for read_timeout default
    connect_timeout: float = 5.0
    read_timeout: float = field(default_factory=lambda: float(TimeoutConfig.KIMI_TIMEOUT_SECS))
    write_timeout: float = 10.0
    pool_timeout: float = 5.0

    # Connection pooling
    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # Initial delay, doubles with each retry


class AsyncModelProvider(ABC):
    """Abstract base class for async model providers.
    
    This class provides the foundation for async provider implementations
    with proper resource management, retry logic, and error handling.
    """
    
    def __init__(self, api_key: str, config: Optional[AsyncProviderConfig] = None, **kwargs):
        """Initialize the async provider.
        
        Args:
            api_key: API key for the provider
            config: Optional configuration object
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = config or AsyncProviderConfig()
        self.extra_config = kwargs
        self._closed = False
        self._http_client: Optional[Any] = None
    
    @abstractmethod
    async def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        """Generate content using the model asynchronously.
        
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
        pass
    
    @abstractmethod
    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        pass
    
    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """Get the provider type."""
        pass
    
    @abstractmethod
    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported by this provider."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and can make requests.
        
        Returns:
            True if provider is healthy, False otherwise
        """
        pass
    
    async def close(self):
        """Clean up resources held by the provider.
        
        This method should be called when the provider is no longer needed
        to ensure proper cleanup of HTTP connections and other resources.
        """
        if self._closed:
            return
        
        self._closed = True
        
        # CRITICAL FIX (2025-10-17): Handle both async and sync HTTP clients gracefully
        # Some clients (like httpx.Client) don't have aclose(), only close()
        # Close HTTP client if it exists
        if self._http_client is not None:
            try:
                # Try async close first (for httpx.AsyncClient)
                if hasattr(self._http_client, 'aclose'):
                    await self._http_client.aclose()
                    logger.debug(f"Closed async HTTP client for {self.get_provider_type().value} provider")
                # Fallback to sync close (for httpx.Client)
                elif hasattr(self._http_client, 'close'):
                    self._http_client.close()
                    logger.debug(f"Closed sync HTTP client for {self.get_provider_type().value} provider")
                else:
                    logger.debug(f"HTTP client has no close method, skipping cleanup")
            except Exception as e:
                logger.debug(f"HTTP client cleanup failed (non-critical): {e}")
            finally:
                self._http_client = None
    
    async def _retry_with_backoff(self, coro, *args, **kwargs):
        """Retry a coroutine with exponential backoff.
        
        Args:
            coro: Coroutine function to retry
            *args: Positional arguments for the coroutine
            **kwargs: Keyword arguments for the coroutine
            
        Returns:
            Result from the coroutine
            
        Raises:
            Exception: If all retries are exhausted
        """
        for attempt in range(self.config.max_retries + 1):
            try:
                return await coro(*args, **kwargs)
            except Exception as e:
                if attempt == self.config.max_retries:
                    logger.error(
                        f"Failed after {self.config.max_retries} retries for "
                        f"{self.get_provider_type().value} provider: {e}"
                    )
                    raise
                
                delay = self.config.retry_delay * (2 ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_retries + 1} failed for "
                    f"{self.get_provider_type().value} provider: {e}. "
                    f"Retrying in {delay}s..."
                )
                await asyncio.sleep(delay)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    def _resolve_model_name(self, model_name: str, supported_models: dict[str, ModelCapabilities]) -> str:
        """Resolve model shorthand to full name.
        
        Args:
            model_name: Model name that may be an alias
            supported_models: Dictionary of supported models
            
        Returns:
            Resolved model name
        """
        # First check if it's already a base model name (case-sensitive exact match)
        if model_name in supported_models:
            return model_name
        
        # Check case-insensitively for both base models and aliases
        model_name_lower = model_name.lower()
        
        # Check base model names case-insensitively
        for base_model in supported_models:
            if base_model.lower() == model_name_lower:
                return base_model
        
        # Check aliases
        for base_model, capabilities in supported_models.items():
            if capabilities.aliases:
                if any(alias.lower() == model_name_lower for alias in capabilities.aliases):
                    return base_model
        
        # If not found, return as-is
        return model_name
    
    def get_effective_temperature(
        self, 
        model_name: str, 
        requested_temperature: float
    ) -> Optional[float]:
        """Get the effective temperature to use for a model.
        
        This method handles:
        - Models that don't support temperature (returns None)
        - Fixed temperature models (returns the fixed value)
        - Clamping to min/max range for models with constraints
        
        Args:
            model_name: The model to get temperature for
            requested_temperature: The temperature requested by the user/tool
            
        Returns:
            The effective temperature to use, or None if temperature shouldn't be passed
        """
        try:
            capabilities = self.get_capabilities(model_name)
            
            # Check if model supports temperature at all
            if not capabilities.supports_temperature:
                return None
            
            # Use temperature constraint to get corrected value
            corrected_temp = capabilities.temperature_constraint.get_corrected_value(requested_temperature)
            
            if corrected_temp != requested_temperature:
                logger.debug(
                    f"Adjusting temperature from {requested_temperature} to {corrected_temp} "
                    f"for model {model_name}"
                )
            
            return corrected_temp
            
        except Exception as e:
            logger.debug(f"Could not determine effective temperature for {model_name}: {e}")
            # If we can't get capabilities, return the requested temperature
            return requested_temperature

