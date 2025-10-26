#!/usr/bin/env python3
"""
MCP WebSocket Client for Baseline Collection
=============================================

Implements actual MCP tool invocation via WebSocket for baseline testing.
Replaces simulated execution with real tool calls through the MCP daemon.

Protocol: Custom WebSocket protocol (not standard MCP JSON-RPC)
Message Format:
  - Request: {"op": "call_tool", "request_id": "...", "name": "tool_name", "arguments": {...}}
  - Response: {"op": "call_tool_res", "request_id": "...", "outputs": [...], "error": null}

Created: 2025-10-24 23:00 AEDT
"""

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

logger = logging.getLogger(__name__)


class MCPWebSocketClient:
    """
    WebSocket client for EXAI-MCP server.
    
    Implements the custom WebSocket protocol used by our MCP daemon.
    Handles connection management, authentication, and tool invocation.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        token: str = None,
        max_message_size: int = 20 * 1024 * 1024  # 20MB
    ):
        """
        Initialize MCP WebSocket client.
        
        Args:
            host: WebSocket server host (default: from EXAI_WS_HOST env)
            port: WebSocket server port (default: from EXAI_WS_PORT env)
            token: Authentication token (default: from EXAI_WS_TOKEN env)
            max_message_size: Maximum message size in bytes
        """
        self.host = host or os.getenv("EXAI_WS_HOST", "127.0.0.1")
        self.port = port or int(os.getenv("EXAI_WS_PORT", "8079"))
        self.token = token or os.getenv("EXAI_WS_TOKEN", "")
        self.max_message_size = max_message_size
        
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.connected = False
        
    async def connect(self, max_retries: int = 3, backoff_factor: float = 2.0) -> bool:
        """
        Establish WebSocket connection and authenticate with retry logic.

        Args:
            max_retries: Maximum number of connection attempts (default: 3)
            backoff_factor: Exponential backoff multiplier (default: 2.0)

        Returns:
            True if connection successful, False otherwise
        """
        for attempt in range(max_retries):
            try:
                uri = f"ws://{self.host}:{self.port}"
                logger.info(f"Connecting to MCP server at {uri} (attempt {attempt + 1}/{max_retries})")

                # Connect to WebSocket server with increased ping timeout
                self.ws = await websockets.connect(
                    uri,
                    max_size=self.max_message_size,
                    ping_interval=20.0,  # Send ping every 20 seconds
                    ping_timeout=20.0    # Wait 20 seconds for pong (increased from 10s)
                )

                # Generate session ID
                self.session_id = f"baseline-{uuid.uuid4().hex[:8]}"

                # Send hello message for authentication
                hello_msg = {
                    "op": "hello",
                    "session_id": self.session_id,
                    "token": self.token
                }
                await self.ws.send(json.dumps(hello_msg))

                # Wait for acknowledgment
                ack_raw = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
                ack = json.loads(ack_raw)

                if not ack.get("ok"):
                    logger.error(f"Authentication failed: {ack}")
                    await self.disconnect()
                    if attempt == max_retries - 1:
                        return False
                    await asyncio.sleep(backoff_factor ** attempt)
                    continue

                self.connected = True
                logger.info(f"Connected to MCP server (session: {self.session_id})")
                return True

            except asyncio.TimeoutError:
                logger.error(f"Connection timeout (attempt {attempt + 1})")
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} connection attempts timed out")
                    return False
                await asyncio.sleep(backoff_factor ** attempt)
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                self.connected = False
                if attempt == max_retries - 1:
                    logger.error(f"All {max_retries} connection attempts failed")
                    return False
                # Exponential backoff
                await asyncio.sleep(backoff_factor ** attempt)

        return False
    
    async def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            try:
                await self.ws.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
            finally:
                self.ws = None
                self.connected = False
                logger.info("Disconnected from MCP server")

    async def ensure_connected(self, max_retries: int = 3) -> bool:
        """
        Ensure WebSocket connection is active, reconnecting if necessary.

        Args:
            max_retries: Maximum number of reconnection attempts

        Returns:
            True if connected, False otherwise
        """
        if self.connected and self.ws:
            return True

        logger.warning("Connection lost, attempting to reconnect...")
        return await self.connect(max_retries=max_retries)

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        timeout: float = 30.0,
        auto_reconnect: bool = True
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        Call a tool via WebSocket and wait for response.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as dictionary
            timeout: Timeout in seconds (default: 30s)
            auto_reconnect: Automatically reconnect if connection is lost (default: True)

        Returns:
            Tuple of (success, outputs, error_message)
            - success: True if tool executed successfully
            - outputs: List of output dictionaries (if successful)
            - error_message: Error message (if failed)
        """
        # Ensure connection is active (with automatic reconnection if enabled)
        if auto_reconnect:
            if not await self.ensure_connected():
                return False, None, "Failed to establish connection"
        elif not self.connected or not self.ws:
            return False, None, "Not connected to MCP server"
        
        request_id = uuid.uuid4().hex
        
        try:
            # Send tool call request
            request = {
                "op": "call_tool",
                "request_id": request_id,
                "name": tool_name,
                "arguments": arguments
            }
            await self.ws.send(json.dumps(request))
            
            # Wait for response
            while True:
                raw = await asyncio.wait_for(self.ws.recv(), timeout=timeout)
                msg = json.loads(raw)
                
                # Check if this is our response
                if msg.get("op") == "call_tool_res" and msg.get("request_id") == request_id:
                    # Check for errors
                    if msg.get("error"):
                        error_msg = str(msg.get("error"))
                        logger.warning(f"Tool {tool_name} failed: {error_msg}")
                        return False, None, error_msg
                    
                    # Extract outputs
                    outputs = msg.get("outputs", [])
                    return True, outputs, None
                
                # Ignore other messages (could be from other requests)
                logger.debug(f"Ignoring message: {msg.get('op')}")
                
        except asyncio.TimeoutError:
            error_msg = f"Tool execution timeout after {timeout}s"
            logger.error(f"{tool_name}: {error_msg}")
            return False, None, error_msg
        except ConnectionClosed:
            error_msg = "WebSocket connection closed"
            logger.error(f"{tool_name}: {error_msg}")
            self.connected = False
            return False, None, error_msg
        except WebSocketException as e:
            error_msg = f"WebSocket error: {str(e)}"
            logger.error(f"{tool_name}: {error_msg}")
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"{tool_name}: {error_msg}")
            return False, None, error_msg
    
    async def execute_tool_with_metrics(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        baseline_version: str,
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Execute a tool and collect performance metrics.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            baseline_version: Baseline version identifier
            iteration: Iteration number (for tracking)
        
        Returns:
            Dictionary with execution metrics
        """
        start_time = time.time()
        
        try:
            # Execute tool
            success, outputs, error = await self.call_tool(tool_name, arguments)
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Build result
            result = {
                "tool_name": tool_name,
                "iteration": iteration,
                "status": "success" if success else "error",
                "latency_ms": round(latency_ms, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "baseline_version": baseline_version
            }
            
            if not success:
                result["error"] = error
            else:
                # Extract text content from outputs
                result["output_count"] = len(outputs) if outputs else 0
                
            return result
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return {
                "tool_name": tool_name,
                "iteration": iteration,
                "status": "error",
                "error": f"Execution failed: {str(e)}",
                "latency_ms": round(latency_ms, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "baseline_version": baseline_version
            }
    
    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.disconnect()

