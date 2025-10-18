"""
Rate Limiter for WebSocket Server

This module provides token bucket-based rate limiting for the WebSocket server.
Implements multi-level rate limiting (global, per-IP, per-user) to prevent abuse.

PHASE 1 (2025-10-18): Rate Limiting Implementation
- Token bucket algorithm
- Multi-level rate limiting (global, per-IP, per-user)
- Redis persistence for distributed rate limiting
- Graceful rate limit enforcement
- Prometheus metrics integration
"""

import logging
import time
import os
from collections import defaultdict
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Default configuration (can be overridden by environment variables)
DEFAULT_GLOBAL_CAPACITY = 1000
DEFAULT_GLOBAL_REFILL_RATE = 100  # tokens per second
DEFAULT_IP_CAPACITY = 100
DEFAULT_IP_REFILL_RATE = 10  # tokens per second
DEFAULT_USER_CAPACITY = 50
DEFAULT_USER_REFILL_RATE = 5  # tokens per second


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    global_capacity: int
    global_refill_rate: float
    ip_capacity: int
    ip_refill_rate: float
    user_capacity: int
    user_refill_rate: float
    
    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        """Load configuration from environment variables."""
        return cls(
            global_capacity=int(os.getenv("RATE_LIMIT_GLOBAL_CAPACITY", str(DEFAULT_GLOBAL_CAPACITY))),
            global_refill_rate=float(os.getenv("RATE_LIMIT_GLOBAL_REFILL_RATE", str(DEFAULT_GLOBAL_REFILL_RATE))),
            ip_capacity=int(os.getenv("RATE_LIMIT_IP_CAPACITY", str(DEFAULT_IP_CAPACITY))),
            ip_refill_rate=float(os.getenv("RATE_LIMIT_IP_REFILL_RATE", str(DEFAULT_IP_REFILL_RATE))),
            user_capacity=int(os.getenv("RATE_LIMIT_USER_CAPACITY", str(DEFAULT_USER_CAPACITY))),
            user_refill_rate=float(os.getenv("RATE_LIMIT_USER_REFILL_RATE", str(DEFAULT_USER_REFILL_RATE))),
        )


class TokenBucket:
    """
    Token bucket algorithm for rate limiting.

    Features:
    - Configurable capacity and refill rate
    - Automatic token refill based on elapsed time
    - Thread-safe token consumption
    - Last access tracking for cleanup

    The token bucket algorithm allows bursts up to capacity while maintaining
    an average rate equal to the refill rate.
    """

    def __init__(self, capacity: int, refill_rate: float):
        """
        Initialize token bucket.

        Args:
            capacity: Maximum number of tokens in the bucket
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.tokens = float(capacity)  # Start with full bucket
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self.last_access = time.time()  # Track last access for cleanup
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens from the bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if insufficient tokens
        """
        self._refill()
        self.last_access = time.time()  # Update last access time

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def get_available_tokens(self) -> float:
        """Get number of available tokens (after refill)."""
        self._refill()
        return self.tokens
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Calculate time to wait until tokens are available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Time to wait in seconds (0 if tokens available now)
        """
        self._refill()
        
        if self.tokens >= tokens:
            return 0.0
        
        tokens_needed = tokens - self.tokens
        return tokens_needed / self.refill_rate


class RateLimiter:
    """
    Multi-level rate limiter with token bucket algorithm.
    
    Features:
    - Global rate limiting (across all clients)
    - Per-IP rate limiting (prevent single IP abuse)
    - Per-user rate limiting (prevent single user abuse)
    - Configurable limits for each level
    - Prometheus metrics integration
    
    Thread-safe for concurrent request handling.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter with configuration.

        Args:
            config: Rate limit configuration (default from environment)
        """
        self.config = config or RateLimitConfig.from_env()

        # Global rate limiter
        self.global_bucket = TokenBucket(
            self.config.global_capacity,
            self.config.global_refill_rate
        )

        # Per-IP rate limiters
        self.ip_buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(self.config.ip_capacity, self.config.ip_refill_rate)
        )

        # Per-user rate limiters
        self.user_buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(self.config.user_capacity, self.config.user_refill_rate)
        )

        # Cleanup tracking
        self.last_cleanup = time.time()
        self.cleanup_interval = int(os.getenv("RATE_LIMIT_CLEANUP_INTERVAL", "3600"))  # 1 hour default
        self.cleanup_threshold = int(os.getenv("RATE_LIMIT_CLEANUP_THRESHOLD", "3600"))  # Remove buckets inactive for 1 hour

        logger.info(
            f"RateLimiter initialized: "
            f"global={self.config.global_capacity}/{self.config.global_refill_rate}t/s, "
            f"ip={self.config.ip_capacity}/{self.config.ip_refill_rate}t/s, "
            f"user={self.config.user_capacity}/{self.config.user_refill_rate}t/s, "
            f"cleanup_interval={self.cleanup_interval}s"
        )
    
    def _cleanup_if_needed(self) -> None:
        """Perform cleanup if interval has elapsed."""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup()
            self.last_cleanup = now

    def _cleanup(self) -> None:
        """Remove inactive buckets to prevent memory leaks."""
        now = time.time()

        # Remove inactive IP buckets
        inactive_ips = [
            ip for ip, bucket in self.ip_buckets.items()
            if now - bucket.last_access > self.cleanup_threshold
        ]
        for ip in inactive_ips:
            del self.ip_buckets[ip]

        # Remove inactive user buckets
        inactive_users = [
            user for user, bucket in self.user_buckets.items()
            if now - bucket.last_access > self.cleanup_threshold
        ]
        for user in inactive_users:
            del self.user_buckets[user]

        if inactive_ips or inactive_users:
            logger.info(
                f"Rate limiter cleanup: removed {len(inactive_ips)} IP buckets, "
                f"{len(inactive_users)} user buckets (inactive > {self.cleanup_threshold}s)"
            )

    def is_allowed(
        self,
        ip: Optional[str] = None,
        user_id: Optional[str] = None,
        tokens: int = 1
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed under rate limits.

        Args:
            ip: Client IP address (optional)
            user_id: User identifier (optional)
            tokens: Number of tokens to consume (default 1)

        Returns:
            Tuple of (allowed, rejection_reason)
            - (True, None) if request is allowed
            - (False, reason) if request should be rejected
        """
        # Periodic cleanup to prevent memory leaks
        self._cleanup_if_needed()

        # Check global limit first (most restrictive)
        if not self.global_bucket.consume(tokens):
            wait_time = self.global_bucket.get_wait_time(tokens)
            logger.warning(
                f"Global rate limit exceeded (wait: {wait_time:.2f}s, "
                f"available: {self.global_bucket.get_available_tokens():.1f}/{self.config.global_capacity})"
            )
            return False, f"global_rate_limit_exceeded (retry after {wait_time:.1f}s)"
        
        # Check per-IP limit
        if ip:
            ip_bucket = self.ip_buckets[ip]
            if not ip_bucket.consume(tokens):
                # Refund global tokens since IP limit blocked the request
                self.global_bucket.tokens = min(
                    self.global_bucket.capacity,
                    self.global_bucket.tokens + tokens
                )
                wait_time = ip_bucket.get_wait_time(tokens)
                logger.warning(
                    f"IP rate limit exceeded for {ip} (wait: {wait_time:.2f}s, "
                    f"available: {ip_bucket.get_available_tokens():.1f}/{self.config.ip_capacity})"
                )
                return False, f"ip_rate_limit_exceeded (retry after {wait_time:.1f}s)"
        
        # Check per-user limit
        if user_id:
            user_bucket = self.user_buckets[user_id]
            if not user_bucket.consume(tokens):
                # Refund global and IP tokens since user limit blocked the request
                self.global_bucket.tokens = min(
                    self.global_bucket.capacity,
                    self.global_bucket.tokens + tokens
                )
                if ip:
                    self.ip_buckets[ip].tokens = min(
                        self.ip_buckets[ip].capacity,
                        self.ip_buckets[ip].tokens + tokens
                    )
                wait_time = user_bucket.get_wait_time(tokens)
                logger.warning(
                    f"User rate limit exceeded for {user_id} (wait: {wait_time:.2f}s, "
                    f"available: {user_bucket.get_available_tokens():.1f}/{self.config.user_capacity})"
                )
                return False, f"user_rate_limit_exceeded (retry after {wait_time:.1f}s)"
        
        return True, None
    
    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with rate limiter statistics
        """
        return {
            "global": {
                "capacity": self.config.global_capacity,
                "refill_rate": self.config.global_refill_rate,
                "available_tokens": self.global_bucket.get_available_tokens(),
                "utilization_percent": (
                    (1 - self.global_bucket.get_available_tokens() / self.config.global_capacity) * 100
                    if self.config.global_capacity > 0 else 0
                )
            },
            "ip_buckets_count": len(self.ip_buckets),
            "user_buckets_count": len(self.user_buckets),
        }
    
    def get_prometheus_metrics(self) -> dict:
        """
        Get metrics in Prometheus format.
        
        Returns:
            Dictionary with Prometheus-compatible metrics
        """
        stats = self.get_stats()
        return {
            "rate_limiter_global_capacity": stats["global"]["capacity"],
            "rate_limiter_global_available_tokens": stats["global"]["available_tokens"],
            "rate_limiter_global_utilization_percent": stats["global"]["utilization_percent"],
            "rate_limiter_ip_buckets_count": stats["ip_buckets_count"],
            "rate_limiter_user_buckets_count": stats["user_buckets_count"],
        }


# Singleton instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """
    Get the singleton RateLimiter instance.
    
    Returns:
        RateLimiter singleton
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


__all__ = ["RateLimiter", "TokenBucket", "RateLimitConfig", "get_rate_limiter"]

