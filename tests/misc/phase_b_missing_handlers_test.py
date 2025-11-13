#!/usr/bin/env python3
"""
Phase B: Missing Handlers Test Script
Tests download and delete handlers implemented via MCP storage adapter.

Date: 2025-10-22
Purpose: Validate missing handlers for Phase B Step 2
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment from .env.docker
env_docker_path = project_root / ".env.docker"
if env_docker_path.exists():
    load_dotenv(env_docker_path)
    print(f"✅ Loaded environment from {env_docker_path}")
else:
    print(f"⚠️  Warning: {env_docker_path} not found")

from src.file_management.mcp_storage_adapter import MCPStorageAdapter
from src.storage.supabase_client import SupabaseStorageManager


async def test_download_handler():
    """Test download handler via MCP"""
    print("=" * 80)
    print("TEST 1: DOWNLOAD HANDLER (MCP)")
    print("=" * 80)
    print()

    # Test file
    file_id = "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb"
    storage_path = "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/rollout_manager.py"
    destination = project_root / "temp" / "test_download.py"
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"1️⃣  Downloading file {file_id} via MCP adapter...")
    print(f"   Destination: {destination}")

    mcp_adapter = MCPStorageAdapter()
    result = mcp_adapter.download_file(file_id=file_id, storage_path=storage_path)

    if result.success:
        print(f"✅ Download successful: {len(result.data)} bytes")

        # Save to file
        with open(destination, 'wb') as f:
            f.write(result.data)

        # Verify file exists
        if destination.exists():
            file_size = destination.stat().st_size
            print(f"✅ File saved: {file_size} bytes")

            # Cleanup
            destination.unlink()
            print(f"🧹 Cleaned up test file")
        else:
            print(f"❌ File not found at destination")
            return False
    else:
        print(f"❌ Download failed: {result.error}")
        return False

    print()
    return True


async def test_download_without_destination():
    """Test download handler without saving to file"""
    print("=" * 80)
    print("TEST 2: DOWNLOAD WITHOUT DESTINATION")
    print("=" * 80)
    print()

    file_id = "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb"
    storage_path = "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/rollout_manager.py"

    print(f"1️⃣  Downloading file {file_id} (in-memory)...")

    mcp_adapter = MCPStorageAdapter()
    result = mcp_adapter.download_file(file_id=file_id, storage_path=storage_path)

    if result.success:
        print(f"✅ Download successful: {len(result.data)} bytes (in-memory)")
        print(f"   Metadata: {result.metadata}")
    else:
        print(f"❌ Download failed: {result.error}")
        return False

    print()
    return True


async def test_download_invalid_file():
    """Test download handler with invalid file ID"""
    print("=" * 80)
    print("TEST 3: DOWNLOAD INVALID FILE (ERROR HANDLING)")
    print("=" * 80)
    print()

    file_id = "00000000-0000-0000-0000-000000000000"
    storage_path = "invalid/path"

    print(f"1️⃣  Attempting to download invalid file {file_id}...")

    mcp_adapter = MCPStorageAdapter()
    result = mcp_adapter.download_file(file_id=file_id, storage_path=storage_path)

    if not result.success:
        print(f"✅ Error handled correctly: {result.error}")
    else:
        print(f"❌ Should have failed but succeeded")
        return False

    print()
    return True


async def test_delete_handler():
    """Test delete handler via MCP"""
    print("=" * 80)
    print("TEST 4: DELETE HANDLER (MCP)")
    print("=" * 80)
    print()

    # Note: We won't actually delete the test files
    # Instead, we'll test with a non-existent file to verify error handling

    file_id = "00000000-0000-0000-0000-000000000000"
    storage_path = "invalid/path"

    print(f"1️⃣  Attempting to delete non-existent file {file_id}...")

    mcp_adapter = MCPStorageAdapter()
    result = mcp_adapter.delete_file(file_id=file_id, storage_path=storage_path)

    if not result.success:
        print(f"✅ Error handled correctly: {result.error}")
    else:
        print(f"❌ Should have failed but succeeded")
        return False

    print()
    return True


async def main():
    """Run all missing handlers tests"""
    print()
    print("=" * 80)
    print("PHASE B: MISSING HANDLERS TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Download Handler", test_download_handler),
        ("Download Without Destination", test_download_without_destination),
        ("Download Invalid File", test_download_invalid_file),
        ("Delete Handler", test_delete_handler),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = await test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print()
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All tests passed! Missing handlers implemented successfully.")
        print()
        print("📊 Next Steps:")
        print("  1. Test database branching POC")
        print("  2. Document findings")
        print("  3. Get EXAI validation for Phase B")
        return 0
    else:
        print("⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

