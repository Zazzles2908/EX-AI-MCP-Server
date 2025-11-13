#!/usr/bin/env python3
"""
EXAI MCP Test with correct tool name
"""
import asyncio
import json
import sys
sys.path.insert(0, 'c:/Users/Jazeel-Home/.claude')

async def test_exai_mcp():
    print("=" * 70)
    print("TESTING EXAI MCP CHAT FUNCTION")
    print("=" * 70)
    print()

    import exai_mcp_server

    # Test 1: Check available tools
    print("[1/4] Listing available tools...")
    tools = await exai_mcp_server.handle_list_tools({})
    print(f"Available tools: {tools.get('tools', [])}")
    print()

    # Test 2: Chat with Kimi
    print("[2/4] Testing exai_chat with Kimi K2...")
    result = await exai_mcp_server.handle_tool_call('exai_chat', {
        "prompt": "EXAI MCP Test - Please respond with 'EXAI_MCP_WORKS'",
        "model": "kimi-k2",
        "use_websearch": False
    })
    print(f"Result: {json.dumps(result, indent=2)[:500]}...")
    print()

    # Test 3: Chat with GLM
    print("[3/4] Testing exai_chat with GLM-4.6...")
    result2 = await exai_mcp_server.handle_tool_call('exai_chat', {
        "prompt": "EXAI MCP GLM Test - Please respond with 'GLM_WORKS'",
        "model": "glm-4.6",
        "use_websearch": False
    })
    print(f"Result: {json.dumps(result2, indent=2)[:500]}...")
    print()

    # Test 4: Check status
    print("[4/4] Checking EXAI status...")
    status = await exai_mcp_server.handle_tool_call('exai_status', {})
    print(f"Status: {json.dumps(status, indent=2)[:300]}...")
    print()

    print("=" * 70)
    print("EXAI MCP TEST COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(test_exai_mcp())
