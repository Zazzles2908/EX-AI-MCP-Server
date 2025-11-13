#!/usr/bin/env python3
"""
Run the shim and capture all output to understand what's happening
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

async def main():
    """Run shim and interact via stdio."""

    print("Starting MCP shim process...")

    # Start the shim as a subprocess
    shim_path = _repo_root / "scripts" / "runtime" / "run_ws_shim.py"
    python_exe = sys.executable

    process = await asyncio.create_subprocess_exec(
        python_exe, str(shim_path),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        limit=1024*1024  # 1MB buffer for large responses
    )

    print(f"Shim process started (PID: {process.pid})")

    # Read stderr in background to see logs
    async def read_stderr():
        while True:
            line = await process.stderr.readline()
            if not line:
                break
            print(f"[SHIM-LOG] {line.decode().rstrip()}")

    stderr_task = asyncio.create_task(read_stderr())

    try:
        # Wait a moment for shim to initialize
        await asyncio.sleep(2)

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
        line = await asyncio.wait_for(process.stdout.readline(), timeout=5)
        initialize_response = json.loads(line.decode())
        print(f"Received initialize response")

        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }

        print(f"Sending initialized notification...")
        process.stdin.write(json.dumps(initialized_notification).encode() + b'\n')
        await process.stdin.drain()

        # Wait a moment
        await asyncio.sleep(2)

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
        # Read the full response (may span multiple lines for large tool lists)
        response_data = b""
        while True:
            chunk = await process.stdout.read(4096)
            if b'\n' in chunk:
                # Found newline, this might be the complete response
                response_data += chunk
                # Check if we have a complete JSON object
                try:
                    # Try to parse to see if we have complete JSON
                    test_data = response_data.decode().strip()
                    if test_data:
                        json.loads(test_data)
                        # Successfully parsed, we have complete JSON
                        break
                except json.JSONDecodeError:
                    # Not complete JSON yet, continue reading
                    continue
            elif not chunk:
                # EOF
                break
            else:
                response_data += chunk

        tools_response = json.loads(response_data.decode().strip())

        if "error" in tools_response:
            print(f"\nERROR in response:")
            print(json.dumps(tools_response['error'], indent=2))
        else:
            tools_count = len(tools_response.get('result', {}).get('tools', []))
            print(f"\n[SUCCESS] Received tools/list response with {tools_count} tools")
            if tools_count > 0:
                first_tool = tools_response.get('result', {}).get('tools', [{}])[0]
                print(f"First tool: {first_tool.get('name', 'NONE')}")
                print(f"Tool description preview: {first_tool.get('description', '')[:100]}...")

        # Keep alive and show logs
        print("\nKeeping process alive for 30 seconds to see logs...")
        await asyncio.sleep(30)

    except asyncio.TimeoutError:
        print("\n[TIMEOUT] Something timed out")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print(f"\nTerminating shim process...")
        stderr_task.cancel()
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
