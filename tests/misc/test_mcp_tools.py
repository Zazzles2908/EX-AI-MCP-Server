#!/usr/bin/env python
"""Test MCP shim tool listing directly."""
import asyncio
import json
import websockets
import os

async def test_list_tools():
    """Test list_tools via WebSocket."""
    ws_host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    ws_port = int(os.getenv("EXAI_WS_PORT", "8079"))
    uri = f"ws://{ws_host}:{ws_port}"

    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        # Send hello first
        hello_msg = {
            "op": "hello",
            "client": "test-client",
            "version": "1.0",
            "token": "test-token-12345"
        }
        await ws.send(json.dumps(hello_msg))
        print(f"Sent hello: {hello_msg}")
        hello_resp = await ws.recv()
        print(f"Hello response: {json.loads(hello_resp)}")

        # Send list_tools request
        req_id = "test-list-tools-123"
        msg = {
            "op": "list_tools",
            "request_id": req_id
        }
        await ws.send(json.dumps(msg))
        print(f"Sent: {msg}")

        # Receive response
        raw = await ws.recv()
        resp = json.loads(raw)
        print(f"Received: {json.dumps(resp, indent=2)[:200]}...")

        if resp.get("op") == "list_tools_res":
            tools = resp.get("tools", [])
            print(f"\n[SUCCESS] Received {len(tools)} tools")
            print(f"Tool names: {[t.get('name') for t in tools[:5]]}{'...' if len(tools) > 5 else ''}")
            return True
        else:
            print(f"\n[FAILED] Unexpected response: {resp}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_list_tools())
    exit(0 if success else 1)
