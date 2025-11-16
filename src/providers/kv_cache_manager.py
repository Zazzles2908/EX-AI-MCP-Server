"""
KV Cache Manager Implementation Based on Parallax Architectural Patterns

This module implements intelligent conversation context caching inspired by Parallax's
advanced KV cache management system. It provides:

1. Dynamic conversation context persistence
2. Intelligent cache eviction policies based on usage patterns
3. Memory-efficient storage for long conversations
4. Cache hit optimization and performance monitoring

Key Parallax-inspired features:
- Usage-based eviction (LRU with frequency tracking)
- Memory pressure handling
- Cache warming for frequently accessed contexts
- Performance metrics and optimization
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a single cache entry with metadata."""
    key: str
    value: Any
    timestamp: float
    last_accessed: float
    access_count: int = 1
    size_bytes: int = 0
    ttl: Optional[float] = None
    tags: Set[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl
    
    @property
    def age_seconds(self) -> float:
        """Get the age of this cache entry in seconds."""
        return time.time() - self.timestamp
    
    @property
    def access_frequency(self) -> float:
        """Calculate access frequency (accesses per second)."""
        if self.age_seconds == 0:
            return float('inf')
        return self.access_count / self.age_seconds


class ParallaxKVCacheManager:
    """
    Intelligent KV cache manager inspired by Parallax architecture.
    
    Features:
    - LRU eviction with frequency tracking
    - Memory pressure management
    - TTL support with automatic cleanup
    - Cache warming for performance
    - Comprehensive metrics and monitoring
    """
    
    def __init__(
        self,
        max_size_mb: int = 100,
        max_entries: int = 10000,
        default_ttl: float = 3600,  # 1 hour
        cleanup_interval: float = 300,  # 5 minutes
        enable_metrics: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize the KV cache manager.
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            max_entries: Maximum number of cache entries
            default_ttl: Default TTL for new entries (seconds)
            cleanup_interval: Interval between cleanup operations (seconds)
            enable_metrics: Enable performance metrics collection
            cache_dir: Optional directory for persistent cache storage
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self.cleanup_interval = cleanup_interval
        self.enable_metrics = enable_metrics
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Cache storage
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order = OrderedDict()  # For LRU tracking
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)  # Tag-based lookup
        
        # Performance metrics
        self._metrics = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired_cleanups': 0,
            'memory_evictions': 0,
            'cache_warmings': 0,
            'total_size_bytes': 0,
            'average_entry_size': 0,
            'hit_rate': 0.0
        } if enable_metrics else None
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._start_background_cleanup()
        
        logger.info(
            f"ParallaxKVCache initialized: {max_size_mb}MB, {max_entries} entries, "
            f"TTL={default_ttl}s, cleanup={cleanup_interval}s"
        )

    def _start_background_cleanup(self):
        """Start background cleanup task."""
        if self.cleanup_interval > 0:
            self._cleanup_task = asyncio.create_task(self._background_cleanup())

    async def _background_cleanup(self):
        """Background task for periodic cache cleanup."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_expired()
                await self._optimize_memory_usage()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")

    async def _cleanup_expired(self):
        """Remove expired cache entries."""
        if not self._cache:
            return
            
        expired_keys = []
        current_time = time.time()
        
        for key, entry in self._cache.items():
            if entry.is_expired:
                expired_keys.append(key)
        
        if expired_keys:
            for key in expired_keys:
                del self._cache[key]
                del self._access_order[key]
                
                # Update tag index
                for tag in self._cache[key].tags if hasattr(self._cache[key], 'tags') else set():
                    if tag in self._tag_index:
                        self._tag_index[tag].discard(key)
                        if not self._tag_index[tag]:
                            del self._tag_index[tag]
            
            if self._metrics:
                self._metrics['expired_cleanups'] += len(expired_keys)
            
            logger.debug(f"Cleaned up {len(expired_keys)} expired entries")

    async def _optimize_memory_usage(self):
        """Optimize memory usage by evicting least valuable entries."""
        current_size = self._calculate_total_size()
        
        if current_size <= self.max_size_bytes and len(self._cache) <= self.max_entries:
            return
        
        # Calculate eviction priority based on multiple factors
        eviction_candidates = []
        
        for key, entry in self._cache.items():
            # Lower priority = higher eviction preference
            priority_score = self._calculate_eviction_priority(entry)
            eviction_candidates.append((priority_score, key, entry))
        
        # Sort by priority (ascending - lowest priority first)
        eviction_candidates.sort(key=lambda x: x[0])
        
        # Evict entries until we're under limits
        target_size = int(self.max_size_bytes * 0.9)  # 90% of max to avoid frequent evictions
        target_entries = int(self.max_entries * 0.9)
        
        evicted_count = 0
        evicted_size = 0
        
        for priority_score, key, entry in eviction_candidates:
            if (current_size - evicted_size <= target_size and 
                len(self._cache) - evicted_count <= target_entries):
                break
                
            del self._cache[key]
            del self._access_order[key]
            evicted_size += entry.size_bytes
            evicted_count += 1
            
            # Update tag index
            for tag in entry.tags:
                self._tag_index[tag].discard(key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]
        
        if evicted_count > 0:
            if self._metrics:
                self._metrics['memory_evictions'] += evicted_count
                self._metrics['total_size_bytes'] = current_size - evicted_size
            
            logger.debug(f"Memory optimization: evicted {evicted_count} entries, "
                        f"freed {evicted_size} bytes")

    def _calculate_eviction_priority(self, entry: CacheEntry) -> float:
        """
        Calculate eviction priority for a cache entry.
        
        Lower scores = higher eviction preference.
        
        Factors:
        - Access frequency (more frequent = lower score)
        - Age (older = higher score)
        - Size (larger = higher score)
        - TTL remaining (more remaining = lower score)
        """
        # Access frequency (normalized)
        freq_score = 1.0 / (1.0 + entry.access_frequency)
        
        # Age factor (older entries have higher eviction preference)
        age_score = min(entry.age_seconds / (24 * 3600), 1.0)  # Cap at 1 day
        
        # Size factor (larger entries have higher eviction preference)
        size_score = min(entry.size_bytes / (1024 * 1024), 1.0)  # Cap at 1MB
        
        # TTL factor (entries with more TTL remaining have lower eviction preference)
        ttl_score = 0.0
        if entry.ttl and entry.ttl > 0:
            ttl_remaining = entry.ttl - (time.time() - entry.timestamp)
            ttl_score = max(0.0, ttl_remaining / entry.ttl)
        
        # Combined priority score (lower = more likely to evict)
        priority_score = (freq_score * 0.4 + age_score * 0.3 + 
                         size_score * 0.2 + (1.0 - ttl_score) * 0.1)
        
        return priority_score

    def _calculate_total_size(self) -> int:
        """Calculate total size of all cache entries."""
        return sum(entry.size_bytes for entry in self._cache.values())

    def _estimate_size(self, value: Any) -> int:
        """Estimate the size of a value in bytes."""
        try:
            return len(json.dumps(value, default=str).encode('utf-8'))
        except Exception:
            return 1024  # Default estimate

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        entry = self._cache.get(key)
        
        if entry is None:
            if self._metrics:
                self._metrics['misses'] += 1
            return default
        
        if entry.is_expired:
            # Remove expired entry
            del self._cache[key]
            del self._access_order[key]
            
            if self._metrics:
                self._metrics['misses'] += 1
            
            return default
        
        # Update access information
        entry.last_accessed = time.time()
        entry.access_count += 1
        self._access_order.move_to_end(key)
        
        if self._metrics:
            self._metrics['hits'] += 1
            
        return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[float] = None,
        tags: Optional[Set[str]] = None
    ) -> bool:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None for default)
            tags: Optional tags for this entry
            
        Returns:
            True if successfully cached, False otherwise
        """
        ttl = ttl or self.default_ttl
        tags = tags or set()
        
        current_time = time.time()
        size_bytes = self._estimate_size(value)
        
        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=value,
            timestamp=current_time,
            last_accessed=current_time,
            size_bytes=size_bytes,
            ttl=ttl,
            tags=tags
        )
        
        # Check if we need to evict entries to make space
        await self._make_space(size_bytes, len(tags))
        
        # Store the entry
        self._cache[key] = entry
        self._access_order[key] = True
        
        # Update tag index
        for tag in tags:
            self._tag_index[tag].add(key)
        
        if self._metrics:
            self._metrics['total_size_bytes'] = self._calculate_total_size()
        
        return True

    async def _make_space(self, required_bytes: int, tag_count: int = 0):
        """Make space in cache for a new entry."""
        current_size = self._calculate_total_size()
        
        if current_size + required_bytes <= self.max_size_bytes and len(self._cache) < self.max_entries:
            return
        
        # Evict entries until we have enough space
        while ((current_size + required_bytes > self.max_size_bytes or 
                len(self._cache) >= self.max_entries) and self._cache):
            
            # Evict least valuable entry
            lru_key = next(iter(self._access_order))
            lru_entry = self._cache[lru_key]
            
            del self._cache[lru_key]
            del self._access_order[lru_key]
            
            # Update tag index
            for tag in lru_entry.tags:
                self._tag_index[tag].discard(lru_key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]
            
            current_size -= lru_entry.size_bytes
            
            if self._metrics:
                self._metrics['evictions'] += 1

    async def delete(self, key: str) -> bool:
        """Delete a key from the cache."""
        entry = self._cache.get(key)
        if entry:
            del self._cache[key]
            del self._access_order[key]
            
            # Update tag index
            for tag in entry.tags:
                self._tag_index[tag].discard(key)
                if not self._tag_index[tag]:
                    del self._tag_index[tag]
            
            if self._metrics:
                self._metrics['total_size_bytes'] = self._calculate_total_size()
            
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache and is not expired."""
        entry = self._cache.get(key)
        return entry is not None and not entry.is_expired

    async def get_by_tags(self, tags: Set[str]) -> Dict[str, Any]:
        """Get all entries that have all the specified tags."""
        if not tags:
            return {}
        
        # Find entries that have all specified tags
        matching_keys = None
        for tag in tags:
            tag_keys = self._tag_index.get(tag, set())
            if matching_keys is None:
                matching_keys = tag_keys.copy()
            else:
                matching_keys &= tag_keys
        
        if not matching_keys:
            return {}
        
        # Return non-expired entries
        result = {}
        current_time = time.time()
        
        for key in matching_keys:
            entry = self._cache.get(key)
            if entry and not entry.is_expired:
                result[key] = entry.value
        
        return result

    async def clear_tags(self, tags: Set[str]) -> int:
        """Clear all entries that have any of the specified tags."""
        if not tags:
            return 0
        
        keys_to_delete = set()
        for tag in tags:
            keys_to_delete.update(self._tag_index.get(tag, set()))
        
        deleted_count = 0
        for key in keys_to_delete:
            if await self.delete(key):
                deleted_count += 1
        
        return deleted_count

    async def clear_all(self):
        """Clear all entries from the cache."""
        self._cache.clear()
        self._access_order.clear()
        self._tag_index.clear()
        
        if self._metrics:
            self._metrics['total_size_bytes'] = 0

    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics."""
        if not self.enable_metrics or not self._metrics:
            return {}
        
        # Calculate hit rate
        total_requests = self._metrics['hits'] + self._metrics['misses']
        if total_requests > 0:
            self._metrics['hit_rate'] = self._metrics['hits'] / total_requests
        
        # Calculate average entry size
        if self._cache:
            total_size = sum(entry.size_bytes for entry in self._cache.values())
            self._metrics['average_entry_size'] = total_size / len(self._cache)
        
        # Current cache statistics
        current_stats = {
            'current_size_mb': self._calculate_total_size() / (1024 * 1024),
            'current_entry_count': len(self._cache),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'max_entries': self.max_entries
        }
        
        return {**self._metrics, **current_stats}

    async def warm_cache(self, warming_data: Dict[str, Dict[str, Any]]):
        """
        Warm the cache with frequently accessed data.
        
        Args:
            warming_data: Dictionary mapping keys to {value, ttl, tags} dictionaries
        """
        warmed_count = 0
        for key, data in warming_data.items():
            try:
                value = data.get('value')
                ttl = data.get('ttl')
                tags = data.get('tags', set())
                
                if value is not None:
                    await self.set(key, value, ttl, tags)
                    warmed_count += 1
            except Exception as e:
                logger.warning(f"Failed to warm cache for key {key}: {e}")
        
        if self._metrics:
            self._metrics['cache_warmings'] += warmed_count
        
        logger.info(f"Cache warming completed: {warmed_count} entries")

    async def close(self):
        """Close the cache manager and cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    def __len__(self) -> int:
        """Return the number of cached entries."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if a key is in the cache."""
        return key in self._cache

    def __repr__(self) -> str:
        """String representation of the cache manager."""
        return (f"ParallaxKVCacheManager("
                f"entries={len(self._cache)}, "
                f"size={self._calculate_total_size() / (1024*1024):.1f}MB, "
                f"hit_rate={self.get_metrics().get('hit_rate', 0):.2%})")


# Global cache instance
_global_cache: Optional[ParallaxKVCacheManager] = None


async def get_kv_cache() -> ParallaxKVCacheManager:
    """Get the global KV cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ParallaxKVCacheManager(
            max_size_mb=100,
            max_entries=10000,
            default_ttl=3600,  # 1 hour
            cleanup_interval=300,  # 5 minutes
            enable_metrics=True
        )
    return _global_cache


async def close_kv_cache():
    """Close the global KV cache instance."""
    global _global_cache
    if _global_cache:
        await _global_cache.close()
        _global_cache = None
