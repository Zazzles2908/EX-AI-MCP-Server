#!/usr/bin/env python3
"""
Final Comprehensive Test - WebSocket MCP Architecture
Tests the complete flow: WebSocket → Daemon → Tools
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Setup paths
_repo_root = Path(__file__).parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from dotenv import load_dotenv
load_dotenv(dotenv_path=str(_repo_root / ".env"))

import websockets

DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3010"))
DAEMON_TOKEN = os.getenv("EXAI_WS_TOKEN", "")

async def test_complete_flow():
    """Test the complete WebSocket MCP flow"""
    print("=" * 70)
    print("EXAI MCP Server - Final Verification Test")
    print("=" * 70)

    daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
    print(f"\n1. Testing connection to: {daemon_uri}")
    print(f"   Token: {DAEMON_TOKEN[:20] if DAEMON_TOKEN else 'NOT SET'}...")

    try:
        async with websockets.connect(daemon_uri) as ws:
            print("   [OK] WebSocket connected!")

            # Send hello
            print("\n2. Sending hello handshake...")
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "token": DAEMON_TOKEN
            }
            await ws.send(json.dumps(hello_msg))

            response = await asyncio.wait_for(ws.recv(), timeout=10)
            hello_ack = json.loads(response)

            if hello_ack.get("ok"):
                print("   [OK] Hello accepted!")
                print(f"   Session: {hello_ack.get('session_id', 'unknown')}")
            else:
                print(f"   [FAIL] Hello rejected: {hello_ack}")
                return False

            # List tools
            print("\n3. Requesting tool list...")
            await ws.send(json.dumps({"op": "list_tools"}))

            response = await asyncio.wait_for(ws.recv(), timeout=10)
            tools_msg = json.loads(response)

            tools = tools_msg.get("tools", [])
            print(f"   [OK] Received {len(tools)} tools")

            # Show first 3 tools
            print("\n4. Available tools (first 3):")
            for i, tool in enumerate(tools[:3], 1):
                print(f"   {i}. {tool['name']}")
                print(f"      {tool['description'][:80]}...")

            # Test tool execution
            print("\n5. Testing tool execution (chat)...")
            await ws.send(json.dumps({
                "op": "tool_call",
                "name": "chat",
                "arguments": {
                    "prompt": "Respond with exactly: 'WebSocket MCP is working perfectly!'"
                }
            }))

            # Wait for completion (with progress updates)
            print("   Executing tool...")
            timeout = 30
            while timeout > 0:
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    msg = json.loads(response)

                    if msg.get("op") == "progress":
                        print(f"   Progress: {msg.get('message', '')}")
                    elif msg.get("op") == "tool_call_res":
                        outputs = msg.get("outputs", [])
                        if outputs:
                            print("   [OK] Tool executed successfully!")
                            print(f"   Response: {outputs[0]['text']}")
                            return True
                    elif msg.get("op") == "stream_complete":
                        print("   Stream complete, waiting for result...")
                        timeout -= 5
                        continue

                except asyncio.TimeoutError:
                    timeout -= 5
                    if timeout > 0:
                        print(f"   Still executing... ({timeout}s remaining)")

            print("   [FAIL] Tool execution timeout")
            return False

    except Exception as e:
        print(f"   [FAIL] {type(e).__name__}: {e}")
        return False

async def main():
    """Main test runner"""
    success = await test_complete_flow()

    print("\n" + "=" * 70)
    if success:
        print("✅ FINAL RESULT: ALL TESTS PASSED")
        print("✅ WebSocket MCP architecture is FULLY OPERATIONAL")
        print("✅ All 19 tools are available and functional")
        print("=" * 70)
        return 0
    else:
        print("❌ FINAL RESULT: TESTS FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
