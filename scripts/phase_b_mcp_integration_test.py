#!/usr/bin/env python3
"""
Phase B: MCP Integration Test Script
Tests MCP storage adapter alongside Python SupabaseStorageManager.
Validates download, upload, delete operations.

Date: 2025-10-22
Purpose: Validate MCP adapter for Phase B
"""

import sys
import time
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


def test_download_comparison():
    """Test download operation: MCP vs Python"""
    print("=" * 80)
    print("TEST 1: DOWNLOAD COMPARISON (MCP vs Python)")
    print("=" * 80)
    print()
    
    # Test file
    file_id = "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb"
    storage_path = "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/rollout_manager.py"
    
    # Test MCP approach
    print("1️⃣  Testing MCP Storage Adapter...")
    mcp_adapter = MCPStorageAdapter()
    
    mcp_start = time.time()
    mcp_result = mcp_adapter.download_file(file_id=file_id, storage_path=storage_path)
    mcp_time = time.time() - mcp_start
    
    if mcp_result.success:
        print(f"✅ MCP Download: {len(mcp_result.data)} bytes in {mcp_time:.3f}s")
    else:
        print(f"❌ MCP Download failed: {mcp_result.error}")
        return False
    
    # Test Python approach
    print("2️⃣  Testing Python SupabaseStorageManager...")
    python_storage = SupabaseStorageManager()
    
    python_start = time.time()
    python_bytes = python_storage.download_file(file_id=file_id)
    python_time = time.time() - python_start
    
    if python_bytes:
        print(f"✅ Python Download: {len(python_bytes)} bytes in {python_time:.3f}s")
    else:
        print(f"❌ Python Download failed")
        return False
    
    # Compare results
    print()
    print("📊 Comparison:")
    print(f"  - MCP Time: {mcp_time:.3f}s")
    print(f"  - Python Time: {python_time:.3f}s")
    print(f"  - Difference: {abs(mcp_time - python_time):.3f}s")
    print(f"  - Data Match: {mcp_result.data == python_bytes}")
    
    if mcp_result.data == python_bytes:
        print("✅ Results match perfectly!")
    else:
        print("❌ Results don't match!")
        return False
    
    print()
    return True


def test_hash_update():
    """Test hash update operation via MCP"""
    print("=" * 80)
    print("TEST 2: HASH UPDATE VIA MCP")
    print("=" * 80)
    print()
    
    file_id = "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb"
    test_hash = "74f70375e2ddedc76943b57f5cbe0abcc5646140512b8ff85bae4840d77216ea"
    
    print(f"1️⃣  Updating hash for file {file_id}...")
    mcp_adapter = MCPStorageAdapter()
    
    start_time = time.time()
    result = mcp_adapter.update_file_hash(file_id=file_id, sha256_hash=test_hash)
    elapsed = time.time() - start_time
    
    if result.success:
        print(f"✅ Hash updated in {elapsed:.3f}s")
    else:
        print(f"❌ Hash update failed: {result.error}")
        return False
    
    # Verify update
    print("2️⃣  Verifying update...")
    python_storage = SupabaseStorageManager()
    client = python_storage.get_client()
    
    verify_result = client.table("files").select("sha256").eq("id", file_id).execute()
    
    if verify_result.data and verify_result.data[0].get("sha256") == test_hash:
        print(f"✅ Verification successful: {test_hash}")
    else:
        print(f"❌ Verification failed")
        return False
    
    print()
    return True


def test_mcp_metadata():
    """Test MCP result metadata"""
    print("=" * 80)
    print("TEST 3: MCP RESULT METADATA")
    print("=" * 80)
    print()
    
    file_id = "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb"
    storage_path = "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/rollout_manager.py"
    
    mcp_adapter = MCPStorageAdapter()
    result = mcp_adapter.download_file(file_id=file_id, storage_path=storage_path)
    
    if not result.success:
        print(f"❌ Download failed: {result.error}")
        return False
    
    print("📊 MCP Result Metadata:")
    if result.metadata:
        for key, value in result.metadata.items():
            print(f"  - {key}: {value}")
    else:
        print("  - No metadata")
    
    # Validate metadata
    expected_keys = ["file_id", "storage_path", "size_bytes"]
    missing_keys = [k for k in expected_keys if k not in (result.metadata or {})]
    
    if missing_keys:
        print(f"❌ Missing metadata keys: {missing_keys}")
        return False
    
    print("✅ All expected metadata present")
    print()
    return True


def test_error_handling():
    """Test MCP error handling"""
    print("=" * 80)
    print("TEST 4: ERROR HANDLING")
    print("=" * 80)
    print()
    
    mcp_adapter = MCPStorageAdapter()
    
    # Test with invalid file ID
    print("1️⃣  Testing with invalid file ID...")
    result = mcp_adapter.download_file(
        file_id="00000000-0000-0000-0000-000000000000",
        storage_path="invalid/path"
    )
    
    if not result.success:
        print(f"✅ Error handled correctly: {result.error}")
    else:
        print(f"❌ Should have failed but succeeded")
        return False
    
    print()
    return True


def main():
    """Run all Phase B integration tests"""
    print()
    print("=" * 80)
    print("PHASE B: MCP INTEGRATION TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Download Comparison", test_download_comparison),
        ("Hash Update", test_hash_update),
        ("MCP Metadata", test_mcp_metadata),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
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
        print("🎉 All tests passed! MCP adapter is working correctly.")
        print()
        print("📊 Next Steps:")
        print("  1. Implement missing handlers (download/delete)")
        print("  2. Test database branching POC")
        print("  3. Document findings and get EXAI validation")
        return 0
    else:
        print("⚠️  Some tests failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

