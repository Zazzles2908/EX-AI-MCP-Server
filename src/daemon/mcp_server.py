"""
Native MCP Server Implementation

Runs MCP protocol directly in daemon, eliminating the shim layer.
This provides native stdio support for MCP clients like Claude Code.

Architecture:
- Native MCP server (this file) - handles MCP JSON-RPC over stdio
- Custom WebSocket server - handles EXAI custom protocol over WebSocket
- Protocol adapter - allows coexistence of both protocols

Usage:
    python -m src.daemon.mcp_server --stdio    # Run over stdio (MCP clients)
    python -m src.daemon.mcp_server --websocket  # Run over WebSocket (direct clients)

Author: EXAI MCP Server
Version: 1.0.0
"""

import asyncio
import json
import logging
import sys
import argparse
from typing import Any, List, Dict
from pathlib import Path

# Setup paths
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Import daemon components
from src.bootstrap.logging_setup import setup_logging
from src.bootstrap.env_loader import load_env
from src.providers.registry_core import get_registry_instance
from tools.registry import get_tool_registry

# Setup logging
logger = logging.getLogger(__name__)


class DaemonMCPServer:
    """
    Native MCP server that runs inside the daemon process.

    This server integrates directly with the EXAI tool registry and provider
    system, eliminating the need for a separate shim process.
    """

    def __init__(self, tool_registry, provider_registry):
        """
        Initialize the native MCP server.

        Args:
            tool_registry: ToolRegistry instance with loaded tools
            provider_registry: ProviderRegistry instance for AI providers
        """
        self.app = Server("exai-mcp")
        self.tool_registry = tool_registry
        self.provider_registry = provider_registry
        self._ws_connections = {}

        # Register handlers
        self._register_handlers()

        logger.info("Native MCP server initialized")

    def _register_handlers(self):
        """Register MCP protocol handlers."""

        @self.app.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """
            List all available tools from the registry.

            Returns:
                List of Tool objects with name, description, and input schema
            """
            logger.info("[MCP] tools/list requested")
            tools = []

            for name, tool_obj in self.tool_registry.list_tools().items():
                try:
                    # Get schema from tool
                    if hasattr(tool_obj, 'get_input_schema'):
                        schema = tool_obj.get_input_schema()
                    elif hasattr(tool_obj, 'get_descriptor'):
                        desc = tool_obj.get_descriptor()
                        schema = desc.get('inputSchema', {})
                    else:
                        # Default schema
                        schema = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }

                    # Get description
                    if hasattr(tool_obj, 'get_description'):
                        description = tool_obj.get_description()
                    else:
                        description = f"Tool: {name}"

                    # Create MCP Tool
                    mcp_tool = Tool(
                        name=name,
                        description=description,
                        inputSchema=schema
                    )
                    tools.append(mcp_tool)

                    logger.debug(f"[MCP] Registered tool: {name}")

                except Exception as e:
                    logger.error(f"[MCP] Failed to register tool {name}: {e}")
                    continue

            logger.info(f"[MCP] ✓ Listed {len(tools)} tools")
            return tools

        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            Execute a tool from the registry.

            Args:
                name: Tool name to execute
                arguments: Tool arguments

            Returns:
                List of TextContent with tool results
            """
            logger.info(f"[MCP] tools/call requested: {name}")

            try:
                # Get tool from registry
                tool_obj = self.tool_registry.get_tool(name)

                # Execute tool
                if hasattr(tool_obj, 'execute'):
                    # Most tools have async execute
                    result = await tool_obj.execute(arguments)
                    logger.info(f"[MCP] ✓ Tool '{name}' executed successfully")
                    return result
                else:
                    logger.error(f"[MCP] Tool '{name}' is not executable")
                    return [
                        TextContent(
                            type="text",
                            text=f"Error: Tool '{name}' is not executable"
                        )
                    ]

            except KeyError:
                logger.error(f"[MCP] Unknown tool: {name}")
                return [
                    TextContent(
                        type="text",
                        text=f"Error: Unknown tool '{name}'"
                    )
                ]
            except Exception as e:
                logger.error(f"[MCP] Tool '{name}' failed: {e}", exc_info=True)
                return [
                    TextContent(
                        type="text",
                        text=f"Error executing tool '{name}': {str(e)}"
                    )
                ]

    async def run_stdio(self):
        """
        Run MCP server over stdio (for MCP clients like Claude Code).

        This is the main entry point for MCP protocol over stdio.
        """
        logger.info("[MCP] Starting native MCP server over stdio...")

        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("[MCP] stdio_server context entered")

                # Run the MCP server
                try:
                    logger.info("[MCP] About to call app.run()...")
                    await self.app.run(
                        read_stream,
                        write_stream,
                        self.app.create_initialization_options()
                    )
                    # If app.run() returns, log but keep stdio_server open
                    # This can happen in 'both' mode when stdio is not actively used
                    logger.warning("[MCP] ⚠️ app.run() returned (may be normal in 'both' mode)")
                except asyncio.CancelledError:
                    logger.info("[MCP] app.run() was cancelled - this is normal during shutdown")
                    raise
                except Exception as e:
                    logger.error(f"[MCP] ⚠️ app.run() crashed with exception: {e}", exc_info=True)
                    raise

                # Keep the stdio_server context alive - don't exit
                logger.info("[MCP] Keeping stdio_server alive (both mode)...")
                # Wait forever or until cancelled
                try:
                    while True:
                        await asyncio.sleep(3600)  # Sleep for 1 hour at a time
                except asyncio.CancelledError:
                    logger.info("[MCP] stdio_server cancelled - shutting down")
                    raise

        except Exception as e:
            logger.error(f"[MCP] stdio_server outer exception: {e}", exc_info=True)
            raise

    async def run_websocket(self, host: str = "0.0.0.0", port: int = 3011):
        """
        Run MCP server over WebSocket (optional, for WebSocket MCP clients).

        Args:
            host: WebSocket bind address
            port: WebSocket port
        """
        logger.info(f"[MCP] Starting native MCP server over WebSocket ({host}:{port})...")

        import websockets

        # WebSocket MCP server (simplified)
        # This would implement MCP protocol over WebSocket
        # For now, we'll focus on stdio mode

        async def handle_client(websocket):
            logger.info(f"[MCP] WebSocket client connected: {websocket.remote_address}")
            try:
                # Handle MCP over WebSocket
                # This is a simplified implementation
                # A full implementation would parse MCP JSON-RPC over WebSocket
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        logger.info(f"[MCP] Received WebSocket message: {data.get('method', 'unknown')}")

                        # Handle MCP requests
                        if data.get('method') == 'tools/list':
                            tools = await handle_list_tools()
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get('id'),
                                "result": {
                                    "tools": [
                                        {
                                            "name": t.name,
                                            "description": t.description,
                                            "inputSchema": t.inputSchema
                                        }
                                        for t in tools
                                    ]
                                }
                            }
                            await websocket.send(json.dumps(response))

                    except json.JSONDecodeError:
                        logger.warning(f"[MCP] Invalid JSON from WebSocket")
                    except Exception as e:
                        logger.error(f"[MCP] WebSocket error: {e}", exc_info=True)

            except websockets.exceptions.ConnectionClosed:
                logger.info(f"[MCP] WebSocket client disconnected")
            except Exception as e:
                logger.error(f"[MCP] WebSocket handler error: {e}", exc_info=True)

        try:
            async with websockets.serve(handle_client, host, port):
                logger.info(f"[MCP] WebSocket server listening on {host}:{port}")
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"[MCP] WebSocket server failed: {e}", exc_info=True)
            raise


async def initialize_daemon_components():
    """
    Initialize all daemon components needed for MCP server.

    This includes:
    - Environment loading
    - Provider registry
    - Tool registry
    - Logging setup

    Returns:
        tuple: (tool_registry, provider_registry)
    """
    logger.info("[INIT] Initializing daemon components...")

    # Load environment
    try:
        load_env()
        logger.info("[INIT] ✓ Environment loaded")
    except Exception as e:
        logger.warning(f"[INIT] ⚠ Failed to load environment: {e}")

    # Setup logging
    try:
        setup_logging()
        logger.info("[INIT] ✓ Logging configured")
    except Exception as e:
        logger.warning(f"[INIT] ⚠ Failed to setup logging: {e}")

    # Initialize provider registry
    try:
        provider_registry = get_registry_instance()
        # Note: _ensure_providers_configured() should be called separately
        logger.info("[INIT] ✓ Provider registry ready")
    except Exception as e:
        logger.error(f"[INIT] ✗ Provider registry failed: {e}")
        raise

    # Initialize tool registry
    try:
        tool_registry = get_tool_registry()
        logger.info(f"[INIT] ✓ Tool registry ready ({len(tool_registry.list_tools())} tools)")
    except Exception as e:
        logger.error(f"[INIT] ✗ Tool registry failed: {e}")
        raise

    return tool_registry, provider_registry


async def main():
    """
    Main entry point for native MCP server.

    Supports both stdio and WebSocket modes.
    """
    parser = argparse.ArgumentParser(description="EXAI Native MCP Server")
    parser.add_argument(
        "--mode",
        choices=["stdio", "websocket"],
        default="stdio",
        help="Transport mode (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="WebSocket host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=3011,
        help="WebSocket port (default: 3011)"
    )

    args = parser.parse_args()

    print("=" * 70)
    print("EXAI Native MCP Server v1.0.0")
    print("=" * 70)
    print(f"Mode: {args.mode}")
    if args.mode == "websocket":
        print(f"WebSocket: {args.host}:{args.port}")
    print("=" * 70)
    logger.info(f"Starting MCP server in {args.mode} mode")

    try:
        # Initialize daemon components
        tool_registry, provider_registry = await initialize_daemon_components()

        # Create MCP server
        mcp_server = DaemonMCPServer(tool_registry, provider_registry)

        # Run in requested mode
        if args.mode == "stdio":
            await mcp_server.run_stdio()
        elif args.mode == "websocket":
            await mcp_server.run_websocket(args.host, args.port)

    except KeyboardInterrupt:
        logger.info("MCP server stopped by user")
    except Exception as e:
        logger.error(f"MCP server fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
