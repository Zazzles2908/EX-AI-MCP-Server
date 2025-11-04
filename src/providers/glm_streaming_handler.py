"""
GLM Streaming Handler

Streaming implementations for GLM provider.
Handles both SDK streaming and HTTP streaming with continuation support.

This is part of the Phase 3 refactoring that split the large glm_chat.py
into focused modules:
- glm_provider.py: Core chat functions
- glm_streaming_handler.py: Streaming implementations (this file)
- glm_tool_processor.py: Tool call processing
"""

import json
import logging
import os
import time
from typing import Any, Optional, Callable

from .base import ModelResponse, ProviderType

# Import monitoring utilities
from utils.monitoring import record_glm_event
from utils.timezone_helper import log_timestamp

# Import circuit breaker
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

logger = logging.getLogger(__name__)


def chat_completions_create_with_continuation(
    prompt: str,
    *,
    sdk_client: Any,
    model: str,
    system_prompt: Optional[str] = None,
    messages: Optional[list[dict]] = None,
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    on_chunk_callback: Optional[Callable[[str], None]] = None,
    stream_timeout: float = 300.0,
    **kwargs
) -> dict:
    """
    Chat completions with automatic continuation support.

    Handles long responses that exceed max_output_tokens by automatically
    continuing the conversation and merging results.

    Args:
        prompt: User prompt
        sdk_client: ZhipuAI SDK client
        model: Model name
        system_prompt: Optional system prompt
        messages: Optional pre-built messages (alternative to prompt)
        tools: Optional tools
        tool_choice: Optional tool choice
        temperature: Temperature
        max_output_tokens: Optional max tokens per response
        max_continuation_attempts: Max continuation attempts
        max_total_tokens: Max total tokens across all continuations
        on_chunk_callback: Optional streaming callback
        stream_timeout: Timeout for streaming operations
        **kwargs: Additional parameters

    Returns:
        Dictionary with content, usage, metadata including continuation info
    """
    start_time = time.time()

    try:
        # Import continuation manager
        from src.utils.response_continuation import (
            ContinuationManager,
            ContinuationResult
        )

        # Determine message format
        if messages:
            # Use provided messages
            chat_messages = messages
        else:
            # Build messages from prompt
            chat_messages = []
            if system_prompt:
                chat_messages.append({"role": "system", "content": system_prompt})
            chat_messages.append({"role": "user", "content": prompt})

        # Create continuation manager
        continuation_manager = ContinuationManager(
            provider="glm",
            sdk_client=sdk_client,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tools=tools,
            tool_choice=tool_choice,
            stream_timeout=stream_timeout,
            on_chunk_callback=on_chunk_callback,
            **kwargs
        )

        # Create provider callable
        def provider_callable(msgs, **prov_kwargs):
            """Provider-specific chat completion."""
            payload = {
                "model": model,
                "messages": msgs,
                "temperature": temperature,
            }

            if max_output_tokens:
                payload["max_tokens"] = max_output_tokens

            if tools:
                payload["tools"] = tools

            if tool_choice:
                payload["tool_choice"] = tool_choice

            # Add any additional kwargs
            for key, value in prov_kwargs.items():
                if key not in payload:
                    payload[key] = value

            # Make request
            result = sdk_client.chat.completions.create(**payload)

            # Extract content
            content = result.choices[0].message.content if result.choices else ""
            usage = dict(result.usage) if hasattr(result, 'usage') and result.usage else {}

            return {
                "content": content,
                "usage": usage,
                "raw": result
            }

        # Make initial request
        logger.debug(f"GLM continuation request: model={model}, max_tokens={max_output_tokens}")

        initial_result = provider_callable(chat_messages)
        initial_response = {
            "provider": "glm",
            "model": model,
            "content": initial_result["content"],
            "usage": initial_result.get("usage", {}),
            "metadata": {
                "model": model,
                "streamed": False,
                "continuation": {
                    "enabled": False,
                }
            },
            "raw": initial_result["raw"]
        }

        # Check if continuation is needed
        usage = initial_result.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)

        if max_total_tokens and total_tokens < max_total_tokens:
            logger.debug(f"Initial response complete: {total_tokens} tokens")
            return initial_response

        # Log initial completion
        ai_response_time_ms = int((time.time() - start_time) * 1000)
        initial_response["metadata"]["ai_response_time_ms"] = ai_response_time_ms

        # Continue the response
        continuation_result = continuation_manager.continue_response_sync(
            original_messages=chat_messages,
            initial_response=initial_result,
            provider_callable=provider_callable,
            model=model,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

        # Merge the continuation result back into the response format
        if continuation_result.complete_response:
            initial_response['content'] = continuation_result.complete_response
            initial_response['metadata']['continuation'] = {
                'enabled': True,
                'attempts': continuation_result.attempts_made,
                'total_tokens': continuation_result.total_tokens_used,
                'is_complete': continuation_result.is_complete,
                'was_truncated': continuation_result.was_truncated,
                'error': continuation_result.error_message
            }
            logger.info(
                f"✅ Continuation complete: {continuation_result.attempts_made} attempts, "
                f"{continuation_result.total_tokens_used} tokens"
            )

        return initial_response

    except Exception as cont_err:
        logger.warning(f"Continuation failed (non-critical): {cont_err}")
        # Return original response if continuation fails
        return initial_response


def chat_completions_create_with_session(
    prompt: str,
    *,
    system_prompt: Optional[str] = None,
    model: str = "glm-4.5-flash",
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    tools: Optional[list[dict]] = None,
    tool_choice: Optional[str | dict] = None,
    use_websearch: bool = False,
    enable_continuation: bool = True,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    timeout_seconds: Optional[float] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Session-managed wrapper for GLM chat with automatic continuation support.

    This function wraps chat_completions_create_with_continuation in a managed session
    to enable concurrent request handling without blocking.

    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model: Model name (default: glm-4.5-flash)
        temperature: Temperature value
        max_output_tokens: Maximum output tokens
        tools: Optional list of tools
        tool_choice: Optional tool choice
        use_websearch: Whether to enable web search
        enable_continuation: Whether to enable automatic continuation
        max_continuation_attempts: Maximum continuation attempts
        max_total_tokens: Maximum total tokens across continuations
        timeout_seconds: Optional timeout override (default: GLM_SESSION_TIMEOUT env var)
        request_id: Optional request ID (generated if not provided)
        **kwargs: Additional parameters

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, metadata,
        and session context (session_id, request_id, duration_seconds)
    """
    # Use GLM_SESSION_TIMEOUT from environment
    default_timeout = float(os.getenv("GLM_SESSION_TIMEOUT", "30"))
    enforce_timeout = os.getenv("ENFORCE_SESSION_TIMEOUT", "true").lower() == "true"

    # Import session manager
    from src.utils.concurrent_session_manager import get_session_manager

    session_manager = get_session_manager(default_timeout=timeout_seconds or default_timeout)

    def _execute_glm_chat():
        """Internal function to execute GLM chat within session."""
        return chat_completions_create_with_continuation(
            prompt,
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            tools=tools,
            tool_choice=tool_choice,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

    # Execute with session management
    result = session_manager.execute_with_session(
        provider="glm",
        request_callable=_execute_glm_chat,
        enforce_timeout=enforce_timeout
    )

    # Add session metadata
    if isinstance(result, dict):
        result.setdefault("metadata", {})["session"] = {
            "session_id": session_manager.session_id,
            "request_id": request_id,
            "duration_seconds": session_manager.duration_seconds,
        }

    return result
