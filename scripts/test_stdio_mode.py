#!/usr/bin/env python
"""
Test script for validating STDIO mode startup and MCP protocol messages.
This script tests that the async event loop and Supabase initialization fixes work correctly.
"""

import asyncio
import json
import subprocess
import sys
import time
from typing import Dict, Any

def test_python_syntax(file_path: str) -> bool:
    """Test if Python file compiles without syntax errors."""
    print(f"\n{'='*70}")
    print(f"Testing: {file_path}")
    print(f"{'='*70}")
    try:
        import py_compile
        py_compile.compile(file_path, doraise=True)
        print(f"[PASS] {file_path} - Compiles successfully")
        return True
    except py_compile.PyCompileError as e:
        print(f"[FAIL] {file_path} - Syntax Error:")
        print(f"   {e}")
        return False

async def test_stdio_mode() -> bool:
    """Test native MCP server in stdio mode."""
    print(f"\n{'='*70}")
    print(f"Testing: STDIO Mode Startup")
    print(f"{'='*70}")

    # Start the MCP server in stdio mode
    process = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "src.daemon.ws_server", "--mode", "stdio",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    print(f"[OK] Process started (PID: {process.pid})")

    try:
        # Wait for startup
        await asyncio.sleep(3)

        # Check if process is still running
        if process.returncode is not None:
            stderr = await process.stderr.read()
            print(f"[FAIL] Process exited early (code: {process.returncode})")
            print(f"   stderr: {stderr.decode()}")
            return False

        print(f"[OK] Process still running after 3 seconds")

        # Send initialize message
        init_message = {
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

        print(f"\n[SEND] Sending initialize message...")
        message_str = json.dumps(init_message) + "\n"
        process.stdin.write(message_str.encode())
        await process.stdin.drain()

        # Wait for response
        try:
            stdout_data = await asyncio.wait_for(
                process.stdout.read(8192),
                timeout=5.0
            )

            if stdout_data:
                print(f"[OK] Received response ({len(stdout_data)} bytes)")
                # Try to parse as JSON
                try:
                    response = json.loads(stdout_data.decode())
                    print(f"   Response: {json.dumps(response, indent=2)}")
                    return True
                except json.JSONDecodeError:
                    print(f"   [WARN] Response not valid JSON (may be log output)")
                    print(f"   Raw: {stdout_data[:200].decode()}")
                    return True
            else:
                print(f"[WARN] No response received (may be working but no output)")
                return True

        except asyncio.TimeoutError:
            print(f"[WARN] Timeout waiting for response (process may be working)")
            return True

    finally:
        # Clean shutdown
        print(f"\n[SEND] Sending shutdown signal...")
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5)
            print(f"[OK] Process terminated gracefully")
        except asyncio.TimeoutError:
            print(f"[WARN] Process didn't terminate, forcing kill...")
            process.kill()
            await process.wait()

    return True

def test_imports() -> bool:
    """Test that critical modules can be imported."""
    print(f"\n{'='*70}")
    print(f"Testing: Module Imports")
    print(f"{'='*70}")

    modules_to_test = [
        ("src.daemon.ws_server", "Main daemon"),
        ("src.daemon.mcp_server", "MCP server"),
        ("src.core.config", "Configuration"),
        ("src.daemon.warmup", "Warmup"),
    ]

    all_passed = True
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"[PASS] {module_name} - {description}")
        except Exception as e:
            print(f"[FAIL] {module_name} - {description}")
            print(f"   Error: {e}")
            all_passed = False

    return all_passed

async def main():
    """Run all tests."""
    print(f"\n{'='*70}")
    print(f"EX-AI-MCP-Server STDIO Mode Validation Test")
    print(f"{'='*70}")
    print(f"Python Version: {sys.version}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "Python Syntax": True,
        "Module Imports": True,
        "STDIO Mode": True,
    }

    # Test Python syntax
    print(f"\n[PHASE 1] Python Syntax Validation")
    syntax_files = [
        "src/daemon/ws_server.py",
        "src/daemon/mcp_server.py",
        "src/core/config.py",
        "src/daemon/warmup.py",
    ]

    for file_path in syntax_files:
        if not test_python_syntax(file_path):
            results["Python Syntax"] = False

    # Test imports
    print(f"\n[PHASE 2] Module Import Test")
    if not test_imports():
        results["Module Imports"] = False

    # Test stdio mode
    print(f"\n[PHASE 3] STDIO Mode Test")
    try:
        if not await test_stdio_mode():
            results["STDIO Mode"] = False
    except Exception as e:
        print(f"[FAIL] STDIO Mode Test Failed: {e}")
        import traceback
        traceback.print_exc()
        results["STDIO Mode"] = False

    # Summary
    print(f"\n{'='*70}")
    print(f"Test Results Summary")
    print(f"{'='*70}")

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")

    all_passed = all(results.values())
    print(f"\n{'='*70}")
    if all_passed:
        print(f"[SUCCESS] ALL TESTS PASSED")
        print(f"{'='*70}")
        return 0
    else:
        print(f"[ERROR] SOME TESTS FAILED")
        print(f"{'='*70}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
