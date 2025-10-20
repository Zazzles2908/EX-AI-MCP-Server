"""GLM chat generation and streaming functionality."""

import json
import logging
import os
import time
from typing import Any, Optional

from .base import ModelResponse, ProviderType

# PHASE 3 (2025-10-18): Import monitoring utilities
from utils.monitoring import record_glm_event
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-18): Import circuit breaker for resilience
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

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

    # Max tokens handling - respects ENFORCE_MAX_TOKENS configuration
    # If max_output_tokens is explicitly provided, always use it
    # If not provided and ENFORCE_MAX_TOKENS=true, use GLM_MAX_OUTPUT_TOKENS default
    # If not provided and ENFORCE_MAX_TOKENS=false, don't set max_tokens (let model decide)
    from config import GLM_MAX_OUTPUT_TOKENS, ENFORCE_MAX_TOKENS
    if max_output_tokens:
        # Explicitly provided - always use it
        payload["max_tokens"] = int(max_output_tokens)
    elif ENFORCE_MAX_TOKENS and GLM_MAX_OUTPUT_TOKENS > 0:
        # Not provided, but enforcement is enabled - use default
        payload["max_tokens"] = int(GLM_MAX_OUTPUT_TOKENS)
        logger.debug(f"Using default max_tokens={GLM_MAX_OUTPUT_TOKENS} for GLM (ENFORCE_MAX_TOKENS=true)")
    # else: Don't set max_tokens, let the model use its default
    
    # GLM Thinking Mode Support (glm-4.6 and later)
    # API Format: "thinking": {"type": "enabled"}
    # Source: https://docs.z.ai/api-reference/llm/chat-completion
    if 'thinking_mode' in kwargs:
        thinking_mode = kwargs.pop('thinking_mode', None)
        # Check if model supports thinking (glm-4.6 and later)
        from .glm_config import get_capabilities, SUPPORTED_MODELS, resolve_model_name_for_glm
        caps = get_capabilities(model_name, SUPPORTED_MODELS, resolve_model_name_for_glm)
        if caps.supports_extended_thinking:
            # GLM uses "thinking": {"type": "enabled"} format
            payload["thinking"] = {"type": "enabled"}
            logger.debug(f"Enabled thinking mode for GLM model {model_name}")
        else:
            logger.warning(
                f"⚠️ Model {model_name} doesn't support thinking_mode - parameter ignored. "
                f"Use glm-4.6, glm-4.5, or glm-4.5-air for thinking mode support. "
                f"Requested mode: {thinking_mode}"
            )

    # Pass through GLM tool capabilities when requested (e.g., native web_search)
    try:
        tools = kwargs.get("tools")
        if tools:
            payload["tools"] = tools

            # CRITICAL FIX (Bug #3): glm-4.6 requires explicit tool_choice="auto"
            # Without this, glm-4.6 returns raw JSON tool calls as text instead of executing them
            # Other GLM models work without explicit tool_choice, but glm-4.6 needs it
            tool_choice = kwargs.get("tool_choice")
            if not tool_choice and model_name == "glm-4.6":
                payload["tool_choice"] = "auto"
                logger.debug(f"GLM-4.6: Auto-setting tool_choice='auto' for function calling (Bug #3 fix)")
            elif tool_choice:
                payload["tool_choice"] = tool_choice

            # CRITICAL FIX (2025-10-15): GLM-4.6 requires tool_stream=True for streaming tool calls
            # According to Z.ai documentation: https://docs.z.ai/guides/tools/stream-tool
            # When stream=True AND tools are present, must set tool_stream=True
            if payload.get("stream"):
                import os as _os
                tool_stream_enabled = _os.getenv("GLM_TOOL_STREAM_ENABLED", "true").strip().lower() == "true"
                if tool_stream_enabled:
                    payload["tool_stream"] = True
                    logger.debug(f"GLM-4.6: Enabled tool_stream=True for streaming tool calls")
    except Exception as e:
        logger.warning(f"Failed to add tools/tool_choice to GLM payload (model: {model_name}): {e}")
        # Continue - payload will be sent without tools, API may reject if tools were required

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
    # Log kwargs for debugging (use logger.debug, not print)
    logger.debug(f"GLM generate_content called with kwargs keys: {list(kwargs.keys())}")

    payload = build_payload(prompt, system_prompt, model_name, temperature, max_output_tokens, **kwargs)

    # PHASE 3 (2025-10-18): Monitor API call start
    start_time = time.time()
    request_size = len(str(payload).encode('utf-8'))
    error = None

    # PHASE 1 (2025-10-18): Apply circuit breaker protection
    breaker = circuit_breaker_manager.get_breaker('glm')

    try:
        stream = bool(payload.get("stream", False))
        
        # Env gate: allow streaming only when GLM_STREAM_ENABLED=true
        try:
            _stream_env = os.getenv("GLM_STREAM_ENABLED", "false").strip().lower() in ("1", "true", "yes")
        except Exception as e:
            logger.debug(f"Failed to parse GLM_STREAM_ENABLED env variable: {e}")
            # Continue with streaming disabled - safer default
            _stream_env = False
        if stream and not _stream_env:
            logger.info("GLM streaming disabled via GLM_STREAM_ENABLED; falling back to non-streaming")
            stream = False
        
        if use_sdk and sdk_client:
            # Use official SDK
            logger.info(f"GLM chat using SDK: model={model_name}, stream={stream}, messages_count={len(payload['messages'])}")

            # CRITICAL FIX: Only pass tools/tool_choice if they exist in payload
            # Passing tools=None can cause SDK to hang or behave unexpectedly
            sdk_kwargs = {
                "model": model_name,
                "messages": payload["messages"],
                "stream": stream,
            }
            if payload.get("temperature") is not None:
                sdk_kwargs["temperature"] = payload["temperature"]
            if payload.get("max_tokens"):
                sdk_kwargs["max_tokens"] = payload["max_tokens"]
            if payload.get("tools"):
                sdk_kwargs["tools"] = payload["tools"]
            if payload.get("tool_choice"):
                sdk_kwargs["tool_choice"] = payload["tool_choice"]

            logger.debug(f"GLM SDK kwargs keys: {list(sdk_kwargs.keys())}")

            # PHASE 1 (2025-10-18): Wrap SDK API call with circuit breaker
            @breaker
            def _glm_sdk_call():
                return sdk_client.chat.completions.create(**sdk_kwargs)

            resp = _glm_sdk_call()
            
            if stream:
                # Aggregate streamed chunks from SDK iterator
                content_parts = []
                actual_model = None
                response_id = None
                created_ts = None

                # CRITICAL FIX (2025-10-15): Add streaming timeout to prevent 6+ hour hangs
                # Get timeout from env (default 5 minutes for GLM)
                # Note: time module already imported at module level (line 6)
                stream_timeout = int(os.getenv("GLM_STREAM_TIMEOUT", "300"))  # 5 minutes default
                stream_start = time.time()

                try:
                    for event in resp:
                        # Check if streaming has exceeded timeout
                        elapsed = time.time() - stream_start
                        if elapsed > stream_timeout:
                            raise TimeoutError(
                                f"GLM streaming exceeded timeout of {stream_timeout}s (elapsed: {int(elapsed)}s). "
                                "This prevents indefinite hangs. Increase GLM_STREAM_TIMEOUT if needed."
                            )

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
                        except Exception as e:
                            logger.debug(f"Failed to parse GLM streaming event metadata: {e}")
                            # Continue - skip this event, next event may have valid data
                            continue
                except TimeoutError as timeout_err:
                    logger.error(f"GLM streaming timeout: {timeout_err}")
                    raise RuntimeError(f"GLM SDK streaming timeout: {timeout_err}") from timeout_err
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
                message = choice0.get("message") or {}
                text = message.get("content") or ""

                # CRITICAL FIX: Check for tool_calls (web_search results)
                # When GLM executes web_search, results are in message.tool_calls
                tool_calls = message.get("tool_calls")

                # Import text format handler
                from src.providers.text_format_handler import (
                    has_text_format_tool_call,
                    parse_and_execute_web_search
                )

                # DEBUG: Log response format to diagnose inconsistent behavior
                has_tool_calls_array = bool(tool_calls and isinstance(tool_calls, list))
                has_tool_call_text = has_text_format_tool_call(text)
                logger.debug(f"GLM response format: tool_calls_array={has_tool_calls_array}, tool_call_text={has_tool_call_text}, model={model_name}")

                if tool_calls and isinstance(tool_calls, list):
                    # Web search was executed - extract results from tool calls
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            func = tc.get("function", {})
                            if func.get("name") == "web_search":
                                # Web search results are in function.arguments
                                try:
                                    import json as _json
                                    args = func.get("arguments", "{}")
                                    if isinstance(args, str):
                                        search_data = _json.loads(args)
                                    else:
                                        search_data = args
                                    # Append search results to content
                                    if search_data:
                                        text = text + "\n\n[Web Search Results]\n" + _json.dumps(search_data, indent=2, ensure_ascii=False)
                                        logger.info(f"GLM web_search executed successfully via tool_calls array")
                                except Exception as e:
                                    logger.debug(f"Failed to parse web_search tool call: {e}")
                elif has_tool_call_text:
                    # GLM returned tool call as TEXT - parse and execute it
                    logger.warning(f"GLM returned tool call as TEXT: {text[:200]}")
                    text, success = parse_and_execute_web_search(text)
                    if success:
                        logger.info(f"GLM web_search executed successfully via text format handler")
                    else:
                        logger.warning(f"Failed to execute web_search from text format")

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
                        except Exception as e:
                            logger.debug(f"Failed to parse GLM streaming JSON line, treating as raw text: {e}")
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
                        except Exception as e:
                            logger.debug(f"Failed to parse GLM streaming choice data: {e}")
                            # Continue - skip this chunk, next chunk may have valid data
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
                # PHASE 1 (2025-10-18): Wrap HTTP API call with circuit breaker
                @breaker
                def _glm_http_call():
                    return http_client.post_json("/chat/completions", payload)

                raw = _glm_http_call()
                choice0 = (raw.get("choices") or [{}])[0]
                message = choice0.get("message") or {}
                text = message.get("content") or ""

                # CRITICAL FIX: Check for tool_calls (web_search results) in HTTP path
                tool_calls = message.get("tool_calls")

                # Import text format handler (same as SDK path)
                from src.providers.text_format_handler import (
                    has_text_format_tool_call,
                    parse_and_execute_web_search
                )

                has_tool_call_text = has_text_format_tool_call(text)

                if tool_calls and isinstance(tool_calls, list):
                    for tc in tool_calls:
                        if isinstance(tc, dict):
                            func = tc.get("function", {})
                            if func.get("name") == "web_search":
                                try:
                                    import json as _json
                                    args = func.get("arguments", "{}")
                                    if isinstance(args, str):
                                        search_data = _json.loads(args)
                                    else:
                                        search_data = args
                                    if search_data:
                                        text = text + "\n\n[Web Search Results]\n" + _json.dumps(search_data, indent=2, ensure_ascii=False)
                                        logger.info(f"GLM web_search executed successfully via tool_calls array (HTTP path)")
                                except Exception as e:
                                    logger.debug(f"Failed to parse web_search tool call: {e}")
                elif has_tool_call_text:
                    # GLM returned tool call as TEXT - parse and execute it (HTTP path)
                    logger.warning(f"GLM returned tool call as TEXT (HTTP path): {text[:200]}")
                    text, success = parse_and_execute_web_search(text)
                    if success:
                        logger.info(f"GLM web_search executed successfully via text format handler (HTTP path)")
                    else:
                        logger.warning(f"Failed to execute web_search from text format (HTTP path)")

                usage = raw.get("usage", {})
        
        # PHASE 3 (2025-10-18): Monitor successful API call
        response_time_ms = (time.time() - start_time) * 1000
        response_size = len(str(text).encode('utf-8'))

        # Extract token usage for monitoring
        total_tokens = 0
        if usage:
            total_tokens = usage.get("total_tokens", 0)

        record_glm_event(
            direction="receive",
            function_name="glm_chat.generate_content",
            data_size=response_size,
            response_time_ms=response_time_ms,
            metadata={
                "model": model_name,
                "tokens": total_tokens,
                "streamed": stream,
                "timestamp": log_timestamp()
            }
        )

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
    except pybreaker.CircuitBreakerError:
        # PHASE 1 (2025-10-18): Circuit breaker is OPEN - GLM API is unavailable
        logger.error("GLM circuit breaker OPEN - API unavailable")
        error = "Circuit breaker OPEN - GLM API unavailable"

        # Record monitoring event
        response_time_ms = (time.time() - start_time) * 1000
        record_glm_event(
            direction="error",
            function_name="glm_chat.generate_content",
            data_size=request_size,
            error=error,
            metadata={
                "model": model_name,
                "timestamp": log_timestamp()
            }
        )

        # Return error response (graceful degradation)
        return ModelResponse(
            content="",
            usage=None,
            model_name=model_name,
            friendly_name="GLM",
            provider=ProviderType.GLM,
            metadata={
                "error": error,
                "circuit_breaker_open": True,
            },
        )
    except Exception as e:
        logger.error("GLM generate_content failed: %s", e)
        error = str(e)

        # PHASE 3 (2025-10-18): Monitor API call failure
        response_time_ms = (time.time() - start_time) * 1000
        record_glm_event(
            direction="error",
            function_name="glm_chat.generate_content",
            data_size=request_size,
            error=error,
            metadata={
                "model": model_name,
                "timestamp": log_timestamp()
            }
        )
        raise


def chat_completions_create(
    sdk_client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.3,
    **kwargs
) -> dict:
    """
    SDK-native chat completions method for GLM provider.

    This method accepts pre-built message arrays (SDK-native format) instead of
    building messages from text prompts. This is the preferred method for tools
    and workflow systems that manage conversation history.

    Args:
        sdk_client: ZhipuAI SDK client instance
        model: Model name (already resolved)
        messages: Pre-built message array in OpenAI format
        tools: Optional list of tools for function calling
        tool_choice: Optional tool choice directive
        temperature: Temperature value (default: 0.3)
        **kwargs: Additional parameters (stream, thinking_mode, etc.)

    Returns:
        Normalized dict with provider, model, content, usage, metadata

    Example:
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant"},
        ...     {"role": "user", "content": "Hello"}
        ... ]
        >>> result = chat_completions_create(
        ...     sdk_client=client,
        ...     model="glm-4.6",
        ...     messages=messages,
        ...     temperature=0.5
        ... )
    """
    # Build payload with messages instead of prompt
    # Extract system message if present
    system_prompt = None
    user_messages = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")

        if role == "system":
            # Combine multiple system messages if present
            if system_prompt:
                system_prompt += "\n\n" + content
            else:
                system_prompt = content
        else:
            # Keep user and assistant messages
            user_messages.append(msg)

    # Build payload using the messages array
    payload = {
        "model": model,
        "messages": messages,  # Use full message array (SDK handles it)
        "stream": bool(kwargs.get("stream", False)),
    }

    if temperature is not None:
        payload["temperature"] = temperature

    # Max tokens handling
    max_output_tokens = kwargs.get("max_output_tokens") or kwargs.get("max_tokens")
    if max_output_tokens:
        payload["max_tokens"] = int(max_output_tokens)

    # Thinking mode support
    if kwargs.get("thinking_mode"):
        from .glm_config import get_capabilities, SUPPORTED_MODELS, resolve_model_name_for_glm
        caps = get_capabilities(model, SUPPORTED_MODELS, resolve_model_name_for_glm)
        if caps.supports_extended_thinking:
            payload["thinking"] = {"type": "enabled"}
            logger.debug(f"Enabled thinking mode for GLM model {model}")

    # Tools and tool_choice
    if tools:
        payload["tools"] = tools
        if tool_choice:
            payload["tool_choice"] = tool_choice
        elif model == "glm-4.6":
            # glm-4.6 requires explicit tool_choice="auto"
            payload["tool_choice"] = "auto"
            logger.debug(f"GLM-4.6: Auto-setting tool_choice='auto' for function calling")

    # Call SDK
    stream = payload.get("stream", False)

    try:
        if stream:
            # Streaming not yet implemented for chat_completions_create
            # Fall back to non-streaming
            logger.warning("Streaming not yet supported in chat_completions_create, using non-streaming")
            payload["stream"] = False
            stream = False

        # Apply circuit breaker
        breaker = circuit_breaker_manager.get_breaker('glm')

        @breaker
        def _glm_sdk_call():
            return sdk_client.chat.completions.create(**payload)

        resp = _glm_sdk_call()

        # Extract response
        choice0 = resp.choices[0] if resp.choices else None
        message = choice0.message if choice0 else None
        content_text = message.content if message else ""
        finish_reason = choice0.finish_reason if choice0 else "unknown"

        # Extract usage
        usage_dict = {}
        if hasattr(resp, "usage") and resp.usage:
            usage_dict = {
                "prompt_tokens": getattr(resp.usage, "prompt_tokens", 0),
                "completion_tokens": getattr(resp.usage, "completion_tokens", 0),
                "total_tokens": getattr(resp.usage, "total_tokens", 0),
            }

        # Return normalized dict (same format as Kimi)
        return {
            "provider": "GLM",
            "model": model,
            "content": content_text or "",
            "tool_calls": None,  # TODO: Extract tool calls if present
            "usage": usage_dict,
            "raw": resp.model_dump() if hasattr(resp, "model_dump") else {},
            "metadata": {
                "finish_reason": finish_reason,
            },
        }

    except Exception as e:
        logger.error(f"GLM chat_completions_create failed: {e}", exc_info=True)
        raise RuntimeError(f"GLM chat completion failed: {e}")


__all__ = ["build_payload", "generate_content", "chat_completions_create"]

