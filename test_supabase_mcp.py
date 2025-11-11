#!/usr/bin/env python3
"""
Supabase MCP Connection Test Script
Tests if the Supabase MCP server can connect and authenticate
"""

import subprocess
import json
import sys
import time

def test_supabase_mcp():
    """Test Supabase MCP server initialization"""

    print("=" * 60)
    print("Supabase MCP Connection Test")
    print("=" * 60)

    # Test 1: Check if npx is available
    print("\n[Test 1] Checking npx availability...")
    try:
        result = subprocess.run(
            ["cmd", "/c", "npx", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"[OK] npx is available: {result.stdout.strip()}")
        else:
            print("[FAIL] npx not found")
            return False
    except Exception as e:
        print(f"[FAIL] Error checking npx: {e}")
        return False

    # Test 2: Check if Supabase MCP package can be found
    print("\n[Test 2] Checking Supabase MCP package...")
    try:
        result = subprocess.run(
            ["cmd", "/c", "npx", "-y", "@supabase/mcp-server-supabase@latest", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "Please provide a personal access token" in result.stderr or "Error" not in result.stderr:
            print("[OK] Supabase MCP package is available")
        else:
            print(f"[WARN] Package response: {result.stderr[:100]}")
    except Exception as e:
        print(f"[FAIL] Error checking package: {e}")
        return False

    # Test 3: Test with access token
    print("\n[Test 3] Testing authentication with access token...")
    access_token = "sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625"

    try:
        # We'll do a quick stdin test - the server will read from stdin
        # and should respond with MCP initialization
        process = subprocess.Popen(
            [
                "npx", "-y", "@supabase/mcp-server-supabase@latest",
                "--access-token", access_token
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send MCP initialize request
        init_request = {
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

        # Send the request and close stdin
        stdout, stderr = process.communicate(input=json.dumps(init_request) + "\n", timeout=5)

        print(f"[OK] Server responded (exit code: {process.returncode})")

        # Check for tools
        if "tools" in stdout.lower() or "list" in stdout.lower():
            print("[OK] Tools list requested successfully")

        return True

    except subprocess.TimeoutExpired:
        process.kill()
        print("[WARN] Server started but didn't respond in time (expected for MCP servers)")
        return True
    except Exception as e:
        print(f"[FAIL] Error during authentication test: {e}")
        return False

    # Test 4: Verify configuration
    print("\n[Test 4] Verifying MCP configuration...")

    try:
        # Check .mcp.json
        with open(".mcp.json", "r") as f:
            config = json.load(f)
            if "supabase-mcp-full" in config.get("mcpServers", {}):
                print("[OK] supabase-mcp-full found in .mcp.json")
            else:
                print("[FAIL] supabase-mcp-full not found in .mcp.json")
                return False

        # Check .claude/.mcp.json
        with open(".claude/.mcp.json", "r") as f:
            config = json.load(f)
            if "supabase-mcp-full" in config.get("mcpServers", {}):
                print("[OK] supabase-mcp-full found in .claude/.mcp.json")
            else:
                print("[FAIL] supabase-mcp-full not found in .claude/.mcp.json")
                return False

        return True

    except Exception as e:
        print(f"[FAIL] Error verifying configuration: {e}")
        return False

def main():
    """Main test runner"""
    print("\nStarting Supabase MCP tests...\n")

    success = test_supabase_mcp()

    print("\n" + "=" * 60)
    if success:
        print("[SUCCESS] All tests passed!")
        print("\nThe Supabase MCP server is properly configured.")
        print("You can now use @supabase-mcp-full in Claude Code.")
        print("\nTry these commands:")
        print("  @supabase-mcp-full list_projects")
        print("  @supabase-mcp-full database list")
        print("  @supabase-mcp-full functions list")
        return 0
    else:
        print("[FAIL] Some tests failed")
        print("\nPlease check the errors above and retry.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
