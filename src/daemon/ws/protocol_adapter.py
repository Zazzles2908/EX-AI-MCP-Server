"""
Protocol Adapter Layer

Allows custom EXAI protocol to coexist with MCP protocol in the same daemon.
This adapter provides a bridge between the two protocols, allowing:
1. Custom EXAI WebSocket clients to continue working
2. MCP protocol tools to execute via the same daemon infrastructure

Architecture:
- Custom EXAI protocol: {"op": "hello", "token": "..."} → Daemon
- MCP protocol: {"jsonrpc": "2.0", "method": "tools/list"} → Adapter → Tool execution

The adapter ensures both protocols can share the same tool registry and
provider infrastructure while maintaining their distinct message formats.

Author: EXAI MCP Server
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ProtocolType(Enum):
    """Enum for different protocol types."""
    EXAI_CUSTOM = "exai_custom"  # {"op": "hello", ...}
    MCP_JSONRPC = "mcp_jsonrpc"  # {"jsonrpc": "2.0", ...}


@dataclass
class ProtocolMessage:
    """Represents a protocol-agnostic message."""
    protocol: ProtocolType
    raw_message: dict
    operation: str
    request_id: Optional[str] = None
    data: Optional[dict] = None


class ProtocolAdapter:
    """
    Adapter for translating between different protocol formats.

    This class provides a unified interface for handling both:
    1. Custom EXAI protocol (WebSocket clients)
    2. MCP JSON-RPC protocol (MCP clients)

    The adapter routes messages to the appropriate handler and ensures
    responses are formatted correctly for each protocol.
    """

    def __init__(self, tool_executor, provider_registry):
        """
        Initialize the protocol adapter.

        Args:
            tool_executor: ToolExecutor instance for executing tools
            provider_registry: ProviderRegistry for AI providers
        """
        self.tool_executor = tool_executor
        self.provider_registry = provider_registry
        self._active_connections = {}

        logger.info("Protocol adapter initialized")

    async def handle_message(self, message: dict, websocket) -> Optional[dict]:
        """
        Handle an incoming message and determine protocol.

        Args:
            message: Raw message dict
            websocket: WebSocket connection (for responses)

        Returns:
            Response message in appropriate protocol format, or None
        """
        try:
            # Determine protocol type
            protocol_type = self._detect_protocol(message)

            if protocol_type == ProtocolType.EXAI_CUSTOM:
                return await self._handle_exai_message(message, websocket)
            elif protocol_type == ProtocolType.MCP_JSONRPC:
                return await self._handle_mcp_message(message, websocket)
            else:
                logger.warning(f"[ADAPTER] Unknown protocol for message: {message}")
                return await self._send_error(
                    websocket,
                    "INVALID_PROTOCOL",
                    "Unknown or unsupported protocol"
                )

        except Exception as e:
            logger.error(f"[ADAPTER] Error handling message: {e}", exc_info=True)
            return await self._send_error(
                websocket,
                "INTERNAL_ERROR",
                f"Internal error: {str(e)}"
            )

    def _detect_protocol(self, message: dict) -> ProtocolType:
        """
        Detect which protocol a message uses.

        Args:
            message: Raw message dict

        Returns:
            ProtocolType enum value
        """
        # Check for custom EXAI protocol
        if "op" in message:
            return ProtocolType.EXAI_CUSTOM

        # Check for MCP JSON-RPC protocol
        if "jsonrpc" in message and message.get("jsonrpc") == "2.0":
            return ProtocolType.MCP_JSONRPC

        # Unknown protocol
        logger.warning(f"[ADAPTER] Unknown protocol for message: {message}")
        return None

    async def _handle_exai_message(self, message: dict, websocket) -> Optional[dict]:
        """
        Handle a custom EXAI protocol message.

        Args:
            message: EXAI protocol message
            websocket: WebSocket connection

        Returns:
            Response in EXAI protocol format
        """
        op = message.get("op")

        if op == "hello":
            return await self._handle_exai_hello(message, websocket)
        elif op == "list_tools":
            return await self._handle_exai_list_tools(websocket)
        elif op == "tool_call":
            return await self._handle_exai_tool_call(message, websocket)
        elif op == "ping":
            return {"op": "pong", "timestamp": message.get("timestamp")}
        else:
            logger.warning(f"[ADAPTER] Unknown EXAI op: {op}")
            return await self._send_error(
                websocket,
                "UNKNOWN_OPERATION",
                f"Unknown operation: {op}"
            )

    async def _handle_mcp_message(self, message: dict, websocket) -> Optional[dict]:
        """
        Handle an MCP JSON-RPC protocol message.

        Args:
            message: MCP protocol message
            websocket: WebSocket connection

        Returns:
            Response in MCP protocol format
        """
        method = message.get("method")
        request_id = message.get("id")

        if method == "initialize":
            return await self._handle_mcp_initialize(message, websocket)
        elif method == "tools/list":
            return await self._handle_mcp_list_tools(message, websocket)
        elif method == "tools/call":
            return await self._handle_mcp_tool_call(message, websocket)
        elif method == "notifications/initialized":
            # Notification - no response needed
            logger.info("[ADAPTER] MCP initialized notification received")
            return None
        else:
            logger.warning(f"[ADAPTER] Unknown MCP method: {method}")
            return await self._send_mcp_error(
                websocket,
                request_id,
                "METHOD_NOT_FOUND",
                f"Method not found: {method}"
            )

    async def _handle_exai_hello(self, message: dict, websocket) -> dict:
        """
        Handle EXAI hello message.

        Args:
            message: Hello message
            websocket: WebSocket connection

        Returns:
            Hello ACK response
        """
        logger.info("[ADAPTER] Processing EXAI hello")

        # Validate required fields
        if "token" not in message:
            return await self._send_error(
                websocket,
                "AUTHENTICATION_REQUIRED",
                "Missing authentication token"
            )

        if "protocolVersion" not in message:
            return await self._send_error(
                websocket,
                "PROTOCOL_VERSION_REQUIRED",
                "Missing protocolVersion"
            )

        # For now, accept any token (authentication is handled elsewhere)
        session_id = f"session_{id(websocket)}"

        response = {
            "op": "hello_ack",
            "ok": True,
            "session_id": session_id,
            "protocol_version": message["protocolVersion"],
            "server_info": {
                "name": "exai-mcp-daemon",
                "version": "1.0.0",
                "protocols": ["exai_custom", "mcp_jsonrpc"]
            }
        }

        logger.info(f"[ADAPTER] ✓ EXAI hello accepted (session: {session_id})")
        return response

    async def _handle_exai_list_tools(self, websocket) -> dict:
        """
        Handle EXAI list_tools request.

        Args:
            websocket: WebSocket connection

        Returns:
            Tools list in EXAI protocol format
        """
        logger.info("[ADAPTER] Processing EXAI list_tools")

        # Get tools from registry
        tools_data = await self._get_mcp_tools_formatted()

        response = {
            "op": "tools_list",
            "tools": tools_data
        }

        logger.info(f"[ADAPTER] ✓ Returned {len(tools_data)} tools")
        return response

    async def _handle_exai_tool_call(self, message: dict, websocket) -> dict:
        """
        Handle EXAI tool_call request.

        Args:
            message: Tool call message
            websocket: WebSocket connection

        Returns:
            Tool result in EXAI protocol format
        """
        logger.info(f"[ADAPTER] Processing EXAI tool_call: {message.get('name', 'unknown')}")

        # Extract parameters
        tool_name = message.get("name")
        arguments = message.get("arguments", {})

        if not tool_name:
            return await self._send_error(
                websocket,
                "TOOL_NAME_REQUIRED",
                "Missing tool name"
            )

        try:
            # Execute via MCP tool executor
            result = await self.tool_executor.execute(tool_name, arguments)

            # Format as EXAI protocol
            response = {
                "op": "call_tool_res",
                "outputs": result,
                "timestamp": asyncio.get_event_loop().time()
            }

            logger.info(f"[ADAPTER] ✓ Tool '{tool_name}' executed successfully")
            return response

        except Exception as e:
            logger.error(f"[ADAPTER] Tool '{tool_name}' failed: {e}", exc_info=True)
            return await self._send_error(
                websocket,
                "TOOL_EXECUTION_FAILED",
                f"Tool execution failed: {str(e)}"
            )

    async def _handle_mcp_initialize(self, message: dict, websocket) -> dict:
        """
        Handle MCP initialize request.

        Args:
            message: Initialize message
            websocket: WebSocket connection

        Returns:
            Initialize response in MCP format
        """
        logger.info("[ADAPTER] Processing MCP initialize")

        # Validate protocol version
        params = message.get("params", {})
        protocol_version = params.get("protocolVersion")

        if protocol_version != "2024-11-05":
            logger.warning(f"[ADAPTER] Unsupported MCP protocol version: {protocol_version}")

        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "experimental": {},
                    "logging": {},
                    "prompts": {"listChanged": False},
                    "resources": {"listChanged": False, "subscribe": False},
                    "tools": {"listChanged": False},
                    "completions": {"listChanged": False}
                },
                "serverInfo": {
                    "name": "exai-mcp",
                    "version": "1.0.0"
                }
            }
        }

        logger.info("[ADAPTER] ✓ MCP initialize accepted")
        return response

    async def _handle_mcp_list_tools(self, message: dict, websocket) -> dict:
        """
        Handle MCP tools/list request.

        Args:
            message: List tools message
            websocket: WebSocket connection

        Returns:
            Tools list in MCP format
        """
        logger.info("[ADAPTER] Processing MCP tools/list")

        # Get tools from registry
        tools_data = await self._get_mcp_tools_formatted()

        response = {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "tools": tools_data
            }
        }

        logger.info(f"[ADAPTER] ✓ MCP returned {len(tools_data)} tools")
        return response

    async def _handle_mcp_tool_call(self, message: dict, websocket) -> dict:
        """
        Handle MCP tools/call request.

        Args:
            message: Tool call message
            websocket: WebSocket connection

        Returns:
            Tool result in MCP format
        """
        logger.info("[ADAPTER] Processing MCP tools/call")

        # Extract parameters
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name:
            return await self._send_mcp_error(
                websocket,
                message.get("id"),
                "INVALID_PARAMS",
                "Missing tool name"
            )

        try:
            # Execute via tool executor
            result = await self.tool_executor.execute(tool_name, arguments)

            # Format as MCP response
            response = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "content": result
                }
            }

            logger.info(f"[ADAPTER] ✓ MCP tool '{tool_name}' executed successfully")
            return response

        except Exception as e:
            logger.error(f"[ADAPTER] MCP tool '{tool_name}' failed: {e}", exc_info=True)
            return await self._send_mcp_error(
                websocket,
                message.get("id"),
                "TOOL_EXECUTION_FAILED",
                f"Tool execution failed: {str(e)}"
            )

    async def _get_mcp_tools_formatted(self) -> List[dict]:
        """
        Get tools from registry formatted for MCP protocol.

        Returns:
            List of tool dicts with name, description, and inputSchema
        """
        # This would get tools from the MCP server's tool registry
        # For now, we'll use a placeholder
        # In the actual implementation, this would call:
        # mcp_server.tool_registry.list_tools()

        tools = []
        # This is a simplified implementation
        # The actual MCP server would handle this directly

        return tools

    async def _send_error(self, websocket, code: str, message: str) -> dict:
        """
        Send error in EXAI protocol format.

        Args:
            websocket: WebSocket connection
            code: Error code
            message: Error message

        Returns:
            Error response dict
        """
        response = {
            "op": "error",
            "error": {
                "code": code,
                "message": message
            }
        }

        try:
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"[ADAPTER] Failed to send error: {e}")

        return response

    async def _send_mcp_error(self, websocket, request_id, code: str, message: str) -> dict:
        """
        Send error in MCP JSON-RPC format.

        Args:
            websocket: WebSocket connection
            request_id: Request ID for correlation
            code: Error code
            message: Error message

        Returns:
            Error response dict
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }

        try:
            await websocket.send(json.dumps(response))
        except Exception as e:
            logger.error(f"[ADAPTER] Failed to send MCP error: {e}")

        return response
