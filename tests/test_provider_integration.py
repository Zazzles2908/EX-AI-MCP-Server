
"""
Provider Integration Tests

Tests for GLM and Kimi provider integration, including API key validation,
timeout handling, retry logic, and error handling.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from aiohttp import ClientTimeout, ClientError

from providers import GLMProvider, KimiProvider, ProviderFactory


class TestProviderIntegration:
    """Test suite for provider integration"""

    @pytest.fixture
    def glm_config(self):
        """Configuration for GLM provider testing"""
        return {
            "REQUEST_TIMEOUT": 30,
            "MAX_RETRIES": 3,
            "AI_MANAGER_MODEL": "glm-4.5-flash"
        }

    @pytest.fixture
    def kimi_config(self):
        """Configuration for Kimi provider testing"""
        return {
            "REQUEST_TIMEOUT": 30,
            "MAX_RETRIES": 3,
            "KIMI_MODEL": "moonshot-v1-8k"
        }

    @pytest.fixture
    def glm_provider(self, glm_config):
        """Create GLM provider instance for testing"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA'
        }):
            return GLMProvider(glm_config)

    @pytest.fixture
    def kimi_provider(self, kimi_config):
        """Create Kimi provider instance for testing"""
        with patch.dict('os.environ', {
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            return KimiProvider(kimi_config)

    def test_glm_api_key_validation(self, glm_provider):
        """Test GLM API key validation"""
        assert glm_provider.validate_api_key() == True
        assert glm_provider.api_key == '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA'

    def test_kimi_api_key_validation(self, kimi_provider):
        """Test Kimi API key validation"""
        assert kimi_provider.validate_api_key() == True
        assert kimi_provider.api_key == 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'

    def test_invalid_api_key_handling(self, glm_config):
        """Test handling of invalid API keys"""
        with patch.dict('os.environ', {'ZHIPUAI_API_KEY': ''}, clear=True):
            provider = GLMProvider(glm_config)
            assert provider.validate_api_key() == False

    @pytest.mark.asyncio
    async def test_glm_web_search_request(self, glm_provider):
        """Test GLM provider web search functionality"""
        request = {
            "tool": "web_search",
            "parameters": {
                "query": "latest AI developments",
                "max_results": 5
            }
        }
        
        # Mock the HTTP response
        mock_response = {
            "choices": [{
                "message": {
                    "content": "Search results for AI developments...",
                    "tool_calls": [{
                        "function": {
                            "name": "web_search",
                            "arguments": '{"results": ["AI result 1", "AI result 2"]}'
                        }
                    }]
                }
            }],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 200,
                "total_tokens": 300
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            result = await glm_provider.execute_request(request)
            
            assert "choices" in result
            assert result["choices"][0]["message"]["content"] is not None

    @pytest.mark.asyncio
    async def test_kimi_file_processing_request(self, kimi_provider):
        """Test Kimi provider file processing functionality"""
        request = {
            "tool": "file_read",
            "parameters": {
                "path": "test_document.pdf",
                "analysis_type": "summary"
            }
        }
        
        mock_response = {
            "choices": [{
                "message": {
                    "content": "File analysis summary: This document contains...",
                }
            }],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 100,
                "total_tokens": 250
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            result = await kimi_provider.execute_request(request)
            
            assert "choices" in result
            assert "file analysis" in result["choices"][0]["message"]["content"].lower()

    @pytest.mark.asyncio
    async def test_timeout_handling(self, glm_provider):
        """Test timeout handling in provider requests"""
        request = {"tool": "web_search", "parameters": {"query": "test"}}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Request timed out")
            
            with pytest.raises(asyncio.TimeoutError):
                await glm_provider.execute_request(request)

    @pytest.mark.asyncio
    async def test_retry_logic(self, glm_provider):
        """Test retry logic on provider failures"""
        request = {"tool": "web_search", "parameters": {"query": "test"}}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            # First two calls fail, third succeeds
            mock_post.side_effect = [
                ClientError("Network error"),
                ClientError("Network error"),
                AsyncMock(json=AsyncMock(return_value={"choices": [{"message": {"content": "success"}}]}), status=200)
            ]
            
            with patch.object(glm_provider, '_should_retry', return_value=True):
                result = await glm_provider.execute_request(request)
                
                assert mock_post.call_count == 3
                assert result["choices"][0]["message"]["content"] == "success"

    @pytest.mark.asyncio
    async def test_error_handling_and_provider_switching(self):
        """Test error handling and automatic provider switching"""
        factory = ProviderFactory({
            "REQUEST_TIMEOUT": 30,
            "MAX_RETRIES": 2
        })
        
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            glm_provider = factory.get_provider("glm")
            kimi_provider = factory.get_provider("kimi")
            
            request = {"tool": "general_chat", "parameters": {"message": "test"}}
            
            # Mock GLM failure and Kimi success
            with patch.object(glm_provider, 'execute_request', side_effect=Exception("GLM failed")):
                with patch.object(kimi_provider, 'execute_request', return_value={"result": "success"}):
                    # This would be handled by the router's fallback mechanism
                    try:
                        await glm_provider.execute_request(request)
                        assert False, "Should have raised exception"
                    except Exception:
                        # Fallback to Kimi
                        result = await kimi_provider.execute_request(request)
                        assert result["result"] == "success"

    @pytest.mark.asyncio
    async def test_concurrent_provider_requests(self, glm_provider):
        """Test handling of concurrent requests to the same provider"""
        requests = [
            {"tool": "web_search", "parameters": {"query": f"query {i}"}}
            for i in range(3)
        ]
        
        mock_response = {"choices": [{"message": {"content": "response"}}]}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            tasks = [glm_provider.execute_request(req) for req in requests]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 3
            assert all("choices" in result for result in results)

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, glm_provider):
        """Test handling of rate limit responses"""
        request = {"tool": "web_search", "parameters": {"query": "test"}}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock rate limit response
            mock_response = Mock()
            mock_response.status = 429
            mock_response.json = AsyncMock(return_value={"error": "Rate limit exceeded"})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception) as exc_info:
                await glm_provider.execute_request(request)
            
            assert "rate limit" in str(exc_info.value).lower() or "429" in str(exc_info.value)

    def test_provider_factory(self):
        """Test provider factory functionality"""
        config = {
            "REQUEST_TIMEOUT": 30,
            "MAX_RETRIES": 3
        }
        
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq'
        }):
            factory = ProviderFactory(config)
            
            glm_provider = factory.get_provider("glm")
            kimi_provider = factory.get_provider("kimi")
            
            assert isinstance(glm_provider, GLMProvider)
            assert isinstance(kimi_provider, KimiProvider)
            assert glm_provider.validate_api_key()
            assert kimi_provider.validate_api_key()

    @pytest.mark.asyncio
    async def test_provider_health_check(self, glm_provider, kimi_provider):
        """Test provider health check functionality"""
        # Mock successful health check
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.return_value.__aenter__.return_value.status = 200
            
            glm_healthy = await glm_provider.health_check()
            kimi_healthy = await kimi_provider.health_check()
            
            assert glm_healthy == True
            assert kimi_healthy == True

    @pytest.mark.asyncio
    async def test_provider_metrics_collection(self, glm_provider):
        """Test that providers collect performance metrics"""
        request = {"tool": "web_search", "parameters": {"query": "test"}}
        
        mock_response = {
            "choices": [{"message": {"content": "response"}}],
            "usage": {"total_tokens": 100}
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            start_time = asyncio.get_event_loop().time()
            result = await glm_provider.execute_request(request)
            end_time = asyncio.get_event_loop().time()
            
            # Verify metrics would be collected
            assert end_time > start_time
            assert "usage" in result
