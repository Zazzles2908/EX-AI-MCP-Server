"""
Semantic Cache Factory for AI API Responses

PHASE 5 FIX (2025-11-01): Fixed import to use semantic_cache_manager.
The semantic_cache_legacy.py was deleted in Phase 2, causing import errors.

Usage:
    from utils.infrastructure.semantic_cache import get_semantic_cache

    cache = get_semantic_cache()
    cached = cache.get(prompt, model, temperature)
    if cached:
        return cached

    response = await call_ai_api(prompt, model, temperature)
    cache.set(prompt, model, response, temperature)
"""

import logging

logger = logging.getLogger(__name__)


def get_semantic_cache():
    """
    Get the global semantic cache instance (singleton pattern).

    Returns SemanticCacheManager (BaseCacheManager-based with L1+L2 Redis).
    This provides better performance and persistence compared to the old legacy implementation.

    Returns:
        SemanticCacheManager: Cache manager instance with L1 (memory) + L2 (Redis) support
    """
    from utils.infrastructure.semantic_cache_manager import get_semantic_cache_manager
    return get_semantic_cache_manager()


__all__ = ["get_semantic_cache"]

