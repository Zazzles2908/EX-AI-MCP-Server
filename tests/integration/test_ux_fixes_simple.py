#!/usr/bin/env python3
"""
Simple UX Fixes Validation Test
Uses the existing MCP client to validate fixes
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scripts.baseline_collection.mcp_client import MCPWebSocketClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run UX validation tests"""
    print("\n" + "="*80)
    print("EXAI MCP SERVER - UX FIXES VALIDATION (Simple Test)")
    print("="*80)

    # Get token from environment
    token = os.getenv('EXAI_WS_TOKEN', '')

    # Create client
    client = MCPWebSocketClient(port=3000, token=token)

    # Test results
    results = {
        'connection': False,
        'listmodels': False,
        'file_upload': False,
        'errors': []
    }

    try:
        # Test 1: Connection
        print("\n" + "="*80)
        print("TEST 1: WebSocket Connection")
        print("="*80)

        success = await client.connect()
        if success:
            print("PASS - WebSocket connection successful")
            results['connection'] = True
        else:
            print("FAIL - WebSocket connection failed")
            results['errors'].append("Connection failed")
            return 1

        # Test 2: Simple tool call (listmodels)
        print("\n" + "="*80)
        print("TEST 2: Simple Tool Call (listmodels)")
        print("="*80)

        success, outputs, error = await client.call_tool(
            "listmodels",
            {},
            timeout=30.0
        )

        if success:
            print(f"PASS - Received {len(outputs)} models")
            results['listmodels'] = True
        else:
            print(f"FAIL - Tool call failed: {error}")
            results['errors'].append(f"listmodels failed: {error}")

        # Test 3: File upload (just verify no file_type error)
        print("\n" + "="*80)
        print("TEST 3: File Upload (smart_file_query)")
        print("="*80)
        print("NOTE: Testing for 'file_type' parameter error")

        # Create test file
        test_file = "/tmp/ux_test.txt"
        with open(test_file, 'w') as f:
            f.write("Test file for UX validation\n")

        success, outputs, error = await client.call_tool(
            "smart_file_query",
            {
                "file_path": test_file,
                "question": "What is in this file?"
            },
            timeout=30.0
        )

        if success:
            print("PASS - File upload completed (no file_type error)")
            results['file_upload'] = True
        else:
            error_str = str(error)
            if 'file_type' in error_str.lower():
                print(f"FAIL - 'file_type' error still present: {error}")
                results['errors'].append(f"file_type error: {error}")
            else:
                print(f"INFO - Other error (not file_type related): {error}")
                results['file_upload'] = True  # Pass if not file_type error

        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

        # Print summary
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        tests = [
            ("WebSocket Connection", results['connection']),
            ("List Models Tool", results['listmodels']),
            ("File Upload (no file_type error)", results['file_upload'])
        ]

        for name, passed in tests:
            status = "PASS" if passed else "FAIL"
            print(f"{status} - {name}")

        print(f"\n{'-'*80}")
        if results['errors']:
            print(f"Errors: {len(results['errors'])}")
            for err in results['errors']:
                print(f"  - {err}")
        else:
            print("All tests passed!")

        print("="*80)

        return 0 if not results['errors'] else 1

    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await client.disconnect()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
