#!/usr/bin/env python3
"""
MCP Configuration Validator

This script validates that all MCP client configurations (Auggie, Augment Code, Claude Desktop)
are consistent with the base template and follow the standardized timeout hierarchy.

Usage:
    python scripts/validate_mcp_configs.py

Exit codes:
    0 - All configurations valid
    1 - Validation errors found
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def load_json(path: Path) -> Dict[str, Any]:
    """Load and parse JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"{RED}✗ Failed to load {path}: {e}{RESET}")
        sys.exit(1)


def validate_timeout_values(config: Dict[str, Any], client_name: str, template: Dict[str, Any]) -> List[str]:
    """Validate that timeout values match the template."""
    errors = []
    expected_timeouts = template["_validation_rules"]["timeout_values"]
    
    # Extract env vars from config
    env_vars = {}
    try:
        if client_name == "claude":
            env_vars = config["servers"]["exai-mcp"]["env"]
        elif client_name == "auggie":
            env_vars = config["mcpServers"]["exai"]["env"]
        elif client_name == "augmentcode":
            env_vars = config["mcpServers"]["EXAI-WS"]["env"]
    except KeyError as e:
        errors.append(f"Missing expected structure: {e}")
        return errors
    
    # Check each timeout value
    for timeout_name, expected_value in expected_timeouts.items():
        actual_value = env_vars.get(timeout_name)
        if actual_value is None:
            errors.append(f"Missing timeout: {timeout_name}")
        elif str(actual_value) != str(expected_value):
            errors.append(
                f"Incorrect timeout: {timeout_name} = {actual_value} (expected {expected_value})"
            )
    
    return errors


def validate_required_env_vars(config: Dict[str, Any], client_name: str, template: Dict[str, Any]) -> List[str]:
    """Validate that all required environment variables are present."""
    errors = []
    required_vars = template["_validation_rules"]["required_env_vars"]
    
    # Extract env vars from config
    env_vars = {}
    try:
        if client_name == "claude":
            env_vars = config["servers"]["exai-mcp"]["env"]
        elif client_name == "auggie":
            env_vars = config["mcpServers"]["exai"]["env"]
        elif client_name == "augmentcode":
            env_vars = config["mcpServers"]["EXAI-WS"]["env"]
    except KeyError as e:
        errors.append(f"Missing expected structure: {e}")
        return errors
    
    # Check each required variable
    for var_name in required_vars:
        if var_name not in env_vars:
            errors.append(f"Missing required env var: {var_name}")
    
    return errors


def validate_structure(config: Dict[str, Any], client_name: str, template: Dict[str, Any]) -> List[str]:
    """Validate that the configuration structure is correct."""
    errors = []
    required_fields = template["_validation_rules"]["required_structure_fields"]
    
    # Extract server config
    server_config = {}
    try:
        if client_name == "claude":
            server_config = config["servers"]["exai-mcp"]
        elif client_name == "auggie":
            server_config = config["mcpServers"]["exai"]
        elif client_name == "augmentcode":
            server_config = config["mcpServers"]["EXAI-WS"]
    except KeyError as e:
        errors.append(f"Missing expected structure: {e}")
        return errors
    
    # Check each required field
    for field_name in required_fields:
        if field_name not in server_config:
            errors.append(f"Missing required field: {field_name}")
    
    return errors


def validate_config(config_path: Path, client_name: str, template: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a single configuration file."""
    print(f"\n{BLUE}Validating {client_name} configuration...{RESET}")
    
    config = load_json(config_path)
    all_errors = []
    
    # Run all validations
    all_errors.extend(validate_structure(config, client_name, template))
    all_errors.extend(validate_required_env_vars(config, client_name, template))
    all_errors.extend(validate_timeout_values(config, client_name, template))
    
    if all_errors:
        print(f"{RED}✗ {len(all_errors)} error(s) found:{RESET}")
        for error in all_errors:
            print(f"  {RED}• {error}{RESET}")
        return False, all_errors
    else:
        print(f"{GREEN}✓ Configuration valid{RESET}")
        return True, []


def compare_timeout_consistency(configs: Dict[str, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """Verify that timeout values are consistent across all configs."""
    print(f"\n{BLUE}Checking timeout consistency across all configs...{RESET}")
    
    errors = []
    timeout_vars = [
        "SIMPLE_TOOL_TIMEOUT_SECS",
        "WORKFLOW_TOOL_TIMEOUT_SECS",
        "EXPERT_ANALYSIS_TIMEOUT_SECS",
        "GLM_TIMEOUT_SECS",
        "KIMI_TIMEOUT_SECS",
        "KIMI_WEB_SEARCH_TIMEOUT_SECS",
    ]
    
    # Extract timeout values from each config
    timeout_values = {}
    for client_name, config in configs.items():
        try:
            if client_name == "claude":
                env_vars = config["servers"]["exai-mcp"]["env"]
            elif client_name == "auggie":
                env_vars = config["mcpServers"]["exai"]["env"]
            elif client_name == "augmentcode":
                env_vars = config["mcpServers"]["EXAI-WS"]["env"]
            
            timeout_values[client_name] = {
                var: env_vars.get(var) for var in timeout_vars
            }
        except KeyError:
            errors.append(f"Could not extract timeout values from {client_name}")
            continue
    
    # Compare values across configs
    for var in timeout_vars:
        values = {client: vals[var] for client, vals in timeout_values.items()}
        unique_values = set(values.values())
        
        if len(unique_values) > 1:
            errors.append(
                f"Inconsistent {var}: " + ", ".join(f"{client}={val}" for client, val in values.items())
            )
    
    if errors:
        print(f"{RED}✗ {len(errors)} inconsistency(ies) found:{RESET}")
        for error in errors:
            print(f"  {RED}• {error}{RESET}")
        return False, errors
    else:
        print(f"{GREEN}✓ All timeout values consistent across configs{RESET}")
        return True, []


def main():
    """Main validation function."""
    print(f"{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}MCP Configuration Validator{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}")
    
    # Paths
    daemon_dir = Path(__file__).parent.parent / "Daemon"
    template_path = daemon_dir / "mcp-config.template.json"
    
    config_paths = {
        "auggie": daemon_dir / "mcp-config.auggie.json",
        "augmentcode": daemon_dir / "mcp-config.augmentcode.json",
        "claude": daemon_dir / "mcp-config.claude.json",
    }
    
    # Load template
    print(f"\n{BLUE}Loading template...{RESET}")
    template = load_json(template_path)
    print(f"{GREEN}✓ Template loaded{RESET}")
    
    # Validate each config
    all_valid = True
    all_errors = {}
    configs = {}
    
    for client_name, config_path in config_paths.items():
        if not config_path.exists():
            print(f"{RED}✗ Config file not found: {config_path}{RESET}")
            all_valid = False
            continue
        
        configs[client_name] = load_json(config_path)
        valid, errors = validate_config(config_path, client_name, template)
        if not valid:
            all_valid = False
            all_errors[client_name] = errors
    
    # Check consistency across configs
    if configs:
        consistent, consistency_errors = compare_timeout_consistency(configs)
        if not consistent:
            all_valid = False
            all_errors["consistency"] = consistency_errors
    
    # Summary
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    if all_valid:
        print(f"{GREEN}✓ All configurations valid and consistent!{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")
        return 0
    else:
        print(f"{RED}✗ Validation failed with errors{RESET}")
        print(f"{BLUE}{'=' * 60}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

