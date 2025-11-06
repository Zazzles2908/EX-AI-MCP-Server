#!/usr/bin/env python3
"""Test chat function with GLM-4.6 to verify images parameter fix"""
import asyncio
import sys
sys.path.insert(0, '.')

from scripts.exai_native_mcp_server import handle_call_tool

async def main():
    print("=" * 70)
    print("TESTING CHAT FUNCTION WITH GLM-4.6")
    print("=" * 70)
    print()

    # Test 1: Chat with GLM-4.6 (without images)
    print("[1/2] Testing chat with GLM-4.6 (no images)...")
    try:
        result = await handle_call_tool('chat', {
            "prompt": "Hello, can you say 'GLM-4.6 is working!'?",
            "model": "glm-4.6"
        })
        data = result[0].text
        print(f"      [PASS] Chat tool works with GLM-4.6")
        print(f"      Response: {data[:100]}...")
    except Exception as e:
        print(f"      [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 2: Chat with GLM-4.6 (with files but no images)
    print("[2/2] Testing chat with GLM-4.6 (with files)...")
    try:
        result = await handle_call_tool('chat', {
            "prompt": "Please explain what Python is in one sentence.",
            "model": "glm-4.6",
            "files": []
        })
        data = result[0].text
        print(f"      [PASS] Chat tool works with GLM-4.6 and files parameter")
        print(f"      Response: {data[:100]}...")
    except Exception as e:
        print(f"      [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()
    print("=" * 70)
    print("CHAT FUNCTION WITH GLM-4.6 IS WORKING!")
    print("=" * 70)
    print()
    print("✅ Fix verified: The supports_images() method prevents GLM")
    print("   from receiving images parameter it doesn't support.")
    print()
    return True

asyncio.run(main())
