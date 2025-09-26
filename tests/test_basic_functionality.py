"""
Basic functionality tests for EX-AI MCP Server

Simple tests to validate core functionality without complex dependencies.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock


class TestBasicFunctionality:
    """Basic functionality test suite"""

    def test_environment_setup(self):
        """Test that test environment is properly configured"""
        # Check that test API keys are available
        assert os.getenv('ZHIPUAI_API_KEY') is not None
        assert os.getenv('MOONSHOT_API_KEY') is not None
        assert os.getenv('ENVIRONMENT') == 'test'

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test that async functionality works"""
        async def sample_async_function():
            await asyncio.sleep(0.01)
            return "async_result"
        
        result = await sample_async_function()
        assert result == "async_result"

    def test_mock_functionality(self):
        """Test that mocking works correctly"""
        mock_obj = Mock()
        mock_obj.test_method.return_value = "mocked_result"
        
        result = mock_obj.test_method()
        assert result == "mocked_result"
        mock_obj.test_method.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_mock_functionality(self):
        """Test that async mocking works correctly"""
        mock_obj = AsyncMock()
        mock_obj.async_method.return_value = "async_mocked_result"
        
        result = await mock_obj.async_method()
        assert result == "async_mocked_result"
        mock_obj.async_method.assert_called_once()

    def test_intelligent_router_imports(self):
        """Test that intelligent router can be imported"""
        try:
            from intelligent_router import ProviderType, TaskType
            assert ProviderType.GLM is not None
            assert ProviderType.KIMI is not None
            assert TaskType.WEB_SEARCH is not None
        except ImportError as e:
            pytest.skip(f"Intelligent router not available: {e}")

    def test_providers_imports(self):
        """Test that providers can be imported"""
        try:
            from providers import BaseProvider
            assert BaseProvider is not None
        except ImportError as e:
            pytest.skip(f"Providers not available: {e}")

    @pytest.mark.asyncio
    async def test_mock_provider_functionality(self):
        """Test mock provider functionality"""
        from tests.mock_helpers import MockProvider
        
        provider = MockProvider("test")
        assert provider.validate_api_key() == True
        
        request = {"tool": "test", "parameters": {"query": "test"}}
        result = await provider.execute_request(request)
        
        assert "choices" in result
        assert "Mock test response" in result["choices"][0]["message"]["content"]

    @pytest.mark.asyncio
    async def test_mock_router_functionality(self):
        """Test mock router functionality"""
        from tests.mock_helpers import MockRouter
        
        router = MockRouter()
        
        request = {"tool": "web_search", "parameters": {"query": "test"}}
        decision = await router.route_request(request)
        
        assert hasattr(decision, 'provider')
        assert hasattr(decision, 'confidence')
        assert hasattr(decision, 'reasoning')

    def test_configuration_loading(self):
        """Test basic configuration functionality"""
        # Test environment variable access
        api_key = os.getenv('ZHIPUAI_API_KEY')
        assert api_key is not None
        assert len(api_key) > 0
        
        # Test boolean conversion
        enable_routing = os.getenv('ENABLE_INTELLIGENT_ROUTING', 'false').lower() == 'true'
        assert isinstance(enable_routing, bool)

    def test_json_handling(self):
        """Test JSON handling functionality"""
        import json
        
        test_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Test serialization
        json_str = json.dumps(test_data)
        assert isinstance(json_str, str)
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        assert parsed_data == test_data

    @pytest.mark.asyncio
    async def test_websocket_mock(self):
        """Test WebSocket mocking functionality"""
        from tests.mock_helpers import MockTransport
        
        transport = MockTransport()
        
        # Test sending
        await transport.send("test message")
        assert "test message" in transport.messages
        
        # Test receiving
        response = await transport.recv()
        assert "jsonrpc" in response

    def test_file_operations(self):
        """Test file operation functionality"""
        import tempfile
        import os
        
        # Test temporary file creation
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        # Test file reading
        with open(temp_path, 'r') as f:
            content = f.read()
            assert content == "test content"
        
        # Cleanup
        os.unlink(temp_path)

    def test_logging_functionality(self):
        """Test logging functionality"""
        import logging
        
        logger = logging.getLogger(__name__)
        
        with patch.object(logger, 'info') as mock_info:
            logger.info("test log message")
            mock_info.assert_called_once_with("test log message")

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_performance_baseline(self):
        """Test performance baseline"""
        import time
        
        start_time = time.time()
        
        # Simulate some work
        await asyncio.sleep(0.01)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete quickly
        assert duration < 1.0

    def test_error_handling(self):
        """Test error handling functionality"""
        def function_that_raises():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            function_that_raises()
        
        assert "Test error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test async error handling"""
        async def async_function_that_raises():
            raise RuntimeError("Async test error")
        
        with pytest.raises(RuntimeError) as exc_info:
            await async_function_that_raises()
        
        assert "Async test error" in str(exc_info.value)
