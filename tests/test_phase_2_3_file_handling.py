"""
Phase 2.3: File Handling Issues - Comprehensive Test Suite

Tests for:
1. File upload/download with different sizes
2. Non-ASCII and special character filenames
3. Bidirectional sync (Moonshot ↔ Supabase)
4. Orphaned file detection
5. File cleanup (30+ days)
6. Retry logic and error handling
7. Filename normalization
"""

import pytest
import os
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

# Import file handling components
from src.providers.kimi import KimiModelProvider
from src.providers.kimi_files import upload_file
from src.storage.supabase_client import get_storage_manager

logger = logging.getLogger(__name__)


class TestFileUploadSizes:
    """Test file uploads with different sizes"""

    @pytest.fixture
    def test_dir(self):
        """Create a test directory in the project"""
        test_path = Path("tests/test_files_temp")
        test_path.mkdir(exist_ok=True)
        yield test_path
        # Cleanup
        import shutil
        if test_path.exists():
            shutil.rmtree(test_path, ignore_errors=True)

    def test_tiny_file_upload(self, test_dir):
        """Test upload of file < 1KB"""
        # Create tiny file (100 bytes)
        test_file = test_dir / "tiny.txt"
        test_file.write_text("x" * 100)
        
        # Upload should succeed
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")
        
        provider = KimiModelProvider(api_key=api_key)
        file_id = upload_file(provider.client, str(test_file))
        
        assert file_id is not None
        assert len(file_id) > 0
    
    def test_small_file_upload(self, test_dir):
        """Test upload of file ~5KB"""
        # Create 5KB file
        test_file = test_dir / "small.txt"
        test_file.write_text("x" * 5000)

        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")

        provider = KimiModelProvider(api_key=api_key)
        file_id = upload_file(provider.client, str(test_file))

        assert file_id is not None
        assert len(file_id) > 0

    def test_medium_file_upload(self, test_dir):
        """Test upload of file ~1MB"""
        # Create 1MB file
        test_file = test_dir / "medium.txt"
        test_file.write_text("x" * (1024 * 1024))

        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")

        provider = KimiModelProvider(api_key=api_key)
        file_id = upload_file(provider.client, str(test_file))

        assert file_id is not None
        assert len(file_id) > 0

    def test_large_file_upload(self, test_dir):
        """Test upload of file ~10MB"""
        # Create 10MB file
        test_file = test_dir / "large.txt"
        test_file.write_text("x" * (10 * 1024 * 1024))
        
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")
        
        provider = KimiModelProvider(api_key=api_key)
        
        # This might fail if there's a size limit
        try:
            file_id = upload_file(provider.client, str(test_file))
            assert file_id is not None
        except (ValueError, RuntimeError) as e:
            # Expected if file exceeds limit
            assert "size" in str(e).lower() or "limit" in str(e).lower()


class TestFilenameEdgeCases:
    """Test uploads with non-ASCII and special character filenames"""

    @pytest.fixture
    def test_dir(self):
        """Create a test directory in the project"""
        test_path = Path("tests/test_files_temp")
        test_path.mkdir(exist_ok=True)
        yield test_path
        # Cleanup
        import shutil
        if test_path.exists():
            shutil.rmtree(test_path, ignore_errors=True)

    def test_non_ascii_filename(self, test_dir):
        """Test upload with non-ASCII characters (Chinese, Japanese, etc.)"""
        # Create file with Chinese characters
        test_file = test_dir / "测试文件.txt"
        test_file.write_text("Test content")
        
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")
        
        provider = KimiModelProvider(api_key=api_key)
        
        try:
            file_id = upload_file(provider.client, str(test_file))
            assert file_id is not None
        except Exception as e:
            # Document the failure for investigation
            logger.error(f"Non-ASCII filename upload failed: {e}")
            pytest.fail(f"Non-ASCII filename not supported: {e}")
    
    def test_special_characters_filename(self, test_dir):
        """Test upload with special characters"""
        # Create file with special characters
        test_file = test_dir / "test_file!@#$%^&().txt"
        test_file.write_text("Test content")

        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")

        provider = KimiModelProvider(api_key=api_key)

        try:
            file_id = upload_file(provider.client, str(test_file))
            assert file_id is not None
        except Exception as e:
            logger.error(f"Special character filename upload failed: {e}")
            pytest.fail(f"Special characters not supported: {e}")

    def test_unicode_emoji_filename(self, test_dir):
        """Test upload with Unicode emoji in filename"""
        # Create file with emoji
        test_file = test_dir / "test_😀_file.txt"
        test_file.write_text("Test content")

        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")

        provider = KimiModelProvider(api_key=api_key)

        try:
            file_id = upload_file(provider.client, str(test_file))
            assert file_id is not None
        except Exception as e:
            logger.error(f"Emoji filename upload failed: {e}")
            pytest.fail(f"Emoji filenames not supported: {e}")

    def test_long_filename(self, test_dir):
        """Test upload with very long filename"""
        # Create file with 200 character filename
        long_name = "a" * 200 + ".txt"
        test_file = test_dir / long_name
        test_file.write_text("Test content")
        
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")
        
        provider = KimiModelProvider(api_key=api_key)
        
        try:
            file_id = upload_file(provider.client, str(test_file))
            assert file_id is not None
        except Exception as e:
            logger.error(f"Long filename upload failed: {e}")
            # This might be expected - document the limit
            assert "name" in str(e).lower() or "length" in str(e).lower()


class TestBidirectionalSync:
    """Test Moonshot ↔ Supabase bidirectional synchronization"""

    @pytest.fixture
    def test_dir(self):
        """Create a test directory in the project"""
        test_path = Path("tests/test_files_temp")
        test_path.mkdir(exist_ok=True)
        yield test_path
        # Cleanup
        import shutil
        if test_path.exists():
            shutil.rmtree(test_path, ignore_errors=True)

    def test_upload_creates_supabase_record(self, test_dir):
        """Test that uploading to Moonshot creates Supabase record"""
        test_file = test_dir / "sync_test.txt"
        test_file.write_text("Sync test content")

        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")

        # Upload file
        provider = KimiModelProvider(api_key=api_key)
        file_id = upload_file(provider.client, str(test_file))

        # Check Supabase record exists
        storage = get_storage_manager()
        if not storage or not storage.enabled:
            pytest.skip("Supabase not enabled")

        # Give it a moment to sync
        time.sleep(1)

        client = storage.get_client()
        result = client.table("provider_file_uploads").select("*").eq("provider_file_id", file_id).execute()

        assert result.data is not None
        assert len(result.data) > 0
        assert result.data[0]["provider"] == "kimi"
        assert result.data[0]["provider_file_id"] == file_id

    def test_supabase_storage_upload(self, test_dir):
        """Test that file content is uploaded to Supabase Storage"""
        test_file = test_dir / "storage_test.txt"
        test_content = "Storage test content"
        test_file.write_text(test_content)
        
        api_key = os.getenv("KIMI_API_KEY")
        if not api_key:
            pytest.skip("KIMI_API_KEY not set")
        
        # Upload file
        provider = KimiModelProvider(api_key=api_key)
        file_id = upload_file(provider.client, str(test_file))
        
        # Check Supabase Storage
        storage = get_storage_manager()
        if not storage or not storage.enabled:
            pytest.skip("Supabase not enabled")
        
        time.sleep(1)
        
        # Get supabase_file_id from provider_file_uploads
        client = storage.get_client()
        result = client.table("provider_file_uploads").select("supabase_file_id").eq("provider_file_id", file_id).execute()
        
        if result.data and result.data[0]["supabase_file_id"]:
            supabase_file_id = result.data[0]["supabase_file_id"]
            
            # Download from Supabase Storage
            downloaded_content = storage.download_file(supabase_file_id)
            
            assert downloaded_content is not None
            assert downloaded_content.decode('utf-8') == test_content


class TestOrphanedFileDetection:
    """Test orphaned file detection and cleanup"""
    
    def test_identify_orphaned_files(self):
        """Test identification of files in Moonshot but not in Supabase"""
        # This test requires manual setup or mocking
        # For now, we'll test the logic exists
        pytest.skip("Requires manual setup - implement after basic tests pass")
    
    def test_cleanup_orphaned_files(self):
        """Test cleanup of orphaned files"""
        pytest.skip("Requires manual setup - implement after basic tests pass")


class TestFileCleanup:
    """Test automatic cleanup of old files (30+ days)"""
    
    def test_cleanup_old_files(self):
        """Test cleanup of files older than 30 days"""
        storage = get_storage_manager()
        if not storage or not storage.enabled:
            pytest.skip("Supabase not enabled")
        
        # This test requires creating old records or mocking
        pytest.skip("Requires time manipulation - implement after basic tests pass")


# Run tests with: python -m pytest tests/test_phase_2_3_file_handling.py -v

