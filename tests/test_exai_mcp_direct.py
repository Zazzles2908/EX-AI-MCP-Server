#!/usr/bin/env python3
"""
Direct EXAI WebSocket Test
Tests the EXAI MCP daemon directly via WebSocket to verify it's working.
"""

import asyncio
import websockets
import json
import sys

async def test_exai():
    """Test EXAI daemon directly."""
    uri = "ws://127.0.0.1:3010"

    print(f"Connecting to EXAI at {uri}...")
    print(f"Time: {sys.argv[1] if len(sys.argv) > 1 else 'N/A'}")
    print()

    async with websockets.connect(uri) as websocket:
        # Send hello
        hello = {
            "op": "hello",
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
            "token": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        }
        await websocket.send(json.dumps(hello))
        print("✅ Sent hello message")

        # Wait for hello_ack
        response = await websocket.recv()
        ack = json.loads(response)
        print(f"✅ Received hello_ack: {ack}")

        if not ack.get("ok"):
            print(f"❌ Hello rejected: {ack.get('error')}")
            return False

        # Test list_models tool
        print("\n" + "="*60)
        print("Testing list_models tool...")
        print("="*60)

        list_req = {
            "op": "list_tools",
            "id": "test_list_models"
        }
        await websocket.send(json.dumps(list_req))
        response = await websocket.recv()
        result = json.loads(response)

        print(f"\n📋 Available Tools: {len(result.get('tools', []))}")
        for tool in result.get('tools', [])[:5]:
            print(f"  - {tool['name']}: {tool.get('description', '')[:60]}...")

        if result.get('tools'):
            print(f"\n✅ EXAI MCP is working! ({len(result.get('tools'))} tools available)")
            return True
        else:
            print(f"\n❌ No tools returned")
            return False

async def main():
    try:
        success = await test_exai()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
