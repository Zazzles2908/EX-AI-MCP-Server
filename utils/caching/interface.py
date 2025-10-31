"""
Cache Interface for EXAI MCP Server

Unified abstract interface for all caching implementations.
Provides consistent API across different caching strategies.

Implementations:
- MemoryLRUTTL: Simple L1-only cache for session continuity
- BaseCacheManager: Multi-layer cache (L1+L2+L3) for distributed caching

Created: 2025-10-31 (Phase 2: Caching Unification)
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, Dict


class CacheInterface(ABC):
    """
    Abstract base class for all cache implementations.
    
    Provides unified API for caching operations across different strategies.
    All cache implementations should inherit from this interface.
    
    Design Principles:
    - Simple, consistent API
    - Optional TTL override per operation
    - Statistics tracking
    - Thread-safe operations (implementation-specific)
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override (seconds). If None, uses default TTL.
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete value from cache.
        
        Args:
            key: Cache key to delete
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all entries from cache.
        """
        pass
    
    @abstractmethod
    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics (implementation-specific)
            
        Common stats:
        - hits: Number of cache hits
        - misses: Number of cache misses
        - size: Current cache size
        - max_size: Maximum cache size
        """
        pass


class SimpleCacheInterface(ABC):
    """
    Simplified cache interface for basic use cases.
    
    Subset of CacheInterface with only essential operations.
    Used by MemoryLRUTTL for backward compatibility.
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def stats(self) -> Tuple[int, int]:
        """
        Get basic cache statistics.
        
        Returns:
            Tuple of (current_size, max_size)
        """
        pass


__all__ = [
    "CacheInterface",
    "SimpleCacheInterface",
]

