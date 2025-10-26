#!/usr/bin/env python
"""
Test K2 Models in Schema

This test verifies that K2 models are included in the tool schema.
Previously, K2 models were filtered out by the disallow_substrings filter.

Expected K2 models:
- kimi-k2-0905-preview (user's preferred model)
- kimi-k2-0711-preview
- kimi-k2-turbo-preview
- kimi-thinking-preview
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Bootstrap: Setup path and load environment
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env

# Load environment variables
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"


async def test_k2_models_in_schema():
    """
    Test that K2 models are included in the tool schema.
    """
    print("\n" + "=" * 70)
    print("TEST: K2 Models in Schema Verification")
    print("=" * 70)
    
    # Connect to daemon
    ws = await websockets.connect(WS_URL, open_timeout=10)
    
    # Send hello
    hello = {"op": "hello", "token": WS_TOKEN}
    await ws.send(json.dumps(hello))
    
    # Wait for ack
    ack_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    ack = json.loads(ack_raw)
    
    if ack.get("op") != "hello_ack" or not ack.get("ok"):
        print(f"❌ FAILED: Hello handshake failed: {ack}")
        await ws.close()
        return False
    
    print(f"✅ Connected to daemon (session: {ack.get('session_id')})")
    
    # Request tool list
    list_tools_msg = {"op": "list_tools"}
    await ws.send(json.dumps(list_tools_msg))
    
    # Wait for response
    response_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    response = json.loads(response_raw)
    
    if response.get("op") != "list_tools_res":
        print(f"❌ FAILED: Unexpected response: {response.get('op')}")
        await ws.close()
        return False
    
    tools = response.get("tools", [])
    print(f"\n✅ Received {len(tools)} tools")
    
    # Find a tool with model field (e.g., chat)
    chat_tool = None
    for tool in tools:
        if tool.get("name") == "chat":
            chat_tool = tool
            break
    
    if not chat_tool:
        print(f"❌ FAILED: Chat tool not found")
        await ws.close()
        return False
    
    print(f"\n✅ Found chat tool")
    
    # Get the model field schema
    input_schema = chat_tool.get("inputSchema", {})
    properties = input_schema.get("properties", {})
    model_field = properties.get("model", {})
    
    if not model_field:
        print(f"❌ FAILED: Model field not found in schema")
        await ws.close()
        return False
    
    print(f"\n✅ Found model field in schema")
    
    # Check if model field has enum
    model_enum = model_field.get("enum")
    model_description = model_field.get("description", "")
    
    # Expected K2 models
    expected_k2_models = [
        "kimi-k2-0905-preview",
        "kimi-k2-0711-preview",
        "kimi-k2-turbo-preview",
        "kimi-thinking-preview"
    ]
    
    print(f"\n📋 Checking for K2 models...")
    
    if model_enum:
        print(f"\n✅ Model field has enum with {len(model_enum)} values")
        print(f"\nAll models in enum:")
        for model in sorted(model_enum):
            print(f"  - {model}")
        
        # Check for K2 models
        missing_k2_models = []
        found_k2_models = []
        
        for k2_model in expected_k2_models:
            if k2_model in model_enum:
                found_k2_models.append(k2_model)
            else:
                missing_k2_models.append(k2_model)
        
        print(f"\n📊 K2 Models Status:")
        print(f"  Found: {len(found_k2_models)}/{len(expected_k2_models)}")
        
        if found_k2_models:
            print(f"\n✅ Found K2 models:")
            for model in found_k2_models:
                print(f"  - {model}")
        
        if missing_k2_models:
            print(f"\n❌ Missing K2 models:")
            for model in missing_k2_models:
                print(f"  - {model}")
            
            await ws.close()
            return False
        
        print(f"\n" + "=" * 70)
        print("✅ TEST PASSED: All K2 models found in schema!")
        print("=" * 70)
        print(f"\nThe bug is FIXED:")
        print(f"  - K2 models are no longer filtered out")
        print(f"  - User's preferred model (kimi-k2-0905-preview) is available")
        print(f"  - All K2 preview models are accessible")
        
        await ws.close()
        return True
    
    else:
        # No enum - check description
        print(f"\n⚠️  Model field has no enum (free-form string)")
        print(f"\nModel description:")
        print(f"{model_description}")
        
        # Check if K2 models are mentioned in description
        k2_in_description = []
        for k2_model in expected_k2_models:
            if k2_model in model_description:
                k2_in_description.append(k2_model)
        
        if k2_in_description:
            print(f"\n✅ Found {len(k2_in_description)} K2 models in description:")
            for model in k2_in_description:
                print(f"  - {model}")
            
            if len(k2_in_description) == len(expected_k2_models):
                print(f"\n" + "=" * 70)
                print("✅ TEST PASSED: All K2 models found in description!")
                print("=" * 70)
                await ws.close()
                return True
            else:
                print(f"\n⚠️  WARNING: Only {len(k2_in_description)}/{len(expected_k2_models)} K2 models in description")
                await ws.close()
                return False
        else:
            print(f"\n❌ FAILED: No K2 models found in description")
            await ws.close()
            return False


async def main():
    """Run the test."""
    try:
        success = await test_k2_models_in_schema()
        return 0 if success else 1
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH EXCEPTION: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

