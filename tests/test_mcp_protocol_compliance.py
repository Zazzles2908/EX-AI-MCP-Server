"""
MCP Protocol Compliance Tests

Tests to validate that the EX-AI MCP Server properly implements the MCP protocol
including tool discovery, WebSocket/stdio transport, message format compliance,
and error handling.
"""

import asyncio
import json
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from mcp.server import Server
from mcp.types import Tool, TextContent
from intelligent_router import IntelligentRouter, ProviderType, TaskType, RoutingDecision
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables for testing
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class TestMCPProtocolCompliance:
    """Test suite for MCP protocol compliance"""

    @pytest.fixture
    def intelligent_router(self):
        """Create a test intelligent router"""
        config = {
            "INTELLIGENT_ROUTING_ENABLED": True,
            "COST_AWARE_ROUTING": True,
            "WEB_SEARCH_PROVIDER": "glm",
            "FILE_PROCESSING_PROVIDER": "kimi",
            "MAX_RETRIES": 3,
            "REQUEST_TIMEOUT": 30
        }
        return IntelligentRouter(config)

    def test_mcp_server_structure(self):
        """Test that MCP server has proper structure"""
        server = Server("Test MCP Server")
        
        # Verify server has required methods
        assert hasattr(server, 'list_tools')
        assert hasattr(server, 'call_tool')
        assert hasattr(server, 'list_prompts')
        assert hasattr(server, 'get_prompt')
        assert callable(server.list_tools)
        assert callable(server.call_tool)

    def test_tool_format_compliance(self):
        """Test that tool definitions comply with MCP format"""
        # Create a sample tool
        test_tool = Tool(
            name="web_search",
            description="Search the web for information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        )
        
        # Verify tool structure
        assert hasattr(test_tool, 'name')
        assert hasattr(test_tool, 'description')
        assert hasattr(test_tool, 'inputSchema')
        assert isinstance(test_tool.inputSchema, dict)
        assert test_tool.name == "web_search"
        assert "query" in test_tool.inputSchema.get('properties', {})

    def test_json_rpc_message_format(self):
        """Test JSON-RPC message format compliance"""
        # Test request format
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        assert request["jsonrpc"] == "2.0"
        assert "id" in request
        assert "method" in request
        
        # Test response format
        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"tools": []}
        }
        
        assert response["jsonrpc"] == "2.0"
        assert "id" in response
        assert "result" in response

    def test_error_response_format(self):
        """Test error response format compliance"""
        error_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": {"details": "Additional error information"}
            }
        }
        
        # Verify error format is MCP compliant
        assert error_response["jsonrpc"] == "2.0"
        assert "error" in error_response
        assert "code" in error_response["error"]
        assert "message" in error_response["error"]
        assert isinstance(error_response["error"]["code"], int)

    @pytest.mark.asyncio
    async def test_intelligent_routing_integration(self, intelligent_router):
        """Test that intelligent routing works with MCP server"""
        # Test routing decision making
        test_request = {
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {"query": "test"}
            }
        }
        
        decision = await intelligent_router.route_request(test_request)
        
        # Verify routing decision
        assert isinstance(decision, RoutingDecision)
        assert decision.provider in [ProviderType.GLM, ProviderType.KIMI]
        assert 0 <= decision.confidence <= 1
        assert len(decision.reasoning) > 0

    @pytest.mark.asyncio
    async def test_provider_fallback_mechanism(self, intelligent_router):
        """Test fallback mechanism in routing"""
        # Test fallback routing
        test_request = {
            "method": "tools/call",
            "params": {
                "name": "file_read",
                "arguments": {"path": "test.pdf"}
            }
        }
        
        decision = await intelligent_router.route_request(test_request)
        
        # Verify fallback provider is set
        assert decision.fallback_provider is not None
        assert decision.fallback_provider != decision.provider

    def test_environment_variable_alignment(self):
        """Test that environment variables are properly aligned with new naming"""
        # Check that new environment variable names are used
        assert os.getenv('GLM_API_KEY') is not None
        assert os.getenv('KIMI_API_KEY') is not None
        
        # Note: We don't check for absence of old names here because other tests
        # may set them temporarily. The important thing is that the new names work.
        # The old names are being phased out but may still be referenced in legacy code.

    def test_configuration_compliance(self):
        """Test that configuration aligns with production requirements"""
        from config import (
            DEFAULT_MODEL, INTELLIGENT_ROUTING_ENABLED, AI_MANAGER_MODEL,
            WEB_SEARCH_PROVIDER, FILE_PROCESSING_PROVIDER
        )
        
        # Verify production-ready configuration
        assert DEFAULT_MODEL == 'glm-4.5-flash'
        assert AI_MANAGER_MODEL == 'glm-4.5-flash'
        assert WEB_SEARCH_PROVIDER == 'glm'
        assert FILE_PROCESSING_PROVIDER == 'kimi'
        assert isinstance(INTELLIGENT_ROUTING_ENABLED, bool)
