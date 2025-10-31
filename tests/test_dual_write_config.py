"""
Tests for Dual-Write Configuration System

Tests for DualWriteConfig, CategoryConfig, AdapterHealthConfig, and ConfigManager.
"""

import pytest
import os
from unittest.mock import patch

from src.monitoring.config.dual_write_config import (
    DualWriteConfig,
    CategoryConfig,
    AdapterHealthConfig,
    AdapterType,
)
from src.monitoring.config.config_manager import ConfigManager, get_config_manager


class TestAdapterHealthConfig:
    """Test AdapterHealthConfig validation."""

    def test_valid_adapter_health_config(self):
        """Test valid adapter health configuration."""
        config = AdapterHealthConfig(error_threshold=0.05, latency_threshold_ms=200)
        assert config.validate()

    def test_invalid_error_threshold_negative(self):
        """Test invalid negative error threshold."""
        config = AdapterHealthConfig(error_threshold=-0.1, latency_threshold_ms=200)
        assert not config.validate()

    def test_invalid_error_threshold_over_one(self):
        """Test invalid error threshold over 1.0."""
        config = AdapterHealthConfig(error_threshold=1.5, latency_threshold_ms=200)
        assert not config.validate()

    def test_invalid_latency_threshold_negative(self):
        """Test invalid negative latency threshold."""
        config = AdapterHealthConfig(error_threshold=0.05, latency_threshold_ms=-100)
        assert not config.validate()

    def test_boundary_error_threshold_zero(self):
        """Test boundary: error threshold = 0."""
        config = AdapterHealthConfig(error_threshold=0.0, latency_threshold_ms=200)
        assert config.validate()

    def test_boundary_error_threshold_one(self):
        """Test boundary: error threshold = 1.0."""
        config = AdapterHealthConfig(error_threshold=1.0, latency_threshold_ms=200)
        assert config.validate()


class TestCategoryConfig:
    """Test CategoryConfig validation."""

    def test_valid_category_config(self):
        """Test valid category configuration."""
        config = CategoryConfig(enabled=True, percentage=50, adapters=["websocket", "realtime"])
        assert config.validate()

    def test_invalid_percentage_negative(self):
        """Test invalid negative percentage."""
        config = CategoryConfig(enabled=True, percentage=-10, adapters=["websocket"])
        assert not config.validate()

    def test_invalid_percentage_over_100(self):
        """Test invalid percentage over 100."""
        config = CategoryConfig(enabled=True, percentage=150, adapters=["websocket"])
        assert not config.validate()

    def test_invalid_adapter_name(self):
        """Test invalid adapter name."""
        config = CategoryConfig(enabled=True, percentage=50, adapters=["invalid_adapter"])
        assert not config.validate()

    def test_boundary_percentage_zero(self):
        """Test boundary: percentage = 0."""
        config = CategoryConfig(enabled=True, percentage=0, adapters=["websocket"])
        assert config.validate()

    def test_boundary_percentage_100(self):
        """Test boundary: percentage = 100."""
        config = CategoryConfig(enabled=True, percentage=100, adapters=["websocket"])
        assert config.validate()

    def test_multiple_adapters(self):
        """Test configuration with multiple adapters."""
        config = CategoryConfig(enabled=True, percentage=100, adapters=["websocket", "realtime"])
        assert config.validate()


class TestDualWriteConfig:
    """Test DualWriteConfig validation and methods."""

    def test_default_config_valid(self):
        """Test default configuration is valid."""
        config = DualWriteConfig()
        assert config.validate()

    def test_get_adapters_for_category_critical(self):
        """Test getting adapters for critical category."""
        config = DualWriteConfig()
        adapters = config.get_adapters_for_category('critical')
        assert 'websocket' in adapters
        assert 'realtime' in adapters

    def test_get_adapters_for_category_performance(self):
        """Test getting adapters for performance category."""
        config = DualWriteConfig()
        adapters = config.get_adapters_for_category('performance')
        assert 'websocket' in adapters

    def test_get_adapters_for_unknown_category(self):
        """Test getting adapters for unknown category."""
        config = DualWriteConfig()
        adapters = config.get_adapters_for_category('unknown')
        assert adapters == ['websocket']

    def test_get_adapters_with_websocket_only_override(self):
        """Test global override: websocket_only."""
        config = DualWriteConfig()
        config.global_override = 'websocket_only'
        
        adapters = config.get_adapters_for_category('critical')
        assert adapters == ['websocket']

    def test_get_adapters_with_realtime_only_override(self):
        """Test global override: realtime_only."""
        config = DualWriteConfig()
        config.global_override = 'realtime_only'
        
        adapters = config.get_adapters_for_category('critical')
        assert adapters == ['realtime']

    def test_should_dual_write_true(self):
        """Test should_dual_write returns True for dual adapters."""
        config = DualWriteConfig()
        assert config.should_dual_write('critical')

    def test_should_dual_write_false(self):
        """Test should_dual_write returns False for single adapter."""
        config = DualWriteConfig()
        assert not config.should_dual_write('performance')

    def test_get_percentage_for_category(self):
        """Test getting percentage for category."""
        config = DualWriteConfig()
        assert config.get_percentage_for_category('critical') == 100
        assert config.get_percentage_for_category('performance') == 50

    def test_get_percentage_for_unknown_category(self):
        """Test getting percentage for unknown category."""
        config = DualWriteConfig()
        assert config.get_percentage_for_category('unknown') == 0

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = DualWriteConfig()
        config_dict = config.to_dict()
        
        assert 'categories' in config_dict
        assert 'global_override' in config_dict
        assert 'adapter_health' in config_dict
        assert 'circuit_breaker_enabled' in config_dict


class TestConfigManager:
    """Test ConfigManager functionality."""

    def test_singleton_pattern(self):
        """Test ConfigManager singleton pattern."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        assert manager1 is manager2

    def test_get_config_manager(self):
        """Test get_config_manager function."""
        manager = get_config_manager()
        assert isinstance(manager, ConfigManager)

    def test_get_config(self):
        """Test getting configuration."""
        manager = ConfigManager()
        config = manager.get_config()
        assert isinstance(config, DualWriteConfig)

    def test_update_category_percentage(self):
        """Test updating category percentage."""
        manager = ConfigManager()
        result = manager.update_category_percentage('critical', 75)
        assert result
        assert manager.get_config().get_percentage_for_category('critical') == 75

    def test_update_category_percentage_invalid_category(self):
        """Test updating percentage for invalid category."""
        manager = ConfigManager()
        result = manager.update_category_percentage('invalid', 50)
        assert not result

    def test_update_category_percentage_invalid_value(self):
        """Test updating percentage with invalid value."""
        manager = ConfigManager()
        result = manager.update_category_percentage('critical', 150)
        assert not result

    def test_update_global_override(self):
        """Test updating global override."""
        manager = ConfigManager()
        result = manager.update_global_override('websocket_only')
        assert result
        assert manager.get_config().global_override == 'websocket_only'

    def test_update_global_override_invalid(self):
        """Test updating global override with invalid value."""
        manager = ConfigManager()
        result = manager.update_global_override('invalid_override')
        assert not result

    def test_update_adapter_health_threshold(self):
        """Test updating adapter health threshold."""
        manager = ConfigManager()
        result = manager.update_adapter_health_threshold(
            'websocket',
            error_threshold=0.1,
            latency_threshold_ms=300
        )
        assert result
        
        health = manager.get_config().adapter_health['websocket']
        assert health.error_threshold == 0.1
        assert health.latency_threshold_ms == 300

    def test_update_adapter_health_threshold_invalid_adapter(self):
        """Test updating health threshold for invalid adapter."""
        manager = ConfigManager()
        result = manager.update_adapter_health_threshold('invalid', error_threshold=0.1)
        assert not result

    def test_register_change_listener(self):
        """Test registering change listener."""
        manager = ConfigManager()
        
        callback_called = []
        
        def callback(config):
            callback_called.append(True)
        
        manager.register_change_listener(callback)
        manager.update_category_percentage('critical', 75)
        
        assert len(callback_called) > 0

    def test_get_config_dict(self):
        """Test getting configuration as dictionary."""
        manager = ConfigManager()
        config_dict = manager.get_config_dict()
        
        assert isinstance(config_dict, dict)
        assert 'categories' in config_dict
        assert 'adapter_health' in config_dict


class TestConfigManagerEnvironmentVariables:
    """Test ConfigManager loading from environment variables."""

    @patch.dict(os.environ, {
        'DUAL_WRITE_CRITICAL_PERCENTAGE': '100',
        'DUAL_WRITE_PERFORMANCE_PERCENTAGE': '75',
        'DUAL_WRITE_USER_ACTIVITY_PERCENTAGE': '25',
        'DUAL_WRITE_SYSTEM_PERCENTAGE': '100',
        'DUAL_WRITE_DEBUG_PERCENTAGE': '0',
        'ADAPTER_WEBSOCKET_ERROR_THRESHOLD': '0.1',
        'ADAPTER_WEBSOCKET_LATENCY_THRESHOLD_MS': '300',
        'ADAPTER_REALTIME_ERROR_THRESHOLD': '0.08',
        'ADAPTER_REALTIME_LATENCY_THRESHOLD_MS': '200',
        'CIRCUIT_BREAKER_ENABLED': 'true',
        'CIRCUIT_BREAKER_FAILURE_THRESHOLD': '0.05',
        'CIRCUIT_BREAKER_RECOVERY_TIME_S': '30',
        'CIRCUIT_BREAKER_LATENCY_MULTIPLIER': '2.0',
    })
    def test_load_from_env(self):
        """Test loading configuration from environment variables."""
        # Reset singleton to force reload from env
        ConfigManager._instance = None
        ConfigManager._config = None

        # Create new manager to load from env
        manager = ConfigManager()
        config = manager.get_config()

        assert config.get_percentage_for_category('critical') == 100
        assert config.get_percentage_for_category('performance') == 75
        assert config.adapter_health['websocket'].error_threshold == 0.1
        assert config.adapter_health['websocket'].latency_threshold_ms == 300

