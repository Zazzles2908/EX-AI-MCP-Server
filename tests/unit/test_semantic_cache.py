"""
Unit tests for semantic cache

Tests cache functionality including:
- Cache hit/miss behavior
- TTL expiration
- LRU eviction
- Cache key generation
- Statistics tracking
"""

import time
import pytest
from utils.infrastructure.semantic_cache import SemanticCache


class TestSemanticCache:
    """Test suite for SemanticCache"""
    
    def test_cache_initialization(self):
        """Test cache initializes with correct parameters"""
        cache = SemanticCache(ttl_seconds=300, max_size=500)
        
        stats = cache.get_stats()
        assert stats["ttl_seconds"] == 300
        assert stats["max_size"] == 500
        assert stats["cache_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0
    
    def test_cache_miss(self):
        """Test cache miss returns None"""
        cache = SemanticCache()
        
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.7
        )
        
        assert result is None
        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
    
    def test_cache_hit(self):
        """Test cache hit returns cached value"""
        cache = SemanticCache()
        
        # Cache a response
        cache.set(
            prompt="What is 2+2?",
            model="test-model",
            response="4",
            temperature=0.7
        )
        
        # Retrieve cached response
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.7
        )
        
        assert result == "4"
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
    
    def test_cache_key_normalization(self):
        """Test cache key is consistent for equivalent requests"""
        cache = SemanticCache()
        
        # Cache with extra whitespace
        cache.set(
            prompt="  What is 2+2?  ",
            model="test-model",
            response="4",
            temperature=0.7
        )
        
        # Retrieve with normalized prompt
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.7
        )
        
        assert result == "4"
    
    def test_cache_different_parameters(self):
        """Test different parameters create different cache entries"""
        cache = SemanticCache()
        
        # Cache response for temperature 0.7
        cache.set(
            prompt="What is 2+2?",
            model="test-model",
            response="4 (temp 0.7)",
            temperature=0.7
        )
        
        # Different temperature should miss
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.5
        )
        
        assert result is None
    
    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL"""
        cache = SemanticCache(ttl_seconds=1)  # 1 second TTL
        
        # Cache a response
        cache.set(
            prompt="What is 2+2?",
            model="test-model",
            response="4",
            temperature=0.7
        )
        
        # Should hit immediately
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.7
        )
        assert result == "4"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should miss after expiration
        result = cache.get(
            prompt="What is 2+2?",
            model="test-model",
            temperature=0.7
        )
        assert result is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = SemanticCache(max_size=3)
        
        # Fill cache
        cache.set("prompt1", "model", "response1")
        cache.set("prompt2", "model", "response2")
        cache.set("prompt3", "model", "response3")
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 3
        
        # Add one more (should evict oldest)
        cache.set("prompt4", "model", "response4")
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 3
        assert stats["evictions"] == 1
    
    def test_cache_clear(self):
        """Test cache clear removes all entries"""
        cache = SemanticCache()
        
        # Add some entries
        cache.set("prompt1", "model", "response1")
        cache.set("prompt2", "model", "response2")
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 2
        
        # Clear cache
        cache.clear()
        
        stats = cache.get_stats()
        assert stats["cache_size"] == 0
    
    def test_cache_stats_tracking(self):
        """Test cache statistics are tracked correctly"""
        cache = SemanticCache()
        
        # Generate some hits and misses
        cache.set("prompt1", "model", "response1")
        cache.get("prompt1", "model")  # Hit
        cache.get("prompt2", "model")  # Miss
        cache.get("prompt1", "model")  # Hit
        
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_requests"] == 3
        assert stats["hit_rate_percent"] == pytest.approx(66.67, rel=0.1)
    
    def test_cache_reset_stats(self):
        """Test cache statistics can be reset"""
        cache = SemanticCache()
        
        # Generate some activity
        cache.set("prompt1", "model", "response1")
        cache.get("prompt1", "model")
        cache.get("prompt2", "model")
        
        # Reset stats
        cache.reset_stats()
        
        stats = cache.get_stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["total_requests"] == 0
    
    def test_cache_with_additional_params(self):
        """Test cache handles additional parameters"""
        cache = SemanticCache()
        
        # Cache with extra params
        cache.set(
            prompt="Test",
            model="test-model",
            response="response",
            thinking_mode="high",
            use_websearch=True,
            custom_param="value"
        )
        
        # Should hit with same params
        result = cache.get(
            prompt="Test",
            model="test-model",
            thinking_mode="high",
            use_websearch=True,
            custom_param="value"
        )
        assert result == "response"
        
        # Should miss with different custom param
        result = cache.get(
            prompt="Test",
            model="test-model",
            thinking_mode="high",
            use_websearch=True,
            custom_param="different"
        )
        assert result is None
    
    def test_cache_ttl_override(self):
        """Test TTL can be overridden per entry"""
        cache = SemanticCache(ttl_seconds=10)
        
        # Cache with custom TTL
        cache.set(
            prompt="Test",
            model="test-model",
            response="response",
            ttl_override=1  # 1 second
        )
        
        # Should hit immediately
        result = cache.get(prompt="Test", model="test-model")
        assert result == "response"
        
        # Wait for custom TTL expiration
        time.sleep(1.1)
        
        # Should miss after custom TTL
        result = cache.get(prompt="Test", model="test-model")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

