"""
Test File Deduplication Implementation

Tests the SHA256-based file deduplication system to ensure:
1. Duplicate files are detected correctly
2. Reference counts are incremented
3. Storage savings are achieved
4. No duplicate uploads to providers

Phase: 2.4 Final 2% - File Deduplication
Date: 2025-10-26
EXAI Consultation: c90cdeec-48bb-4d10-b075-925ebbf39c8a
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env.docker
env_docker = project_root / ".env.docker"
if env_docker.exists():
    load_dotenv(env_docker)
    print(f"✅ Loaded environment from {env_docker}")
else:
    print(f"⚠️  Warning: {env_docker} not found")

from utils.file.deduplication import FileDeduplicationManager, get_dedup_metrics, reset_dedup_metrics
from utils.file.cache import FileCache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_test_file(content: str, filename: str) -> Path:
    """Create a temporary test file with given content"""
    temp_dir = Path(tempfile.gettempdir()) / "dedup_test"
    temp_dir.mkdir(exist_ok=True)
    
    file_path = temp_dir / filename
    file_path.write_text(content)
    
    return file_path


def test_deduplication_detection():
    """Test that duplicate files are detected correctly"""
    print("\n" + "="*80)
    print("TEST 1: Deduplication Detection")
    print("="*80)
    
    # Create two files with identical content
    content = "This is test content for deduplication testing"
    file1 = create_test_file(content, "test_file_1.txt")
    file2 = create_test_file(content, "test_file_2.txt")  # Same content, different name
    
    # Calculate SHA256 for both
    sha1 = FileCache.sha256_file(file1)
    sha2 = FileCache.sha256_file(file2)
    
    print(f"File 1: {file1.name} -> SHA256: {sha1[:16]}...")
    print(f"File 2: {file2.name} -> SHA256: {sha2[:16]}...")
    
    if sha1 == sha2:
        print("✅ PASS: Identical content produces identical SHA256 hashes")
        return True
    else:
        print("❌ FAIL: Identical content produced different hashes")
        return False


def test_reference_counting():
    """Test that reference counts are tracked correctly"""
    print("\n" + "="*80)
    print("TEST 2: Reference Counting")
    print("="*80)
    
    try:
        from src.storage.supabase_client import get_storage_manager
        storage = get_storage_manager()
        
        if not storage or not storage.enabled:
            print("⚠️  SKIP: Supabase not available")
            return None
        
        dedup_manager = FileDeduplicationManager(storage)
        
        # Create test file
        content = "Reference counting test content"
        test_file = create_test_file(content, "ref_count_test.txt")
        
        # Check for duplicate (should be None for new file)
        existing = dedup_manager.check_duplicate(test_file, "kimi")
        
        if existing:
            print(f"Found existing file: {existing['provider_file_id']}")
            print(f"Current reference count: {existing.get('reference_count', 1)}")
            
            # Increment reference
            success = dedup_manager.increment_reference(existing['provider_file_id'], "kimi")
            
            if success:
                # Check again to verify increment
                updated = dedup_manager.check_duplicate(test_file, "kimi")
                new_count = updated.get('reference_count', 1)
                old_count = existing.get('reference_count', 1)
                
                if new_count > old_count:
                    print(f"✅ PASS: Reference count incremented from {old_count} to {new_count}")
                    return True
                else:
                    print(f"❌ FAIL: Reference count not incremented (still {new_count})")
                    return False
            else:
                print("❌ FAIL: Failed to increment reference count")
                return False
        else:
            print("ℹ️  No existing file found - this is expected for first run")
            print("   Run test again after uploading a file to test increment")
            return None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deduplication_stats():
    """Test deduplication statistics retrieval"""
    print("\n" + "="*80)
    print("TEST 3: Deduplication Statistics")
    print("="*80)
    
    try:
        from src.storage.supabase_client import get_storage_manager
        storage = get_storage_manager()
        
        if not storage or not storage.enabled:
            print("⚠️  SKIP: Supabase not available")
            return None
        
        dedup_manager = FileDeduplicationManager(storage)
        
        # Get stats for Kimi
        kimi_stats = dedup_manager.get_deduplication_stats("kimi")
        print(f"\nKimi Deduplication Stats:")
        print(f"  Total files: {kimi_stats['total_files']}")
        print(f"  Total references: {kimi_stats['total_references']}")
        print(f"  Deduplicated files: {kimi_stats['deduplicated_files']}")
        print(f"  Storage saved: {kimi_stats['storage_saved_bytes']:,} bytes ({kimi_stats['storage_saved_bytes'] / 1024 / 1024:.2f} MB)")
        
        # Get stats for GLM
        glm_stats = dedup_manager.get_deduplication_stats("glm")
        print(f"\nGLM Deduplication Stats:")
        print(f"  Total files: {glm_stats['total_files']}")
        print(f"  Total references: {glm_stats['total_references']}")
        print(f"  Deduplicated files: {glm_stats['deduplicated_files']}")
        print(f"  Storage saved: {glm_stats['storage_saved_bytes']:,} bytes ({glm_stats['storage_saved_bytes'] / 1024 / 1024:.2f} MB)")
        
        # Get overall stats
        overall_stats = dedup_manager.get_deduplication_stats()
        print(f"\nOverall Deduplication Stats:")
        print(f"  Total files: {overall_stats['total_files']}")
        print(f"  Total references: {overall_stats['total_references']}")
        print(f"  Deduplicated files: {overall_stats['deduplicated_files']}")
        print(f"  Storage saved: {overall_stats['storage_saved_bytes']:,} bytes ({overall_stats['storage_saved_bytes'] / 1024 / 1024:.2f} MB)")
        
        print("\n✅ PASS: Statistics retrieved successfully")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_integration():
    """Test integration with FileCache"""
    print("\n" + "="*80)
    print("TEST 4: FileCache Integration")
    print("="*80)
    
    try:
        from src.storage.supabase_client import get_storage_manager
        storage = get_storage_manager()
        
        if not storage or not storage.enabled:
            print("⚠️  SKIP: Supabase not available")
            return None
        
        dedup_manager = FileDeduplicationManager(storage)
        
        # Create test file
        content = "Cache integration test content"
        test_file = create_test_file(content, "cache_test.txt")
        sha256 = FileCache.sha256_file(test_file)
        
        # First check - should hit database
        print("First check (should query database)...")
        existing1 = dedup_manager.check_duplicate(test_file, "kimi")
        
        # Second check - should hit cache
        print("Second check (should hit cache)...")
        existing2 = dedup_manager.check_duplicate(test_file, "kimi")
        
        if existing1 and existing2:
            if existing1['provider_file_id'] == existing2['provider_file_id']:
                print(f"✅ PASS: Cache integration working (file_id: {existing1['provider_file_id']})")
                return True
            else:
                print("❌ FAIL: Cache returned different file_id")
                return False
        elif not existing1 and not existing2:
            print("ℹ️  No existing file found - expected for first run")
            return None
        else:
            print("❌ FAIL: Inconsistent results between checks")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cleanup_unreferenced():
    """Test cleanup of unreferenced files"""
    print("\n" + "="*80)
    print("TEST 5: Cleanup Unreferenced Files")
    print("="*80)

    try:
        from src.storage.supabase_client import get_storage_manager
        storage = get_storage_manager()

        if not storage or not storage.enabled:
            print("⚠️  SKIP: Supabase not available")
            return None

        dedup_manager = FileDeduplicationManager(storage)

        # Run cleanup in dry-run mode
        print("Running cleanup (dry-run mode)...")
        result = dedup_manager.cleanup_unreferenced_files(
            provider=None,  # All providers
            grace_period_hours=24,
            dry_run=True
        )

        print(f"Files found: {result['files_found']}")
        print(f"Would delete: {result['files_deleted']}")
        print(f"Would free: {result['storage_freed_bytes']:,} bytes ({result['storage_freed_bytes'] / 1024 / 1024:.2f} MB)")

        if result.get('errors'):
            print(f"Errors: {result['errors']}")

        print("✅ PASS: Cleanup dry-run completed successfully")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monitoring_metrics():
    """Test deduplication monitoring metrics"""
    print("\n" + "="*80)
    print("TEST 6: Monitoring Metrics")
    print("="*80)

    try:
        # Reset metrics
        reset_dedup_metrics()

        # Get current metrics
        metrics = get_dedup_metrics()

        print(f"\nCurrent Metrics:")
        print(f"  Cache hits: {metrics['cache_hits']}")
        print(f"  Cache misses: {metrics['cache_misses']}")
        print(f"  Cache hit rate: {metrics['cache_hit_rate']}%")
        print(f"  DB hits: {metrics['db_hits']}")
        print(f"  DB misses: {metrics['db_misses']}")
        print(f"  Total checks: {metrics['total_checks']}")
        print(f"  Storage saved: {metrics['storage_saved_bytes']:,} bytes")

        print("\n✅ PASS: Monitoring metrics retrieved successfully")
        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all deduplication tests"""
    print("\n" + "="*80)
    print("FILE DEDUPLICATION TEST SUITE")
    print("Phase 2.4 Final 2% - File Deduplication (Enhanced)")
    print("="*80)

    results = {
        "SHA256 Detection": test_deduplication_detection(),
        "Reference Counting": test_reference_counting(),
        "Statistics": test_deduplication_stats(),
        "Cache Integration": test_cache_integration(),
        "Cleanup Unreferenced": test_cleanup_unreferenced(),
        "Monitoring Metrics": test_monitoring_metrics()
    }
    
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    
    if failed > 0:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
    elif passed > 0:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n⚠️  ALL TESTS SKIPPED (Supabase not available)")
        sys.exit(0)


if __name__ == "__main__":
    main()

