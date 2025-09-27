
"""
Streamlined Tool Registry for EX-AI MCP Server

Simplified tool registration with visibility management integration.
Only registers tools that are enabled via ToolVisibilityManager.
"""
import logging
from typing import Dict, Any, Optional, Type
import importlib

from src.core.tool_visibility import ToolVisibilityManager

logger = logging.getLogger(__name__)

class StreamlinedToolRegistry:
    """Streamlined tool registry with visibility management."""
    
    # Tool import mapping
    TOOL_IMPORTS = {
        # Visible tools
        "chat": ("tools.visible.chat", "ChatTool"),
        "planner": ("tools.visible.planner", "PlannerTool"), 
        "thinkdeep": ("tools.visible.thinkdeep", "ThinkDeepTool"),
        "self-check": ("tools.visible.selfcheck", "SelfCheckTool"),
        
        # Hidden tools
        "consensus": ("tools.hidden.consensus", "ConsensusTool"),
        "codereview": ("tools.hidden.codereview", "CodeReviewTool"),
        "precommit": ("tools.hidden.precommit", "PrecommitTool"),
        "debug": ("tools.hidden.debug", "DebugIssueTool"),
        "secaudit": ("tools.hidden.secaudit", "SecauditTool"),
        "docgen": ("tools.hidden.docgen", "DocgenTool"),
        "analyze": ("tools.hidden.analyze", "AnalyzeTool"),
        "refactor": ("tools.hidden.refactor", "RefactorTool"),
        "tracer": ("tools.hidden.tracer", "TracerTool"),
        "testgen": ("tools.hidden.testgen", "TestGenTool"),
        "challenge": ("tools.hidden.challenge", "ChallengeTool"),
        "listmodels": ("tools.hidden.listmodels", "ListModelsTool"),
        "version": ("tools.hidden.version", "VersionTool")
    }
    
    def __init__(self):
        self.visibility_manager = ToolVisibilityManager()
        self._tools: Dict[str, Any] = {}
        self._load_enabled_tools()
    
    def _load_enabled_tools(self) -> None:
        """Load only the tools that are enabled."""
        enabled_tools = self.visibility_manager.get_enabled_tools()
        
        for tool_name in enabled_tools:
            if tool_name in self.TOOL_IMPORTS:
                try:
                    module_path, class_name = self.TOOL_IMPORTS[tool_name]
                    module = importlib.import_module(module_path)
                    tool_class = getattr(module, class_name)
                    self._tools[tool_name] = tool_class()
                    logger.debug(f"Loaded tool: {tool_name}")
                except Exception as e:
                    logger.error(f"Failed to load tool {tool_name}: {e}")
        
        logger.info(f"Loaded {len(self._tools)} tools: {sorted(self._tools.keys())}")
    
    def get_tool(self, name: str) -> Optional[Any]:
        """Get a tool by name if it's enabled."""
        return self._tools.get(name)
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is available."""
        return name in self._tools
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """List all available tools with their metadata."""
        tools_info = {}
        
        for name, tool in self._tools.items():
            try:
                tools_info[name] = {
                    "name": name,
                    "description": getattr(tool, "description", "No description available"),
                    "parameters": getattr(tool, "parameters", {}),
                    "enabled": True
                }
            except Exception as e:
                logger.error(f"Error getting info for tool {name}: {e}")
                tools_info[name] = {
                    "name": name,
                    "description": "Error loading tool info",
                    "enabled": True
                }
        
        return tools_info
    
    def get_disabled_tool_message(self, name: str) -> str:
        """Get message for disabled tool."""
        return self.visibility_manager.get_disabled_reason(name)
    
    def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status for diagnostics."""
        return {
            "loaded_tools": sorted(self._tools.keys()),
            "tool_count": len(self._tools),
            "visibility_status": self.visibility_manager.get_tool_status()
        }
