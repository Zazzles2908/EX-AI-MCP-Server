"""
Request Router Utilities

Utility functions for WebSocket request routing.
Provides normalization, key generation, and helper functions.

This is part of the Phase 3 refactoring that split the large request_router.py
into focused modules:
- router_utils.py: Utility functions (this file)
- cache_manager.py: Result caching and inflight tracking
- tool_executor.py: Tool execution with semaphore management
- request_router.py: Main message routing logic
"""

import hashlib
import json
from typing import Any, Dict, List


def normalize_tool_name(name: str) -> str:
    """
    Normalize tool names by stripping common suffixes.

    This handles MCP client-side aliasing where tools may be suffixed with
    _EXAI-WS, -EXAI-WS, _EXAI_WS, or -EXAI_WS.

    Examples:
        chat_EXAI-WS -> chat
        analyze_EXAI-WS -> analyze
        kimi_chat_with_tools_EXAI-WS -> kimi_chat_with_tools
    """
    try:
        # Generic suffix-stripping for all EXAI-WS variants
        # This automatically handles all tools without hardcoded aliases
        for suf in ("_EXAI-WS", "-EXAI-WS", "_EXAI_WS", "-EXAI_WS"):
            if name.endswith(suf):
                return name[: -len(suf)]
    except (AttributeError, TypeError) as e:
        # Return original name - normalization is cosmetic
        pass
    return name


def normalize_outputs(outputs: List[Any]) -> List[Dict[str, Any]]:
    """
    Normalize tool outputs to standard format.

    Converts various output formats (mcp.types.TextContent, dicts, etc.)
    to a consistent list of {"type": "text", "text": "..."} dictionaries.
    """
    norm: List[Dict[str, Any]] = []
    for o in outputs or []:
        try:
            # mcp.types.TextContent has attributes type/text
            t = getattr(o, "type", None) or (o.get("type") if isinstance(o, dict) else None)
            if t == "text":
                text = getattr(o, "text", None) or (o.get("text") if isinstance(o, dict) else None)
                norm.append({"type": "text", "text": text or ""})
            else:
                # Fallback: best-effort stringification
                norm.append({"type": "text", "text": str(o)})
        except Exception:
            norm.append({"type": "text", "text": str(o)})
    return norm


def make_call_key(name: str, arguments: Dict[str, Any]) -> str:
    """
    Generate a deterministic cache key for tool calls.

    Used for deduplication and result caching.
    """
    try:
        # Sort keys for deterministic hashing
        args_str = json.dumps(arguments, sort_keys=True)
        combined = f"{name}:{args_str}"
        return hashlib.sha256(combined.encode()).hexdigest()
    except Exception as e:
        # Fallback to simple concatenation
        return f"{name}:{str(arguments)}"
