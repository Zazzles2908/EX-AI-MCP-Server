#!/usr/bin/env python3
"""
Test MCP server with a real client to see if the issue is with stdin or actual protocol
"""

import asyncio
import json
import sys
from pathlib import Path

# Add repo root to path
_repo_root = Path(__file__).parent
sys.path.insert(0, str(_repo_root))

async def test_mcp_client():
    """Test MCP connection with actual client"""
    import subprocess
    import websockets

    print("=" * 70)
    print("MCP CLIENT CONNECTION TEST")
    print("=" * 70)

    # First, connect to the WebSocket daemon
    print("\n1. Testing WebSocket daemon (port 8079)...")
    try:
        uri = "ws://127.0.0.1:8079"
        async with websockets.connect(uri, timeout=5) as ws:
            print("   ✓ Connected to WebSocket daemon")

            # Send MCP initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            await ws.send(json.dumps(init_msg))
            print("   ✓ Sent MCP initialize")

            # Try to receive response
            try:
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                result = json.loads(response)
                print(f"   ✓ Received response: {result.get('result', {}).get('serverInfo', {})}")

                # Now try tools/list
                tools_msg = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                await ws.send(json.dumps(tools_msg))
                print("   ✓ Sent tools/list request")

                tools_response = await asyncio.wait_for(ws.recv(), timeout=10)
                tools_result = json.loads(tools_response)
                tools = tools_result.get('result', {}).get('tools', [])
                print(f"   ✓ Received {len(tools)} tools")

                return True

            except asyncio.TimeoutError:
                print("   ✗ Timeout waiting for response")
                return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Now test native MCP stdio
    print("\n2. Testing native MCP stdio server...")
    try:
        # Create a simple MCP client that sends initialize
        client_code = """
import asyncio
import json

async def main():
    # Send initialize
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    print(json.dumps(init_msg))
    await asyncio.sleep(0.1)

    # Send tools/list
    tools_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    print(json.dumps(tools_msg))

asyncio.run(main())
"""
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", client_code,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        # Run our MCP server and connect the client
        from src.daemon.mcp_server import DaemonMCPServer
        from tools.registry import get_tool_registry
        from src.providers.registry_core import get_registry_instance

        tool_registry = get_tool_registry()
        provider_registry = get_registry_instance()
        mcp_server = DaemonMCPServer(tool_registry, provider_registry)

        # This should block if working correctly
        try:
            # Set a timeout to see if it blocks or returns immediately
            await asyncio.wait_for(mcp_server.run_stdio(), timeout=3)
            print("   ✗ MCP server returned immediately (BUG!)")
            return False
        except asyncio.TimeoutError:
            print("   ✓ MCP server blocked correctly (waiting for stdin)")
            return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_client())
    sys.exit(0 if success else 1)
