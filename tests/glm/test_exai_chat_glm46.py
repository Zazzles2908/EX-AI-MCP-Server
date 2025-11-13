#!/usr/bin/env python
"""Test EXAI chat with GLM-4.6 via WebSocket."""
import asyncio
import json
import websockets
import os

async def test_chat_glm46():
    """Test chat with GLM-4.6 model."""
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
        hello_resp = json.loads(await ws.recv())
        print(f"Hello: {hello_resp['ok']}")

        # Send chat request
        req_id = "test-chat-glm46-123"
        msg = {
            "op": "tool_call",
            "request_id": req_id,
            "tool": {"name": "chat"},
            "arguments": {
                "prompt": "Say 'EXAI_CHAT_WORKS' in exactly those words",
                "model": "glm-4.6",
                "use_websearch": False
            }
        }
        await ws.send(json.dumps(msg))
        print(f"Sent chat request with GLM-4.6...")

        # Receive response
        raw = await ws.recv()
        resp = json.loads(raw)
        print(f"Received response (first 200 chars): {json.dumps(resp, indent=2)[:200]}...")

        # Response could be tool_call_res, call_tool_res, or stream_complete
        if resp.get("op") in ("tool_call_res", "call_tool_res", "stream_complete"):
            print(f"\n[SUCCESS] Received {resp.get('op')} response")
            # Check for any content in the response
            if "outputs" in resp and resp["outputs"]:
                outputs = resp.get("outputs", [])
                if outputs and len(outputs) > 0:
                    content = outputs[0].get("text", "")
                    # Check if it's an error
                    if content.startswith('{"status":"error"'):
                        print(f"[ERROR] API Error: {content[:200]}")
                        # Check the specific error
                        try:
                            import json as json_mod
                            error_data = json_mod.loads(content)
                            print(f"Error details: {error_data}")
                        except:
                            pass
                        return False
                    else:
                        print(f"Chat response content: {content[:100]}")
                        return "EXAI_CHAT_WORKS" in content
            print("No content in response")
            return True
        else:
            print(f"\n[ERROR] Unexpected response: {resp}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_chat_glm46())
    print(f"\n{'='*60}")
    print(f"GLM-4.6 Chat Test: {'PASSED' if success else 'FAILED'}")
    print(f"{'='*60}")
    exit(0 if success else 1)
