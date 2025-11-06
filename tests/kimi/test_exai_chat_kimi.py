#!/usr/bin/env python
"""Test EXAI chat with Kimi."""
import asyncio
import json
import websockets
import os

async def test_chat_kimi():
    """Test chat with Kimi model."""
    ws_host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    ws_port = int(os.getenv("EXAI_WS_PORT", "8079"))
    uri = f"ws://{ws_host}:{ws_port}"

    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as ws:
        # Send hello
        await ws.send(json.dumps({"op": "hello", "client": "test", "version": "1.0", "token": "test-token-12345"}))
        await ws.recv()

        # Send chat request with Kimi
        await ws.send(json.dumps({
            "op": "tool_call",
            "request_id": "test-chat-kimi-123",
            "tool": {"name": "chat"},
            "arguments": {
                "prompt": "Say 'EXAI_KIMI_WORKS'",
                "model": "kimi-k2",
                "use_websearch": False
            }
        }))
        print("Sent Kimi chat request...")

        # Receive response
        raw = await ws.recv()
        resp = json.loads(raw)
        print(f"Response: {json.dumps(resp, indent=2)[:300]}...")

        if resp.get("op") == "call_tool_res" or resp.get("op") == "stream_complete":
            print("\n[SUCCESS] Kimi chat completed")
            return True
        else:
            print(f"\n[FAILED] Unexpected response: {resp}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_chat_kimi())
    print(f"\n{'='*60}")
    print(f"Kimi Chat Test: {'PASSED' if success else 'FAILED'}")
    print(f"{'='*60}")
    exit(0 if success else 1)
