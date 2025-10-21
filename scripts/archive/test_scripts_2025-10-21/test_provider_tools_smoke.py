#!/usr/bin/env python
"""
Provider-Specific Tools Smoke Test

Quick smoke test to verify provider-specific tools are accessible and respond.
This is NOT a comprehensive functional test - just verifies tools exist and can be called.

Provider Tools (8 total):
- Kimi tools (5): kimi_upload_and_extract, kimi_multi_file_chat, kimi_intent_analysis, 
                  kimi_capture_headers, kimi_chat_with_tools
- GLM tools (3): glm_upload_file, glm_web_search, glm_payload_preview
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Bootstrap
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env
load_env()

import websockets

# Configuration
WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "")
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"


async def check_tool_exists(tool_name):
    """Quick check if a tool exists in the tool list."""
    ws = await websockets.connect(WS_URL, open_timeout=10)
    
    # Send hello
    hello = {"op": "hello", "token": WS_TOKEN}
    await ws.send(json.dumps(hello))
    
    # Wait for ack
    ack_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    ack = json.loads(ack_raw)
    
    if ack.get("op") != "hello_ack" or not ack.get("ok"):
        await ws.close()
        return False
    
    # Request tool list
    list_tools_msg = {"op": "list_tools"}
    await ws.send(json.dumps(list_tools_msg))
    
    # Wait for response
    response_raw = await asyncio.wait_for(ws.recv(), timeout=10)
    response = json.loads(response_raw)
    
    if response.get("op") != "list_tools_res":
        await ws.close()
        return False
    
    tools = response.get("tools", [])
    tool_names = [t.get("name") for t in tools]
    
    await ws.close()
    
    return tool_name in tool_names


async def main():
    """Run smoke tests for all provider tools."""
    print("\n" + "=" * 70)
    print("PROVIDER-SPECIFIC TOOLS SMOKE TEST")
    print("=" * 70)
    print("Testing 8 provider-specific tools (quick existence check)")
    
    # Define provider tools
    kimi_tools = [
        "kimi_upload_and_extract",
        "kimi_multi_file_chat",
        "kimi_intent_analysis",
        "kimi_capture_headers",
        "kimi_chat_with_tools"
    ]
    
    glm_tools = [
        "glm_upload_file",
        "glm_web_search",
        "glm_payload_preview"
    ]
    
    all_provider_tools = kimi_tools + glm_tools
    
    results = {}
    
    print(f"\n📋 Checking {len(all_provider_tools)} provider tools...")
    
    for tool_name in all_provider_tools:
        try:
            exists = await check_tool_exists(tool_name)
            results[tool_name] = exists
            status = "✅" if exists else "❌"
            print(f"  {status} {tool_name}")
        except Exception as e:
            results[tool_name] = False
            print(f"  ❌ {tool_name} (error: {e})")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTools found: {passed}/{total}")
    
    # Breakdown by provider
    kimi_passed = sum(1 for t in kimi_tools if results.get(t, False))
    glm_passed = sum(1 for t in glm_tools if results.get(t, False))
    
    print(f"\nKimi tools: {kimi_passed}/{len(kimi_tools)}")
    for tool in kimi_tools:
        status = "✅" if results.get(tool, False) else "❌"
        print(f"  {status} {tool}")
    
    print(f"\nGLM tools: {glm_passed}/{len(glm_tools)}")
    for tool in glm_tools:
        status = "✅" if results.get(tool, False) else "❌"
        print(f"  {status} {tool}")
    
    if passed == total:
        print(f"\n✅ ALL PROVIDER TOOLS FOUND!")
        print(f"\n📊 Provider Tools Coverage: {passed}/{total} (100%)")
        print(f"\nNOTE: This is a smoke test - tools exist and are registered.")
        print(f"      Functional testing of these tools requires:")
        print(f"      - File upload capabilities")
        print(f"      - Web search integration")
        print(f"      - Provider-specific features")
        return 0
    else:
        print(f"\n❌ SOME PROVIDER TOOLS MISSING")
        missing = [t for t, exists in results.items() if not exists]
        print(f"\nMissing tools:")
        for tool in missing:
            print(f"  - {tool}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

