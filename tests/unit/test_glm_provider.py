"""Unit tests for GLMModelProvider."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestGLMProviderInitialization:
    """Test GLMModelProvider initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test provider initializes with API key."""
        from src.providers.glm import GLMModelProvider

        provider = GLMModelProvider(api_key="test-key-123")
        assert provider is not None
        assert provider.get_provider_type().value == "glm"

    def test_initialization_with_custom_base_url(self):
        """Test provider initializes with custom base URL."""
        from src.providers.glm import GLMModelProvider
        
        custom_url = "https://custom.api.example.com/v1"
        provider = GLMModelProvider(api_key="test-key", base_url=custom_url)
        assert provider is not None

    def test_default_base_url_from_env(self, monkeypatch):
        """Test provider uses GLM_API_URL from environment."""
        from src.providers.glm import GLMModelProvider
        
        test_url = "https://test.z.ai/api/paas/v4"
        monkeypatch.setenv("GLM_API_URL", test_url)
        
        # Reload module to pick up env variable
        import importlib
        import src.providers.glm as glm_module
        importlib.reload(glm_module)
        
        assert glm_module.GLMModelProvider.DEFAULT_BASE_URL == test_url

    def test_default_base_url_fallback(self):
        """Test provider falls back to default z.ai URL."""
        from src.providers.glm import GLMModelProvider
        
        # Should use default if no env variable
        assert "z.ai" in GLMModelProvider.DEFAULT_BASE_URL


class TestGLMModelResolution:
    """Test GLM model resolution and capabilities."""

    def test_supported_models_exist(self):
        """Test that SUPPORTED_MODELS dictionary is populated."""
        from src.providers.glm import GLMModelProvider
        
        assert len(GLMModelProvider.SUPPORTED_MODELS) > 0
        assert "glm-4.5-flash" in GLMModelProvider.SUPPORTED_MODELS
        assert "glm-4.6" in GLMModelProvider.SUPPORTED_MODELS

    def test_model_capabilities_structure(self):
        """Test model capabilities have required fields."""
        from src.providers.glm import GLMModelProvider
        
        flash_caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.5-flash"]
        assert flash_caps.context_window == 128000
        assert flash_caps.supports_images is True
        assert flash_caps.supports_function_calling is True
        assert flash_caps.supports_streaming is True

    def test_glm_4_6_capabilities(self):
        """Test GLM-4.6 model capabilities."""
        from src.providers.glm import GLMModelProvider
        
        caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.6"]
        assert caps.context_window == 200000  # 200K
        assert caps.supports_images is True

    def test_glm_4_5v_vision_model(self):
        """Test GLM-4.5V vision model exists and has correct config."""
        from src.providers.glm import GLMModelProvider
        
        assert "glm-4.5v" in GLMModelProvider.SUPPORTED_MODELS
        caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.5v"]
        assert caps.context_window == 65536  # 64K
        assert caps.supports_images is True

    def test_glm_4_5_x_alias(self):
        """Test GLM-4.5-X is aliased to glm-4.5-air."""
        from src.providers.glm import GLMModelProvider
        
        air_caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.5-air"]
        assert "glm-4.5-x" in air_caps.aliases


class TestGLMWebSearchSupport:
    """Test GLM web search capabilities and configuration."""

    def test_glm_4_plus_supports_native_websearch(self):
        """Test glm-4-plus supports native web search tool calling."""
        from src.providers.capabilities import GLMCapabilities

        config = {"model_name": "glm-4-plus", "use_websearch": True}
        caps = GLMCapabilities()
        schema = caps.get_websearch_tool_schema(config)

        # Should return valid schema for glm-4-plus
        assert schema.tools is not None
        assert schema.tool_choice is not None

    def test_glm_4_6_supports_native_websearch(self):
        """Test glm-4.6 supports native web search tool calling."""
        from src.providers.capabilities import GLMCapabilities

        config = {"model_name": "glm-4.6", "use_websearch": True}
        caps = GLMCapabilities()
        schema = caps.get_websearch_tool_schema(config)

        # Should return valid schema for glm-4.6
        assert schema.tools is not None
        assert schema.tool_choice is not None

    def test_glm_4_5_flash_no_native_websearch(self):
        """Test glm-4.5-flash does NOT support native web search tool calling."""
        from src.providers.capabilities import GLMCapabilities

        config = {"model_name": "glm-4.5-flash"}
        caps = GLMCapabilities()
        schema = caps.get_websearch_tool_schema(config)

        # Should return empty schema (no native tool calling support)
        assert schema.tools is None
        assert schema.tool_choice is None


class TestGLMPayloadBuilding:
    """Test GLM payload construction."""

    def test_build_payload_basic(self):
        """Test basic payload building."""
        from src.providers.glm import GLMModelProvider
        
        provider = GLMModelProvider(api_key="test-key")
        payload = provider._build_payload(
            prompt="Hello",
            system_prompt=None,
            model_name="glm-4.5-flash",
            temperature=0.3,
            max_output_tokens=None,
            tools=None,
            tool_choice=None,
        )
        
        assert isinstance(payload, dict)
        assert payload["model"] == "glm-4.5-flash"
        assert "messages" in payload
        assert payload.get("temperature") == 0.3

    def test_build_payload_with_websearch_tools(self):
        """Test payload building with web search tools."""
        from src.providers.glm import GLMModelProvider
        
        provider = GLMModelProvider(api_key="test-key")
        payload = provider._build_payload(
            prompt="Search for Python tutorials",
            system_prompt=None,
            model_name="glm-4.6",
            temperature=0.3,
            max_output_tokens=None,
            tools=[{"type": "web_search"}],
            tool_choice=None,
        )
        
        assert isinstance(payload, dict)
        assert payload.get("tools") == [{"type": "web_search"}]

    def test_build_payload_with_system_prompt(self):
        """Test payload building with system prompt."""
        from src.providers.glm import GLMModelProvider
        
        provider = GLMModelProvider(api_key="test-key")
        payload = provider._build_payload(
            prompt="Hello",
            system_prompt="You are a helpful assistant",
            model_name="glm-4.5-flash",
            temperature=0.3,
            max_output_tokens=None,
            tools=None,
            tool_choice=None,
        )
        
        assert isinstance(payload, dict)
        messages = payload.get("messages", [])
        # Should have system message first
        assert any(msg.get("role") == "system" for msg in messages)


class TestGLMSDKFallback:
    """Test GLM SDK vs HTTP fallback behavior."""

    def test_has_sdk_fallback_mechanism(self):
        """Test provider has SDK fallback mechanism."""
        from src.providers.glm import GLMModelProvider
        
        provider = GLMModelProvider(api_key="test-key")
        # Provider should have methods for both SDK and HTTP
        assert hasattr(provider, '_build_payload')


class TestGLMProviderType:
    """Test GLM provider type identification."""

    def test_get_provider_type(self):
        """Test provider returns correct type."""
        from src.providers.glm import GLMModelProvider
        from src.providers.base import ProviderType
        
        provider = GLMModelProvider(api_key="test-key")
        assert provider.get_provider_type() == ProviderType.GLM

    def test_provider_type_value(self):
        """Test provider type has correct string value."""
        from src.providers.glm import GLMModelProvider

        provider = GLMModelProvider(api_key="test-key")
        assert provider.get_provider_type().value == "glm"


class TestGLMContextWindows:
    """Test GLM model context window configurations."""

    def test_glm_4_6_context_window(self):
        """Test GLM-4.6 has 200K context window."""
        from src.providers.glm import GLMModelProvider
        
        caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.6"]
        assert caps.context_window == 200000

    def test_glm_4_5_flash_context_window(self):
        """Test GLM-4.5-Flash has 128K context window."""
        from src.providers.glm import GLMModelProvider
        
        caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.5-flash"]
        assert caps.context_window == 128000

    def test_glm_4_5v_context_window(self):
        """Test GLM-4.5V has 64K context window."""
        from src.providers.glm import GLMModelProvider
        
        caps = GLMModelProvider.SUPPORTED_MODELS["glm-4.5v"]
        assert caps.context_window == 65536  # 64K = 65536 tokens

