#!/usr/bin/env python3
"""
Backfill Verification Script

Verifies that the SHA256 backfill completed successfully by checking:
1. All files have SHA256 hashes
2. No duplicate hash conflicts
3. Database consistency

Reference: EXAI consultation (Continuation: 9222d725-b6cd-44f1-8406-274e5a3b3389)

Usage:
    python scripts/verify_backfill.py
"""

import os
import sys
from pathlib import Path
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseStorageManager


def verify_backfill():
    """Verify backfill completion and database consistency"""
    print("=" * 60)
    print("BACKFILL VERIFICATION")
    print("=" * 60)
    
    # Initialize storage
    print("\n1. Connecting to Supabase...")
    storage = SupabaseStorageManager()
    
    if not storage.enabled:
        print("❌ ERROR: Supabase not configured!")
        return False
    
    print("✅ Connected to Supabase")
    
    # Get all files
    print("\n2. Fetching all files from database...")
    client = storage.get_client()
    result = client.table("files").select("id, sha256, original_name, size").execute()
    files = result.data if result.data else []
    
    total_files = len(files)
    print(f"✅ Found {total_files} total files")
    
    # Check for files with SHA256
    print("\n3. Checking SHA256 coverage...")
    files_with_hash = [f for f in files if f.get("sha256")]
    files_without_hash = [f for f in files if not f.get("sha256")]
    
    print(f"   Files with SHA256:    {len(files_with_hash)}")
    print(f"   Files without SHA256: {len(files_without_hash)}")
    
    if files_without_hash:
        print("\n⚠️  Files missing SHA256:")
        for f in files_without_hash[:10]:  # Show first 10
            print(f"   - {f.get('original_name', 'Unknown')} (ID: {f.get('id')})")
        if len(files_without_hash) > 10:
            print(f"   ... and {len(files_without_hash) - 10} more")
    else:
        print("✅ All files have SHA256 hashes")
    
    # Check for duplicate hashes
    print("\n4. Checking for duplicate hashes...")
    hash_counts = Counter(f.get("sha256") for f in files_with_hash if f.get("sha256"))
    duplicates = {h: c for h, c in hash_counts.items() if c > 1}
    
    if duplicates:
        print(f"⚠️  Found {len(duplicates)} duplicate hashes:")
        for hash_val, count in list(duplicates.items())[:5]:  # Show first 5
            print(f"   - {hash_val[:16]}... appears {count} times")
            # Find files with this hash
            dup_files = [f for f in files_with_hash if f.get("sha256") == hash_val]
            for df in dup_files[:3]:  # Show first 3 files
                print(f"     • {df.get('original_name', 'Unknown')} ({df.get('size', 0)} bytes)")
        if len(duplicates) > 5:
            print(f"   ... and {len(duplicates) - 5} more duplicate hashes")
        print("\n   Note: Duplicates are expected for identical file content")
    else:
        print("✅ No duplicate hashes found")
    
    # Database consistency checks
    print("\n5. Database consistency checks...")
    
    # Check for null values in critical fields
    null_checks = {
        "original_name": sum(1 for f in files if not f.get("original_name")),
        "size": sum(1 for f in files if f.get("size") is None),
    }
    
    consistency_ok = True
    for field, count in null_checks.items():
        if count > 0:
            print(f"⚠️  {count} files have null {field}")
            consistency_ok = False
        else:
            print(f"✅ All files have {field}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total files:          {total_files}")
    print(f"Files with SHA256:    {len(files_with_hash)}")
    print(f"Files without SHA256: {len(files_without_hash)}")
    print(f"Duplicate hashes:     {len(duplicates)}")
    print(f"Consistency:          {'✅ PASS' if consistency_ok else '⚠️  ISSUES FOUND'}")
    print("=" * 60)
    
    # Determine overall success
    success = len(files_without_hash) == 0 and consistency_ok
    
    if success:
        print("\n🎉 VERIFICATION PASSED - Backfill completed successfully!")
        print("\nNext steps:")
        print("1. Review any duplicate hashes (expected for identical content)")
        print("2. Proceed with shadow mode enablement")
        print("3. Monitor shadow mode logs for 24-48 hours")
    else:
        print("\n❌ VERIFICATION FAILED - Issues found")
        print("\nRecommended actions:")
        if files_without_hash:
            print("1. Re-run backfill script for missing files")
        if not consistency_ok:
            print("2. Investigate database consistency issues")
    
    return success


if __name__ == "__main__":
    try:
        success = verify_backfill()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

