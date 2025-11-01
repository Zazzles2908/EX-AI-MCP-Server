"""
Dual-Write Configuration Management

Manages per-category feature flags and adapter health thresholds for gradual
rollout from WebSocket to Supabase Realtime.

Phase 2.6.2 - Dual-Write Enhancement
EXAI Consultation: d3e51bcb-c3ea-4122-834f-21e602a0a9b1
Date: 2025-11-01
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterType(Enum):
    """Supported adapter types."""
    WEBSOCKET = "websocket"
    REALTIME = "realtime"


@dataclass
class AdapterHealthConfig:
    """Health thresholds for an adapter."""
    
    error_threshold: float = 0.05  # 5% error rate
    latency_threshold_ms: int = 200  # 200ms latency
    
    def validate(self) -> bool:
        """Validate configuration values."""
        if not (0 <= self.error_threshold <= 1):
            logger.error(f"Invalid error_threshold: {self.error_threshold}")
            return False
        if self.latency_threshold_ms < 0:
            logger.error(f"Invalid latency_threshold_ms: {self.latency_threshold_ms}")
            return False
        return True


@dataclass
class CategoryConfig:
    """Configuration for a specific event category."""
    
    enabled: bool = True
    percentage: int = 100  # 0-100% of events
    adapters: List[str] = field(default_factory=lambda: ["websocket", "realtime"])
    
    def validate(self) -> bool:
        """Validate configuration values."""
        if not (0 <= self.percentage <= 100):
            logger.error(f"Invalid percentage: {self.percentage}")
            return False
        
        valid_adapters = {AdapterType.WEBSOCKET.value, AdapterType.REALTIME.value}
        for adapter in self.adapters:
            if adapter not in valid_adapters:
                logger.error(f"Invalid adapter: {adapter}")
                return False
        
        return True


@dataclass
class DualWriteConfig:
    """
    Dual-write configuration for gradual rollout.
    
    Enables per-category feature flags and percentage-based sampling
    for controlled migration from WebSocket to Supabase Realtime.
    """
    
    # Per-category configurations
    categories: Dict[str, CategoryConfig] = field(default_factory=lambda: {
        'critical': CategoryConfig(enabled=True, percentage=100, adapters=["websocket", "realtime"]),
        'performance': CategoryConfig(enabled=True, percentage=50, adapters=["websocket"]),
        'user_activity': CategoryConfig(enabled=False, percentage=0, adapters=["realtime"]),
        'system': CategoryConfig(enabled=True, percentage=100, adapters=["websocket", "realtime"]),
        'debug': CategoryConfig(enabled=False, percentage=0, adapters=[]),
    })
    
    # Global override (emergency kill switch)
    global_override: Optional[str] = None  # "websocket_only" or "realtime_only"
    
    # Adapter health thresholds
    adapter_health: Dict[str, AdapterHealthConfig] = field(default_factory=lambda: {
        'websocket': AdapterHealthConfig(error_threshold=0.05, latency_threshold_ms=200),
        'realtime': AdapterHealthConfig(error_threshold=0.05, latency_threshold_ms=150),
    })
    
    # Circuit breaker configuration
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: float = 0.05  # 5% failure rate
    circuit_breaker_recovery_time_s: int = 30
    circuit_breaker_latency_multiplier: float = 2.0
    
    def validate(self) -> bool:
        """Validate entire configuration."""
        # Validate categories
        for category_name, config in self.categories.items():
            if not config.validate():
                logger.error(f"Invalid category config: {category_name}")
                return False
        
        # Validate adapter health
        for adapter_name, health_config in self.adapter_health.items():
            if not health_config.validate():
                logger.error(f"Invalid adapter health config: {adapter_name}")
                return False
        
        # Validate global override
        if self.global_override and self.global_override not in ["websocket_only", "realtime_only"]:
            logger.error(f"Invalid global_override: {self.global_override}")
            return False
        
        # Validate circuit breaker config
        if not (0 <= self.circuit_breaker_failure_threshold <= 1):
            logger.error(f"Invalid circuit_breaker_failure_threshold: {self.circuit_breaker_failure_threshold}")
            return False
        
        if self.circuit_breaker_recovery_time_s < 0:
            logger.error(f"Invalid circuit_breaker_recovery_time_s: {self.circuit_breaker_recovery_time_s}")
            return False
        
        if self.circuit_breaker_latency_multiplier < 1.0:
            logger.error(f"Invalid circuit_breaker_latency_multiplier: {self.circuit_breaker_latency_multiplier}")
            return False
        
        return True
    
    def get_adapters_for_category(self, category: str) -> List[str]:
        """
        Get adapters for a specific category, considering global override.
        
        Args:
            category: Event category (e.g., 'critical', 'performance')
        
        Returns:
            List of adapter names to use
        """
        # Check global override first
        if self.global_override == "websocket_only":
            return ["websocket"]
        elif self.global_override == "realtime_only":
            return ["realtime"]
        
        # Check category configuration
        if category not in self.categories:
            logger.warning(f"Unknown category: {category}, defaulting to websocket")
            return ["websocket"]
        
        category_config = self.categories[category]
        
        # If category is disabled, use websocket only
        if not category_config.enabled:
            return ["websocket"]
        
        return category_config.adapters
    
    def should_dual_write(self, category: str) -> bool:
        """
        Determine if dual-write should be used for a category.
        
        Args:
            category: Event category
        
        Returns:
            True if dual-write should be used
        """
        adapters = self.get_adapters_for_category(category)
        return len(adapters) > 1
    
    def get_percentage_for_category(self, category: str) -> int:
        """
        Get the percentage of events to dual-write for a category.
        
        Args:
            category: Event category
        
        Returns:
            Percentage (0-100)
        """
        if category not in self.categories:
            return 0
        
        return self.categories[category].percentage
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'categories': {
                name: {
                    'enabled': config.enabled,
                    'percentage': config.percentage,
                    'adapters': config.adapters,
                }
                for name, config in self.categories.items()
            },
            'global_override': self.global_override,
            'adapter_health': {
                name: {
                    'error_threshold': health.error_threshold,
                    'latency_threshold_ms': health.latency_threshold_ms,
                }
                for name, health in self.adapter_health.items()
            },
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'circuit_breaker_failure_threshold': self.circuit_breaker_failure_threshold,
            'circuit_breaker_recovery_time_s': self.circuit_breaker_recovery_time_s,
            'circuit_breaker_latency_multiplier': self.circuit_breaker_latency_multiplier,
        }

