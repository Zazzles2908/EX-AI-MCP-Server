from __future__ import annotations

"""
Registry Bridge for EX MCP Server

Purpose:
- Provide a thin, centralized bridge around tools.registry.ToolRegistry
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
        self._reg = ToolRegistry()
        self._built = False
        self._lock = RLock()

    def build(self, force: bool = False) -> None:
        with self._lock:
            if not self._built or force:
                # Idempotent: ToolRegistry.build_tools() repopulates with current env
                self._reg.build_tools()
                self._built = True

    def list_tools(self) -> Dict[str, Any]:
        # Safe to call before build(); returns current (possibly empty) map
        return self._reg.list_tools()

    def list_descriptors(self) -> Dict[str, Any]:
        return self._reg.list_descriptors()

    def get_tool(self, name: str) -> Any:
        tools = self._reg.list_tools()
        if name in tools:
            return tools[name]
        # fall back to ToolRegistry error for better message
        return self._reg.get_tool(name)


# Singleton accessors
_registry_singleton: _RegistryBridge | None = None

def get_registry() -> _RegistryBridge:
    global _registry_singleton
    if _registry_singleton is None:
        _registry_singleton = _RegistryBridge()
    return _registry_singleton

# Convenience alias for modules that prefer attribute-style import
registry = get_registry()

