#!/usr/bin/env python
"""
Test script to verify tool execution works.
"""
import asyncio
import websockets
import json
import sys

async def test_tool_execution():
    """Test tool execution via WebSocket."""
    import os

    # Determine if we're in Docker or on host
    in_docker = os.path.exists('/.dockerenv')
    port = "8079" if in_docker else "3000"

    uri = f"ws://localhost:{port}"
    print(f"[INFO] Testing from {'Docker' if in_docker else 'host'}, connecting to {uri}")

    # Authentication token
    token = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"

    try:
        async with websockets.connect(uri) as websocket:
            print(f"[OK] Connected to {uri}")

            # Send hello
            hello_msg = {
                "op": "hello",
                "token": token
            }
            await websocket.send(json.dumps(hello_msg))
            print(f"[SEND] Sent hello")

            # Wait for hello response
            response = await websocket.recv()
            hello_resp = json.loads(response)
            print(f"[RECV] Hello response: {json.dumps(hello_resp, indent=2)}")
            if not hello_resp.get("ok"):
                print(f"[ERROR] Hello failed: {hello_resp}")
                return False

            # List tools
            list_msg = {
                "op": "list_tools",
                "request_id": "test-1"
            }
            await websocket.send(json.dumps(list_msg))
            print(f"[SEND] Sent list_tools")

            # Wait for tools list
            response = await websocket.recv()
            tools_resp = json.loads(response)
            print(f"[RECV] Tools response: {json.dumps(tools_resp, indent=2)}")

            tools = tools_resp.get("tools", [])
            if not tools:
                print(f"[ERROR] No tools returned")
                return False

            print(f"[OK] Found {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', '')[:50]}...")

            # Test chat tool - use the schema from the tools list
            chat_tool = next((t for t in tools if t.get("name") == "chat"), None)
            if chat_tool:
                schema = chat_tool.get("inputSchema", {})
                required = schema.get("required", [])
                properties = schema.get("properties", {})
                print(f"[INFO] Chat schema: required={required}")
                print(f"[INFO] Chat properties: {list(properties.keys())}")

            # Send tool call with correct schema based on the actual tool structure
            chat_msg = {
                "op": "tool_call",
                "request_id": "test-2",
                "tool": {
                    "name": "chat"
                },
                "arguments": {
                    "prompt": "Say hello!"  # Use "prompt" not "message"
                }
            }
            await websocket.send(json.dumps(chat_msg))
            print(f"[SEND] Sent chat tool call")

            # Wait for response with timeout
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30)
                chat_resp = json.loads(response)
                print(f"[RECV] Chat tool response: {json.dumps(chat_resp, indent=2)}")

                if "error" in chat_resp:
                    print(f"[FAIL] Chat tool FAILED")
                    print(f"  Error code: {chat_resp['error'].get('code', 'N/A')}")
                    print(f"  Error message: {chat_resp['error'].get('message', 'N/A')}")
                    return False
                else:
                    print(f"[OK] Chat tool SUCCESS!")
                    # Check for outputs
                    outputs = chat_resp.get("outputs", [])
                    if outputs:
                        print(f"  Got {len(outputs)} output(s)")
                        for i, output in enumerate(outputs):
                            print(f"  Output {i+1}: {str(output)[:100]}...")
                    return True
            except asyncio.TimeoutError:
                print(f"[FAIL] Chat tool timed out after 30 seconds")
                return False

    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_tool_execution())
    sys.exit(0 if success else 1)
