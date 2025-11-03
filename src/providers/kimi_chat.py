"""Kimi chat functionality with cache token integration."""

import hashlib
import logging
import os
import time
from typing import Any, Optional

from . import kimi_cache

# PHASE 3 (2025-10-18): Import monitoring utilities
from utils.monitoring import record_kimi_event
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-18): Import circuit breaker for resilience
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

# PHASE 2.2.3 (2025-10-21): Import concurrent session manager
from src.utils.concurrent_session_manager import get_session_manager

logger = logging.getLogger(__name__)


def prefix_hash(messages: list[dict[str, Any]]) -> str:
    """Generate hash of message prefix for cache key.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        SHA256 hash of message prefix
    """
    try:
        # Serialize a stable prefix of messages (roles + first 2k chars)
        parts: list[str] = []
        for m in messages[:6]:  # limit to first few messages
            role = str(m.get("role", ""))
            content = str(m.get("content", ""))[:2048]
            parts.append(role + "\n" + content + "\n")
        joined = "\n".join(parts)
        return hashlib.sha256(joined.encode("utf-8", errors="ignore")).hexdigest()
    except Exception as e:
        logger.warning(f"Failed to generate call key hash from messages: {e}")
        # Continue - empty call key means no caching/deduplication, but request will still work
        return ""


def chat_completions_create(
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
    thinking_enabled: bool = False,  # CRITICAL FIX (2025-11-02): Enable thinking mode for kimi-thinking-preview
    **kwargs
) -> dict:
    """Wrapper that injects idempotency and Kimi context-cache headers, captures cache token, and returns normalized dict.

    Args:
        client: OpenAI-compatible client instance
        model: Model name
        messages: List of message dictionaries
        tools: Optional list of tools
        tool_choice: Optional tool choice
        temperature: Temperature value
        cache_id: Optional cache identifier for Moonshot context caching
        reset_cache_ttl: Whether to reset cache TTL (keeps cache alive)
        **kwargs: Additional parameters (session_id, call_key, tool_name, etc.)

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, and metadata
    """
    session_id = kwargs.get("_session_id") or kwargs.get("session_id")
    call_key = kwargs.get("_call_key") or kwargs.get("call_key")
    tool_name = kwargs.get("_tool_name") or "kimi_chat_with_tools"
    msg_prefix_hash = prefix_hash(messages)

    # Build extra headers (with defensive caps to avoid 400 'Request Header or Cookie Too Large')
    extra_headers = {"Msh-Trace-Mode": "on"}
    try:
        max_hdr_len = int(os.getenv("KIMI_MAX_HEADER_LEN", "4096"))
    except Exception as e:
        logger.debug(f"Failed to parse KIMI_MAX_HEADER_LEN env variable: {e}")
        # Continue with default - header length limit will be 4096
        max_hdr_len = 4096

    def _safe_set(hname: str, hval: str):
        try:
            if not hval:
                return
            # UTF-8 safe length check (count bytes, not characters)
            hval_bytes = hval.encode('utf-8', errors='ignore')
            if max_hdr_len > 0 and len(hval_bytes) > max_hdr_len:
                # Drop overly large headers rather than sending
                logger.warning("Kimi header %s too large (%s bytes > %s), dropping", hname, len(hval_bytes), max_hdr_len)
                return
            extra_headers[hname] = hval
        except (TypeError, ValueError, UnicodeError) as e:
            logger.warning(f"Failed to set header {hname}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error setting header {hname}: {e}")

    if call_key:
        _safe_set("Idempotency-Key", str(call_key))

    # Add Moonshot context caching headers if cache_id provided
    if cache_id:
        _safe_set("X-Msh-Context-Cache", cache_id)
        if reset_cache_ttl:
            _safe_set("X-Msh-Context-Cache-Reset-TTL", "3600")
        logger.info(f"🔑 Kimi context cache: {cache_id} (reset_ttl={reset_cache_ttl})")

    # ❌ REMOVED (2025-11-03): X-Moonshot-Thinking header DOES NOT EXIST
    # External AI fact-check confirmed: No such header in Moonshot API docs
    # Thinking mode works automatically with kimi-thinking-preview model
    # Field name is 'reasoning_content' (returned automatically, no header needed)

    # Attach cached context token if available (legacy cache system)
    cache_token = None
    cache_attached = False
    if session_id and msg_prefix_hash:
        cache_token = kimi_cache.get_cache_token(session_id, tool_name, msg_prefix_hash)
        if cache_token:
            _safe_set("Msh-Context-Cache-Token", cache_token)
            cache_attached = "Msh-Context-Cache-Token" in extra_headers
            if cache_attached:
                logger.info("Kimi attach cache token suffix=%s", cache_token[-6:])

    # Sanitize tools/tool_choice per Moonshot tool-use: do not send tool_choice when no tools
    try:
        if tools is not None and not tools:
            tools = None
        if not tools:
            tool_choice = None
    except Exception as e:
        logger.warning(f"Failed to sanitize tools/tool_choice (model: {model}): {e}")
        # Continue - tools/tool_choice will be sent as-is, API may reject if invalid

    # Call with raw response to capture headers when possible
    content_text = ""
    raw_payload = None
    cache_saved = False

    # PHASE 3 (2025-10-18): Monitor API call start
    start_time = time.time()
    request_size = len(str(messages).encode('utf-8'))
    error = None
    response_size = 0
    total_tokens = 0
    finish_reason = "unknown"

    # PHASE 1 (2025-10-18): Apply circuit breaker protection
    breaker = circuit_breaker_manager.get_breaker('kimi')

    try:
        api = getattr(client.chat.completions, "with_raw_response", None)
        if api:
            # Build API call parameters
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
                logger.debug(f"Kimi API: Using max_tokens={validated_max_tokens} for model {model}")

            # PHASE 1 (2025-10-18): Wrap API call with circuit breaker
            @breaker
            def _kimi_api_call():
                return api.create(**api_params)

            raw = _kimi_api_call()
            # Parse JSON body
            try:
                raw_payload = raw.parse()
            except Exception as e:
                logger.debug(f"Failed to parse raw response, falling back to http_response attribute: {e}")
                # Continue - fallback to http_response attribute
                raw_payload = getattr(raw, "http_response", None)

            # PHASE 2.1.2 (2025-10-21): Check for truncation and log to Supabase
            try:
                from src.utils.truncation_detector import (
                    check_truncation,
                    should_log_truncation,
                    format_truncation_event,
                    log_truncation_to_supabase_sync
                )
                if raw_payload:
                    payload_dict = raw_payload.model_dump() if hasattr(raw_payload, 'model_dump') else (raw_payload if isinstance(raw_payload, dict) else {})
                    truncation_info = check_truncation(payload_dict, model)

                    if truncation_info.get('is_truncated'):
                        logger.warning(f"⚠️ Truncated response detected for {model} (finish_reason=length)")

                        # Log to Supabase for monitoring (backup/recovery - non-blocking)
                        if should_log_truncation(truncation_info):
                            # Extract tool_name and conversation_id from context if available
                            tool_name = kwargs.get('tool_name')
                            conversation_id = kwargs.get('continuation_id')

                            # Format event for Supabase
                            truncation_event = format_truncation_event(
                                truncation_info,
                                tool_name=tool_name,
                                conversation_id=conversation_id
                            )

                            # Log synchronously (non-blocking, failures are acceptable)
                            log_truncation_to_supabase_sync(truncation_event)
            except Exception as trunc_err:
                logger.debug(f"Truncation check error (non-critical): {trunc_err}")
            
            # Extract headers
            try:
                hdrs = getattr(raw, "http_response", None)
                hdrs = getattr(hdrs, "headers", None) or {}
                token_saved = None
                for k, v in hdrs.items():
                    lk = (k.lower() if isinstance(k, str) else str(k).lower())
                    if lk in ("msh-context-cache-token-saved", "msh_context_cache_token_saved"):
                        token_saved = v
                        break
                if token_saved and session_id and msg_prefix_hash:
                    kimi_cache.save_cache_token(session_id, tool_name, msg_prefix_hash, token_saved)
                    cache_saved = True
                else:
                    cache_saved = False
            except (AttributeError, KeyError, TypeError) as e:
                logger.debug(f"Failed to extract cache token from headers: {e}")
                cache_saved = False
            except Exception as e:
                logger.warning(f"Unexpected error extracting cache token: {e}")
                cache_saved = False
            
            # Pull content with structure validation
            try:
                # Validate response structure BEFORE parsing
                if not hasattr(raw_payload, "choices") and not (isinstance(raw_payload, dict) and "choices" in raw_payload):
                    raise ValueError(
                        f"Invalid Kimi API response: missing 'choices' field. "
                        f"Response type: {type(raw_payload)}"
                    )

                choices = raw_payload.choices if hasattr(raw_payload, "choices") else raw_payload.get("choices")

                if not choices or len(choices) == 0:
                    raise ValueError(
                        f"Invalid Kimi API response: empty 'choices' array. "
                        f"This may indicate an API error or rate limit."
                    )

                choice0 = choices[0]

                # Validate choice has message field
                if not hasattr(choice0, "message") and not (isinstance(choice0, dict) and "message" in choice0):
                    raise ValueError(
                        f"Invalid Kimi API response: choice missing 'message' field. "
                        f"Choice type: {type(choice0)}"
                    )

                # Extract message - handle both Pydantic objects and dicts
                if hasattr(choice0, "message"):
                    msg = choice0.message
                elif isinstance(choice0, dict):
                    msg = choice0.get("message", {})
                else:
                    msg = None

                # Extract content - handle both Pydantic objects and dicts
                if msg:
                    if hasattr(msg, "content"):
                        content_text = msg.content
                    elif isinstance(msg, dict):
                        content_text = msg.get("content", "")
                    else:
                        content_text = ""
                else:
                    content_text = ""

                # ✅ FIXED (2025-11-03): Extract reasoning_content for kimi-thinking-preview
                # Official field name is 'reasoning_content' (singular) per Moonshot API docs
                # External AI fact-check: No need for triple fallback, single field only
                reasoning_content = None
                if msg:
                    if hasattr(msg, "reasoning_content"):
                        reasoning_content = msg.reasoning_content
                    elif isinstance(msg, dict):
                        reasoning_content = msg.get("reasoning_content")
            except ValueError as e:
                # Re-raise validation errors - these indicate API problems
                logger.error(f"Kimi API response validation failed (model: {model}): {e}")
                raise
            except Exception as e:
                logger.warning(f"Failed to extract content from Kimi response (model: {model}): {e}")
                # Continue - empty content will be returned, may indicate API response format change
                content_text = ""
        else:
            # Fallback without raw headers support
            # Build API call parameters
            api_params = {
                "model": model,
                "messages": messages,
                "tools": tools,
                "tool_choice": tool_choice,
                "temperature": temperature,
                "stream": False,
                "extra_headers": extra_headers,
            }

            # PHASE 2.1.1.1 (2025-10-21): Model-aware max_tokens handling (fallback path)
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
                logger.debug(f"Kimi API (fallback): Using max_tokens={validated_max_tokens} for model {model}")

            # PHASE 1 (2025-10-18): Wrap fallback API call with circuit breaker
            @breaker
            def _kimi_api_call_fallback():
                return client.chat.completions.create(**api_params)

            resp = _kimi_api_call_fallback()
            raw_payload = getattr(resp, "model_dump", lambda: resp)()
            try:
                content_text = resp.choices[0].message.content
            except (AttributeError, IndexError, KeyError) as e:
                logger.debug(f"Failed to extract content from response object, falling back to dict access: {e}")
                content_text = (raw_payload.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
            except Exception as e:
                logger.warning(f"Unexpected error extracting content: {e}")
                content_text = (raw_payload.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
    except pybreaker.CircuitBreakerError:
        # PHASE 1 (2025-10-18): Circuit breaker is OPEN - Kimi API is unavailable
        logger.error("Kimi circuit breaker OPEN - API unavailable")
        error = "Circuit breaker OPEN - Kimi API unavailable"

        # PHASE 3 (2025-10-23): Monitoring will be recorded in finally block
        # Return error response (graceful degradation)
        return {
            "provider": "KIMI",
            "model": model,
            "content": "",
            "tool_calls": None,
            "usage": None,
            "raw": {},
            "metadata": {
                "error": error,
                "circuit_breaker_open": True,
            },
        }
    except Exception as e:
        logger.error("Kimi chat call error: %s", e)
        error = str(e)
        # PHASE 3 (2025-10-23): Monitoring will be recorded in finally block
        raise
    finally:
        # PHASE 3 (2025-10-23): ALWAYS record monitoring event (all code paths)
        logger.info(f"[MONITORING_DEBUG] FINALLY BLOCK ENTERED for model={model}")

        try:
            response_time_ms = (time.time() - start_time) * 1000

            # Determine direction based on error state
            direction = "error" if error else "receive"

            logger.info(f"[MONITORING_DEBUG] About to call record_kimi_event for model={model}, tokens={total_tokens}, error={error}")

            record_kimi_event(
                direction=direction,
                function_name="kimi_chat.chat_completions_create",
                data_size=response_size if not error else request_size,
                response_time_ms=response_time_ms,
                error=error if error else None,
                metadata={
                    "model": model,
                    "tokens": total_tokens,
                    "cache_hit": bool(cache_attached),
                    "finish_reason": finish_reason,
                    "timestamp": log_timestamp()
                }
            )
            logger.info(f"[MONITORING_DEBUG] Successfully called record_kimi_event")
        except Exception as e:
            logger.error(f"[MONITORING_DEBUG] FINALLY BLOCK ERROR: {e}", exc_info=True)

    # Normalize usage to a plain dict to ensure JSON-serializable output
    _usage = None
    try:
        if hasattr(raw_payload, "usage"):
            u = getattr(raw_payload, "usage")
            if hasattr(u, "model_dump"):
                _usage = u.model_dump()
            elif isinstance(u, dict):
                _usage = u
            else:
                _usage = {
                    "prompt_tokens": getattr(u, "prompt_tokens", None),
                    "completion_tokens": getattr(u, "completion_tokens", None),
                    "total_tokens": getattr(u, "total_tokens", None),
                }
        elif isinstance(raw_payload, dict):
            _usage = raw_payload.get("usage")
    except Exception as e:
        logger.debug(f"Failed to extract usage from Kimi response (model: {model}): {e}")
        # Continue - usage will be None, metrics may be incomplete but response is still valid
        _usage = None

    # Extract tool_calls from response if present
    tool_calls_data = None
    try:
        if isinstance(raw_payload, dict):
            choices = raw_payload.get("choices", [])
        else:
            choices = getattr(raw_payload, "choices", [])

        if choices:
            if isinstance(choices[0], dict):
                msg = choices[0].get("message", {})
            else:
                msg = getattr(choices[0], "message", {})

            if isinstance(msg, dict):
                tool_calls_data = msg.get("tool_calls")
            else:
                tool_calls_data = getattr(msg, "tool_calls", None)
    except Exception as e:
        logger.debug(f"Failed to extract tool_calls from Kimi response (model: {model}): {e}")
        # Continue - tool_calls will be None, tool use functionality may not work but response is still valid
        tool_calls_data = None

    # Extract finish_reason from response (CRITICAL for detecting truncation)
    finish_reason = "unknown"
    try:
        if isinstance(raw_payload, dict):
            choices = raw_payload.get("choices", [])
        else:
            choices = getattr(raw_payload, "choices", [])

        if choices:
            if isinstance(choices[0], dict):
                finish_reason = choices[0].get("finish_reason", "unknown")
            else:
                finish_reason = getattr(choices[0], "finish_reason", "unknown")
    except Exception as e:
        logger.debug(f"Failed to extract finish_reason from Kimi response (model: {model}): {e}")
        # Continue - finish_reason will be "unknown", completeness check may not work but response is still valid
        finish_reason = "unknown"

    # PHASE 3 (2025-10-23): Update monitoring context variables for finally block
    response_size = len(str(content_text).encode('utf-8'))
    if _usage:
        total_tokens = _usage.get("total_tokens", 0)

    # PHASE 1 (2025-10-24): Calculate response time for metadata
    ai_response_time_ms = int((time.time() - start_time) * 1000)

    return {
        "provider": "KIMI",
        "model": model,
        "content": content_text or "",
        "reasoning_content": locals().get('reasoning_content'),  # ✅ FIXED (2025-11-03): Correct field name per Moonshot API
        "tool_calls": tool_calls_data,  # Now properly extracted instead of hardcoded None
        "usage": _usage,
        "raw": getattr(raw_payload, "model_dump", lambda: raw_payload)() if hasattr(raw_payload, "model_dump") else raw_payload,
        "metadata": {
            "finish_reason": finish_reason,  # CRITICAL: Now extracted for completeness validation
            "cache": {
                "attached": bool(cache_attached),
                "saved": bool(cache_saved),
            },
            "idempotency_key": str(call_key) if call_key else None,
            "prefix_hash": msg_prefix_hash or None,
            "ai_response_time_ms": ai_response_time_ms,
        },
    }


def chat_completions_create_with_continuation(
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
    thinking_enabled: bool = False,  # CRITICAL FIX (2025-11-02): Pass through thinking mode
    enable_continuation: bool = True,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    **kwargs
) -> dict:
    """
    Wrapper for chat_completions_create with automatic continuation support.

    PHASE 2.1.3 (2025-10-21): Automatic Continuation

    This function automatically detects truncated responses and continues them
    until completion or max attempts reached.

    Args:
        client: OpenAI-compatible client instance
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
        Dictionary with provider, model, content, tool_calls, usage, raw, and metadata
    """
    # Call the base function
    initial_response = chat_completions_create(
        client,
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        cache_id=cache_id,
        reset_cache_ttl=reset_cache_ttl,
        thinking_enabled=thinking_enabled,  # CRITICAL FIX (2025-11-02): Pass through thinking mode
        **kwargs
    )

    # If continuation is disabled, return as-is
    if not enable_continuation:
        return initial_response

    # Check if response was truncated
    try:
        from src.utils.truncation_detector import check_truncation
        from src.utils.continuation_manager import get_continuation_manager

        # Check for truncation
        truncation_info = check_truncation(initial_response.get('raw', {}), model)

        if not truncation_info.get('is_truncated'):
            # Not truncated, return as-is
            return initial_response

        logger.info(f"🔄 Truncated response detected for {model}, starting continuation...")

        # Get continuation manager
        continuation_manager = get_continuation_manager()

        # Prepare provider callable
        def provider_callable(cont_messages, **cont_kwargs):
            return chat_completions_create(
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

        # Continue the response
        continuation_result = continuation_manager.continue_response_sync(
            original_messages=messages,
            initial_response=initial_response.get('raw', {}),
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
    thinking_enabled: bool = False,  # CRITICAL FIX (2025-11-02): Pass through thinking mode
    enable_continuation: bool = True,
    max_continuation_attempts: int = 3,
    max_total_tokens: int = 32000,
    timeout_seconds: Optional[float] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Session-managed wrapper for Kimi chat with automatic continuation support.

    PHASE 2.2.3 (2025-10-21): Concurrent Request Handling
    Refactored to use execute_with_session() helper per EXAI recommendation.

    PHASE 0.3 (2025-10-24): Added timeout enforcement to prevent provider hangs
    Uses KIMI_SESSION_TIMEOUT env var (default: 25s) with active enforcement

    This function wraps chat_completions_create_with_continuation in a managed session
    to enable concurrent request handling without blocking. Each request gets its own
    isolated session with timeout handling and lifecycle tracking.

    Args:
        client: OpenAI-compatible client instance
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
        timeout_seconds: Optional timeout override (default: KIMI_SESSION_TIMEOUT env var)
        request_id: Optional request ID (generated if not provided)
        **kwargs: Additional parameters

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, metadata,
        and session context (session_id, request_id, duration_seconds)
    """
    # PHASE 0.3 (2025-10-24): Use KIMI_SESSION_TIMEOUT from environment
    default_timeout = float(os.getenv("KIMI_SESSION_TIMEOUT", "25"))
    enforce_timeout = os.getenv("ENFORCE_SESSION_TIMEOUT", "true").lower() == "true"

    session_manager = get_session_manager(default_timeout=timeout_seconds or default_timeout)

    def _execute_kimi_chat():
        """Internal function to execute Kimi chat within session."""
        return chat_completions_create_with_continuation(
            client,
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            thinking_enabled=thinking_enabled,  # CRITICAL FIX (2025-11-02): Pass through thinking mode
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            cache_id=cache_id,
            reset_cache_ttl=reset_cache_ttl,
            enable_continuation=enable_continuation,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

    # Execute within managed session with automatic session context addition
    # PHASE 0.3 (2025-10-24): Enable timeout enforcement to prevent hangs
    return session_manager.execute_with_session(
        provider="kimi",
        model=model,
        func=_execute_kimi_chat,
        request_id=request_id,
        timeout_seconds=timeout_seconds,
        add_session_context=True,
        enforce_timeout=enforce_timeout
    )


__all__ = [
    "prefix_hash",
    "chat_completions_create",
    "chat_completions_create_with_continuation",
    "chat_completions_create_with_session"
]

