#!/usr/bin/env python3
"""Quick test script to check provider registry functionality."""

def test_registry():
    try:
        from src.providers import ModelProviderRegistry
        from src.providers.kimi import KimiProvider
        from src.providers.glm import GLMModelProvider
        print('SUCCESS: Provider registry imports successful')
        
        registry = ModelProviderRegistry()
        print('SUCCESS: ModelProviderRegistry instantiated successfully')
        
        # Test provider registration
        from src.providers.base import ProviderType
        print(f'SUCCESS: Provider types available: {[t.value for t in ProviderType]}')
        
        return True
    except Exception as e:
        print('ERROR: Import error:', str(e))
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_registry()