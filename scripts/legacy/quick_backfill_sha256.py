#!/usr/bin/env python3
"""
Quick SHA256 Backfill Script

Simple script to calculate SHA256 hashes for existing files in Supabase.
Run this once from Docker container to backfill the 199 files.

Usage:
    python scripts/quick_backfill_sha256.py
"""

import os
import sys
import hashlib
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage.supabase_client import SupabaseStorageManager


def calculate_sha256(file_data: bytes) -> str:
    """Calculate SHA256 hash of file data"""
    return hashlib.sha256(file_data).hexdigest()


def main():
    print("=" * 60)
    print("QUICK SHA256 BACKFILL")
    print("=" * 60)
    
    # Initialize storage
    print("\n1. Initializing Supabase connection...")
    storage = SupabaseStorageManager()
    
    if not storage.enabled:
        print("❌ ERROR: Supabase not configured!")
        print("   Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set")
        return 1
    
    print("✅ Connected to Supabase")
    
    # Get files without SHA256
    print("\n2. Finding files without SHA256...")
    client = storage.get_client()
    result = client.table("files").select("*").is_("sha256", "null").execute()
    files = result.data if result.data else []
    
    print(f"✅ Found {len(files)} files to process")
    
    if len(files) == 0:
        print("\n🎉 All files already have SHA256 hashes!")
        return 0
    
    # Process each file
    print(f"\n3. Processing {len(files)} files...")
    print("-" * 60)
    
    success_count = 0
    error_count = 0
    
    for i, file_record in enumerate(files, 1):
        file_id = file_record["id"]
        storage_path = file_record["storage_path"]
        original_name = file_record["original_name"]
        
        print(f"\n[{i}/{len(files)}] {original_name}")
        print(f"   Path: {storage_path}")
        
        try:
            # Determine bucket from path
            if storage_path.startswith("contexts/"):
                bucket = "user-files"
                path = storage_path
            else:
                bucket = "user-files"
                path = storage_path
            
            # Download file
            print(f"   Downloading from bucket '{bucket}'...")
            file_data = client.storage.from_(bucket).download(path)

            # Calculate SHA256
            sha256 = calculate_sha256(file_data)
            print(f"   SHA256: {sha256}")

            # Update database
            try:
                client.table("files").update({
                    "sha256": sha256
                }).eq("id", file_id).execute()

                print(f"   ✅ Updated")
                success_count += 1
            except Exception as update_error:
                # Check if it's a duplicate hash error
                if "duplicate key value violates unique constraint" in str(update_error):
                    print(f"   ⚠️  Duplicate (same content already exists)")
                    success_count += 1  # Count as success - file has correct hash
                else:
                    raise  # Re-raise if it's a different error
            
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("BACKFILL COMPLETE")
    print("=" * 60)
    print(f"✅ Success: {success_count}")
    print(f"❌ Errors:  {error_count}")
    print(f"📊 Total:   {len(files)}")
    print("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

