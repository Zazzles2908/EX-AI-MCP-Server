"""Async Kimi chat functionality using openai.AsyncOpenAI."""

import logging
from typing import Any, Optional

from .base import ModelResponse, ProviderType
from .kimi_chat import prefix_hash  # Reuse hash function
from . import kimi_cache

logger = logging.getLogger(__name__)


async def chat_completions_create_async(
    client: Any,  # AsyncOpenAI instance
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
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
    
    try:
        # CRITICAL: Use await for async API call
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            stream=False,
            extra_headers=extra_headers,
        )
        
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

