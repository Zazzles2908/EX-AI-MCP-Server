"""
Integration tests for caching systems.

Tests semantic cache and file cache working together with real components.

Created: 2025-10-11 (Phase 2 Cleanup, Task 2.D)
"""

import pytest
import tempfile
import time
from pathlib import Path
from utils.infrastructure.semantic_cache import SemanticCache
from utils.file.cache import FileCache


class TestSemanticCacheIntegration:
    """Integration tests for semantic cache."""
    
    def setup_method(self):
        """Setup test cache."""
        self.cache = SemanticCache(ttl_seconds=60, max_size=100)
    
    def test_cache_hit_reduces_latency(self):
        """Test that cache hits eliminate API call latency."""
        prompt = "Test prompt"
        model = "test-model"
        response = {"content": "Test response"}
        
        # First call - cache miss
        result = self.cache.get(prompt, model)
        assert result is None
        
        # Store response
        self.cache.set(prompt, model, response)
        
        # Second call - cache hit (should be instant)
        start = time.time()
        result = self.cache.get(prompt, model)
        duration = time.time() - start
        
        assert result == response
        assert duration < 0.001  # Should be < 1ms
    
    def test_cache_respects_ttl(self):
        """Test that cache entries expire after TTL."""
        cache = SemanticCache(ttl_seconds=1, max_size=100)
        
        prompt = "Test prompt"
        model = "test-model"
        response = {"content": "Test response"}
        
        # Store response
        cache.set(prompt, model, response)
        
        # Immediate retrieval should work
        result = cache.get(prompt, model)
        assert result == response
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        result = cache.get(prompt, model)
        assert result is None
    
    def test_cache_handles_different_parameters(self):
        """Test that cache distinguishes between different parameters."""
        prompt = "Test prompt"
        model = "test-model"
        
        # Store with temperature=0.5
        response1 = {"content": "Response 1"}
        self.cache.set(prompt, model, response1, temperature=0.5)
        
        # Store with temperature=0.8
        response2 = {"content": "Response 2"}
        self.cache.set(prompt, model, response2, temperature=0.8)
        
        # Retrieve with temperature=0.5
        result1 = self.cache.get(prompt, model, temperature=0.5)
        assert result1 == response1
        
        # Retrieve with temperature=0.8
        result2 = self.cache.get(prompt, model, temperature=0.8)
        assert result2 == response2
    
    def test_cache_size_limit(self):
        """Test that cache respects max size limit."""
        cache = SemanticCache(ttl_seconds=60, max_size=10)
        
        # Fill cache to capacity
        for i in range(10):
            cache.set(f"prompt_{i}", "model", {"content": f"response_{i}"})
        
        # Add one more (should evict oldest)
        cache.set("prompt_new", "model", {"content": "response_new"})
        
        # First entry should be evicted
        result = cache.get("prompt_0", "model")
        assert result is None
        
        # New entry should be present
        result = cache.get("prompt_new", "model")
        assert result is not None
    
    def test_cache_rejects_large_responses(self):
        """Test that cache rejects responses exceeding max size."""
        cache = SemanticCache(ttl_seconds=60, max_size=100, max_response_size=1000)
        
        # Create large response (> 1000 bytes)
        large_response = {"content": "x" * 2000}
        
        # Try to cache it
        cache.set("prompt", "model", large_response)
        
        # Should not be cached
        result = cache.get("prompt", "model")
        assert result is None
        
        # Check metrics
        stats = cache.get_stats()
        assert stats["size_rejections"] > 0


class TestFileCacheIntegration:
    """Integration tests for file cache."""
    
    def setup_method(self):
        """Setup test cache with temporary file."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_path = Path(self.temp_dir) / "test_cache.json"
        self.cache = FileCache(path=self.cache_path, ttl_secs=60)
    
    def test_cache_persists_across_instances(self):
        """Test that cache persists to disk and loads correctly."""
        sha256 = "abc123"
        provider = "KIMI"
        file_id = "file_123"
        
        # Store in first instance
        self.cache.set(sha256, provider, file_id)
        
        # Create new instance (should load from disk)
        cache2 = FileCache(path=self.cache_path, ttl_secs=60)
        
        # Should retrieve cached value
        result = cache2.get(sha256, provider)
        assert result == file_id
    
    def test_cache_handles_multiple_providers(self):
        """Test that cache stores separate file IDs per provider."""
        sha256 = "abc123"
        
        # Store for KIMI
        self.cache.set(sha256, "KIMI", "kimi_file_123")
        
        # Store for GLM
        self.cache.set(sha256, "GLM", "glm_file_456")
        
        # Retrieve for KIMI
        result_kimi = self.cache.get(sha256, "KIMI")
        assert result_kimi == "kimi_file_123"
        
        # Retrieve for GLM
        result_glm = self.cache.get(sha256, "GLM")
        assert result_glm == "glm_file_456"
    
    def test_cache_expires_old_entries(self):
        """Test that cache expires entries after TTL."""
        cache = FileCache(path=self.cache_path, ttl_secs=1)
        
        sha256 = "abc123"
        provider = "KIMI"
        file_id = "file_123"
        
        # Store entry
        cache.set(sha256, provider, file_id)
        
        # Immediate retrieval should work
        result = cache.get(sha256, provider)
        assert result == file_id
        
        # Wait for TTL to expire
        time.sleep(1.1)
        
        # Should be expired now
        result = cache.get(sha256, provider)
        assert result is None
    
    def test_cache_sha256_hashing(self):
        """Test SHA256 file hashing."""
        # Create temporary file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("Hello, World!")
        
        # Calculate SHA256
        sha256 = FileCache.sha256_file(test_file)
        
        # Should be deterministic
        sha256_2 = FileCache.sha256_file(test_file)
        assert sha256 == sha256_2
        
        # Should be 64 hex characters
        assert len(sha256) == 64
        assert all(c in "0123456789abcdef" for c in sha256)


class TestCacheInteraction:
    """Test interaction between semantic cache and file cache."""
    
    def setup_method(self):
        """Setup both caches."""
        self.temp_dir = tempfile.mkdtemp()
        self.semantic_cache = SemanticCache(ttl_seconds=60, max_size=100)
        self.file_cache = FileCache(
            path=Path(self.temp_dir) / "file_cache.json",
            ttl_secs=60
        )
    
    def test_caches_work_independently(self):
        """Test that semantic and file caches don't interfere."""
        # Store in semantic cache
        self.semantic_cache.set("prompt", "model", {"content": "response"})
        
        # Store in file cache
        self.file_cache.set("sha256", "KIMI", "file_id")
        
        # Both should be retrievable
        semantic_result = self.semantic_cache.get("prompt", "model")
        assert semantic_result == {"content": "response"}
        
        file_result = self.file_cache.get("sha256", "KIMI")
        assert file_result == "file_id"
    
    def test_cache_metrics_are_separate(self):
        """Test that cache metrics are tracked separately."""
        # Generate some cache activity
        self.semantic_cache.set("prompt", "model", {"content": "response"})
        self.semantic_cache.get("prompt", "model")  # Hit
        self.semantic_cache.get("other_prompt", "model")  # Miss
        
        self.file_cache.set("sha256", "KIMI", "file_id")
        self.file_cache.get("sha256", "KIMI")  # Hit
        self.file_cache.get("other_sha256", "KIMI")  # Miss
        
        # Check semantic cache stats
        semantic_stats = self.semantic_cache.get_stats()
        assert semantic_stats["hits"] == 1
        assert semantic_stats["misses"] == 1
        
        # File cache doesn't have get_stats method, but metrics are tracked
        # via performance_metrics module


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

