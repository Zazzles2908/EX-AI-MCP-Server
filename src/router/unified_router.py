"""UnifiedRouter shim integrating the streamlined router with existing servers.

This lightweight adapter preserves the simplified architecture while ensuring
compatibility with the existing WebSocket daemon (ws_server.py) and the MCP
stdio server (server.py). It forwards tool calls to the central handlers so both
transports share identical routing behavior.
"""
from __future__ import annotations

from typing import Any, Dict
import logging

from src.server.handlers import handle_call_tool

logger = logging.getLogger(__name__)


class UnifiedRouter:
    """Minimal unified router used by both stdio MCP and WS daemon.

    The daemon can import and use this router to keep parity with stdio routing
    without duplicating logic. This class intentionally stays thin and delegates
    to the canonical server handlers used by server.py.
    """

    async def route_tool(self, name: str, arguments: Dict[str, Any]):
        """Route a tool call to the canonical handler.

        Args:
            name: tool name
            arguments: tool arguments
        Returns:
            The same response format as MCP call_tool (list[TextContent]).
        """
        logger.debug("UnifiedRouter.route_tool -> %s", name)
        return await handle_call_tool(name, arguments)


# Convenience singleton (optional)
router = UnifiedRouter()

