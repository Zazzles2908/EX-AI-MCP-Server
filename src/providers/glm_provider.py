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

    return payload


def generate_content(
    prompt: str,
    *,
    sdk_client: Any,
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
    **kwargs
) -> ModelResponse:
    """
    Generate content using GLM API with circuit breaker protection.

    Args:
        prompt: User prompt
        sdk_client: ZhipuAI SDK client
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
        logger.debug(f"GLM request: model={model_name}, stream={stream}")

        # Apply circuit breaker and make request
        @breaker
        def _call_with_breaker():
            return sdk_client.chat.completions.create(**payload)

        result = _call_with_breaker()

        # Process result
        content = result.choices[0].message.content if result.choices else ""
        actual_model = result.model if hasattr(result, 'model') else model_name
        response_id = result.id if hasattr(result, 'id') else None
        created_ts = result.created if hasattr(result, 'created') else None
        usage = dict(result.usage) if hasattr(result, 'usage') and result.usage else {}

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
        raise RuntimeError(f"GLM generate_content failed: {e}")

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
            logger.error(f"Failed to record monitoring event: {e}", exc_info=True)


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
    for key, value in kwargs.items():
        if key not in payload:
            payload[key] = value

    try:
        # Make request with circuit breaker protection
        breaker = circuit_breaker_manager.get_breaker('glm')

        @breaker
        def _call_with_breaker():
            return sdk_client.chat.completions.create(**payload)

        result = _call_with_breaker()

        # Extract response data
        content = result.choices[0].message.content if result.choices else ""
        usage = dict(result.usage) if hasattr(result, 'usage') and result.usage else {}

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
        logger.error("GLM circuit breaker OPEN during chat_completions_create")
        raise RuntimeError("GLM API unavailable (circuit breaker open)")

    except Exception as e:
        logger.error("GLM chat_completions_create failed: %s", e)
        raise RuntimeError(f"GLM chat completion failed: {e}")
