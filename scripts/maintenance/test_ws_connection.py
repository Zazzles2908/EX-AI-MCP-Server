#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test WebSocket connection to daemon - simulates VSCode MCP client."""
import asyncio
import json
import websockets
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8

# Add repo root to path
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env
load_env()

import os

WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "test-token-12345")

async def test_connection(session_id: str):
    """Test WebSocket connection and list_tools operation."""
    uri = f"ws://{WS_HOST}:{WS_PORT}"
    
    print(f"\n{'='*80}")
    print(f"Testing connection for session: {session_id}")
    print(f"URI: {uri}")
    print(f"{'='*80}\n")
    
    try:
        async with websockets.connect(uri, ping_interval=45, ping_timeout=240) as ws:
            print(f"[OK] Connected to {uri}")

            # Send hello message
            hello_msg = {
                "op": "hello",
                "session_id": session_id,
                "token": WS_TOKEN
            }
            print(f"\n[SEND] Sending hello: {json.dumps(hello_msg, indent=2)}")
            await ws.send(json.dumps(hello_msg))

            # Wait for hello response
            print("[WAIT] Waiting for hello response...")
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            hello_resp = json.loads(raw)
            print(f"[RECV] Received hello response: {json.dumps(hello_resp, indent=2)}")

            if hello_resp.get("op") != "hello_ack":
                print(f"[ERROR] Expected hello_ack, got {hello_resp.get('op')}")
                return False

            print("[OK] Hello handshake successful!")

            # Send list_tools request
            list_tools_msg = {"op": "list_tools"}
            print(f"\n[SEND] Sending list_tools: {json.dumps(list_tools_msg, indent=2)}")
            await ws.send(json.dumps(list_tools_msg))

            # Wait for list_tools response
            print("[WAIT] Waiting for list_tools response...")
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            tools_resp = json.loads(raw)
            print(f"[RECV] Received response op={tools_resp.get('op')}")

            if tools_resp.get("op") != "list_tools_res":
                print(f"[ERROR] Expected list_tools_res, got {tools_resp.get('op')}")
                print(f"Full response: {json.dumps(tools_resp, indent=2)}")
                return False

            tools = tools_resp.get("tools", [])
            print(f"[OK] Received {len(tools)} tools!")
            print(f"Tool names: {[t['name'] for t in tools[:5]]}{'...' if len(tools) > 5 else ''}")

            # Test second list_tools request (this is where it fails!)
            print(f"\n[SEND] Sending SECOND list_tools request...")
            await ws.send(json.dumps(list_tools_msg))

            print("[WAIT] Waiting for SECOND list_tools response...")
            raw = await asyncio.wait_for(ws.recv(), timeout=10)
            tools_resp2 = json.loads(raw)
            print(f"[RECV] Received SECOND response op={tools_resp2.get('op')}")

            if tools_resp2.get("op") != "list_tools_res":
                print(f"[ERROR] Second list_tools failed! Got {tools_resp2.get('op')}")
                return False

            print(f"[OK] SECOND list_tools successful! Received {len(tools_resp2.get('tools', []))} tools")

            return True

    except asyncio.TimeoutError:
        print("[ERROR] TIMEOUT: No response from daemon!")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run tests for both sessions."""
    print("\n" + "="*80)
    print("WebSocket Connection Test")
    print("="*80)
    
    # Test session 1
    result1 = await test_connection("vscode-instance-1")
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test session 2
    result2 = await test_connection("vscode-instance-2")

    print("\n" + "="*80)
    print("TEST RESULTS")
    print("="*80)
    print(f"Session 1 (vscode-instance-1): {'[PASS]' if result1 else '[FAIL]'}")
    print(f"Session 2 (vscode-instance-2): {'[PASS]' if result2 else '[FAIL]'}")
    print("="*80 + "\n")

    return result1 and result2

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

