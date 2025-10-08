# Unit Tests for EX-AI-MCP-Server

**Created:** 2025-10-07  
**Purpose:** Direct unit tests for core provider functionality

---

## Overview

This directory contains **pure unit tests** that test core provider functionality **without** requiring:
- API keys
- Network access
- Running daemon/MCP server
- External services

These tests focus on:
- Provider initialization
- Model configuration
- Context window validation
- Timeout hierarchy
- Base URL configuration
- Model resolution

---

## Test Files

### test_glm_provider.py
**Tests:** GLMModelProvider class

**Coverage:**
- ✅ Provider initialization with API key
- ✅ Base URL configuration (env variable + custom)
- ✅ Model resolution and capabilities
- ✅ Context window validation (glm-4.6: 200K, glm-4.5-flash: 128K, glm-4.5v: 64K)
- ✅ Web search support (native tool calling vs direct API)
- ✅ Payload building
- ✅ Provider type identification
- ✅ GLM-4.5-X alias validation

**Test Classes:**
- `TestGLMProviderInitialization` - Initialization and configuration
- `TestGLMModelResolution` - Model resolution and capabilities
- `TestGLMWebSearchSupport` - Web search capabilities
- `TestGLMPayloadBuilding` - Payload construction
- `TestGLMSDKFallback` - SDK vs HTTP fallback
- `TestGLMProviderType` - Provider type identification
- `TestGLMContextWindows` - Context window validation

---

### test_kimi_provider.py
**Tests:** KimiModelProvider class

**Coverage:**
- ✅ Provider initialization with API key
- ✅ Base URL configuration (env variable + custom)
- ✅ Model resolution and capabilities
- ✅ Context window validation (all models: k2-0905: 256K, k2-0711: 128K, etc.)
- ✅ Context caching functionality
- ✅ OpenAI compatibility
- ✅ Model aliases
- ✅ Image/vision support
- ✅ Function calling support

**Test Classes:**
- `TestKimiProviderInitialization` - Initialization and configuration
- `TestKimiModelResolution` - Model resolution and capabilities
- `TestKimiContextWindows` - Context window validation (8 tests for all models)
- `TestKimiContextCaching` - Cache token storage and retrieval
- `TestKimiProviderType` - Provider type identification
- `TestKimiOpenAICompatibility` - OpenAI compatibility
- `TestKimiModelAliases` - Model alias validation
- `TestKimiImageSupport` - Vision/image support
- `TestKimiFunctionCalling` - Function calling support

---

### test_http_client_timeout.py
**Tests:** HTTP client and timeout configuration

**Coverage:**
- ✅ HTTP client timeout configuration
- ✅ Timeout hierarchy validation (tool < daemon < shim < client)
- ✅ Auto-calculated timeouts (daemon: 1.5x, shim: 2x, client: 2.5x)
- ✅ Environment variable handling
- ✅ Provider-specific timeouts
- ✅ Timeout ratio calculations
- ✅ Documentation validation

**Test Classes:**
- `TestHTTPClientTimeoutConfiguration` - HTTP client timeout
- `TestTimeoutHierarchy` - Timeout hierarchy validation
- `TestTimeoutEnvironmentVariables` - Env variable handling
- `TestProviderTimeouts` - Provider-specific timeouts
- `TestTimeoutRatios` - Ratio calculations
- `TestTimeoutDocumentation` - Documentation validation

---

## Running Tests

### Run All Unit Tests
```bash
python tests/unit/run_unit_tests.py
```

### Run Specific Test Suite
```bash
# GLM provider tests only
python tests/unit/run_unit_tests.py --test glm

# Kimi provider tests only
python tests/unit/run_unit_tests.py --test kimi

# Timeout tests only
python tests/unit/run_unit_tests.py --test timeout
```

### Run with Verbose Output
```bash
python tests/unit/run_unit_tests.py --verbose
```

### Run with pytest directly
```bash
# All unit tests
pytest tests/unit/

# Specific file
pytest tests/unit/test_glm_provider.py

# Specific test class
pytest tests/unit/test_glm_provider.py::TestGLMContextWindows

# Specific test
pytest tests/unit/test_glm_provider.py::TestGLMContextWindows::test_glm_4_6_context_window

# With coverage
pytest tests/unit/ --cov=src/providers --cov-report=term-missing
```

---

## Test Statistics

**Total Test Files:** 3  
**Total Test Classes:** 21  
**Total Test Methods:** 60+

**Coverage:**
- GLMModelProvider: 25+ tests
- KimiModelProvider: 25+ tests
- Timeout Configuration: 15+ tests

---

## Requirements

```bash
pip install pytest
pip install pytest-cov  # Optional, for coverage reports
```

---

## Difference from Integration Tests

| Aspect | Unit Tests (this directory) | Integration Tests (tool_validation_suite) |
|--------|----------------------------|-------------------------------------------|
| **API Keys** | Not required | Required |
| **Network** | Not required | Required |
| **Daemon** | Not required | Required |
| **Speed** | Fast (<1 second) | Slow (minutes) |
| **Focus** | Provider internals | End-to-end workflows |
| **Mocking** | Heavy mocking | Real API calls |

---

## Adding New Tests

When adding new unit tests:

1. **Create test file:** `test_<component>.py`
2. **Organize by class:** Group related tests in test classes
3. **Use descriptive names:** `test_<what>_<expected_behavior>`
4. **No API calls:** Mock external dependencies
5. **Fast execution:** Tests should run in milliseconds
6. **Update README:** Add test file to documentation

---

## Related Documentation

- **Timeout Configuration:** `tool_validation_suite/docs/current/guides/TIMEOUT_CONFIGURATION_GUIDE.md`
- **Model Configuration Audit:** `tool_validation_suite/docs/current/MODEL_CONFIGURATION_AUDIT_2025-10-07.md`
- **Integration Tests:** `tool_validation_suite/README_CURRENT.md`

---

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run Unit Tests
  run: python tests/unit/run_unit_tests.py --verbose
```

---

**Last Updated:** 2025-10-07  
**Maintained By:** EX-AI-MCP-Server Team

