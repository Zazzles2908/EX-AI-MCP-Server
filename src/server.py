"""
EX MCP Server - Minimal Implementation

Simplified MCP server for production use.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import TextContent
from mcp.server.stdio import stdio_server

from src.providers.registry_core import get_registry_instance
from src.router.minimax_m2_router import MiniMaxM2Router

# Initialize logging - respect LOG_LEVEL environment variable
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)

# Initialize server
app = Server("exai-mcp")
router = MiniMaxM2Router()
registry_instance = get_registry_instance()

def _ensure_providers_configured():
    """Ensure providers are configured."""
    from src.providers.registry_core import get_registry_instance
    from src.providers.base import ProviderType
    from src.providers.glm_provider import GLMProvider
    from src.providers.kimi import KimiProvider

    registry = get_registry_instance()

    # Register Kimi provider class
    try:
        registry.register_provider(ProviderType.KIMI, KimiProvider)
        logger.info("Registered Kimi provider")
    except Exception as e:
        logger.warning(f"Failed to register Kimi provider: {e}")

    # Register GLM provider class
    try:
        registry.register_provider(ProviderType.GLM, GLMProvider)
        logger.info("Registered GLM provider")
    except Exception as e:
        logger.warning(f"Failed to register GLM provider: {e}")

# Build tools from registry
from tools.registry import ToolRegistry

tool_registry = ToolRegistry()
tool_registry.build_tools()

# Get tool objects and convert to dict format for daemon
# Note: The daemon expects a list of tool dicts for schema, but we need to also
# provide a dict of tool objects for the ToolExecutor
loaded_tools = tool_registry.list_tools()

# Create schema list (for backward compatibility with MCP list_tools)
TOOLS = []
for name, tool_obj in loaded_tools.items():
    try:
        # Get schema from tool object
        if hasattr(tool_obj, 'get_input_schema'):
            schema = tool_obj.get_input_schema()
        elif hasattr(tool_obj, 'get_descriptor'):
            desc = tool_obj.get_descriptor()
            schema = desc.get('inputSchema', {})
        else:
            # Default schema
            schema = {"type": "object", "properties": {}}

        # Build tool dict
        tool_dict = {
            "name": name,
            "description": getattr(tool_obj, 'get_description', lambda: '')() or f"Tool: {name}",
            "inputSchema": schema
        }
        TOOLS.append(tool_dict)
    except Exception as e:
        logger.warning(f"Failed to get schema for tool {name}: {e}")

# SERVER_TOOLS should be a dict of tool objects for ToolExecutor
SERVER_TOOLS = loaded_tools

# Ensure providers are configured AFTER all tools are loaded
_ensure_providers_configured()

# Export TOOLS for MCP compatibility
TOOLS = TOOLS

def register_provider_specific_tools():
    """Register provider-specific tools."""
    pass


def get_follow_up_instructions(tool_id: int) -> str:
    """Get follow-up instructions for a tool (stub function)."""
    # TODO: Implement follow-up instructions if needed
    return ""


@app.list_tools()
async def handle_list_tools() -> List[Dict[str, Any]]:
    """Return list of available tools from the registry."""
    # Return the TOOLS list which contains schemas for all loaded tools
    return TOOLS


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls by routing to actual tool objects."""
    try:
        # Get the tool object from SERVER_TOOLS (dict of tool objects)
        tool_obj = SERVER_TOOLS.get(name)

        if not tool_obj:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        # Execute the tool
        # The tool objects have an execute() method that returns a list of TextContent
        if hasattr(tool_obj, 'execute'):
            result = await tool_obj.execute(arguments)
            return result
        else:
            return [TextContent(type="text", text=f"Tool {name} is not executable")]

    except Exception as e:
        logger.error(f"Error in tool call: {e}")
        import traceback
        traceback.print_exc()
        return [TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")]


async def main():
    """Main entry point."""
    try:
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
