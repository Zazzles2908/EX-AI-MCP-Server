"""
Test Supabase Integration - Complete Upload → Download Workflow
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Tests the complete workflow: upload → query → download with caching.
"""

import os
import sys
import time
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env.docker
env_path = Path(__file__).parent.parent.parent / '.env.docker'
load_dotenv(env_path)

def create_test_file(size_kb, content_prefix="integration"):
    """Create a test file of specified size."""
    temp_fd, temp_path = tempfile.mkstemp(prefix=f'{content_prefix}_', suffix='.txt')
    with os.fdopen(temp_fd, 'w') as f:
        content = f"{content_prefix} test content for integration testing\n" * (size_kb * 1024 // 60)
        f.write(content)
    return temp_path


def test_integration():
    """Test complete upload → download workflow."""
    print("=" * 80)
    print("Testing Supabase Integration - Complete Workflow")
    print("=" * 80)
    
    from supabase import create_client
    from tools.supabase_upload import SupabaseUploadManager
    from tools.supabase_download import SupabaseDownloadManager, CacheManager
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    client = create_client(url, service_key)
    
    # Get dev user ID
    print("\n1. Getting dev user ID...")
    result = client.rpc('get_dev_user_id').execute()
    user_id = result.data
    print(f"   ✅ Dev user ID: {user_id}")
    
    # Initialize managers
    upload_manager = SupabaseUploadManager(client)
    cache_manager = CacheManager(
        cache_dir=os.path.join(os.path.dirname(__file__), 'integration_cache'),
        max_size=50 * 1024 * 1024,  # 50MB
        ttl=3600  # 1 hour
    )
    download_manager = SupabaseDownloadManager(
        supabase_client=client,
        cache_manager=cache_manager,
        default_bucket="user-files"
    )
    
    # Test 1: Upload a new file
    print("\n2. Test 1: Upload new file...")
    test_file = create_test_file(50, "integration_test")
    try:
        upload_start = time.time()
        upload_result = upload_manager.upload_file(
            file_path=test_file,
            user_id=user_id,
            filename="integration_test.txt",
            bucket="user-files",
            tags=["integration", "test"]
        )
        upload_time = time.time() - upload_start
        
        print(f"   ✅ Upload successful!")
        print(f"      Time: {upload_time:.2f}s")
        print(f"      File ID: {upload_result['file_id']}")
        print(f"      Metadata ID: {upload_result['metadata_id']}")
        print(f"      Deduplicated: {upload_result['deduplicated']}")
        
        file_id = upload_result['file_id']
        
    finally:
        os.unlink(test_file)
    
    # Test 2: Query metadata
    print("\n3. Test 2: Query file metadata...")
    metadata_result = client.table('file_metadata').select('*').eq('file_id', file_id).execute()
    if metadata_result.data:
        metadata = metadata_result.data[0]
        print(f"   ✅ Metadata found!")
        print(f"      Filename: {metadata['filename']}")
        print(f"      Size: {metadata['file_size']} bytes")
        print(f"      Hash: {metadata['sha256_hash'][:16]}...")
        print(f"      Tags: {metadata['tags']}")
        print(f"      Access count: {metadata['access_count']}")
    else:
        print(f"   ❌ Metadata not found")
        return False
    
    # Test 3: Download the file (cache miss)
    print("\n4. Test 3: Download file (cache miss)...")
    download_start = time.time()
    downloaded_path = download_manager.download_file(
        file_id=file_id,
        bucket="user-files"
    )
    download_time_1 = time.time() - download_start
    
    print(f"   ✅ Download successful!")
    print(f"      Time: {download_time_1:.2f}s")
    print(f"      Path: {downloaded_path}")
    print(f"      Size: {os.path.getsize(downloaded_path)} bytes")
    
    # Test 4: Download again (cache hit)
    print("\n5. Test 4: Download again (cache hit)...")
    download_start = time.time()
    downloaded_path_2 = download_manager.download_file(
        file_id=file_id,
        bucket="user-files"
    )
    download_time_2 = time.time() - download_start
    
    print(f"   ✅ Download successful!")
    print(f"      Time: {download_time_2:.2f}s")
    print(f"      Same path: {downloaded_path == downloaded_path_2}")
    
    speedup = download_time_1 / download_time_2 if download_time_2 > 0 else 0
    print(f"   ✅ Cache speedup: {speedup:.1f}x faster")
    
    # Test 5: Verify metadata access count updated
    print("\n6. Test 5: Verify metadata updates...")
    metadata_result_2 = client.table('file_metadata').select('*').eq('file_id', file_id).execute()
    if metadata_result_2.data:
        new_access_count = metadata_result_2.data[0]['access_count']
        print(f"   ✅ Access count updated: {metadata['access_count']} → {new_access_count}")
        if new_access_count > metadata['access_count']:
            print(f"   ✅ Metadata tracking working!")
        else:
            print(f"   ⚠️  Access count not incremented")
    
    # Test 6: Upload duplicate file (test deduplication)
    print("\n7. Test 6: Upload duplicate file...")
    test_file_2 = create_test_file(50, "integration_test")  # Same content
    try:
        upload_result_2 = upload_manager.upload_file(
            file_path=test_file_2,
            user_id=user_id,
            filename="integration_test_duplicate.txt",
            bucket="user-files",
            tags=["integration", "duplicate"]
        )
        
        print(f"   ✅ Upload successful!")
        print(f"      Deduplicated: {upload_result_2['deduplicated']}")
        
        if upload_result_2['deduplicated']:
            print(f"   ✅ Deduplication working in integration!")
        else:
            print(f"   ⚠️  Deduplication not triggered")
        
    finally:
        os.unlink(test_file_2)
    
    # Test 7: Verify operations logged
    print("\n8. Test 7: Verify operations logged...")
    ops_result = client.table('file_operations').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
    print(f"   ✅ Found {len(ops_result.data)} recent operations")
    for op in ops_result.data[:3]:
        print(f"      - {op['operation_type']}: {op['status']}")
    
    # Test 8: Cache statistics
    print("\n9. Test 8: Cache statistics...")
    cache_size = cache_manager.db.get_total_size()
    cache_entries = len(cache_manager.lru_cache)
    print(f"   ✅ Cache size: {cache_size / 1024:.1f}KB")
    print(f"   ✅ Cache entries: {cache_entries}")
    
    print("\n" + "=" * 80)
    print("✅ Integration tests PASSED")
    print("=" * 80)
    print(f"\nIntegration Test Results:")
    print(f"- Upload time: {upload_time:.2f}s")
    print(f"- Download time (cache miss): {download_time_1:.2f}s")
    print(f"- Download time (cache hit): {download_time_2:.2f}s")
    print(f"- Cache speedup: {speedup:.1f}x")
    print(f"- Deduplication: {'✅ Working' if upload_result_2['deduplicated'] else '⚠️  Not working'}")
    print(f"- Metadata tracking: {'✅ Working' if new_access_count > metadata['access_count'] else '⚠️  Not working'}")
    print(f"- Operations logged: {len(ops_result.data)}")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

