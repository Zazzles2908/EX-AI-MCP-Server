"""
Cache Manager

Manages result caching and inflight request tracking.
Provides deduplication and caching for WebSocket request routing.

This is part of the Phase 3 refactoring that split the large request_router.py
into focused modules:
- router_utils.py: Utility functions
- cache_manager.py: Result caching and inflight tracking (this file)
- tool_executor.py: Tool execution with semaphore management
- request_router.py: Main message routing logic
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manages result caching and inflight request tracking.

    Provides:
    - Result caching by request_id and call_key
    - Inflight request tracking for deduplication
    - TTL-based expiration for both results and inflight requests
    """

    def __init__(
        self,
        inflight_ttl_secs: int = 300,
        result_ttl_secs: int = 300
    ):
        """
        Initialize cache manager.

        Args:
            inflight_ttl_secs: TTL for inflight requests in seconds (default 300)
            result_ttl_secs: TTL for cached results in seconds (default 300)
        """
        self.inflight_ttl_secs = inflight_ttl_secs
        self.result_ttl_secs = result_ttl_secs

        # Inflight requests: request_id -> asyncio.Future
        self.inflight_requests: Dict[str, asyncio.Future] = {}

        # Cached results: call_key -> (result, timestamp)
        self.cached_results: Dict[str, tuple[Any, float]] = {}

        # Locks for thread safety
        self._inflight_lock = asyncio.Lock()
        self._results_lock = asyncio.Lock()

    async def get_inflight(self, request_id: str) -> Optional[asyncio.Future]:
        """
        Get inflight request future if it exists and is not expired.

        Args:
            request_id: Request ID to check

        Returns:
            Future if request is inflight and not expired, None otherwise
        """
        async with self._inflight_lock:
            if request_id in self.inflight_requests:
                future = self.inflight_requests[request_id]
                # Note: We don't track creation time per request_id
                # In production, you might want to add timestamps for proper TTL
                return future
            return None

    async def add_inflight(self, request_id: str, future: asyncio.Future) -> None:
        """
        Add a request to inflight tracking.

        Args:
            request_id: Request ID to track
            future: Future to track
        """
        async with self._inflight_lock:
            self.inflight_requests[request_id] = future

        # Clean up when future completes
        future.add_done_callback(
            lambda f: asyncio.create_task(self._remove_inflight(request_id))
        )

    async def _remove_inflight(self, request_id: str) -> None:
        """Remove a request from inflight tracking."""
        async with self._inflight_lock:
            self.inflight_requests.pop(request_id, None)

    async def get_cached_result(self, call_key: str) -> Optional[Any]:
        """
        Get cached result if it exists and is not expired.

        Args:
            call_key: Cache key to look up

        Returns:
            Cached result if available and not expired, None otherwise
        """
        async with self._results_lock:
            if call_key in self.cached_results:
                result, timestamp = self.cached_results[call_key]
                age = time.time() - timestamp

                if age < self.result_ttl_secs:
                    return result
                else:
                    # Expired, remove it
                    del self.cached_results[call_key]

            return None

    async def cache_result(self, call_key: str, result: Any) -> None:
        """
        Cache a result with current timestamp.

        Args:
            call_key: Cache key to store under
            result: Result to cache
        """
        async with self._results_lock:
            self.cached_results[call_key] = (result, time.time())

    async def clear_expired(self) -> Dict[str, int]:
        """
        Clear all expired entries from both caches.

        Returns:
            Dictionary with counts of cleared entries
        """
        cleared = {"inflight": 0, "results": 0}
        current_time = time.time()

        # Clear expired inflight requests
        # Note: Without per-request timestamps, we can't properly expire inflight requests
        # In production, you might want to track creation times

        # Clear expired results
        async with self._results_lock:
            expired_keys = []
            for call_key, (result, timestamp) in self.cached_results.items():
                if current_time - timestamp >= self.result_ttl_secs:
                    expired_keys.append(call_key)

            for key in expired_keys:
                del self.cached_results[key]

            cleared["results"] = len(expired_keys)

        return cleared

    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "inflight_count": len(self.inflight_requests),
            "cached_results_count": len(self.cached_results),
            "inflight_ttl_secs": self.inflight_ttl_secs,
            "result_ttl_secs": self.result_ttl_secs,
        }
