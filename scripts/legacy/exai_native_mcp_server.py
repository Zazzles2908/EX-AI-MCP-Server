#!/usr/bin/env python
"""
EXAI Native MCP Server - Direct programmatic access to EXAI tools

This MCP server provides native programmatic access to EXAI workflow tools
via MCP protocol, enabling AI coders to call tools like:
    mcp__exai_native__analyze()
    mcp__exai_native__debug()
    mcp__exai_native__chat()
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Bootstrap: Setup path
_repo_root = Path(__file__).resolve().parents[1]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.bootstrap import load_env, get_repo_root, setup_logging

# Load environment
load_env()

import websockets
from mcp.server import Server
from mcp.types import Tool, TextContent

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Configuration
EXAI_WS_HOST = os.getenv("EXAI_WS_HOST", "127.0.0.1")
EXAI_WS_PORT = int(os.getenv("EXAI_WS_PORT", "8079"))
EXAI_WS_TOKEN = os.getenv("EXAI_WS_TOKEN", "test-token-12345")

# Setup logging
log_file_path = get_repo_root() / "logs" / "exai_native_mcp.log"
logger = setup_logging("exai_native_mcp", log_file=str(log_file_path))

# Create server
server = Server("exai-native-mcp")

# WebSocket connection management
_ws = None
_ws_lock = asyncio.Lock()


async def _ensure_ws():
    """Ensure WebSocket connection to daemon is established"""
    global _ws
    if _ws and _ws.close_code is None:
        return _ws

    async with _ws_lock:
        if _ws and _ws.close_code is None:
            return _ws

        uri = f"ws://{EXAI_WS_HOST}:{EXAI_WS_PORT}"
        try:
            logger.info(f"Connecting to {uri}...")
            _ws = await websockets.connect(uri, open_timeout=10)
            logger.info("WebSocket connected, sending hello...")

            # Hello handshake
            hello_msg = {
                "op": "hello",
                "token": EXAI_WS_TOKEN,
                "data": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"roots": {"listChanged": True}},
                    "clientInfo": {"name": "exai-native-mcp", "version": "1.0.0"}
                }
            }
            logger.info(f"Sending hello: {json.dumps(hello_msg)}")
            await _ws.send(json.dumps(hello_msg))
            logger.info("Hello sent, waiting for ack...")
            ack = await asyncio.wait_for(_ws.recv(), timeout=5)
            logger.info(f"Received ack: {ack}")
            ack_data = json.loads(ack)
            if not ack_data.get('ok'):
                raise RuntimeError(f"Auth failed: {ack_data}")

            logger.info(f"Connected to EXAI daemon at {uri}")
            return _ws
        except Exception as e:
            logger.error(f"Failed to connect to daemon: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise


async def _call_daemon_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Call a tool via WebSocket daemon"""
    ws = await _ensure_ws()
    req_id = f"native-{name}-{id(asyncio.get_running_loop())}"

    await ws.send(json.dumps({
        "op": "tool_call",
        "tool": {"name": name},
        "arguments": arguments or {},
        "request_id": req_id
    }))

    # Wait for response
    timeout = 120  # 2 minutes
    deadline = asyncio.get_running_loop().time() + timeout

    while True:
        remaining = max(0.1, deadline - asyncio.get_running_loop().time())
        try:
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
        except asyncio.TimeoutError:
            raise RuntimeError(f"Tool {name} timed out after {timeout}s")

        try:
            msg = json.loads(raw)
        except Exception:
            continue

        # Handle ack
        if msg.get("request_id") == req_id and msg.get("op") == "call_tool_ack":
            continue

        # Handle progress
        if msg.get("request_id") == req_id and msg.get("op") == "progress":
            continue

        # Handle result
        if msg.get("op") == "call_tool_res" and msg.get("request_id") == req_id:
            if msg.get("error"):
                raise RuntimeError(f"Daemon error: {msg['error']}")

            # Extract text content
            if isinstance(msg.get("text"), str) and msg.get("text").strip():
                return [TextContent(type="text", text=msg["text"])]

            outputs = []
            for o in msg.get("outputs", []):
                if (o or {}).get("type") == "text":
                    outputs.append(TextContent(type="text", text=(o or {}).get("text") or ""))
                else:
                    outputs.append(TextContent(type="text", text=json.dumps(o)))
            return outputs


# Tool definitions with proper schemas

TOOLS = [
    Tool(
        name="analyze",
        description="Analyze code or tasks with GLM-4.6",
        inputSchema={
            "type": "object",
            "properties": {
                "step": {"type": "string", "description": "Analysis step or task"},
                "step_number": {"type": "integer", "description": "Step number"},
                "total_steps": {"type": "integer", "description": "Total steps"},
                "next_step_required": {"type": "boolean", "description": "Whether next step is required"},
                "files_to_check": {"type": "array", "items": {"type": "string"}, "description": "Files to analyze"},
                "model": {"type": "string", "description": "Model to use (default: glm-4.6)", "default": "glm-4.6"},
                "temperature": {"type": "number", "description": "Temperature (0-1)", "default": 0.3},
                "thinking_mode": {"type": "string", "description": "Thinking mode", "enum": ["minimal", "low", "medium", "high", "max"]},
            },
            "required": ["step"]
        }
    ),
    Tool(
        name="debug",
        description="Debug issues with configurable thinking modes",
        inputSchema={
            "type": "object",
            "properties": {
                "request": {"type": "string", "description": "Debug request"},
                "thinking_mode": {"type": "string", "description": "Thinking depth", "enum": ["minimal", "low", "medium", "high", "max"]},
            },
            "required": ["request"]
        }
    ),
    Tool(
        name="codereview",
        description="Review code with GLM-4.6",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to review"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="chat",
        description="Chat with AI models",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Chat message"},
                "model": {"type": "string", "description": "Model to use"},
            },
            "required": ["message"]
        }
    ),
    Tool(
        name="refactor",
        description="Refactor code with Kimi",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to refactor"},
                "model": {"type": "string", "description": "Model (default: kimi-k2)", "default": "kimi-k2"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="testgen",
        description="Generate tests with GLM-4.6",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to generate tests for"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="thinkdeep",
        description="Deep thinking with Kimi",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "Question to think about"},
                "thinking_mode": {"type": "string", "description": "Thinking depth", "enum": ["minimal", "low", "medium", "high", "max"]},
            },
            "required": ["question"]
        }
    ),
    Tool(
        name="smart_file_query",
        description="Query files intelligently",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query about files"},
                "file_paths": {"type": "array", "items": {"type": "string"}, "description": "File paths to analyze"},
                "thinking_mode": {"type": "string", "description": "Thinking mode", "enum": ["minimal", "low", "medium", "high", "max"]},
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="status",
        description="Get server status",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="listmodels",
        description="List available models",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="planner",
        description="Create plans and task breakdowns",
        inputSchema={
            "type": "object",
            "properties": {
                "goal": {"type": "string", "description": "Goal to plan for"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["goal"]
        }
    ),
    Tool(
        name="secaudit",
        description="Perform security audit",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to audit"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="docgen",
        description="Generate documentation",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to document"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="tracer",
        description="Trace code execution",
        inputSchema={
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code to trace"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["code"]
        }
    ),
    Tool(
        name="consensus",
        description="Build consensus from multiple models",
        inputSchema={
            "type": "object",
            "properties": {
                "request": {"type": "string", "description": "Consensus request"},
                "models": {"type": "array", "items": {"type": "string"}, "description": "Models to consult"},
            },
            "required": ["request"]
        }
    ),
    Tool(
        name="precommit",
        description="Pre-commit checks",
        inputSchema={
            "type": "object",
            "properties": {
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files to check"},
                "model": {"type": "string", "description": "Model (default: glm-4.6)", "default": "glm-4.6"},
            },
            "required": ["files"]
        }
    ),
    Tool(
        name="version",
        description="Get version information",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="glm_payload_preview",
        description="Preview GLM payload",
        inputSchema={
            "type": "object",
            "properties": {
                "payload": {"type": "object", "description": "Payload to preview"},
            },
            "required": ["payload"]
        }
    ),
    Tool(
        name="kimi_chat_with_tools",
        description="Chat with Kimi using tools",
        inputSchema={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Chat message"},
                "files": {"type": "array", "items": {"type": "string"}, "description": "Files to include"},
            },
            "required": ["message"]
        }
    ),
]


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available EXAI tools"""
    logger.info("[LIST_TOOLS] Returning EXAI native tools")
    return TOOLS


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Call an EXAI tool"""
    logger.info(f"[CALL_TOOL] {name} with args: {list(arguments.keys()) if arguments else []}")
    try:
        result = await _call_daemon_tool(name, arguments)
        logger.info(f"[CALL_TOOL] {name} completed successfully")
        return result
    except Exception as e:
        logger.error(f"[CALL_TOOL] {name} failed: {e}")
        raise


async def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("EXAI Native MCP Server Starting")
    logger.info(f"Connecting to: {EXAI_WS_HOST}:{EXAI_WS_PORT}")
    logger.info(f"Tools available: {len(TOOLS)}")
    logger.info("=" * 80)

    # Establish WebSocket connection BEFORE starting MCP server
    logger.info("Establishing WebSocket connection to daemon...")
    try:
        await _ensure_ws()
        logger.info("WebSocket connection established successfully")
    except Exception as e:
        logger.error(f"Failed to establish WebSocket connection: {e}")
        logger.error("MCP server will not be able to execute tools")
        raise

    init_opts = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, init_opts)


if __name__ == "__main__":
    asyncio.run(main())
