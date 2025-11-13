"""
OpenAI Compatible Provider - Token Management Module

Handles token counting, usage extraction, and parameter validation.
Provides layered token counting approach and usage statistics extraction.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management (this file)
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation
- openai_compatible.py: Main provider class
"""

import logging
from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    pass

from src.daemon.error_handling import log_error, ErrorCode

logger = logging.getLogger(__name__)


class OpenAITokenManager:
    """
    Manages token counting and usage extraction for OpenAI-compatible providers.

    Handles:
    - Token counting (multiple strategies)
    - Usage statistics extraction
    - Parameter validation
    """

    def count_tokens(self, text: str, model_name: str) -> int:
        """
        Count tokens for the given text.

        Uses a layered approach:
        1. Try provider-specific token counting endpoint
        2. Try tiktoken for known model families
        3. Fall back to character-based estimation

        Args:
            text: Text to count tokens for
            model_name: Model name for tokenizer selection

        Returns:
            Estimated token count
        """
        # 1. Check if provider has a remote token counting endpoint
        if hasattr(self, "count_tokens_remote"):
            try:
                return self.count_tokens_remote(text, model_name)
            except Exception as e:
                logging.debug(f"Remote token counting failed: {e}")

        # 2. Try tiktoken for known models
        try:
            import tiktoken

            # Try to get encoding for the specific model
            try:
                encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")

            return len(encoding.encode(text))

        except (ImportError, Exception) as e:
            logging.debug(f"Tiktoken not available or failed: {e}")

        # 3. Fall back to character-based estimation
        logging.warning(
            f"No specific tokenizer available for '{model_name}'. "
            "Using character-based estimation (~4 chars per token)."
        )
        return len(text) // 4

    def extract_usage(self, response) -> Dict[str, int]:
        """
        Extract token usage from OpenAI response.

        Args:
            response: OpenAI API response object

        Returns:
            Dictionary with usage statistics
        """
        usage = {}

        if hasattr(response, "usage") and response.usage:
            # Safely extract token counts with None handling
            usage["input_tokens"] = getattr(response.usage, "prompt_tokens", 0) or 0
            usage["output_tokens"] = getattr(response.usage, "completion_tokens", 0) or 0
            usage["total_tokens"] = getattr(response.usage, "total_tokens", 0) or 0

        return usage

    def process_image(self, image_path: str) -> Dict:
        """
        Process image for multimodal input.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with processed image data

        Raises:
            FileNotFoundError: If image file doesn't exist
            ValueError: If image format is unsupported
        """
        import base64
        import mimetypes
        import os

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type or not mime_type.startswith("image/"):
            raise ValueError(f"Unsupported image format: {image_path}")

        # Read and encode image
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")

            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{image_data}"
                }
            }
        except Exception as e:
            log_error(ErrorCode.INTERNAL_ERROR, f"Failed to process image {image_path}: {e}", exc_info=True)
            raise
