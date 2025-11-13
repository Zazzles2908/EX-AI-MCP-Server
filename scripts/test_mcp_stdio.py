#!/usr/bin/env python3
"""
Test MCP stdio communication - simulates what VSCode does
"""

import asyncio
import json
import sys
from pathlib import Path

# Setup paths
_repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(_repo_root))

# Load environment
from dotenv import load_dotenv
load_dotenv(dotenv_path=str(_repo_root / ".env"))

import subprocess

async def test_mcp_stdio():
    """Test MCP stdio communication with the shim."""

    print("Starting MCP shim process...")

    # Start the shim as a subprocess
    shim_path = _repo_root / "scripts" / "runtime" / "run_ws_shim.py"
    python_exe = sys.executable

    process = await asyncio.create_subprocess_exec(
        python_exe, str(shim_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    print(f"Shim process started (PID: {process.pid})")

    try:
        # Send initialize request
        initialize_request = {
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

        print(f"\nSending initialize request...")
        process.stdin.write(json.dumps(initialize_request).encode() + b'\n')
        await process.stdin.drain()

        # Read initialize response
        print("Reading initialize response...")
        line = await process.stdout.readline()
        initialize_response = json.loads(line.decode())
        print(f"Received initialize response: {json.dumps(initialize_response, indent=2)}")

        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }

        print(f"\nSending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification).encode() + b'\n')
        await process.stdin.drain()

        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }

        print(f"\nSending tools/list request...")
        process.stdin.write(json.dumps(tools_request).encode() + b'\n')
        await process.stdin.drain()

        # Read tools/list response
        print("Reading tools/list response...")
        line = await asyncio.wait_for(process.stdout.readline(), timeout=10)
        tools_response = json.loads(line.decode())

        if "error" in tools_response:
            print(f"ERROR in response: {json.dumps(tools_response['error'], indent=2)}")
            return False

        print(f"Received tools/list response with {len(tools_response.get('result', {}).get('tools', []))} tools")
        print(f"First tool: {tools_response.get('result', {}).get('tools', [{}])[0].get('name', 'NONE')}")

        print("\n[SUCCESS] MCP stdio communication test passed!")
        return True

    except asyncio.TimeoutError:
        print("\n[FAIL] Timeout waiting for tools/list response")
        return False
    except Exception as e:
        print(f"\n[FAIL] Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        print(f"\nTerminating shim process (PID: {process.pid})...")
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_stdio())
    sys.exit(0 if success else 1)
