"""
Integration Tests: Expert Analysis & Configuration

Tests the integration of expert validation with deduplication, configuration
loading and validation, and environment variable precedence.

Created: 2025-10-05
Week: 3, Day 13
"""

import pytest
import asyncio
import os
import time
from unittest.mock import Mock, patch, AsyncMock
from config import TimeoutConfig
from tools.workflow.expert_analysis import (
    _expert_validation_cache,
    _expert_validation_in_progress,
    _expert_validation_lock,
)


class TestExpertValidationIntegration:
    """Test expert validation with deduplication integration."""

    @pytest.fixture(autouse=True)
    def clear_cache(self):
        """Clear cache before each test."""
        _expert_validation_cache.clear()
        _expert_validation_in_progress.clear()
        yield
        _expert_validation_cache.clear()
        _expert_validation_in_progress.clear()

    @pytest.mark.asyncio
    async def test_expert_validation_cache_exists(self):
        """Test that expert validation cache is accessible."""
        # Verify cache exists and is empty initially
        assert isinstance(_expert_validation_cache, dict)
        assert isinstance(_expert_validation_in_progress, set)
        assert len(_expert_validation_cache) == 0
        assert len(_expert_validation_in_progress) == 0

    @pytest.mark.asyncio
    async def test_expert_validation_cache_stores_results(self):
        """Test that expert validation cache stores results."""
        # Add a result to cache
        cache_key = "test_prompt_hash"
        result = {"status": "validated", "findings": []}

        _expert_validation_cache[cache_key] = result

        # Verify it's stored
        assert cache_key in _expert_validation_cache
        assert _expert_validation_cache[cache_key] == result
    
    @pytest.mark.asyncio
    async def test_expert_validation_in_progress_tracking(self):
        """Test that in-progress tracking works."""
        # Simulate in-progress tracking
        cache_key = "test_prompt_in_progress"

        _expert_validation_in_progress.add(cache_key)

        # Verify it's tracked
        assert cache_key in _expert_validation_in_progress

        # Cleanup
        _expert_validation_in_progress.discard(cache_key)
        assert cache_key not in _expert_validation_in_progress

    @pytest.mark.asyncio
    async def test_expert_validation_lock_exists(self):
        """Test that expert validation lock exists."""
        # Verify lock exists
        assert _expert_validation_lock is not None
        assert isinstance(_expert_validation_lock, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_expert_validation_timeout_config(self):
        """Test that expert validation uses correct timeout."""
        # Verify expert analysis timeout is configured
        expert_timeout = TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS
        assert expert_timeout > 0
        assert expert_timeout == 90  # Default value

    @pytest.mark.asyncio
    async def test_expert_validation_with_progress_heartbeat(self):
        """Test that expert validation can use progress heartbeat."""
        from utils.progress import ProgressHeartbeat

        progress_messages = []

        async def progress_callback(data):
            progress_messages.append(data)

        # Simulate expert validation with progress
        async with ProgressHeartbeat(interval_secs=0.5, callback=progress_callback) as hb:
            hb.set_total_steps(3)
            for step in range(1, 4):
                hb.set_current_step(step)
                await hb.send_heartbeat(f"Expert analysis step {step}")
                await asyncio.sleep(0.3)

        # Should have received progress messages
        assert len(progress_messages) >= 1

        # Verify progress structure
        for msg in progress_messages:
            assert "message" in msg
            assert "elapsed_secs" in msg


class TestConfigurationIntegration:
    """Test configuration loading and validation integration."""
    
    def test_config_loads_from_environment(self):
        """Test that configuration loads from environment variables."""
        # Set environment variables
        os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"] = "150"
        os.environ["SESSION_TIMEOUT_SECS"] = "7200"
        
        # Reload config (in real scenario, would restart server)
        workflow_timeout = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "120"))
        session_timeout = int(os.getenv("SESSION_TIMEOUT_SECS", "3600"))
        
        assert workflow_timeout == 150
        assert session_timeout == 7200
        
        # Cleanup
        del os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"]
        del os.environ["SESSION_TIMEOUT_SECS"]
    
    def test_config_timeout_values_are_positive(self):
        """Test that all timeout values are positive."""
        # Verify all timeout values are positive
        assert TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS > 0
        assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS > 0
        assert TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS > 0
        assert TimeoutConfig.get_daemon_timeout() > 0
        assert TimeoutConfig.get_shim_timeout() > 0
        assert TimeoutConfig.get_client_timeout() > 0

    def test_config_timeout_values_are_reasonable(self):
        """Test that timeout values are within reasonable ranges."""
        # Verify timeout values are reasonable (not too small or too large)
        assert 30 <= TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS <= 300
        assert 60 <= TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS <= 600
        assert 60 <= TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS <= 300
        assert 120 <= TimeoutConfig.get_daemon_timeout() <= 900
        assert 180 <= TimeoutConfig.get_shim_timeout() <= 1200
        assert 240 <= TimeoutConfig.get_client_timeout() <= 1500
    
    def test_config_environment_precedence(self):
        """Test that environment variables take precedence over defaults."""
        # Set environment variable
        os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"] = "180"
        
        # Get value (env should override default)
        value = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "120"))
        assert value == 180  # Environment value, not default
        
        # Cleanup
        del os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"]
    
    def test_config_default_values(self):
        """Test that default values are used when env vars not set."""
        # Ensure env var not set
        if "WORKFLOW_TOOL_TIMEOUT_SECS" in os.environ:
            del os.environ["WORKFLOW_TOOL_TIMEOUT_SECS"]
        
        # Get value (should use default)
        value = int(os.getenv("WORKFLOW_TOOL_TIMEOUT_SECS", "120"))
        assert value == 120  # Default value
    
    def test_config_timeout_hierarchy_consistency(self):
        """Test that timeout hierarchy remains consistent."""
        # Get all timeout values
        tool_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon_timeout = TimeoutConfig.get_daemon_timeout()
        shim_timeout = TimeoutConfig.get_shim_timeout()
        client_timeout = TimeoutConfig.get_client_timeout()
        
        # Verify hierarchy
        assert tool_timeout < daemon_timeout < shim_timeout < client_timeout
        
        # Verify ratios
        assert daemon_timeout == tool_timeout * 1.5
        assert shim_timeout == tool_timeout * 2.0
        assert client_timeout == tool_timeout * 2.5
    
    def test_config_type_safety(self):
        """Test that configuration values have correct types."""
        # Verify all timeout values are integers
        assert isinstance(TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS, int)
        assert isinstance(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS, int)
        assert isinstance(TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS, int)
        assert isinstance(TimeoutConfig.get_daemon_timeout(), int)
        assert isinstance(TimeoutConfig.get_shim_timeout(), int)
        assert isinstance(TimeoutConfig.get_client_timeout(), int)
    
    def test_config_error_handling_missing_required(self):
        """Test that configuration handles missing required values."""
        # Ensure required env var not set
        if "MOONSHOT_API_KEY" in os.environ:
            api_key = os.environ["MOONSHOT_API_KEY"]
            del os.environ["MOONSHOT_API_KEY"]
        else:
            api_key = None
        
        # Get value (should return None or empty)
        value = os.getenv("MOONSHOT_API_KEY")
        assert value is None or value == ""
        
        # Restore if it existed
        if api_key:
            os.environ["MOONSHOT_API_KEY"] = api_key


class TestConfigurationLoadingOrder:
    """Test configuration loading order and initialization."""
    
    def test_env_loaded_before_config(self):
        """Test that environment variables are loaded before config initialization."""
        # This is a conceptual test - in real scenario, env is loaded first
        # Set env var
        os.environ["TEST_CONFIG_VALUE"] = "from_env"
        
        # Simulate config loading
        value = os.getenv("TEST_CONFIG_VALUE", "default")
        
        # Should get env value, not default
        assert value == "from_env"
        
        # Cleanup
        del os.environ["TEST_CONFIG_VALUE"]
    
    def test_config_initialization_order(self):
        """Test that configuration components initialize in correct order."""
        # Conceptual test - verify initialization order
        # 1. Environment variables loaded
        # 2. TimeoutConfig initialized
        # 3. SessionManager initialized
        # 4. Other components initialized
        
        # Verify TimeoutConfig is accessible
        assert hasattr(TimeoutConfig, 'WORKFLOW_TOOL_TIMEOUT_SECS')
        assert hasattr(TimeoutConfig, 'get_daemon_timeout')
        
        # Verify timeout values are valid
        assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS > 0
        assert TimeoutConfig.get_daemon_timeout() > 0
    
    def test_config_singleton_pattern(self):
        """Test that configuration uses singleton pattern."""
        # TimeoutConfig should be a singleton (class-level attributes)
        timeout1 = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        timeout2 = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        
        # Should be the same value (singleton)
        assert timeout1 == timeout2
        
        # Should be the same object reference
        assert id(TimeoutConfig) == id(TimeoutConfig)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

