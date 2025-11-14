#!/usr/bin/env python3
"""Test MCP server doesn't exit in 'both' mode"""

import asyncio
import subprocess
import time
import sys

async def test_both_mode_stability():
    """Test that 'both' mode MCP server doesn't exit unexpectedly."""
    print("🧪 Testing 'both' mode MCP server stability...")

    try:
        # Start in both mode
        proc = subprocess.Popen([
            'python', '-m', 'src.daemon.ws_server', '--mode', 'both'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Wait for startup
        await asyncio.sleep(5)

        # Check if process is still running
        poll = proc.poll()
        if poll is not None:
            stdout, stderr = proc.communicate()
            print(f"❌ Process exited with code {poll}")
            print(f"STDOUT:\n{stdout}")
            print(f"STDERR:\n{stderr}")
            return False

        print("✅ Both mode process still running after 5 seconds")

        # Check logs for critical errors
        logs = subprocess.run([
            'docker', 'logs', '--tail', '50', 'exai-mcp-server'
        ], capture_output=True, text=True)

        if "app.run() returned" in logs.stderr:
            print("❌ MCP server exited unexpectedly")
            return False

        if "RuntimeError: no running event loop" in logs.stderr:
            print("❌ Async event loop error still present")
            return False

        print("✅ No critical errors detected")

        # Clean shutdown
        proc.terminate()
        await asyncio.sleep(2)
        proc.wait(timeout=5)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_both_mode_stability())
    sys.exit(0 if success else 1)
