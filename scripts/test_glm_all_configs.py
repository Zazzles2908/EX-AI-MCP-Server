#!/usr/bin/env python
"""
Test GLM web search with all possible configurations.
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
print("GLM WEB SEARCH - ALL CONFIGURATIONS TEST")
print("="*80)

query = "What is the current weather in Tokyo?"

# Test configurations
configs = [
    {
        "name": "Config 1: Basic web_search",
        "model": "glm-4-plus",
        "tools": [{
            "type": "web_search",
            "web_search": {}
        }]
    },
    {
        "name": "Config 2: With enable_search=True",
        "model": "glm-4-plus",
        "tools": [{
            "type": "web_search",
            "web_search": {
                "enable_search": True
            }
        }]
    },
    {
        "name": "Config 3: Full config",
        "model": "glm-4-plus",
        "tools": [{
            "type": "web_search",
            "web_search": {
                "search_engine": "search_pro_jina",
                "search_recency_filter": "oneDay",
                "search_result": True,
                "require_search": True
            }
        }]
    },
]

for config in configs:
    print(f"\n" + "="*80)
    print(f"{config['name']}")
    print(f"Model: {config['model']}")
    print("="*80)
    
    print(f"\n🔧 Tools:")
    print(json.dumps(config['tools'], indent=2))
    
    try:
        response = client.chat.completions.create(
            model=config['model'],
            messages=[{"role": "user", "content": query}],
            tools=config['tools'],
            tool_choice="auto"
        )
        
        print(f"\n✅ Response received")
        print(f"📊 Finish reason: {response.choices[0].finish_reason}")
        
        # Check for tool_calls
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            print(f"🔧 Tool calls: {len(tool_calls)}")
        else:
            print(f"🔧 No tool calls")
        
        # Print content
        content = response.choices[0].message.content or ""
        print(f"\n📝 Content ({len(content)} chars):")
        print(content[:300])
        
        # Check for search indicators
        if "real-time" in content.lower() or "don't have access" in content.lower():
            print(f"\n❌ Model says it doesn't have real-time access - SEARCH NOT WORKING")
        elif "weather" in content.lower() and ("tokyo" in content.lower() or "temperature" in content.lower()):
            print(f"\n✅ Response contains weather info - SEARCH MIGHT BE WORKING!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

print(f"\n" + "="*80)
print("TESTING COMPLETE")
print("="*80)

