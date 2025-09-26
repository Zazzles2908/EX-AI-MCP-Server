"""Helper functions for test mocking."""

from unittest.mock import Mock, AsyncMock
from typing import Dict, Any


class MockProvider:
    """Mock provider for testing"""
    
    def __init__(self, provider_type: str = "glm"):
        self.provider_type = provider_type
        self.api_key = "test_api_key"
        self.timeout = 30
        self.max_retries = 3
    
    def validate_api_key(self) -> bool:
        return True
    
    async def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "content": f"Mock {self.provider_type} response"
                }
            }],
            "usage": {"total_tokens": 100}
        }
    
    async def health_check(self) -> bool:
        return True


class MockRouter:
    """Mock intelligent router for testing"""
    
    def __init__(self):
        self.providers = {
            "glm": MockProvider("glm"),
            "kimi": MockProvider("kimi")
        }
    
    async def route_request(self, request: Dict[str, Any]):
        from intelligent_router import RoutingDecision, ProviderType
        
        # Simple routing logic for testing
        if "web_search" in request.get("tool", ""):
            provider = ProviderType.GLM
        elif "file" in request.get("tool", ""):
            provider = ProviderType.KIMI
        else:
            provider = ProviderType.GLM
        
        return RoutingDecision(
            provider=provider,
            confidence=0.9,
            reasoning=f"Mock routing to {provider.value}"
        )
    
    async def execute_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "choices": [{
                "message": {
                    "content": "Mock router response"
                }
            }]
        }


class MockTransport:
    """Mock transport for testing"""
    
    def __init__(self):
        self.messages = []
    
    async def send(self, message: str):
        self.messages.append(message)
    
    async def recv(self) -> str:
        return '{"jsonrpc": "2.0", "id": 1, "result": {"status": "ok"}}'


def create_mock_provider(provider_type: str = "glm") -> MockProvider:
    """Create a mock provider for testing"""
    return MockProvider(provider_type)


def create_mock_router() -> MockRouter:
    """Create a mock router for testing"""
    return MockRouter()


def create_mock_transport() -> MockTransport:
    """Create a mock transport for testing"""
    return MockTransport()
