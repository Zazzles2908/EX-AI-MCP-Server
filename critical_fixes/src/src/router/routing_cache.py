"""
Routing Cache Implementation
Performance optimization with TTL-based caching for EX-AI-MCP-Server
"""

import os
import time
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies for different types of routing decisions"""
    NO_CACHE = "no_cache"
    SHORT_TTL = "short_ttl"  # 5 minutes
    MEDIUM_TTL = "medium_ttl"  # 30 minutes  
    LONG_TTL = "long_ttl"  # 2 hours
    PERMANENT = "permanent"  # Never expires


@dataclass
class CacheEntry:
    """Cache entry with TTL and metadata"""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0.0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return time.time() - self.timestamp > self.ttl
    
    def get_age(self) -> float:
        """Get age of cache entry in seconds"""
        return time.time() - self.timestamp
    
    def access(self) -> Any:
        """Access the cache entry and update statistics"""
        self.access_count += 1
        self.last_access = time.time()
        return self.data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'data': self.data,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'access_count': self.access_count,
            'last_access': self.last_access,
            'is_expired': self.is_expired(),
            'age_seconds': self.get_age()
        }


class RoutingCache:
    """TTL-based routing decision cache"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize routing cache
        
        Args:
            default_ttl: Default TTL in seconds (5 minutes)
            max_size: Maximum number of cache entries
        """
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, CacheEntry] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_cleaned': 0,
            'total_entries': 0,
            'cache_size': 0
        }
        self._default_strategies = {
            'model_selection': CacheStrategy.MEDIUM_TTL,
            'provider_status': CacheStrategy.SHORT_TTL,
            'routing_rules': CacheStrategy.LONG_TTL,
            'performance_metrics': CacheStrategy.MEDIUM_TTL,
            'user_preferences': CacheStrategy.PERMANENT
        }
        
        logger.info(f"Initialized routing cache with TTL={default_ttl}s, max_size={max_size}")
    
    def _get_cache_key(self, category: str, identifier: str) -> str:
        """Generate cache key from category and identifier"""
        return f"{category}:{identifier}"
    
    def _get_strategy_ttl(self, category: str, strategy: Optional[CacheStrategy] = None) -> int:
        """Get TTL for a cache strategy"""
        if strategy == CacheStrategy.NO_CACHE:
            return 0
        elif strategy == CacheStrategy.SHORT_TTL:
            return 5 * 60  # 5 minutes
        elif strategy == CacheStrategy.MEDIUM_TTL:
            return 30 * 60  # 30 minutes
        elif strategy == CacheStrategy.LONG_TTL:
            return 2 * 60 * 60  # 2 hours
        elif strategy == CacheStrategy.PERMANENT:
            return 24 * 60 * 60 * 365  # 1 year (effectively permanent)
        else:
            # Use default strategy for category
            default_strategy = self._default_strategies.get(category, CacheStrategy.MEDIUM_TTL)
            return self._get_strategy_ttl(category, default_strategy)
    
    def _cleanup_expired(self):
        """Remove expired cache entries"""
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self._stats['expired_cleaned'] += 1
        
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _evict_lru(self):
        """Evict least recently used entries when cache is full"""
        if len(self._cache) <= self.max_size:
            return
        
        # Sort by last access time
        sorted_entries = sorted(
            self._cache.items(),
            key=lambda x: x[1].last_access
        )
        
        # Remove oldest entries
        entries_to_remove = len(self._cache) - self.max_size
        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del self._cache[key]
            self._stats['evictions'] += 1
        
        logger.debug(f"Evicted {entries_to_remove} LRU cache entries")
    
    def get(
        self, 
        category: str, 
        identifier: str,
        strategy: Optional[CacheStrategy] = None
    ) -> Optional[Any]:
        """
        Get cached data
        
        Args:
            category: Cache category (e.g., 'model_selection', 'provider_status')
            identifier: Unique identifier for the cached item
            strategy: Cache strategy to use
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._get_cache_key(category, identifier)
        entry = self._cache.get(cache_key)
        
        if entry is None:
            self._stats['misses'] += 1
            return None
        
        if entry.is_expired():
            del self._cache[cache_key]
            self._stats['misses'] += 1
            return None
        
        # Update statistics
        self._stats['hits'] += 1
        data = entry.access()
        
        logger.debug(f"Cache hit for {cache_key} (age: {entry.get_age():.1f}s)")
        return data
    
    def set(
        self,
        category: str,
        identifier: str,
        data: Any,
        strategy: Optional[CacheStrategy] = None,
        custom_ttl: Optional[int] = None
    ) -> bool:
        """
        Set cached data
        
        Args:
            category: Cache category
            identifier: Unique identifier
            data: Data to cache
            strategy: Cache strategy
            custom_ttl: Custom TTL in seconds
            
        Returns:
            True if successfully cached
        """
        cache_key = self._get_cache_key(category, identifier)
        
        # Determine TTL
        if custom_ttl is not None:
            ttl = custom_ttl
        else:
            ttl = self._get_strategy_ttl(category, strategy)
        
        # Don't cache if TTL is 0 (no-cache strategy)
        if ttl == 0:
            logger.debug(f"Not caching {cache_key} (no-cache strategy)")
            return False
        
        # Clean up expired entries if cache is getting full
        if len(self._cache) > self.max_size * 0.8:
            self._cleanup_expired()
        
        # Evict LRU if still over capacity
        if len(self._cache) >= self.max_size:
            self._evict_lru()
        
        # Create cache entry
        entry = CacheEntry(
            data=data,
            timestamp=time.time(),
            ttl=ttl
        )
        
        self._cache[cache_key] = entry
        self._stats['total_entries'] += 1
        self._stats['cache_size'] = len(self._cache)
        
        logger.debug(f"Cached {cache_key} with TTL={ttl}s")
        return True
    
    def delete(self, category: str, identifier: str) -> bool:
        """Delete a specific cache entry"""
        cache_key = self._get_cache_key(category, identifier)
        if cache_key in self._cache:
            del self._cache[cache_key]
            logger.debug(f"Deleted cache entry {cache_key}")
            return True
        return False
    
    def clear_category(self, category: str) -> int:
        """Clear all entries in a specific category"""
        keys_to_delete = [
            key for key in self._cache.keys()
            if key.startswith(f"{category}:")
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
        
        logger.info(f"Cleared {len(keys_to_delete)} cache entries from category '{category}'")
        return len(keys_to_delete)
    
    def clear_all(self):
        """Clear all cache entries"""
        self._cache.clear()
        logger.info("Cleared all cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = self._stats['hits'] / total_requests if total_requests > 0 else 0
        
        stats = {
            **self._stats,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_usage_percent': (len(self._cache) / self.max_size) * 100,
            'categories': {}
        }
        
        # Count entries by category
        for key in self._cache.keys():
            category = key.split(':')[0]
            if category not in stats['categories']:
                stats['categories'][category] = 0
            stats['categories'][category] += 1
        
        return stats
    
    def get_cached_categories(self) -> Dict[str, int]:
        """Get list of cached categories and their entry counts"""
        categories = {}
        for key in self._cache.keys():
            category = key.split(':')[0]
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def preload_common_entries(self):
        """Preload commonly accessed cache entries"""
        # Provider status cache (short TTL)
        provider_status_keys = ['available_providers', 'provider_capabilities']
        for key in provider_status_keys:
            self.set('provider_status', key, {'status': 'checking'}, CacheStrategy.SHORT_TTL)
        
        # Performance metrics (medium TTL)
        self.set('performance_metrics', 'current_load', {'requests_per_minute': 0}, CacheStrategy.MEDIUM_TTL)
        
        logger.info("Preloaded common cache entries")
    
    def save_to_file(self, filepath: str) -> bool:
        """Save cache to file (non-expired entries only)"""
        try:
            cache_data = {
                'timestamp': time.time(),
                'default_ttl': self.default_ttl,
                'max_size': self.max_size,
                'entries': {}
            }
            
            for key, entry in self._cache.items():
                if not entry.is_expired():
                    cache_data['entries'][key] = entry.to_dict()
            
            with open(filepath, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(cache_data['entries'])} cache entries to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save cache to {filepath}: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """Load cache from file"""
        try:
            with open(filepath, 'r') as f:
                cache_data = json.load(f)
            
            loaded_entries = 0
            for key, entry_data in cache_data.get('entries', {}).items():
                # Skip expired entries
                if time.time() - entry_data['timestamp'] > entry_data['ttl']:
                    continue
                
                entry = CacheEntry(
                    data=entry_data['data'],
                    timestamp=entry_data['timestamp'],
                    ttl=entry_data['ttl'],
                    access_count=entry_data.get('access_count', 0),
                    last_access=entry_data.get('last_access', 0)
                )
                
                self._cache[key] = entry
                loaded_entries += 1
            
            logger.info(f"Loaded {loaded_entries} cache entries from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load cache from {filepath}: {e}")
            return False


# Global cache instance
_cache_instance: Optional[RoutingCache] = None


def get_routing_cache(default_ttl: int = 300, max_size: int = 1000) -> RoutingCache:
    """Get the global routing cache instance (singleton pattern)"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RoutingCache(default_ttl, max_size)
        logger.info("Initialized global routing cache")
    return _cache_instance


def reset_cache():
    """Reset the global cache instance (for testing)"""
    global _cache_instance
    _cache_instance = None
    logger.info("Reset global routing cache")


# Export main classes and functions
__all__ = [
    'CacheStrategy',
    'CacheEntry',
    'RoutingCache',
    'get_routing_cache',
    'reset_cache'
]