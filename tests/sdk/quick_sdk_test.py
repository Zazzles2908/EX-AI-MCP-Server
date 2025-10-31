#!/usr/bin/env python3
"""Quick SDK functionality test for GLM and Kimi"""
import os
import time
from zhipuai import ZhipuAI
from openai import OpenAI

print("=" * 80)
print("SDK FUNCTIONALITY TEST")
print("=" * 80)

# Test 1: GLM SDK
print("\n[TEST 1] GLM Chat via ZhipuAI SDK")
print("-" * 80)
try:
    glm_client = ZhipuAI(api_key=os.getenv("GLM_API_KEY"))
    start = time.time()
    glm_response = glm_client.chat.completions.create(
        model="glm-4.5-flash",
        messages=[{"role": "user", "content": "What is 2+2? Answer in one sentence."}]
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ Response: {glm_response.choices[0].message.content}")
    print(f"⏱️  Time: {elapsed}ms")
    print(f"📊 Model: {glm_response.model}")
    print(f"📊 Usage: {glm_response.usage}")
    print(f"   - Input: {glm_response.usage.prompt_tokens}")
    print(f"   - Output: {glm_response.usage.completion_tokens}")
    print(f"   - Total: {glm_response.usage.total_tokens}")
except Exception as e:
    print(f"❌ FAILED: {e}")

# Test 2: Kimi SDK
print("\n[TEST 2] Kimi Chat via OpenAI SDK")
print("-" * 80)
try:
    kimi_client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.ai/v1"
    )
    start = time.time()
    kimi_response = kimi_client.chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=[{"role": "user", "content": "What is 2+2? Answer in one sentence."}]
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ Response: {kimi_response.choices[0].message.content}")
    print(f"⏱️  Time: {elapsed}ms")
    print(f"📊 Model: {kimi_response.model}")
    print(f"📊 Usage: {kimi_response.usage}")
    print(f"   - Input: {kimi_response.usage.prompt_tokens}")
    print(f"   - Output: {kimi_response.usage.completion_tokens}")
    print(f"   - Total: {kimi_response.usage.total_tokens}")
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)

