"""Kimi chat functionality with cache token integration."""

import hashlib
import logging
import os
from typing import Any, Optional

from . import kimi_cache

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
    cache_id: Optional[str] = None,
    reset_cache_ttl: bool = False,
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
    
    try:
        api = getattr(client.chat.completions, "with_raw_response", None)
        if api:
            raw = api.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                stream=False,
                extra_headers=extra_headers,
            )
            # Parse JSON body
            try:
                raw_payload = raw.parse()
            except Exception as e:
                logger.debug(f"Failed to parse raw response, falling back to http_response attribute: {e}")
                # Continue - fallback to http_response attribute
                raw_payload = getattr(raw, "http_response", None)
            
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
            
            # Pull content
            try:
                choice0 = (raw_payload.choices if hasattr(raw_payload, "choices") else raw_payload.get("choices"))[0]
                msg = getattr(choice0, "message", None) or choice0.get("message", {})
                content_text = getattr(msg, "content", None) or msg.get("content", "")
            except Exception as e:
                logger.warning(f"Failed to extract content from Kimi response (model: {model}): {e}")
                # Continue - empty content will be returned, may indicate API response format change
                content_text = ""
        else:
            # Fallback without raw headers support
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                stream=False,
                extra_headers=extra_headers,
            )
            raw_payload = getattr(resp, "model_dump", lambda: resp)()
            try:
                content_text = resp.choices[0].message.content
            except (AttributeError, IndexError, KeyError) as e:
                logger.debug(f"Failed to extract content from response object, falling back to dict access: {e}")
                content_text = (raw_payload.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
            except Exception as e:
                logger.warning(f"Unexpected error extracting content: {e}")
                content_text = (raw_payload.get("choices", [{}])[0].get("message", {}) or {}).get("content", "")
    except Exception as e:
        logger.error("Kimi chat call error: %s", e)
        raise

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

    return {
        "provider": "KIMI",
        "model": model,
        "content": content_text or "",
        "tool_calls": tool_calls_data,  # Now properly extracted instead of hardcoded None
        "usage": _usage,
        "raw": getattr(raw_payload, "model_dump", lambda: raw_payload)() if hasattr(raw_payload, "model_dump") else raw_payload,
        "metadata": {
            "cache": {
                "attached": bool(cache_attached),
                "saved": bool(cache_saved),
            },
            "idempotency_key": str(call_key) if call_key else None,
            "prefix_hash": msg_prefix_hash or None,
        },
    }


__all__ = ["prefix_hash", "chat_completions_create"]

