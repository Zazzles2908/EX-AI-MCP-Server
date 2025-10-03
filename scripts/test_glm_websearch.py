#!/usr/bin/env python
"""
Test GLM web search with different models to find which ones support it.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

try:
    from zhipuai import ZhipuAI
except ImportError:
    print("❌ zhipuai package not installed")
    sys.exit(1)

api_key = os.getenv("GLM_API_KEY", "").strip()
if not api_key:
    print("❌ GLM_API_KEY not set")
    sys.exit(1)

client = ZhipuAI(api_key=api_key)

print("="*80)
print("GLM WEB SEARCH TESTING")
print("="*80)

# Models to test
models_to_test = [
    "glm-4-flash",
    "glm-4-plus",
    "glm-4-air",
    "glm-4-airx",
    "glm-4-0520",
    "glm-4",
]

query = "What is the current pricing for Moonshot AI's Kimi K2 model in 2025?"

print(f"\n📝 Query: {query}")

# GLM web search configuration
tools = [{
    "type": "web_search",
    "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek",
    }
}]

print(f"\n🔧 Tools config:")
print(json.dumps(tools, indent=2))

for model in models_to_test:
    print(f"\n" + "="*80)
    print(f"Testing model: {model}")
    print("="*80)
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        print(f"\n✅ Response received")
        print(f"📊 Finish reason: {response.choices[0].finish_reason}")
        
        # Check for tool_calls
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            print(f"🔧 Tool calls: {len(tool_calls)}")
            for i, tc in enumerate(tool_calls):
                print(f"  Tool {i+1}: {tc}")
        else:
            print(f"🔧 No tool calls")
        
        # Print content
        content = response.choices[0].message.content or ""
        print(f"\n📝 Content length: {len(content)} chars")
        print(f"\n📄 RESPONSE (first 500 chars):")
        print(content[:500])
        
        # Check if content contains search results
        if "$" in content or "price" in content.lower() or "cost" in content.lower():
            print(f"\n✅ Response appears to contain pricing information!")
        else:
            print(f"\n⚠️  Response may not contain specific pricing data")
        
        print(f"\n✅ MODEL {model} SUPPORTS WEB SEARCH!")
        break  # Found a working model
        
    except Exception as e:
        error_msg = str(e)
        if "1211" in error_msg or "模型不存在" in error_msg:
            print(f"\n❌ Model {model} does not exist or doesn't support web_search")
        else:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

print(f"\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)

