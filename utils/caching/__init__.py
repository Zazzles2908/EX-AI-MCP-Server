"""
Caching utilities for EXAI MCP Server

Provides unified caching abstractions for multi-layer caching (L1 + L2 + L3).

Phase 2 Update (2025-10-31): Added CacheInterface for unified API
"""

from .interface import CacheInterface, SimpleCacheInterface
from .base_cache_manager import BaseCacheManager

__all__ = [
    "CacheInterface",
    "SimpleCacheInterface",
    "BaseCacheManager",
]

