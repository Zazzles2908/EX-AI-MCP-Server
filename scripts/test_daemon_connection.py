#!/usr/bin/env python3
"""
Test daemon WebSocket connection - simulates what the shim does
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

# Load environment
from dotenv import load_dotenv
load_dotenv(dotenv_path=str(_repo_root / ".env"))

import websockets

DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3010"))
DAEMON_TOKEN = os.getenv("EXAI_WS_TOKEN", "")

async def test_connection():
    daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
    print(f"Testing connection to: {daemon_uri}")
    print(f"Token: {DAEMON_TOKEN[:20] if DAEMON_TOKEN else 'NOT SET'}...")

    try:
        async with websockets.connect(daemon_uri) as ws:
            print("[OK] WebSocket connected!")

            # Send hello
            hello_msg = {
                "op": "hello",
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
                "token": DAEMON_TOKEN
            }
            print(f"Sending hello: {json.dumps(hello_msg, indent=2)}")
            await ws.send(json.dumps(hello_msg))

            # Wait for hello_ack
            response = await asyncio.wait_for(ws.recv(), timeout=10)
            hello_ack = json.loads(response)
            print(f"Received hello_ack: {json.dumps(hello_ack, indent=2)}")

            if not hello_ack.get("ok"):
                print("[FAIL] Daemon rejected connection")
                return False

            print("[OK] Daemon accepted connection!")

            # Test list_tools
            print("\nTesting list_tools...")
            list_request = {
                "op": "list_tools",
                "id": "test_list"
            }
            await ws.send(json.dumps(list_request))

            response = await asyncio.wait_for(ws.recv(), timeout=10)
            tools_response = json.loads(response)
            print(f"Received tools: {json.dumps(tools_response, indent=2)}")

            tools = tools_response.get("tools", [])
            print(f"\n[OK] Successfully retrieved {len(tools)} tools from daemon!")

            return True

    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
