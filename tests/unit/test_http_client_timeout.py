"""Unit tests for HTTP client timeout configuration."""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestHTTPClientTimeoutConfiguration:
    """Test HTTP client timeout configuration."""

    def test_default_timeout_from_env(self, monkeypatch):
        """Test HTTP client uses EX_HTTP_TIMEOUT_SECONDS from environment."""
        monkeypatch.setenv("EX_HTTP_TIMEOUT_SECONDS", "600")

        # Import after setting env variable
        from utils.http_client import HttpClient

        # Create client and verify timeout is respected
        client = HttpClient(base_url="https://test.example.com", api_key="test")
        assert client._timeout == 600.0

    def test_default_timeout_fallback(self):
        """Test HTTP client has reasonable default timeout."""
        from utils.http_client import HttpClient

        # Create client without env variable
        client = HttpClient(base_url="https://test.example.com", api_key="test")
        # Should have default timeout of 300s
        assert client._timeout == 300.0

    def test_custom_timeout_override(self, monkeypatch):
        """Test HTTP client accepts custom timeout parameter."""
        # Clear env variable to test custom timeout
        monkeypatch.delenv("EX_HTTP_TIMEOUT_SECONDS", raising=False)

        from utils.http_client import HttpClient

        custom_timeout = 900.0
        client = HttpClient(base_url="https://test.example.com", api_key="test", timeout=custom_timeout)
        assert client._timeout == custom_timeout


class TestTimeoutHierarchy:
    """Test timeout hierarchy validation."""

    def test_timeout_config_exists(self):
        """Test TimeoutConfig class exists and is accessible."""
        from config import TimeoutConfig
        
        assert TimeoutConfig is not None
        assert hasattr(TimeoutConfig, 'WORKFLOW_TOOL_TIMEOUT_SECS')

    def test_workflow_tool_timeout_default(self):
        """Test workflow tool timeout has reasonable default."""
        from config import TimeoutConfig
        
        timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        assert isinstance(timeout, int)
        assert timeout > 0
        assert timeout >= 120  # Should be at least 2 minutes

    def test_daemon_timeout_calculation(self):
        """Test daemon timeout is 1.5x workflow timeout."""
        from config import TimeoutConfig
        
        workflow_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon_timeout = TimeoutConfig.get_daemon_timeout()
        
        assert daemon_timeout == int(workflow_timeout * 1.5)

    def test_shim_timeout_calculation(self):
        """Test shim timeout is 2x workflow timeout."""
        from config import TimeoutConfig
        
        workflow_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        shim_timeout = TimeoutConfig.get_shim_timeout()
        
        assert shim_timeout == int(workflow_timeout * 2.0)

    def test_client_timeout_calculation(self):
        """Test client timeout is 2.5x workflow timeout."""
        from config import TimeoutConfig
        
        workflow_timeout = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        client_timeout = TimeoutConfig.get_client_timeout()
        
        assert client_timeout == int(workflow_timeout * 2.5)

    def test_timeout_hierarchy_validation(self):
        """Test timeout hierarchy is valid (tool < daemon < shim < client)."""
        from config import TimeoutConfig
        
        tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = TimeoutConfig.get_daemon_timeout()
        shim = TimeoutConfig.get_shim_timeout()
        client = TimeoutConfig.get_client_timeout()
        
        assert tool < daemon < shim < client

    def test_validate_hierarchy_method(self):
        """Test validate_hierarchy method works."""
        from config import TimeoutConfig
        
        # Should not raise exception for valid hierarchy
        result = TimeoutConfig.validate_hierarchy()
        assert result is True

    def test_timeout_config_has_required_methods(self):
        """Test TimeoutConfig has required timeout calculation methods."""
        from config import TimeoutConfig

        # Verify all required methods exist
        assert hasattr(TimeoutConfig, 'get_daemon_timeout')
        assert hasattr(TimeoutConfig, 'get_shim_timeout')
        assert hasattr(TimeoutConfig, 'get_client_timeout')
        assert hasattr(TimeoutConfig, 'validate_hierarchy')

        # Verify methods are callable
        assert callable(TimeoutConfig.get_daemon_timeout)
        assert callable(TimeoutConfig.get_shim_timeout)
        assert callable(TimeoutConfig.get_client_timeout)
        assert callable(TimeoutConfig.validate_hierarchy)


class TestTimeoutEnvironmentVariables:
    """Test timeout environment variable handling."""

    def test_workflow_timeout_from_env(self, monkeypatch):
        """Test WORKFLOW_TOOL_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("WORKFLOW_TOOL_TIMEOUT_SECS", "600")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS == 600

    def test_simple_timeout_from_env(self, monkeypatch):
        """Test SIMPLE_TOOL_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("SIMPLE_TOOL_TIMEOUT_SECS", "90")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS == 90

    def test_expert_analysis_timeout_from_env(self, monkeypatch):
        """Test EXPERT_ANALYSIS_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("EXPERT_ANALYSIS_TIMEOUT_SECS", "240")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS == 240


class TestProviderTimeouts:
    """Test provider-specific timeout configurations."""

    def test_glm_timeout_from_env(self, monkeypatch):
        """Test GLM_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("GLM_TIMEOUT_SECS", "120")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.GLM_TIMEOUT_SECS == 120

    def test_kimi_timeout_from_env(self, monkeypatch):
        """Test KIMI_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("KIMI_TIMEOUT_SECS", "180")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.KIMI_TIMEOUT_SECS == 180

    def test_kimi_web_search_timeout_from_env(self, monkeypatch):
        """Test KIMI_WEB_SEARCH_TIMEOUT_SECS can be set via environment."""
        monkeypatch.setenv("KIMI_WEB_SEARCH_TIMEOUT_SECS", "200")
        
        # Reload config to pick up env variable
        import importlib
        import config as config_module
        importlib.reload(config_module)
        
        from config import TimeoutConfig
        assert TimeoutConfig.KIMI_WEB_SEARCH_TIMEOUT_SECS == 200


class TestTimeoutRatios:
    """Test timeout ratio calculations."""

    def test_daemon_ratio_is_1_5x(self):
        """Test daemon timeout is exactly 1.5x workflow timeout."""
        from config import TimeoutConfig
        
        workflow = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = TimeoutConfig.get_daemon_timeout()
        
        ratio = daemon / workflow
        assert abs(ratio - 1.5) < 0.01  # Allow small floating point error

    def test_shim_ratio_is_2x(self):
        """Test shim timeout is exactly 2x workflow timeout."""
        from config import TimeoutConfig
        
        workflow = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        shim = TimeoutConfig.get_shim_timeout()
        
        ratio = shim / workflow
        assert abs(ratio - 2.0) < 0.01

    def test_client_ratio_is_2_5x(self):
        """Test client timeout is exactly 2.5x workflow timeout."""
        from config import TimeoutConfig
        
        workflow = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        client = TimeoutConfig.get_client_timeout()
        
        ratio = client / workflow
        assert abs(ratio - 2.5) < 0.01


class TestTimeoutDocumentation:
    """Test timeout configuration is properly documented."""

    def test_env_example_has_timeout_docs(self):
        """Test .env.example has timeout documentation."""
        import os
        from pathlib import Path
        
        env_example = Path(".env.example")
        if env_example.exists():
            content = env_example.read_text()
            assert "TIMEOUT" in content
            assert "WORKFLOW_TOOL_TIMEOUT_SECS" in content
            assert "auto-calculated" in content.lower()

    def test_timeout_guide_exists(self):
        """Test TIMEOUT_CONFIGURATION_GUIDE.md exists."""
        from pathlib import Path

        guide = Path("tool_validation_suite/docs/current/guides/TIMEOUT_CONFIGURATION_GUIDE.md")
        assert guide.exists()

        # Use UTF-8 encoding to handle special characters
        content = guide.read_text(encoding='utf-8')
        assert "Timeout Configuration Guide" in content
        assert "Auto-Calculated" in content

