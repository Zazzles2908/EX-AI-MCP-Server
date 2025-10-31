#!/usr/bin/env python3
"""
Kimi Chat Completion SDK Test
Tests Kimi chat via OpenAI SDK with metadata verification
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from openai import OpenAI

def test_kimi_chat_basic():
    """Test basic Kimi chat completion via OpenAI SDK"""
    print("=" * 80)
    print("TEST 1: Kimi Chat Completion - Basic Test")
    print("=" * 80)
    
    # Get API key from environment
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ ERROR: KIMI_API_KEY not found in environment")
        return False
    
    try:
        # Initialize OpenAI client with Kimi base URL
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )
        print("✅ OpenAI client initialized (Kimi/Moonshot)")
        
        # Test prompt
        test_prompt = "What is the capital of France? Answer in one sentence."
        print(f"\n📝 Test Prompt: {test_prompt}")
        
        # Start timing
        start_time = time.time()
        
        # Make API call
        response = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                {"role": "user", "content": test_prompt}
            ]
        )
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Extract response
        content = response.choices[0].message.content
        print(f"\n💬 Response: {content}")
        print(f"\n⏱️  Response Time: {response_time_ms}ms")
        
        # Check metadata
        print("\n📊 Metadata Check:")
        print(f"  - Model: {response.model}")
        print(f"  - Usage: {response.usage}")
        
        if hasattr(response, 'usage') and response.usage:
            print(f"    • Input Tokens: {response.usage.prompt_tokens}")
            print(f"    • Output Tokens: {response.usage.completion_tokens}")
            print(f"    • Total Tokens: {response.usage.total_tokens}")
            print("  ✅ Token usage metadata present")
        else:
            print("  ⚠️  Token usage metadata missing")
        
        print("\n✅ TEST PASSED: Kimi chat completion successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_kimi_chat_with_thinking():
    """Test Kimi chat with thinking mode enabled"""
    print("\n" + "=" * 80)
    print("TEST 2: Kimi Chat Completion - Thinking Mode")
    print("=" * 80)
    
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ ERROR: KIMI_API_KEY not found in environment")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )
        print("✅ OpenAI client initialized (Kimi/Moonshot)")
        
        test_prompt = "Solve this problem: If a train travels 120 km in 2 hours, what is its average speed?"
        print(f"\n📝 Test Prompt: {test_prompt}")
        
        start_time = time.time()
        
        # Make API call with thinking mode
        response = client.chat.completions.create(
            model="kimi-thinking-preview",
            messages=[
                {"role": "user", "content": test_prompt}
            ]
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        content = response.choices[0].message.content
        print(f"\n💬 Response: {content}")
        print(f"\n⏱️  Response Time: {response_time_ms}ms")
        
        # Check for thinking content
        if hasattr(response.choices[0].message, 'reasoning_content'):
            print(f"\n🧠 Reasoning Content: {response.choices[0].message.reasoning_content[:200]}...")
            print("  ✅ Thinking mode working")
        else:
            print("  ℹ️  No reasoning content attribute (may be in content)")
        
        print(f"\n📊 Usage: {response.usage}")
        print("\n✅ TEST PASSED: Kimi thinking mode successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_kimi_chat_streaming():
    """Test Kimi chat with streaming enabled"""
    print("\n" + "=" * 80)
    print("TEST 3: Kimi Chat Completion - Streaming Mode")
    print("=" * 80)
    
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ ERROR: KIMI_API_KEY not found in environment")
        return False
    
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.ai/v1"
        )
        print("✅ OpenAI client initialized (Kimi/Moonshot)")
        
        test_prompt = "Count from 1 to 5."
        print(f"\n📝 Test Prompt: {test_prompt}")
        
        start_time = time.time()
        
        # Make streaming API call
        stream = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                {"role": "user", "content": test_prompt}
            ],
            stream=True
        )
        
        print("\n💬 Streaming Response:")
        full_content = ""
        chunk_count = 0
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_content += content
                print(content, end="", flush=True)
                chunk_count += 1
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        print(f"\n\n⏱️  Response Time: {response_time_ms}ms")
        print(f"📦 Chunks Received: {chunk_count}")
        print(f"📝 Full Content Length: {len(full_content)} characters")
        
        print("\n✅ TEST PASSED: Kimi streaming successful")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Kimi Chat SDK Functional Tests")
    print(f"📅 Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python Version: {sys.version}")
    
    results = []
    
    # Run all tests
    results.append(("Basic Chat", test_kimi_chat_basic()))
    results.append(("Thinking Mode", test_kimi_chat_with_thinking()))
    results.append(("Streaming Mode", test_kimi_chat_streaming()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        sys.exit(1)

