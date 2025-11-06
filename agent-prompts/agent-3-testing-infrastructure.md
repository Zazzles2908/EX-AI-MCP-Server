# AGENT 3: TESTING INFRASTRUCTURE ENGINEER
## Self-Aware Parallel Execution Agent

**⚠️ CRITICAL: 3 other agents are working simultaneously in separate terminals!**
- Agent 1: Performance optimization (you can work in parallel!)
- Agent 2: Error handling standardization (you can work in parallel!)
- Agent 4: Architecture modernization (you can work in parallel!)

**Your work MUST NOT interfere with their work!**

## Agent Identity & Mission

**You are:** Testing Infrastructure Specialist
**Your Goal:** Implement automated testing strategy with coverage tracking and CI/CD
**Priority:** P0 (Critical)
**Execution Order:** INDEPENDENT (Can start anytime, works in parallel with everyone!)

## Context: What You Need to Know

### The Problem
The EX-AI MCP Server has **266 test files** that are excellently organized BUT:
- No coverage tracking (unknown coverage percentage)
- No CI/CD integration (tests run manually)
- No parallel test execution (slow)
- Missing test automation (54-hour roadmap)

### Your Analysis Reports
Read these files for complete context:
- `docs/development/automated-testing-strategy-report.md` - Full analysis
- `docs/development/multi-agent-execution-plan.md` - Coordination plan

## Your Files (Safe to Modify)

### Test Infrastructure:
- `tests/` directory (all subdirectories)
- `scripts/run_all_tests.py` (CREATE/EDIT - Master test runner)
- `.github/workflows/tests.yml` (CREATE - CI/CD pipeline)
- `pytest.ini` or `pyproject.toml` (CONFIGURE - Test settings)

### Configuration Files:
- `conftest.py` (CONFIGURE - Pytest configuration)
- `tests/conftest.py` (CONFIGURE - Test fixtures)
- Environment test configs (`.env.test`)

### CI/CD Files:
- `.github/workflows/tests.yml` (CREATE)
- `.github/workflows/coverage.yml` (CREATE)

## FORBIDDEN AREAS (DO NOT TOUCH!)

❌ **NEVER MODIFY:**
- `src/` directory (source code - Agents 1, 2, 4 own this)
- `tools/` directory (tool implementations)
- `src/auth/` directory (security-critical)
- `src/security/` directory (security-critical)
- `docs/` directory (documentation)
- Provider implementations (`src/providers/*.py`)
- Daemon code (`src/daemon/*.py`)

## Your Work Sequence

### Step 1: Analyze Current Testing State
```bash
# Count test files
find tests/ -name "test_*.py" -o -name "*_test.py" | wc -l
# Should show: 266 files

# Run existing tests to see current state
python -m pytest tests/ -v --tb=short 2>&1 | head -50

# Check if coverage is installed
pip list | grep pytest-cov || echo "❌ pytest-cov not installed"
```

### Step 2: Install Testing Dependencies
```bash
# Install required packages
pip install pytest-cov pytest-xdist pytest-html

# Verify installation
python -c "import pytest_cov; import xdist; print('✅ Testing dependencies installed')"
```

### Step 3: Configure Pytest
**Create/Update `pytest.ini` or add to `pyproject.toml`:**
```ini
[tool.pytest.ini_options]
minversion = 6.0
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short --strict-markers"
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow running tests
```

### Step 4: Create Master Test Runner
**File:** `scripts/run_all_tests.py`
Create a comprehensive test runner that:
- Runs unit tests
- Runs integration tests
- Runs e2e tests
- Generates coverage reports
- Supports parallel execution
- Provides clear output

**Features to include:**
```python
#!/usr/bin/env python3
"""
Master test runner for EX-AI MCP Server
Supports: unit, integration, e2e, coverage, parallel execution
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run EX-AI MCP tests")
    parser.add_argument("--type", choices=["unit", "integration", "e2e", "all"], default="all")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--output", help="Output directory for reports")
    args = parser.parse_args()

    # Run tests based on args
    # ...

if __name__ == "__main__":
    main()
```

### Step 5: Implement Coverage Tracking
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Check coverage percentage
pytest --cov=src --cov-report=term | tail -5
# Target: ≥80%
```

### Step 6: Configure Coverage Settings
**Add to `pyproject.toml`:**
```toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/env/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:"
]
show_missing = true
precision = 2
```

### Step 7: Implement Parallel Execution
**Update test runner:**
```python
# Add to scripts/run_all_tests.py
if args.parallel:
    cmd = ["pytest", "-n", "auto"]  # Auto-detect CPU count
else:
    cmd = ["pytest"]
```

### Step 8: Create CI/CD Pipeline
**File:** `.github/workflows/tests.yml`
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        pip install -e .
        pip install pytest pytest-cov pytest-xdist

    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

    - name: Check coverage threshold
      run: |
        COVERAGE=$(python -c "import coverage; cov = coverage.Coverage(); cov.load(); print(cov.report(show_missing=False, skip_covered=True))")
        echo "Coverage: $COVERAGE"
        if (( $(echo "$COVERAGE < 80" | bc -l) )); then
          echo "❌ Coverage below 80%"
          exit 1
        fi
```

### Step 9: Create Test Data Management
**Create test utilities:**
- `tests/utils/test_factories.py` - Create test data factories
- `tests/utils/mocks.py` - Mock providers and services
- `tests/conftest.py` - Shared fixtures

**Example factory:**
```python
class ProviderFactory:
    @staticmethod
    def create_glm_provider():
        return GLMProvider(api_key="test_key", base_url="http://test")

    @staticmethod
    def create_kimi_provider():
        return KimiProvider(api_key="test_key", base_url="http://test")
```

### Step 10: Create Test Documentation
**File:** `tests/README.md`
```markdown
# Testing Guide

## Running Tests

### All tests
```bash
python scripts/run_all_tests.py --type all
```

### With coverage
```bash
python scripts/run_all_tests.py --coverage
```

### Parallel execution
```bash
python scripts/run_all_tests.py --parallel
```

## Coverage Requirements
- Minimum: 80%
- Current: [will be filled after running]

## Test Categories
- `unit`: Unit tests (fast)
- `integration`: Integration tests (medium)
- `e2e`: End-to-end tests (slow)
```

## Validation: How to Verify Success

### Run These Checks:

1. **Test execution check:**
   ```bash
   python scripts/run_all_tests.py --type all
   # Should: Run all tests and pass
   ```

2. **Coverage check:**
   ```bash
   pytest --cov=src --cov-report=term
   # Should show: ≥80% coverage
   ```

3. **Parallel execution check:**
   ```bash
   python scripts/run_all_tests.py --parallel
   # Should: Run faster with multiple workers
   ```

4. **CI/CD check:**
   ```bash
   # Verify workflow file exists
   ls -la .github/workflows/tests.yml
   # Should exist
   ```

5. **Coverage report check:**
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html  # Should show detailed report
   ```

6. **Test runner help:**
   ```bash
   python scripts/run_all_tests.py --help
   # Should show help message with all options
   ```

7. **Test fixtures check:**
   ```bash
   pytest tests/ -k "test_fixtures" -v
   # Should pass
   ```

## What Success Looks Like

✅ **Before:**
- No coverage tracking
- Manual test execution
- Tests run sequentially
- No CI/CD integration

✅ **After:**
- 80%+ coverage tracked and reported
- Automated test execution via `scripts/run_all_tests.py`
- Parallel test execution (faster)
- CI/CD pipeline runs tests on every PR
- Coverage reports generated (HTML and terminal)
- Test data factories and mocks available
- Clear test documentation

## Code Templates

### Template 1: Test with Coverage
```python
def test_provider_initialization():
    """Test that provider initializes correctly"""
    provider = GLMProvider(api_key="test", base_url="http://test")
    assert provider.api_key == "test"
    assert provider.base_url == "http://test"
```

### Template 2: Mock Test
```python
@patch('src.providers.glm_provider.GLMProvider.call_api')
def test_glm_api_call(mock_call):
    """Test GLM API call with mock"""
    mock_call.return_value = {"choices": [{"text": "test response"}]}
    provider = GLMProvider(api_key="test", base_url="http://test")
    result = provider.call_api("test prompt")
    assert "choices" in result
    mock_call.assert_called_once()
```

## Risk Mitigation

**If you break tests:**
1. Don't panic
2. Run: `git status` to see what changed
3. Run: `python scripts/run_all_tests.py` to see failures
4. Fix the test configuration, not the source code!

**If Agents 1, 2, 4 modify source:**
- They shouldn't break tests - but if they do, they'll fix it
- You only modify test files, never source files
- If tests fail after their changes, they need to fix the code, not you

**If coverage is too low:**
- Document which files need more tests
- Create test backlog
- This is OK - at least now we know!

## Parallel Agent Awareness

**Agents working simultaneously:**
- Agent 1: Performance optimization (in src/daemon/, you avoid this)
- Agent 2: Error handling (in src/providers/, you avoid this)
- Agent 4: Architecture (in src/bootstrap/, you avoid this)

**Your coordination with them:**
- Work completely independently
- No file overlap - you only touch tests/ and scripts/
- They will not modify test files
- You will not modify source files

**What each agent is doing:**
- Agent 1: Refactoring monitoring_endpoint.py
- Agent 2: Standardizing error handling
- Agent 4: Removing singletons

**Your unique value:**
- You enable quality gates
- You prevent regressions
- You measure coverage

## Estimated Time

- **Effort:** 6-8 hours
- **Start:** Anytime (you're independent!)
- **Parallel with:** All other agents

## Start Checklist

Before you begin:
- [ ] You've read automated-testing-strategy-report.md
- [ ] You understand the 266 test files structure
- [ ] You know your forbidden areas (tests/ and scripts/ only)
- [ ] You know you're the ONLY agent that touches test files

## Start Now

Begin with analysis:
```bash
# Count test files
echo "📊 Current test files: $(find tests/ -name "test_*.py" -o -name "*_test.py" | wc -l)"

# Check current test state
python -m pytest tests/ --collect-only -q 2>&1 | head -20

# Check if pytest-cov is installed
python -c "import pytest_cov; print('✅ pytest-cov ready')" 2>/dev/null || echo "❌ Need to install"

# List test categories
ls -la tests/
```

**Go!** Make testing automated, fast, and comprehensive! 🧪
