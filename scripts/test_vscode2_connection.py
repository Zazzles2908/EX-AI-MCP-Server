"""
Test VSCode2 MCP Connection

This script tests if VSCode2 can connect to the EXAI daemon and call tools.
Run this from VSCode2 to diagnose the "red tools" issue.

Usage:
    python scripts/test_vscode2_connection.py
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import websockets


async def test_connection():
    """Test direct WebSocket connection to daemon."""
    
    print("=" * 60)
    print("VSCode2 Connection Diagnostic Test")
    print("=" * 60)
    
    # Get connection details from environment
    host = os.getenv("EXAI_WS_HOST", "127.0.0.1")
    port = int(os.getenv("EXAI_WS_PORT", "8079"))
    token = os.getenv("EXAI_WS_TOKEN", "")
    session_id = os.getenv("EXAI_SESSION_ID", "test-session")
    
    print(f"\n[CONFIG]")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  Token: {token[:10]}..." if token else "  Token: (not set)")
    print(f"  Session ID: {session_id}")
    
    # Test 1: Port connectivity
    print(f"\n[TEST 1] Port Connectivity")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"  ✅ Port {port} is reachable")
        else:
            print(f"  ❌ Port {port} is NOT reachable (error code: {result})")
            return False
    except Exception as e:
        print(f"  ❌ Port check failed: {e}")
        return False
    
    # Test 2: WebSocket connection
    print(f"\n[TEST 2] WebSocket Connection")
    try:
        uri = f"ws://{host}:{port}"
        print(f"  Connecting to {uri}...")
        
        async with websockets.connect(uri, ping_interval=None, ping_timeout=None) as ws:
            print(f"  ✅ WebSocket connected")
            
            # Test 3: Hello handshake
            print(f"\n[TEST 3] Hello Handshake")
            hello_msg = {
                "op": "hello",
                "session_id": session_id,
                "token": token
            }
            
            await ws.send(json.dumps(hello_msg))
            print(f"  ✅ Sent hello message")
            
            # Wait for ack
            ack_raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
            ack = json.loads(ack_raw)
            
            if ack.get("op") == "ack":
                print(f"  ✅ Received ack: {ack.get('message', 'OK')}")
            else:
                print(f"  ❌ Unexpected response: {ack}")
                return False
            
            # Test 4: List tools
            print(f"\n[TEST 4] List Tools")
            list_tools_msg = {
                "op": "list_tools",
                "request_id": f"test-{int(time.time())}"
            }
            
            await ws.send(json.dumps(list_tools_msg))
            print(f"  ✅ Sent list_tools request")
            
            # Wait for response
            response_raw = await asyncio.wait_for(ws.recv(), timeout=10.0)
            response = json.loads(response_raw)
            
            if response.get("op") == "tools_list":
                tools = response.get("tools", [])
                print(f"  ✅ Received {len(tools)} tools:")
                for tool in tools[:5]:  # Show first 5
                    print(f"     - {tool.get('name', 'unknown')}")
                if len(tools) > 5:
                    print(f"     ... and {len(tools) - 5} more")
            else:
                print(f"  ❌ Unexpected response: {response}")
                return False
            
            # Test 5: Call a simple tool (chat)
            print(f"\n[TEST 5] Call Chat Tool")
            chat_msg = {
                "op": "call_tool",
                "request_id": f"test-chat-{int(time.time())}",
                "tool_name": "chat_EXAI-WS",
                "arguments": {
                    "prompt": "Hello from VSCode2 diagnostic test! Please respond with 'Connection successful'.",
                    "model": "glm-4.5-flash"
                }
            }
            
            await ws.send(json.dumps(chat_msg))
            print(f"  ✅ Sent chat tool call")
            
            # Wait for response (chat can take a while)
            print(f"  ⏳ Waiting for response (max 30s)...")
            response_raw = await asyncio.wait_for(ws.recv(), timeout=30.0)
            response = json.loads(response_raw)
            
            if response.get("op") == "tool_result":
                result = response.get("result", {})
                if isinstance(result, dict):
                    content = result.get("content", "")
                    print(f"  ✅ Tool call successful!")
                    print(f"  Response preview: {content[:100]}...")
                else:
                    print(f"  ✅ Tool call completed: {result}")
            else:
                print(f"  ❌ Unexpected response: {response}")
                return False
            
            print(f"\n{'=' * 60}")
            print(f"✅ ALL TESTS PASSED - VSCode2 connection is WORKING!")
            print(f"{'=' * 60}")
            print(f"\nIf tools are still RED in VSCode2, the issue is:")
            print(f"  1. VSCode MCP extension not loading the config")
            print(f"  2. VSCode settings pointing to wrong config file")
            print(f"  3. VSCode MCP extension needs restart/reload")
            print(f"\nRecommended actions:")
            print(f"  1. Check VSCode2 settings.json for 'mcp.configPath'")
            print(f"  2. Reload VSCode2 window (Ctrl+Shift+P -> 'Developer: Reload Window')")
            print(f"  3. Restart MCP server (Ctrl+Shift+P -> 'MCP: Restart Server')")
            
            return True
            
    except asyncio.TimeoutError:
        print(f"  ❌ Timeout waiting for response")
        return False
    except websockets.exceptions.WebSocketException as e:
        print(f"  ❌ WebSocket error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main entry point."""
    success = await test_connection()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())

