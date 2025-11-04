"""
OpenAI Compatible Provider - Main Module

Base class for OpenAI-compatible API providers.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class (this file)

This file provides a backward-compatible wrapper that imports from the
refactored modules and maintains the original API.
"""

import os
import logging

from .base import ModelProvider
from .mixins import RetryMixin

# Import refactored modules
from .openai_config import OpenAIConfig
from .openai_client import OpenAIClientManager
from .openai_capabilities import OpenAICapabilities
from .openai_token_manager import OpenAITokenManager
from .openai_error_handler import OpenAIErrorHandler
from .openai_content_generator import OpenAIContentGenerator

# Initialize logger for this module
logger = logging.getLogger(__name__)

# FIX (2025-10-24): Enable DEBUG logging for OpenAI SDK and httpx to capture retry errors
if os.getenv("OPENAI_DEBUG_LOGGING", "false").lower() == "true":
    logging.getLogger("openai").setLevel(logging.DEBUG)
    logging.getLogger("httpx").setLevel(logging.DEBUG)
    logger.info("OpenAI SDK debug logging enabled (OPENAI_DEBUG_LOGGING=true)")


class OpenAICompatibleProvider(
    RetryMixin,
    ModelProvider,
    OpenAIConfig,
    OpenAICapabilities,
    OpenAITokenManager,
    OpenAIErrorHandler
):
    """Base class for any provider using an OpenAI-compatible API.

    This includes:
    - Direct OpenAI API
    - OpenRouter
    - Any other OpenAI-compatible endpoint

    This class is a backward-compatible wrapper that delegates to
    specialized modules for each responsibility.
    """

    DEFAULT_HEADERS = {}
    FRIENDLY_NAME = "OpenAI Compatible"

    def __init__(self, api_key: str, base_url: str = None, **kwargs):
        """Initialize the provider with API key and optional base URL.

        Args:
            api_key: API key for authentication
            base_url: Base URL for the API endpoint
            **kwargs: Additional configuration options including timeout and max_retries
        """
        super().__init__(api_key, **kwargs)

        # Parse allowed models
        self.allowed_models = self._parse_allowed_models()

        # Store configuration
        self.max_retries = kwargs.get("max_retries", 2)
        self.organization = kwargs.get("organization")

        # Configure timeouts
        self.timeout_config = self._configure_timeouts(
            base_url=base_url,
            is_localhost_url=self._is_localhost_url(base_url),
            **kwargs
        )

        # Validate base URL
        if base_url:
            self._validate_base_url(base_url)

        # Warn if using external URL without authentication
        if base_url and not self._is_localhost_url(base_url) and not api_key:
            logger.warning(
                f"Using external URL '{base_url}' without API key. "
                "This may be insecure. Consider setting an API key for authentication."
            )

        # Initialize managers
        self._client_manager = OpenAIClientManager(
            api_key=api_key,
            base_url=base_url,
            organization=self.organization,
            timeout_config=self.timeout_config,
            max_retries=self.max_retries,
            default_headers=self.DEFAULT_HEADERS,
            test_transport=getattr(self, "_test_transport", None)
        )

        self._content_generator = OpenAIContentGenerator(
            client_manager=self._client_manager,
            capabilities_manager=self,
            token_manager=self,
            error_handler=self,
            friendly_name=self.FRIENDLY_NAME
        )

    # Delegate to client manager
    @property
    def client(self):
        """Get OpenAI client instance."""
        return self._client_manager.client

    # Delegate to content generator
    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: str = None,
        temperature: float = 0.3,
        max_output_tokens: int = None,
        images: list = None,
        **kwargs,
    ):
        """Generate content using the OpenAI-compatible API.

        This method delegates to OpenAIContentGenerator which handles
        the full content generation workflow including retries, streaming,
        and response processing.
        """
        return self._content_generator.generate_content(
            prompt=prompt,
            model_name=model_name,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            images=images,
            **kwargs
        )

    # Delegate to content generator for backward compatibility
    def safe_extract_output_text(self, response):
        """Safely extract output text from response."""
        return self._content_generator.safe_extract_output_text(response)

    # Expose helper methods from OpenAIConfig for backward compatibility
    def _parse_allowed_models(self):
        """Parse allowed models from environment variable."""
        provider_type = self.get_provider_type().value.upper()
        return OpenAIConfig.parse_allowed_models(provider_type)

    def _configure_timeouts(self, base_url=None, is_localhost_url=False, **kwargs):
        """Configure timeout settings."""
        return OpenAIConfig.configure_timeouts(
            base_url=base_url,
            is_localhost_url=is_localhost_url,
            **kwargs
        )

    def _is_localhost_url(self, base_url=None):
        """Check if URL is localhost."""
        if base_url is None:
            base_url = getattr(self._client_manager, "base_url", None)
        return OpenAIConfig.is_localhost_url(base_url)

    def _validate_base_url(self, base_url=None):
        """Validate base URL."""
        if base_url is None:
            base_url = getattr(self._client_manager, "base_url", None)
        OpenAIConfig.validate_base_url(base_url)

    # Abstract methods that must be implemented by subclasses

    def get_capabilities(self, model_name: str):
        """Get capabilities for a specific model.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_capabilities")

    def get_provider_type(self):
        """Get the provider type.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_provider_type")

    def validate_model_name(self, model_name: str) -> bool:
        """Validate if the model name is supported.

        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement validate_model_name")


# Backward compatibility: Re-export the main class
__all__ = ["OpenAICompatibleProvider"]
