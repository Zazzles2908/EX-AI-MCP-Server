"""
OpenAI Compatible Provider - Client Management Module

Handles OpenAI client initialization and management for compatible providers.
Provides lazy initialization with security checks, timeout configuration,
and proxy avoidance.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management (this file)
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class
"""

import logging
import os
from typing import Optional

from openai import OpenAI

from src.daemon.error_handling import log_error, ErrorCode

logger = logging.getLogger(__name__)


class OpenAIClientManager:
    """
    Manages OpenAI client initialization and configuration.

    Handles:
    - Lazy client initialization
    - Security checks and validation
    - Timeout configuration
    - Proxy avoidance
    - Test transport injection
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        timeout_config: Optional[object] = None,
        max_retries: int = 2,
        default_headers: Optional[dict] = None,
        test_transport: Optional[object] = None
    ):
        """
        Initialize client manager.

        Args:
            api_key: API key for authentication
            base_url: Optional base URL for API
            organization: Optional organization ID
            timeout_config: Optional httpx.Timeout object
            max_retries: Maximum retry attempts
            default_headers: Optional default headers
            test_transport: Optional test transport for testing
        """
        self.api_key = api_key
        self.base_url = base_url
        self.organization = organization
        self.timeout_config = timeout_config
        self.max_retries = max_retries
        self.default_headers = default_headers or {}
        self.test_transport = test_transport
        self._client = None

    @property
    def client(self) -> OpenAI:
        """
        Lazy initialization of OpenAI client with security checks.

        Returns:
            Configured OpenAI client

        Raises:
            Exception: If client initialization fails
        """
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> OpenAI:
        """
        Create and configure OpenAI client.

        Uses a layered approach with fallbacks:
        1. Custom httpx client with timeout config
        2. Minimal client with basic config

        Returns:
            Configured OpenAI client

        Raises:
            Exception: If all initialization attempts fail
        """
        # Temporarily disable proxy environment variables
        original_env = {}
        proxy_env_vars = [
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
            "http_proxy", "https_proxy", "all_proxy"
        ]

        for var in proxy_env_vars:
            if var in os.environ:
                original_env[var] = os.environ[var]
                del os.environ[var]

        try:
            # Create a custom httpx client to avoid proxy conflicts
            timeout_config = (
                self.timeout_config if self.timeout_config else
                self._get_default_timeout()
            )

            # Check for test transport injection
            if self.test_transport:
                # Use custom transport for testing (HTTP recording/replay)
                import httpx
                http_client = httpx.Client(
                    transport=self.test_transport,
                    timeout=timeout_config,
                    follow_redirects=True,
                )
            else:
                # Normal production client
                import httpx
                http_client = httpx.Client(
                    timeout=timeout_config,
                    follow_redirects=True,
                )

            # Build client kwargs
            client_kwargs = {
                "api_key": self.api_key,
                "http_client": http_client,
                "max_retries": self.max_retries,
            }

            if self.base_url:
                client_kwargs["base_url"] = self.base_url

            if self.organization:
                client_kwargs["organization"] = self.organization

            if self.default_headers:
                client_kwargs["default_headers"] = self.default_headers.copy()

            logging.debug(
                f"OpenAI client initialized with custom httpx client, "
                f"timeout: {timeout_config}, max_retries: {self.max_retries}"
            )

            # Create OpenAI client with custom httpx client
            return OpenAI(**client_kwargs)

        except Exception as e:
            # If all else fails, try absolute minimal client
            logger.warning(
                f"Failed to create client with custom httpx, "
                f"falling back to minimal config: {e}",
                exc_info=True
            )
            try:
                minimal_kwargs = {
                    "api_key": self.api_key,
                    "max_retries": self.max_retries,
                }
                if self.base_url:
                    minimal_kwargs["base_url"] = self.base_url
                return OpenAI(**minimal_kwargs)
            except Exception as fallback_error:
                log_error(ErrorCode.INTERNAL_ERROR, f"Even minimal OpenAI client creation failed: {fallback_error}", exc_info=True)
                raise
        finally:
            # Restore original proxy environment variables
            for var, value in original_env.items():
                os.environ[var] = value

    @staticmethod
    def _get_default_timeout() -> object:
        """Get default timeout configuration."""
        import httpx
        return httpx.Timeout(30.0)

    @staticmethod
    def sanitize_for_logging(params: dict) -> dict:
        """
        Sanitize parameters for safe logging.

        Removes or masks sensitive information like API keys.

        Args:
            params: Parameters to sanitize

        Returns:
            Sanitized parameters dictionary
        """
        sanitized = {}
        sensitive_keys = {"api_key", "authorization", "token", "key"}

        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***" if value else None
            else:
                sanitized[key] = value

        return sanitized
