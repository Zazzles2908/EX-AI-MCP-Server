"""
GLM Tool Processor

Tool call processing for GLM provider.
Handles tool calls in text format and streaming responses.

This is part of the Phase 3 refactoring that split the large glm_chat.py
into focused modules:
- glm_provider.py: Core chat functions
- glm_streaming_handler.py: Streaming implementations
- glm_tool_processor.py: Tool call processing (this file)
"""

import json
import logging
import time
from typing import Any, Optional, Tuple

# Import provider base
from .base import ModelResponse, ProviderType

# Import circuit breaker manager
from src.resilience.circuit_breaker_manager import circuit_breaker_manager

# Import error handling framework
from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)


def _process_tool_calls_in_text(text: str, context: str = "unknown") -> Tuple[str, bool]:
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
    # Import text format handler
    try:
        from src.providers.text_format_handler import (
            has_text_format_tool_call,
            parse_and_execute_web_search
        )
    except ImportError:
        logger.warning("text_format_handler not available, skipping tool call processing")
        return text, True

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
        log_error(ErrorCode.TOOL_EXECUTION_ERROR, f"Tool call processing failed ({context}): {e}", exc_info=True)
        return text, False


def chat_completions_create_messages_with_session(
    messages: list[dict[str, Any]],
    *,
    sdk_client: Any,
    model: str = "glm-4.5-flash",
    temperature: float = 0.3,
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    stream: bool = False,
    stream_timeout: float = 300.0,
    on_chunk_callback: Optional[callable] = None,
    **kwargs
) -> ModelResponse:
    """
    Session-managed chat completions with messages array.

    This is the main entry point for GLM chat with session management.
    Handles both streaming and non-streaming responses with tool call processing.

    Args:
        messages: Message array in OpenAI format
        sdk_client: ZhipuAI SDK client
        model: Model name (default: glm-4.5-flash)
        temperature: Temperature (default 0.3)
        tools: Optional tools for function calling
        tool_choice: Optional tool choice directive
        stream: Enable streaming (default False)
        stream_timeout: Timeout for streaming in seconds (default 300)
        on_chunk_callback: Optional callback for streaming chunks
        **kwargs: Additional parameters

    Returns:
        ModelResponse with content, usage, and metadata

    Raises:
        RuntimeError: On API errors
    """
    from src.utils.concurrent_session_manager import get_session_manager

    # Get session manager
    session_manager = get_session_manager()
    start_time = time.time()

    def _execute_glm_chat():
        """Execute GLM chat within session."""
        breaker = circuit_breaker_manager.get_breaker('glm')

        try:
            # Build payload
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }

            if tools:
                payload["tools"] = tools

            if tool_choice:
                payload["tool_choice"] = tool_choice

            if stream:
                payload["stream"] = True

            # Add any additional kwargs
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value

            # Log request
            logger.debug(f"GLM chat: model={model}, stream={stream}")

            @breaker
            def _call_with_breaker():
                if stream:
                    return sdk_client.chat.completions.create(**payload)
                else:
                    return sdk_client.chat.completions.create(**payload)

            if stream:
                # Handle streaming
                return _handle_streaming_response(
                    sdk_client=sdk_client,
                    payload=payload,
                    stream_start=start_time,
                    stream_timeout=stream_timeout,
                    on_chunk_callback=on_chunk_callback
                )
            else:
                # Handle non-streaming
                return _handle_non_streaming_response(
                    sdk_client=sdk_client,
                    payload=payload,
                    start_time=start_time
                )

        except Exception as e:
            log_error(ErrorCode.PROVIDER_ERROR, f"GLM chat execution failed: {e}", exc_info=True)
            raise ProviderError("GLM", e) from e

    # Execute with session management
    result_container = session_manager.execute_sync(
        provider="glm",
        func=_execute_glm_chat
    )

    if "exception" in result_container:
        raise result_container["exception"]

    return result_container["result"]


def _handle_non_streaming_response(
    sdk_client: Any,
    payload: dict,
    start_time: float
) -> ModelResponse:
    """Handle non-streaming response."""
    breaker = circuit_breaker_manager.get_breaker('glm')
    model_name = payload["model"]

    @breaker
    def _call():
        return sdk_client.chat.completions.create(**payload)

    result = _call()

    # Extract response data
    content = result.choices[0].message.content if result.choices else ""
    usage = dict(result.usage) if hasattr(result, 'usage') and result.usage else {}
    actual_model = result.model if hasattr(result, 'model') else model_name
    response_id = result.id if hasattr(result, 'id') else None
    created_ts = result.created if hasattr(result, 'created') else None

    # Process tool calls from text if needed
    text, success = _process_tool_calls_in_text(content, context="non-streaming")

    response_size = len(str(text).encode('utf-8'))
    ai_response_time_ms = int((time.time() - start_time) * 1000)

    return ModelResponse(
        content=text,
        usage=usage,
        model_name=model_name,
        friendly_name="GLM",
        provider=ProviderType.GLM,
        metadata={
            "model": actual_model or model_name,
            "id": response_id,
            "created": created_ts,
            "tools": payload.get("tools"),
            "tool_choice": payload.get("tool_choice"),
            "streamed": False,
            "ai_response_time_ms": ai_response_time_ms,
        },
    )


def _handle_streaming_response(
    sdk_client: Any,
    payload: dict,
    stream_start: float,
    stream_timeout: float,
    on_chunk_callback: Optional[callable] = None
) -> ModelResponse:
    """Handle streaming response."""
    import pybreaker

    breaker = circuit_breaker_manager.get_breaker('glm')
    model_name = payload["model"]
    content_parts = []
    tool_calls_list = []
    actual_model = None
    response_id = None
    created_ts = None

    @breaker
    def _call():
        return sdk_client.chat.completions.create(**payload)

    resp = _call()

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
                        # Extract tool_calls from delta
                        if getattr(delta, "tool_calls", None):
                            tool_calls_list.extend(delta.tool_calls)
                            logger.debug(f"[WEBSEARCH_FIX] Captured tool_calls from streaming delta: {len(delta.tool_calls)} calls")

                        if getattr(delta, "content", None):
                            chunk_text = delta.content
                            content_parts.append(chunk_text)

                            # Forward chunk immediately if callback provided
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
                continue

    except TimeoutError as timeout_err:
        log_error(ErrorCode.TIMEOUT, f"GLM streaming timeout: {timeout_err}", exc_info=True)
        raise ProviderError("GLM", timeout_err) from timeout_err

    except Exception as stream_err:
        raise ProviderError("GLM", stream_err) from stream_err

    # Capture monitoring data before return
    text = "".join(content_parts)

    # Execute web_search tool calls from streaming
    if tool_calls_list:
        logger.info(f"[WEBSEARCH_FIX] Processing {len(tool_calls_list)} tool calls from SDK streaming")
        for tc in tool_calls_list:
            if hasattr(tc, 'function') and tc.function:
                func = tc.function
                if func.name == "web_search":
                    try:
                        args = func.arguments if hasattr(func, 'arguments') else "{}"
                        if isinstance(args, str):
                            search_data = json.loads(args)
                        else:
                            search_data = args
                        if search_data:
                            text = text + "\n\n[Web Search Results]\n" + json.dumps(search_data, indent=2, ensure_ascii=False)
                            logger.info("[WEBSEARCH_FIX] GLM web_search executed successfully via SDK streaming tool_calls")
                    except Exception as e:
                        log_error(ErrorCode.TOOL_EXECUTION_ERROR, f"[WEBSEARCH_FIX] Failed to parse web_search tool call: {e}", exc_info=True)
    else:
        # Fallback: Check for text-embedded tool calls (legacy format)
        text, _ = _process_tool_calls_in_text(text, context="SDK streaming")

    raw = None
    usage = {}
    stream_mode = True
    response_size = len(str(text).encode('utf-8'))

    # Calculate response time for metadata
    ai_response_time_ms = int((time.time() - stream_start) * 1000)

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
