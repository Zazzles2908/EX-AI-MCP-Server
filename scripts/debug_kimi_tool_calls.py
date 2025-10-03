#!/usr/bin/env python
"""
Debug script to inspect Kimi API responses when web search is used.

This will show us what tool_calls look like in the actual API response.
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

def test_kimi_websearch_raw():
    """Test Kimi web search with raw API inspection"""
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai SDK not installed. Install with: pip install openai")
        return
    
    api_key = os.getenv("KIMI_API_KEY")
    if not api_key:
        print("❌ KIMI_API_KEY not found in environment")
        return
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    print("="*80)
    print("KIMI WEB SEARCH RAW API RESPONSE TEST")
    print("="*80)
    
    # Test query that should trigger web search
    test_query = "What is the current pricing for Moonshot AI's Kimi K2 model in 2025?"
    
    print(f"\nTest Query: {test_query}")
    print(f"Model: kimi-k2-0905-preview")
    print(f"Tools: web_search function")
    print("\n" + "="*80)
    
    try:
        response = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=[
                {"role": "user", "content": test_query}
            ],
            tools=[{
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Internet search",
                    "parameters": {
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                },
            }],
            tool_choice="auto",
        )
        
        # Convert to dict for inspection
        response_dict = response.model_dump()
        
        print("\n📋 FULL API RESPONSE:")
        print(json.dumps(response_dict, indent=2, ensure_ascii=False))
        
        print("\n" + "="*80)
        print("ANALYSIS:")
        print("="*80)
        
        # Check for tool_calls
        choices = response_dict.get("choices", [])
        if choices:
            choice = choices[0]
            message = choice.get("message", {})
            
            print(f"\n✓ Message role: {message.get('role')}")
            print(f"✓ Message content length: {len(message.get('content', '') or '')} chars")
            
            tool_calls = message.get("tool_calls")
            if tool_calls:
                print(f"\n🔧 TOOL_CALLS FOUND: {len(tool_calls)} call(s)")
                for i, tc in enumerate(tool_calls):
                    print(f"\n  Tool Call #{i+1}:")
                    print(f"    ID: {tc.get('id')}")
                    print(f"    Type: {tc.get('type')}")
                    func = tc.get('function', {})
                    print(f"    Function Name: {func.get('name')}")
                    print(f"    Function Arguments:")
                    try:
                        args = json.loads(func.get('arguments', '{}'))
                        print(json.dumps(args, indent=6, ensure_ascii=False))
                    except:
                        print(f"      {func.get('arguments')}")
            else:
                print("\n❌ NO TOOL_CALLS in response")
                print("   This means either:")
                print("   1. Kimi didn't use web search for this query")
                print("   2. Kimi returns web search results differently")
                print("   3. Web search is not actually enabled/working")
            
            # Check content
            content = message.get("content", "") or ""
            if content:
                print(f"\n📝 MESSAGE CONTENT (first 500 chars):")
                print(content[:500])
                if len(content) > 500:
                    print(f"... ({len(content) - 500} more chars)")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_kimi_websearch_raw()

