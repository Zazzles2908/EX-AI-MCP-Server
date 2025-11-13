"""
OpenAI Compatible Provider - Content Generation Module

Handles content generation, streaming, and response processing.
Provides the main generate_content method and all related helper functions.

This is part of the refactoring that split the large openai_compatible.py
into focused modules:
- openai_config.py: Configuration and validation
- openai_client.py: Client management
- openai_capabilities.py: Model capabilities
- openai_token_manager.py: Token management
- openai_error_handler.py: Error handling
- openai_content_generator.py: Content generation (this file)
- openai_compatible.py: Main provider class
"""

import json
import logging
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from .base import ModelCapabilities, ModelResponse, ProviderType

from src.daemon.error_handling import ProviderError, ErrorCode, log_error

logger = logging.getLogger(__name__)


class OpenAIContentGenerator:
    """
    Handles content generation for OpenAI-compatible providers.

    Provides:
    - Main content generation with retries
    - Streaming support
    - Response extraction and normalization
    - Monitoring integration
    - Special endpoint handling (o3-pro)
    """

    def __init__(
        self,
        client_manager,
        capabilities_manager,
        token_manager,
        error_handler,
        friendly_name: str
    ):
        """
        Initialize content generator.

        Args:
            client_manager: OpenAIClientManager instance
            capabilities_manager: OpenAICapabilities instance
            token_manager: OpenAITokenManager instance
            error_handler: OpenAIErrorHandler instance
            friendly_name: Provider friendly name for responses
        """
        self._client_manager = client_manager
        self._capabilities_manager = capabilities_manager
        self._token_manager = token_manager
        self._error_handler = error_handler
        self.FRIENDLY_NAME = friendly_name

        # Cache for Kimi context token
        self._kimi_cache_token = None

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        images: Optional[List[str]] = None,
        **kwargs,
    ) -> "ModelResponse":
        """
        Generate content using the OpenAI-compatible API.

        Args:
            prompt: User prompt
            model_name: Model to use
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_output_tokens: Maximum output tokens
            images: Optional list of image paths
            **kwargs: Additional parameters (tools, stream, etc.)

        Returns:
            ModelResponse with generated content
        """
        # Initialize monitoring context
        from .base import ProviderType
        is_kimi = self._capabilities_manager.get_provider_type() == ProviderType.KIMI
        start_time = time.time() if is_kimi else None
        request_size = len(str(prompt).encode('utf-8')) if is_kimi else 0
        error = None
        response_size = 0
        total_tokens = 0

        # Extract continuation_id for session tracking
        continuation_id = kwargs.get("continuation_id") or kwargs.get("conversation_id")
        if continuation_id and not continuation_id.strip():
            continuation_id = None

        try:
            # Validate model
            if not self._capabilities_manager.validate_model_name(model_name):
                raise ValueError(
                    f"Model '{model_name}' not in allowed models list"
                )

            # Resolve model and parameters
            resolved_model = self._resolve_model_name(model_name)
            effective_temperature = self._get_effective_temperature(resolved_model, temperature)

            # Validate parameters if supported
            if effective_temperature is not None:
                self._capabilities_manager.validate_parameters(
                    resolved_model, effective_temperature
                )

            # Build messages
            messages = self._build_messages(
                prompt, system_prompt, images, resolved_model, **kwargs
            )

            # Build completion parameters
            completion_params = self._build_completion_params(
                resolved_model,
                messages,
                effective_temperature,
                max_output_tokens,
                **kwargs
            )

            # Log sanitized payload
            self._log_sanitized_payload(completion_params)

            # Execute chat request with retries
            result = self._execute_chat_request(completion_params, **kwargs)

            # Extract metrics
            response_size = len(str(result.content).encode('utf-8'))
            total_tokens = result.usage.get("total_tokens", 0) if result.usage else 0

            return result

        except Exception as e:
            error = str(e)
            log_error(ErrorCode.PROVIDER_ERROR, f"Content generation failed: {error}", exc_info=True)
            raise ProviderError("OpenAI", e) from e

        finally:
            # Record monitoring event if Kimi
            if is_kimi and start_time is not None:
                try:
                    from utils.monitoring import record_kimi_event
                    from utils.timezone_helper import log_timestamp

                    response_time_ms = (time.time() - start_time) * 1000
                    direction = "error" if error else "receive"

                    metadata = {
                        "model": model_name,
                        "tokens": total_tokens,
                        "timestamp": log_timestamp()
                    }
                    if continuation_id:
                        metadata["continuation_id"] = continuation_id

                    record_kimi_event(
                        direction=direction,
                        function_name="openai_compatible.generate_content",
                        data_size=response_size if not error else request_size,
                        response_time_ms=response_time_ms,
                        error=error if error else None,
                        metadata=metadata
                    )
                except Exception as e:
                    log_error(ErrorCode.INTERNAL_ERROR, f"Failed to record monitoring event: {e}", exc_info=True)

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model name (placeholder for future expansion)."""
        return model_name

    def _get_effective_temperature(
        self, model_name: str, temperature: float
    ) -> Optional[float]:
        """Get effective temperature for model."""
        try:
            capabilities = self._capabilities_manager.get_capabilities(model_name)
            if capabilities and getattr(capabilities, "supports_temperature", True):
                return temperature
            return None
        except Exception:
            return temperature

    def _build_messages(
        self,
        prompt: str,
        system_prompt: Optional[str],
        images: Optional[List[str]],
        model_name: str,
        **kwargs
    ) -> List[Dict]:
        """Build messages array for API call."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # User content: text + optional images
        user_content = [{"type": "text", "text": prompt}]

        if images and self._capabilities_manager._supports_vision(model_name):
            for image_path in images:
                try:
                    image_content = self._token_manager.process_image(image_path)
                    if image_content:
                        user_content.append(image_content)
                except Exception as e:
                    logging.warning(f"Failed to process image {image_path}: {e}")
        elif images:
            logging.warning(
                f"Model {model_name} does not support images, "
                f"ignoring {len(images)} image(s)"
            )

        # Handle file_ids
        file_ids = kwargs.get("file_ids") or []
        if file_ids and bool(kwargs.get("use_input_file_parts", False)):
            for fid in file_ids:
                try:
                    user_content.append({"type": "input_file", "file_id": fid})
                except Exception as e:
                    logging.warning(f"Failed to attach file_id {fid}: {e}")

        # Add user message
        if len(user_content) == 1:
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": user_content})

        return messages

    def _build_completion_params(
        self,
        model_name: str,
        messages: List[Dict],
        temperature: Optional[float],
        max_output_tokens: Optional[int],
        **kwargs
    ) -> Dict:
        """Build completion parameters."""
        completion_params = {"model": model_name, "messages": messages}

        # Inject provider-specific headers
        self._inject_provider_headers(**kwargs)

        # Temperature
        if temperature is not None:
            completion_params["temperature"] = temperature

        # Max tokens
        self._handle_max_tokens(completion_params, model_name, max_output_tokens, **kwargs)

        # Optional parameters
        if kwargs.get("tools"):
            completion_params["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            completion_params["tool_choice"] = kwargs["tool_choice"]
        if "stream" in kwargs:
            completion_params["stream"] = kwargs["stream"]
        if isinstance(kwargs.get("extra_headers"), dict):
            completion_params["extra_headers"] = kwargs["extra_headers"]
        if isinstance(kwargs.get("extra_body"), dict):
            completion_params["extra_body"] = kwargs["extra_body"]

        # Additional parameters
        for key in ["top_p", "frequency_penalty", "presence_penalty", "seed", "stop"]:
            if key in kwargs:
                if temperature is None and key in ["top_p", "frequency_penalty", "presence_penalty"]:
                    continue
                completion_params[key] = kwargs[key]

        return completion_params

    def _inject_provider_headers(self, **kwargs) -> None:
        """Inject provider-specific headers."""
        try:
            client = self._client_manager.client
            hdrs = getattr(client, "_default_headers", None)

            if hdrs is None:
                return

            # Idempotency key
            call_key = kwargs.get("_call_key") or kwargs.get("call_key")
            if call_key:
                hdrs["Idempotency-Key"] = str(call_key)

            # Kimi context cache token
            cache_token = kwargs.get("_kimi_cache_token") or getattr(self, "_kimi_cache_token", None)
            if cache_token:
                hdrs["Msh-Context-Cache-Token"] = str(cache_token)

            # Tracing
            hdrs.setdefault("Msh-Trace-Mode", "on")

        except Exception as e:
            logger.debug(f"Failed to set provider-specific headers: {e}")

    def _handle_max_tokens(
        self,
        completion_params: Dict,
        model_name: str,
        max_output_tokens: Optional[int],
        **kwargs
    ) -> None:
        """Handle max_tokens parameter."""
        try:
            # Import here to avoid circular dependency
            from config import DEFAULT_MAX_OUTPUT_TOKENS, KIMI_MAX_OUTPUT_TOKENS, ENFORCE_MAX_TOKENS
            from .base import ProviderType

            if max_output_tokens:
                # Explicitly provided - always use it
                completion_params["max_tokens"] = int(max_output_tokens)
            elif ENFORCE_MAX_TOKENS:
                # Not provided, but enforcement is enabled - use provider-specific default
                provider_type = self._capabilities_manager.get_provider_type()
                if provider_type == ProviderType.KIMI and KIMI_MAX_OUTPUT_TOKENS > 0:
                    completion_params["max_tokens"] = int(KIMI_MAX_OUTPUT_TOKENS)
                    logger.debug(
                        f"Using default max_tokens={KIMI_MAX_OUTPUT_TOKENS} for Kimi "
                        f"(ENFORCE_MAX_TOKENS=true)"
                    )
                elif DEFAULT_MAX_OUTPUT_TOKENS > 0:
                    completion_params["max_tokens"] = int(DEFAULT_MAX_OUTPUT_TOKENS)
                    logger.debug(
                        f"Using default max_tokens={DEFAULT_MAX_OUTPUT_TOKENS} "
                        f"(ENFORCE_MAX_TOKENS=true)"
                    )
            # else: Don't set max_tokens, let the model use its default

        except ImportError:
            logger.debug("Config module not available, skipping max_tokens handling")

    def _log_sanitized_payload(self, completion_params: Dict) -> None:
        """Log sanitized payload for debugging."""
        try:
            def _sanitize_value(v):
                if isinstance(v, dict):
                    return {k: _sanitize_value(v) for k, v in v.items()
                           if k.lower() not in {"api_key", "authorization"}}
                if isinstance(v, list):
                    return [_sanitize_value(x) for x in v]
                return v

            logger.info(
                "chat.completions.create payload (sanitized): %s",
                json.dumps(_sanitize_value(completion_params), ensure_ascii=False)
            )
        except Exception as e:
            logger.debug(f"Failed to log sanitized payload: {e}")

    def _execute_chat_request(
        self,
        completion_params: Dict,
        **kwargs
    ) -> "ModelResponse":
        """Execute chat completion request with retry logic."""
        from .base import ModelResponse, ProviderType

        # Use retry mixin if available
        if hasattr(self, "with_retry"):
            return self.with_retry(
                self._execute_single_request,
                completion_params,
                **kwargs
            )
        else:
            return self._execute_single_request(completion_params, **kwargs)

    def _execute_single_request(
        self,
        completion_params: Dict,
        **kwargs
    ) -> "ModelResponse":
        """Execute single chat completion request."""
        from .base import ModelResponse, ProviderType

        client = self._client_manager.client

        # Attach idempotency per attempt
        req_opts = {}
        try:
            call_key = kwargs.get("_call_key") or kwargs.get("call_key")
            if call_key:
                req_opts["idempotency_key"] = str(call_key)
        except Exception:
            pass

        response = client.chat.completions.create(**completion_params, **req_opts)

        # Capture Kimi context-cache token
        self._capture_kimi_cache_token(response)

        # Handle streaming
        if completion_params.get("stream") is True:
            return self._handle_streaming_response(response, completion_params, **kwargs)

        # Handle non-streaming
        return self._handle_non_streaming_response(response, completion_params)

    def _capture_kimi_cache_token(self, response) -> None:
        """Capture Kimi context-cache token from response."""
        try:
            headers = (
                getattr(response, "response_headers", None) or
                getattr(self._client_manager.client, "_last_response_headers", None)
            )
            if headers:
                for k, v in headers.items():
                    lk = k.lower()
                    if lk in ("msh-context-cache-token-saved", "msh_context_cache_token_saved"):
                        self._kimi_cache_token = v
                        logger.info("Kimi context cache saved token suffix=%s", str(v)[-6:])
                        break
        except Exception as e:
            logger.debug(f"Failed to capture Kimi cache token: {e}")

    def _handle_streaming_response(
        self,
        response,
        completion_params: Dict,
        **kwargs
    ) -> "ModelResponse":
        """Handle streaming response."""
        from .base import ModelResponse

        content_parts = []
        actual_model = None
        response_id = None
        created_ts = None

        # Get on_chunk callback
        on_chunk_callback = kwargs.get("on_chunk")

        try:
            for event in response:
                try:
                    choice = event.choices[0]
                    delta = getattr(choice, "delta", None)
                    if delta and getattr(delta, "content", None):
                        chunk_text = delta.content
                        content_parts.append(chunk_text)

                        # Forward chunk if callback provided
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
                    logger.debug(f"Failed to process streaming event: {e}")
                    continue
        except Exception as stream_err:
            log_error(ErrorCode.PROVIDER_ERROR, f"Streaming failed: {stream_err}", exc_info=True)
            raise ProviderError("OpenAI", stream_err) from stream_err

        content = "".join(content_parts)
        return ModelResponse(
            content=content,
            usage=None,
            model_name=completion_params["model"],
            friendly_name=self.FRIENDLY_NAME,
            provider=self._capabilities_manager.get_provider_type(),
            metadata={
                "finish_reason": "stop",
                "model": actual_model or completion_params["model"],
                "id": response_id,
                "created": created_ts,
                "streamed": True,
            },
        )

    def _handle_non_streaming_response(
        self,
        response,
        completion_params: Dict
    ) -> "ModelResponse":
        """Handle non-streaming response."""
        from .base import ModelResponse

        # Extract content
        content = self._extract_output_text(response)

        # Extract usage
        usage = self._token_manager.extract_usage(response)

        # Build metadata
        actual_model = getattr(response, "model", None) or completion_params["model"]
        response_id = getattr(response, "id", None)
        created_ts = getattr(response, "created", None)

        return ModelResponse(
            content=content,
            usage=usage,
            model_name=completion_params["model"],
            friendly_name=self.FRIENDLY_NAME,
            provider=self._capabilities_manager.get_provider_type(),
            metadata={
                "model": actual_model,
                "id": response_id,
                "created": created_ts,
                "streamed": False,
            },
        )

    def _extract_output_text(self, response) -> str:
        """Extract output text from response."""
        # Try multiple extraction methods
        content = None

        try:
            choices = getattr(response, "choices", []) or []
            if choices:
                choice0 = choices[0]
                msg = getattr(choice0, "message", None)
                if msg is not None and getattr(msg, "content", None):
                    content = msg.content
        except Exception as e:
            logger.debug(f"Failed to extract message content: {e}")

        if not content:
            try:
                if getattr(response, "content", None):
                    content = response.content
            except Exception as e:
                logger.debug(f"Failed to extract response content: {e}")

        return content or ""

    def _generate_with_responses_endpoint(
        self,
        model_name: str,
        messages: List[Dict],
        temperature: float,
        max_output_tokens: Optional[int],
        **kwargs
    ) -> "ModelResponse":
        """
        Generate content using responses endpoint (for o3-pro).

        NOTE: This method is currently unused. The o3-pro model falls back to
        the standard chat completion endpoint. This placeholder is retained for
        future implementation if needed.

        For now, this method should not be called as o3-pro models use the
        standard chat completion flow.
        """
        # This is a placeholder for future implementation
        # Currently not used - o3-pro models use standard chat completions
        logger.warning(
            f"_generate_with_responses_endpoint called for {model_name}, "
            f"but responses endpoint is not yet implemented. "
            f"This should not happen as o3-pro models use chat completions."
        )
        # Fall back to standard method instead of raising
        completion_params = self._build_completion_params(
            model_name,
            messages,
            temperature,
            max_output_tokens,
            **kwargs
        )
        return self._execute_chat_request(completion_params, **kwargs)

    def safe_extract_output_text(self, response) -> str:
        """Safely extract output text from response."""
        return self._extract_output_text(response)
