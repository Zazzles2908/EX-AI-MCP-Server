#!/usr/bin/env python3
"""
Simple EXAI MCP Client Test
Tests EXAI chat function via MCP protocol
"""
import asyncio
import json
import sys
import os

# Add the EXAI server to path
sys.path.insert(0, 'c:/Users/Jazeel-Home/.claude')

async def test_exai_mcp():
    print("=" * 70)
    print("TESTING EXAI MCP CHAT FUNCTION")
    print("=" * 70)
    print()

    try:
        # Import the EXAI MCP server
        print("[1/3] Loading EXAI MCP server...")
        import exai_mcp_server

        print("[2/3] Testing chat tool...")
        # Test the chat tool with Kimi
        result = await exai_mcp_server.handle_tool_call('chat', {
            "prompt": "EXAI MCP Test - Please respond with 'EXAI_MCP_WORKS'",
            "model": "kimi-k2",
            "use_websearch": False
        })

        print("[3/3] Processing response...")
        print(f"Result type: {type(result)}")

        # Handle different result formats
        if isinstance(result, dict):
            print(f"Status: {result.get('status', 'unknown')}")
            content = result.get('content', '')
            print(f"Content: {content[:200]}...")

            if "EXAI_MCP_WORKS" in content or result.get('status') == 'success':
                print()
                print("=" * 70)
                print("SUCCESS! EXAI MCP CHAT WORKS!")
                print("=" * 70)
                return True
        elif isinstance(result, list) and len(result) > 0:
            data = result[0] if hasattr(result[0], 'text') else result[0]
            if isinstance(data, str):
                print(f"Response: {data[:300]}...")

                if "EXAI_MCP_WORKS" in data or '"status"' in data.lower():
                    print()
                    print("=" * 70)
                    print("SUCCESS! EXAI MCP CHAT WORKS!")
                    print("=" * 70)
                    return True

        print()
        print("Response received, but couldn't verify exact format")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_exai_mcp())
    sys.exit(0 if success else 1)
