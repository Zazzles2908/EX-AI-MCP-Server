#!/usr/bin/env python3
"""Test chat with unique prompt to bypass cache"""
import asyncio
import sys
import time
sys.path.insert(0, '.')

from scripts.exai_native_mcp_server import handle_call_tool

async def main():
    print("=" * 70)
    print("TESTING CHAT FUNCTION WITH UNIQUE PROMPT")
    print("=" * 70)
    print()

    # Use unique timestamp to bypass cache
    unique_id = str(int(time.time() * 1000000))

    print(f"Testing with unique prompt ID: {unique_id}")
    print()

    try:
        result = await handle_call_tool('chat', {
            "prompt": f"UNIQUE_TEST_{unique_id} - Please respond with just 'SUCCESS' if you can see this message.",
            "model": "glm-4.6",
            "use_websearch": False
        })

        data = result[0].text
        print(f"Raw response: {data}")
        print()

        # Parse the response
        import json
        try:
            parsed = json.loads(data)
            if parsed.get("status") == "success":
                print("=" * 70)
                print("SUCCESS! CHAT FUNCTION WORKS WITH GLM-4.6!")
                print("=" * 70)
                print()
                print("The images parameter fix is working correctly.")
                print(f"Response content: {parsed.get('content', '')[:200]}...")
                return True
            else:
                print(f"FAILED - Status: {parsed.get('status')}")
                print(f"Error: {parsed.get('content', '')[:200]}")
                return False
        except json.JSONDecodeError:
            print(f"FAILED - Invalid JSON response: {data[:200]}")
            return False

    except Exception as e:
        print(f"FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

asyncio.run(main())
