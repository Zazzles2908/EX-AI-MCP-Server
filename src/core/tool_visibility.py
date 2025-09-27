
"""
Tool Visibility Management for EX-AI MCP Server

Manages which tools are visible vs hidden based on environment flags.
Provides centralized control over tool availability.
"""
import os
from typing import Set, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ToolVisibilityManager:
    """Manages tool visibility based on environment configuration."""
    
    # Always visible tools (core functionality)
    VISIBLE_TOOLS = {
        "chat",
        "planner", 
        "thinkdeep",
        "self-check"
    }
    
    # Hidden tools with environment flags
    HIDDEN_TOOLS = {
        "consensus": "ENABLE_CONSENSUS",
        "codereview": "ENABLE_CODEREVIEW", 
        "precommit": "ENABLE_PRECOMMIT",
        "debug": "ENABLE_DEBUG",
        "secaudit": "ENABLE_SECAUDIT",
        "docgen": "ENABLE_DOCGEN",
        "analyze": "ENABLE_ANALYZE",
        "refactor": "ENABLE_REFACTOR",
        "tracer": "ENABLE_TRACER",
        "testgen": "ENABLE_TESTGEN",
        "challenge": "ENABLE_CHALLENGE",
        "listmodels": "ENABLE_LISTMODELS",
        "version": "ENABLE_VERSION"
    }
    
    def __init__(self):
        self._enabled_tools = self._calculate_enabled_tools()
        logger.info(f"Tool visibility initialized. Enabled tools: {sorted(self._enabled_tools)}")
    
    def _calculate_enabled_tools(self) -> Set[str]:
        """Calculate which tools are enabled based on environment."""
        enabled = set(self.VISIBLE_TOOLS)
        
        # Check environment flags for hidden tools
        for tool_name, env_flag in self.HIDDEN_TOOLS.items():
            if self._env_true(env_flag):
                enabled.add(tool_name)
                logger.debug(f"Tool '{tool_name}' enabled via {env_flag}")
        
        return enabled
    
    def _env_true(self, key: str) -> bool:
        """Check if environment variable is set to a truthy value."""
        return os.getenv(key, "false").lower() in ("true", "1", "yes", "on")
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        return tool_name in self._enabled_tools
    
    def get_enabled_tools(self) -> Set[str]:
        """Get all enabled tools."""
        return self._enabled_tools.copy()
    
    def get_disabled_reason(self, tool_name: str) -> str:
        """Get reason why a tool is disabled."""
        if tool_name in self.VISIBLE_TOOLS:
            return f"Tool '{tool_name}' should be visible but is not enabled"
        
        if tool_name in self.HIDDEN_TOOLS:
            env_flag = self.HIDDEN_TOOLS[tool_name]
            return f"Tool '{tool_name}' is disabled. Set {env_flag}=true to enable."
        
        return f"Unknown tool '{tool_name}'"
    
    def get_tool_status(self) -> Dict[str, Any]:
        """Get comprehensive tool status for diagnostics."""
        return {
            "visible_tools": sorted(self.VISIBLE_TOOLS),
            "hidden_tools": sorted(self.HIDDEN_TOOLS.keys()),
            "enabled_tools": sorted(self._enabled_tools),
            "disabled_tools": sorted(
                (set(self.VISIBLE_TOOLS) | set(self.HIDDEN_TOOLS.keys())) - self._enabled_tools
            )
        }
