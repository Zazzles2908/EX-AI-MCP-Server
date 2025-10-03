#!/usr/bin/env python
"""
Debug script to inspect actual GLM API responses when web search is enabled.

This will help us understand:
1. Does GLM actually return tool_calls in the response?
2. What format does the web search result take?
3. Is the issue in our response parsing?
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

def test_glm_websearch_raw():
    """Test GLM web search with raw API inspection"""
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("❌ zhipuai SDK not installed. Install with: pip install zhipuai")
        return
    
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("❌ GLM_API_KEY not found in environment")
        return
    
    client = ZhipuAI(api_key=api_key)
    
    print("="*80)
    print("GLM WEB SEARCH RAW API RESPONSE TEST")
    print("="*80)
    
    # Test query that should trigger web search
    test_query = "What is the current weather in Tokyo, Japan?"
    
    print(f"\nTest Query: {test_query}")
    print(f"Model: glm-4.5")
    print(f"Tools: [{{'type': 'web_search', 'web_search': {{}}}}]")
    print(f"Tool Choice: auto")
    print("\n" + "="*80)
    
    try:
        response = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": test_query}
            ],
            tools=[{"type": "web_search", "web_search": {}}],
            tool_choice="auto",
            stream=False
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
            print(f"✓ Message content length: {len(message.get('content', ''))} chars")
            
            tool_calls = message.get("tool_calls")
            if tool_calls:
                print(f"\n🔧 TOOL_CALLS FOUND: {len(tool_calls)} call(s)")
                for i, tc in enumerate(tool_calls):
                    print(f"\n  Tool Call #{i+1}:")
                    print(f"    Type: {tc.get('type')}")
                    print(f"    ID: {tc.get('id')}")
                    if 'web_search' in tc:
                        print(f"    Web Search Data:")
                        print(json.dumps(tc['web_search'], indent=6, ensure_ascii=False))
            else:
                print("\n❌ NO TOOL_CALLS in response")
                print("   This means either:")
                print("   1. GLM didn't use web search for this query")
                print("   2. GLM returns web search results differently")
                print("   3. Web search is not actually enabled/working")
            
            # Check content
            content = message.get("content", "")
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
    test_glm_websearch_raw()

