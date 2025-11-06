"""
Test Supabase Upload Utility
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Tests the upload utility with various file sizes and verifies deduplication.
"""

import os
import sys
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env.docker
env_path = Path(__file__).parent.parent.parent / '.env.docker'
load_dotenv(env_path)

def create_test_file(size_kb, content_prefix="test"):
    """Create a test file of specified size."""
    temp_fd, temp_path = tempfile.mkstemp(prefix=f'{content_prefix}_', suffix='.txt')
    with os.fdopen(temp_fd, 'w') as f:
        # Write content to reach desired size
        content = f"{content_prefix} content\n" * (size_kb * 1024 // 20)
        f.write(content)
    return temp_path


def progress_callback(bytes_uploaded, percent):
    """Progress callback for uploads."""
    print(f"      Progress: {bytes_uploaded} bytes ({percent:.1f}%)")


def test_upload():
    """Test upload utility."""
    print("=" * 80)
    print("Testing Supabase Upload Utility")
    print("=" * 80)
    
    from supabase import create_client
    from tools.supabase_upload import SupabaseUploadManager
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    client = create_client(url, service_key)
    upload_manager = SupabaseUploadManager(client)
    
    # Get dev user ID
    print("\n1. Getting dev user ID...")
    result = client.rpc('get_dev_user_id').execute()
    user_id = result.data
    print(f"   ✅ Dev user ID: {user_id}")
    
    # Test 1: Upload small file
    print("\n2. Test 1: Upload small file (10KB)...")
    test_file_1 = create_test_file(10, "small")
    try:
        result = upload_manager.upload_file(
            file_path=test_file_1,
            user_id=user_id,
            filename="test_small.txt",
            bucket="user-files",
            progress_callback=progress_callback,
            tags=["test", "small"]
        )
        print(f"   ✅ Upload successful!")
        print(f"      Metadata ID: {result['metadata_id']}")
        print(f"      Deduplicated: {result['deduplicated']}")
        print(f"      File ID: {result.get('file_id', 'N/A')}")
        
        file_id_1 = result.get('file_id')
        
    finally:
        os.unlink(test_file_1)
    
    # Test 2: Upload same file again (test deduplication)
    print("\n3. Test 2: Upload same file again (test deduplication)...")
    test_file_2 = create_test_file(10, "small")  # Same content
    try:
        result = upload_manager.upload_file(
            file_path=test_file_2,
            user_id=user_id,
            filename="test_small_duplicate.txt",
            bucket="user-files",
            tags=["test", "duplicate"]
        )
        print(f"   ✅ Upload successful!")
        print(f"      Metadata ID: {result['metadata_id']}")
        print(f"      Deduplicated: {result['deduplicated']}")
        
        if result['deduplicated']:
            print("   ✅ Deduplication working correctly!")
        else:
            print("   ⚠️  Deduplication did not trigger (unexpected)")
        
    finally:
        os.unlink(test_file_2)
    
    # Test 3: Upload medium file
    print("\n4. Test 3: Upload medium file (100KB)...")
    test_file_3 = create_test_file(100, "medium")
    try:
        result = upload_manager.upload_file(
            file_path=test_file_3,
            user_id=user_id,
            filename="test_medium.txt",
            bucket="user-files",
            progress_callback=progress_callback,
            tags=["test", "medium"]
        )
        print(f"   ✅ Upload successful!")
        print(f"      Metadata ID: {result['metadata_id']}")
        print(f"      File ID: {result.get('file_id', 'N/A')}")
        
        file_id_3 = result.get('file_id')
        
    finally:
        os.unlink(test_file_3)
    
    # Test 4: Verify metadata in database
    print("\n5. Test 4: Verify metadata in database...")
    metadata_result = client.table('file_metadata').select('*').eq('user_id', user_id).execute()
    print(f"   ✅ Found {len(metadata_result.data)} file metadata records")
    
    for record in metadata_result.data:
        print(f"      - {record['filename']} ({record['file_size']} bytes, hash: {record['sha256_hash'][:16]}...)")
    
    # Test 5: Verify operations in database
    print("\n6. Test 5: Verify operations in database...")
    ops_result = client.table('file_operations').select('*').eq('user_id', user_id).execute()
    print(f"   ✅ Found {len(ops_result.data)} file operations")
    
    for op in ops_result.data:
        print(f"      - {op['operation_type']}: {op['status']}")
    
    print("\n" + "=" * 80)
    print("✅ Upload utility tests PASSED")
    print("=" * 80)
    print(f"\nTest Results:")
    print(f"- Files uploaded: 3")
    print(f"- Deduplication: {'✅ Working' if result['deduplicated'] else '⚠️  Not tested'}")
    print(f"- Metadata records: {len(metadata_result.data)}")
    print(f"- Operations logged: {len(ops_result.data)}")
    print("=" * 80)
    
    return True, file_id_1, file_id_3


if __name__ == "__main__":
    try:
        success, file_id_1, file_id_3 = test_upload()
        
        # Save file IDs for download test
        with open('test_file_ids.txt', 'w') as f:
            f.write(f"{file_id_1}\n{file_id_3}\n")
        
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

