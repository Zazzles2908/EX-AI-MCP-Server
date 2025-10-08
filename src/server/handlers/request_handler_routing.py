"""
Request Handler Routing Module

This module handles tool name resolution and filtering including:
- Tool name normalization (case handling)
- Thinking tool aliasing (deepthink → thinkdeep)
- Client allow/deny list enforcement
- Unknown tool suggestions using difflib

ARCHITECTURE NOTE (v2.0.2+):
- This module delegates to singleton registry via src/server/registry_bridge
- NEVER instantiate ToolRegistry directly - always use get_registry()
- registry_bridge.build() is idempotent and delegates to src/bootstrap/singletons
- Ensures TOOLS is SERVER_TOOLS identity check always passes
"""

import difflib
import logging
from typing import Dict, Any, Optional
from mcp.types import TextContent

logger = logging.getLogger(__name__)


def normalize_tool_name(name: str, tool_map: Dict[str, Any], think_routing_enabled: bool) -> str:
    """
    Normalize tool name and apply aliasing rules.
    
    Handles thinking tool rerouting:
    1. exact 'deepthink' -> 'thinkdeep'
    2. unknown tool name containing 'think' (case-insensitive) -> 'thinkdeep'
    3. do NOT reroute if a valid tool other than thinkdeep contains 'think'
    
    Args:
        name: Original tool name
        tool_map: Dictionary of available tools
        think_routing_enabled: Whether thinking tool routing is enabled
        
    Returns:
        Normalized tool name
    """
    if not think_routing_enabled:
        return name
    
    try:
        original_name = name
        lower_name = (name or "").lower()
        
        # Determine current active tool names
        active_tool_names = set(tool_map.keys())
        
        reroute = False
        if lower_name == "deepthink":
            reroute = True
        elif lower_name not in active_tool_names and "think" in lower_name:
            reroute = True
        
        if reroute:
            # Respect rule (3): if name is a valid tool (not thinkdeep), don't reroute
            if lower_name in active_tool_names and lower_name != "thinkdeep":
                pass  # no-op
            else:
                name = "thinkdeep"
                logger.info(f"REROUTE: '{original_name}' → 'thinkdeep'")
    except Exception as _e:
        logger.debug(f"[THINK_ROUTING] aliasing skipped/failed: {_e}")
    
    return name


def check_client_filters(name: str) -> Optional[str]:
    """
    Check allow/deny lists, return error message if blocked.
    
    Args:
        name: Tool name to check
        
    Returns:
        Error message if blocked, None if allowed
    """
    # Client filtering logic would go here
    # Currently not implemented in the original code
    # Placeholder for future implementation
    return None


def suggest_tool_name(name: str, tool_map: Dict[str, Any], env_true_func) -> Optional[TextContent]:
    """
    Suggest close matches for unknown tool names using difflib.
    
    Args:
        name: Unknown tool name
        tool_map: Dictionary of available tools
        env_true_func: Function to check environment variables
        
    Returns:
        TextContent with suggestion or None
    """
    try:
        if env_true_func("SUGGEST_TOOL_ALIASES", "true"):
            try:
                from src.server.registry_bridge import get_registry as _get_reg  # type: ignore
                _reg = _get_reg()
                # Idempotent guard: build() delegates to singleton, safe to call multiple times
                _reg.build()
                _names = list(_reg.list_tools().keys())
                cand = difflib.get_close_matches(name, _names, n=1, cutoff=0.6)
                if cand:
                    suggestion = cand[0]
                    tool_obj = _reg.list_tools().get(suggestion)
                    desc = tool_obj.get_description() if tool_obj else ""
                    return TextContent(
                        type="text",
                        text=f"Unknown tool: {name}. Did you mean: {suggestion}? {desc}"
                    )
            except Exception:
                pass
    except Exception:
        pass
    
    return None


def handle_unknown_tool(name: str, tool_map: Dict[str, Any], env_true_func) -> list[TextContent]:
    """
    Handle unknown tool requests gracefully with suggestions.
    
    Args:
        name: Unknown tool name
        tool_map: Dictionary of available tools
        env_true_func: Function to check environment variables
        
    Returns:
        List of TextContent with error message and optional suggestion
    """
    # Try to suggest a close match
    suggestion = suggest_tool_name(name, tool_map, env_true_func)
    if suggestion:
        return [suggestion]
    
    # Default unknown tool message
    return [TextContent(type="text", text=f"Unknown tool: {name}")]


# Export public API
__all__ = [
    'normalize_tool_name',
    'check_client_filters',
    'suggest_tool_name',
    'handle_unknown_tool',
]

