"""
In-memory (with optional Redis) storage backend for conversation threads

This module provides a thread-safe, in-memory alternative to Redis for storing
conversation contexts. In production, a Redis backend can be enabled via REDIS_URL
for persistence across MCP client reconnections. If REDIS_URL is not set or Redis
is unavailable, the system falls back to in-memory storage.

⚠️  PROCESS-SPECIFIC STORAGE: This storage is confined to a single Python process.
    Data stored in one process is NOT accessible from other processes or subprocesses.
    This is why simulator tests that run server.py as separate subprocesses cannot
    share conversation state between tool calls.

Key Features:
- Thread-safe operations using locks
- TTL support with automatic expiration
- Background cleanup thread for memory management
- Singleton pattern for consistent state within a single process
- Drop-in replacement for Redis storage (for single-process scenarios)
"""

import logging
import os
import threading
import time
from typing import Optional

# PHASE 3 (2025-10-18): Import monitoring utilities
from utils.monitoring import record_redis_event
from utils.timezone_helper import log_timestamp

# PHASE 1 (2025-10-18): Import circuit breaker for resilience
from src.resilience.circuit_breaker_manager import circuit_breaker_manager
import pybreaker

logger = logging.getLogger(__name__)

try:
    import redis  # type: ignore
    _redis_available = True
except Exception:
    _redis_available = False


class InMemoryStorage:
    """Thread-safe in-memory storage for conversation threads"""

    def __init__(self):
        self._store: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()
        # Match Redis behavior: cleanup interval based on conversation timeout
        # Run cleanup at 1/10th of timeout interval (e.g., 18 mins for 3 hour timeout)
        timeout_hours = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))
        self._cleanup_interval = (timeout_hours * 3600) // 10
        self._cleanup_interval = max(300, self._cleanup_interval)  # Minimum 5 minutes
        self._shutdown = False

        # Start background cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

        logger.info(
            f"In-memory storage initialized with {timeout_hours}h timeout, cleanup every {self._cleanup_interval//60}m"
        )

    def set_with_ttl(self, key: str, ttl_seconds: int, value: str) -> None:
        """Store value with expiration time"""
        start_time = time.time()
        data_size = len(value.encode('utf-8'))

        with self._lock:
            expires_at = time.time() + ttl_seconds
            self._store[key] = (value, expires_at)
            logger.debug(f"Stored key {key} with TTL {ttl_seconds}s")

        # PHASE 3 (2025-10-18): Monitor ALL WRITE operations (EXAI recommended)
        response_time_ms = (time.time() - start_time) * 1000
        record_redis_event(
            direction="send",
            function_name="InMemoryStorage.set_with_ttl",
            data_size=data_size,
            response_time_ms=response_time_ms,
            metadata={"key": key, "ttl": ttl_seconds, "timestamp": log_timestamp()}
        )

    def get(self, key: str) -> Optional[str]:
        """Retrieve value if not expired"""
        start_time = time.time()

        # PHASE 3 (2025-10-23): Calculate request size for monitoring
        request_size = len(key.encode('utf-8'))

        with self._lock:
            if key in self._store:
                value, expires_at = self._store[key]
                if time.time() < expires_at:
                    logger.debug(f"Retrieved key {key}")

                    # PHASE 3 (2025-10-18): Monitor READ operations (sample 1 in 5)
                    if hash(key) % 5 == 0:
                        response_time_ms = (time.time() - start_time) * 1000
                        response_size = len(value.encode('utf-8')) if value else 0
                        # Use response size if available, otherwise use request size
                        data_size = response_size if response_size > 0 else request_size
                        record_redis_event(
                            direction="receive",
                            function_name="InMemoryStorage.get",
                            data_size=data_size,
                            response_time_ms=response_time_ms,
                            metadata={
                                "key": key,
                                "hit": True,
                                "request_size": request_size,
                                "response_size": response_size,
                                "timestamp": log_timestamp()
                            }
                        )

                    return value
                else:
                    # Clean up expired entry
                    del self._store[key]
                    logger.debug(f"Key {key} expired and removed")

        # PHASE 3 (2025-10-23): Monitor cache misses (sample 1 in 5) - use request size
        if hash(key) % 5 == 0:
            response_time_ms = (time.time() - start_time) * 1000
            record_redis_event(
                direction="receive",
                function_name="InMemoryStorage.get",
                data_size=request_size,  # Use request size for cache misses
                response_time_ms=response_time_ms,
                metadata={
                    "key": key,
                    "hit": False,
                    "request_size": request_size,
                    "response_size": 0,
                    "timestamp": log_timestamp()
                }
            )

        return None

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        """Redis-compatible setex method"""
        self.set_with_ttl(key, ttl_seconds, value)

    def _cleanup_worker(self):
        """Background thread that periodically cleans up expired entries"""
        while not self._shutdown:
            time.sleep(self._cleanup_interval)
            self._cleanup_expired()

    def _cleanup_expired(self):
        """Remove all expired entries"""
        with self._lock:
            current_time = time.time()
            expired_keys = [k for k, (_, exp) in self._store.items() if exp < current_time]
            for key in expired_keys:
                del self._store[key]

            if expired_keys:
                logger.debug(f"Cleaned up {len(expired_keys)} expired conversation threads")

    def shutdown(self):
        """Graceful shutdown of background thread"""
        self._shutdown = True
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1)


# Optional Redis storage backend
class RedisStorage:
    def __init__(self, url: str, ttl_seconds: int):
        self._client = redis.from_url(url, decode_responses=True)
        self._ttl = ttl_seconds
        # PHASE 1 (2025-10-18): Get circuit breaker for Redis operations
        self._breaker = circuit_breaker_manager.get_breaker('redis')
        # Sanitize URL to hide password in logs (P0-9 security fix)
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.password:
            safe_url = url.replace(f':{parsed.password}@', ':****@')
        else:
            safe_url = url
        logger.info(f"Redis storage initialized (ttl={ttl_seconds}s) at {safe_url}")
    def set_with_ttl(self, key: str, ttl_seconds: int, value: str) -> None:
        start_time = time.time()
        data_size = len(value.encode('utf-8'))

        try:
            # PHASE 1 (2025-10-18): Circuit breaker protected operation
            self._breaker.call(self._client.setex, key, ttl_seconds, value)

            # PHASE 3 (2025-10-18): Monitor ALL WRITE operations
            response_time_ms = (time.time() - start_time) * 1000
            record_redis_event(
                direction="send",
                function_name="RedisStorage.set_with_ttl",
                data_size=data_size,
                response_time_ms=response_time_ms,
                metadata={"key": key, "ttl": ttl_seconds, "timestamp": log_timestamp()}
            )
        except pybreaker.CircuitBreakerError:
            # Circuit breaker is OPEN - Redis is unavailable
            breaker_state = self._breaker.current_state.name
            logger.error(f"Redis circuit breaker {breaker_state} - cannot set key: {key}")
            record_redis_event(
                direction="error",
                function_name="RedisStorage.set_with_ttl",
                data_size=data_size,
                error=f"Circuit breaker {breaker_state}",
                metadata={"key": key, "breaker_state": breaker_state, "timestamp": log_timestamp()}
            )
            # Graceful degradation: Don't raise, just log (data will be lost but service continues)
            return
        except Exception as e:
            # PHASE 3 (2025-10-18): Monitor errors
            record_redis_event(
                direction="error",
                function_name="RedisStorage.set_with_ttl",
                data_size=data_size,
                error=str(e),
                metadata={"key": key, "timestamp": log_timestamp()}
            )
            raise

    def get(self, key: str):
        start_time = time.time()

        # PHASE 3 (2025-10-23): Calculate request size for monitoring
        request_size = len(key.encode('utf-8'))

        try:
            # PHASE 1 (2025-10-18): Circuit breaker protected operation
            value = self._breaker.call(self._client.get, key)

            # PHASE 3 (2025-10-23): Monitor READ operations (sample 1 in 5)
            if hash(key) % 5 == 0:
                response_time_ms = (time.time() - start_time) * 1000
                response_size = len(value.encode('utf-8')) if value else 0
                # Use response size if available, otherwise use request size
                data_size = response_size if response_size > 0 else request_size
                record_redis_event(
                    direction="receive",
                    function_name="RedisStorage.get",
                    data_size=data_size,
                    response_time_ms=response_time_ms,
                    metadata={
                        "key": key,
                        "hit": value is not None,
                        "request_size": request_size,
                        "response_size": response_size,
                        "timestamp": log_timestamp()
                    }
                )

            return value
        except pybreaker.CircuitBreakerError:
            # Circuit breaker is OPEN - Redis is unavailable
            breaker_state = self._breaker.current_state.name
            logger.warning(f"Redis circuit breaker {breaker_state} - cannot get key: {key}")
            record_redis_event(
                direction="error",
                function_name="RedisStorage.get",
                data_size=request_size,  # Use request size for errors
                error=f"Circuit breaker {breaker_state}",
                metadata={
                    "key": key,
                    "breaker_state": breaker_state,
                    "request_size": request_size,
                    "timestamp": log_timestamp()
                }
            )
            # Graceful degradation: Return None (cache miss)
            return None
        except Exception as e:
            # PHASE 3 (2025-10-23): Monitor errors - use request size
            record_redis_event(
                direction="error",
                function_name="RedisStorage.get",
                data_size=request_size,  # Use request size for errors
                error=str(e),
                metadata={
                    "key": key,
                    "request_size": request_size,
                    "timestamp": log_timestamp()
                }
            )
            raise

    def setex(self, key: str, ttl_seconds: int, value: str) -> None:
        self.set_with_ttl(key, ttl_seconds, value)

# Global singleton instance
_storage_instance = None
_storage_lock = threading.Lock()


def get_storage_backend():
    """Get the global storage instance (singleton pattern)"""
    global _storage_instance
    if _storage_instance is None:
        with _storage_lock:
            if _storage_instance is None:
                # Choose Redis when configured and available; else in-memory
                redis_url = os.getenv("REDIS_URL")
                if redis_url and _redis_available:
                    try:
                        timeout_hours = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))
                        ttl = timeout_hours * 3600
                        _storage_instance = RedisStorage(redis_url, ttl)
                        logger.info("Initialized Redis conversation storage")
                    except Exception as e:
                        logger.warning(f"Redis storage init failed ({e}); falling back to in-memory storage")
                        _storage_instance = InMemoryStorage()
                        logger.info("Initialized in-memory conversation storage")
                else:
                    _storage_instance = InMemoryStorage()
                    logger.info("Initialized in-memory conversation storage")
    return _storage_instance
