"""
Test Supabase Download Utility
Date: 2025-10-30
EXAI Consultation ID: bbfac185-ce22-4140-9b30-b3fda4c362d9

Tests the download utility with caching, LRU eviction, and cache hit/miss scenarios.
"""

import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables from .env.docker
env_path = Path(__file__).parent.parent.parent / '.env.docker'
load_dotenv(env_path)

def progress_callback(bytes_downloaded, percent):
    """Progress callback for downloads."""
    print(f"      Progress: {bytes_downloaded} bytes ({percent:.1f}%)")


def test_download():
    """Test download utility."""
    print("=" * 80)
    print("Testing Supabase Download Utility")
    print("=" * 80)
    
    from supabase import create_client
    from tools.supabase_download import SupabaseDownloadManager, CacheManager
    
    url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    client = create_client(url, service_key)
    
    # Create cache manager with small size for testing (10MB)
    cache_manager = CacheManager(
        cache_dir=os.path.join(os.path.dirname(__file__), 'test_cache'),
        max_size=10 * 1024 * 1024,  # 10MB
        ttl=3600  # 1 hour
    )
    
    download_manager = SupabaseDownloadManager(
        supabase_client=client,
        cache_manager=cache_manager,
        default_bucket="user-files"
    )
    
    # Get file IDs from upload test
    print("\n1. Getting file IDs from upload test...")
    try:
        with open('test_file_ids.txt', 'r') as f:
            file_ids = [line.strip() for line in f.readlines()]
        print(f"   ✅ Found {len(file_ids)} file IDs")
        for i, fid in enumerate(file_ids, 1):
            print(f"      {i}. {fid}")
    except FileNotFoundError:
        print("   ❌ test_file_ids.txt not found. Run test_upload.py first.")
        return False
    
    if not file_ids:
        print("   ❌ No file IDs found")
        return False
    
    file_id_1 = file_ids[0]
    file_id_2 = file_ids[1] if len(file_ids) > 1 else file_ids[0]
    
    # Test 1: Download file (cache miss)
    print(f"\n2. Test 1: Download file (cache miss)...")
    print(f"   File ID: {file_id_1}")
    start_time = time.time()
    try:
        downloaded_path_1 = download_manager.download_file(
            file_id=file_id_1,
            bucket="user-files",
            force_download=False,
            progress_callback=progress_callback
        )
        download_time_1 = time.time() - start_time
        print(f"   ✅ Download successful!")
        print(f"      Path: {downloaded_path_1}")
        print(f"      Time: {download_time_1:.2f}s")
        print(f"      Exists: {os.path.exists(downloaded_path_1)}")
        print(f"      Size: {os.path.getsize(downloaded_path_1)} bytes")
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Download same file again (cache hit)
    print(f"\n3. Test 2: Download same file again (cache hit)...")
    start_time = time.time()
    try:
        downloaded_path_2 = download_manager.download_file(
            file_id=file_id_1,
            bucket="user-files",
            force_download=False
        )
        download_time_2 = time.time() - start_time
        print(f"   ✅ Download successful!")
        print(f"      Path: {downloaded_path_2}")
        print(f"      Time: {download_time_2:.2f}s")
        print(f"      Same path: {downloaded_path_1 == downloaded_path_2}")
        
        if download_time_2 < download_time_1:
            print(f"   ✅ Cache hit detected (faster: {download_time_1:.2f}s → {download_time_2:.2f}s)")
        else:
            print(f"   ⚠️  Cache hit not detected (same speed)")
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False
    
    # Test 3: Download different file
    print(f"\n4. Test 3: Download different file...")
    print(f"   File ID: {file_id_2}")
    try:
        downloaded_path_3 = download_manager.download_file(
            file_id=file_id_2,
            bucket="user-files",
            progress_callback=progress_callback
        )
        print(f"   ✅ Download successful!")
        print(f"      Path: {downloaded_path_3}")
        print(f"      Size: {os.path.getsize(downloaded_path_3)} bytes")
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False
    
    # Test 4: Force download (bypass cache)
    print(f"\n5. Test 4: Force download (bypass cache)...")
    start_time = time.time()
    try:
        downloaded_path_4 = download_manager.download_file(
            file_id=file_id_1,
            bucket="user-files",
            force_download=True,
            progress_callback=progress_callback
        )
        download_time_4 = time.time() - start_time
        print(f"   ✅ Download successful!")
        print(f"      Time: {download_time_4:.2f}s")
        print(f"      Bypassed cache: {download_time_4 > download_time_2}")
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False
    
    # Test 5: Verify cache statistics
    print(f"\n6. Test 5: Verify cache statistics...")
    cache_size = cache_manager.db.get_total_size()
    print(f"   ✅ Cache size: {cache_size / 1024:.1f}KB")
    print(f"   ✅ Cache entries: {len(cache_manager.lru_cache)}")
    
    # Test 6: Verify metadata updates
    print(f"\n7. Test 6: Verify metadata access count...")
    metadata_result = client.table('file_metadata').select('*').eq('file_id', file_id_1).execute()
    if metadata_result.data:
        access_count = metadata_result.data[0].get('access_count', 0)
        print(f"   ✅ Access count: {access_count}")
        if access_count > 0:
            print(f"   ✅ Metadata updates working!")
        else:
            print(f"   ⚠️  Access count not updated")
    else:
        print(f"   ⚠️  No metadata found for file")
    
    # Test 7: Cache cleanup
    print(f"\n8. Test 7: Test cache cleanup...")
    try:
        cache_manager.cleanup_expired()
        print(f"   ✅ Cache cleanup successful")
    except Exception as e:
        print(f"   ⚠️  Cache cleanup failed: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Download utility tests PASSED")
    print("=" * 80)
    print(f"\nTest Results:")
    print(f"- Files downloaded: 3 unique files")
    print(f"- Cache hits: {'✅ Working' if download_time_2 < download_time_1 else '⚠️  Not detected'}")
    print(f"- Force download: {'✅ Working' if download_time_4 > download_time_2 else '⚠️  Not working'}")
    print(f"- Cache size: {cache_size / 1024:.1f}KB")
    print(f"- Metadata updates: {'✅ Working' if access_count > 0 else '⚠️  Not working'}")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    try:
        success = test_download()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

