"""Unit tests for KimiModelProvider."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestKimiProviderInitialization:
    """Test KimiModelProvider initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test provider initializes with API key."""
        from src.providers.kimi import KimiModelProvider

        provider = KimiModelProvider(api_key="test-key-123")
        assert provider is not None
        assert provider.get_provider_type().value == "kimi"

    def test_initialization_with_custom_base_url(self):
        """Test provider initializes with custom base URL."""
        from src.providers.kimi import KimiModelProvider
        
        custom_url = "https://custom.moonshot.example.com/v1"
        provider = KimiModelProvider(api_key="test-key", base_url=custom_url)
        assert provider is not None

    def test_default_base_url_from_env(self, monkeypatch):
        """Test provider uses KIMI_API_URL from environment."""
        from src.providers.kimi import KimiModelProvider
        
        test_url = "https://test.moonshot.ai/v1"
        monkeypatch.setenv("KIMI_API_URL", test_url)
        
        # Reload module to pick up env variable
        import importlib
        import src.providers.kimi as kimi_module
        importlib.reload(kimi_module)
        
        assert kimi_module.KimiModelProvider.DEFAULT_BASE_URL == test_url

    def test_default_base_url_fallback(self):
        """Test provider falls back to default moonshot.ai URL."""
        from src.providers.kimi import KimiModelProvider
        
        # Should use default if no env variable
        assert "moonshot.ai" in KimiModelProvider.DEFAULT_BASE_URL


class TestKimiModelResolution:
    """Test Kimi model resolution and capabilities."""

    def test_supported_models_exist(self):
        """Test that SUPPORTED_MODELS dictionary is populated."""
        from src.providers.kimi import KimiModelProvider
        
        assert len(KimiModelProvider.SUPPORTED_MODELS) > 0
        assert "kimi-k2-0905-preview" in KimiModelProvider.SUPPORTED_MODELS
        assert "kimi-k2-0711-preview" in KimiModelProvider.SUPPORTED_MODELS

    def test_model_capabilities_structure(self):
        """Test model capabilities have required fields."""
        from src.providers.kimi import KimiModelProvider
        
        k2_caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-0905-preview"]
        assert k2_caps.context_window == 262144  # 256K
        assert k2_caps.supports_images is True
        assert k2_caps.supports_function_calling is True
        assert k2_caps.supports_streaming is True

    def test_kimi_latest_models_exist(self):
        """Test kimi-latest-* models exist."""
        from src.providers.kimi import KimiModelProvider
        
        assert "kimi-latest-8k" in KimiModelProvider.SUPPORTED_MODELS
        assert "kimi-latest-32k" in KimiModelProvider.SUPPORTED_MODELS
        assert "kimi-latest-128k" in KimiModelProvider.SUPPORTED_MODELS

    def test_kimi_thinking_preview_exists(self):
        """Test kimi-thinking-preview model exists."""
        from src.providers.kimi import KimiModelProvider
        
        assert "kimi-thinking-preview" in KimiModelProvider.SUPPORTED_MODELS
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-thinking-preview"]
        assert caps.supports_extended_thinking is True


class TestKimiContextWindows:
    """Test Kimi model context window configurations."""

    def test_kimi_k2_0905_context_window(self):
        """Test kimi-k2-0905-preview has 256K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-0905-preview"]
        assert caps.context_window == 262144  # 256K = 262144 tokens

    def test_kimi_k2_0711_context_window(self):
        """Test kimi-k2-0711-preview has 128K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-0711-preview"]
        assert caps.context_window == 131072  # 128K = 131072 tokens

    def test_kimi_k2_turbo_context_window(self):
        """Test kimi-k2-turbo-preview has 256K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-turbo-preview"]
        assert caps.context_window == 262144  # 256K = 262144 tokens

    def test_kimi_thinking_context_window(self):
        """Test kimi-thinking-preview has 128K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-thinking-preview"]
        assert caps.context_window == 131072  # 128K = 131072 tokens

    def test_kimi_latest_8k_context_window(self):
        """Test kimi-latest-8k has 8K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-latest-8k"]
        assert caps.context_window == 8192

    def test_kimi_latest_32k_context_window(self):
        """Test kimi-latest-32k has 32K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-latest-32k"]
        assert caps.context_window == 32768

    def test_kimi_latest_128k_context_window(self):
        """Test kimi-latest-128k has 128K context window."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-latest-128k"]
        assert caps.context_window == 131072  # 128K = 131072 tokens


class TestKimiContextCaching:
    """Test Kimi context caching functionality."""

    def test_prefix_hash_generation(self):
        """Test prefix hash generation for cache keys."""
        from src.providers.kimi import KimiModelProvider
        
        provider = KimiModelProvider(api_key="test-key")
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        hash1 = provider._prefix_hash(messages)
        assert isinstance(hash1, str)
        assert len(hash1) >= 32  # Should be a hash string

    def test_prefix_hash_consistency(self):
        """Test prefix hash is consistent for same messages."""
        from src.providers.kimi import KimiModelProvider
        
        provider = KimiModelProvider(api_key="test-key")
        messages = [{"role": "user", "content": "Test"}]
        
        hash1 = provider._prefix_hash(messages)
        hash2 = provider._prefix_hash(messages)
        assert hash1 == hash2

    def test_cache_token_storage_and_retrieval(self):
        """Test cache token can be stored and retrieved."""
        from src.providers.kimi import KimiModelProvider
        
        provider = KimiModelProvider(api_key="test-key")
        session_id = "test-session"
        tool_name = "test-tool"
        prefix_hash = "test-hash-123"
        cache_token = "cache-token-456"
        
        # Initially should be None
        assert provider.get_cache_token(session_id, tool_name, prefix_hash) is None
        
        # Save token
        provider.save_cache_token(session_id, tool_name, prefix_hash, cache_token)
        
        # Should retrieve same token
        retrieved = provider.get_cache_token(session_id, tool_name, prefix_hash)
        assert retrieved == cache_token

    def test_cache_token_isolation_by_session(self):
        """Test cache tokens are isolated by session ID."""
        from src.providers.kimi import KimiModelProvider
        
        provider = KimiModelProvider(api_key="test-key")
        tool_name = "test-tool"
        prefix_hash = "test-hash"
        
        provider.save_cache_token("session-1", tool_name, prefix_hash, "token-1")
        provider.save_cache_token("session-2", tool_name, prefix_hash, "token-2")
        
        assert provider.get_cache_token("session-1", tool_name, prefix_hash) == "token-1"
        assert provider.get_cache_token("session-2", tool_name, prefix_hash) == "token-2"


class TestKimiProviderType:
    """Test Kimi provider type identification."""

    def test_get_provider_type(self):
        """Test provider returns correct type."""
        from src.providers.kimi import KimiModelProvider
        from src.providers.base import ProviderType
        
        provider = KimiModelProvider(api_key="test-key")
        assert provider.get_provider_type() == ProviderType.KIMI

    def test_provider_type_value(self):
        """Test provider type has correct string value."""
        from src.providers.kimi import KimiModelProvider

        provider = KimiModelProvider(api_key="test-key")
        assert provider.get_provider_type().value == "kimi"


class TestKimiOpenAICompatibility:
    """Test Kimi provider OpenAI compatibility."""

    def test_inherits_from_openai_compatible(self):
        """Test KimiModelProvider inherits from OpenAICompatibleProvider."""
        from src.providers.kimi import KimiModelProvider
        from src.providers.openai_compatible import OpenAICompatibleProvider
        
        provider = KimiModelProvider(api_key="test-key")
        assert isinstance(provider, OpenAICompatibleProvider)

    def test_has_retry_mixin(self):
        """Test provider has retry functionality from RetryMixin."""
        from src.providers.kimi import KimiModelProvider
        
        provider = KimiModelProvider(api_key="test-key")
        # Should have retry methods from mixin
        assert hasattr(provider, '_execute_with_retry')


class TestKimiModelAliases:
    """Test Kimi model aliases."""

    def test_kimi_k2_aliases(self):
        """Test kimi-k2-0905-preview has correct aliases."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-0905-preview"]
        assert "kimi-k2-0905" in caps.aliases
        assert "kimi-k2" in caps.aliases


class TestKimiImageSupport:
    """Test Kimi image/vision support."""

    def test_models_support_images(self):
        """Test Kimi models support image inputs."""
        from src.providers.kimi import KimiModelProvider
        
        # All major Kimi models should support images
        for model_name in ["kimi-k2-0905-preview", "kimi-k2-0711-preview", "kimi-latest-128k"]:
            caps = KimiModelProvider.SUPPORTED_MODELS[model_name]
            assert caps.supports_images is True

    def test_max_image_size(self):
        """Test Kimi models have max image size configured."""
        from src.providers.kimi import KimiModelProvider
        
        caps = KimiModelProvider.SUPPORTED_MODELS["kimi-k2-0905-preview"]
        assert caps.max_image_size_mb == 20.0


class TestKimiFunctionCalling:
    """Test Kimi function calling support."""

    def test_models_support_function_calling(self):
        """Test Kimi models support function calling."""
        from src.providers.kimi import KimiModelProvider
        
        # All major Kimi models should support function calling
        for model_name in ["kimi-k2-0905-preview", "kimi-k2-turbo-preview"]:
            caps = KimiModelProvider.SUPPORTED_MODELS[model_name]
            assert caps.supports_function_calling is True

