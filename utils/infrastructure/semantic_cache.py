"""
Semantic Cache for AI API Responses

This module provides intelligent caching for AI API responses to reduce latency
and API costs. It caches responses based on semantic similarity of requests.

Key Features:
- Request similarity detection (hash prompt + model + key parameters)
- TTL-based cache expiration (default 10 minutes)
- Cache hit/miss tracking for metrics
- Thread-safe operations
- LRU eviction when cache size limit reached

Performance Impact:
- Cache hit: ~1-5ms (vs 1-4 seconds for AI API call)
- Potential latency reduction: 40-80% for repeated/similar requests
- Expected hit rate: 30-50% for common prompts

Usage:
    from utils.infrastructure.semantic_cache import get_semantic_cache
    
    cache = get_semantic_cache()
    
    # Try to get cached response
    cached = cache.get(prompt, model, temperature)
    if cached:
        return cached
    
    # Call AI API
    response = await call_ai_api(prompt, model, temperature)
    
    # Cache the response
    cache.set(prompt, model, temperature, response)
"""

import hashlib
import json
import logging
import threading
import time
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)

# Import performance metrics (optional)
try:
    from utils.infrastructure.performance_metrics import record_cache_hit, record_cache_miss
    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False
    def record_cache_hit(cache_name: str): pass
    def record_cache_miss(cache_name: str): pass


class SemanticCache:
    """
    Thread-safe semantic cache for AI API responses.
    
    Caches responses based on request parameters (prompt, model, temperature, etc.)
    with TTL-based expiration and LRU eviction.
    """
    
    def __init__(self, ttl_seconds: int = 600, max_size: int = 1000, max_response_size: int = 1048576):
        """
        Initialize semantic cache.

        Args:
            ttl_seconds: Time-to-live for cached entries (default 10 minutes)
            max_size: Maximum number of cached entries (default 1000)
            max_response_size: Maximum size of a single response in bytes (default 1MB)
        """
        self._cache: Dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()
        self._ttl = ttl_seconds
        self._max_size = max_size
        self._max_response_size = max_response_size

        # Metrics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._size_rejections = 0  # Track responses too large to cache

        logger.info(f"Semantic cache initialized (TTL={ttl_seconds}s, max_size={max_size}, max_response_size={max_response_size} bytes)")
    
    def _generate_cache_key(
        self,
        prompt: str,
        model: str,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        **kwargs
    ) -> str:
        """
        Generate cache key from request parameters.
        
        Args:
            prompt: The prompt text
            model: Model name
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            **kwargs: Additional parameters to include in cache key
            
        Returns:
            SHA256 hash of normalized request parameters
        """
        # Normalize parameters for consistent hashing
        # CRITICAL FIX (P1): Include full model name to prevent cross-model cache pollution
        # This prevents kimi-k2-0905-preview and kimi-k2-0711-preview from sharing cache entries
        # which was causing 8x variance in safety calculations (2.6 vs 21.2 cal/cm²)
        cache_params = {
            "prompt": prompt.strip(),
            "model": model,  # Full model name including version
            "temperature": round(temperature, 2) if temperature is not None else None,
            "thinking_mode": thinking_mode,
            "use_websearch": use_websearch,
        }
        
        # Add any additional kwargs
        for key, value in kwargs.items():
            if value is not None:
                cache_params[key] = value
        
        # Create deterministic JSON string
        cache_str = json.dumps(cache_params, sort_keys=True)
        
        # Generate hash
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def get(
        self,
        prompt: str,
        model: str,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        **kwargs
    ) -> Optional[Any]:
        """
        Get cached response if available and not expired.
        
        Args:
            prompt: The prompt text
            model: Model name
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            **kwargs: Additional parameters
            
        Returns:
            Cached response if available, None otherwise
        """
        cache_key = self._generate_cache_key(
            prompt, model, temperature, thinking_mode, use_websearch, **kwargs
        )
        
        with self._lock:
            if cache_key in self._cache:
                response, expires_at = self._cache[cache_key]
                
                # Check if expired
                if time.time() < expires_at:
                    self._hits += 1
                    if _METRICS_AVAILABLE:
                        record_cache_hit("semantic_cache")
                    logger.debug(f"Cache HIT for model={model} (key={cache_key[:8]}...)")
                    return response
                else:
                    # Remove expired entry
                    del self._cache[cache_key]
                    logger.debug(f"Cache entry expired for model={model}")

            self._misses += 1
            if _METRICS_AVAILABLE:
                record_cache_miss("semantic_cache")
            logger.debug(f"Cache MISS for model={model} (key={cache_key[:8]}...)")
            return None
    
    def set(
        self,
        prompt: str,
        model: str,
        response: Any,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        ttl_override: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Cache a response with TTL.
        
        Args:
            prompt: The prompt text
            model: Model name
            response: The response to cache
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            ttl_override: Override default TTL for this entry
            **kwargs: Additional parameters
        """
        cache_key = self._generate_cache_key(
            prompt, model, temperature, thinking_mode, use_websearch, **kwargs
        )

        # Check response size before caching
        import sys
        response_size = sys.getsizeof(response)
        if response_size > self._max_response_size:
            with self._lock:
                self._size_rejections += 1
            logger.warning(
                f"Response too large to cache: {response_size} bytes "
                f"(max: {self._max_response_size} bytes) for model={model}"
            )
            return

        ttl = ttl_override if ttl_override is not None else self._ttl
        expires_at = time.time() + ttl

        with self._lock:
            # Check if we need to evict entries (LRU)
            if len(self._cache) >= self._max_size:
                self._evict_oldest()

            self._cache[cache_key] = (response, expires_at)
            logger.debug(f"Cached response for model={model} (TTL={ttl}s, size={response_size} bytes, key={cache_key[:8]}...)")
    
    def _evict_oldest(self) -> None:
        """Evict the oldest entry (LRU eviction)."""
        if not self._cache:
            return
        
        # Find entry with earliest expiration time
        oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
        del self._cache[oldest_key]
        self._evictions += 1
        logger.debug(f"Evicted oldest cache entry (total evictions: {self._evictions})")
    
    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cleared {count} cached entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total_requests,
                "hit_rate_percent": round(hit_rate, 2),
                "cache_size": len(self._cache),
                "max_size": self._max_size,
                "evictions": self._evictions,
                "size_rejections": self._size_rejections,
                "ttl_seconds": self._ttl,
                "max_response_size_bytes": self._max_response_size,
            }
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._evictions = 0
            self._size_rejections = 0
            logger.info("Cache statistics reset")


# Global singleton instance
_cache_instance: Optional[SemanticCache] = None
_cache_lock = threading.Lock()


def get_semantic_cache() -> SemanticCache:
    """
    Get the global semantic cache instance (singleton pattern).
    
    Returns:
        SemanticCache instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                import os

                # Get configuration from environment
                ttl = int(os.getenv("SEMANTIC_CACHE_TTL_SECONDS", "600"))  # 10 minutes default
                max_size = int(os.getenv("SEMANTIC_CACHE_MAX_SIZE", "1000"))
                max_response_size = int(os.getenv("SEMANTIC_CACHE_MAX_RESPONSE_SIZE", "1048576"))  # 1MB default

                _cache_instance = SemanticCache(
                    ttl_seconds=ttl,
                    max_size=max_size,
                    max_response_size=max_response_size
                )
                logger.info(
                    f"Initialized global semantic cache "
                    f"(TTL={ttl}s, max_size={max_size}, max_response_size={max_response_size} bytes)"
                )

    return _cache_instance

