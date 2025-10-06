"""
Test suite for TimeoutConfig coordinated timeout hierarchy.

This test suite validates the timeout configuration implementation from Day 1-2
of the Master Fix Implementation Plan.

Tests:
1. TimeoutConfig class exists and is importable
2. Tool-level timeout constants are set correctly
3. Infrastructure timeout methods return correct values
4. Timeout hierarchy is valid (tool < daemon < shim < client)
5. Timeout ratios are correct (1.5x, 2x, 2.5x)
6. validate_hierarchy() method works correctly
7. get_timeout_summary() returns complete information
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from config import TimeoutConfig


class TestTimeoutConfigExists:
    """Test that TimeoutConfig class exists and is importable."""
    
    def test_timeout_config_importable(self):
        """TimeoutConfig should be importable from config module."""
        assert TimeoutConfig is not None
        assert hasattr(TimeoutConfig, 'SIMPLE_TOOL_TIMEOUT_SECS')
        assert hasattr(TimeoutConfig, 'WORKFLOW_TOOL_TIMEOUT_SECS')
        assert hasattr(TimeoutConfig, 'EXPERT_ANALYSIS_TIMEOUT_SECS')


class TestToolLevelTimeouts:
    """Test that tool-level timeout constants are set correctly."""
    
    def test_simple_tool_timeout(self):
        """Simple tool timeout should be 60 seconds."""
        assert TimeoutConfig.SIMPLE_TOOL_TIMEOUT_SECS == 60
    
    def test_workflow_tool_timeout(self):
        """Workflow tool timeout should be 120 seconds."""
        assert TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS == 120
    
    def test_expert_analysis_timeout(self):
        """Expert analysis timeout should be 90 seconds."""
        assert TimeoutConfig.EXPERT_ANALYSIS_TIMEOUT_SECS == 90


class TestProviderTimeouts:
    """Test that provider timeout constants are set correctly."""
    
    def test_glm_timeout(self):
        """GLM timeout should be 90 seconds."""
        assert TimeoutConfig.GLM_TIMEOUT_SECS == 90
    
    def test_kimi_timeout(self):
        """Kimi timeout should be 120 seconds."""
        assert TimeoutConfig.KIMI_TIMEOUT_SECS == 120
    
    def test_kimi_web_search_timeout(self):
        """Kimi web search timeout should be 150 seconds."""
        assert TimeoutConfig.KIMI_WEB_SEARCH_TIMEOUT_SECS == 150


class TestInfrastructureTimeouts:
    """Test that infrastructure timeout methods return correct values."""
    
    def test_daemon_timeout(self):
        """Daemon timeout should be 180 seconds (1.5x workflow tool timeout)."""
        expected = int(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS * 1.5)
        assert TimeoutConfig.get_daemon_timeout() == expected
        assert TimeoutConfig.get_daemon_timeout() == 180
    
    def test_shim_timeout(self):
        """Shim timeout should be 240 seconds (2x workflow tool timeout)."""
        expected = int(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS * 2.0)
        assert TimeoutConfig.get_shim_timeout() == expected
        assert TimeoutConfig.get_shim_timeout() == 240
    
    def test_client_timeout(self):
        """Client timeout should be 300 seconds (2.5x workflow tool timeout)."""
        expected = int(TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS * 2.5)
        assert TimeoutConfig.get_client_timeout() == expected
        assert TimeoutConfig.get_client_timeout() == 300


class TestTimeoutHierarchy:
    """Test that timeout hierarchy is valid."""
    
    def test_hierarchy_order(self):
        """Timeouts should follow: tool < daemon < shim < client."""
        tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = TimeoutConfig.get_daemon_timeout()
        shim = TimeoutConfig.get_shim_timeout()
        client = TimeoutConfig.get_client_timeout()
        
        assert tool < daemon, f"Tool timeout ({tool}s) should be less than daemon ({daemon}s)"
        assert daemon < shim, f"Daemon timeout ({daemon}s) should be less than shim ({shim}s)"
        assert shim < client, f"Shim timeout ({shim}s) should be less than client ({client}s)"
    
    def test_daemon_ratio(self):
        """Daemon timeout should be at least 1.5x tool timeout."""
        tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        daemon = TimeoutConfig.get_daemon_timeout()
        ratio = daemon / tool
        assert ratio >= 1.5, f"Daemon ratio ({ratio:.2f}x) should be at least 1.5x"
    
    def test_shim_ratio(self):
        """Shim timeout should be at least 2x tool timeout."""
        tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        shim = TimeoutConfig.get_shim_timeout()
        ratio = shim / tool
        assert ratio >= 2.0, f"Shim ratio ({ratio:.2f}x) should be at least 2.0x"
    
    def test_client_ratio(self):
        """Client timeout should be at least 2.5x tool timeout."""
        tool = TimeoutConfig.WORKFLOW_TOOL_TIMEOUT_SECS
        client = TimeoutConfig.get_client_timeout()
        ratio = client / tool
        assert ratio >= 2.5, f"Client ratio ({ratio:.2f}x) should be at least 2.5x"


class TestValidateHierarchy:
    """Test that validate_hierarchy() method works correctly."""
    
    def test_validate_hierarchy_returns_true(self):
        """validate_hierarchy() should return True for valid configuration."""
        result = TimeoutConfig.validate_hierarchy()
        assert result is True
    
    def test_validate_hierarchy_no_exception(self):
        """validate_hierarchy() should not raise exception for valid configuration."""
        try:
            TimeoutConfig.validate_hierarchy()
        except ValueError as e:
            pytest.fail(f"validate_hierarchy() raised ValueError: {e}")


class TestTimeoutSummary:
    """Test that get_timeout_summary() returns complete information."""
    
    def test_summary_structure(self):
        """get_timeout_summary() should return dict with expected keys."""
        summary = TimeoutConfig.get_timeout_summary()
        assert isinstance(summary, dict)
        assert "tool_timeouts" in summary
        assert "infrastructure_timeouts" in summary
        assert "provider_timeouts" in summary
        assert "ratios" in summary
        assert "hierarchy_valid" in summary
    
    def test_summary_tool_timeouts(self):
        """Summary should include all tool timeout values."""
        summary = TimeoutConfig.get_timeout_summary()
        tool_timeouts = summary["tool_timeouts"]
        assert tool_timeouts["simple"] == 60
        assert tool_timeouts["workflow"] == 120
        assert tool_timeouts["expert_analysis"] == 90
    
    def test_summary_infrastructure_timeouts(self):
        """Summary should include all infrastructure timeout values."""
        summary = TimeoutConfig.get_timeout_summary()
        infra_timeouts = summary["infrastructure_timeouts"]
        assert infra_timeouts["daemon"] == 180
        assert infra_timeouts["shim"] == 240
        assert infra_timeouts["client"] == 300
    
    def test_summary_provider_timeouts(self):
        """Summary should include all provider timeout values."""
        summary = TimeoutConfig.get_timeout_summary()
        provider_timeouts = summary["provider_timeouts"]
        assert provider_timeouts["glm"] == 90
        assert provider_timeouts["kimi"] == 120
        assert provider_timeouts["kimi_web_search"] == 150
    
    def test_summary_ratios(self):
        """Summary should include correct timeout ratios."""
        summary = TimeoutConfig.get_timeout_summary()
        ratios = summary["ratios"]
        assert ratios["daemon_to_tool"] == 1.5
        assert ratios["shim_to_tool"] == 2.0
        assert ratios["client_to_tool"] == 2.5
    
    def test_summary_hierarchy_valid(self):
        """Summary should indicate hierarchy is valid."""
        summary = TimeoutConfig.get_timeout_summary()
        assert summary["hierarchy_valid"] is True


class TestIntegration:
    """Integration tests for timeout configuration."""
    
    def test_daemon_imports_timeout_config(self):
        """Daemon should be able to import and use TimeoutConfig."""
        try:
            from src.daemon.ws_server import CALL_TIMEOUT
            assert CALL_TIMEOUT == 180
        except ImportError:
            pytest.skip("Daemon module not available")
    
    def test_workflow_base_imports_timeout_config(self):
        """Workflow base should be able to import and use TimeoutConfig."""
        try:
            from tools.workflow.base import WorkflowTool
            # Can't instantiate abstract class, but can check it imports
            assert hasattr(WorkflowTool, '__init__')
        except ImportError:
            pytest.skip("Workflow base module not available")
    
    def test_expert_analysis_imports_timeout_config(self):
        """Expert analysis should be able to import and use TimeoutConfig."""
        try:
            from tools.workflow.expert_analysis import ExpertAnalysisMixin
            ea = ExpertAnalysisMixin()
            timeout = ea.get_expert_timeout_secs()
            assert timeout == 90.0
        except ImportError:
            pytest.skip("Expert analysis module not available")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])

