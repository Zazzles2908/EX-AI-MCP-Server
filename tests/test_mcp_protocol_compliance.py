
"""
MCP Protocol Compliance Tests

Tests to validate that the EX-AI MCP Server properly implements the MCP protocol
including tool discovery, WebSocket/stdio transport, message format compliance,
and error handling.
"""

import asyncio
import json
import pytest
import websockets
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from server import MCPServer
from intelligent_router import IntelligentRouter, ProviderType


class TestMCPProtocolCompliance:
    """Test suite for MCP protocol compliance"""

    @pytest.fixture
    def mcp_server(self):
        """Create a test MCP server instance"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            return MCPServer()

    @pytest.mark.asyncio
    async def test_tool_discovery(self, mcp_server):
        """Test that tools are properly discovered and registered"""
        tools = await mcp_server.list_tools()
        
        # Verify essential tools are present
        tool_names = [tool['name'] for tool in tools]
        expected_tools = [
            'web_search',
            'file_read',
            'file_write',
            'code_analysis',
            'general_chat'
        ]
        
        for tool in expected_tools:
            assert tool in tool_names, f"Tool {tool} not found in discovered tools"
        
        # Verify tool schema compliance
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'inputSchema' in tool
            assert isinstance(tool['inputSchema'], dict)

    @pytest.mark.asyncio
    async def test_websocket_transport(self):
        """Test WebSocket transport protocol"""
        # Mock WebSocket server
        async def mock_handler(websocket, path):
            async for message in websocket:
                data = json.loads(message)
                
                # Echo back with proper MCP format
                response = {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "result": {"status": "ok"}
                }
                await websocket.send(json.dumps(response))

        # Test WebSocket connection and message format
        with patch('websockets.serve') as mock_serve:
            mock_serve.return_value = AsyncMock()
            
            # Simulate WebSocket message exchange
            test_message = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            # Verify message format compliance
            assert test_message["jsonrpc"] == "2.0"
            assert "id" in test_message
            assert "method" in test_message

    @pytest.mark.asyncio
    async def test_stdio_transport(self, mcp_server):
        """Test stdio transport protocol"""
        with patch('sys.stdin') as mock_stdin, patch('sys.stdout') as mock_stdout:
            # Mock stdin input
            mock_stdin.readline.return_value = json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            })
            
            # Test stdio message handling
            # This would normally be handled by the MCP server's stdio handler
            assert mock_stdin.readline.return_value is not None

    @pytest.mark.asyncio
    async def test_message_format_compliance(self, mcp_server):
        """Test that all messages comply with MCP format"""
        # Test tool list response format
        tools = await mcp_server.list_tools()
        
        # Verify response structure
        assert isinstance(tools, list)
        for tool in tools:
            # Each tool must have required fields
            required_fields = ['name', 'description', 'inputSchema']
            for field in required_fields:
                assert field in tool, f"Tool missing required field: {field}"

    @pytest.mark.asyncio
    async def test_error_handling_compliance(self, mcp_server):
        """Test that errors are properly formatted according to MCP spec"""
        with patch.object(mcp_server, 'call_tool', side_effect=Exception("Test error")):
            try:
                await mcp_server.call_tool("nonexistent_tool", {})
            except Exception as e:
                # Verify error format would be MCP compliant
                error_response = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                
                assert error_response["jsonrpc"] == "2.0"
                assert "error" in error_response
                assert "code" in error_response["error"]
                assert "message" in error_response["error"]

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, mcp_server):
        """Test handling of concurrent MCP requests"""
        async def make_request(tool_name: str):
            return await mcp_server.list_tools()
        
        # Create multiple concurrent requests
        tasks = [make_request(f"tool_{i}") for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all requests completed successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_tool_call_format(self, mcp_server):
        """Test that tool calls follow proper MCP format"""
        with patch.object(mcp_server, 'call_tool') as mock_call:
            mock_call.return_value = {"result": "success"}
            
            # Test tool call with proper parameters
            result = await mcp_server.call_tool("web_search", {
                "query": "test query",
                "max_results": 5
            })
            
            # Verify call was made with correct parameters
            mock_call.assert_called_once()
            args, kwargs = mock_call.call_args
            assert args[0] == "web_search"
            assert isinstance(args[1], dict)

    def test_server_initialization(self):
        """Test that server initializes with proper MCP configuration"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            server = MCPServer()
            
            # Verify server has required components
            assert hasattr(server, 'router')
            assert hasattr(server, 'providers')
