"""
Tool Filtering and Management Module

This module handles tool filtering, validation, and configuration
for the EX MCP Server tool registry.
"""

import logging
from typing import Any, Dict, Set

logger = logging.getLogger(__name__)
import os
from src.providers.registry import ModelProviderRegistry
from src.providers.base import ProviderType


# Core tool set that cannot be disabled via DISABLED_TOOLS (safety)
ESSENTIAL_TOOLS: set[str] = {
    "chat","thinkdeep","planner","consensus","codereview","precommit",
    "debug","secaudit","docgen","analyze","refactor","tracer",
    "testgen","challenge","listmodels","version","selfcheck"
}


def parse_disabled_tools_env() -> set[str]:
    """
    Parse the DISABLED_TOOLS environment variable into a set of tool names.

    Returns:
        Set of lowercase tool names to disable, empty set if none specified
    """
    disabled_tools_env = os.getenv("DISABLED_TOOLS", "").strip()
    if not disabled_tools_env:
        return set()
    return {t.strip().lower() for t in disabled_tools_env.split(",") if t.strip()}


def validate_disabled_tools(disabled_tools: set[str], all_tools: dict[str, Any]) -> None:
    """
    Validate the disabled tools list and log appropriate warnings.

    Args:
        disabled_tools: Set of tool names requested to be disabled
        all_tools: Dictionary of all available tool instances
    """
    essential_disabled = disabled_tools & ESSENTIAL_TOOLS
    if essential_disabled:
        logger.warning(f"Cannot disable essential tools: {sorted(essential_disabled)}")
    unknown_tools = disabled_tools - set(all_tools.keys())
    if unknown_tools:
        logger.warning(f"Unknown tools in DISABLED_TOOLS: {sorted(unknown_tools)}")


def apply_tool_filter(all_tools: dict[str, Any], disabled_tools: set[str]) -> dict[str, Any]:
    """
    Apply the disabled tools filter to create the final tools dictionary.

    Args:
        all_tools: Dictionary of all available tool instances
        disabled_tools: Set of tool names to disable

    Returns:
        Dictionary containing only enabled tools
    """
    enabled_tools = {}
    for tool_name, tool_instance in all_tools.items():
        if tool_name in ESSENTIAL_TOOLS or tool_name not in disabled_tools:
            enabled_tools[tool_name] = tool_instance
        else:
            logger.debug(f"Tool '{tool_name}' disabled via DISABLED_TOOLS")
    return enabled_tools


def log_tool_configuration(disabled_tools: set[str], enabled_tools: dict[str, Any]) -> None:
    """
    Log the final tool configuration for visibility.

    Args:
        disabled_tools: Set of tool names that were requested to be disabled
        enabled_tools: Dictionary of tools that remain enabled
    """
    if not disabled_tools:
        logger.info("All tools enabled (DISABLED_TOOLS not set)")
        return
    actual_disabled = disabled_tools - ESSENTIAL_TOOLS
    if actual_disabled:
        logger.debug(f"Disabled tools: {sorted(actual_disabled)}")
        logger.info(f"Active tools: {sorted(enabled_tools.keys())}")


def filter_disabled_tools(all_tools: dict[str, Any]) -> dict[str, Any]:
    """
    Filter tools based on DISABLED_TOOLS environment variable.

    Args:
        all_tools: Dictionary of all available tool instances

    Returns:
        dict: Filtered dictionary containing only enabled tools
    """
    disabled_tools = parse_disabled_tools_env()
    if not disabled_tools:
        log_tool_configuration(disabled_tools, all_tools)
        return all_tools
    validate_disabled_tools(disabled_tools, all_tools)
    enabled_tools = apply_tool_filter(all_tools, disabled_tools)
    log_tool_configuration(disabled_tools, enabled_tools)
    return enabled_tools


def filter_by_provider_capabilities(all_tools: dict[str, Any]) -> dict[str, Any]:
    """
    Filter provider-specific tools based on which providers are initialized.

    - If Kimi provider is unavailable, remove tools prefixed with 'kimi_'
    - If GLM provider is unavailable, remove tools prefixed with 'glm_'

    This preserves the simplified configuration while avoiding broken tools when
    provider keys are missing or providers are disallowed via ALLOWED_PROVIDERS.
    """
    try:
        enabled = dict(all_tools)
        kimi_available = ModelProviderRegistry.get_provider(ProviderType.KIMI) is not None
        glm_available = ModelProviderRegistry.get_provider(ProviderType.GLM) is not None

        if not kimi_available:
            removed = []
            for name in list(enabled.keys()):
                if name.startswith("kimi_"):
                    removed.append(name)
                    enabled.pop(name, None)
            if removed:
                logger.info("ToolVisibility: Kimi not available; disabling %s", sorted(removed))

        if not glm_available:
            removed = []
            for name in list(enabled.keys()):
                if name.startswith("glm_"):
                    removed.append(name)
                    enabled.pop(name, None)
            if removed:
                logger.info("ToolVisibility: GLM not available; disabling %s", sorted(removed))

        return enabled
    except Exception as e:
        logger.debug("Provider-capability filtering skipped: %s", e)
        return all_tools




