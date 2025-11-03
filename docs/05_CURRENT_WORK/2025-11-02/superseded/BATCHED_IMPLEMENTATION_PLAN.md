# Batched Implementation Plan - File Upload System Overhaul
**Date:** 2025-11-02  
**EXAI Continuation ID:** 2990f86f-4ce1-457d-9398-516d599e5902  
**Model:** glm-4.6  
**Starting Batch:** 4  
**Total Batches:** 8

---

## Batch Overview

| Batch | Focus | Priority | Duration | Tasks |
|-------|-------|----------|----------|-------|
| Batch 4 | Critical Security Fixes | CRITICAL | 2 days | 3 |
| Batch 5 | Architecture Consolidation | HIGH | 2 days | 2 |
| Batch 6 | Enhanced Reliability | HIGH | 2 days | 2 |
| Batch 7 | Configuration Optimization | MEDIUM | 1 day | 1 |
| Batch 8 | Advanced Features | LOW | 2 days | 2 |

**Total Timeline:** 9 days, 10 tasks

---

## Batch 4: Critical Security Fixes (2 days)
**Priority:** CRITICAL - Addresses immediate security vulnerabilities

### Task 4.1: Enable Supabase File Tracking
**Files:** `.env.docker`, `src/providers/kimi_files.py`

**Changes:**
```bash
# .env.docker
KIMI_UPLOAD_TO_SUPABASE=true  # Changed from false
```

**Actions:**
1. Update environment variable
2. Test file upload with Supabase tracking
3. Verify bidirectional sync between `files` and `provider_file_uploads` tables
4. Monitor for service key authentication issues

**Acceptance Criteria:**
- Upload test file appears in both Supabase tables
- Provider file ID correctly mapped to Supabase file ID
- No authentication errors in logs

**Rollback:** Set `KIMI_UPLOAD_TO_SUPABASE=false`

---

### Task 4.2: Fix Path Traversal Vulnerability
**Files:** `src/security/path_validator.py` (new), `src/core/env_config.py`

**Changes:**
```python
# src/security/path_validator.py (new)
from pathlib import Path
from typing import List

class PathValidator:
    def __init__(self, allowed_prefixes: List[str]):
        self.allowed_prefixes = [Path(p).resolve() for p in allowed_prefixes]
    
    def is_allowed(self, file_path: str) -> bool:
        path = Path(file_path).resolve()
        return any(
            str(path).startswith(str(prefix))
            for prefix in self.allowed_prefixes
        )

# Update .env.docker
EX_ALLOW_EXTERNAL_PATHS=false
EX_ALLOWED_EXTERNAL_PREFIXES=/app,/mnt/project
```

**Actions:**
1. Create path validator with strict allowlist
2. Integrate into all file upload functions
3. Update environment to disable external paths
4. Test with various path traversal attempts

**Acceptance Criteria:**
- Allowed paths (`/app`, `/mnt/project`) work
- Disallowed paths rejected with security error
- Path traversal attempts blocked

**Rollback:** Revert to `EX_ALLOW_EXTERNAL_PATHS=true`

---

### Task 4.3: Implement JWT Authentication
**Files:** `src/auth/jwt_validator.py` (new), `server.py`

**Changes:**
```python
# src/auth/jwt_validator.py (new)
import jwt
from typing import Optional, Dict

class JWTValidator:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def validate_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.InvalidTokenError:
            return None

# server.py - Add to WebSocket handler
from src.auth.jwt_validator import JWTValidator

validator = JWTValidator(os.getenv("JWT_SECRET_KEY"))

async def handle_connection(websocket):
    token = websocket.request_headers.get("Authorization", "").replace("Bearer ", "")
    user = validator.validate_token(token)
    
    if not user:
        await websocket.close(1008, "Unauthorized")
        return
```

**Actions:**
1. Create JWT validator
2. Add authentication to WebSocket handler
3. Add `JWT_SECRET_KEY` to environment
4. Implement 2-week grace period accepting both auth methods

**Acceptance Criteria:**
- Valid JWT tokens accepted
- Invalid/missing tokens rejected
- Grace period allows both methods

**Rollback:** Disable JWT validation temporarily

---

## Batch 5: Architecture Consolidation (2 days)
**Priority:** HIGH - Reduces code duplication and improves maintainability

### Task 5.1: Create Unified File Manager
**Files:** `src/storage/unified_file_manager.py` (new), update all upload tools

**Changes:**
```python
# src/storage/unified_file_manager.py (new)
from typing import Optional, Dict
from src.providers.glm_files import GLMFileProvider
from src.providers.kimi_files import KimiFileProvider

class UnifiedFileManager:
    def __init__(self):
        self.providers = {
            "glm": GLMFileProvider(),
            "kimi": KimiFileProvider()
        }
    
    async def upload_file(
        self,
        file_path: str,
        provider: str = "auto",
        purpose: str = "assistants"
    ) -> Dict:
        # Auto-select provider based on file size
        if provider == "auto":
            file_size = os.path.getsize(file_path)
            provider = "glm" if file_size > 512*1024*1024 else "kimi"
        
        # Upload to provider
        result = await self.providers[provider].upload(file_path, purpose)
        
        # Track in Supabase
        await self.track_upload(result, provider)
        
        return result
```

**Actions:**
1. Create unified manager with auto-provider selection
2. Migrate `smart_file_query.py` to use unified interface
3. Implement provider selection logic (GLM for >512MB, Kimi for smaller)
4. Add comprehensive Supabase tracking

**Acceptance Criteria:**
- All existing tests pass with new interface
- Provider selection works correctly
- Supabase tracking functional

**Rollback:** Keep old code behind feature flag

---

### Task 5.2: Consolidate Provider Code
**Files:** `src/providers/file_base.py`, `src/providers/glm_files.py`, `src/providers/kimi_files.py`

**Changes:**
1. Extract common upload logic to `file_base.py`
2. Implement abstract methods in both providers
3. Remove 70% duplicate code
4. Standardize error handling

**Actions:**
1. Identify common code patterns
2. Move to base class implementation
3. Update providers to inherit and override
4. Remove duplicate functions

**Acceptance Criteria:**
- Unit tests for each provider pass
- Integration tests maintain functionality
- Code coverage maintained >80%

**Rollback:** Keep duplicate code commented out temporarily

---

## Batch 6: Enhanced Reliability (2 days)
**Priority:** HIGH - Improves upload success rate and system stability

### Task 6.1: Implement Retry Logic
**Files:** `src/providers/retry_handler.py` (new), update provider implementations

**Changes:**
```python
# src/providers/retry_handler.py (new)
import asyncio
import random
from typing import Callable, Any

class RetryHandler:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def retry_with_backoff(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if not self.is_retryable(e):
                    raise
                
                if attempt == self.max_retries - 1:
                    raise
                
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
    
    def is_retryable(self, error: Exception) -> bool:
        retryable_codes = [429, 500, 502, 503, 504]
        return hasattr(error, 'status_code') and error.status_code in retryable_codes
```

**Actions:**
1. Create retry handler with exponential backoff
2. Add to all upload functions
3. Configure retryable error codes
4. Test with simulated failures

**Acceptance Criteria:**
- Network errors trigger retries
- Auth errors do not retry
- Rate limits handled with backoff

**Rollback:** Disable retry logic temporarily

---

### Task 6.2: Implement Automatic Cleanup
**Files:** `src/storage/file_cleanup.py` (new), `server.py`

**Changes:**
```python
# src/storage/file_cleanup.py (new)
import asyncio
from datetime import datetime, timedelta
from src.storage.supabase_client import get_supabase_client

class FileCleanupService:
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.client = get_supabase_client()
    
    async def cleanup_old_files(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        result = self.client.table("files").select("*").lt("created_at", cutoff).execute()
        
        for file in result.data:
            await self.delete_from_provider(file)
            self.client.table("files").delete().eq("id", file["id"]).execute()
    
    async def run_periodic_cleanup(self):
        while True:
            await self.cleanup_old_files()
            await asyncio.sleep(86400)  # Daily

# server.py - Add to startup
cleanup_service = FileCleanupService(retention_days=30)
asyncio.create_task(cleanup_service.run_periodic_cleanup())
```

**Actions:**
1. Create cleanup service with configurable retention
2. Add to server startup
3. Test with old test files
4. Monitor cleanup cycles

**Acceptance Criteria:**
- Old files automatically deleted
- Provider and Supabase records cleaned
- No storage leaks

**Rollback:** Stop cleanup service temporarily

---

## Batch 7: Configuration Optimization (1 day)
**Priority:** MEDIUM - Reduces complexity and improves maintainability

### Task 7.1: Consolidate Configuration
**Files:** `.env.docker`, create `.env.dev`, `.env.prod`

**Changes:**
1. Reduce from 738 to <200 lines
2. Remove duplicate provider configs
3. Separate dev/prod configurations
4. Centralize timeout settings

**Actions:**
1. Audit all environment variables
2. Identify duplicates and redundancies
3. Create environment-specific files
4. Update configuration loading

**Acceptance Criteria:**
- All features work with reduced config
- Dev/prod configs correct
- No missing variables

**Rollback:** Keep original .env.docker as backup

---

## Batch 8: Advanced Features (2 days)
**Priority:** LOW - Nice-to-have features for production readiness

### Task 8.1: Add Comprehensive Monitoring
**Files:** `src/monitoring/file_upload_metrics.py` (new), update providers

**Changes:**
```python
# src/monitoring/file_upload_metrics.py (new)
from prometheus_client import Counter, Histogram, Gauge

upload_total = Counter('file_upload_total', 'Total file uploads', ['provider', 'status'])
upload_duration = Histogram('file_upload_duration_seconds', 'Upload duration', ['provider'])
upload_size = Histogram('file_upload_size_bytes', 'Upload size', ['provider'])
storage_usage = Gauge('storage_usage_bytes', 'Total storage usage')

class FileUploadMetrics:
    @staticmethod
    def record_upload(provider: str, duration: float, size: int, success: bool):
        status = 'success' if success else 'failure'
        upload_total.labels(provider=provider, status=status).inc()
        upload_duration.labels(provider=provider).observe(duration)
        upload_size.labels(provider=provider).observe(size)
```

**Actions:**
1. Create metrics collector
2. Add to all upload functions
3. Integrate with Prometheus
4. Update monitoring dashboard

**Acceptance Criteria:**
- Metrics appear in Prometheus
- Dashboard shows upload stats
- Alerts configured for failures

**Rollback:** Disable metrics collection

---

### Task 8.2: Remove Dead Code
**Files:** Delete unused files and functions

**Changes:**
1. Delete `tools/async_file_upload_refactored.py`
2. Delete `tools/file_upload_optimizer.py`
3. Remove unused functions from `file_base.py`
4. Update documentation

**Actions:**
1. Verify files are unused
2. Check for imports
3. Delete files
4. Update references

**Acceptance Criteria:**
- No import errors
- All tests pass
- System functions normally

**Rollback:** Restore from git if needed

---

## Success Metrics

- **Security:** All vulnerabilities patched
- **Reliability:** 99%+ upload success rate
- **Performance:** <5s average upload time
- **Maintainability:** <200 lines config, 70% code reduction
- **Monitoring:** Full observability with metrics


