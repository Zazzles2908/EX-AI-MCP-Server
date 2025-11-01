"""
Base Cache Manager for EXAI MCP Server

Unified caching abstraction supporting multi-layer caching (L1 + L2 + optional L3).
Used by both routing cache and conversation cache to eliminate duplication.

Implements CacheInterface for unified caching API.

Architecture:
- L1: In-memory TTLCache (fastest, configurable TTL and size)
- L2: Redis distributed cache (fast, persistent across restarts)
- L3: Optional persistent storage (Supabase, database, etc.)

Performance Benefits:
- L1 hit: <1ms (in-memory)
- L2 hit: 1-5ms (Redis)
- L3 hit: 10-50ms (network call)
- Cache miss: Full retrieval + population

Created: 2025-10-16
Updated: 2025-10-31 (Phase 2: Implements CacheInterface)
"""

import json
import logging
import os
import threading
from typing import Optional, Dict, Any, Callable, TYPE_CHECKING
from urllib.parse import urlparse

from utils.caching.interface import CacheInterface

if TYPE_CHECKING:
    from src.providers.base import ModelResponse

try:
    from cachetools import TTLCache, LRUCache
except ImportError:
    # Fallback to simple dict if cachetools not available
    TTLCache = dict
    LRUCache = dict

logger = logging.getLogger(__name__)


class BaseCacheManager(CacheInterface):
    """
    Base class for multi-layer caching with L1 (memory) + L2 (Redis) support.

    Implements CacheInterface for unified caching API.

    Subclasses should override:
    - _get_cache_prefix() - Return cache key prefix (e.g., "routing:", "conversation:")
    - _serialize_value() - Custom serialization if needed (default: JSON)
    - _deserialize_value() - Custom deserialization if needed (default: JSON)
    """
    
    _lock = threading.Lock()
    
    def __init__(
        self,
        l1_maxsize: int = 100,
        l1_ttl: int = 300,
        l2_ttl: int = 1800,
        enable_redis: bool = True,
        cache_prefix: str = "cache",
        max_response_size: Optional[int] = None
    ):
        """
        Initialize base cache manager.

        Args:
            l1_maxsize: Maximum items in L1 cache
            l1_ttl: L1 cache TTL in seconds
            l2_ttl: L2 (Redis) cache TTL in seconds
            enable_redis: Whether to enable L2 Redis caching
            cache_prefix: Prefix for cache keys (e.g., "routing", "conversation")
            max_response_size: Maximum size of a single response in bytes (optional, for semantic caching)
        """
        self._cache_prefix = cache_prefix
        self._l1_ttl = l1_ttl
        self._l2_ttl = l2_ttl
        self._enable_redis = enable_redis
        self._max_response_size = max_response_size
        
        # L1: In-memory cache
        try:
            self._l1_cache = TTLCache(maxsize=l1_maxsize, ttl=l1_ttl)
            logger.info(
                f"[{self._cache_prefix.upper()}_CACHE] L1 initialized: "
                f"TTLCache(maxsize={l1_maxsize}, ttl={l1_ttl}s)"
            )
        except TypeError:
            # Fallback if TTLCache not available
            self._l1_cache = {}
            logger.warning(f"[{self._cache_prefix.upper()}_CACHE] L1 using fallback dict (no TTL)")
        
        # L2: Redis cache (lazy initialization)
        self._redis_client = None
        self._redis_enabled = False
        
        # Statistics
        self._stats = {
            'l1_hits': 0,
            'l2_hits': 0,
            'misses': 0,
            'writes': 0,
            'errors': 0,
            'size_rejections': 0  # Track responses too large to cache
        }
        
        logger.info(f"[{self._cache_prefix.upper()}_CACHE] Base cache manager initialized")
    
    def _get_redis_client(self):
        """Lazy initialization of Redis client with connection pooling."""
        if self._redis_client is not None:
            return self._redis_client
        
        if not self._enable_redis:
            return None
        
        try:
            import redis
            
            # Get Redis URL from environment
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            
            # Parse Redis URL
            parsed = urlparse(redis_url)
            
            # Create Redis client with connection pooling
            self._redis_client = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip('/')) if parsed.path else 0,
                password=parsed.password,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self._redis_client.ping()
            self._redis_enabled = True

            # Log connection without exposing password (P0-9 security fix)
            logger.info(
                f"[{self._cache_prefix.upper()}_CACHE] L2 (Redis) connected: "
                f"{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/') if parsed.path else 0}"
            )
            
            return self._redis_client
            
        except Exception as e:
            logger.warning(
                f"[{self._cache_prefix.upper()}_CACHE] L2 (Redis) unavailable: {e}. "
                "Falling back to L1 only."
            )
            self._redis_enabled = False
            return None
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self._cache_prefix}:{key}"
    
    def _serialize_value(self, value: Any) -> str:
        """
        Serialize value for Redis storage with ModelResponse support.

        Handles:
        - ModelResponse objects (via to_dict method)
        - Other dataclasses (generic conversion)
        - Primitive types (standard JSON)

        Returns:
            JSON string representation of value
        """
        # Handle ModelResponse objects - explicit type check first
        # Phase 6.3 Fix (2025-11-01): Added explicit type check to ensure proper detection
        if value.__class__.__name__ == 'ModelResponse':
            if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
                return json.dumps(value.to_dict())
            else:
                # Fallback: ModelResponse without to_dict method (shouldn't happen)
                logger.error(f"[{self._cache_prefix.upper()}_CACHE] ModelResponse missing to_dict method!")

        # Handle other objects with to_dict method
        if hasattr(value, 'to_dict') and callable(getattr(value, 'to_dict')):
            return json.dumps(value.to_dict())

        # Handle other dataclasses
        if hasattr(value, '__dataclass_fields__'):
            # Convert dataclass to dict, handling nested objects
            result = {}
            for field_name, field_def in value.__dataclass_fields__.items():
                field_value = getattr(value, field_name)

                # Handle enums
                if hasattr(field_value, 'value'):
                    result[field_name] = field_value.value
                # Handle nested dataclasses
                elif hasattr(field_value, '__dataclass_fields__'):
                    result[field_name] = self._serialize_dataclass_to_dict(field_value)
                else:
                    result[field_name] = field_value

            # Add type marker for deserialization
            result["__type__"] = value.__class__.__name__
            return json.dumps(result)

        # Default JSON serialization for primitive types
        return json.dumps(value)

    def _deserialize_value(self, data: str) -> Any:
        """
        Deserialize value from Redis with ModelResponse support.

        Handles:
        - ModelResponse objects (via from_dict method)
        - Other typed objects (basic reconstruction)
        - Primitive types (standard JSON)
        - Backward compatibility (legacy cached data)

        Returns:
            Deserialized value
        """
        try:
            parsed = json.loads(data)

            # Handle typed objects with __type__ marker
            if isinstance(parsed, dict) and "__type__" in parsed:
                type_name = parsed["__type__"]

                # Handle ModelResponse
                if type_name == "ModelResponse":
                    from src.providers.base import ModelResponse
                    return ModelResponse.from_dict(parsed)

                # Handle other dataclasses (basic reconstruction)
                # Note: This is a fallback - specific types should have their own from_dict methods
                logger.warning(f"[{self._cache_prefix.upper()}_CACHE] Deserializing unknown type: {type_name}")
                # Remove type marker and return as dict
                parsed_copy = parsed.copy()
                del parsed_copy["__type__"]
                return parsed_copy

            return parsed

        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.warning(f"[{self._cache_prefix.upper()}_CACHE] Deserialization error: {e}")
            # Return raw data if deserialization fails
            return data

    def _serialize_dataclass_to_dict(self, obj: Any) -> dict[str, Any]:
        """
        Helper to serialize nested dataclasses to dict.

        Recursively handles nested dataclasses and enums.

        Args:
            obj: Dataclass instance to serialize

        Returns:
            Dictionary representation
        """
        result = {}
        for field_name, field_def in obj.__dataclass_fields__.items():
            field_value = getattr(obj, field_name)

            if hasattr(field_value, 'value'):
                result[field_name] = field_value.value
            elif hasattr(field_value, '__dataclass_fields__'):
                result[field_name] = self._serialize_dataclass_to_dict(field_value)
            else:
                result[field_name] = field_value

        return result
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (L1 -> L2 -> miss).
        
        Args:
            key: Cache key (without prefix)
            
        Returns:
            Cached value or None if not found
        """
        # L1 cache check
        if key in self._l1_cache:
            self._stats['l1_hits'] += 1
            logger.debug(f"[{self._cache_prefix.upper()}_CACHE] L1 HIT: {key}")
            return self._l1_cache[key]
        
        # L2 cache check (Redis)
        if self._enable_redis:
            redis_client = self._get_redis_client()
            if redis_client:
                try:
                    cached = redis_client.get(self._make_key(key))
                    if cached:
                        value = self._deserialize_value(cached)
                        # Populate L1 cache
                        self._l1_cache[key] = value
                        self._stats['l2_hits'] += 1
                        logger.debug(f"[{self._cache_prefix.upper()}_CACHE] L2 HIT: {key}")
                        return value
                except Exception as e:
                    logger.warning(f"[{self._cache_prefix.upper()}_CACHE] L2 read error: {e}")
                    self._stats['errors'] += 1
        
        # Cache miss
        self._stats['misses'] += 1
        logger.debug(f"[{self._cache_prefix.upper()}_CACHE] MISS: {key}")
        return None
    
    def _validate_response_size(self, response: Any) -> bool:
        """
        Validate response size against max_response_size limit.

        Args:
            response: Response to validate

        Returns:
            True if response size is acceptable, False otherwise
        """
        if self._max_response_size is None:
            return True

        import sys
        response_size = sys.getsizeof(response)
        if response_size > self._max_response_size:
            self._stats['size_rejections'] += 1
            logger.warning(
                f"[{self._cache_prefix.upper()}_CACHE] Response too large to cache: "
                f"{response_size} bytes (max: {self._max_response_size} bytes)"
            )
            return False

        return True

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache (write-through to L1 and L2).

        Args:
            key: Cache key (without prefix)
            value: Value to cache
            ttl: Optional TTL override (uses default if None)
        """
        # Validate response size if configured
        if not self._validate_response_size(value):
            return

        # L1 cache
        self._l1_cache[key] = value
        
        # L2 cache (Redis)
        if self._enable_redis:
            redis_client = self._get_redis_client()
            if redis_client:
                try:
                    redis_ttl = ttl if ttl is not None else self._l2_ttl
                    redis_client.setex(
                        self._make_key(key),
                        redis_ttl,
                        self._serialize_value(value)
                    )
                except Exception as e:
                    logger.warning(f"[{self._cache_prefix.upper()}_CACHE] L2 write error: {e}")
                    self._stats['errors'] += 1
        
        self._stats['writes'] += 1
        logger.debug(f"[{self._cache_prefix.upper()}_CACHE] WRITE: {key}")
    
    def delete(self, key: str) -> None:
        """
        Delete value from all cache layers.
        
        Args:
            key: Cache key (without prefix)
        """
        # L1 cache
        self._l1_cache.pop(key, None)
        
        # L2 cache (Redis)
        if self._enable_redis:
            redis_client = self._get_redis_client()
            if redis_client:
                try:
                    redis_client.delete(self._make_key(key))
                except Exception as e:
                    logger.warning(f"[{self._cache_prefix.upper()}_CACHE] L2 delete error: {e}")
                    self._stats['errors'] += 1
        
        logger.debug(f"[{self._cache_prefix.upper()}_CACHE] DELETE: {key}")
    
    def clear(self) -> None:
        """Clear all caches (L1 and L2)."""
        # L1 cache
        self._l1_cache.clear()
        
        # L2 cache (Redis) - delete all keys with prefix
        if self._enable_redis:
            redis_client = self._get_redis_client()
            if redis_client:
                try:
                    pattern = f"{self._cache_prefix}:*"
                    keys = redis_client.keys(pattern)
                    if keys:
                        redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"[{self._cache_prefix.upper()}_CACHE] L2 clear error: {e}")
                    self._stats['errors'] += 1
        
        logger.info(f"[{self._cache_prefix.upper()}_CACHE] All caches cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with hit/miss counts and ratios
        """
        total_requests = self._stats['l1_hits'] + self._stats['l2_hits'] + self._stats['misses']
        total_hits = self._stats['l1_hits'] + self._stats['l2_hits']

        stats = {
            'l1_hits': self._stats['l1_hits'],
            'l2_hits': self._stats['l2_hits'],
            'misses': self._stats['misses'],
            'writes': self._stats['writes'],
            'errors': self._stats['errors'],
            'total_requests': total_requests,
            'total_hits': total_hits,
            'hit_ratio': total_hits / total_requests if total_requests > 0 else 0.0,
            'l1_hit_ratio': self._stats['l1_hits'] / total_requests if total_requests > 0 else 0.0,
            'l2_hit_ratio': self._stats['l2_hits'] / total_requests if total_requests > 0 else 0.0,
        }

        # Include size_rejections if max_response_size is configured
        if self._max_response_size is not None:
            stats['size_rejections'] = self._stats['size_rejections']
            stats['max_response_size_bytes'] = self._max_response_size

        return stats

    def stats(self) -> Dict[str, Any]:
        """
        Get cache statistics (CacheInterface implementation).

        Alias for get_stats() to comply with CacheInterface.

        Returns:
            Dictionary with hit/miss counts and ratios
        """
        return self.get_stats()


__all__ = ["BaseCacheManager"]

