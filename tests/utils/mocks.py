"""
Mock objects and utilities for EX-AI MCP Server testing

Provides pre-configured mock objects for:
- External API calls
- Database operations
- File system operations
- Redis operations
- WebSocket connections
"""

import json
from unittest.mock import AsyncMock, MagicMock, Mock
from typing import Any, Dict, List, Optional, Callable


class ProviderMocks:
    """Pre-configured mocks for provider operations"""

    @staticmethod
    def mock_glm_api_response(
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        raise_error: Optional[Exception] = None
    ) -> Mock:
        """Create a mock for GLM API calls"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json = Mock(return_value=response_data or {
            "choices": [{"text": "Mock GLM response"}],
            "usage": {"total_tokens": 30}
        })
        mock_response.text = json.dumps(response_data) if response_data else "{}"
        mock_response.raise_for_status = Mock()

        if raise_error:
            mock_response.raise_for_status.side_effect = raise_error

        return mock_response

    @staticmethod
    def mock_kimi_api_response(
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        raise_error: Optional[Exception] = None
    ) -> Mock:
        """Create a mock for Kimi API calls"""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.json = Mock(return_value=response_data or {
            "choices": [{"text": "Mock Kimi response"}],
            "usage": {"total_tokens": 30}
        })
        mock_response.text = json.dumps(response_data) if response_data else "{}"
        mock_response.raise_for_status = Mock()

        if raise_error:
            mock_response.raise_for_status.side_effect = raise_error

        return mock_response

    @staticmethod
    def create_mock_provider_client(
        provider_name: str = "glm",
        responses: Optional[List[Dict[str, Any]]] = None
    ) -> MagicMock:
        """Create a mock provider client with configurable responses"""
        client = MagicMock()
        client.name = provider_name

        # Default successful response
        default_response = {
            "success": True,
            "choices": [{"text": f"Mock response from {provider_name}"}],
            "usage": {"total_tokens": 30}
        }

        # Set up the call_api method
        if responses:
            # Rotate through provided responses
            response_iter = iter(responses)
            client.call_api = MagicMock(side_effect=lambda *args, **kwargs: next(response_iter, default_response))
        else:
            client.call_api = MagicMock(return_value=default_response)

        # Mock async methods if needed
        client.call_api_async = AsyncMock(return_value=default_response)

        return client


class DatabaseMocks:
    """Pre-configured mocks for database operations"""

    @staticmethod
    def mock_supabase_client(
        table_name: str,
        data: Optional[List[Dict[str, Any]]] = None,
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock Supabase client"""
        client = MagicMock()
        table = MagicMock()

        # Mock table operations
        table.insert = MagicMock()
        table.select = MagicMock()
        table.update = MagicMock()
        table.delete = MagicMock()

        # Set up return values
        if raise_error:
            table.insert.side_effect = raise_error
        elif data is not None:
            table.insert.return_value = data
            table.select.return_value = data
            table.update.return_value = data

        client.table = MagicMock(return_value=table)

        return client

    @staticmethod
    def mock_database_query(
        result: Any = None,
        raise_error: Optional[Exception] = None
    ) -> Mock:
        """Create a mock database query result"""
        mock_result = Mock()
        mock_result.fetchone = Mock(return_value=result)
        mock_result.fetchall = Mock(return_value=result if isinstance(result, list) else [result])
        mock_result.execute = Mock()

        if raise_error:
            mock_result.execute.side_effect = raise_error

        return mock_result


class FileSystemMocks:
    """Pre-configured mocks for file system operations"""

    @staticmethod
    def mock_file_read(
        content: str = "test content",
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock for file reading"""
        mock_file = MagicMock()
        mock_file.read = Mock(return_value=content)
        mock_file.readlines = Mock(return_value=content.splitlines())

        if raise_error:
            mock_file.read.side_effect = raise_error

        return mock_file

    @staticmethod
    def mock_file_write(
        success: bool = True,
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock for file writing"""
        mock_file = MagicMock()
        mock_file.write = Mock()
        mock_file.flush = Mock()

        if raise_error:
            mock_file.write.side_effect = raise_error
        elif not success:
            mock_file.write.side_effect = IOError("Write failed")

        return mock_file

    @staticmethod
    def mock_file_exists(
        exists: bool = True,
        is_file: bool = True,
        is_dir: bool = False
    ) -> MagicMock:
        """Create a mock for file existence checks"""
        import os
        mock_path = MagicMock()
        mock_path.exists = Mock(return_value=exists)
        mock_path.is_file = Mock(return_value=is_file and not is_dir)
        mock_path.is_dir = Mock(return_value=is_dir)
        mock_path.stat = Mock(return_value=MagicMock(st_size=1024))

        return mock_path


class RedisMocks:
    """Pre-configured mocks for Redis operations"""

    @staticmethod
    def mock_redis_client(
        data: Optional[Dict[str, Any]] = None,
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock Redis client"""
        client = MagicMock()
        client.get = Mock(return_value=None)
        client.set = Mock(return_value=True)
        client.delete = Mock(return_value=1)
        client.exists = Mock(return_value=False)
        client.expire = Mock(return_value=True)
        client.ttl = Mock(return_value=-1)

        # Set up initial data
        if data:
            for key, value in data.items():
                client.get.return_value = value
                client.get = Mock(side_effect=lambda k, default=None: data.get(k, default))

        if raise_error:
            client.get.side_effect = raise_error

        return client


class WebSocketMocks:
    """Pre-configured mocks for WebSocket operations"""

    @staticmethod
    def mock_websocket_connection(
        messages: Optional[List[Dict[str, Any]]] = None,
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock WebSocket connection"""
        ws = MagicMock()
        ws.send = Mock()
        ws.recv = Mock(return_value=json.dumps(messages[0]) if messages else "{}")
        ws.close = Mock()
        ws.connected = True

        if raise_error:
            ws.recv.side_effect = raise_error
            ws.send.side_effect = raise_error

        return ws

    @staticmethod
    def create_mock_websocket_handler(
        response_message: Optional[str] = None
    ) -> MagicMock:
        """Create a mock WebSocket handler"""
        handler = MagicMock()
        handler.handle_message = AsyncMock(return_value=response_message or "Mock response")
        handler.send_message = Mock()
        handler.close = Mock()

        return handler


class HTTPMocks:
    """Pre-configured mocks for HTTP operations"""

    @staticmethod
    def mock_http_request(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        raise_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock HTTP request response"""
        response = MagicMock()
        response.status_code = status_code
        response.json = Mock(return_value=json_data or {})
        response.text = text or json.dumps(json_data) if json_data else ""
        response.headers = {"Content-Type": "application/json"}
        response.raise_for_status = Mock()

        if raise_error:
            response.raise_for_status.side_effect = raise_error

        return response

    @staticmethod
    def create_mock_http_client(
        responses: Optional[List[MagicMock]] = None
    ) -> MagicMock:
        """Create a mock HTTP client"""
        client = MagicMock()

        if responses:
            response_iter = iter(responses)
            client.request = MagicMock(side_effect=lambda *args, **kwargs: next(response_iter))
        else:
            client.request = MagicMock(return_value=HTTPMocks.mock_http_request())

        return client


class APIMocks:
    """Pre-configured mocks for API operations"""

    @staticmethod
    def mock_external_api(
        endpoint: str,
        response_data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
        raise_error: Optional[Exception] = None
    ) -> Callable:
        """Create a mock for external API calls"""
        def mock_fn(*args, **kwargs):
            if raise_error:
                raise raise_error

            return {
                "endpoint": endpoint,
                "status_code": status_code,
                "data": response_data or {"mock": "data"},
                "args": args,
                "kwargs": kwargs
            }

        return mock_fn


class CircuitBreakerMocks:
    """Pre-configured mocks for circuit breaker operations"""

    @staticmethod
    def mock_circuit_breaker(
        state: str = "closed",
        failure_count: int = 0,
        last_error: Optional[Exception] = None
    ) -> MagicMock:
        """Create a mock circuit breaker"""
        cb = MagicMock()
        cb.state = state
        cb.failure_count = failure_count
        cb.last_error = last_error
        cb.call = MagicMock(return_value={"success": True, "data": "mocked"})
        cb.record_success = MagicMock()
        cb.record_failure = MagicMock()

        if state == "open":
            cb.call.side_effect = Exception("Circuit breaker is open")

        return cb


class RateLimiterMocks:
    """Pre-configured mocks for rate limiter operations"""

    @staticmethod
    def mock_rate_limiter(
        allowed: bool = True,
        remaining: int = 100,
        reset_time: int = 60
    ) -> MagicMock:
        """Create a mock rate limiter"""
        limiter = MagicMock()
        limiter.is_allowed = Mock(return_value=allowed)
        limiter.get_remaining = Mock(return_value=remaining)
        limiter.get_reset_time = Mock(return_value=reset_time)
        limiter.record_request = Mock()

        if not allowed:
            limiter.is_allowed.side_effect = Exception("Rate limit exceeded")

        return limiter


class HealthCheckMocks:
    """Pre-configured mocks for health check operations"""

    @staticmethod
    def mock_health_check(
        status: str = "healthy",
        message: str = "All systems operational",
        response_time: float = 0.1
    ) -> Dict[str, Any]:
        """Create a mock health check response"""
        import time
        return {
            "status": status,
            "message": message,
            "timestamp": time.time(),
            "response_time_ms": response_time * 1000,
            "checks": {
                "database": "ok" if status == "healthy" else "error",
                "cache": "ok" if status == "healthy" else "error",
                "external_apis": "ok" if status == "healthy" else "timeout"
            }
        }


class TestMockContext:
    """Context manager for test mocking with cleanup"""

    def __init__(self, *mocks):
        self.mocks = mocks
        self.original_values = {}

    def __enter__(self):
        for mock_obj, attribute, new_value in self.mocks:
            if hasattr(mock_obj, attribute):
                self.original_values[(mock_obj, attribute)] = getattr(mock_obj, attribute)
                setattr(mock_obj, attribute, new_value)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for (mock_obj, attribute), original_value in self.original_values.items():
            setattr(mock_obj, attribute, original_value)


def create_mock_with_spec(spec_class: type, **kwargs) -> MagicMock:
    """Create a mock that follows the specification of a class"""
    mock = MagicMock(spec=spec_class)

    for key, value in kwargs.items():
        setattr(mock, key, value)

    return mock
