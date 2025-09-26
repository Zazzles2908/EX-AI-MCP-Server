
"""
Load testing for EX-AI MCP Server using Locust

This module provides load testing scenarios to validate the server's
performance under concurrent load.
"""

import json
import asyncio
import websockets
from locust import User, task, between
from locust.exception import LocustError


class MCPWebSocketUser(User):
    """Locust user that connects via WebSocket to test MCP server"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Initialize WebSocket connection"""
        self.websocket = None
        self.request_id = 0
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect("ws://localhost:8765")
        except Exception as e:
            raise LocustError(f"Failed to connect to WebSocket: {e}")
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
    
    async def send_mcp_request(self, method: str, params: dict = None):
        """Send MCP request and measure response time"""
        if not self.websocket:
            await self.connect()
        
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            
            end_time = asyncio.get_event_loop().time()
            response_time = (end_time - start_time) * 1000  # Convert to ms
            
            response_data = json.loads(response)
            
            # Report success/failure to Locust
            if "error" in response_data:
                self.environment.events.request_failure.fire(
                    request_type="WebSocket",
                    name=method,
                    response_time=response_time,
                    response_length=len(response),
                    exception=Exception(response_data["error"]["message"])
                )
            else:
                self.environment.events.request_success.fire(
                    request_type="WebSocket",
                    name=method,
                    response_time=response_time,
                    response_length=len(response)
                )
            
            return response_data
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            response_time = (end_time - start_time) * 1000
            
            self.environment.events.request_failure.fire(
                request_type="WebSocket",
                name=method,
                response_time=response_time,
                response_length=0,
                exception=e
            )
            raise
    
    @task(3)
    def test_list_tools(self):
        """Test tools/list endpoint"""
        asyncio.run(self.send_mcp_request("tools/list"))
    
    @task(5)
    def test_web_search(self):
        """Test web search tool"""
        params = {
            "name": "web_search",
            "arguments": {
                "query": "test search query",
                "max_results": 5
            }
        }
        asyncio.run(self.send_mcp_request("tools/call", params))
    
    @task(3)
    def test_file_processing(self):
        """Test file processing tool"""
        params = {
            "name": "file_read",
            "arguments": {
                "path": "test_file.txt",
                "analysis_type": "summary"
            }
        }
        asyncio.run(self.send_mcp_request("tools/call", params))
    
    @task(2)
    def test_general_chat(self):
        """Test general chat tool"""
        params = {
            "name": "general_chat",
            "arguments": {
                "message": "Hello, this is a test message"
            }
        }
        asyncio.run(self.send_mcp_request("tools/call", params))
    
    def on_stop(self):
        """Cleanup when user stops"""
        if self.websocket:
            asyncio.run(self.disconnect())


class MCPStressTestUser(MCPWebSocketUser):
    """High-intensity stress test user"""
    
    wait_time = between(0.1, 0.5)  # Much faster requests
    
    @task(10)
    def rapid_fire_requests(self):
        """Send rapid requests to stress test the server"""
        for i in range(5):
            try:
                asyncio.run(self.send_mcp_request("tools/list"))
            except Exception:
                break  # Stop if server becomes unresponsive


class MCPConcurrencyTestUser(MCPWebSocketUser):
    """Test concurrent request handling"""
    
    @task(1)
    def concurrent_requests(self):
        """Send multiple concurrent requests"""
        async def run_concurrent():
            tasks = [
                self.send_mcp_request("tools/list"),
                self.send_mcp_request("tools/call", {
                    "name": "web_search",
                    "arguments": {"query": "concurrent test"}
                }),
                self.send_mcp_request("tools/call", {
                    "name": "general_chat", 
                    "arguments": {"message": "concurrent message"}
                })
            ]
            
            try:
                await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                print(f"Concurrent request failed: {e}")
        
        asyncio.run(run_concurrent())
