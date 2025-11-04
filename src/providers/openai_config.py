"""
OpenAI Compatible Provider - Configuration Module

Handles configuration, validation, and security for OpenAI-compatible providers.
Includes URL validation, timeout configuration, and model allow-list parsing.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation (this file)
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class
"""

import ipaddress
import logging
import os
from typing import Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class OpenAIConfig:
    """
    Manages configuration and validation for OpenAI-compatible providers.

    Handles:
    - URL validation and security
    - Timeout configuration
    - Model allow-list parsing
    - Base URL validation
    """

    @staticmethod
    def parse_allowed_models(provider_type_value: str) -> Optional[Set[str]]:
        """
        Parse allowed models from environment variable.

        Args:
            provider_type_value: Provider type value (e.g., 'OPENROUTER', 'OPENAI')

        Returns:
            Set of allowed model names (lowercase) or None if not configured
        """
        env_var = f"{provider_type_value}_ALLOWED_MODELS"
        models_str = os.getenv(env_var, "")

        if models_str:
            # Parse and normalize to lowercase for case-insensitive comparison
            models = {m.strip().lower() for m in models_str.split(",") if m.strip()}
            if models:
                logging.info(f"Configured allowed models: {sorted(models)}")
                return models

        # Log info if no allow-list configured for proxy providers
        if provider_type_value not in ["GOOGLE", "OPENAI"]:
            logging.info(
                f"Model allow-list not configured - all models permitted. "
                f"To restrict access, set {env_var} with comma-separated model names."
            )

        return None

    @staticmethod
    def configure_timeouts(
        base_url: Optional[str],
        is_localhost_url: bool,
        **kwargs
    ) -> object:
        """
        Configure timeout settings based on provider type.

        Custom URLs and local models need longer timeouts due to:
        - Network latency on local networks
        - Extended thinking models taking longer
        - Local inference being slower than cloud APIs

        Args:
            base_url: API base URL
            is_localhost_url: Whether URL points to localhost
            **kwargs: Override timeout values

        Returns:
            httpx.Timeout object with configured timeouts
        """
        import httpx

        # Default timeouts - more generous for custom/local endpoints
        default_connect = 30.0  # 30 seconds for connection
        default_read = 600.0  # 10 minutes for reading
        default_write = 600.0  # 10 minutes for writing
        default_pool = 600.0  # 10 minutes for pool

        # For custom/local URLs, use even longer timeouts
        if is_localhost_url:
            default_connect = 60.0  # 1 minute for local connections
            default_read = 1800.0  # 30 minutes for local models
            default_write = 1800.0  # 30 minutes for local models
            default_pool = 1800.0  # 30 minutes for local models
            logging.info(f"Using extended timeouts for local endpoint: {base_url}")
        elif base_url:
            default_connect = 45.0  # 45 seconds for custom remote endpoints
            default_read = 900.0  # 15 minutes for custom remote endpoints
            default_write = 900.0  # 15 minutes for custom remote endpoints
            default_pool = 900.0  # 15 minutes for custom remote endpoints
            logging.info(f"Using extended timeouts for custom endpoint: {base_url}")

        # Allow override via kwargs or environment variables
        connect_timeout = kwargs.get(
            "connect_timeout",
            float(os.getenv("CUSTOM_CONNECT_TIMEOUT", default_connect))
        )
        read_timeout = kwargs.get(
            "read_timeout",
            float(os.getenv("CUSTOM_READ_TIMEOUT", default_read))
        )
        write_timeout = kwargs.get(
            "write_timeout",
            float(os.getenv("CUSTOM_WRITE_TIMEOUT", default_write))
        )
        pool_timeout = kwargs.get(
            "pool_timeout",
            float(os.getenv("CUSTOM_POOL_TIMEOUT", default_pool))
        )

        timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=write_timeout,
            pool=pool_timeout
        )

        logging.debug(
            f"Configured timeouts - Connect: {connect_timeout}s, "
            f"Read: {read_timeout}s, Write: {write_timeout}s, Pool: {pool_timeout}s"
        )

        return timeout

    @staticmethod
    def is_localhost_url(base_url: Optional[str]) -> bool:
        """
        Check if the base URL points to localhost or local network.

        Args:
            base_url: URL to check

        Returns:
            True if URL is localhost or local network, False otherwise
        """
        if not base_url:
            return False

        try:
            parsed = urlparse(base_url)
            hostname = parsed.hostname

            # Check for common localhost patterns
            if hostname in ["localhost", "127.0.0.1", "::1"]:
                return True

            # Check for private network ranges (local network)
            if hostname:
                try:
                    ip = ipaddress.ip_address(hostname)
                    return ip.is_private or ip.is_loopback
                except ValueError:
                    # Not an IP address, might be a hostname
                    pass

            return False
        except Exception as e:
            logger.debug(f"Failed to check if URL is localhost: {e}")
            return False

    @staticmethod
    def validate_base_url(base_url: Optional[str]) -> None:
        """
        Validate base URL for security (SSRF protection).

        Args:
            base_url: URL to validate

        Raises:
            ValueError: If URL is invalid or potentially unsafe
        """
        if not base_url:
            return

        try:
            parsed = urlparse(base_url)

            # Check URL scheme - only allow http/https
            if parsed.scheme not in ("http", "https"):
                raise ValueError(
                    f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed."
                )

            # Check hostname exists
            if not parsed.hostname:
                raise ValueError("URL must include a hostname")

            # Check port is valid (if specified)
            port = parsed.port
            if port is not None and (port < 1 or port > 65535):
                raise ValueError(
                    f"Invalid port number: {port}. Must be between 1 and 65535."
                )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid base URL '{base_url}': {str(e)}")
