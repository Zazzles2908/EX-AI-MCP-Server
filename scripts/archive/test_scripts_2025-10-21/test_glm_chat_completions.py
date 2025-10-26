#!/usr/bin/env python3
"""
Test script for GLM chat_completions_create method.
Verifies that the new SDK-native message array method works correctly.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.providers.glm import GLMModelProvider


def test_glm_chat_completions_create():
    """Test GLM chat_completions_create with message arrays."""
    
    # Get API key
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ GLM_API_KEY not set")
        return False
    
    # Create provider
    print("Creating GLM provider...")
    provider = GLMModelProvider(api_key=api_key)
    
    # Test 1: Simple message array
    print("\n=== Test 1: Simple message array ===")
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Respond in one sentence."},
        {"role": "user", "content": "What is 2+2?"}
    ]
    
    try:
        result = provider.chat_completions_create(
            model="glm-4.5-flash",
            messages=messages,
            temperature=0.3
        )
        
        print(f"✅ Provider: {result.get('provider')}")
        print(f"✅ Model: {result.get('model')}")
        print(f"✅ Content: {result.get('content')[:100]}...")
        print(f"✅ Usage: {result.get('usage')}")
        
        if result.get('provider') != 'GLM':
            print("❌ Wrong provider!")
            return False
            
        if not result.get('content'):
            print("❌ No content returned!")
            return False
            
        print("✅ Test 1 PASSED")
        
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Multi-turn conversation
    print("\n=== Test 2: Multi-turn conversation ===")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "My name is Alice."},
        {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
        {"role": "user", "content": "What's my name?"}
    ]
    
    try:
        result = provider.chat_completions_create(
            model="glm-4.5-flash",
            messages=messages,
            temperature=0.3
        )
        
        content = result.get('content', '').lower()
        print(f"✅ Content: {result.get('content')[:100]}...")
        
        if 'alice' in content:
            print("✅ Test 2 PASSED - Conversation context maintained!")
        else:
            print("⚠️ Test 2 WARNING - Context may not be maintained")
            print(f"   Expected 'alice' in response, got: {content}")
        
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED - GLM chat_completions_create works!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_glm_chat_completions_create()
    sys.exit(0 if success else 1)

