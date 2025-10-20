# Testing Framework

## Purpose & Responsibility

This component provides a comprehensive testing framework for the EXAI MCP Server using pytest and related testing tools, ensuring code quality through unit, integration, and end-to-end tests.

## Pytest Setup

### Configuration

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    external: Tests that require external services
```

### Fixtures

```python
# conftest.py
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_kimi_client():
    client = AsyncMock()
    client.chat.completions.create.return_value = {
        "choices": [{"message": {"content": "Test response"}}]
    }
    return client

@pytest.fixture
def sample_request():
    return {
        "provider": "kimi",
        "model": "kimi-k2-0905-preview",
        "messages": [{"role": "user", "content": "Test message"}],
        "max_tokens": 100
    }

@pytest.fixture
async def mcp_server():
    from src.server import MCPServer
    server = MCPServer(config=test_config)
    await server.start()
    yield server
    await server.stop()
```

## Test Types

### Unit Tests

```python
# tests/unit/test_protocol_handler.py
import pytest
from src.mcp.protocol_handler import MCPProtocolHandler

class TestMCPProtocolHandler:
    def test_validate_request_valid(self, sample_request):
        handler = MCPProtocolHandler(config=test_config)
        # Should not raise exception
        handler._validate_request(sample_request)
    
    def test_validate_request_missing_provider(self, sample_request):
        handler = MCPProtocolHandler(config=test_config)
        del sample_request["provider"]
        with pytest.raises(ValidationError):
            handler._validate_request(sample_request)
    
    @pytest.mark.asyncio
    async def test_handle_request_success(self, mock_kimi_client, sample_request):
        handler = MCPProtocolHandler(config=test_config)
        handler.connections["kimi"] = mock_kimi_client
        
        response = await handler.handle_request(sample_request)
        
        assert response.status == "success"
        assert "content" in response.data
```

### Integration Tests

```python
# tests/integration/test_provider_integration.py
import pytest
from src.providers import KimiProvider

@pytest.mark.integration
class TestProviderIntegration:
    @pytest.mark.asyncio
    async def test_kimi_provider_request(self):
        provider = KimiProvider(api_key=os.getenv("KIMI_API_KEY"))
        request = {
            "model": "kimi-k2-0905-preview",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 10
        }
        
        response = await provider.execute(request)
        
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]
    
    @pytest.mark.asyncio
    async def test_connection_pool(self):
        from src.mcp.connection_pool import ConnectionPool
        
        pool = ConnectionPool(provider="kimi", pool_size=2)
        connection1 = await pool.get_connection()
        connection2 = await pool.get_connection()
        
        assert connection1 is not connection2
        
        # Release connections
        await pool.release_connection(connection1)
        await pool.release_connection(connection2)
```

### End-to-End Tests

```python
# tests/e2e/test_api_endpoints.py
import pytest
from fastapi.testclient import TestClient
from src.main import app

@pytest.mark.e2e
class TestAPIEndpoints:
    def test_health_endpoint(self):
        client = TestClient(app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_chat_endpoint(self):
        client = TestClient(app)
        request_data = {
            "provider": "kimi",
            "model": "kimi-k2-0905-preview",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        response = client.post("/chat", json=request_data)
        assert response.status_code == 200
        assert "response" in response.json()
```

## Coverage Requirements

### Configuration

```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*
    */migrations/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

### Coverage Enforcement

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
```

### Quality Gates

```python
# tests/test_coverage.py
import pytest
import coverage

def test_coverage_threshold():
    cov = coverage.Coverage()
    cov.load()
    total = cov.report()
    
    # Enforce minimum coverage
    assert total >= 80, f"Coverage {total}% is below required 80%"
```

## Test Organization

### Directory Structure

```
tests/
├── unit/           # Fast, isolated tests
│   ├── test_protocol.py
│   ├── test_handlers.py
│   └── test_utils.py
├── integration/    # Service integration tests
│   ├── test_providers.py
│   ├── test_database.py
│   └── test_cache.py
├── e2e/           # Full application tests
│   ├── test_api.py
│   └── test_workflows.py
└── fixtures/      # Test data
    ├── requests.json
    └── responses.json
```

### Test Running

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m e2e          # End-to-end tests only

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_protocol.py

# Run with verbose output
pytest -v
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use fixtures for setup/teardown
   - Mock external dependencies

2. **Test Naming**
   - Use descriptive test names
   - Follow pattern: `test_<what>_<condition>_<expected>`
   - Example: `test_validate_request_missing_provider_raises_error`

3. **Assertions**
   - Use specific assertions
   - Test one thing per test
   - Include helpful error messages

4. **Performance**
   - Keep unit tests fast (< 1s each)
   - Mark slow tests with `@pytest.mark.slow`
   - Use parallel execution for large test suites

5. **Maintenance**
   - Keep tests simple and readable
   - Avoid test duplication
   - Update tests when code changes

## Integration Points

- **CI/CD Pipeline**: Automated test execution on commits
- **Code Coverage**: Tracks test coverage metrics
- **Quality Gates**: Enforces minimum coverage thresholds
- **Monitoring**: Reports test failures and trends

