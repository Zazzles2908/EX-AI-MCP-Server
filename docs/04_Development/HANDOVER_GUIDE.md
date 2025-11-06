# Handover Guide - EX-AI MCP Server v2.3

> **Complete Knowledge Transfer for New Developers**
> Created: 2025-11-05
> Version: 2.3.0

---

## Table of Contents

1. [Overview](#overview)
2. [System Status](#system-status)
3. [Critical Files](#critical-files)
4. [Known Issues](#known-issues)
5. [Quick Start](#quick-start)
6. [Development Workflow](#development-workflow)
7. [Testing Guidelines](#testing-guidelines)
8. [Deployment Process](#deployment-process)
9. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
10. [Contact Information](#contact-information)

---

## Overview

The EX-AI MCP Server v2.3 is a production-ready AI model access platform with intelligent routing, multi-provider support, and real-time monitoring. The system implements a thin orchestrator pattern with 86% code reduction through modular architecture.

### Architecture Highlights
- **Thin Orchestrator**: Minimal business logic, maximal delegation
- **Multi-Provider Support**: OpenAI, GLM, Kimi, MiniMax, and extensible
- **WebSocket Real-Time**: Streaming responses and monitoring
- **File Management**: Upload, store, and manage files
- **Circuit Breaker Protection**: Resilient to provider failures
- **Comprehensive Monitoring**: Metrics, logging, and alerting

### Technology Stack
- **Language**: Python 3.13
- **Framework**: aiohttp (async HTTP/WebSocket)
- **Database**: Supabase (PostgreSQL)
- **Cache**: Redis
- **Container**: Docker
- **Monitoring**: Prometheus, custom metrics

---

## System Status

### ✅ OPERATIONAL (with minor issues)

**Current State:**
- Core functionality: **WORKING**
- Multi-provider routing: **WORKING**
- File management: **WORKING**
- WebSocket communication: **WORKING**
- Health monitoring: **WORKING**

**Known Status:**
- System shows "OPERATIONAL WITH DEGRADATION"
- Async to sync fallback active (not a blocker)
- Minor issues exist (see Known Issues)

### Recent Fixes (2025-11-05)

1. **✅ CRITICAL**: ConcurrentSessionManager.execute_sync() - ADDED
2. **✅ CRITICAL**: PyJWT version conflict (zhipuai → zai-sdk) - RESOLVED
3. **✅ CRITICAL**: Dependency conflicts - RESOLVED
4. **✅ Integration Tests**: 7/7 tests passing

### Recent Changes
- Added `execute_sync()` method to ConcurrentSessionManager
- Migrated from zhipuai to zai-sdk for PyJWT compatibility
- Updated pyproject.toml dependencies
- Created comprehensive integration tests

---

## Critical Files

### Core Configuration
- `pyproject.toml` - Python dependencies and project metadata
- `requirements.txt` - Detailed dependency documentation
- `.env.example` - Environment variable template
- `docker-compose.yml` - Docker orchestration

### Source Code Structure
```
src/
├── daemon/                 # Main server daemon
│   ├── ws/                 # WebSocket implementation
│   ├── monitoring_endpoint.py  # Real-time monitoring
│   ├── health_endpoint.py      # Health checks
│   └── multi_user_session_manager.py
├── providers/              # AI provider integrations
│   ├── openai_provider.py  # OpenAI integration
│   ├── glm_provider.py     # GLM integration
│   ├── kimi_chat.py        # Kimi integration
│   └── capability_router.py # Provider selection
├── router/                 # Request routing
│   ├── unified_router.py   # Main routing logic
│   └── service.py          # Routing service
├── storage/                # File storage
│   ├── storage_manager.py  # Unified storage interface
│   └── supabase_client.py  # Supabase integration
├── utils/                  # Utilities
│   ├── concurrent_session_manager.py  # CRITICAL: Session management
│   └── async_concurrent_session_manager.py
└── monitoring/             # Monitoring & metrics
    ├── metrics.py          # Prometheus metrics
    └── broadcaster.py      # Event broadcasting
```

### Documentation
- `docs/01_Core_Architecture/SYSTEM_ARCHITECTURE.md` - Complete architecture
- `docs/02_Reference/API_REFERENCE.md` - API documentation
- `MASTER_TRACKER__SYSTEM_FIXES_2025-11-05.md` - Issue tracker
- `docs/05_CURRENT_WORK/COMPREHENSIVE_FIX_CHECKLIST__2025-11-04.md` - Validation checklist

### Logs
- `logs/docker_latest_2025-11-04.log` - Docker container logs
- `logs/dependency_resolution_2025-11-05.log` - Dependency fix log
- `logs/integration_test_results_2025-11-05.log` - Test results

---

## Known Issues

### 🔴 CRITICAL (High Priority)

#### Issue #1: Hardcoded API URLs
**Location:** Multiple files
**Impact:** Security and maintainability
**Fix Required:** Move to environment variables

**Files to Fix:**
1. `src/daemon/monitoring_endpoint.py:1467` - api.moonshot.ai
2. `src/providers/openai_config.py` - api.openai.com

**How to Fix:**
```python
# Instead of:
base_url = "https://api.moonshot.ai/v1"

# Use:
import os
base_url = os.getenv("MOONSHOT_API_URL", "https://api.moonshot.ai/v1")
```

**Action Items:**
- [ ] Create/update .env.example with all required env vars
- [ ] Update all hardcoded URLs to use env vars
- [ ] Add validation for required env vars
- [ ] Test with environment variable configuration

#### Issue #2: Oversized Files (19 files >500 lines)
**Impact:** Maintainability and readability
**Fix Required:** Refactor into smaller modules

**Top Priority Files:**
1. `src/daemon/monitoring_endpoint.py` (1467 lines)
2. `src/file_management/lifecycle/lifecycle_sync.py` (1131 lines)
3. `src/daemon/ws/ws_server.py` (855 lines)

**How to Refactor:**
- Break into logical modules
- Maintain single responsibility
- Update imports
- Add tests

**Action Items:**
- [ ] Create refactoring plan for each file
- [ ] Break into smaller modules
- [ ] Update all imports
- [ ] Run tests after each refactor

### 🟡 MEDIUM (Medium Priority)

#### Issue #3: Outdated Dependencies
**Count:** 100+ packages have updates
**Impact:** Security and performance
**Fix Required:** Systematic updates

**Examples:**
- mcp: 1.16.0 → 1.20.0
- httpx: 0.27.2 → latest
- supabase: 2.15.3 → 2.23.2

**How to Update:**
```bash
# Check for outdated packages
pip list --outdated

# Update a package
pip install --upgrade package_name

# Test after update
python -m pytest tests/
```

**Action Items:**
- [ ] Create update schedule
- [ ] Test in staging environment
- [ ] Update breaking changes
- [ ] Document changes

### 🟢 LOW (Low Priority)

#### Issue #4: WebSocket Sampling Logging
**Location:** `src/daemon/ws/connection_manager.py:72`
**Current:** Logs every 1000th message (0.1%)
**Status:** May be too verbose in production

**Action Items:**
- [ ] Monitor log volume
- [ ] Adjust sampling rate if needed
- [ ] Document logging configuration

---

## Quick Start

### Prerequisites
- Python 3.13+
- Docker & Docker Compose
- Redis (local or Docker)
- Supabase account
- API keys for providers (OpenAI, GLM, etc.)

### Setup

1. **Clone Repository**
```bash
git clone <repository-url>
cd EX-AI-MCP-Server
```

2. **Create Environment File**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Required Environment Variables**
```bash
# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# OpenAI
OPENAI_API_KEY=your_openai_key

# GLM
GLM_API_KEY=your_glm_key

# Kimi
KIMI_API_KEY=your_kimi_key

# Redis
REDIS_URL=redis://localhost:6379

# Web Server
HOST=0.0.0.0
PORT=8080
```

4. **Install Dependencies**
```bash
pip install -e .
```

5. **Run Tests**
```bash
python -m pytest tests/ -v
```

6. **Start Server**
```bash
python -m src.server
# Or with Docker
docker-compose up -d
```

7. **Verify Health**
```bash
curl http://localhost:8080/health
```

### Verify Installation

**Integration Test:**
```bash
cd src
python -m pytest ../tests/integration/test_dependency_fixes.py -v
```

**Expected Output:**
```
======= 7 passed in 2.92s =======
```

---

## Development Workflow

### Daily Development

1. **Start with Health Check**
```bash
curl http://localhost:8080/health
```

2. **Check Logs**
```bash
docker logs exai-mcp-server
tail -f logs/*.log
```

3. **Run Tests**
```bash
# Quick tests
python -m pytest tests/ -x -v

# Integration tests
python -m pytest tests/integration/ -v
```

### Code Changes

1. **Follow Naming Conventions**
   - Use snake_case for files and functions
   - Use PascalCase for classes
   - Max 500 lines per file

2. **Add Type Hints**
```python
from typing import List, Optional, Dict, Any

def process_request(
    request_id: str,
    messages: List[Dict[str, str]],
    model: str
) -> Dict[str, Any]:
    """Process a chat completion request."""
    pass
```

3. **Add Docstrings**
```python
async def chat_completion(
    messages: List[Message],
    model: str,
    **kwargs
) -> ChatCompletion:
    """
    Create a chat completion.

    Args:
        messages: List of chat messages
        model: Model name or 'auto' for routing
        **kwargs: Additional parameters

    Returns:
        ChatCompletion object with response

    Raises:
        ProviderError: If provider call fails
        ValidationError: If request is invalid
    """
    pass
```

4. **Update Documentation**
   - Add/update docstrings
   - Update API reference if needed
   - Document new endpoints

### Adding a New Provider

1. **Create Provider Class**
```python
class NewProvider(Provider):
    async def chat_completion(
        self,
        messages: List[Message],
        model: str,
        **kwargs
    ) -> ChatCompletion:
        # Implementation
        pass

    def get_capabilities(self) -> Capabilities:
        # Return provider capabilities
        pass
```

2. **Register Provider**
```python
# In provider factory
def get_provider(name: str) -> Provider:
    providers = {
        'openai': OpenAIProvider(),
        'glm': GLMProvider(),
        'new_provider': NewProvider(),
    }
    return providers[name]
```

3. **Add Tests**
```python
def test_new_provider():
    provider = NewProvider()
    result = await provider.chat_completion(...)
    assert result.success
```

4. **Update Documentation**
   - Add to API reference
   - Document capabilities
   - Add integration guide

### Working with WebSocket

**Connection Flow:**
1. Client connects to ws://server/ws
2. Send auth message
3. Send request message
4. Receive streaming responses
5. Close connection

**Example Client:**
```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8080/ws"
    async with websockets.connect(uri) as ws:
        # Authenticate
        await ws.send(json.dumps({
            "type": "auth",
            "token": "your_jwt_token"
        }))

        # Send request
        await ws.send(json.dumps({
            "type": "request",
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello!"}]
        }))

        # Receive response
        async for message in ws:
            data = json.loads(message)
            if data["type"] == "response":
                print(data["content"])
                break

asyncio.run(test_websocket())
```

---

## Testing Guidelines

### Test Structure
```
tests/
├── unit/              # Unit tests
│   ├── test_provider_*.py
│   ├── test_router_*.py
│   └── ...
├── integration/       # Integration tests
│   ├── test_dependency_fixes.py
│   └── test_*.py
└── conftest.py        # Shared fixtures
```

### Running Tests

**All Tests:**
```bash
python -m pytest tests/ -v --cov=src --cov-report=html
```

**Specific Test:**
```bash
python -m pytest tests/unit/test_provider.py::test_chat_completion -v
```

**Integration Tests:**
```bash
python -m pytest tests/integration/ -v
```

**With Coverage:**
```bash
python -m pytest tests/ --cov=src --cov-report=term-missing
```

### Writing Tests

**Unit Test Example:**
```python
import pytest
from src.providers.glm_provider import GLMProvider

@pytest.fixture
def provider():
    return GLMProvider(api_key="test_key")

def test_chat_completion_success(provider):
    """Test successful chat completion."""
    messages = [{"role": "user", "content": "Hello"}]
    result = await provider.chat_completion(messages, "glm-4")
    assert result.success
    assert result.content is not None

def test_chat_completion_failure(provider):
    """Test failure handling."""
    with pytest.raises(ProviderError):
        await provider.chat_completion([], "invalid_model")
```

**Integration Test Example:**
```python
def test_execute_sync_method():
    """Test that execute_sync method exists and works."""
    from src.utils.concurrent_session_manager import ConcurrentSessionManager

    manager = ConcurrentSessionManager()

    def mock_func():
        return "test_result"

    result = manager.execute_sync(
        provider="test",
        func=mock_func
    )

    assert result['completed'] is True
    assert result['result'] == "test_result"
```

### Test Requirements
- Minimum 80% code coverage
- Test all public methods
- Include edge cases
- Mock external dependencies
- Use descriptive test names

---

## Deployment Process

### Docker Deployment

**Build Image:**
```bash
docker build -t exai-mcp-server:2.3.0 .
```

**Run Container:**
```bash
docker run -d \
  --name exai-mcp-server \
  -p 8080:8080 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  exai-mcp-server:2.3.0
```

**With Docker Compose:**
```bash
docker-compose up -d
```

### Environment Variables

**Required:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service key
- `OPENAI_API_KEY` - OpenAI API key
- `GLM_API_KEY` - GLM API key
- `REDIS_URL` - Redis connection string

**Optional:**
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8080)
- `LOG_LEVEL` - Logging level (default: INFO)

### Health Checks

**HTTP Health Check:**
```bash
curl http://localhost:8080/health
```

**Prometheus Metrics:**
```bash
curl http://localhost:8080/metrics
```

**WebSocket Monitoring:**
```bash
# Connect to ws://localhost:8080/ws/monitoring
# Subscribe to real-time metrics
```

### Rolling Updates

**Blue-Green Deployment:**
1. Deploy new version alongside old
2. Run health checks
3. Switch traffic (load balancer)
4. Monitor for errors
5. Stop old version

**Kubernetes:**
```yaml
kubectl set image deployment/exai-mcp-server \
  exai-mcp-server=exai-mcp-server:2.3.1
```

---

## Monitoring & Troubleshooting

### Key Metrics

**Response Time:**
- Target: <200ms (p95)
- Monitor: `exai_request_duration_seconds`

**Throughput:**
- Target: >1000 req/s
- Monitor: `exai_requests_total`

**Error Rate:**
- Target: <0.1%
- Monitor: `exai_errors_total`

**Provider Health:**
- Monitor: `exai_provider_health`
- Alerts on circuit breaker open

### Log Locations

**Application Logs:**
- Docker: `docker logs exai-mcp-server`
- File: `logs/app.log`

**Access Logs:**
- HTTP: `logs/access.log`
- WebSocket: `logs/ws.log`

**Error Logs:**
- `logs/error.log`

### Common Issues

#### Issue: "ConcurrentSessionManager" object has no attribute 'execute_sync'
**Status:** ✅ FIXED (2025-11-05)
**Solution:** Method was added to ConcurrentSessionManager class

#### Issue: ImportError for zhipuai
**Status:** ✅ FIXED (2025-11-05)
**Solution:** Migrated to zai-sdk

#### Issue: Provider not responding
**Diagnosis:** Check circuit breaker status
```bash
curl http://localhost:8080/metrics | grep circuit_breaker
```
**Solution:** Circuit breaker will auto-recover, or check provider API status

#### Issue: High memory usage
**Diagnosis:** Check for memory leaks
```python
# In monitoring endpoint
curl http://localhost:8080/metrics | grep memory
```
**Solution:** Check for unclosed connections, session leaks

#### Issue: Slow response times
**Diagnosis:** Check provider latency
```bash
curl http://localhost:8080/metrics | grep duration
```
**Solution:** Check provider status, consider routing to faster provider

### Debugging

**Enable Debug Logging:**
```bash
export LOG_LEVEL=DEBUG
python -m src.server
```

**Add Custom Logs:**
```python
import logging

logger = logging.getLogger(__name__)

logger.info("Request received", extra={
    "request_id": request_id,
    "provider": provider,
    "model": model
})
```

**Trace Request Flow:**
1. Check access logs for request
2. Check application logs for processing
3. Check provider logs for external call
4. Check metrics for performance

---

## Contact Information

### Development Team
- **Primary:** Development Team Lead
- **EXAI Consultation:** c89df87b-feb3-4dfe-8f8c-38b61b7a7d06

### Documentation
- **System Architecture:** `docs/01_Core_Architecture/SYSTEM_ARCHITECTURE.md`
- **API Reference:** `docs/02_Reference/API_REFERENCE.md`
- **Master Tracker:** `MASTER_TRACKER__SYSTEM_FIXES_2025-11-05.md`
- **Fix Checklist:** `docs/05_CURRENT_WORK/COMPREHENSIVE_FIX_CHECKLIST__2025-11-04.md`

### Support
- **GitHub Issues:** [Repository URL]/issues
- **Documentation:** [Repository URL]/docs
- **Wiki:** [Repository URL]/wiki

---

## Additional Resources

### Architecture Diagrams
[To be added in future update - visual diagrams needed]

### Video Tutorials
[To be created - video walkthrough of key components]

### External Resources
- **aiohttp:** https://docs.aiohttp.org/
- **Supabase:** https://supabase.com/docs
- **WebSockets:** https://websockets.readthedocs.io/
- **Prometheus:** https://prometheus.io/docs/

---

## Appendix

### A. File Size Report
```
Files >500 lines (needs refactoring):
1. src/daemon/monitoring_endpoint.py - 1467 lines
2. src/file_management/lifecycle/lifecycle_sync.py - 1131 lines
3. src/daemon/ws/ws_server.py - 855 lines
4. src/storage/storage_manager.py - 798 lines
5. src/core/config.py - 654 lines
... (19 total)
```

### B. Dependency Status
```
✅ RESOLVED:
- zhipuai → zai-sdk migration
- PyJWT version conflict
- All critical dependencies compatible

⚠️ PENDING:
- 100+ outdated packages need updates
- Security audit of dependencies
```

### C. Test Results
```
Integration Tests: 7/7 PASSED
- test_execute_sync_method_exists ✅
- test_execute_sync_returns_correct_structure ✅
- test_execute_sync_handles_exceptions ✅
- test_zai_sdk_import ✅
- test_pyjwt_version ✅
- test_glm_provider_imports ✅
- test_session_manager_integration ✅
```

---

**Last Updated:** 2025-11-05
**Version:** 2.3.0
**Status:** ✅ PHASE 5.4 COMPLETE
