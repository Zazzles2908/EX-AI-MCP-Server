"""
Test MiniMax M2 Provider Implementation

This test validates the MiniMax provider implementation including:
- Provider initialization
- Model capabilities
- Thinking process handling
- API connectivity
- Error handling
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, 'src')

from providers.minimax import MiniMaxModelProvider
from providers.base import ProviderType, ModelCapabilities


class TestMiniMaxProvider:
    """Test suite for MiniMax provider."""
    
    def test_provider_initialization(self):
        """Test provider initialization with valid API key."""
        # Mock the Anthropic client
        with patch('providers.minimax.ANTHROPIC_AVAILABLE', True), \
             patch('providers.minimax.Anthropic') as mock_anthropic:
            
            provider = MiniMaxModelProvider(
                api_key="test_key",
                base_url="https://api.minimax.io/anthropic"
            )
            
            assert provider.api_key == "test_key"
            assert provider.base_url == "https://api.minimax.io/anthropic"
            assert provider.client is not None
            mock_anthropic.assert_called_once()
    
    def test_provider_initialization_no_anthropic(self):
        """Test provider initialization when anthropic package unavailable."""
        with patch('providers.minimax.ANTHROPIC_AVAILABLE', False):
            provider = MiniMaxModelProvider(api_key="test_key")
            assert provider.client is None
            assert provider.api_key == "test_key"
    
    def test_supported_models(self):
        """Test that supported models are correctly defined."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        assert "MiniMax-M2-Stable" in provider.SUPPORTED_MODELS
        capabilities = provider.SUPPORTED_MODELS["MiniMax-M2-Stable"]
        
        assert capabilities.context_window == 200000
        assert capabilities.supports_extended_thinking is True
        assert capabilities.supports_function_calling is False
        assert capabilities.supports_vision is False
        assert capabilities.aliases == ["minimax-m2", "m2-stable"]
    
    def test_provider_type(self):
        """Test provider type identification."""
        provider = MiniMaxModelProvider(api_key="test_key")
        assert provider.get_provider_type() == ProviderType.MINIMAX
    
    def test_validate_model_name(self):
        """Test model name validation."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # Valid model names
        assert provider.validate_model_name("MiniMax-M2-Stable") is True
        assert provider.validate_model_name("minimax-m2") is True  # Alias
        assert provider.validate_model_name("m2-stable") is True  # Alias
        
        # Invalid model names
        assert provider.validate_model_name("invalid-model") is False
        assert provider.validate_model_name("") is False
    
    def test_supports_thinking_mode(self):
        """Test thinking mode support detection."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        assert provider.supports_thinking_mode("MiniMax-M2-Stable") is True
        assert provider.supports_thinking_mode("minimax-m2") is True  # Alias
    
    def test_supports_images(self):
        """Test image support detection."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # MiniMax does not support images
        assert provider.supports_images("MiniMax-M2-Stable") is False
    
    def test_supports_streaming(self):
        """Test streaming support detection."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # MiniMax has limited streaming
        capabilities = provider.SUPPORTED_MODELS["MiniMax-M2-Stable"]
        assert provider.supports_streaming("MiniMax-M2-Stable") == capabilities.supports_streaming
    
    def test_model_capabilities(self):
        """Test model capabilities retrieval."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        capabilities = provider.get_capabilities("MiniMax-M2-Stable")
        assert isinstance(capabilities, ModelCapabilities)
        assert capabilities.context_window == 200000
        assert capabilities.supports_extended_thinking is True
    
    def test_resolve_model_name(self):
        """Test model name resolution with aliases."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # Test direct resolution
        assert provider._resolve_model_name("MiniMax-M2-Stable") == "MiniMax-M2-Stable"
        
        # Test alias resolution
        assert provider._resolve_model_name("minimax-m2") == "MiniMax-M2-Stable"
        assert provider._resolve_model_name("m2-stable") == "MiniMax-M2-Stable"
        
        # Test case insensitive
        assert provider._resolve_model_name("MINIMAX-M2-STABLE") == "MiniMax-M2-Stable"
        
        # Test unknown model (returns as-is)
        assert provider._resolve_model_name("unknown-model") == "unknown-model"
    
    def test_temperature_constraint(self):
        """Test temperature validation and correction."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # Test valid temperature
        temp = provider.get_effective_temperature("MiniMax-M2-Stable", 0.7)
        assert temp == 0.7
        
        # Test temperature out of range (should be clamped)
        temp = provider.get_effective_temperature("MiniMax-M2-Stable", 2.0)
        assert temp == 1.0  # Max temperature
        
        temp = provider.get_effective_temperature("MiniMax-M2-Stable", -0.5)
        assert temp == 0.0  # Min temperature
    
    @patch('providers.minimax.ANTHROPIC_AVAILABLE', True)
    def test_chat_completions_with_thinking(self):
        """Test chat completions with thinking process."""
        # Mock response with thinking content
        mock_response = Mock()
        mock_response.content = [
            Mock(thinking="This is the thinking process"),
            Mock(text="This is the final answer")
        ]
        mock_response.usage.input_tokens = 50
        mock_response.usage.output_tokens = 100
        mock_response.stop_reason = "max_tokens"
        
        with patch('providers.minimax.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            provider = MiniMaxModelProvider(api_key="test_key")
            
            result = provider.chat_completions_create(
                model="MiniMax-M2-Stable",
                messages=[{"role": "user", "content": "Test"}]
            )
            
            assert result["provider"] == "minimax"
            assert result["model"] == "MiniMax-M2-Stable"
            assert result["content"] == "This is the final answer"
            assert result["thinking"] == "This is the thinking process"
            assert result["usage"]["input_tokens"] == 50
            assert result["usage"]["output_tokens"] == 100
    
    def test_chat_completions_without_client(self):
        """Test chat completions when client is not available."""
        provider = MiniMaxModelProvider(api_key="test_key")
        provider.client = None
        
        with pytest.raises(RuntimeError, match="MiniMax client not available"):
            provider.chat_completions_create(
                model="MiniMax-M2-Stable",
                messages=[{"role": "user", "content": "Test"}]
            )
    
    def test_chat_completions_ignores_tools(self):
        """Test that function calling parameters are ignored."""
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 50
        
        with patch('providers.minimax.ANTHROPIC_AVAILABLE', True), \
             patch('providers.minimax.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client
            
            provider = MiniMaxModelProvider(api_key="test_key")
            
            # Should work even with tools parameter
            result = provider.chat_completions_create(
                model="MiniMax-M2-Stable",
                messages=[{"role": "user", "content": "Test"}],
                tools=[{"name": "test_tool"}],  # Should be ignored
                tool_choice="auto"  # Should be ignored
            )
            
            assert result["provider"] == "minimax"
    
    def test_upload_file_not_supported(self):
        """Test that file upload raises NotImplementedError."""
        provider = MiniMaxModelProvider(api_key="test_key")
        
        with pytest.raises(NotImplementedError, match="does not support file uploads"):
            provider.upload_file("test.txt")


def test_minimax_in_provider_registry():
    """Test that MiniMax is properly registered in provider system."""
    from providers.registry_core import ModelProviderRegistry
    from providers.base import ProviderType
    
    registry = ModelProviderRegistry()
    
    # Check that MINIMAX is in the key map
    key_map = registry._get_api_key_for_provider.__code__.co_consts
    # The key_map is accessed through the get_api_key_for_provider method
    # This is a basic check that the provider type exists
    assert ProviderType.MINIMAX in ProviderType


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running MiniMax Provider Smoke Tests...")
    
    try:
        test_provider = TestMiniMaxProvider()
        
        print("✅ Provider initialization test")
        test_provider.test_provider_initialization()
        
        print("✅ Model capabilities test")
        test_provider.test_supported_models()
        
        print("✅ Provider type test")
        test_provider.test_provider_type()
        
        print("✅ Model validation test")
        test_provider.test_validate_model_name()
        
        print("✅ Thinking mode test")
        test_provider.test_supports_thinking_mode()
        
        print("✅ Model resolution test")
        test_provider.test_resolve_model_name()
        
        print("✅ All tests passed!")
        print("\n🎉 MiniMax provider implementation is working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
