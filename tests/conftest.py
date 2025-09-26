
"""
Pytest configuration and shared fixtures for EX-AI MCP Server tests

This module provides common fixtures, test configuration, and utilities
used across the test suite.
"""

import pytest
import asyncio
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Import test utilities
from tests.mock_helpers import MockProvider, MockRouter, MockTransport


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_api_keys():
    """Provide test API keys for testing"""
    return {
        'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
        'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
    }


@pytest.fixture
def test_environment(test_api_keys):
    """Set up test environment variables"""
    test_env = {
        **test_api_keys,
        'AI_MANAGER_MODEL': 'glm-4.5-flash',
        'KIMI_MODEL': 'moonshot-v1-8k',
        'REQUEST_TIMEOUT': '30',
        'MAX_RETRIES': '3',
        'ENABLE_INTELLIGENT_ROUTING': 'true',
        'LOG_LEVEL': 'DEBUG',
        'ENVIRONMENT': 'test'
    }
    
    with patch.dict('os.environ', test_env):
        yield test_env


@pytest.fixture
def mock_glm_response():
    """Standard mock response for GLM provider"""
    return {
        "choices": [{
            "message": {
                "content": "Mock GLM response for testing",
                "tool_calls": [{
                    "function": {
                        "name": "web_search",
                        "arguments": '{"results": ["result1", "result2"]}'
                    }
                }]
            }
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 150,
            "total_tokens": 250
        }
    }


@pytest.fixture
def mock_kimi_response():
    """Standard mock response for Kimi provider"""
    return {
        "choices": [{
            "message": {
                "content": "Mock Kimi response for file processing testing"
            }
        }],
        "usage": {
            "prompt_tokens": 80,
            "completion_tokens": 120,
            "total_tokens": 200
        }
    }


@pytest.fixture
def mock_http_session():
    """Mock aiohttp ClientSession for testing"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = Mock()
        mock_response.status = 200
        mock_response.json = AsyncMock()
        
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        yield mock_session


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file for testing"""
    config_content = """
# Test configuration file
ZHIPUAI_API_KEY=test_glm_key
MOONSHOT_API_KEY=test_kimi_key
AI_MANAGER_MODEL=glm-4.5-flash
REQUEST_TIMEOUT=30
MAX_RETRIES=3
ENABLE_INTELLIGENT_ROUTING=true
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(config_content)
        f.flush()
        yield f.name
    
    os.unlink(f.name)


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for testing"""
    mock_ws = Mock()
    mock_ws.send = AsyncMock()
    mock_ws.recv = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


@pytest.fixture
def sample_mcp_requests():
    """Sample MCP requests for testing"""
    return {
        "list_tools": {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        "call_tool": {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "query": "test query",
                    "max_results": 5
                }
            }
        },
        "invalid_request": {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "invalid/method",
            "params": {}
        }
    }


@pytest.fixture
def performance_thresholds():
    """Performance thresholds for testing"""
    return {
        "web_search_max_time": 5.0,
        "file_processing_max_time": 3.0,
        "general_chat_max_time": 2.0,
        "concurrent_requests_max_time": 10.0,
        "max_memory_usage_mb": 500
    }


@pytest.fixture
def test_files_directory():
    """Create a temporary directory with test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample test files
        test_files = {
            "sample.txt": "This is a sample text file for testing.",
            "data.json": '{"test": "data", "numbers": [1, 2, 3]}',
            "code.py": "def hello_world():\n    print('Hello, World!')\n",
            "document.md": "# Test Document\n\nThis is a test markdown document."
        }
        
        for filename, content in test_files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        yield temp_dir


@pytest.fixture
def mock_logging():
    """Mock logging for testing"""
    with patch('logging.getLogger') as mock_logger:
        logger_instance = Mock()
        logger_instance.info = Mock()
        logger_instance.warning = Mock()
        logger_instance.error = Mock()
        logger_instance.debug = Mock()
        
        mock_logger.return_value = logger_instance
        yield logger_instance


@pytest.fixture(autouse=True)
def cleanup_after_test():
    """Cleanup fixture that runs after each test"""
    yield
    # Cleanup any test artifacts
    # This runs after each test completes


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance
pytest.mark.slow = pytest.mark.slow


# Custom assertions
def assert_mcp_response_format(response):
    """Assert that a response follows MCP format"""
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "id" in response
    assert ("result" in response) or ("error" in response)


def assert_provider_response_format(response):
    """Assert that a provider response has the expected format"""
    assert "choices" in response
    assert len(response["choices"]) > 0
    assert "message" in response["choices"][0]
    assert "content" in response["choices"][0]["message"]


def assert_routing_decision_format(decision):
    """Assert that a routing decision has the expected format"""
    from intelligent_router import RoutingDecision, ProviderType
    
    assert isinstance(decision, RoutingDecision)
    assert isinstance(decision.provider, ProviderType)
    assert isinstance(decision.confidence, float)
    assert 0.0 <= decision.confidence <= 1.0
    assert isinstance(decision.reasoning, str)
    assert len(decision.reasoning) > 0


# Test utilities
class TestDataGenerator:
    """Generate test data for various scenarios"""
    
    @staticmethod
    def generate_web_search_requests(count: int = 5):
        """Generate web search test requests"""
        return [
            {
                "tool": "web_search",
                "parameters": {
                    "query": f"test query {i}",
                    "max_results": 5 + i
                }
            }
            for i in range(count)
        ]
    
    @staticmethod
    def generate_file_processing_requests(count: int = 5):
        """Generate file processing test requests"""
        return [
            {
                "tool": "file_read",
                "parameters": {
                    "path": f"test_file_{i}.txt",
                    "analysis_type": "summary"
                }
            }
            for i in range(count)
        ]
    
    @staticmethod
    def generate_mixed_requests(count: int = 10):
        """Generate mixed request types for testing"""
        tools = ["web_search", "file_read", "general_chat", "code_analysis"]
        requests = []
        
        for i in range(count):
            tool = tools[i % len(tools)]
            if tool == "web_search":
                request = {
                    "tool": tool,
                    "parameters": {"query": f"query {i}", "max_results": 5}
                }
            elif tool == "file_read":
                request = {
                    "tool": tool,
                    "parameters": {"path": f"file_{i}.txt"}
                }
            elif tool == "general_chat":
                request = {
                    "tool": tool,
                    "parameters": {"message": f"question {i}"}
                }
            else:  # code_analysis
                request = {
                    "tool": tool,
                    "parameters": {"code": f"def function_{i}(): pass"}
                }
            
            requests.append(request)
        
        return requests


# Export test utilities
__all__ = [
    'assert_mcp_response_format',
    'assert_provider_response_format', 
    'assert_routing_decision_format',
    'TestDataGenerator'
]
