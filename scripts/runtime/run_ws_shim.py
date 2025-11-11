#!/usr/bin/env python
"""
EXAI MCP WebSocket Shim - Protocol Translator
Bridges standard MCP protocol <-> EXAI custom WebSocket protocol.

This shim connects to the EXAI daemon (running in Docker) and translates:
- MCP initialize/hello -> Custom "op" protocol
- Custom responses -> MCP responses
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import websockets

# Setup paths
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

# Load environment
try:
    from src.bootstrap import load_env
    load_env()
except Exception as e:
    logger.warning(f"Could not load env from bootstrap: {e}")
    # Try loading .env manually
    from dotenv import load_dotenv
    env_file = os.getenv('ENV_FILE', '.env')
    load_dotenv(env_file)

logger = logging.getLogger(__name__)

# Configuration
DAEMON_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
# Use the external port (what Docker maps 8079 to)
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3004"))
SHIM_PORT = int(os.getenv("SHIM_LISTEN_PORT", "3005"))  # Listen on different port


class MCPShimProtocol:
    """Protocol handler for MCP <-> Custom translation."""

    def __init__(self, client_ws):
        self.client_ws = client_ws
        self.daemon_ws = None
        self.running = True

    async def connect_to_daemon(self):
        """Establish connection to EXAI daemon."""
        daemon_uri = f"ws://{DAEMON_HOST}:{DAEMON_PORT}"
        logger.info(f"Connecting to EXAI daemon at {daemon_uri}...")

        try:
            self.daemon_ws = await websockets.connect(daemon_uri, timeout=10)
            logger.info("✓ Connected to EXAI daemon")
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to daemon: {e}")
            return False

    async def handle_client_messages(self):
        """Handle messages from MCP client and translate to daemon protocol."""
        try:
            async for message in self.client_ws:
                data = json.loads(message)

                # Log MCP message
                if "method" in data:
                    logger.debug(f"Received MCP: {data['method']}")

                # Handle MCP initialize
                if data.get("method") == "initialize":
                    await self._handle_initialize(data)
                    continue

                # Handle MCP tools/list
                if data.get("method") == "tools/list":
                    await self._handle_tools_list(data)
                    continue

                # Handle MCP tools/call
                if data.get("method") == "tools/call":
                    await self._handle_tools_call(data)
                    continue

                # Forward other messages
                await self._forward_to_daemon(data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from client: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"Error handling client messages: {e}", exc_info=True)
        finally:
            self.running = False

    async def _handle_initialize(self, data):
        """Translate MCP initialize to custom hello protocol."""
        client_info = data.get("params", {}).get("clientInfo", {})
        protocol_version = data.get("params", {}).get("protocolVersion", "2024-11-05")

        # Send custom hello to daemon
        hello_msg = {
            "op": "hello",
            "protocolVersion": protocol_version,
            "capabilities": data.get("params", {}).get("capabilities", {}),
            "clientInfo": client_info
        }

        logger.debug(f"Sending hello to daemon: {hello_msg}")
        await self.daemon_ws.send(json.dumps(hello_msg))

        # Wait for hello_ack
        try:
            response = await asyncio.wait_for(self.daemon_ws.recv(), timeout=5)
            hello_ack = json.loads(response)

            logger.debug(f"Received hello_ack: {hello_ack}")

            if hello_ack.get("ok"):
                # Send MCP initialize response
                init_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "exai-mcp-shim",
                            "version": "1.0.0"
                        }
                    }
                }
                await self.client_ws.send(json.dumps(init_response))
                logger.info("✓ MCP initialization complete")
            else:
                error_msg = hello_ack.get("error", "unknown error")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {"code": -32000, "message": f"Daemon error: {error_msg}"}
                }
                await self.client_ws.send(json.dumps(error_response))

        except asyncio.TimeoutError:
            logger.error("✗ Timeout waiting for daemon hello_ack")
            error_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32000, "message": "Daemon timeout"}
            }
            await self.client_ws.send(json.dumps(error_response))

    async def _handle_tools_list(self, data):
        """Handle tools/list - just forward to daemon."""
        # Convert MCP request to daemon format
        await self.daemon_ws.send(json.dumps({
            "op": "list_tools",
            "id": data.get("id")
        }))

    async def _handle_tools_call(self, data):
        """Handle tools/call - forward to daemon."""
        tool_call = data.get("params", {})
        await self.daemon_ws.send(json.dumps({
            "op": "call_tool",
            "id": data.get("id"),
            "tool": tool_call.get("name"),
            "arguments": tool_call.get("arguments", {})
        }))

    async def _forward_to_daemon(self, data):
        """Forward MCP messages to daemon."""
        if self.daemon_ws:
            await self.daemon_ws.send(json.dumps(data))

    async def handle_daemon_messages(self):
        """Handle messages from EXAI daemon and translate to MCP."""
        try:
            async for message in self.daemon_ws:
                try:
                    data = json.loads(message)

                    # Handle daemon responses and forward appropriately
                    if "op" in data:
                        # This is a custom daemon message
                        await self._translate_daemon_response(data)
                    else:
                        # Forward JSON-RPC messages directly
                        await self.client_ws.send(message)

                except json.JSONDecodeError:
                    # Forward raw messages
                    await self.client_ws.send(message)

        except websockets.exceptions.ConnectionClosed:
            logger.info("Daemon disconnected")
        except Exception as e:
            logger.error(f"Error handling daemon messages: {e}", exc_info=True)
        finally:
            self.running = False

    async def _translate_daemon_response(self, data):
        """Translate daemon custom responses to MCP format."""
        op = data.get("op")

        if op == "hello_ack":
            # Already handled in _handle_initialize
            pass

        elif op == "list_tools_result":
            # Convert to MCP tools/list response
            tools = data.get("tools", [])
            mcp_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {"tools": tools}
            }
            await self.client_ws.send(json.dumps(mcp_response))

        elif op == "call_result":
            # Convert to MCP tools/call response
            result = data.get("result", [])
            mcp_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {"content": result}
            }
            await self.client_ws.send(json.dumps(mcp_response))

        elif op == "error":
            # Forward error
            error = data.get("error", {})
            mcp_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": error.get("code", -32000),
                    "message": error.get("message", "Unknown error")
                }
            }
            await self.client_ws.send(json.dumps(mcp_response))

        else:
            # Unknown op, forward as-is
            logger.warning(f"Unknown daemon op: {op}")
            await self.client_ws.send(json.dumps(data))

    async def run(self):
        """Run the protocol bridge."""
        logger.info("Starting MCP shim protocol bridge...")

        # Connect to daemon
        if not await self.connect_to_daemon():
            raise Exception("Failed to connect to daemon")

        # Run both handlers concurrently
        try:
            await asyncio.gather(
                self.handle_client_messages(),
                self.handle_daemon_messages(),
                return_exceptions=True
            )
        except Exception as e:
            logger.error(f"Error in protocol bridge: {e}", exc_info=True)
        finally:
            if self.daemon_ws:
                await self.daemon_ws.close()


async def handle_client(ws: websockets.WebSocketServerProtocol):
    """Handle new MCP client connection."""
    client_id = id(ws)
    peer = ws.remote_address
    logger.info(f"[{client_id}] New MCP client from {peer}")

    protocol = None
    try:
        protocol = MCPShimProtocol(ws)
        await protocol.run()
    except Exception as e:
        logger.error(f"[{client_id}] Error: {e}", exc_info=True)
    finally:
        logger.info(f"[{client_id}] Client disconnected")
        if protocol and protocol.daemon_ws:
            try:
                await protocol.daemon_ws.close()
            except:
                pass


async def main():
    """Main shim server."""
    logger.info(f"=" * 60)
    logger.info(f"EXAI MCP Shim Starting")
    logger.info(f"  Listening: {SHIM_PORT}")
    logger.info(f"  Daemon: {DAEMON_HOST}:{DAEMON_PORT}")
    logger.info(f"=" * 60)

    # Start WebSocket server
    async with websockets.serve(handle_client, "127.0.0.1", SHIM_PORT):
        logger.info("✓ MCP Shim ready - waiting for connections...")
        # Keep running
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    # Setup logging
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shim stopped by user")
    except Exception as e:
        logger.error(f"Shim fatal error: {e}", exc_info=True)
        sys.exit(1)
