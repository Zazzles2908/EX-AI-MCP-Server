#!/usr/bin/env python3
"""
Web Search SDK Test
Tests GLM web search via HTTP endpoint and Kimi web search via SDK
"""
import os
import time
import json
import urllib.request
from openai import OpenAI

print("=" * 80)
print("WEB SEARCH SDK TEST")
print("=" * 80)

# Test 1: GLM Web Search (HTTP endpoint)
print("\n[TEST 1] GLM Web Search via HTTP Endpoint")
print("-" * 80)
try:
    api_key = os.getenv("GLM_API_KEY")
    base_url = "https://api.z.ai/api/paas/v4"
    
    # Prepare request
    payload = {
        "search_query": "Python programming language",
        "count": 3,
        "search_engine": "search-prime",
        "search_recency_filter": "all"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Make request
    start = time.time()
    url = f"{base_url}/web_search"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers=headers
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ Web search successful")
    print(f"⏱️  Search time: {elapsed}ms")
    print(f"📊 Results count: {len(result.get('data', []))}")
    
    if result.get('data'):
        print("\n📋 Search Results:")
        for i, item in enumerate(result['data'][:3], 1):
            print(f"  {i}. {item.get('title', 'N/A')}")
            print(f"     URL: {item.get('url', 'N/A')}")
            print(f"     Snippet: {item.get('content', 'N/A')[:100]}...")
    
    print("\n✅ GLM web search test PASSED")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Kimi Web Search (via SDK with tools)
print("\n[TEST 2] Kimi Web Search via OpenAI SDK (with tools)")
print("-" * 80)
try:
    kimi_client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url="https://api.moonshot.ai/v1"
    )
    
    # Define web search tool
    tools = [{
        "type": "builtin_function",
        "function": {
            "name": "$web_search"
        }
    }]
    
    # Make request with web search enabled
    start = time.time()
    response = kimi_client.chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=[
            {"role": "user", "content": "Search for information about Python programming language"}
        ],
        tools=tools
    )
    elapsed = int((time.time() - start) * 1000)
    
    print(f"✅ Web search chat successful")
    print(f"⏱️  Response time: {elapsed}ms")
    print(f"📊 Model: {response.model}")
    
    # Check if tool was called
    if response.choices[0].message.tool_calls:
        print(f"📊 Tool calls: {len(response.choices[0].message.tool_calls)}")
        for tool_call in response.choices[0].message.tool_calls:
            print(f"   - Function: {tool_call.function.name}")
    
    print(f"\n💬 Response: {response.choices[0].message.content[:200]}...")
    print("\n✅ Kimi web search test PASSED")
    
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("WEB SEARCH TEST COMPLETE")
print("=" * 80)

