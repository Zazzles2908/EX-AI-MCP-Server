"""
WebSocket Stability Configuration

Centralized configuration for WebSocket stability enhancements.
EXAI QA Recommendation: Centralized configuration management.

Created: 2025-10-26
Phase: Task 2 Week 1 - EXAI QA Fixes
EXAI Consultation: c657a995-0f0d-4b97-91be-2618055313f4
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MetricsConfig:
    """Configuration for WebSocket metrics tracking."""
    
    enabled: bool = True
    """Enable metrics tracking"""
    
    sample_rate: float = 1.0
    """Metrics sampling rate (0.0-1.0). Use <1.0 for high-traffic production."""
    
    client_metrics_ttl: int = 3600
    """Time-to-live for inactive client metrics (seconds). Default: 1 hour."""
    
    cleanup_interval: int = 300
    """Interval for periodic cleanup of inactive clients (seconds). Default: 5 minutes."""


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    
    enabled: bool = True
    """Enable circuit breaker protection"""
    
    failure_threshold: int = 5
    """Number of failures before opening circuit"""
    
    success_threshold: int = 2
    """Number of successes in half-open state before closing circuit"""
    
    timeout_seconds: float = 60.0
    """Time to wait before attempting half-open state (seconds)"""
    
    half_open_max_calls: int = 3
    """Maximum calls allowed in half-open state"""


@dataclass
class DeduplicationConfig:
    """Configuration for message deduplication."""
    
    enabled: bool = True
    """Enable message deduplication"""
    
    ttl_seconds: int = 300
    """Time-to-live for message IDs (seconds). Default: 5 minutes."""
    
    use_fast_hash: bool = True
    """Use fast built-in hash() instead of SHA256/MD5. Recommended for performance."""


@dataclass
class WebSocketStabilityConfig:
    """
    Centralized configuration for WebSocket stability enhancements.
    
    EXAI QA Recommendation: Centralized configuration management for easier
    testing, deployment, and environment-specific tuning.
    
    Example usage:
        # Development configuration
        dev_config = WebSocketStabilityConfig(
            metrics=MetricsConfig(sample_rate=1.0),
            circuit_breaker=CircuitBreakerConfig(failure_threshold=3),
            deduplication=DeduplicationConfig(ttl_seconds=60)
        )
        
        # Production configuration
        prod_config = WebSocketStabilityConfig(
            metrics=MetricsConfig(sample_rate=0.1, cleanup_interval=600),
            circuit_breaker=CircuitBreakerConfig(failure_threshold=10),
            deduplication=DeduplicationConfig(ttl_seconds=600)
        )
        
        # Create WebSocket manager with config
        manager = ResilientWebSocketManager(config=prod_config)
    """
    
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    """Metrics tracking configuration"""
    
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    """Circuit breaker configuration"""
    
    deduplication: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    """Message deduplication configuration"""
    
    # Connection management
    connection_timeout: int = 120
    """Connection timeout in seconds. Default: 2 minutes."""
    
    max_queue_size: int = 1000
    """Maximum pending message queue size per client"""
    
    message_ttl: int = 300
    """Time-to-live for pending messages (seconds). Default: 5 minutes."""
    
    # Retry configuration
    max_retry_attempts: int = 3
    """Maximum retry attempts for failed sends"""
    
    retry_base_delay: float = 1.0
    """Base delay for exponential backoff (seconds)"""
    
    retry_max_delay: float = 60.0
    """Maximum retry delay (seconds)"""
    
    @classmethod
    def development(cls) -> "WebSocketStabilityConfig":
        """
        Development environment configuration.
        
        - Full metrics sampling
        - Lower failure thresholds for faster testing
        - Shorter TTLs for faster iteration
        """
        return cls(
            metrics=MetricsConfig(
                sample_rate=1.0,
                client_metrics_ttl=600,  # 10 minutes
                cleanup_interval=60  # 1 minute
            ),
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=3,
                success_threshold=2,
                timeout_seconds=30.0
            ),
            deduplication=DeduplicationConfig(
                ttl_seconds=60  # 1 minute
            ),
            connection_timeout=60,
            message_ttl=120
        )
    
    @classmethod
    def production(cls) -> "WebSocketStabilityConfig":
        """
        Production environment configuration.
        
        - Sampled metrics for performance
        - Higher failure thresholds for stability
        - Longer TTLs for reliability
        """
        return cls(
            metrics=MetricsConfig(
                sample_rate=0.1,  # 10% sampling
                client_metrics_ttl=3600,  # 1 hour
                cleanup_interval=600  # 10 minutes
            ),
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=10,
                success_threshold=3,
                timeout_seconds=120.0
            ),
            deduplication=DeduplicationConfig(
                ttl_seconds=600  # 10 minutes
            ),
            connection_timeout=120,
            message_ttl=300
        )
    
    @classmethod
    def testing(cls) -> "WebSocketStabilityConfig":
        """
        Testing environment configuration.
        
        - Full metrics for validation
        - Very low thresholds for fast failure testing
        - Short TTLs for rapid iteration
        """
        return cls(
            metrics=MetricsConfig(
                sample_rate=1.0,
                client_metrics_ttl=60,  # 1 minute
                cleanup_interval=10  # 10 seconds
            ),
            circuit_breaker=CircuitBreakerConfig(
                failure_threshold=2,
                success_threshold=1,
                timeout_seconds=5.0
            ),
            deduplication=DeduplicationConfig(
                ttl_seconds=30  # 30 seconds
            ),
            connection_timeout=30,
            message_ttl=60
        )

