"""
Test Factories for EX-AI MCP Server

Provides factories for creating test data objects including:
- Provider instances
- Request/Response objects
- Configuration objects
- File objects
- User session objects
"""

import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock


class ProviderFactory:
    """Factory for creating provider test instances"""

    @staticmethod
    def create_glm_provider(
        api_key: str = "test_glm_api_key",
        base_url: str = "https://test.glm.com/api",
        timeout: int = 30,
        retries: int = 3
    ) -> MagicMock:
        """Create a mocked GLM provider"""
        provider = MagicMock()
        provider.api_key = api_key
        provider.base_url = base_url
        provider.timeout = timeout
        provider.retries = retries
        provider.call_api = MagicMock(return_value={
            "choices": [{"text": "Test GLM response"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        })
        return provider

    @staticmethod
    def create_kimi_provider(
        api_key: str = "test_kimi_api_key",
        base_url: str = "https://test.kimi.com/api",
        timeout: int = 30,
        retries: int = 3
    ) -> MagicMock:
        """Create a mocked Kimi provider"""
        provider = MagicMock()
        provider.api_key = api_key
        provider.base_url = base_url
        provider.timeout = timeout
        provider.retries = retries
        provider.call_api = MagicMock(return_value={
            "choices": [{"text": "Test Kimi response"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        })
        return provider

    @staticmethod
    def create_provider_response(
        text: str = "Test response",
        model: str = "test-model",
        tokens_used: int = 30,
        success: bool = True,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a provider response object"""
        if not success:
            return {
                "success": False,
                "error": error or "Test error",
                "model": model
            }

        return {
            "success": True,
            "choices": [{"text": text}],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": tokens_used - 10,
                "total_tokens": tokens_used
            },
            "model": model,
            "created": int(time.time())
        }


class FileFactory:
    """Factory for creating file test objects"""

    @staticmethod
    def create_test_file(
        filename: str = "test.txt",
        content: str = "Test file content",
        size: Optional[int] = None,
        mime_type: str = "text/plain"
    ) -> Dict[str, Any]:
        """Create a test file object"""
        if size is None:
            size = len(content)

        return {
            "name": filename,
            "content": content,
            "size": size,
            "mime_type": mime_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "id": str(uuid.uuid4())
        }

    @staticmethod
    def create_file_metadata(
        filename: str = "test.txt",
        path: str = "/test/path/test.txt",
        size: int = 1024,
        checksum: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create file metadata"""
        return {
            "filename": filename,
            "path": path,
            "size": size,
            "checksum": checksum or str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "modified_at": datetime.now(timezone.utc).isoformat(),
            "id": str(uuid.uuid4())
        }


class UserFactory:
    """Factory for creating user test objects"""

    @staticmethod
    def create_user(
        user_id: Optional[str] = None,
        username: str = "testuser",
        email: str = "test@example.com",
        is_active: bool = True
    ) -> Dict[str, Any]:
        """Create a test user object"""
        return {
            "id": user_id or str(uuid.uuid4()),
            "username": username,
            "email": email,
            "is_active": is_active,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": datetime.now(timezone.utc).isoformat() if is_active else None
        }

    @staticmethod
    def create_user_session(
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create a test user session"""
        if expires_at is None:
            expires_at = datetime.now(timezone.utc)

        return {
            "user_id": user_id or str(uuid.uuid4()),
            "session_id": session_id or str(uuid.uuid4()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat(),
            "is_active": True
        }


class RequestFactory:
    """Factory for creating request test objects"""

    @staticmethod
    def create_chat_request(
        prompt: str = "Test prompt",
        model: str = "test-model",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False,
        provider: str = "glm"
    ) -> Dict[str, Any]:
        """Create a chat completion request"""
        return {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "provider": provider,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def create_file_upload_request(
        filename: str = "test.txt",
        content: Union[str, bytes] = "Test content",
        mime_type: str = "text/plain",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a file upload request"""
        return {
            "filename": filename,
            "content": content,
            "mime_type": mime_type,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


class ConfigFactory:
    """Factory for creating configuration test objects"""

    @staticmethod
    def create_app_config(
        debug: bool = False,
        log_level: str = "INFO",
        test_mode: bool = True
    ) -> Dict[str, Any]:
        """Create application configuration"""
        return {
            "debug": debug,
            "log_level": log_level,
            "test_mode": test_mode,
            "redis_url": "redis://localhost:6379/0",
            "supabase_url": "https://test.supabase.co",
            "supabase_key": "test-key"
        }

    @staticmethod
    def create_provider_config(
        name: str = "test",
        api_key: str = "test-key",
        base_url: str = "https://test.com/api",
        timeout: int = 30,
        enabled: bool = True
    ) -> Dict[str, Any]:
        """Create provider configuration"""
        return {
            "name": name,
            "api_key": api_key,
            "base_url": base_url,
            "timeout": timeout,
            "enabled": enabled,
            "retry_count": 3,
            "rate_limit": 100
        }


class MonitoringFactory:
    """Factory for creating monitoring test objects"""

    @staticmethod
    def create_metric(
        name: str = "test_metric",
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a test metric"""
        return {
            "name": name,
            "value": value,
            "tags": tags or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def create_health_status(
        component: str = "test_component",
        status: str = "healthy",
        message: str = "All good"
    ) -> Dict[str, Any]:
        """Create a health status object"""
        return {
            "component": component,
            "status": status,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": 0
        }


class WebSocketFactory:
    """Factory for creating WebSocket test objects"""

    @staticmethod
    def create_websocket_message(
        type: str = "chat",
        data: Optional[Dict[str, Any]] = None,
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a WebSocket message"""
        return {
            "type": type,
            "data": data or {},
            "message_id": message_id or str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @staticmethod
    def create_connection_event(
        connection_id: Optional[str] = None,
        event_type: str = "connected",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a connection event"""
        return {
            "connection_id": connection_id or str(uuid.uuid4()),
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {}
        }


class TestDataGenerator:
    """Generate various test data for different scenarios"""

    @staticmethod
    def generate_prompts(count: int = 5) -> List[str]:
        """Generate test prompts"""
        prompts = [
            "What is the capital of France?",
            "Explain quantum computing in simple terms",
            "Write a Python function to calculate fibonacci",
            "How does machine learning work?",
            "What are the benefits of microservices?",
            "Explain the difference between synchronous and asynchronous programming",
            "What is REST API?",
            "How to implement caching in web applications?",
            "What is database normalization?",
            "Explain CI/CD pipeline"
        ]
        return prompts[:count]

    @staticmethod
    def generate_file_names(count: int = 10) -> List[str]:
        """Generate test file names"""
        extensions = [".txt", ".py", ".md", ".json", ".yaml", ".csv", ".xml"]
        files = []
        for i in range(count):
            files.append(f"test_file_{i}{extensions[i % len(extensions)]}")
        return files

    @staticmethod
    def generate_users(count: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple test users"""
        return [
            UserFactory.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com"
            ) for i in range(count)
        ]

    @staticmethod
    def generate_provider_responses(
        count: int = 5,
        success_rate: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Generate multiple provider responses"""
        responses = []
        prompts = TestDataGenerator.generate_prompts(count)
        for i, prompt in enumerate(prompts):
            success = (i / count) < success_rate
            responses.append(
                ProviderFactory.create_provider_response(
                    text=f"Response to: {prompt}",
                    success=success,
                    error="Test error" if not success else None
                )
            )
        return responses


class MockContext:
    """Context manager for temporary mocking"""

    def __init__(self, **mocks):
        self.mocks = mocks
        self.patches = []

    def __enter__(self):
        from unittest.mock import patch
        for name, mock in self.mocks.items():
            patch_obj = patch(name, mock)
            patch_obj.start()
            self.patches.append(patch_obj)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from unittest.mock import patch
        for patch_obj in self.patches:
            patch_obj.stop()
