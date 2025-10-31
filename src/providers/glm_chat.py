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

# PHASE 2.2.3 (2025-10-21): Import concurrent session manager
from src.utils.concurrent_session_manager import get_session_manager

# PHASE 1 (2025-10-24): Import error capture for comprehensive monitoring
from utils.monitoring.error_capture import capture_errors, extract_provider_context

logger = logging.getLogger(__name__)


def _process_tool_calls_in_text(text: str, context: str = "unknown") -> tuple[str, bool]:
    """
    Process tool calls embedded in text response.

    This helper function handles cases where GLM returns tool calls as text
    instead of structured tool_calls array. This commonly happens in streaming
    mode where tool calls get embedded in the content stream.

    Args:
        text: The response text that may contain tool calls
        context: Context string for logging (e.g., "SDK streaming", "HTTP non-streaming")

    Returns:
        tuple: (processed_text, success_flag)
            - processed_text: Text with tool calls executed and results appended
            - success_flag: True if tool call was found and executed successfully
    """
    from src.providers.text_format_handler import (
        has_text_format_tool_call,
        parse_and_execute_web_search
    )

    if not has_text_format_tool_call(text):
        return text, True

    logger.warning(f"GLM returned tool call as TEXT ({context}): {text[:200]}...")

    try:
        processed_text, success = parse_and_execute_web_search(text)
        if success:
            logger.info(f"GLM web_search executed successfully via text format handler ({context})")
        else:
            logger.warning(f"Web search execution failed ({context})")
        return processed_text, success
    except Exception as e:
        logger.error(f"Tool call processing failed ({context}): {e}")
        return text, False


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

    # PHASE 2.1.1.1 (2025-10-21): Model-aware max_tokens handling
    from config import ENFORCE_MAX_TOKENS
    from .model_config import validate_max_tokens

    validated_max_tokens = validate_max_tokens(
        model_name=model_name,
        requested_max_tokens=max_output_tokens,
        input_tokens=0,  # TODO: Add token counting for input
        enforce_limits=ENFORCE_MAX_TOKENS
    )

    if validated_max_tokens is not None:
        payload["max_tokens"] = validated_max_tokens
        logger.debug(f"GLM API: Using max_tokens={validated_max_tokens} for model {model_name}")
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
                logger.debug("GLM-4.6: Auto-setting tool_choice='auto' for function calling (Bug #3 fix)")
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
                    logger.debug("GLM-4.6: Enabled tool_stream=True for streaming tool calls")
    except Exception as e:
        logger.warning(f"Failed to add tools/tool_choice to GLM payload (model: {model_name}): {e}")
        # Continue - payload will be sent without tools, API may reject if tools were required

    # Images handling placeholder
    return payload


@capture_errors(
    connection_type="glm",
    script_name="glm_chat.py",
    context_extractor=lambda *args, **kwargs: {
        "model": args[3] if len(args) > 3 else kwargs.get("model_name"),
        "stream": kwargs.get("stream", False),
        "use_sdk": args[7] if len(args) > 7 else kwargs.get("use_sdk"),
        "continuation_id": kwargs.get("continuation_id") or kwargs.get("conversation_id"),
    }
)
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
    # DIAGNOSTIC (2025-10-23): Entry point logging
    logger.info(f"[MONITORING_DEBUG] FUNCTION ENTRY: generate_content called for model={model_name}")

    # Log kwargs for debugging (use logger.debug, not print)
    logger.debug(f"GLM generate_content called with kwargs keys: {list(kwargs.keys())}")

    # PHASE 4 (2025-10-23): Extract continuation_id for session tracking (with conversation_id fallback)
    continuation_id = kwargs.get("continuation_id") or kwargs.get("conversation_id")
    if continuation_id and not continuation_id.strip():  # Handle empty strings
        continuation_id = None

    payload = build_payload(prompt, system_prompt, model_name, temperature, max_output_tokens, **kwargs)

    # PHASE 3 (2025-10-18): Monitor API call start
    start_time = time.time()
    request_size = len(str(payload).encode('utf-8'))
    error = None
    response_size = 0
    text = ""
    usage = {}
    stream_mode = False

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
                tool_calls_list = []  # CRITICAL FIX (2025-10-23): Collect tool calls from stream
                actual_model = None
                response_id = None
                created_ts = None

                # NEW (2025-10-24): Extract on_chunk callback for progressive streaming
                on_chunk_callback = kwargs.get("on_chunk")

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
                                if delta:
                                    # CRITICAL FIX (2025-10-23): Extract tool_calls from delta
                                    # This is what we were missing - GLM sends tool calls in delta.tool_calls
                                    if getattr(delta, "tool_calls", None):
                                        tool_calls_list.extend(delta.tool_calls)
                                        logger.debug(f"[WEBSEARCH_FIX] Captured tool_calls from streaming delta: {len(delta.tool_calls)} calls")

                                    if getattr(delta, "content", None):
                                        chunk_text = delta.content
                                        content_parts.append(chunk_text)

                                        # NEW (2025-10-24): Forward chunk immediately if callback provided
                                        if on_chunk_callback:
                                            from src.streaming.streaming_adapter import _safe_call_chunk_callback
                                            _safe_call_chunk_callback(on_chunk_callback, chunk_text)

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

                # Capture monitoring data before return
                text = "".join(content_parts)

                # CRITICAL FIX (2025-10-23): Execute web_search tool calls from streaming
                # GLM sends tool calls in delta.tool_calls during streaming - execute them now
                if tool_calls_list:
                    logger.info(f"[WEBSEARCH_FIX] Processing {len(tool_calls_list)} tool calls from SDK streaming")
                    for tc in tool_calls_list:
                        if hasattr(tc, 'function') and tc.function:
                            func = tc.function
                            if func.name == "web_search":
                                try:
                                    import json as _json
                                    args = func.arguments if hasattr(func, 'arguments') else "{}"
                                    if isinstance(args, str):
                                        search_data = _json.loads(args)
                                    else:
                                        search_data = args
                                    if search_data:
                                        text = text + "\n\n[Web Search Results]\n" + _json.dumps(search_data, indent=2, ensure_ascii=False)
                                        logger.info("[WEBSEARCH_FIX] GLM web_search executed successfully via SDK streaming tool_calls")
                                except Exception as e:
                                    logger.error(f"[WEBSEARCH_FIX] Failed to parse web_search tool call: {e}")
                else:
                    # Fallback: Check for text-embedded tool calls (legacy format)
                    text, _ = _process_tool_calls_in_text(text, context="SDK streaming")

                raw = None
                usage = {}
                stream_mode = True
                response_size = len(str(text).encode('utf-8'))

                # PHASE 1 (2025-10-24): Calculate response time for metadata
                ai_response_time_ms = int((time.time() - start_time) * 1000)

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
                        "ai_response_time_ms": ai_response_time_ms,
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
                                        logger.info("GLM web_search executed successfully via tool_calls array (SDK non-streaming)")
                                except Exception as e:
                                    logger.debug(f"Failed to parse web_search tool call: {e}")
                else:
                    # No structured tool_calls - check for text-embedded tool calls
                    text, _ = _process_tool_calls_in_text(text, context="SDK non-streaming")

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
                
                # Capture monitoring data before return
                text = "".join(content_parts)

                # CRITICAL FIX (2025-10-23): Process tool calls in streaming responses
                # GLM may return tool calls as text in streaming mode - execute them
                text, _ = _process_tool_calls_in_text(text, context="HTTP streaming")

                raw = None
                usage = {}
                stream_mode = True
                response_size = len(str(text).encode('utf-8'))

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
                                        logger.info("GLM web_search executed successfully via tool_calls array (HTTP non-streaming)")
                                except Exception as e:
                                    logger.debug(f"Failed to parse web_search tool call: {e}")
                else:
                    # No structured tool_calls - check for text-embedded tool calls
                    text, _ = _process_tool_calls_in_text(text, context="HTTP non-streaming")

                usage = raw.get("usage", {})

        # PHASE 2.1.2 (2025-10-21): Check for truncation and log to Supabase
        try:
            from src.utils.truncation_detector import (
                check_truncation,
                should_log_truncation,
                format_truncation_event,
                log_truncation_to_supabase_sync
            )

            # Check for truncation in the response
            if raw and isinstance(raw, dict):
                truncation_info = check_truncation(raw, model_name)

                if truncation_info.get('is_truncated'):
                    logger.warning(f"⚠️ Truncated response detected for {model_name} (finish_reason=length)")

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

        # Capture monitoring data for non-streaming path
        response_size = len(str(text).encode('utf-8'))
        stream_mode = stream

        # PHASE 1 (2025-10-24): Calculate response time for metadata
        ai_response_time_ms = int((time.time() - start_time) * 1000)

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
                "ai_response_time_ms": ai_response_time_ms,
            },
        )
    except pybreaker.CircuitBreakerError:
        # PHASE 1 (2025-10-18): Circuit breaker is OPEN - GLM API is unavailable
        logger.error("GLM circuit breaker OPEN - API unavailable")
        error = "Circuit breaker OPEN - GLM API unavailable"

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
        raise
    finally:
        # PHASE 3 (2025-10-23): ALWAYS record monitoring event (streaming and non-streaming)
        # This finally block ensures monitoring is recorded regardless of return path
        logger.info(f"[MONITORING_DEBUG] FINALLY BLOCK ENTERED for model={model_name}")

        try:
            response_time_ms = (time.time() - start_time) * 1000

            # Extract token usage for monitoring
            total_tokens = 0
            if usage:
                total_tokens = usage.get("total_tokens", 0)

            # Determine direction based on error state
            direction = "error" if error else "receive"

            # DIAGNOSTIC (2025-10-23): Debug logging to verify monitoring execution
            logger.info(f"[MONITORING_DEBUG] About to call record_glm_event for model={model_name}, tokens={total_tokens}, stream={stream_mode}, error={error}")

            # PHASE 4 (2025-10-23): Include continuation_id for session tracking
            metadata = {
                "model": model_name,
                "tokens": total_tokens,
                "streamed": stream_mode,
                "timestamp": log_timestamp()
            }
            if continuation_id:
                metadata["continuation_id"] = continuation_id

            record_glm_event(
                direction=direction,
                function_name="glm_chat.generate_content",
                data_size=response_size if not error else request_size,
                response_time_ms=response_time_ms,
                error=error if error else None,
                metadata=metadata
            )
            logger.info(f"[MONITORING_DEBUG] Successfully called record_glm_event")
        except Exception as e:
            logger.error(f"[MONITORING_DEBUG] FINALLY BLOCK ERROR: {e}", exc_info=True)


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
            logger.debug("GLM-4.6: Auto-setting tool_choice='auto' for function calling")

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


def chat_completions_create_with_continuation(
    sdk_client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    use_websearch: bool = False,
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
        sdk_client: ZhipuAI SDK client instance
        model: Model name
        messages: List of message dictionaries
        tools: Optional list of tools
        tool_choice: Optional tool choice
        temperature: Temperature value
        max_output_tokens: Maximum output tokens per request
        use_websearch: Whether to enable web search
        enable_continuation: Whether to enable automatic continuation (default: True)
        max_continuation_attempts: Maximum continuation attempts (default: 3)
        max_total_tokens: Maximum cumulative tokens across continuations (default: 32000)
        **kwargs: Additional parameters

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, and metadata
    """
    # Call the base function
    initial_response = chat_completions_create(
        sdk_client,
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        use_websearch=use_websearch,
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
                sdk_client,
                model=model,
                messages=cont_messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                use_websearch=use_websearch,
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

    PHASE 2.2.3 (2025-10-21): Concurrent Request Handling
    Refactored to use execute_with_session() helper per EXAI recommendation.

    PHASE 0.3 (2025-10-24): Added timeout enforcement to prevent provider hangs
    Uses GLM_SESSION_TIMEOUT env var (default: 30s) with active enforcement

    This function wraps chat_completions_create_with_continuation in a managed session
    to enable concurrent request handling without blocking. Each request gets its own
    isolated session with timeout handling and lifecycle tracking.

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
    # PHASE 0.3 (2025-10-24): Use GLM_SESSION_TIMEOUT from environment
    default_timeout = float(os.getenv("GLM_SESSION_TIMEOUT", "30"))
    enforce_timeout = os.getenv("ENFORCE_SESSION_TIMEOUT", "true").lower() == "true"

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
            use_websearch=use_websearch,
            enable_continuation=enable_continuation,
            max_continuation_attempts=max_continuation_attempts,
            max_total_tokens=max_total_tokens,
            **kwargs
        )

    # Execute within managed session with automatic session context addition
    # PHASE 0.3 (2025-10-24): Enable timeout enforcement to prevent hangs
    return session_manager.execute_with_session(
        provider="glm",
        model=model,
        func=_execute_glm_chat,
        request_id=request_id,
        timeout_seconds=timeout_seconds,
        add_session_context=True,
        enforce_timeout=enforce_timeout
    )


def chat_completions_create_messages_with_session(
    sdk_client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.3,
    timeout_seconds: Optional[float] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> dict:
    """
    Session-managed wrapper for GLM chat completions (message-based).

    PHASE 2.2.4 (2025-10-21): Concurrent Request Handling
    Provides session management for message-based chat completions.

    PHASE 0.3 (2025-10-24): Added timeout enforcement to prevent provider hangs
    Uses GLM_SESSION_TIMEOUT env var (default: 30s) with active enforcement

    This function wraps chat_completions_create in a managed session
    to enable concurrent request handling without blocking. Each request gets its own
    isolated session with timeout handling and lifecycle tracking.

    Args:
        sdk_client: ZhipuAI SDK client instance
        model: Model name (already resolved)
        messages: Pre-built message array in OpenAI format
        tools: Optional list of tools for function calling
        tool_choice: Optional tool choice directive
        temperature: Temperature value (default: 0.3)
        timeout_seconds: Optional timeout override (default: GLM_SESSION_TIMEOUT env var)
        request_id: Optional request ID (generated if not provided)
        **kwargs: Additional parameters (stream, thinking_mode, etc.)

    Returns:
        Dictionary with provider, model, content, tool_calls, usage, raw, metadata,
        and session context (session_id, request_id, duration_seconds)
    """
    from src.utils.concurrent_session_manager import get_session_manager

    # PHASE 0.3 (2025-10-24): Use GLM_SESSION_TIMEOUT from environment
    default_timeout = float(os.getenv("GLM_SESSION_TIMEOUT", "30"))
    enforce_timeout = os.getenv("ENFORCE_SESSION_TIMEOUT", "true").lower() == "true"

    session_manager = get_session_manager(default_timeout=timeout_seconds or default_timeout)

    def _execute_glm_chat():
        """Internal function to execute GLM chat within session."""
        return chat_completions_create(
            sdk_client,
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            **kwargs
        )

    # Execute within managed session with automatic session context addition
    # PHASE 0.3 (2025-10-24): Enable timeout enforcement to prevent hangs
    return session_manager.execute_with_session(
        provider="glm",
        model=model,
        func=_execute_glm_chat,
        request_id=request_id,
        timeout_seconds=timeout_seconds,
        add_session_context=True,
        enforce_timeout=enforce_timeout
    )


__all__ = [
    "build_payload",
    "generate_content",
    "chat_completions_create",
    "chat_completions_create_with_continuation",
    "chat_completions_create_with_session",
    "chat_completions_create_messages_with_session"
]

