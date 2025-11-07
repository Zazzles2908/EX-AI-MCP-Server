"""
Semantic Cache Manager for AI API Responses

Extends BaseCacheManager with semantic-specific features:
- Complex cache key generation (SHA256 hash of multiple parameters)
- Response size validation
- Performance metrics integration
- L2 Redis persistence (survives restarts)

This is the new implementation that replaces the legacy SemanticCache.

Migration Strategy:
- Feature flag: SEMANTIC_CACHE_USE_BASE_MANAGER (default: false)
- Gradual rollout with performance monitoring
- Rollback capability if performance degrades

Created: 2025-10-31 (Phase 3: SemanticCache Migration)
"""

import hashlib
import json
import logging
import os
from typing import Any, Optional, Dict

from utils.caching.base_cache_manager import BaseCacheManager

logger = logging.getLogger(__name__)

# Import performance metrics (optional)
try:
    from utils.infrastructure.performance_metrics import record_cache_hit, record_cache_miss
    _METRICS_AVAILABLE = True
except ImportError:
    _METRICS_AVAILABLE = False
    def record_cache_hit(cache_name: str): pass
    def record_cache_miss(cache_name: str): pass

# Import cache metrics collector (Week 2-3 Monitoring Phase - 2025-10-31)
try:
    from utils.monitoring.cache_metrics_collector import (
        record_cache_hit as record_detailed_hit,
        record_cache_miss as record_detailed_miss,
        record_cache_set as record_detailed_set,
        record_cache_error as record_detailed_error
    )
    _DETAILED_METRICS_AVAILABLE = True
except ImportError:
    _DETAILED_METRICS_AVAILABLE = False
    logger.debug("[SEMANTIC_CACHE_MANAGER] Detailed metrics collector not available (optional feature)")
    def record_detailed_hit(*args, **kwargs): pass
    def record_detailed_miss(*args, **kwargs): pass
    def record_detailed_set(*args, **kwargs): pass
    def record_detailed_error(*args, **kwargs): pass

import time


class SemanticCacheManager(BaseCacheManager):
    """
    Semantic cache manager for AI API responses.
    
    Extends BaseCacheManager with:
    - Complex cache key generation (SHA256 hash)
    - Response size validation
    - Performance metrics integration
    - L2 Redis persistence
    
    Benefits over legacy SemanticCache:
    - Gains L2 Redis persistence (survives restarts)
    - Distributed caching across processes
    - Unified caching infrastructure
    - Better monitoring and statistics
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int = 600,
        max_response_size: int = 1048576,
        enable_redis: bool = True
    ):
        """
        Initialize semantic cache manager.
        
        Args:
            max_size: Maximum number of cached entries (default 1000)
            ttl_seconds: Time-to-live for cached entries (default 10 minutes)
            max_response_size: Maximum size of a single response in bytes (default 1MB)
            enable_redis: Whether to enable L2 Redis caching (default True)
        """
        super().__init__(
            l1_maxsize=max_size,
            l1_ttl=ttl_seconds,
            l2_ttl=ttl_seconds * 3,  # Longer persistence in Redis (30 minutes)
            enable_redis=enable_redis,
            cache_prefix="semantic",
            max_response_size=max_response_size
        )
        
        logger.info(
            f"Semantic cache manager initialized "
            f"(TTL={ttl_seconds}s, max_size={max_size}, max_response_size={max_response_size} bytes, "
            f"redis_enabled={enable_redis})"
        )
    
    def _generate_cache_key(
        self,
        prompt: str,
        model: str,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        system_prompt_hash: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate cache key from request parameters.
        
        Uses SHA256 hash of normalized request parameters to create
        deterministic cache keys that prevent cross-model cache pollution.
        
        Args:
            prompt: The prompt text
            model: Model name (full name including version)
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            system_prompt_hash: Hash of system prompt (to avoid false cache hits)
            **kwargs: Additional parameters to include in cache key
            
        Returns:
            SHA256 hash of normalized request parameters
        """
        # Normalize parameters for consistent hashing
        # CRITICAL: Include full model name to prevent cross-model cache pollution
        cache_params = {
            "prompt": prompt.strip(),
            "model": model,  # Full model name including version
            "temperature": round(temperature, 2) if temperature is not None else None,
            "thinking_mode": thinking_mode,
            "use_websearch": use_websearch,
            "system_prompt_hash": system_prompt_hash,
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
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        system_prompt_hash: Optional[str] = None,
        **kwargs
    ) -> Optional[Any]:
        """
        Get cached response if available and not expired.

        This method supports TWO calling conventions:
        1. Direct: get(prompt="...", model="glm-4.5", temperature=0.5)
        2. Dict unpacking: get(**{'prompt': '...', 'model': 'glm-4.5', 'temperature': 0.5})

        Args:
            prompt: The prompt text (can be None if passed via kwargs)
            model: Model name (can be None if passed via kwargs)
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            system_prompt_hash: Hash of system prompt
            **kwargs: Additional parameters (also used for prompt/model if not passed directly)

        Returns:
            Cached response if available, None otherwise
        """
        # Handle both calling conventions
        # If prompt is None, try to extract from kwargs (dict unpacking)
        if prompt is None:
            if not kwargs:
                raise TypeError("get() missing required argument: 'prompt' (or dict with 'prompt' key)")
            prompt = kwargs.get('prompt')
            model = kwargs.get('model', model)
            temperature = kwargs.get('temperature', temperature)
            thinking_mode = kwargs.get('thinking_mode', thinking_mode)
            use_websearch = kwargs.get('use_websearch', use_websearch)
            system_prompt_hash = kwargs.get('system_prompt_hash', system_prompt_hash)

        if not prompt:
            raise TypeError("get() missing required argument: 'prompt'")

        # Handle missing model - use a placeholder or skip caching
        if not model:
            # If no model is provided, we can't do semantic caching
            # Just return None to skip cache
            logger.debug(f"[SEMANTIC_CACHE] No model provided for prompt, skipping cache")
            return None

        # Start timing for metrics (Week 2-3 Monitoring Phase - 2025-10-31)
        start_time = time.time()

        cache_key = self._generate_cache_key(
            prompt, model, temperature, thinking_mode, use_websearch,
            system_prompt_hash, **kwargs
        )

        result = super().get(cache_key)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        cache_size = self._l1_cache.currsize if hasattr(self._l1_cache, 'currsize') else 0

        # Record metrics
        if result is not None:
            if _METRICS_AVAILABLE:
                record_cache_hit("semantic_cache")

            # Record detailed metrics (Week 2-3 Monitoring Phase - 2025-10-31)
            if _DETAILED_METRICS_AVAILABLE:
                record_detailed_hit(
                    cache_key=cache_key[:32],  # Truncate for privacy
                    implementation_type='new',
                    response_time_ms=response_time_ms,
                    cache_size=cache_size
                )

            logger.debug(f"Semantic cache HIT for model={model} (key={cache_key[:8]}..., {response_time_ms}ms)")
        else:
            if _METRICS_AVAILABLE:
                record_cache_miss("semantic_cache")

            # Record detailed metrics (Week 2-3 Monitoring Phase - 2025-10-31)
            if _DETAILED_METRICS_AVAILABLE:
                record_detailed_miss(
                    cache_key=cache_key[:32],  # Truncate for privacy
                    implementation_type='new',
                    response_time_ms=response_time_ms,
                    cache_size=cache_size
                )

            logger.debug(f"Semantic cache MISS for model={model} (key={cache_key[:8]}..., {response_time_ms}ms)")

        return result
    
    def set(
        self,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
        response: Optional[Any] = None,
        temperature: Optional[float] = None,
        thinking_mode: Optional[str] = None,
        use_websearch: bool = False,
        system_prompt_hash: Optional[str] = None,
        ttl_override: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Cache a response with TTL.

        This method supports TWO calling conventions:
        1. Direct: set(prompt="...", model="glm-4.5", response=..., temperature=0.5)
        2. Dict unpacking: set(**{'prompt': '...', 'model': 'glm-4.5', 'response': ..., 'temperature': 0.5})

        Args:
            prompt: The prompt text (can be None if passed via kwargs)
            model: Model name (can be None if passed via kwargs)
            response: The response to cache (can be None if passed via kwargs)
            temperature: Temperature value
            thinking_mode: Thinking mode
            use_websearch: Whether web search is enabled
            system_prompt_hash: Hash of system prompt
            ttl_override: Override default TTL for this entry
            **kwargs: Additional parameters (also used for prompt/model/response if not passed directly)
        """
        # Handle both calling conventions
        # If prompt is None, try to extract from kwargs (dict unpacking)
        if prompt is None:
            if not kwargs:
                raise TypeError("set() missing required argument: 'prompt' (or dict with 'prompt' key)")
            prompt = kwargs.get('prompt')
            model = kwargs.get('model', model)
            response = kwargs.get('response', response)
            temperature = kwargs.get('temperature', temperature)
            thinking_mode = kwargs.get('thinking_mode', thinking_mode)
            use_websearch = kwargs.get('use_websearch', use_websearch)
            system_prompt_hash = kwargs.get('system_prompt_hash', system_prompt_hash)
            ttl_override = kwargs.get('ttl_override', ttl_override)

        if not prompt:
            raise TypeError("set() missing required argument: 'prompt'")

        # Handle missing model - use a placeholder or skip caching
        if not model:
            logger.debug(f"[SEMANTIC_CACHE] No model provided for prompt, skipping cache")
            return

        if response is None:
            raise TypeError("set() missing required argument: 'response'")

        # Start timing for metrics (Week 2-3 Monitoring Phase - 2025-10-31)
        start_time = time.time()

        cache_key = self._generate_cache_key(
            prompt, model, temperature, thinking_mode, use_websearch,
            system_prompt_hash, **kwargs
        )

        # BaseCacheManager.set() will validate response size
        super().set(cache_key, response, ttl_override)

        import sys
        response_size = sys.getsizeof(response)

        # Calculate response time and get cache size
        response_time_ms = int((time.time() - start_time) * 1000)
        cache_size = self._l1_cache.currsize if hasattr(self._l1_cache, 'currsize') else 0

        # Record detailed metrics (Week 2-3 Monitoring Phase - 2025-10-31)
        if _DETAILED_METRICS_AVAILABLE:
            record_detailed_set(
                cache_key=cache_key[:32],  # Truncate for privacy
                implementation_type='new',
                response_time_ms=response_time_ms,
                cache_size=cache_size
            )

        logger.debug(
            f"Cached response for model={model} "
            f"(TTL={ttl_override or self._l1_ttl}s, size={response_size} bytes, key={cache_key[:8]}..., {response_time_ms}ms)"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics with semantic-specific metrics.
        
        Returns:
            Dictionary with cache metrics including hit rate percentage
        """
        stats = super().get_stats()
        
        # Add semantic-specific metrics
        total_requests = stats['total_requests']
        if total_requests > 0:
            hit_rate_percent = (stats['total_hits'] / total_requests) * 100
            stats['hit_rate_percent'] = round(hit_rate_percent, 2)
        else:
            stats['hit_rate_percent'] = 0.0
        
        # Add TTL info
        stats['ttl_seconds'] = self._l1_ttl
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self._stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'writes': 0,
            'errors': 0,
            'size_rejections': 0
        }
        logger.info("Semantic cache statistics reset")


# Global singleton instance
_cache_instance: Optional[SemanticCacheManager] = None
_cache_lock = None


def get_semantic_cache_manager() -> SemanticCacheManager:
    """
    Get the global semantic cache manager instance (singleton pattern).
    
    Returns:
        SemanticCacheManager instance
    """
    global _cache_instance, _cache_lock
    
    if _cache_lock is None:
        import threading
        _cache_lock = threading.Lock()
    
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                # Get configuration from environment
                ttl = int(os.getenv("SEMANTIC_CACHE_TTL_SECONDS", "600"))  # 10 minutes default
                max_size = int(os.getenv("SEMANTIC_CACHE_MAX_SIZE", "1000"))
                max_response_size = int(os.getenv("SEMANTIC_CACHE_MAX_RESPONSE_SIZE", "1048576"))  # 1MB default
                enable_redis = os.getenv("SEMANTIC_CACHE_ENABLE_REDIS", "true").lower() == "true"
                
                _cache_instance = SemanticCacheManager(
                    max_size=max_size,
                    ttl_seconds=ttl,
                    max_response_size=max_response_size,
                    enable_redis=enable_redis
                )
                logger.info(
                    f"Initialized global semantic cache manager "
                    f"(TTL={ttl}s, max_size={max_size}, max_response_size={max_response_size} bytes, "
                    f"redis_enabled={enable_redis})"
                )
    
    return _cache_instance


__all__ = ["SemanticCacheManager", "get_semantic_cache_manager"]

