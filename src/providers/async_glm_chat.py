"""Async GLM chat generation using asyncio.to_thread() wrapper around sync ZhipuAI SDK.

NOTE: zhipuai SDK does NOT have native async support (no AsyncZhipuAI).
We use asyncio.to_thread() to run the sync SDK in a thread pool.
"""

import asyncio
import logging
from typing import Any, Optional

from .base import ModelResponse, ProviderType
from .glm_chat import build_payload, generate_content  # Reuse sync implementation

logger = logging.getLogger(__name__)


async def generate_content_async(
    sdk_client: Any,  # ZhipuAI instance (sync client)
    http_client: Any,  # HTTP client for fallback
    prompt: str,
    model_name: str,
    system_prompt: Optional[str],
    temperature: float,
    max_output_tokens: Optional[int],
    use_sdk: bool = True,  # Whether SDK is available
    **kwargs
) -> ModelResponse:
    """Generate content asynchronously by wrapping sync ZhipuAI SDK with asyncio.to_thread().

    NOTE: This uses asyncio.to_thread() (Python 3.9+) to run the sync SDK in a thread pool.
    This is the recommended approach since zhipuai SDK doesn't have native async support.

    Args:
        sdk_client: ZhipuAI SDK client instance (sync)
        http_client: HTTP client for fallback
        prompt: User prompt
        model_name: Model name (already resolved)
        system_prompt: Optional system prompt
        temperature: Temperature value (already validated)
        max_output_tokens: Optional max output tokens
        use_sdk: Whether SDK is available and should be used
        **kwargs: Additional parameters (stream, tools, tool_choice, etc.)

    Returns:
        ModelResponse with generated content

    Raises:
        RuntimeError: If generation fails
    """
    logger.debug(f"Async GLM generate_content called with kwargs keys: {list(kwargs.keys())}")

    # CRITICAL FIX (2025-10-17): Pass http_client and use_sdk to sync generate_content
    # This fixes the signature mismatch error that was causing fallback to sync provider
    # Use asyncio.to_thread() to run sync generate_content in thread pool
    # This is the modern Python 3.9+ way to run blocking code in async context
    return await asyncio.to_thread(
        generate_content,
        sdk_client=sdk_client,
        http_client=http_client,
        prompt=prompt,
        model_name=model_name,
        system_prompt=system_prompt,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        use_sdk=use_sdk,
        **kwargs
    )
# That's it! The entire async implementation is just wrapping the sync function with asyncio.to_thread()
# No need to duplicate all the streaming/non-streaming logic - it's already in glm_chat.generate_content()

