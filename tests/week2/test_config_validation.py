"""
Tests for MCP Configuration Validation

This test suite validates:
1. Configuration template structure
2. Configuration validation logic
3. Timeout consistency across configs
4. Required environment variables
5. Configuration structure validation
"""

import json
import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.validate_mcp_configs import (
    validate_timeout_values,
    validate_required_env_vars,
    validate_structure,
    compare_timeout_consistency,
    load_json,
)


class TestTemplateStructure:
    """Test that the configuration template has the correct structure."""
    
    def test_template_exists(self):
        """Test that the template file exists."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        assert template_path.exists(), "Template file should exist"
    
    def test_template_valid_json(self):
        """Test that the template is valid JSON."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        template = load_json(template_path)
        assert isinstance(template, dict), "Template should be a dictionary"
    
    def test_template_has_required_sections(self):
        """Test that the template has all required sections."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        template = load_json(template_path)
        
        required_sections = [
            "_standard_env_vars",
            "_client_specific_vars",
            "_config_structure",
            "_validation_rules",
        ]
        
        for section in required_sections:
            assert section in template, f"Template should have {section} section"
    
    def test_template_validation_rules(self):
        """Test that validation rules are properly defined."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        template = load_json(template_path)
        
        validation_rules = template["_validation_rules"]
        assert "required_env_vars" in validation_rules
        assert "timeout_values" in validation_rules
        assert "required_structure_fields" in validation_rules
        
        # Check timeout values
        timeout_values = validation_rules["timeout_values"]
        assert timeout_values["SIMPLE_TOOL_TIMEOUT_SECS"] == 60
        assert timeout_values["WORKFLOW_TOOL_TIMEOUT_SECS"] == 120
        assert timeout_values["EXPERT_ANALYSIS_TIMEOUT_SECS"] == 90
        assert timeout_values["GLM_TIMEOUT_SECS"] == 90
        assert timeout_values["KIMI_TIMEOUT_SECS"] == 120
        assert timeout_values["KIMI_WEB_SEARCH_TIMEOUT_SECS"] == 150


class TestConfigurationFiles:
    """Test that all configuration files exist and are valid."""
    
    def test_auggie_config_exists(self):
        """Test that Auggie config exists."""
        config_path = project_root / "Daemon" / "mcp-config.auggie.json"
        assert config_path.exists(), "Auggie config should exist"
    
    def test_augmentcode_config_exists(self):
        """Test that Augment Code config exists."""
        config_path = project_root / "Daemon" / "mcp-config.augmentcode.json"
        assert config_path.exists(), "Augment Code config should exist"
    
    def test_claude_config_exists(self):
        """Test that Claude config exists."""
        config_path = project_root / "Daemon" / "mcp-config.claude.json"
        assert config_path.exists(), "Claude config should exist"
    
    def test_all_configs_valid_json(self):
        """Test that all configs are valid JSON."""
        config_names = ["auggie", "augmentcode", "claude"]
        
        for name in config_names:
            config_path = project_root / "Daemon" / f"mcp-config.{name}.json"
            config = load_json(config_path)
            assert isinstance(config, dict), f"{name} config should be a dictionary"


class TestTimeoutValidation:
    """Test timeout value validation."""
    
    def test_auggie_timeout_values(self):
        """Test that Auggie config has correct timeout values."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.auggie.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_timeout_values(config, "auggie", template)
        assert len(errors) == 0, f"Auggie config should have no timeout errors: {errors}"
    
    def test_augmentcode_timeout_values(self):
        """Test that Augment Code config has correct timeout values."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.augmentcode.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_timeout_values(config, "augmentcode", template)
        assert len(errors) == 0, f"Augment Code config should have no timeout errors: {errors}"
    
    def test_claude_timeout_values(self):
        """Test that Claude config has correct timeout values."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.claude.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_timeout_values(config, "claude", template)
        assert len(errors) == 0, f"Claude config should have no timeout errors: {errors}"


class TestRequiredEnvVars:
    """Test required environment variable validation."""
    
    def test_auggie_required_env_vars(self):
        """Test that Auggie config has all required env vars."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.auggie.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_required_env_vars(config, "auggie", template)
        assert len(errors) == 0, f"Auggie config should have all required env vars: {errors}"
    
    def test_augmentcode_required_env_vars(self):
        """Test that Augment Code config has all required env vars."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.augmentcode.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_required_env_vars(config, "augmentcode", template)
        assert len(errors) == 0, f"Augment Code config should have all required env vars: {errors}"
    
    def test_claude_required_env_vars(self):
        """Test that Claude config has all required env vars."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.claude.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_required_env_vars(config, "claude", template)
        assert len(errors) == 0, f"Claude config should have all required env vars: {errors}"


class TestStructureValidation:
    """Test configuration structure validation."""
    
    def test_auggie_structure(self):
        """Test that Auggie config has correct structure."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.auggie.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_structure(config, "auggie", template)
        assert len(errors) == 0, f"Auggie config should have correct structure: {errors}"
    
    def test_augmentcode_structure(self):
        """Test that Augment Code config has correct structure."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.augmentcode.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_structure(config, "augmentcode", template)
        assert len(errors) == 0, f"Augment Code config should have correct structure: {errors}"
    
    def test_claude_structure(self):
        """Test that Claude config has correct structure."""
        template_path = project_root / "Daemon" / "mcp-config.template.json"
        config_path = project_root / "Daemon" / "mcp-config.claude.json"
        
        template = load_json(template_path)
        config = load_json(config_path)
        
        errors = validate_structure(config, "claude", template)
        assert len(errors) == 0, f"Claude config should have correct structure: {errors}"


class TestConsistencyAcrossConfigs:
    """Test that timeout values are consistent across all configs."""
    
    def test_timeout_consistency(self):
        """Test that all configs have identical timeout values."""
        configs = {}
        config_names = ["auggie", "augmentcode", "claude"]
        
        for name in config_names:
            config_path = project_root / "Daemon" / f"mcp-config.{name}.json"
            configs[name] = load_json(config_path)
        
        consistent, errors = compare_timeout_consistency(configs)
        assert consistent, f"Timeout values should be consistent across all configs: {errors}"
    
    def test_all_configs_have_same_timeout_count(self):
        """Test that all configs have the same number of timeout variables."""
        timeout_vars = [
            "SIMPLE_TOOL_TIMEOUT_SECS",
            "WORKFLOW_TOOL_TIMEOUT_SECS",
            "EXPERT_ANALYSIS_TIMEOUT_SECS",
            "GLM_TIMEOUT_SECS",
            "KIMI_TIMEOUT_SECS",
            "KIMI_WEB_SEARCH_TIMEOUT_SECS",
        ]
        
        config_names = ["auggie", "augmentcode", "claude"]
        
        for name in config_names:
            config_path = project_root / "Daemon" / f"mcp-config.{name}.json"
            config = load_json(config_path)
            
            # Extract env vars
            if name == "claude":
                env_vars = config["servers"]["exai-mcp"]["env"]
            elif name == "auggie":
                env_vars = config["mcpServers"]["exai"]["env"]
            elif name == "augmentcode":
                env_vars = config["mcpServers"]["EXAI-WS"]["env"]
            
            # Check that all timeout vars are present
            for var in timeout_vars:
                assert var in env_vars, f"{name} config should have {var}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

