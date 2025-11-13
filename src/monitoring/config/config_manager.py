"""
Configuration Manager for Dual-Write System

Loads, validates, and manages dual-write configuration from environment variables.
Supports runtime configuration updates and change notifications.

Phase 2.6.2 - Dual-Write Enhancement
EXAI Consultation: d3e51bcb-c3ea-4122-834f-21e602a0a9b1
Date: 2025-11-01
"""

import logging
import os
from typing import Callable, List, Optional

from src.monitoring.config.dual_write_config import (
    DualWriteConfig,
    CategoryConfig,
    AdapterHealthConfig,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages dual-write configuration with environment variable support.

    Loads configuration from .env file and provides methods for:
    - Configuration validation
    - Runtime updates
    - Change notifications
    - Configuration queries

    REFACTORED: Removed singleton pattern - now uses dependency injection
    for better testability and maintainability.
    """

    def __init__(self):
        """Initialize configuration manager."""
        self._config: DualWriteConfig = self._load_from_env()
        self._change_listeners: List[Callable] = []

        if not self._config.validate():
            logger.error("Configuration validation failed, using defaults")
            self._config = DualWriteConfig()
    
    @staticmethod
    def _load_from_env() -> DualWriteConfig:
        """Load configuration from environment variables."""
        config = DualWriteConfig()
        
        # Load per-category percentages
        category_percentages = {
            'critical': int(os.getenv('DUAL_WRITE_CRITICAL_PERCENTAGE', '100')),
            'performance': int(os.getenv('DUAL_WRITE_PERFORMANCE_PERCENTAGE', '50')),
            'user_activity': int(os.getenv('DUAL_WRITE_USER_ACTIVITY_PERCENTAGE', '0')),
            'system': int(os.getenv('DUAL_WRITE_SYSTEM_PERCENTAGE', '100')),
            'debug': int(os.getenv('DUAL_WRITE_DEBUG_PERCENTAGE', '0')),
        }
        
        for category, percentage in category_percentages.items():
            if category in config.categories:
                config.categories[category].percentage = percentage
        
        # Load global override
        global_override = os.getenv('DUAL_WRITE_GLOBAL_OVERRIDE', None)
        if global_override:
            config.global_override = global_override
        
        # Load adapter health thresholds
        websocket_error_threshold = float(os.getenv('ADAPTER_WEBSOCKET_ERROR_THRESHOLD', '0.05'))
        websocket_latency_threshold = int(os.getenv('ADAPTER_WEBSOCKET_LATENCY_THRESHOLD_MS', '200'))
        realtime_error_threshold = float(os.getenv('ADAPTER_REALTIME_ERROR_THRESHOLD', '0.05'))
        realtime_latency_threshold = int(os.getenv('ADAPTER_REALTIME_LATENCY_THRESHOLD_MS', '150'))
        
        config.adapter_health['websocket'] = AdapterHealthConfig(
            error_threshold=websocket_error_threshold,
            latency_threshold_ms=websocket_latency_threshold,
        )
        config.adapter_health['realtime'] = AdapterHealthConfig(
            error_threshold=realtime_error_threshold,
            latency_threshold_ms=realtime_latency_threshold,
        )
        
        # Load circuit breaker config
        config.circuit_breaker_enabled = os.getenv('CIRCUIT_BREAKER_ENABLED', 'true').lower() == 'true'
        config.circuit_breaker_failure_threshold = float(os.getenv('CIRCUIT_BREAKER_FAILURE_THRESHOLD', '0.05'))
        config.circuit_breaker_recovery_time_s = int(os.getenv('CIRCUIT_BREAKER_RECOVERY_TIME_S', '30'))
        config.circuit_breaker_latency_multiplier = float(os.getenv('CIRCUIT_BREAKER_LATENCY_MULTIPLIER', '2.0'))
        
        logger.info("Configuration loaded from environment variables")
        return config
    
    def get_config(self) -> DualWriteConfig:
        """Get current configuration."""
        return self._config
    
    def update_category_percentage(self, category: str, percentage: int) -> bool:
        """
        Update percentage for a category.
        
        Args:
            category: Category name
            percentage: New percentage (0-100)
        
        Returns:
            True if update successful
        """
        if category not in self._config.categories:
            logger.error(f"Unknown category: {category}")
            return False
        
        if not (0 <= percentage <= 100):
            logger.error(f"Invalid percentage: {percentage}")
            return False
        
        self._config.categories[category].percentage = percentage
        logger.info(f"Updated {category} percentage to {percentage}%")
        self._notify_listeners()
        return True
    
    def update_global_override(self, override: Optional[str]) -> bool:
        """
        Update global override.
        
        Args:
            override: "websocket_only", "realtime_only", or None
        
        Returns:
            True if update successful
        """
        if override and override not in ["websocket_only", "realtime_only"]:
            logger.error(f"Invalid override: {override}")
            return False
        
        self._config.global_override = override
        logger.info(f"Updated global override to {override}")
        self._notify_listeners()
        return True
    
    def update_adapter_health_threshold(
        self,
        adapter: str,
        error_threshold: Optional[float] = None,
        latency_threshold_ms: Optional[int] = None,
    ) -> bool:
        """
        Update adapter health thresholds.
        
        Args:
            adapter: Adapter name ("websocket" or "realtime")
            error_threshold: New error threshold (0-1)
            latency_threshold_ms: New latency threshold in ms
        
        Returns:
            True if update successful
        """
        if adapter not in self._config.adapter_health:
            logger.error(f"Unknown adapter: {adapter}")
            return False
        
        health_config = self._config.adapter_health[adapter]
        
        if error_threshold is not None:
            if not (0 <= error_threshold <= 1):
                logger.error(f"Invalid error_threshold: {error_threshold}")
                return False
            health_config.error_threshold = error_threshold
        
        if latency_threshold_ms is not None:
            if latency_threshold_ms < 0:
                logger.error(f"Invalid latency_threshold_ms: {latency_threshold_ms}")
                return False
            health_config.latency_threshold_ms = latency_threshold_ms
        
        logger.info(f"Updated {adapter} health thresholds")
        self._notify_listeners()
        return True
    
    def register_change_listener(self, callback: Callable) -> None:
        """
        Register a callback to be notified of configuration changes.
        
        Args:
            callback: Function to call when configuration changes
        """
        self._change_listeners.append(callback)
        logger.debug(f"Registered change listener: {callback.__name__}")
    
    def _notify_listeners(self) -> None:
        """Notify all registered listeners of configuration changes."""
        for listener in self._change_listeners:
            try:
                listener(self._config)
            except Exception as e:
                logger.error(f"Error notifying listener {listener.__name__}: {e}")
    
    def reload_from_env(self) -> bool:
        """
        Reload configuration from environment variables.
        
        Returns:
            True if reload successful
        """
        new_config = self._load_from_env()
        
        if not new_config.validate():
            logger.error("New configuration validation failed, keeping current config")
            return False
        
        self._config = new_config
        logger.info("Configuration reloaded from environment variables")
        self._notify_listeners()
        return True
    
    def get_config_dict(self) -> dict:
        """Get configuration as dictionary."""
        return self._config.to_dict()


# DEPRECATED: Singleton instance removed
# Use dependency injection instead:
# config_manager = ConfigManager()
# consumer = SomeClass(config_manager)

