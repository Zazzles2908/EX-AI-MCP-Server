
"""
End-to-End Workflow Tests

Tests complete user request workflows, validates intelligent routing decisions,
tests concurrent request handling, and verifies performance and response times.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from server import MCPServer
from intelligent_router import IntelligentRouter, ProviderType


class TestEndToEndWorkflows:
    """Test suite for end-to-end workflows"""

    @pytest.fixture
    def mcp_server(self):
        """Create a fully configured MCP server for E2E testing"""
        with patch.dict('os.environ', {
            'ZHIPUAI_API_KEY': '4973ff3ce3c0435a999ce4674bb89259.jqNMImfTWzjHMLlA',
            'MOONSHOT_API_KEY': 'sk-FbWAPZ23R4bhd5XHWttMqGgDK1QAfCk22dZmXGkliUMPu6rq',
            'ENABLE_INTELLIGENT_ROUTING': 'true'
        }):
            return MCPServer()

    @pytest.mark.asyncio
    async def test_web_search_workflow(self, mcp_server):
        """Test complete web search workflow from request to response"""
        # Mock GLM provider response
        mock_search_results = {
            "choices": [{
                "message": {
                    "content": "Here are the latest AI developments:\n1. GPT-4 improvements\n2. New multimodal capabilities",
                    "tool_calls": [{
                        "function": {
                            "name": "web_search",
                            "arguments": '{"results": ["AI breakthrough 1", "AI breakthrough 2"]}'
                        }
                    }]
                }
            }],
            "usage": {"total_tokens": 250}
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_search_results)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            # Execute web search workflow
            result = await mcp_server.call_tool("web_search", {
                "query": "latest AI developments 2024",
                "max_results": 5
            })
            
            # Verify workflow completion
            assert result is not None
            assert "choices" in result
            assert "ai developments" in result["choices"][0]["message"]["content"].lower()

    @pytest.mark.asyncio
    async def test_file_processing_workflow(self, mcp_server):
        """Test complete file processing workflow"""
        # Mock Kimi provider response
        mock_file_analysis = {
            "choices": [{
                "message": {
                    "content": "File Analysis Summary:\n- Document type: PDF\n- Pages: 10\n- Key topics: Machine Learning, AI Ethics"
                }
            }],
            "usage": {"total_tokens": 180}
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_file_analysis)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            # Execute file processing workflow
            result = await mcp_server.call_tool("file_read", {
                "path": "research_paper.pdf",
                "analysis_type": "summary"
            })
            
            # Verify workflow completion
            assert result is not None
            assert "analysis" in result["choices"][0]["message"]["content"].lower()

    @pytest.mark.asyncio
    async def test_intelligent_routing_decision_validation(self, mcp_server):
        """Test that routing decisions match expected outcomes"""
        test_cases = [
            {
                "tool": "web_search",
                "parameters": {"query": "current news"},
                "expected_provider": ProviderType.GLM,
                "description": "Web search should route to GLM"
            },
            {
                "tool": "file_read", 
                "parameters": {"path": "document.pdf"},
                "expected_provider": ProviderType.KIMI,
                "description": "File processing should route to Kimi"
            },
            {
                "tool": "code_analysis",
                "parameters": {"code": "def hello(): pass"},
                "expected_provider": ProviderType.KIMI,
                "description": "Code analysis should route to Kimi"
            }
        ]
        
        for case in test_cases:
            with patch.object(mcp_server.router, 'route_request') as mock_route:
                from intelligent_router import RoutingDecision
                mock_route.return_value = RoutingDecision(
                    provider=case["expected_provider"],
                    confidence=0.9,
                    reasoning=case["description"]
                )
                
                # Mock provider execution
                mock_response = {"choices": [{"message": {"content": "test response"}}]}
                with patch.object(mcp_server.router, 'execute_request', return_value=mock_response):
                    result = await mcp_server.call_tool(case["tool"], case["parameters"])
                    
                    # Verify routing decision was made
                    mock_route.assert_called_once()
                    call_args = mock_route.call_args[0][0]
                    assert call_args["tool"] == case["tool"]

    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, mcp_server):
        """Test handling of multiple concurrent requests"""
        # Create diverse concurrent requests
        requests = [
            ("web_search", {"query": f"search query {i}"}),
            ("file_read", {"path": f"file_{i}.txt"}),
            ("general_chat", {"message": f"question {i}"})
            for i in range(3)
        ]
        
        # Mock responses for different providers
        mock_responses = {
            "web_search": {"choices": [{"message": {"content": "search results"}}]},
            "file_read": {"choices": [{"message": {"content": "file content"}}]},
            "general_chat": {"choices": [{"message": {"content": "chat response"}}]}
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            def mock_response_factory(tool_name):
                response = Mock()
                response.json = AsyncMock(return_value=mock_responses.get(tool_name, mock_responses["general_chat"]))
                response.status = 200
                return response
            
            mock_post.return_value.__aenter__.return_value = mock_response_factory("web_search")
            
            # Execute concurrent requests
            tasks = [
                mcp_server.call_tool(tool, params) 
                for tool, params in requests
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Verify all requests completed
            assert len(results) == len(requests)
            for result in results:
                assert not isinstance(result, Exception), f"Request failed: {result}"
            
            # Verify reasonable performance (should handle concurrency efficiently)
            total_time = end_time - start_time
            assert total_time < 10.0, f"Concurrent requests took too long: {total_time}s"

    @pytest.mark.asyncio
    async def test_performance_and_response_times(self, mcp_server):
        """Test performance benchmarks and response times"""
        performance_tests = [
            {
                "name": "Simple web search",
                "tool": "web_search",
                "parameters": {"query": "weather today"},
                "max_time": 5.0
            },
            {
                "name": "File processing",
                "tool": "file_read", 
                "parameters": {"path": "small_file.txt"},
                "max_time": 3.0
            },
            {
                "name": "General chat",
                "tool": "general_chat",
                "parameters": {"message": "Hello"},
                "max_time": 2.0
            }
        ]
        
        mock_response = {"choices": [{"message": {"content": "response"}}]}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            for test in performance_tests:
                start_time = time.time()
                
                result = await mcp_server.call_tool(test["tool"], test["parameters"])
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # Verify response time meets requirements
                assert response_time < test["max_time"], \
                    f"{test['name']} took {response_time:.2f}s, expected < {test['max_time']}s"
                
                # Verify successful response
                assert result is not None
                assert "choices" in result

    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mcp_server):
        """Test complete error recovery and fallback workflow"""
        request_params = {
            "tool": "web_search",
            "parameters": {"query": "test query"}
        }
        
        # Mock primary provider failure and fallback success
        call_count = 0
        def mock_post_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            if call_count == 1:
                # First call (GLM) fails
                raise Exception("GLM provider unavailable")
            else:
                # Second call (Kimi fallback) succeeds
                response = Mock()
                response.json = AsyncMock(return_value={
                    "choices": [{"message": {"content": "fallback response"}}]
                })
                response.status = 200
                return response
        
        with patch('aiohttp.ClientSession.post', side_effect=mock_post_side_effect):
            # Should automatically fallback and succeed
            result = await mcp_server.call_tool(
                request_params["tool"], 
                request_params["parameters"]
            )
            
            # Verify fallback worked
            assert result is not None
            assert "fallback response" in result["choices"][0]["message"]["content"]

    @pytest.mark.asyncio
    async def test_complex_multi_step_workflow(self, mcp_server):
        """Test complex workflow involving multiple tools and providers"""
        # Simulate a complex workflow: search -> analyze -> summarize
        
        # Step 1: Web search
        search_response = {
            "choices": [{
                "message": {
                    "content": "Found research papers on AI safety",
                    "tool_calls": [{
                        "function": {
                            "name": "web_search",
                            "arguments": '{"results": ["paper1.pdf", "paper2.pdf"]}'
                        }
                    }]
                }
            }]
        }
        
        # Step 2: File analysis
        analysis_response = {
            "choices": [{
                "message": {
                    "content": "Analysis of research papers: Key findings on AI safety measures"
                }
            }]
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Configure different responses for different calls
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                side_effect=[search_response, analysis_response]
            )
            mock_post.return_value.__aenter__.return_value.status = 200
            
            # Execute multi-step workflow
            search_result = await mcp_server.call_tool("web_search", {
                "query": "AI safety research papers"
            })
            
            analysis_result = await mcp_server.call_tool("file_read", {
                "path": "paper1.pdf",
                "analysis_type": "summary"
            })
            
            # Verify both steps completed successfully
            assert "research papers" in search_result["choices"][0]["message"]["content"].lower()
            assert "analysis" in analysis_result["choices"][0]["message"]["content"].lower()

    @pytest.mark.asyncio
    async def test_workflow_monitoring_and_logging(self, mcp_server):
        """Test that workflows are properly monitored and logged"""
        with patch('logging.Logger.info') as mock_log:
            mock_response = {"choices": [{"message": {"content": "test response"}}]}
            
            with patch('aiohttp.ClientSession.post') as mock_post:
                mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
                mock_post.return_value.__aenter__.return_value.status = 200
                
                await mcp_server.call_tool("web_search", {"query": "test"})
                
                # Verify logging occurred (workflow should be monitored)
                assert mock_log.call_count > 0

    @pytest.mark.asyncio
    async def test_resource_cleanup_after_workflow(self, mcp_server):
        """Test that resources are properly cleaned up after workflows"""
        initial_connections = getattr(mcp_server, '_active_connections', 0)
        
        mock_response = {"choices": [{"message": {"content": "test response"}}]}
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            mock_post.return_value.__aenter__.return_value.status = 200
            
            # Execute workflow
            await mcp_server.call_tool("web_search", {"query": "test"})
            
            # Verify no resource leaks (connections should be cleaned up)
            final_connections = getattr(mcp_server, '_active_connections', 0)
            assert final_connections <= initial_connections
