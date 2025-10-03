#!/usr/bin/env python
"""
Test the complete Kimi builtin_function flow for web search.
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
    from openai import OpenAI
except ImportError:
    print("❌ openai package not installed")
    sys.exit(1)

api_key = os.getenv("KIMI_API_KEY", "").strip()
if not api_key:
    print("❌ KIMI_API_KEY not set")
    sys.exit(1)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.ai/v1"
)

print("="*80)
print("KIMI BUILTIN $web_search COMPLETE FLOW TEST")
print("="*80)

query = "What is the current pricing for Moonshot AI's Kimi K2 model in 2025?"

print(f"\n📝 Query: {query}")

# Step 1: Initial request with builtin_function tool
print(f"\n🔧 STEP 1: Send request with $web_search builtin_function")

tools = [{
    "type": "builtin_function",
    "function": {"name": "$web_search"}
}]

messages = [
    {"role": "user", "content": query}
]

print(f"   Tools: {json.dumps(tools, indent=6)}")

response1 = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

print(f"\n✅ Response 1 received")
print(f"   Finish reason: {response1.choices[0].finish_reason}")
print(f"   Content: '{response1.choices[0].message.content or ''}'")

tool_calls = response1.choices[0].message.tool_calls
if tool_calls:
    print(f"\n🔧 TOOL CALLS: {len(tool_calls)}")
    for i, tc in enumerate(tool_calls):
        print(f"\n   Tool Call {i+1}:")
        print(f"     ID: {tc.id}")
        print(f"     Type: {tc.type}")
        if hasattr(tc, 'function'):
            print(f"     Function: {tc.function.name}")
            if hasattr(tc.function, 'arguments'):
                print(f"     Arguments: {tc.function.arguments}")
    
    # Step 2: Send acknowledgment with tool results
    print(f"\n🔧 STEP 2: Send acknowledgment (Kimi executed search server-side)")
    
    # Add assistant message with tool_calls
    messages.append({
        "role": "assistant",
        "content": response1.choices[0].message.content or "",
        "tool_calls": [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name if hasattr(tc, 'function') else "$web_search",
                    "arguments": tc.function.arguments if hasattr(tc, 'function') and hasattr(tc.function, 'arguments') else "{}"
                }
            }
            for tc in tool_calls
        ]
    })
    
    # Add tool response (empty since Kimi did the search)
    for tc in tool_calls:
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps({"status": "executed_server_side"})
        })
    
    print(f"   Sending {len(messages)} messages back to Kimi")
    
    response2 = client.chat.completions.create(
        model="kimi-k2-0905-preview",
        messages=messages
    )
    
    print(f"\n✅ Response 2 received")
    print(f"   Finish reason: {response2.choices[0].finish_reason}")
    
    content = response2.choices[0].message.content or ""
    print(f"\n📄 FINAL RESPONSE ({len(content)} chars):")
    print("="*80)
    print(content)
    print("="*80)
    
    # Check if response contains actual pricing data
    if "$" in content or "price" in content.lower() or "cost" in content.lower():
        print(f"\n✅ Response appears to contain pricing information!")
    else:
        print(f"\n⚠️  Response may not contain specific pricing data")
        
else:
    print(f"\n⚠️  No tool calls - Kimi returned direct response")
    content = response1.choices[0].message.content or ""
    print(f"\n📄 RESPONSE ({len(content)} chars):")
    print(content)

print(f"\n" + "="*80)
print("TEST COMPLETE")
print("="*80)

