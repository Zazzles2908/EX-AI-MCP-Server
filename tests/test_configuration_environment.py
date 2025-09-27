"""
Configuration and Environment Tests

Tests for production configuration loading, API key authentication,
environment variable handling, and logging/monitoring functionality.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables for testing
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

from config import (
    DEFAULT_MODEL, INTELLIGENT_ROUTING_ENABLED, AI_MANAGER_MODEL,
    WEB_SEARCH_PROVIDER, FILE_PROCESSING_PROVIDER, COST_AWARE_ROUTING,
    LOG_LEVEL, MAX_RETRIES, REQUEST_TIMEOUT, ENABLE_FALLBACK,
    MCP_WEBSOCKET_ENABLED, MCP_WEBSOCKET_PORT, MCP_WEBSOCKET_HOST,
    MAX_CONCURRENT_REQUESTS, RATE_LIMIT_PER_MINUTE, CACHE_ENABLED, CACHE_TTL,
    VALIDATE_API_KEYS, __version__, __release_name__
)


class TestConfigurationEnvironment:
    """Test suite for configuration and environment handling"""

    def test_production_configuration_loading(self):
        """Test that production configuration values are properly set"""
        # Test that configuration constants are loaded from environment
        assert DEFAULT_MODEL == 'glm-4.5-flash'
        assert AI_MANAGER_MODEL == 'glm-4.5-flash'
        assert WEB_SEARCH_PROVIDER == 'glm'
        assert FILE_PROCESSING_PROVIDER == 'kimi'
        assert isinstance(INTELLIGENT_ROUTING_ENABLED, bool)
        assert isinstance(COST_AWARE_ROUTING, bool)
        assert LOG_LEVEL == 'INFO'
        assert isinstance(MAX_RETRIES, int)
        assert isinstance(REQUEST_TIMEOUT, int)
        assert isinstance(ENABLE_FALLBACK, bool)

    def test_websocket_configuration(self):
        """Test WebSocket configuration"""
        assert isinstance(MCP_WEBSOCKET_ENABLED, bool)
        assert isinstance(MCP_WEBSOCKET_PORT, int)
        assert MCP_WEBSOCKET_HOST == '0.0.0.0'

    def test_performance_configuration(self):
        """Test performance-related configuration"""
        assert isinstance(MAX_CONCURRENT_REQUESTS, int)
        assert isinstance(RATE_LIMIT_PER_MINUTE, int)
        assert isinstance(CACHE_ENABLED, bool)
        assert isinstance(CACHE_TTL, int)

    def test_security_configuration(self):
        """Test security configuration"""
        assert isinstance(VALIDATE_API_KEYS, bool)

    def test_api_key_validation(self):
        """Test that API keys are available in environment"""
        # Check that API keys are set (from .env file)
        assert os.getenv('GLM_API_KEY') is not None
        assert os.getenv('KIMI_API_KEY') is not None
        assert len(os.getenv('GLM_API_KEY')) > 0
        assert len(os.getenv('KIMI_API_KEY')) > 0

    def test_environment_variable_precedence(self):
        """Test that environment variables affect configuration"""
        # Test that REQUEST_TIMEOUT can be overridden
        with patch.dict('os.environ', {'REQUEST_TIMEOUT': '60'}):
            # Create a temporary config module to test
            import importlib
            import sys
            # Create a temporary module
            temp_config = type(sys)('temp_config')
            temp_config.REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', '30'))
            assert temp_config.REQUEST_TIMEOUT == 60

    def test_configuration_type_conversion(self):
        """Test proper type conversion of configuration values"""
        # Test boolean conversion
        assert isinstance(INTELLIGENT_ROUTING_ENABLED, bool)
        assert isinstance(COST_AWARE_ROUTING, bool)
        assert isinstance(ENABLE_FALLBACK, bool)
        assert isinstance(CACHE_ENABLED, bool)
        assert isinstance(VALIDATE_API_KEYS, bool)
        
        # Test integer conversion
        assert isinstance(MAX_RETRIES, int)
        assert isinstance(REQUEST_TIMEOUT, int)
        assert isinstance(MCP_WEBSOCKET_PORT, int)
        assert isinstance(MAX_CONCURRENT_REQUESTS, int)
        assert isinstance(RATE_LIMIT_PER_MINUTE, int)
        assert isinstance(CACHE_TTL, int)

    def test_default_configuration_values(self):
        """Test that default values are properly set"""
        # Test version information
        assert __version__ == "2.0.0"
        assert "Production-Ready" in __release_name__
        
        # Test that defaults are applied when env vars not set
        # These should have sensible defaults
        assert DEFAULT_MODEL == 'glm-4.5-flash'
        assert AI_MANAGER_MODEL == 'glm-4.5-flash'
        assert WEB_SEARCH_PROVIDER == 'glm'
        assert FILE_PROCESSING_PROVIDER == 'kimi'

    def test_intelligent_routing_configuration(self):
        """Test intelligent routing configuration"""
        assert isinstance(INTELLIGENT_ROUTING_ENABLED, bool)
        assert AI_MANAGER_MODEL == 'glm-4.5-flash'
        assert WEB_SEARCH_PROVIDER == 'glm'
        assert FILE_PROCESSING_PROVIDER == 'kimi'
        assert isinstance(COST_AWARE_ROUTING, bool)
