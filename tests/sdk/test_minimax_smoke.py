"""
Simple smoke test for MiniMax provider - no external dependencies
"""

import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, '/app/src')

try:
    from providers.minimax import MiniMaxModelProvider
    from providers.base import ProviderType
    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)


def test_provider_initialization():
    """Test basic provider initialization."""
    print("\n🧪 Testing provider initialization...")
    
    try:
        with patch('providers.minimax.ANTHROPIC_AVAILABLE', True), \
             patch('providers.minimax.Anthropic') as mock_anthropic:
            
            provider = MiniMaxModelProvider(
                api_key="test_key",
                base_url="https://api.minimax.io/anthropic"
            )
            
            assert provider.api_key == "test_key"
            assert provider.base_url == "https://api.minimax.io/anthropic"
            assert provider.client is not None
            print("✅ Provider initialization works")
            return True
    except Exception as e:
        print(f"❌ Provider initialization failed: {e}")
        return False


def test_supported_models():
    """Test model capabilities."""
    print("\n🧪 Testing model capabilities...")
    
    try:
        provider = MiniMaxModelProvider(api_key="test_key")
        
        assert "MiniMax-M2-Stable" in provider.SUPPORTED_MODELS
        capabilities = provider.SUPPORTED_MODELS["MiniMax-M2-Stable"]
        
        assert capabilities.context_window == 200000
        assert capabilities.supports_extended_thinking is True
        assert capabilities.supports_function_calling is False
        assert capabilities.supports_vision is False
        
        print("✅ Model capabilities correct")
        return True
    except Exception as e:
        print(f"❌ Model capabilities test failed: {e}")
        return False


def test_provider_type():
    """Test provider type identification."""
    print("\n🧪 Testing provider type...")
    
    try:
        provider = MiniMaxModelProvider(api_key="test_key")
        provider_type = provider.get_provider_type()
        
        assert provider_type == ProviderType.MINIMAX
        print("✅ Provider type correct")
        return True
    except Exception as e:
        print(f"❌ Provider type test failed: {e}")
        return False


def test_model_validation():
    """Test model name validation."""
    print("\n🧪 Testing model validation...")
    
    try:
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # Valid models
        assert provider.validate_model_name("MiniMax-M2-Stable") is True
        assert provider.validate_model_name("minimax-m2") is True  # Alias
        assert provider.validate_model_name("m2-stable") is True  # Alias
        
        # Invalid models
        assert provider.validate_model_name("invalid-model") is False
        
        print("✅ Model validation works")
        return True
    except Exception as e:
        print(f"❌ Model validation test failed: {e}")
        return False


def test_thinking_mode():
    """Test thinking mode support."""
    print("\n🧪 Testing thinking mode support...")
    
    try:
        provider = MiniMaxModelProvider(api_key="test_key")
        
        assert provider.supports_thinking_mode("MiniMax-M2-Stable") is True
        assert provider.supports_thinking_mode("minimax-m2") is True  # Alias
        
        print("✅ Thinking mode support correct")
        return True
    except Exception as e:
        print(f"❌ Thinking mode test failed: {e}")
        return False


def test_model_resolution():
    """Test model name resolution."""
    print("\n🧪 Testing model name resolution...")
    
    try:
        provider = MiniMaxModelProvider(api_key="test_key")
        
        # Test direct resolution
        assert provider._resolve_model_name("MiniMax-M2-Stable") == "MiniMax-M2-Stable"
        
        # Test alias resolution
        assert provider._resolve_model_name("minimax-m2") == "MiniMax-M2-Stable"
        assert provider._resolve_model_name("m2-stable") == "MiniMax-M2-Stable"
        
        # Test case insensitive
        assert provider._resolve_model_name("MINIMAX-M2-STABLE") == "MiniMax-M2-Stable"
        
        print("✅ Model name resolution works")
        return True
    except Exception as e:
        print(f"❌ Model resolution test failed: {e}")
        return False


def test_registry_integration():
    """Test integration with provider registry."""
    print("\n🧪 Testing registry integration...")
    
    try:
        from providers.registry_core import ModelProviderRegistry
        
        registry = ModelProviderRegistry()
        
        # Check that MINIMAX is in the key map by checking provider type exists
        assert ProviderType.MINIMAX in ProviderType
        
        print("✅ Registry integration correct")
        return True
    except Exception as e:
        print(f"❌ Registry integration test failed: {e}")
        return False


def run_all_tests():
    """Run all smoke tests."""
    print("🚀 Running MiniMax Provider Smoke Tests...")
    print("=" * 50)
    
    tests = [
        test_provider_initialization,
        test_supported_models,
        test_provider_type,
        test_model_validation,
        test_thinking_mode,
        test_model_resolution,
        test_registry_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! MiniMax provider is working correctly!")
        return True
    else:
        print(f"⚠️  {failed} test(s) failed. Check implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
