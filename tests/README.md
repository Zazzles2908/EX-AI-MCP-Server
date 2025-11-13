# Testing Guide for EX-AI MCP Server

This guide explains how to use the testing infrastructure for the EX-AI MCP Server project.

## Quick Start

### Running All Tests
```bash
python scripts/run_all_tests.py --type all
```

### Running Tests with Coverage
```bash
python scripts/run_all_tests.py --coverage
```

### Running Tests in Parallel
```bash
python scripts/run_all_tests.py --parallel
```

### Running Specific Test Types
```bash
# Unit tests only (fast)
python scripts/run_all_tests.py --type unit

# Integration tests only
python scripts/run_all_tests.py --type integration

# End-to-end tests only
python scripts/run_all_tests.py --type e2e
```

## Test Categories

### Unit Tests
- **Purpose**: Test individual functions and methods in isolation
- **Speed**: Fast (should complete in seconds)
- **Scope**: Single unit of code
- **Marker**: `@pytest.mark.unit` or automatic if in unit test directory
- **Example**:
  ```python
  @pytest.mark.unit
  def test_provider_initialization():
      provider = GLMProvider(api_key="test", base_url="http://test")
      assert provider.api_key == "test"
  ```

### Integration Tests
- **Purpose**: Test interaction between components
- **Speed**: Medium (may take a minute or two)
- **Scope**: Multiple components working together
- **Marker**: `@pytest.mark.integration`
- **Example**:
  ```python
  @pytest.mark.integration
  def test_provider_database_integration(mock_supabase_client):
      result = provider.save_data(mock_supabase_client)
      assert result["success"] is True
  ```

### End-to-End (E2E) Tests
- **Purpose**: Test complete workflows from start to finish
- **Speed**: Slow (may take several minutes)
- **Scope**: Full system behavior
- **Marker**: `@pytest.mark.e2e`
- **Example**:
  ```python
  @pytest.mark.e2e
  def test_full_chat_workflow(mock_websocket_connection):
      result = chat_handler.handle_message("Hello")
      assert "response" in result
  ```

### Performance Tests
- **Purpose**: Test system performance and scalability
- **Speed**: Variable
- **Marker**: `@pytest.mark.performance`
- **Example**:
  ```python
  @pytest.mark.performance
  def test_response_time():
      start = time.time()
      result = provider.call_api("prompt")
      duration = time.time() - start
      assert duration < 1.0  # Should respond within 1 second
  ```

### Slow Tests
- **Purpose**: Tests that should run infrequently (e.g., external API calls)
- **Speed**: Slow
- **Marker**: `@pytest.mark.slow`
- **Usage**: Run with `--run-slow` flag
- **Example**:
  ```python
  @pytest.mark.slow
  def test_external_api_call():
      # This test makes a real API call, so it's marked as slow
      result = external_service.get_data()
      assert result is not None
  ```

## Test Runner Options

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--type` | Test type to run | `--type unit` |
| `--coverage` | Generate coverage report | `--coverage` |
| `--parallel` | Run tests in parallel | `--parallel` |
| `--output` | Output directory for reports | `--output test-reports` |
| `--verbose` | Enable verbose output | `--verbose` |
| `--fail-fast` | Stop on first failure | `--fail-fast` |
| `--list` | List tests without running | `--list` |
| `--check-coverage` | Check coverage threshold | `--check-coverage` |

### Test Types
- `unit`: Unit tests (default: all non-slow, non-integration tests)
- `integration`: Integration tests
- `e2e`: End-to-end tests
- `all`: All tests

### Examples

```bash
# Run all tests with coverage and parallel execution
python scripts/run_all_tests.py --type all --coverage --parallel

# Run unit tests and check coverage threshold
python scripts/run_all_tests.py --type unit --coverage --check-coverage

# Run tests and generate reports
python scripts/run_all_tests.py --type all --output test-reports

# Run tests with verbose output
python scripts/run_all_tests.py --type all --verbose

# List all tests
python scripts/run_all_tests.py --list
```

## Coverage Requirements

### Minimum Coverage
- **Target**: 80% or higher
- **Current**: See coverage report

### Generating Coverage Reports

1. **Terminal Report** (shows missing lines):
   ```bash
   python scripts/run_all_tests.py --coverage
   ```

2. **HTML Report** (detailed view):
   ```bash
   python scripts/run_all_tests.py --coverage
   open htmlcov/index.html  # macOS
   start htmlcov/index.html  # Windows
   ```

3. **XML Report** (for CI/CD):
   ```bash
   python scripts/run_all_tests.py --coverage
   # Coverage XML generated at: coverage.xml
   ```

### Coverage Configuration

Coverage settings are configured in `pytest.ini`:

```ini
[coverage:run]
source = src
omit =
    */tests/*
    */__pycache__/*
    */venv/*

[coverage:report]
show_missing = true
precision = 2
exclude_lines =
    pragma: no cover
    raise NotImplementedError
```

## Test Fixtures

The test suite provides numerous fixtures in `conftest.py` for easy testing:

### Provider Fixtures

```python
def test_glm_provider(mock_glm_provider):
    # Use pre-configured GLM provider mock
    result = mock_glm_provider.call_api("test prompt")
    assert "choices" in result

def test_kimi_provider(mock_kimi_provider):
    # Use pre-configured Kimi provider mock
    result = mock_kimi_provider.call_api("test prompt")
    assert "choices" in result
```

### Database Fixtures

```python
def test_database_operation(mock_supabase_client):
    # Use pre-configured Supabase client mock
    result = mock_supabase_client.table("test").insert({"data": "test"})
    assert result[0]["id"] == 1
```

### Redis Fixtures

```python
def test_cache_operation(mock_redis_client):
    # Use pre-configured Redis client mock
    mock_redis_client.set("key", "value")
    mock_redis_client.get.assert_called_with("key")
```

### WebSocket Fixtures

```python
def test_websocket(mock_websocket_connection):
    # Use pre-configured WebSocket mock
    mock_websocket_connection.send("test message")
    mock_websocket_connection.send.assert_called_once()
```

### Other Fixtures

| Fixture | Description |
|---------|-------------|
| `test_config` | Test configuration dictionary |
| `sample_user` | Sample user object |
| `sample_file` | Sample file object |
| `mock_http_response` | Mock HTTP response |
| `mock_circuit_breaker` | Mock circuit breaker |
| `mock_rate_limiter` | Mock rate limiter |
| `mock_file_operations` | Mock file operations |
| `mock_metrics_collector` | Mock metrics collector |
| `mock_health_checker` | Mock health checker |
| `temp_dir` | Temporary directory |
| `temp_file` | Temporary file |
| `mock_event_loop` | Event loop for async tests |

## Test Factories

Use test factories to create consistent test data:

### ProviderFactory

```python
from tests.utils.test_factories import ProviderFactory

# Create a GLM provider
glm_provider = ProviderFactory.create_glm_provider(
    api_key="test_key",
    base_url="https://test.com/api"
)

# Create a provider response
response = ProviderFactory.create_provider_response(
    text="Test response",
    success=True
)
```

### FileFactory

```python
from tests.utils.test_factories import FileFactory

# Create a test file
test_file = FileFactory.create_test_file(
    filename="test.txt",
    content="Test content",
    size=1024
)

# Create file metadata
metadata = FileFactory.create_file_metadata(
    filename="test.txt",
    path="/test/path/test.txt"
)
```

### UserFactory

```python
from tests.utils.test_factories import UserFactory

# Create a test user
user = UserFactory.create_user(
    username="testuser",
    email="test@example.com"
)

# Create a user session
session = UserFactory.create_user_session(
    user_id=user["id"]
)
```

### RequestFactory

```python
from tests.utils.test_factories import RequestFactory

# Create a chat request
request = RequestFactory.create_chat_request(
    prompt="Test prompt",
    model="test-model"
)
```

### TestDataGenerator

```python
from tests.utils.test_factories import TestDataGenerator

# Generate multiple test prompts
prompts = TestDataGenerator.generate_prompts(count=10)

# Generate multiple users
users = TestDataGenerator.generate_users(count=5)

# Generate provider responses
responses = TestDataGenerator.generate_provider_responses(count=5)
```

## Mock Utilities

Use mock utilities to simulate external dependencies:

### ProviderMocks

```python
from tests.utils.mocks import ProviderMocks

# Create a mock GLM API response
mock_response = ProviderMocks.mock_glm_api_response(
    response_data={"choices": [{"text": "Test"}]},
    status_code=200
)

# Create a mock provider client
client = ProviderMocks.create_mock_provider_client(
    provider_name="glm",
    responses=[response1, response2]
)
```

### DatabaseMocks

```python
from tests.utils.mocks import DatabaseMocks

# Mock Supabase client
mock_client = DatabaseMocks.mock_supabase_client(
    table_name="test",
    data=[{"id": 1, "name": "test"}]
)
```

### FileSystemMocks

```python
from tests.utils.mocks import FileSystemMocks

# Mock file read
mock_file = FileSystemMocks.mock_file_read(
    content="test content"
)

# Mock file exists check
mock_path = FileSystemMocks.mock_file_exists(
    exists=True,
    is_file=True
)
```

### WebSocketMocks

```python
from tests.utils.mocks import WebSocketMocks

# Mock WebSocket connection
ws = WebSocketMocks.mock_websocket_connection(
    messages=[{"type": "chat", "data": {}}]
)
```

## Best Practices

### 1. Mark Your Tests
Always use appropriate markers for your tests:

```python
@pytest.mark.unit
def test_simple_function():
    pass

@pytest.mark.integration
def test_component_interaction():
    pass

@pytest.mark.e2e
def test_full_workflow():
    pass

@pytest.mark.slow
def test_external_api():
    pass
```

### 2. Use Fixtures
Use existing fixtures instead of creating your own:

```python
# Good
def test_provider(mock_glm_provider):
    result = mock_glm_provider.call_api("prompt")
    assert result is not None

# Bad
def test_provider():
    mock = MagicMock()
    result = mock.call_api("prompt")
    assert result is not None
```

### 3. Use Test Factories
Use test factories for consistent test data:

```python
# Good
user = UserFactory.create_user(username="testuser")

# Bad
user = {"username": "testuser", "email": "test@test.com"}
```

### 4. Mock External Dependencies
Always mock external services (APIs, databases, etc.):

```python
# Good
def test_api_call(mock_http_response):
    result = call_api("http://example.com")
    assert result["status"] == "success"

# Bad
def test_api_call():
    result = call_api("http://example.com")  # Makes real HTTP call!
    assert result["status"] == "success"
```

### 5. Test Edge Cases
Test both happy path and edge cases:

```python
@pytest.mark.unit
def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)

@pytest.mark.unit
def test_divide_success():
    assert divide(10, 2) == 5
```

### 6. Use Descriptive Test Names
Test names should describe what they're testing:

```python
# Good
def test_glm_provider_returns_response_with_valid_api_key():
    pass

# Bad
def test_provider():
    pass
```

### 7. Test One Thing Per Test
Each test should test one specific behavior:

```python
# Good
def test_provider_validates_api_key():
    with pytest.raises(ValueError):
        GLMProvider(api_key="")

def test_provider_makes_api_call():
    result = provider.call_api("prompt")
    assert result is not None

# Bad
def test_provider():
    # Tests multiple things - avoid this
    pass
```

### 8. Clean Up After Tests
Use fixtures and context managers for cleanup:

```python
@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("test")
    return file_path

def test_file_operations(temp_file):
    # File is automatically cleaned up after test
    assert temp_file.exists()
```

## Continuous Integration

Tests are automatically run on:
- Every push to `main`, `develop`, or `phase5-production-validation`
- Every pull request to `main` or `develop`

The CI pipeline:
1. Runs tests on multiple Python versions (3.9, 3.10, 3.11, 3.12, 3.13)
2. Runs on multiple operating systems (Ubuntu, Windows)
3. Generates coverage reports
4. Checks coverage threshold (80%)
5. Uploads coverage to Codecov
6. Runs security scans
7. Generates test reports

## Troubleshooting

### Tests Fail with Import Errors
Make sure you've added the project root to the Python path:
```python
from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
```

### Coverage is Too Low
Run coverage report to see what's missing:
```bash
python scripts/run_all_tests.py --coverage
open htmlcov/index.html  # View detailed report
```

### Tests Run Too Slowly
Run only unit tests for development:
```bash
python scripts/run_all_tests.py --type unit
```

Or run in parallel:
```bash
python scripts/run_all_tests.py --type all --parallel
```

### Environment Variable Issues
The test suite automatically loads `.env.docker` for environment variables. If your tests need specific environment variables, add them to `.env.docker` or use the `reset_environment` fixture.

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage Documentation](https://coverage.readthedocs.io/)
- [Test Fixtures Guide](https://docs.pytest.org/en/latest/fixture.html)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

## Questions?

If you have questions about the testing infrastructure:
1. Check this guide
2. Review the example tests in `tests/examples/`
3. Ask the development team

---

**Happy Testing!** 🧪
