#!/usr/bin/env python3
"""
Standalone test to debug MCP stdio server issue
This will help identify why app.run() exits immediately
"""

import asyncio
import sys
from pathlib import Path

# Add repo root to path
_repo_root = Path(__file__).parent
sys.path.insert(0, str(_repo_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

# Create a simple MCP server for testing
app = Server("test-mcp")

@app.list_tools()
async def handle_list_tools():
    print("DEBUG: handle_list_tools() called", flush=True)
    return []

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    print(f"DEBUG: handle_call_tool() called: {name}", flush=True)
    return [TextContent(type="text", text=f"Test result for {name}")]

async def test_stdio():
    print("=" * 70)
    print("MCP STDIO DEBUG TEST")
    print("=" * 70)
    print(f"Python version: {sys.version}")
    print(f"MCP library imported successfully", flush=True)

    try:
        async with stdio_server() as (read_stream, write_stream):
            print("DEBUG: stdio_server context entered", flush=True)
            print("DEBUG: About to call app.run()...", flush=True)

            # Call app.run() with proper initialization options
            init_options = app.create_initialization_options()
            print(f"DEBUG: Initialization options created: {init_options}", flush=True)

            # This is the critical call - let's see what happens
            try:
                await app.run(
                    read_stream,
                    write_stream,
                    init_options
                )
                print("ERROR: app.run() returned - THIS IS THE BUG!", flush=True)
            except asyncio.CancelledError:
                print("DEBUG: app.run() was cancelled", flush=True)
                raise
            except Exception as e:
                print(f"ERROR: app.run() raised exception: {e}", flush=True)
                raise

            print("ERROR: Should never reach here!", flush=True)

    except Exception as e:
        print(f"ERROR: stdio_server exception: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(test_stdio())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("DEBUG: Interrupted by user", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"FATAL: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
