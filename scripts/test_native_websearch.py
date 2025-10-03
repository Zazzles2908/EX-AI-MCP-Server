#!/usr/bin/env python
"""
Test native web search for both GLM and Kimi providers.
This tests the ACTUAL provider APIs to understand how web search works.
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


def test_glm_native_websearch():
    """Test GLM's native web_search tool"""
    print("\n" + "="*80)
    print("TEST 1: GLM NATIVE WEB SEARCH")
    print("="*80)
    
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        print("❌ zhipuai package not installed")
        return
    
    api_key = os.getenv("GLM_API_KEY", "").strip()
    if not api_key:
        print("❌ GLM_API_KEY not set")
        return
    
    client = ZhipuAI(api_key=api_key)
    
    # Test query
    query = "What is the current weather in Tokyo?"
    
    print(f"\n📝 Query: {query}")
    print(f"🔧 Using web_search tool with GLM API")
    
    try:
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
        
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "user", "content": query}
            ],
            tools=tools,
            tool_choice="auto"
        )
        
        print(f"\n✅ Response received")
        print(f"📊 Finish reason: {response.choices[0].finish_reason}")
        print(f"📝 Content length: {len(response.choices[0].message.content or '')} chars")
        
        # Check for tool_calls
        tool_calls = response.choices[0].message.tool_calls
        print(f"🔧 Tool calls: {tool_calls}")
        
        # Print content
        content = response.choices[0].message.content or ""
        print(f"\n📄 RESPONSE CONTENT (first 500 chars):")
        print(content[:500])
        
        # Check if content contains search results
        if "search" in content.lower() or "weather" in content.lower():
            print(f"\n✅ Content appears to include search-based information")
        else:
            print(f"\n⚠️  Content may not include search results")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_kimi_native_websearch():
    """Test Kimi's web_search function tool"""
    print("\n" + "="*80)
    print("TEST 2: KIMI NATIVE WEB SEARCH")
    print("="*80)
    
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed")
        return
    
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    if not api_key:
        print("❌ KIMI_API_KEY not set")
        return
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    # Test query
    query = "What is the current weather in Tokyo?"
    
    print(f"\n📝 Query: {query}")
    print(f"🔧 Using web_search function tool with Kimi API")
    
    try:
        # Kimi web search configuration
        tools = [{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            }
        }]
        
        print(f"\n🔧 Tools config:")
        print(json.dumps(tools, indent=2))
        
        response = client.chat.completions.create(
            model="kimi-k2-0905-preview",
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
            print(f"\n🔧 TOOL CALLS DETECTED: {len(tool_calls)}")
            for i, tc in enumerate(tool_calls):
                print(f"\n  Tool Call {i+1}:")
                print(f"    ID: {tc.id}")
                print(f"    Function: {tc.function.name}")
                print(f"    Arguments: {tc.function.arguments}")
            
            print(f"\n⚠️  Kimi is asking US to execute the search!")
            print(f"   This is CLIENT-SIDE search pattern")
        else:
            print(f"\n🔧 No tool calls - checking content")
            content = response.choices[0].message.content or ""
            print(f"📝 Content length: {len(content)} chars")
            print(f"\n📄 RESPONSE CONTENT (first 500 chars):")
            print(content[:500])
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_kimi_builtin_websearch():
    """Test Kimi's $web_search builtin function"""
    print("\n" + "="*80)
    print("TEST 3: KIMI BUILTIN $web_search")
    print("="*80)
    
    try:
        from openai import OpenAI
    except ImportError:
        print("❌ openai package not installed")
        return
    
    api_key = os.getenv("KIMI_API_KEY", "").strip()
    if not api_key:
        print("❌ KIMI_API_KEY not set")
        return
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    # Test query
    query = "What is the current weather in Tokyo?"
    
    print(f"\n📝 Query: {query}")
    print(f"🔧 Using $web_search builtin function with Kimi API")
    
    try:
        # Kimi builtin web search
        tools = [{
            "type": "builtin_function",
            "function": {"name": "$web_search"}
        }]
        
        print(f"\n🔧 Tools config:")
        print(json.dumps(tools, indent=2))
        
        response = client.chat.completions.create(
            model="kimi-k2-0905-preview",
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
            print(f"\n🔧 TOOL CALLS: {len(tool_calls)}")
            for i, tc in enumerate(tool_calls):
                print(f"\n  Tool Call {i+1}:")
                print(f"    ID: {tc.id}")
                print(f"    Type: {tc.type}")
                if hasattr(tc, 'function'):
                    print(f"    Function: {tc.function.name}")
        
        content = response.choices[0].message.content or ""
        print(f"\n📝 Content length: {len(content)} chars")
        print(f"\n📄 RESPONSE CONTENT (first 500 chars):")
        print(content[:500])
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔬 NATIVE WEB SEARCH TESTING")
    print("Testing how GLM and Kimi actually handle web search")
    
    test_glm_native_websearch()
    test_kimi_native_websearch()
    test_kimi_builtin_websearch()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

