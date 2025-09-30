"""GLM chat generation and streaming functionality."""

import json
import logging
import os
from typing import Any, Optional

from .base import ModelResponse, ProviderType

logger = logging.getLogger(__name__)


def build_payload(
    prompt: str,
    system_prompt: Optional[str],
    model_name: str,
    temperature: float,
    max_output_tokens: Optional[int],
    **kwargs
) -> dict:
    """Build request payload for GLM API.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        model_name: Model name (already resolved)
        temperature: Temperature value (already validated)
        max_output_tokens: Optional max output tokens
        **kwargs: Additional parameters (stream, tools, tool_choice, etc.)
        
    Returns:
        Request payload dictionary
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages,
        # Allow callers to request streaming; default False for MCP tools
        "stream": bool(kwargs.get("stream", False)),
    }
    
    if temperature is not None:
        payload["temperature"] = temperature
    if max_output_tokens:
        payload["max_tokens"] = int(max_output_tokens)
    
    # Pass through GLM tool capabilities when requested (e.g., native web_search)
    try:
        tools = kwargs.get("tools")
        if tools:
            payload["tools"] = tools
        tool_choice = kwargs.get("tool_choice")
        if tool_choice:
            payload["tool_choice"] = tool_choice
    except Exception:
        # be permissive
        pass
    
    # Images handling placeholder
    return payload


def generate_content(
    sdk_client: Any,
    http_client: Any,
    prompt: str,
    model_name: str,
    system_prompt: Optional[str],
    temperature: float,
    max_output_tokens: Optional[int],
    use_sdk: bool,
    **kwargs
) -> ModelResponse:
    """Generate content with streaming support.
    
    Supports both SDK and HTTP client paths with automatic fallback.
    Handles streaming and non-streaming modes.
    
    Args:
        sdk_client: ZhipuAI SDK client instance (if available)
        http_client: HTTP client instance for fallback
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
    payload = build_payload(prompt, system_prompt, model_name, temperature, max_output_tokens, **kwargs)
    
    try:
        stream = bool(payload.get("stream", False))
        
        # Env gate: allow streaming only when GLM_STREAM_ENABLED=true
        try:
            _stream_env = os.getenv("GLM_STREAM_ENABLED", "false").strip().lower() in ("1", "true", "yes")
        except Exception:
            _stream_env = False
        if stream and not _stream_env:
            logger.info("GLM streaming disabled via GLM_STREAM_ENABLED; falling back to non-streaming")
            stream = False
        
        if use_sdk and sdk_client:
            # Use official SDK
            resp = sdk_client.chat.completions.create(
                model=model_name,
                messages=payload["messages"],
                temperature=payload.get("temperature"),
                max_tokens=payload.get("max_tokens"),
                stream=stream,
                tools=payload.get("tools"),
                tool_choice=payload.get("tool_choice"),
            )
            
            if stream:
                # Aggregate streamed chunks from SDK iterator
                content_parts = []
                actual_model = None
                response_id = None
                created_ts = None
                try:
                    for event in resp:
                        try:
                            # Support both delta and message content shapes
                            choice = getattr(event, "choices", [None])[0]
                            if choice is not None:
                                delta = getattr(choice, "delta", None)
                                if delta and getattr(delta, "content", None):
                                    content_parts.append(delta.content)
                                msg = getattr(choice, "message", None)
                                if msg and getattr(msg, "content", None):
                                    content_parts.append(msg.content)
                            if actual_model is None and getattr(event, "model", None):
                                actual_model = event.model
                            if response_id is None and getattr(event, "id", None):
                                response_id = event.id
                            if created_ts is None and getattr(event, "created", None):
                                created_ts = event.created
                        except Exception:
                            continue
                except Exception as stream_err:
                    raise RuntimeError(f"GLM SDK streaming failed: {stream_err}") from stream_err
                
                text = "".join(content_parts)
                raw = None
                usage = {}
                return ModelResponse(
                    content=text or "",
                    usage=usage or None,
                    model_name=model_name,
                    friendly_name="GLM",
                    provider=ProviderType.GLM,
                    metadata={
                        "streamed": True,
                        "model": actual_model or model_name,
                        "id": response_id,
                        "created": created_ts,
                        "tools": payload.get("tools"),
                        "tool_choice": payload.get("tool_choice"),
                    },
                )
            else:
                # Non-streaming via SDK
                raw = getattr(resp, "model_dump", lambda: resp)()
                choice0 = (raw.get("choices") or [{}])[0]
                text = ((choice0.get("message") or {}).get("content")) or ""
                usage = raw.get("usage", {})
        else:
            # HTTP fallback
            if stream:
                # SSE streaming
                content_parts = []
                actual_model = None
                response_id = None
                created_ts = None
                try:
                    for data in http_client.stream_sse("/chat/completions", payload, event_field="data"):
                        line = (data or "").strip()
                        if not line:
                            continue
                        if line == "[DONE]":
                            break
                        try:
                            evt = json.loads(line)
                        except Exception:
                            # Some implementations send raw text chunks; append directly
                            content_parts.append(line)
                            continue
                        try:
                            choice0 = (evt.get("choices") or [{}])[0]
                            # GLM-like chunk may include delta or message
                            delta = (choice0.get("delta") or {})
                            if isinstance(delta, dict) and delta.get("content"):
                                content_parts.append(delta.get("content") or "")
                            msg = (choice0.get("message") or {})
                            if isinstance(msg, dict) and msg.get("content"):
                                content_parts.append(msg.get("content") or "")
                            actual_model = actual_model or evt.get("model")
                            response_id = response_id or evt.get("id")
                            created_ts = created_ts or evt.get("created")
                            finish_reason = choice0.get("finish_reason")
                            if finish_reason in ("stop", "length"):
                                # Let loop continue to consume until provider sends DONE
                                pass
                        except Exception:
                            continue
                except Exception as stream_err:
                    raise RuntimeError(f"GLM HTTP streaming failed: {stream_err}") from stream_err
                
                text = "".join(content_parts)
                raw = None
                usage = {}
                return ModelResponse(
                    content=text or "",
                    usage=usage or None,
                    model_name=model_name,
                    friendly_name="GLM",
                    provider=ProviderType.GLM,
                    metadata={
                        "streamed": True,
                        "model": actual_model or model_name,
                        "id": response_id,
                        "created": created_ts,
                        "tools": payload.get("tools"),
                        "tool_choice": payload.get("tool_choice"),
                    },
                )
            else:
                raw = http_client.post_json("/chat/completions", payload)
                text = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
                usage = raw.get("usage", {})
        
        return ModelResponse(
            content=text or "",
            usage={
                "input_tokens": int(usage.get("prompt_tokens", 0)),
                "output_tokens": int(usage.get("completion_tokens", 0)),
                "total_tokens": int(usage.get("total_tokens", 0)),
            } if usage else None,
            model_name=model_name,
            friendly_name="GLM",
            provider=ProviderType.GLM,
            metadata={
                "raw": raw,
                "streamed": bool(stream),
                "tools": payload.get("tools"),
                "tool_choice": payload.get("tool_choice"),
            },
        )
    except Exception as e:
        logger.error("GLM generate_content failed: %s", e)
        raise


__all__ = ["build_payload", "generate_content"]

