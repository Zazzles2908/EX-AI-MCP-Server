"""
Semantic Cache Factory for AI API Responses

This module provides a factory function that returns the appropriate semantic cache
implementation based on feature flags.

Migration Strategy:
- Feature flag: SEMANTIC_CACHE_USE_BASE_MANAGER (default: false)
- Legacy implementation: SemanticCache (dict-based, L1-only)
- New implementation: SemanticCacheManager (BaseCacheManager-based, L1+L2 Redis)

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
    cache.set(prompt, model, response, temperature)

Created: 2025-10-31 (Phase 3: SemanticCache Migration)
"""

import logging
import os
from typing import Union

logger = logging.getLogger(__name__)


def get_semantic_cache() -> Union['SemanticCache', 'SemanticCacheManager']:
    """
    Get the global semantic cache instance (singleton pattern).
    
    Returns the appropriate implementation based on feature flags:
    - SEMANTIC_CACHE_USE_BASE_MANAGER=true: Returns SemanticCacheManager (new, L1+L2 Redis)
    - SEMANTIC_CACHE_USE_BASE_MANAGER=false: Returns SemanticCache (legacy, L1-only)
    
    Returns:
        Semantic cache instance (either legacy or new implementation)
    """
    use_base_manager = os.getenv('SEMANTIC_CACHE_USE_BASE_MANAGER', 'false').lower() == 'true'
    
    if use_base_manager:
        # New implementation: BaseCacheManager-based with L2 Redis
        from utils.infrastructure.semantic_cache_manager import get_semantic_cache_manager
        logger.info("Using new SemanticCacheManager (BaseCacheManager-based, L1+L2 Redis)")
        return get_semantic_cache_manager()
    else:
        # Legacy implementation: dict-based, L1-only
        from utils.infrastructure.semantic_cache_legacy import get_semantic_cache as get_legacy_cache
        logger.debug("Using legacy SemanticCache (dict-based, L1-only)")
        return get_legacy_cache()


# Re-export for backward compatibility
__all__ = ["get_semantic_cache"]

