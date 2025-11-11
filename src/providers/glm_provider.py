"""
GLM Provider - Core Chat Functions

Core chat generation functionality for GLM provider.
Handles payload building, content generation, and chat completions.

This is part of the Phase 3 refactoring that split the large glm_chat.py
into focused modules:
- glm_provider.py: Core chat functions (this file)
- glm_streaming_handler.py: Streaming implementations
- glm_tool_processor.py: Tool call processing
"""

import json
import logging
import os
import time
from typing import Any, Optional

from .base import ModelResponse, ProviderType

# Import monitoring utilities
from utils.monitoring import record_glm_event
from utils.timezone_helper import log_timestamp

# Import circuit breaker
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

from src.daemon.error_handling import ProviderError, ErrorCode, log_error

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
        payload["max_tokens"] = max_output_tokens

    # Handle tools if provided
    if kwargs.get("tools"):
        payload["tools"] = kwargs["tools"]

    if kwargs.get("tool_choice"):
        payload["tool_choice"] = kwargs["tool_choice"]

    # CRITICAL FIX (2025-11-05): Filter out thinking_mode parameter from kwargs
    # This prevents thinking_mode from being passed to Completions.create()
    if "thinking_mode" in kwargs:
        thinking_mode_value = kwargs["thinking_mode"]
        if thinking_mode_value and thinking_mode_value != "disabled":
            logger.debug(f"[GLM_PROVIDER] build_payload: thinking_mode='{thinking_mode_value}' ignored for GLM provider")
        else:
            logger.debug(f"[GLM_PROVIDER] build_payload: thinking_mode disabled or empty")
        # Remove thinking_mode from kwargs to prevent it from being added to payload
        kwargs = {k: v for k, v in kwargs.items() if k != "thinking_mode"}

    # Add any remaining kwargs to payload
    for key, value in kwargs.items():
        if key not in payload:  # Don't override existing keys
            payload[key] = value

    return payload


def generate_content(
    prompt: str,
    *,
    sdk_client: Any,
    http_client: Any,
    model_name: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3,
    max_output_tokens: Optional[int] = None,
    tools: Optional[list] = None,
    tool_choice: Optional[Any] = None,
    stream: bool = False,
    stream_timeout: float = 300.0,
    request_id: Optional[str] = None,
    on_chunk_callback: Optional[callable] = None,
    session_id: Optional[str] = None,
    use_sdk: bool = False,
    **kwargs
) -> ModelResponse:
    """
    Generate content using GLM API with circuit breaker protection.

    Args:
        prompt: User prompt
        sdk_client: ZhipuAI SDK client (can be None if use_sdk=False)
        http_client: HTTP client for fallback
        model_name: Model name
        system_prompt: Optional system prompt
        temperature: Temperature (default 0.3)
        max_output_tokens: Optional max tokens
        tools: Optional tools for function calling
        tool_choice: Optional tool choice directive
        stream: Enable streaming (default False)
        stream_timeout: Stream timeout in seconds (default 300)
        request_id: Optional request ID
        on_chunk_callback: Optional callback for streaming chunks
        session_id: Optional session ID
        use_sdk: Whether to use SDK client (default False)
        **kwargs: Additional parameters

    Returns:
        ModelResponse with content and metadata

    Raises:
        RuntimeError: On API errors
    """
    # Get circuit breaker
    breaker = circuit_breaker_manager.get_breaker('glm')
    start_time = time.time()
    error = None
    request_size = len(str({"prompt": prompt, "kwargs": kwargs}).encode('utf-8'))
    response_size = 0
    stream_mode = stream

    try:
        try:
            # Build payload
            payload = build_payload(
                prompt=prompt,
                system_prompt=system_prompt,
                model_name=model_name,
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                stream=stream,
                tools=tools,
                tool_choice=tool_choice,
                **kwargs
            )

            # Log request details
            logger.debug(f"GLM request: model={model_name}, stream={stream}, use_sdk={use_sdk}")

            # Use SDK if available, otherwise fall back to HTTP client
            if use_sdk and sdk_client:
                # Apply circuit breaker and make request with SDK
                @breaker
                def _call_with_breaker():
                    return sdk_client.chat.completions.create(**payload)
            else:
                # Fall back to HTTP client
                @breaker
                def _call_with_breaker():
                    return http_client.post("/chat/completions", json=payload)

            result = _call_with_breaker()
        except Exception as inner_e:
            import traceback
            log_error(ErrorCode.PROVIDER_ERROR, f"GLM generate_content failed: {type(inner_e).__name__}: {inner_e}", request_id, exc_info=True)
            raise ProviderError("GLM", inner_e) from inner_e

        # DEBUG: Log result type and attributes
        logger.debug(f"GLM result type: {type(result)}, has choices: {hasattr(result, 'choices')}, is dict: {isinstance(result, dict)}")
        if not isinstance(result, dict):
            logger.debug(f"GLM result attributes: {dir(result)}")

        # Process result - handle both SDK object and HTTP dict responses
        if isinstance(result, dict):
            # HTTP client returns dict
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            actual_model = result.get("model", model_name)
            response_id = result.get("id")
            created_ts = result.get("created")
            usage = result.get("usage", {})
        else:
            # SDK returns object - handle both zai-sdk StreamResponse and regular response
            # zai-sdk returns StreamResponse which needs to be consumed
            if hasattr(result, '__iter__') and not hasattr(result, 'choices'):
                # StreamResponse - consume the stream
                chunks = []
                for chunk in result:
                    if hasattr(chunk, 'choices') and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            chunks.append(delta.content)
                content = ''.join(chunks)
                # Get metadata from last chunk
                actual_model = chunk.model if hasattr(chunk, 'model') else model_name
                response_id = chunk.id if hasattr(chunk, 'id') else None
                created_ts = chunk.created if hasattr(chunk, 'created') else None
                usage = {}  # Stream responses don't have usage info
            else:
                # Regular response object
                content = result.choices[0].message.content if result.choices else ""
                actual_model = result.model if hasattr(result, 'model') else model_name
                response_id = result.id if hasattr(result, 'id') else None
                created_ts = result.created if hasattr(result, 'created') else None

                # CRITICAL FIX: Handle CompletionUsage object with comprehensive error handling
                usage = {}
                try:
                    if hasattr(result, 'usage') and result.usage:
                        # Try multiple approaches to safely extract usage info
                        if isinstance(result.usage, dict):
                            # Already a dict, use it directly
                            usage = result.usage.copy()
                        elif hasattr(result.usage, '__dict__'):
                            # Object with attributes, extract them safely
                            usage = {}
                            for attr in ['prompt_tokens', 'completion_tokens', 'total_tokens', 'cost']:
                                if hasattr(result.usage, attr):
                                    usage[attr] = getattr(result.usage, attr, 0)
                        else:
                            # Try getattr with defaults
                            usage = {
                                "prompt_tokens": getattr(result.usage, 'prompt_tokens', 0),
                                "completion_tokens": getattr(result.usage, 'completion_tokens', 0),
                                "total_tokens": getattr(result.usage, 'total_tokens', 0),
                            }

                        logger.debug(f"[GLM_PROVIDER] Successfully extracted usage: {usage}")
                    else:
                        logger.debug("[GLM_PROVIDER] No usage info in result")
                except Exception as e:
                    log_error(ErrorCode.INTERNAL_ERROR, f"Failed to extract usage info: {e}", request_id, exc_info=True)
                    usage = {}

        response_size = len(str(content).encode('utf-8'))

        # Return successful response
        return ModelResponse(
            content=content or "",
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
            },
        )

    except pybreaker.CircuitBreakerError:
        # Circuit breaker is OPEN - GLM API is unavailable
        log_error(ErrorCode.SERVICE_UNAVAILABLE, "GLM circuit breaker OPEN - API unavailable", request_id)
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
        log_error(ErrorCode.PROVIDER_ERROR, f"GLM generate_content failed: {e}", request_id, exc_info=True)
        error = str(e)
        raise ProviderError("GLM", e) from e

    finally:
        # Record monitoring event
        try:
            response_time_ms = (time.time() - start_time) * 1000

            # Extract token usage
            total_tokens = 0
            # Note: usage would be available in the result if successful
            # For error tracking, we'll use 0

            # Determine direction based on error state
            direction = "error" if error else "receive"

            metadata = {
                "model": model_name,
                "tokens": total_tokens,
                "streamed": stream_mode,
                "timestamp": log_timestamp(),
            }
            if session_id:
                metadata["session_id"] = session_id

            record_glm_event(
                direction=direction,
                function_name="glm_provider.generate_content",
                data_size=response_size if not error else request_size,
                response_time_ms=response_time_ms,
                error=error if error else None,
                metadata=metadata
            )

        except Exception as e:
            log_error(ErrorCode.INTERNAL_ERROR, f"Failed to record monitoring event: {e}", request_id, exc_info=True)


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
        temperature: Temperature value (default 0.3)
        **kwargs: Additional parameters (stream, thinking_mode, etc.)

    Returns:
        Normalized dict with provider, model, content, usage, metadata
    """
    # Build payload from messages
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    # Add optional parameters
    if tools:
        payload["tools"] = tools

    if tool_choice:
        payload["tool_choice"] = tool_choice

    # Add any additional kwargs
    # CRITICAL FIX (2025-11-05): Transform thinking_mode parameter for GLM provider
    # GLM expects thinking mode as {"thinking": {"type": "enabled"}} format, not thinking_mode parameter
    logger.info(f"[GLM_PROVIDER] Processing {len(kwargs)} kwargs: {list(kwargs.keys())}")
    for key, value in kwargs.items():
        if key in payload:
            logger.debug(f"[GLM_PROVIDER] Skipping key '{key}' (already in payload)")
            continue

        # CRITICAL FIX: Explicitly filter out thinking_mode before it reaches Completions.create()
        # This prevents the error "Completions.create() got an unexpected keyword argument 'thinking_mode'"
        if key == "thinking_mode":
            if value and value != "disabled":
                # Convert thinking_mode string to GLM's thinking parameter format
                payload["thinking"] = {"type": "enabled"}
                logger.warning(f"[GLM_PROVIDER] Transformed thinking_mode='{value}' to GLM thinking format. Note: GLM's thinking mode support is limited.")
            else:
                logger.debug(f"[GLM_PROVIDER] Skipping thinking_mode (value={value})")
            continue

        # CRITICAL FIX (2025-11-06): Filter out on_chunk parameter
        # GLM SDK doesn't support streaming callbacks (on_chunk)
        if key == "on_chunk":
            logger.warning(f"[GLM_PROVIDER] Skipping on_chunk parameter (streaming not supported) - value type: {type(value)}")
            continue

        # Filter out other thinking-related parameters that GLM doesn't understand
        if key not in ("kimi_thinking",):
            payload[key] = value
            logger.debug(f"[GLM_PROVIDER] Added key '{key}' to payload")

    logger.info(f"[GLM_PROVIDER] Final payload keys: {list(payload.keys())}")

    try:
        # CRITICAL DEBUG: Log thinking_mode status before calling Completions.create()
        if "thinking_mode" in payload:
            log_error(ErrorCode.INTERNAL_ERROR, f"CRITICAL: thinking_mode is still in payload! Payload keys: {list(payload.keys())}")

        # Make request with circuit breaker protection
        breaker = circuit_breaker_manager.get_breaker('glm')

        @breaker
        def _call_with_breaker():
            # CRITICAL DEBUG: Check payload before calling Completions.create()
            if "thinking_mode" in payload:
                log_error(ErrorCode.INTERNAL_ERROR, f"ERROR: Passing thinking_mode to Completions.create()! Payload: {payload}")
                raise ValueError(f"Internal error: thinking_mode not filtered from payload. Keys: {list(payload.keys())}")
            return sdk_client.chat.completions.create(**payload)

        result = _call_with_breaker()

        try:
            # Extract response data
            content = result.choices[0].message.content if result.choices else ""
            # CRITICAL FIX: Handle CompletionUsage object with comprehensive error handling
            usage = {}
            if hasattr(result, 'usage') and result.usage:
                # Try multiple approaches to safely extract usage info
                if isinstance(result.usage, dict):
                    # Already a dict, use it directly
                    usage = result.usage.copy()
                elif hasattr(result.usage, '__dict__'):
                    # Object with attributes, extract them safely
                    usage = {}
                    for attr in ['prompt_tokens', 'completion_tokens', 'total_tokens', 'cost']:
                        if hasattr(result.usage, attr):
                            usage[attr] = getattr(result.usage, attr, 0)
                else:
                    # Try getattr with defaults
                    usage = {
                        "prompt_tokens": getattr(result.usage, 'prompt_tokens', 0),
                        "completion_tokens": getattr(result.usage, 'completion_tokens', 0),
                        "total_tokens": getattr(result.usage, 'total_tokens', 0),
                    }
                logger.debug(f"[GLM_PROVIDER] chat_completions: Successfully extracted usage: {usage}")
            else:
                logger.debug("[GLM_PROVIDER] chat_completions: No usage info in result")
        except Exception as e:
            log_error(ErrorCode.INTERNAL_ERROR, f"Failed to extract usage info: {type(e).__name__}: {e}", exc_info=True)
            usage = {}

        # Return normalized response
        return {
            "provider": "glm",
            "model": model,
            "content": content,
            "usage": usage,
            "metadata": {
                "id": result.id if hasattr(result, 'id') else None,
                "created": result.created if hasattr(result, 'created') else None,
                "finish_reason": result.choices[0].finish_reason if result.choices else None,
            },
            "raw": result,
        }

    except pybreaker.CircuitBreakerError:
        log_error(ErrorCode.SERVICE_UNAVAILABLE, "GLM circuit breaker OPEN during chat_completions_create")
        raise ProviderError("GLM", Exception("GLM API unavailable (circuit breaker open)"))

    except Exception as e:
        log_error(ErrorCode.PROVIDER_ERROR, f"GLM chat_completions_create failed: {e}", exc_info=True)
        raise ProviderError("GLM", e) from e
