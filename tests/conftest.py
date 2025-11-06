"""
Pytest configuration for EX-AI MCP Server tests

Loads environment variables from .env.docker and provides common test fixtures
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env.docker
def load_env_docker():
    """Load environment variables from .env.docker"""
    env_file = project_root / ".env.docker"
    if not env_file.exists():
        return

    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Remove inline comments
                if '#' in value:
                    value = value.split('#')[0].strip()

                # Set environment variable
                os.environ[key] = value

# Load environment variables before tests run
load_env_docker()


# Pytest fixtures

@pytest.fixture
def mock_glm_provider():
    """Create a mock GLM provider"""
    provider = MagicMock()
    provider.name = "glm"
    provider.api_key = "test_glm_key"
    provider.base_url = "https://test.glm.com/api"
    provider.call_api = MagicMock(return_value={
        "choices": [{"text": "Test GLM response"}],
        "usage": {"total_tokens": 30}
    })
    return provider


@pytest.fixture
def mock_kimi_provider():
    """Create a mock Kimi provider"""
    provider = MagicMock()
    provider.name = "kimi"
    provider.api_key = "test_kimi_key"
    provider.base_url = "https://test.kimi.com/api"
    provider.call_api = MagicMock(return_value={
        "choices": [{"text": "Test Kimi response"}],
        "usage": {"total_tokens": 30}
    })
    return provider


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client"""
    client = MagicMock()
    table = MagicMock()
    table.insert = MagicMock(return_value=[{"id": 1, "data": "test"}])
    table.select = MagicMock(return_value=[{"id": 1, "data": "test"}])
    table.update = MagicMock(return_value=[{"id": 1, "data": "updated"}])
    table.delete = MagicMock(return_value={"success": True})
    client.table = MagicMock(return_value=table)
    return client


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client"""
    client = MagicMock()
    client.get = MagicMock(return_value=None)
    client.set = MagicMock(return_value=True)
    client.delete = MagicMock(return_value=1)
    client.exists = MagicMock(return_value=False)
    client.expire = MagicMock(return_value=True)
    return client


@pytest.fixture
def mock_websocket_connection():
    """Create a mock WebSocket connection"""
    ws = MagicMock()
    ws.send = MagicMock()
    ws.recv = MagicMock(return_value='{"type": "chat", "data": {}}')
    ws.close = MagicMock()
    ws.connected = True
    return ws


@pytest.fixture
def test_config():
    """Create a test configuration dictionary"""
    return {
        "debug": True,
        "log_level": "DEBUG",
        "test_mode": True,
        "redis_url": "redis://localhost:6379/0",
        "supabase_url": "https://test.supabase.co",
        "supabase_key": "test-key",
        "api_timeout": 30
    }


@pytest.fixture
def sample_user():
    """Create a sample user object"""
    return {
        "id": "test-user-123",
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_file():
    """Create a sample file object"""
    return {
        "name": "test.txt",
        "content": "This is a test file",
        "size": 1024,
        "mime_type": "text/plain",
        "id": "file-123"
    }


@pytest.fixture
def mock_http_response():
    """Create a mock HTTP response"""
    response = MagicMock()
    response.status_code = 200
    response.json = MagicMock(return_value={"status": "success", "data": {}})
    response.text = '{"status": "success", "data": {}}'
    response.headers = {"Content-Type": "application/json"}
    return response


@pytest.fixture
def mock_circuit_breaker():
    """Create a mock circuit breaker"""
    cb = MagicMock()
    cb.state = "closed"
    cb.failure_count = 0
    cb.call = MagicMock(return_value={"success": True, "data": "mocked"})
    cb.record_success = MagicMock()
    cb.record_failure = MagicMock()
    return cb


@pytest.fixture
def mock_rate_limiter():
    """Create a mock rate limiter"""
    limiter = MagicMock()
    limiter.is_allowed = MagicMock(return_value=True)
    limiter.get_remaining = MagicMock(return_value=100)
    limiter.get_reset_time = MagicMock(return_value=60)
    limiter.record_request = MagicMock()
    return limiter


@pytest.fixture
def mock_file_operations():
    """Create mock file operations"""
    mock = MagicMock()
    mock.read_file = MagicMock(return_value="test content")
    mock.write_file = MagicMock(return_value=True)
    mock.delete_file = MagicMock(return_value=True)
    mock.file_exists = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_metrics_collector():
    """Create a mock metrics collector"""
    collector = MagicMock()
    collector.record = MagicMock()
    collector.get_metrics = MagicMock(return_value={})
    collector.reset = MagicMock()
    return collector


@pytest.fixture
def mock_health_checker():
    """Create a mock health checker"""
    checker = MagicMock()
    checker.check_health = MagicMock(return_value={
        "status": "healthy",
        "message": "All systems operational",
        "checks": {
            "database": "ok",
            "cache": "ok",
            "external_apis": "ok"
        }
    })
    return checker


@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for tests"""
    return tmp_path


@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file for tests"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test"""
    # Store original values
    original_values = {}
    test_vars = [
        "REDIS_URL",
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "LOG_LEVEL",
        "DEBUG"
    ]

    for var in test_vars:
        if var in os.environ:
            original_values[var] = os.environ[var]

    yield

    # Restore original values
    for var in test_vars:
        if var in original_values:
            os.environ[var] = original_values[var]
        else:
            os.environ.pop(var, None)


@pytest.fixture
def mock_event_loop():
    """Create an event loop for async tests"""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Marker fixtures for test categorization

@pytest.fixture
def unit_test_marker():
    """Mark test as a unit test"""
    return "unit"


@pytest.fixture
def integration_test_marker():
    """Mark test as an integration test"""
    return "integration"


@pytest.fixture
def e2e_test_marker():
    """Mark test as an end-to-end test"""
    return "e2e"


@pytest.fixture
def performance_test_marker():
    """Mark test as a performance test"""
    return "performance"


@pytest.fixture
def slow_test_marker():
    """Mark test as a slow test"""
    return "slow"


# Helper functions for tests

def create_mock_response(status_code: int = 200, data: dict = None):
    """Create a mock HTTP response"""
    response = MagicMock()
    response.status_code = status_code
    response.json = MagicMock(return_value=data or {})
    response.raise_for_status = MagicMock()
    return response


def assert_called_with_async(mock_async_func, *args, **kwargs):
    """Helper to assert an async function was called"""
    mock_async_func.assert_called_once()
    call_args = mock_async_func.call_args
    assert call_args[0] == args
    assert call_args[1] == kwargs


# Global test configuration

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "unit: Mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: Mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: Mark test as an end-to-end test"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "slow: Mark test as a slow test (runs infrequently)"
    )
    config.addinivalue_line(
        "markers", "mcp_protocol: Mark test as MCP protocol compliance test"
    )
    config.addinivalue_line(
        "markers", "routing: Mark test as intelligent routing test"
    )
    config.addinivalue_line(
        "markers", "providers: Mark test as provider integration test"
    )
    config.addinivalue_line(
        "markers", "config: Mark test as configuration and environment test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location"""
    for item in items:
        # Add unit marker to tests in unit test directories
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to tests in integration directories
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add e2e marker to tests in e2e directories
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

