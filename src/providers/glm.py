"""GLM (ZhipuAI) provider implementation."""

import logging
import os
from typing import Any, Optional

from .base import ModelProvider, ModelCapabilities, ModelResponse, ProviderType
from utils.http_client import HttpClient
from config import TimeoutConfig

# Import from new modules
from . import glm_config
from . import glm_chat
from . import glm_files

logger = logging.getLogger(__name__)


class GLMModelProvider(ModelProvider):
    """Provider implementation for GLM models (ZhipuAI)."""

    DEFAULT_BASE_URL = os.getenv("GLM_API_URL", "https://api.z.ai/api/paas/v4")

    # Use model configurations from glm_config module
    SUPPORTED_MODELS: dict[str, ModelCapabilities] = glm_config.SUPPORTED_MODELS

    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.base_url = base_url or self.DEFAULT_BASE_URL
        # Initialize HTTP client first (always needed as fallback)
        self.client = HttpClient(self.base_url, api_key=self.api_key, api_key_header="Authorization", api_key_prefix="Bearer ")
        # Prefer official SDK; fallback to HTTP if not available
        try:
            from zai import ZaiClient  # Official Z.ai SDK (compatible with MCP 1.20.0)
            self._use_sdk = True
            # CRITICAL FIX: Use zai-sdk instead of zhipuai for MCP 1.20.0 compatibility
            # zai-sdk requires PyJWT>=2.8.0 (compatible with MCP 1.20.0's PyJWT>=2.10.1)
            # zhipuai requires PyJWT<2.9.0 (INCOMPATIBLE with MCP 1.20.0)
            self._sdk_client = ZaiClient(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=TimeoutConfig.GLM_TIMEOUT_SECS,  # Use centralized timeout config
                max_retries=3,  # Retry logic with exponential backoff
            )
            logger.info(f"GLM provider using zai-sdk with base_url={self.base_url}, timeout={TimeoutConfig.GLM_TIMEOUT_SECS}s, max_retries=3")
        except Exception as e:
            logger.warning("zai-sdk unavailable or failed to init; falling back to HTTP client: %s", e, exc_info=True)
            self._use_sdk = False

    def get_provider_type(self) -> ProviderType:
        return ProviderType.GLM

    def validate_model_name(self, model_name: str) -> bool:
        resolved = self._resolve_model_name(model_name)
        return resolved in self.SUPPORTED_MODELS

    def supports_thinking_mode(self, model_name: str) -> bool:
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        return bool(capabilities and capabilities.supports_extended_thinking)

    def supports_images(self, model_name: str) -> bool:
        """Check if the model supports image inputs.

        Args:
            model_name: Name of the model to check

        Returns:
            True if the model supports images, False otherwise
        """
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        return bool(capabilities and capabilities.supports_images)

    def supports_streaming(self, model_name: str) -> bool:
        """Check if the model/provider supports streaming callbacks (on_chunk).

        Args:
            model_name: Name of the model to check

        Returns:
            True if the model supports streaming, False otherwise
        """
        # GLM provider does not support streaming callbacks
        return False

    def list_models(self, respect_restrictions: bool = True):
        return super().list_models(respect_restrictions=respect_restrictions)

    def get_model_configurations(self) -> dict[str, ModelCapabilities]:
        return self.SUPPORTED_MODELS

    def get_all_model_aliases(self) -> dict[str, list[str]]:
        return glm_config.get_all_model_aliases(self.SUPPORTED_MODELS)

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        return glm_config.get_capabilities(model_name, self.SUPPORTED_MODELS, self._resolve_model_name)

    def count_tokens(self, text: str, model_name: str) -> int:
        return glm_config.count_tokens(text, model_name)

    def _resolve_model_name(self, model_name: str) -> str:
        """Resolve model shorthand to full name.

        Args:
            model_name: Model name that may be an alias

        Returns:
            Resolved model name
        """
        # First check if it's already a base model name (case-sensitive exact match)
        if model_name in self.SUPPORTED_MODELS:
            return model_name

        # Check case-insensitively for both base models and aliases
        model_name_lower = model_name.lower()

        # Check base model names case-insensitively
        for base_model in self.SUPPORTED_MODELS:
            if base_model.lower() == model_name_lower:
                return base_model

        # Check aliases
        for base_model, capabilities in self.SUPPORTED_MODELS.items():
            if capabilities.aliases:
                if any(alias.lower() == model_name_lower for alias in capabilities.aliases):
                    return base_model

        # If not found, return as-is
        return model_name

    def get_effective_temperature(self, model_name: str, temperature: float) -> float:
        """Get effective temperature for model (with constraints).

        Args:
            model_name: Name of the model
            temperature: Requested temperature

        Returns:
            Effective temperature (clamped to model constraints)
        """
        capabilities = self.SUPPORTED_MODELS.get(model_name)
        if capabilities and hasattr(capabilities, 'temperature_constraint'):
            return capabilities.temperature_constraint.get_corrected_value(temperature)
        return temperature

    def _build_payload(self, prompt: str, system_prompt: Optional[str], model_name: str, temperature: float, max_output_tokens: Optional[int], **kwargs) -> dict:
        resolved = self._resolve_model_name(model_name)
        effective_temp = self.get_effective_temperature(resolved, temperature)
        return glm_chat.build_payload(prompt, system_prompt, resolved, effective_temp, max_output_tokens, **kwargs)

    def chat_completions_create(
        self,
        *,
        model: str,
        messages: list[dict[str, Any]],
        tools: Optional[list[Any]] = None,
        tool_choice: Optional[Any] = None,
        temperature: float = 0.3,
        **kwargs
    ) -> dict:
        """
        SDK-native chat completions method (message array format).

        This is the preferred method for tools and workflow systems that manage
        conversation history. It accepts pre-built message arrays instead of
        building messages from text prompts.

        PHASE 2.2.4 (2025-10-21): Updated to use session-managed wrapper for concurrent request handling.

        Args:
            model: Model name (will be resolved to canonical name)
            messages: Pre-built message array in OpenAI format
            tools: Optional list of tools for function calling
            tool_choice: Optional tool choice directive
            temperature: Temperature value (default: 0.3)
            **kwargs: Additional parameters (stream, thinking_mode, etc.)

        Returns:
            Normalized dict with provider, model, content, usage, metadata
        """
        resolved = self._resolve_model_name(model)
        effective_temp = self.get_effective_temperature(resolved, temperature)

        return glm_chat.chat_completions_create_messages_with_session(
            sdk_client=self._sdk_client,
            model=resolved,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=effective_temp,
            **kwargs
        )

    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        **kwargs,
    ) -> ModelResponse:
        resolved = self._resolve_model_name(model_name)
        effective_temp = self.get_effective_temperature(resolved, temperature)

        return glm_chat.generate_content(
            sdk_client=getattr(self, "_sdk_client", None),
            http_client=self.client,
            prompt=prompt,
            model_name=resolved,
            system_prompt=system_prompt,
            temperature=effective_temp,
            max_output_tokens=max_output_tokens,
            use_sdk=getattr(self, "_use_sdk", False),
            **kwargs
        )

    def upload_file(self, file_path: str, purpose: str = "agent") -> str:
        """Upload a file to GLM Files API and return its file id.

        Uses native SDK when available; falls back to HTTP client otherwise.
        """
        return glm_files.upload_file(
            sdk_client=getattr(self, "_sdk_client", None),
            http_client=self.client,
            file_path=file_path,
            purpose=purpose,
            use_sdk=getattr(self, "_use_sdk", False)
        )
