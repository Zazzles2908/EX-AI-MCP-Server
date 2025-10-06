"""GLM (ZhipuAI) provider implementation."""

import logging
import os
from typing import Any, Optional

from .base import ModelProvider, ModelCapabilities, ModelResponse, ProviderType
from utils.http_client import HttpClient

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
        super().__init__(api_key, **kwargs)
        self.base_url = base_url or self.DEFAULT_BASE_URL
        # Initialize HTTP client first (always needed as fallback)
        self.client = HttpClient(self.base_url, api_key=self.api_key, api_key_header="Authorization", api_key_prefix="Bearer ")
        # Prefer official SDK; fallback to HTTP if not available
        try:
            from zhipuai import ZhipuAI  # type: ignore
            self._use_sdk = True
            # CRITICAL FIX: Pass base_url to SDK to use z.ai proxy instead of bigmodel.cn
            self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
            logger.info(f"GLM provider using SDK with base_url={self.base_url}")
        except Exception as e:
            logger.warning("zhipuai SDK unavailable or failed to init; falling back to HTTP client: %s", e)
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

    def _build_payload(self, prompt: str, system_prompt: Optional[str], model_name: str, temperature: float, max_output_tokens: Optional[int], **kwargs) -> dict:
        resolved = self._resolve_model_name(model_name)
        effective_temp = self.get_effective_temperature(resolved, temperature)
        return glm_chat.build_payload(prompt, system_prompt, resolved, effective_temp, max_output_tokens, **kwargs)

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
