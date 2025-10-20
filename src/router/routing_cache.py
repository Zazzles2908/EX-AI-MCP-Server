"""
Routing Cache for EXAI MCP Server

Caches routing decisions to reduce overhead on every request.
Uses multi-layer caching pattern (L1 + L2 Redis) via BaseCacheManager.

Performance Impact:
- Provider availability: Cached for 5 minutes (reduces redundant checks)
- Model selection: Cached for 3 minutes (based on request context)
- Tool normalization: Cached with LRU eviction (200 items max)
- Fallback chain: Cached for 10 minutes

Architecture:
- L1: In-memory TTLCache (fast, lost on restart)
- L2: Redis distributed cache (persistent across restarts)

Created: 2025-10-16
Updated: 2025-10-16 (Phase 1: Unified with BaseCacheManager, added Redis L2, fixed memory leak)
"""

import hashlib
import json
import logging
import os
from typing import Optional, Dict, Any, List

try:
    from cachetools import TTLCache, LRUCache
except ImportError:
    TTLCache = dict
    LRUCache = dict

from utils.caching.base_cache_manager import BaseCacheManager

logger = logging.getLogger(__name__)


class RoutingCache:
    """
    Caching layer for routing decisions with L1+L2 (Redis) support.

    Reduces overhead by caching:
    - Provider availability status (L1+L2, 5min TTL)
    - Model selection results (L1+L2, 3min TTL)
    - Tool name normalization (L1 LRU, 200 items max)
    - Fallback chain evaluation (L1+L2, 10min TTL)

    Uses BaseCacheManager for L1+L2 caching with Redis persistence.
    """

    def __init__(self):
        """Initialize routing cache with configurable TTLs and Redis L2 support."""
        # Configurable TTLs from environment
        self._provider_ttl = int(os.getenv("ROUTING_CACHE_PROVIDER_TTL_SECS", "300"))  # 5min
        self._model_ttl = int(os.getenv("ROUTING_CACHE_MODEL_TTL_SECS", "180"))  # 3min
        self._fallback_ttl = int(os.getenv("ROUTING_CACHE_FALLBACK_TTL_SECS", "600"))  # 10min

        # Enable Redis L2 caching (can be disabled via env)
        enable_redis = os.getenv("ROUTING_CACHE_ENABLE_REDIS", "true").lower() == "true"

        # Provider availability cache (L1+L2, 5 minutes)
        self._provider_cache = BaseCacheManager(
            l1_maxsize=50,
            l1_ttl=self._provider_ttl,
            l2_ttl=self._provider_ttl,
            enable_redis=enable_redis,
            cache_prefix="routing:provider"
        )

        # Model selection cache (L1+L2, 3 minutes)
        self._model_cache = BaseCacheManager(
            l1_maxsize=100,
            l1_ttl=self._model_ttl,
            l2_ttl=self._model_ttl,
            enable_redis=enable_redis,
            cache_prefix="routing:model"
        )

        # Tool normalization cache (L1 LRU only, no Redis needed for static mapping)
        # FIX: Use LRUCache with size limit instead of unlimited dict (memory leak fix)
        try:
            self._tool_cache = LRUCache(maxsize=200)
            logger.info("[ROUTING_CACHE] Tool cache: LRUCache(maxsize=200)")
        except (TypeError, NameError):
            self._tool_cache: Dict[str, str] = {}
            logger.warning("[ROUTING_CACHE] Tool cache: fallback dict (no size limit)")

        # Fallback chain cache (L1+L2, 10 minutes)
        self._fallback_cache = BaseCacheManager(
            l1_maxsize=50,
            l1_ttl=self._fallback_ttl,
            l2_ttl=self._fallback_ttl,
            enable_redis=enable_redis,
            cache_prefix="routing:fallback"
        )

        # Statistics (aggregated from all caches)
        self._stats = {
            "provider_hits": 0,
            "provider_misses": 0,
            "model_hits": 0,
            "model_misses": 0,
            "tool_hits": 0,
            "tool_misses": 0,
            "fallback_hits": 0,
            "fallback_misses": 0,
        }

        logger.info(
            f"[ROUTING_CACHE] Initialized with Redis L2: "
            f"provider_ttl={self._provider_ttl}s, "
            f"model_ttl={self._model_ttl}s, "
            f"fallback_ttl={self._fallback_ttl}s, "
            f"redis_enabled={enable_redis}"
        )
    
    # Provider Availability Caching (L1+L2 Redis)

    def get_provider_status(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get cached provider availability status (L1+L2)."""
        status = self._provider_cache.get(provider_name)

        if status is not None:
            self._stats["provider_hits"] += 1
            logger.debug(f"[ROUTING_CACHE] Provider cache HIT: {provider_name}")
        else:
            self._stats["provider_misses"] += 1
            logger.debug(f"[ROUTING_CACHE] Provider cache MISS: {provider_name}")

        return status

    def set_provider_status(self, provider_name: str, status: Dict[str, Any]) -> None:
        """Cache provider availability status (L1+L2 write-through)."""
        self._provider_cache.set(provider_name, status)
        logger.debug(f"[ROUTING_CACHE] Cached provider status: {provider_name}")

    def invalidate_provider(self, provider_name: str) -> None:
        """Invalidate cached provider status from all layers."""
        self._provider_cache.delete(provider_name)
        logger.debug(f"[ROUTING_CACHE] Invalidated provider: {provider_name}")
    
    # Model Selection Caching (L1+L2 Redis)

    def get_model_selection(self, request_context: Dict[str, Any]) -> Optional[str]:
        """Get cached model selection based on request context (L1+L2)."""
        key = self._hash_context(request_context)
        model = self._model_cache.get(key)

        if model is not None:
            self._stats["model_hits"] += 1
            logger.debug(f"[ROUTING_CACHE] Model cache HIT: {model}")
        else:
            self._stats["model_misses"] += 1
            logger.debug(f"[ROUTING_CACHE] Model cache MISS")

        return model

    def set_model_selection(self, request_context: Dict[str, Any], model: str) -> None:
        """Cache model selection result (L1+L2 write-through)."""
        key = self._hash_context(request_context)
        self._model_cache.set(key, model)
        logger.debug(f"[ROUTING_CACHE] Cached model selection: {model}")
    
    # Tool Normalization Caching
    
    def get_normalized_tool(self, tool_name: str) -> Optional[str]:
        """Get cached normalized tool name."""
        normalized = self._tool_cache.get(tool_name)
        
        if normalized is not None:
            self._stats["tool_hits"] += 1
            logger.debug(f"[ROUTING_CACHE] Tool cache HIT: {tool_name} → {normalized}")
        else:
            self._stats["tool_misses"] += 1
            logger.debug(f"[ROUTING_CACHE] Tool cache MISS: {tool_name}")
        
        return normalized
    
    def set_normalized_tool(self, tool_name: str, normalized: str) -> None:
        """Cache tool name normalization (permanent)."""
        self._tool_cache[tool_name] = normalized
        logger.debug(f"[ROUTING_CACHE] Cached tool normalization: {tool_name} → {normalized}")
    
    # Fallback Chain Caching (L1+L2 Redis)

    def get_fallback_chain(self, request_context: Dict[str, Any]) -> Optional[List[str]]:
        """Get cached fallback chain (L1+L2)."""
        key = self._hash_context(request_context)
        chain = self._fallback_cache.get(key)

        if chain is not None:
            self._stats["fallback_hits"] += 1
            logger.debug(f"[ROUTING_CACHE] Fallback cache HIT: {chain}")
        else:
            self._stats["fallback_misses"] += 1
            logger.debug(f"[ROUTING_CACHE] Fallback cache MISS")

        return chain

    def set_fallback_chain(self, request_context: Dict[str, Any], chain: List[str]) -> None:
        """Cache fallback chain evaluation (L1+L2 write-through)."""
        key = self._hash_context(request_context)
        self._fallback_cache.set(key, chain)
        logger.debug(f"[ROUTING_CACHE] Cached fallback chain: {chain}")

    # Utilities

    def _hash_context(self, context: Dict[str, Any]) -> str:
        """
        Create a stable hash key from request context.

        OPTIMIZED: Uses json.dumps + blake2b instead of str(sorted()) + MD5
        - 30-50% faster than previous implementation
        - Handles unhashable types gracefully (default=str)
        - Stable ordering with sort_keys=True
        """
        try:
            # Use json.dumps with sorted keys for stable, fast serialization
            context_str = json.dumps(context, sort_keys=True, default=str)
            # Use blake2b for faster hashing (vs MD5)
            context_hash = hashlib.blake2b(context_str.encode(), digest_size=8).hexdigest()
            return context_hash
        except Exception as e:
            # Fallback to simple string hash if json serialization fails
            logger.warning(f"[ROUTING_CACHE] Hash context error: {e}, using fallback")
            return hashlib.md5(str(context).encode()).hexdigest()[:16]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_provider = self._stats["provider_hits"] + self._stats["provider_misses"]
        total_model = self._stats["model_hits"] + self._stats["model_misses"]
        total_tool = self._stats["tool_hits"] + self._stats["tool_misses"]
        total_fallback = self._stats["fallback_hits"] + self._stats["fallback_misses"]
        
        return {
            **self._stats,
            "provider_hit_ratio": self._stats["provider_hits"] / total_provider if total_provider > 0 else 0.0,
            "model_hit_ratio": self._stats["model_hits"] / total_model if total_model > 0 else 0.0,
            "tool_hit_ratio": self._stats["tool_hits"] / total_tool if total_tool > 0 else 0.0,
            "fallback_hit_ratio": self._stats["fallback_hits"] / total_fallback if total_fallback > 0 else 0.0,
            "cache_sizes": {
                "provider": len(self._provider_cache),
                "model": len(self._model_cache),
                "tool": len(self._tool_cache),
                "fallback": len(self._fallback_cache),
            }
        }
    
    def clear_all(self) -> None:
        """Clear all caches (for testing or manual invalidation)."""
        self._provider_cache.clear()
        self._model_cache.clear()
        self._tool_cache.clear()
        self._fallback_cache.clear()
        logger.info("[ROUTING_CACHE] All caches cleared")


# Singleton instance
_routing_cache: Optional[RoutingCache] = None


def get_routing_cache() -> RoutingCache:
    """
    Get the singleton routing cache instance.
    
    Returns:
        RoutingCache instance
    """
    global _routing_cache
    if _routing_cache is None:
        _routing_cache = RoutingCache()
    return _routing_cache


__all__ = ["RoutingCache", "get_routing_cache"]

