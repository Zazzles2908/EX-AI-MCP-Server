#!/usr/bin/env python
"""
Detailed test of GLM web search to see the full response structure.
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
print("GLM WEB SEARCH DETAILED TEST")
print("="*80)

query = "What is the current weather in Tokyo right now?"

print(f"\n📝 Query: {query}")

# GLM web search configuration
tools = [{
    "type": "web_search",
    "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneDay",
        "search_result": True,
    }
}]

print(f"\n🔧 Tools config:")
print(json.dumps(tools, indent=2))

try:
    response = client.chat.completions.create(
        model="glm-4-plus",
        messages=[
            {"role": "user", "content": query}
        ],
        tools=tools,
        tool_choice="auto"
    )
    
    print(f"\n✅ Response received")
    print(f"\n📊 FULL RESPONSE STRUCTURE:")
    print("="*80)
    
    # Print response attributes
    print(f"ID: {response.id}")
    print(f"Created: {response.created}")
    print(f"Model: {response.model}")
    
    # Print choices
    print(f"\nChoices: {len(response.choices)}")
    for i, choice in enumerate(response.choices):
        print(f"\n  Choice {i}:")
        print(f"    Finish reason: {choice.finish_reason}")
        print(f"    Index: {choice.index}")
        
        # Message
        msg = choice.message
        print(f"\n    Message:")
        print(f"      Role: {msg.role}")
        print(f"      Content length: {len(msg.content or '')} chars")
        
        # Tool calls
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            print(f"      Tool calls: {len(msg.tool_calls)}")
            for j, tc in enumerate(msg.tool_calls):
                print(f"\n        Tool call {j}:")
                print(f"          ID: {tc.id if hasattr(tc, 'id') else 'N/A'}")
                print(f"          Type: {tc.type if hasattr(tc, 'type') else 'N/A'}")
                if hasattr(tc, 'function'):
                    print(f"          Function: {tc.function.name}")
                    print(f"          Arguments: {tc.function.arguments}")
        else:
            print(f"      Tool calls: None")
    
    # Usage
    if hasattr(response, 'usage'):
        print(f"\n📊 Usage:")
        print(f"  Prompt tokens: {response.usage.prompt_tokens}")
        print(f"  Completion tokens: {response.usage.completion_tokens}")
        print(f"  Total tokens: {response.usage.total_tokens}")
    
    # Print content
    content = response.choices[0].message.content or ""
    print(f"\n📄 RESPONSE CONTENT:")
    print("="*80)
    print(content)
    print("="*80)
    
    # Check for web search indicators
    if "search" in content.lower() or "weather" in content.lower():
        print(f"\n✅ Content appears to include search-based information")
    else:
        print(f"\n⚠️  Content may not include search results")
    
    # Try to access raw response
    print(f"\n🔍 Checking for additional attributes...")
    for attr in dir(response):
        if not attr.startswith('_'):
            try:
                val = getattr(response, attr)
                if not callable(val):
                    print(f"  {attr}: {type(val).__name__}")
            except:
                pass
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print(f"\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

