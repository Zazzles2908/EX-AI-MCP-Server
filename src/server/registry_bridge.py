from __future__ import annotations

"""
Registry Bridge for EX MCP Server

ARCHITECTURE NOTE (v2.0.2):
- This module now delegates to src/bootstrap/singletons for tool registry access
- Ensures TOOLS is SERVER_TOOLS identity check always passes (same object reference)
- No longer creates a second ToolRegistry instance - uses singleton pattern
- All methods return references to the shared singleton tools dict

Purpose:
- Provide a thin, centralized bridge around the singleton tool registry
- Build tool instances once (honoring env: LEAN_MODE, DISABLED_TOOLS, etc.)
- Expose helpers to list/get tools for handlers without importing server.TOOLS

This restores the original dynamic registry behavior so provider-specific tools
(e.g., kimi_*, glm_*) are exposed to MCP list_tools and callable via call_tool.
"""

from typing import Any, Dict
from threading import RLock

from tools.registry import ToolRegistry


class _RegistryBridge:
    def __init__(self) -> None:
        # CRITICAL: Delegate to singleton instead of creating second ToolRegistry instance
        from src.bootstrap.singletons import ensure_tools_built, get_tools
        self._ensure_tools_built = ensure_tools_built
        self._get_tools = get_tools
        self._lock = RLock()

    def build(self, force: bool = False) -> None:
        with self._lock:
            # Delegate to singleton - idempotent by design
            # force parameter ignored as singleton handles idempotency
            self._ensure_tools_built()

    def list_tools(self) -> Dict[str, Any]:
        # Return singleton tools dict (same object as server.TOOLS)
        tools = self._get_tools()
        return tools if tools is not None else {}

    def list_descriptors(self) -> Dict[str, Any]:
        # Descriptors are built alongside tools in singleton
        from tools.registry import ToolRegistry
        return ToolRegistry().list_descriptors()

    def get_tool(self, name: str) -> Any:
        # Use singleton tools dict for lookup
        tools = self._get_tools()
        if tools and name in tools:
            return tools[name]
        raise KeyError(f"Tool '{name}' not found in registry")


# Singleton accessors
_registry_singleton: _RegistryBridge | None = None

def get_registry() -> _RegistryBridge:
    global _registry_singleton
    if _registry_singleton is None:
        _registry_singleton = _RegistryBridge()
    return _registry_singleton

# Convenience alias for modules that prefer attribute-style import
registry = get_registry()

