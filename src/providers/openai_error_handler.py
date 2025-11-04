"""
OpenAI Compatible Provider - Error Handling Module

Handles error classification, retry logic, and image processing.
Provides methods to determine if errors are retryable and handle common error cases.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling (this file)
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class OpenAIErrorHandler:
    """
    Handles error classification and retry logic for OpenAI-compatible providers.

    Provides methods to:
    - Determine if errors are retryable
    - Classify error types
    - Extract structured error information
    """

    def is_error_retryable(self, error: Exception) -> bool:
        """
        Determine if an error should be retried based on structured error codes.

        Uses OpenAI API error structure instead of text pattern matching for reliability.

        Args:
            error: Exception from OpenAI API call

        Returns:
            True if error should be retried, False otherwise
        """
        error_str = str(error).lower()

        # Check for 429 errors first - these need special handling
        if "429" in error_str:
            # 429 errors (rate limiting) are always retryable
            logger.info(f"Rate limit error (429) detected - will retry")
            return True

        # Check for 5xx server errors
        if "500" in error_str or "502" in error_str or "503" in error_str or "504" in error_str:
            # 5xx errors indicate server issues - retryable
            logger.info(f"Server error detected ({error_str[:50]}) - will retry")
            return True

        # Check for network/connection errors
        if any(term in error_str for term in [
            "connection",
            "network",
            "timeout",
            "unreachable",
            "reset"
        ]):
            # Network errors are retryable
            logger.info(f"Network error detected ({error_str[:50]}) - will retry")
            return True

        # Check for specific OpenAI error codes in the error message
        # This is a fallback for when we can't access structured error data
        error_type = None
        error_code = None

        # Parse structured error from OpenAI API response
        if hasattr(error, "response"):
            response = error.response
            if hasattr(response, "json"):
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_type = error_data.get("type")
                        error_code = error_data.get("code")
                        error_message = error_data.get("message", "")

                        logger.info(
                            f"Parsed structured error: type={error_type}, "
                            f"code={error_code}, message={error_message[:100]}"
                        )

                        # Check for retryable error types
                        if error_type == "rate_limit_exceeded":
                            logger.info("Rate limit exceeded - will retry")
                            return True
                        elif error_type == "insufficient_quota":
                            logger.warning("Insufficient quota - will not retry")
                            return False
                        elif error_type == "invalid_request_error":
                            # Check specific codes
                            if error_code in ["context_length_exceeded", "invalid_model"]:
                                logger.warning(f"Invalid request error ({error_code}) - will not retry")
                                return False
                        elif error_type == "authentication_error":
                            logger.warning("Authentication error - will not retry")
                            return False
                        elif error_type == "permission_error":
                            logger.warning("Permission error - will not retry")
                            return False

                except Exception:
                    # Failed to parse error data
                    pass

        # Check for specific error codes in the error string
        if "rate_limit" in error_str or "too many requests" in error_str:
            logger.info("Rate limit detected in error string - will retry")
            return True

        if "context_length" in error_str or "too many tokens" in error_str:
            logger.warning("Context length exceeded - will not retry")
            return False

        if "invalid_model" in error_str or "model not found" in error_str:
            logger.warning("Invalid model - will not retry")
            return False

        if "authentication" in error_str or "unauthorized" in error_str:
            logger.warning("Authentication error - will not retry")
            return False

        if "permission" in error_str or "forbidden" in error_str:
            logger.warning("Permission error - will not retry")
            return False

        if "quota" in error_str or "billing" in error_str:
            logger.warning("Quota/billing error - will not retry")
            return False

        # Default: don't retry unknown errors to be safe
        logger.warning(f"Unknown error type - will not retry: {error_str[:100]}")
        return False

    def classify_error(self, error: Exception) -> str:
        """
        Classify error into a general category.

        Args:
            error: Exception to classify

        Returns:
            Error category string (rate_limit, auth, validation, server, network, unknown)
        """
        error_str = str(error).lower()

        if "429" in error_str or "rate_limit" in error_str or "too many requests" in error_str:
            return "rate_limit"
        elif "401" in error_str or "403" in error_str or "authentication" in error_str or "unauthorized" in error_str:
            return "auth"
        elif "400" in error_str or "invalid" in error_str or "validation" in error_str:
            return "validation"
        elif "500" in error_str or "502" in error_str or "503" in error_str or "server" in error_str:
            return "server"
        elif "connection" in error_str or "network" in error_str or "timeout" in error_str:
            return "network"
        else:
            return "unknown"
