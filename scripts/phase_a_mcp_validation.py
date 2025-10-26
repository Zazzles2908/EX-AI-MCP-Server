#!/usr/bin/env python3
"""
Phase A: MCP Storage Validation Script
Tests MCP storage tools for downloading files, calculating SHA256, and updating database.
Compares with Docker script approach.

Date: 2025-10-22
Purpose: Validate MCP approach before Phase B
"""

import hashlib
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment from .env.docker (Supabase credentials)
env_docker_path = project_root / ".env.docker"
if env_docker_path.exists():
    load_dotenv(env_docker_path)
    print(f"✅ Loaded environment from {env_docker_path}")
else:
    print(f"⚠️  Warning: {env_docker_path} not found")

from src.storage.supabase_client import SupabaseStorageManager


def calculate_sha256(file_path: str) -> str:
    """Calculate SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def test_mcp_approach():
    """
    Test MCP storage approach for file operations.
    
    This script uses Python SupabaseStorageManager to simulate what MCP storage tools would do.
    In Phase B, we'll replace this with actual MCP storage tool calls.
    """
    print("=" * 80)
    print("PHASE A: MCP STORAGE VALIDATION")
    print("=" * 80)
    print()
    
    # Files to process
    files_to_process = [
        {
            "id": "77911c5f-91a6-4aa7-b0e6-cbeaaf510ebb",
            "original_name": "rollout_manager.py",
            "storage_path": "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/rollout_manager.py",
            "size_bytes": 8097
        },
        {
            "id": "fe3b770a-b17a-4e19-91f4-b605cbabaac2",
            "original_name": "migration_facade.py",
            "storage_path": "contexts/9222d725-b6cd-44f1-8406-274e5a3b3389/migration_facade.py",
            "size_bytes": 10020
        }
    ]
    
    # Initialize storage manager
    print("Initializing SupabaseStorageManager...")
    storage = SupabaseStorageManager()
    print("✅ Storage manager initialized")
    print()
    
    # Create temp directory for downloads
    temp_dir = project_root / "temp" / "phase_a_validation"
    temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Temp directory: {temp_dir}")
    print()
    
    results = []
    
    for file_info in files_to_process:
        print("-" * 80)
        print(f"Processing: {file_info['original_name']}")
        print("-" * 80)
        
        start_time = time.time()
        
        try:
            # Step 1: Download file from storage
            print(f"1️⃣  Downloading from storage path: {file_info['storage_path']}")
            download_start = time.time()

            # Download file (this simulates MCP storage download)
            local_path = temp_dir / file_info['original_name']

            # Use storage manager to download
            # Note: In Phase B, this will be replaced with MCP storage tool call
            file_bytes = storage.download_file(file_id=file_info['id'])

            download_time = time.time() - download_start

            if file_bytes is None:
                print(f"❌ Download failed: No data returned")
                results.append({
                    "file": file_info['original_name'],
                    "success": False,
                    "error": "No data returned from download",
                    "download_time": download_time
                })
                continue

            # Save to local file
            with open(local_path, 'wb') as f:
                f.write(file_bytes)

            print(f"✅ Downloaded {len(file_bytes)} bytes in {download_time:.2f}s")
            
            # Step 2: Calculate SHA256 hash
            print(f"2️⃣  Calculating SHA256 hash...")
            hash_start = time.time()
            
            sha256_hash = calculate_sha256(str(local_path))
            
            hash_time = time.time() - hash_start
            print(f"✅ SHA256: {sha256_hash} (calculated in {hash_time:.2f}s)")
            
            # Step 3: Update database with SHA256
            print(f"3️⃣  Updating database...")
            update_start = time.time()

            # Update database (this simulates MCP SQL update)
            # Note: In Phase B, this will be replaced with MCP execute_sql tool call
            client = storage.get_client()
            update_result = client.table("files").update({
                "sha256": sha256_hash
            }).eq("id", file_info['id']).execute()

            update_time = time.time() - update_start
            print(f"✅ Database updated in {update_time:.2f}s")

            # Total time
            total_time = time.time() - start_time

            # Verify update
            print(f"4️⃣  Verifying update...")
            verify_result = client.table("files").select("sha256").eq("id", file_info['id']).execute()
            
            if verify_result.data and verify_result.data[0].get("sha256") == sha256_hash:
                print(f"✅ Verification successful")
            else:
                print(f"❌ Verification failed")
            
            print()
            print(f"⏱️  Total time: {total_time:.2f}s")
            print(f"   - Download: {download_time:.2f}s ({download_time/total_time*100:.1f}%)")
            print(f"   - Hash calculation: {hash_time:.2f}s ({hash_time/total_time*100:.1f}%)")
            print(f"   - Database update: {update_time:.2f}s ({update_time/total_time*100:.1f}%)")
            
            results.append({
                "file": file_info['original_name'],
                "success": True,
                "sha256": sha256_hash,
                "download_time": download_time,
                "hash_time": hash_time,
                "update_time": update_time,
                "total_time": total_time
            })
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                "file": file_info['original_name'],
                "success": False,
                "error": str(e),
                "total_time": time.time() - start_time
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()
    
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]
    
    print(f"✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print()
    
    if successful:
        avg_download = sum(r["download_time"] for r in successful) / len(successful)
        avg_hash = sum(r["hash_time"] for r in successful) / len(successful)
        avg_update = sum(r["update_time"] for r in successful) / len(successful)
        avg_total = sum(r["total_time"] for r in successful) / len(successful)
        
        print("Average Times:")
        print(f"  - Download: {avg_download:.2f}s")
        print(f"  - Hash calculation: {avg_hash:.2f}s")
        print(f"  - Database update: {avg_update:.2f}s")
        print(f"  - Total: {avg_total:.2f}s")
        print()
    
    if failed:
        print("Failed Files:")
        for r in failed:
            print(f"  - {r['file']}: {r.get('error', 'Unknown error')}")
        print()
    
    # Cleanup
    print("🧹 Cleaning up temp files...")
    for file_path in temp_dir.glob("*"):
        file_path.unlink()
    print("✅ Cleanup complete")
    print()
    
    print("=" * 80)
    print("PHASE A VALIDATION COMPLETE")
    print("=" * 80)
    print()
    print("📊 Next Steps:")
    print("  1. Review performance metrics above")
    print("  2. Compare with Docker script approach")
    print("  3. Document findings in validation report")
    print("  4. Consult with EXAI for Phase A completion")
    print()
    
    return results


if __name__ == "__main__":
    try:
        results = test_mcp_approach()
        
        # Exit with success if all files processed successfully
        if all(r.get("success") for r in results):
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

