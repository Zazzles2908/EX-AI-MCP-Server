"""Kimi (Moonshot) provider implementation."""

import logging
import os
from typing import Any, Optional

from .base import ModelProvider, ModelCapabilities, ModelResponse, ProviderType
from .openai_compatible import OpenAICompatibleProvider

# Import from new modules
from . import kimi_config
from . import kimi_cache
from . import kimi_chat
from . import kimi_files

logger = logging.getLogger(__name__)


class KimiModelProvider(OpenAICompatibleProvider):
    """Provider implementation for Kimi (Moonshot) models."""

    # API configuration
    DEFAULT_BASE_URL = os.getenv("KIMI_API_URL", "https://api.moonshot.ai/v1")

    # Use model configurations from kimi_config module
    SUPPORTED_MODELS: dict[str, ModelCapabilities] = kimi_config.SUPPORTED_MODELS


    def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
        self.base_url = base_url or self.DEFAULT_BASE_URL
        # Provider-specific timeout overrides via env
        try:
            rt = os.getenv("KIMI_READ_TIMEOUT_SECS", "").strip()
            ct = os.getenv("KIMI_CONNECT_TIMEOUT_SECS", "").strip()
            wt = os.getenv("KIMI_WRITE_TIMEOUT_SECS", "").strip()
            pt = os.getenv("KIMI_POOL_TIMEOUT_SECS", "").strip()
            if rt:
                kwargs["read_timeout"] = float(rt)
            if ct:
                kwargs["connect_timeout"] = float(ct)
            if wt:
                kwargs["write_timeout"] = float(wt)
            if pt:
                kwargs["pool_timeout"] = float(pt)
            # Provide a Kimi-specific sane default if nothing configured
            if "read_timeout" not in kwargs and not rt:
                # Default to 300s to avoid multi-minute hangs on web-enabled prompts
                kwargs["read_timeout"] = float(os.getenv("KIMI_DEFAULT_READ_TIMEOUT_SECS", "300"))
        except Exception:
            pass
        super().__init__(api_key, base_url=self.base_url, **kwargs)

    def get_provider_type(self) -> ProviderType:
        return ProviderType.KIMI

    def validate_model_name(self, model_name: str) -> bool:
        # Allow aliases to pass validation
        resolved = self._resolve_model_name(model_name)
        return resolved in self.SUPPORTED_MODELS

    def supports_thinking_mode(self, model_name: str) -> bool:
        resolved = self._resolve_model_name(model_name)
        capabilities = self.SUPPORTED_MODELS.get(resolved)
        return bool(capabilities and capabilities.supports_extended_thinking)

    def list_models(self, respect_restrictions: bool = True):
        # Use base implementation with restriction awareness
        return super().list_models(respect_restrictions=respect_restrictions)

    def get_model_configurations(self) -> dict[str, ModelCapabilities]:
        # Use our static SUPPORTED_MODELS
        return self.SUPPORTED_MODELS

    def get_all_model_aliases(self) -> dict[str, list[str]]:
        return kimi_config.get_all_model_aliases(self.SUPPORTED_MODELS)

    def get_capabilities(self, model_name: str) -> ModelCapabilities:
        return kimi_config.get_capabilities(model_name, self.SUPPORTED_MODELS, self._resolve_model_name)

    def count_tokens(self, text: str, model_name: str) -> int:
        return kimi_config.count_tokens(text, model_name)

    def _lru_key(self, session_id: str, tool_name: str, prefix_hash: str) -> str:
        return kimi_cache.lru_key(session_id, tool_name, prefix_hash)

    def save_cache_token(self, session_id: str, tool_name: str, prefix_hash: str, token: str) -> None:
        kimi_cache.save_cache_token(session_id, tool_name, prefix_hash, token)

    def get_cache_token(self, session_id: str, tool_name: str, prefix_hash: str) -> Optional[str]:
        return kimi_cache.get_cache_token(session_id, tool_name, prefix_hash)

    def _purge_cache_tokens(self) -> None:
        kimi_cache.purge_cache_tokens()


    def upload_file(self, file_path: str, purpose: str = "file-extract") -> str:
        """Upload a local file to Moonshot (Kimi) and return file_id.

        Args:
            file_path: Path to a local file
            purpose: Moonshot purpose tag (e.g., 'file-extract', 'assistants')
        Returns:
            The provider-assigned file id string
        """
        return kimi_files.upload_file(self.client, file_path, purpose)

    def _prefix_hash(self, messages: list[dict[str, Any]]) -> str:
        return kimi_chat.prefix_hash(messages)

    def chat_completions_create(self, *, model: str, messages: list[dict[str, Any]], tools: Optional[list[Any]] = None, tool_choice: Optional[Any] = None, temperature: float = 0.6, **kwargs) -> dict:
        """Wrapper that injects idempotency and Kimi context-cache headers, captures cache token, and returns normalized dict.
        """
        return kimi_chat.chat_completions_create(
            self.client,
            model=model,
            messages=messages,
            tools=tools,
            tool_choice=tool_choice,
            temperature=temperature,
            **kwargs
        )


    def generate_content(
        self,
        prompt: str,
        model_name: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = None,
        images: Optional[list[str]] = None,
        **kwargs,
    ) -> ModelResponse:
        # Delegate to OpenAI-compatible base using Moonshot base_url
        # Ensure non-streaming by default for MCP tools
        kwargs.setdefault("stream", False)
        return super().generate_content(
            prompt=prompt,
            model_name=self._resolve_model_name(model_name),
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            images=images,
            **kwargs,
        )
