"""
Unit tests for FileCache

Tests file ID caching functionality including:
- SHA256 file hashing
- Cache hit/miss behavior
- TTL expiration
- Multi-provider support
- Persistence
"""

import tempfile
import time
import pytest
from pathlib import Path
from utils.file.cache import FileCache


class TestFileCache:
    """Test suite for FileCache"""
    
    def test_cache_initialization(self):
        """Test cache initializes with correct parameters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path, ttl_secs=3600)
            
            assert cache.path == cache_path
            assert cache.ttl_secs == 3600
            assert cache._data == {"items": {}}
    
    def test_sha256_file_hashing(self):
        """Test SHA256 file hashing is consistent"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test content for hashing")
            temp_path = Path(f.name)
        
        try:
            # Hash the same file twice
            hash1 = FileCache.sha256_file(temp_path)
            hash2 = FileCache.sha256_file(temp_path)
            
            # Should be identical
            assert hash1 == hash2
            assert len(hash1) == 64  # SHA256 produces 64 hex chars
        finally:
            temp_path.unlink()
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path)
            
            result = cache.get("nonexistent_sha256", "KIMI")
            assert result is None
    
    def test_cache_hit(self):
        """Test cache hit returns file_id"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path)
            
            # Set a file_id
            cache.set("test_sha256", "KIMI", "file-12345")
            
            # Retrieve it
            result = cache.get("test_sha256", "KIMI")
            assert result == "file-12345"
    
    def test_multi_provider_support(self):
        """Test same file can have different IDs for different providers"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path)
            
            sha = "test_sha256"
            
            # Set file_id for KIMI
            cache.set(sha, "KIMI", "kimi-file-123")
            
            # Set file_id for GLM
            cache.set(sha, "GLM", "glm-file-456")
            
            # Both should be retrievable
            assert cache.get(sha, "KIMI") == "kimi-file-123"
            assert cache.get(sha, "GLM") == "glm-file-456"
    
    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path, ttl_secs=1)  # 1 second TTL
            
            # Set a file_id
            cache.set("test_sha256", "KIMI", "file-12345")
            
            # Should hit immediately
            result = cache.get("test_sha256", "KIMI")
            assert result == "file-12345"
            
            # Wait for expiration
            time.sleep(1.1)
            
            # Should miss after expiration
            result = cache.get("test_sha256", "KIMI")
            assert result is None
    
    def test_cache_persistence(self):
        """Test cache persists to disk and can be reloaded"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            
            # Create cache and set value
            cache1 = FileCache(path=cache_path)
            cache1.set("test_sha256", "KIMI", "file-12345")
            
            # Create new cache instance (should load from disk)
            cache2 = FileCache(path=cache_path)
            result = cache2.get("test_sha256", "KIMI")
            
            assert result == "file-12345"
    
    def test_cache_file_integration(self):
        """Test end-to-end: hash file, cache ID, retrieve ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Test content")
            
            # Create cache
            cache_path = Path(tmpdir) / "cache.json"
            cache = FileCache(path=cache_path)
            
            # Hash the file
            sha = FileCache.sha256_file(test_file)
            
            # Cache should miss initially
            assert cache.get(sha, "KIMI") is None
            
            # Set file_id
            cache.set(sha, "KIMI", "file-12345")
            
            # Should hit now
            assert cache.get(sha, "KIMI") == "file-12345"
    
    def test_cache_different_files_different_hashes(self):
        """Test different files produce different hashes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two different files
            file1 = Path(tmpdir) / "file1.txt"
            file2 = Path(tmpdir) / "file2.txt"
            
            file1.write_text("Content 1")
            file2.write_text("Content 2")
            
            # Hash both files
            hash1 = FileCache.sha256_file(file1)
            hash2 = FileCache.sha256_file(file2)
            
            # Hashes should be different
            assert hash1 != hash2
    
    def test_cache_same_content_same_hash(self):
        """Test files with same content produce same hash"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two files with identical content
            file1 = Path(tmpdir) / "file1.txt"
            file2 = Path(tmpdir) / "file2.txt"
            
            content = "Identical content"
            file1.write_text(content)
            file2.write_text(content)
            
            # Hash both files
            hash1 = FileCache.sha256_file(file1)
            hash2 = FileCache.sha256_file(file2)
            
            # Hashes should be identical
            assert hash1 == hash2
    
    def test_cache_expiration_cleanup(self):
        """Test expired entries are cleaned up"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path, ttl_secs=1)
            
            # Set a file_id
            cache.set("test_sha256", "KIMI", "file-12345")
            
            # Verify it's in the cache
            assert "test_sha256" in cache._data["items"]
            
            # Wait for expiration
            time.sleep(1.1)
            
            # Access expired entry (should trigger cleanup)
            result = cache.get("test_sha256", "KIMI")
            assert result is None
            
            # Entry should be removed from cache
            assert "test_sha256" not in cache._data["items"]
    
    def test_cache_zero_ttl_disables_expiration(self):
        """Test TTL=0 disables expiration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "test_cache.json"
            cache = FileCache(path=cache_path, ttl_secs=0)
            
            # Set a file_id
            cache.set("test_sha256", "KIMI", "file-12345")
            
            # Wait a bit
            time.sleep(0.5)
            
            # Should still hit (no expiration)
            result = cache.get("test_sha256", "KIMI")
            assert result == "file-12345"
    
    def test_cache_handles_missing_file(self):
        """Test cache handles missing cache file gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "nonexistent.json"
            
            # Should not raise error
            cache = FileCache(path=cache_path)
            
            # Should have empty data
            assert cache._data == {"items": {}}
    
    def test_cache_handles_corrupted_file(self):
        """Test cache handles corrupted cache file gracefully"""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = Path(tmpdir) / "corrupted.json"
            
            # Write corrupted JSON
            cache_path.write_text("{ invalid json }")
            
            # Should not raise error
            cache = FileCache(path=cache_path)
            
            # Should have empty data
            assert cache._data == {"items": {}}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

