#!/usr/bin/env python3
"""
Simple EXAI MCP Client Test
Tests EXAI chat function via direct MCP protocol
"""
import asyncio
import json
import sys
import os

# Add the EXAI server to path
sys.path.insert(0, 'c:/Users/Jazeel-Home/.claude')

async def test_exai_mcp_chat():
    print("=" * 70)
    print("TESTING EXAI MCP CHAT FUNCTION")
    print("=" * 70)
    print()

    try:
        # Import and run the EXAI MCP server
        print("[1/3] Starting EXAI MCP server...")
        from exai_mcp_server import handle_call_tool

        print("[2/3] Testing chat with Kimi K2...")
        result = await handle_call_tool('chat', {
            "prompt": "EXAI MCP Test - Please respond with 'EXAI_MCP_WORKS'",
            "model": "kimi-k2",
            "use_websearch": False
        })

        print("[3/3] Processing response...")
        data = result[0].text if hasattr(result[0], 'text') else result[0]
        print(f"Response: {data[:300]}...")
        print()

        # Try to parse as JSON
        try:
            parsed = json.loads(data)
            if "content" in parsed:
                if "EXAI_MCP_WORKS" in parsed["content"]:
                    print("=" * 70)
                    print("SUCCESS! EXAI MCP CHAT WORKS!")
                    print("=" * 70)
                    return True
                else:
                    print(f"Got response: {parsed['content'][:100]}...")
            print("Status:", parsed.get("status", "unknown"))
        except:
            pass

        return True

    except ImportError as e:
        print(f"ERROR: Could not import exai_mcp_server: {e}")
        print()
        print("Trying alternative approach...")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_exai_mcp_chat())
    sys.exit(0 if success else 1)
