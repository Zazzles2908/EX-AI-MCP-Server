#!/usr/bin/env python3
"""
Test Kimi File Tools Redesign - 2025-10-17
Tests the new single-purpose Kimi file management tools
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.providers.kimi.kimi_files import (
    KimiUploadFilesTool,
    KimiChatWithFilesTool,
    KimiManageFilesTool
)


async def main():
    """Test all Kimi file tools"""
    print("\n" + "="*70)
    print("KIMI FILE TOOLS REDESIGN - VALIDATION TEST")
    print("="*70)
    
    # Test 1: List files
    print("\n[TEST 1] Listing existing files...")
    manage_tool = KimiManageFilesTool()
    try:
        result = await manage_tool.execute({"operation": "list", "limit": 10})
        data = json.loads(result[0].text)
        print(f"✅ Found {data.get('count', 0)} files")
    except Exception as e:
        print(f"❌ List failed: {e}")
        return
    
    # Test 2: Cleanup (dry run)
    print("\n[TEST 2] Cleanup dry run...")
    try:
        result = await manage_tool.execute({"operation": "cleanup_all", "dry_run": True})
        data = json.loads(result[0].text)
        file_count = data.get('deleted_count', 0)
        print(f"✅ Would delete {file_count} files")
        
        if file_count > 0:
            print(f"\n[TEST 3] Executing cleanup...")
            result = await manage_tool.execute({"operation": "cleanup_all", "dry_run": False})
            data = json.loads(result[0].text)
            print(f"✅ Deleted {data.get('deleted_count', 0)} files")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n" + "="*70)
    print("TESTS COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

