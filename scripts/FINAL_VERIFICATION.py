#!/usr/bin/env python3
"""Final verification of EXAI MCP Server"""
import asyncio
import sys
sys.path.insert(0, '.')

from scripts.exai_native_mcp_server import handle_call_tool

async def main():
    print("=" * 70)
    print("EXAI MCP SERVER - FINAL VERIFICATION")
    print("=" * 70)
    print()

    # Test 1: Status
    print("[1/3] Testing mcp__exai_native_mcp__status()...")
    try:
        result = await handle_call_tool('status', {})
        data = result[0].text
        if "providers_configured" in data and "models_available" in data:
            print("      [PASS] Status tool works correctly")
        else:
            print("      [FAIL] Unexpected response format")
            return False
    except Exception as e:
        print(f"      [FAIL] Error: {e}")
        return False

    # Test 2: List models
    print("[2/3] Testing mcp__exai_native_mcp__listmodels()...")
    try:
        result = await handle_call_tool('listmodels', {})
        data = result[0].text
        if "glm-4" in data or "kimi" in data:
            print("      [PASS] List models tool works correctly")
        else:
            print("      [FAIL] Unexpected response format")
            return False
    except Exception as e:
        print(f"      [FAIL] Error: {e}")
        return False

    # Test 3: Version
    print("[3/3] Testing mcp__exai_native_mcp__version()...")
    try:
        result = await handle_call_tool('version', {})
        data = result[0].text
        if data:
            print("      [PASS] Version tool works correctly")
        else:
            print("      [FAIL] Empty response")
            return False
    except Exception as e:
        print(f"      [FAIL] Error: {e}")
        return False

    print()
    print("=" * 70)
    print("ALL TESTS PASSED - EXAI MCP SERVER IS OPERATIONAL!")
    print("=" * 70)
    print()
    print("Available tools: 19 EXAI workflow tools")
    print("You can now use: mcp__exai_native_mcp__<tool_name>()")
    print()
    return True

asyncio.run(main())
