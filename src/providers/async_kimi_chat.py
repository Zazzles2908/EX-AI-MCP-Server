"""Async Kimi chat functionality using openai.AsyncOpenAI."""

import logging
from typing import Any, Optional

from .base import ModelResponse, ProviderType
from .kimi_chat import prefix_hash  # Reuse hash function
from . import kimi_cache

# PHASE 2.2.3 (2025-10-21): Import async concurrent session manager
from src.utils.async_concurrent_session_manager import get_async_session_manager

logger = logging.getLogger(__name__)


async def chat_completions_create_async(
    client: Any,  # AsyncOpenAI instance
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    max_output_tokens: Optional[int] = None,
    cache_id: Optional[str] = None,
    reset_cache_ttl: bool = False,
    **kwargs
) -> ModelResponse:
    """Async wrapper for Kimi chat completions with caching support.
    
    Args:
        client: AsyncOpenAI client instance
        model: Model name
        messages: List of message dictionaries
        tools: Optional list of tools
        tool_choice: Optional tool choice
        temperature: Temperature value
        cache_id: Optional cache identifier for Moonshot context caching
        reset_cache_ttl: Whether to reset cache TTL
        **kwargs: Additional parameters (session_id, call_key, tool_name, etc.)
        
    Returns:
        ModelResponse with generated content and metadata
    """
    session_id = kwargs.get("_session_id") or kwargs.get("session_id")
    call_key = kwargs.get("_call_key") or kwargs.get("call_key")
    tool_name = kwargs.get("_tool_name") or "async_kimi_chat"
    msg_prefix_hash = prefix_hash(messages)
    
    # Build extra headers
    extra_headers = {"Msh-Trace-Mode": "on"}
    
    def _safe_set(hname: str, hval: str):
        try:
            if not hval:
                return
            hval_bytes = hval.encode('utf-8', errors='ignore')
            max_hdr_len = 4096
            if len(hval_bytes) > max_hdr_len:
                logger.warning(f"Async Kimi header {hname} too large ({len(hval_bytes)} bytes > {max_hdr_len}), dropping")
                return
            extra_headers[hname] = hval
        except Exception as e:
            logger.warning(f"Failed to set async Kimi header {hname}: {e}")
    
    if call_key:
        _safe_set("Idempotency-Key", str(call_key))
    
    # Add Moonshot context caching headers
    if cache_id:
        _safe_set("X-Msh-Context-Cache", cache_id)
        if reset_cache_ttl:
            _safe_set("X-Msh-Context-Cache-Reset-TTL", "3600")
        logger.info(f"🔑 Async Kimi context cache: {cache_id} (reset_ttl={reset_cache_ttl})")
    
    # Attach cached context token if available
    cache_token = None
    cache_attached = False
    if session_id and msg_prefix_hash:
        cache_token = kimi_cache.get_cache_token(session_id, tool_name, msg_prefix_hash)
        if cache_token:
            _safe_set("Msh-Context-Cache-Token", cache_token)
            cache_attached = "Msh-Context-Cache-Token" in extra_headers
            if cache_attached:
                logger.info(f"Async Kimi attach cache token suffix={cache_token[-6:]}")
    
    # Sanitize tools/tool_choice
    if tools is not None and not tools:
        tools = None
    if not tools:
        tool_choice = None

    # PHASE 2.1 (2025-10-21): Build API call parameters with max_tokens support
    api_params = {
        "model": model,
        "messages": messages,
        "tools": tools,
        "tool_choice": tool_choice,
        "temperature": temperature,
        "stream": False,
        "extra_headers": extra_headers,
    }

    # PHASE 2.1.1.1 (2025-10-21): Model-aware max_tokens handling
    from config import ENFORCE_MAX_TOKENS
    from .model_config import validate_max_tokens

    validated_max_tokens = validate_max_tokens(
        model_name=model,
        requested_max_tokens=max_output_tokens,
        input_tokens=0,  # TODO: Add token counting for input
        enforce_limits=ENFORCE_MAX_TOKENS
    )

    if validated_max_tokens is not None:
        api_params["max_tokens"] = validated_max_tokens
        logger.debug(f"Async Kimi API: Using max_tokens={validated_max_tokens} for model {model}")

    try:
        # CRITICAL: Use await for async API call
        response = await client.chat.completions.create(**api_params)

        # Parse response
        choice0 = response.choices[0] if response.choices else None
        if not choice0:
            raise RuntimeError("Async Kimi returned empty choices")

        message = choice0.message
        content_text = message.content or ""
        tool_calls = message.tool_calls

        # Extract usage
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        # PHASE 2.1.2 (2025-10-21): Check for truncation and log to Supabase
        try:
            from src.utils.truncation_detector import (
                check_truncation,
                should_log_truncation,
                format_truncation_event,
                log_truncation_to_supabase
            )

            # Convert response to dict for truncation check
            response_dict = response.model_dump() if hasattr(response, 'model_dump') else {}
            truncation_info = check_truncation(response_dict, model)

            if truncation_info.get('is_truncated'):
                logger.warning(f"⚠️ Truncated response detected for {model} (finish_reason=length)")

                # Log to Supabase for monitoring (backup/recovery - non-blocking)
                if should_log_truncation(truncation_info):
                    # Extract tool_name and conversation_id from context if available
                    conversation_id = kwargs.get('continuation_id')

                    # Format event for Supabase
                    truncation_event = format_truncation_event(
                        truncation_info,
                        tool_name=tool_name,
                        conversation_id=conversation_id
                    )

                    # Log asynchronously (non-blocking, failures are acceptable)
                    await log_truncation_to_supabase(truncation_event)
        except Exception as trunc_err:
            logger.debug(f"Truncation check error (non-critical): {trunc_err}")

        # Build metadata
        metadata = {
            "model": response.model,
            "id": response.id,
            "created": response.created,
            "finish_reason": choice0.finish_reason,
            "cache_attached": cache_attached,
            "cache_saved": False,  # Async version doesn't extract cache tokens from headers
        }
        
        # Add tool calls to metadata if present
        if tool_calls:
            metadata["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in tool_calls
            ]
        
        return ModelResponse(
            content=content_text,
            usage=usage,
            model_name=model,
            friendly_name="Kimi",
            provider=ProviderType.KIMI,
            metadata=metadata,
        )
        
    except Exception as e:
        logger.error(f"Async Kimi chat completion failed: {e}", exc_info=True)
        raise RuntimeError(f"Async Kimi chat completion failed: {e}") from e


async def chat_completions_create_async_with_continuation(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    max_output_tokens: Optional[int] = None,
    cache_id: Optional[str] = None,
    reset_cache_ttl: bool = False,
    enable_continuation: bool = True,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    **kwargs
) -> ModelResponse:
    """
    Async wrapper for Kimi chat completions with automatic continuation support.

    PHASE 2.1.3 (2025-10-21): Automatic Continuation

    This function automatically detects truncated responses and continues them
    until completion or max attempts reached.

    Args:
        client: AsyncOpenAI client instance
        model: Model name
        messages: List of message dictionaries
        tools: Optional list of tools
        tool_choice: Optional tool choice
        temperature: Temperature value
        max_output_tokens: Maximum output tokens per request
        cache_id: Optional cache identifier
        reset_cache_ttl: Whether to reset cache TTL
        enable_continuation: Whether to enable automatic continuation (default: True)
        max_continuation_attempts: Maximum continuation attempts (default: 3)
        max_total_tokens: Maximum cumulative tokens across continuations (default: 32000)
        **kwargs: Additional parameters

    Returns:
        ModelResponse with generated content and metadata
    """
    # Call the base function
    initial_response = await chat_completions_create_async(
        client,
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        cache_id=cache_id,
        reset_cache_ttl=reset_cache_ttl,
        **kwargs
    )

    # If continuation is disabled, return as-is
    if not enable_continuation:
        return initial_response

    # Check if response was truncated
    try:
        from src.utils.truncation_detector import check_truncation
        from src.utils.continuation_manager import get_continuation_manager

        # Convert ModelResponse to dict for truncation check
        response_dict = {
            'choices': [{
                'finish_reason': initial_response.metadata.get('finish_reason', 'stop'),
                'message': {'content': initial_response.content}
            }],
            'usage': initial_response.usage
        }

        # Check for truncation
        truncation_info = check_truncation(response_dict, model)

        if not truncation_info.get('is_truncated'):
            # Not truncated, return as-is
            return initial_response

        logger.info(f"🔄 Truncated response detected for {model}, starting continuation...")

        # Get continuation manager
        continuation_manager = get_continuation_manager()

        # Prepare provider callable
        async def provider_callable(cont_messages, **cont_kwargs):
            response = await chat_completions_create_async(
                client,
                model=model,
                messages=cont_messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                cache_id=cache_id,
                reset_cache_ttl=reset_cache_ttl,
                **cont_kwargs
            )
            # Convert ModelResponse to dict for continuation manager
            return {
                'choices': [{
                    'finish_reason': response.metadata.get('finish_reason', 'stop'),
                    'message': {'content': response.content}
                }],
                'usage': response.usage
            }

        # Continue the response
        continuation_result = await continuation_manager.continue_response_async(
            original_messages=messages,
            initial_response=response_dict,
            provider_callable=provider_callable,
            model=model,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

        # Merge the continuation result back into the ModelResponse
        if continuation_result.complete_response:
            initial_response.content = continuation_result.complete_response
            initial_response.metadata['continuation'] = {
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


async def chat_completions_create_async_with_session(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    max_output_tokens: Optional[int] = None,
    cache_id: Optional[str] = None,
    reset_cache_ttl: bool = False,
    enable_continuation: bool = True,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    timeout_seconds: Optional[float] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Async session-managed wrapper for Kimi chat with automatic continuation support.

    PHASE 2.2.3 (2025-10-21): Concurrent Request Handling (Async)
    Uses AsyncConcurrentSessionManager for async request isolation.

    This function wraps chat_completions_create_async_with_continuation in a managed
    async session to enable concurrent async request handling without blocking.
    Each request gets its own isolated session with timeout handling and lifecycle tracking.

    Args:
        client: AsyncOpenAI client instance
        model: Model name
        messages: List of message dictionaries
        tools: Optional list of tools
        tool_choice: Optional tool choice
        temperature: Temperature value
        max_output_tokens: Maximum output tokens
        cache_id: Optional cache identifier for Moonshot context caching
        reset_cache_ttl: Whether to reset cache TTL
        enable_continuation: Whether to enable automatic continuation
        max_continuation_attempts: Maximum continuation attempts
        max_total_tokens: Maximum total tokens across continuations
        timeout_seconds: Optional timeout override (default: 30s)
        request_id: Optional request ID (generated if not provided)
        **kwargs: Additional parameters

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, metadata,
        and session context (session_id, request_id, duration_seconds)
    """
    session_manager = await get_async_session_manager(default_timeout=timeout_seconds or 30.0)

    async def _execute_async_kimi_chat():
        """Internal async function to execute Kimi chat within session."""
        return await chat_completions_create_async_with_continuation(
            client,
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            cache_id=cache_id,
            reset_cache_ttl=reset_cache_ttl,
            enable_continuation=enable_continuation,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

    # Execute within managed async session with automatic session context addition
    return await session_manager.execute_with_session(
        provider="kimi",
        model=model,
        func=_execute_async_kimi_chat,
        request_id=request_id,
        timeout_seconds=timeout_seconds,
        add_session_context=True
    )


__all__ = [
    "chat_completions_create_async",
    "chat_completions_create_async_with_continuation",
    "chat_completions_create_async_with_session"
]

