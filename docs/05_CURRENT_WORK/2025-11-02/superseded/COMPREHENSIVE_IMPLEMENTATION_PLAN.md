# Comprehensive Implementation Plan - File Upload System Overhaul
**Date:** 2025-11-02  
**Based on:** EXAI Phase 1 & 2 Analysis  
**Timeline:** 6 weeks  
**Priority:** Critical system improvements

---

## Executive Summary

This implementation plan addresses ALL critical issues identified in the file upload system analysis:
- **Security gaps** (authentication, path traversal)
- **Configuration bloat** (738 → <200 lines)
- **Dead code** (remove unused tools)
- **Provider fragmentation** (70% duplicate code)
- **Missing features** (retry logic, monitoring, cleanup)

**Total Effort:** 6 weeks, 4 phases, 25 tasks

---

## Phase 0: Preparation (Week 0 - 3 days)

### 0.1 System Backup
**Priority:** CRITICAL  
**Files:** All  
**Actions:**
1. Create git branch: `feat/file-upload-overhaul`
2. Tag current state: `v-pre-file-upload-overhaul`
3. Backup Supabase database
4. Document current behavior

**Validation:**
- Git tag created
- Branch created
- Backup verified

**Risk:** None  
**Effort:** 2 hours

### 0.2 Create Test Suite
**Priority:** CRITICAL  
**Files:** Create `tests/file_upload/`  
**Actions:**
1. Create baseline tests for current behavior
2. Test file upload (GLM, Kimi)
3. Test file download
4. Test file cleanup
5. Test error handling

**Validation:**
- All tests pass with current code
- Test coverage >80%

**Risk:** None  
**Effort:** 1 day

### 0.3 Set Up Monitoring Baseline
**Priority:** HIGH  
**Files:** Monitoring dashboard  
**Actions:**
1. Document current metrics
2. Capture baseline performance
3. Note current error rates

**Validation:**
- Baseline documented
- Metrics captured

**Risk:** None  
**Effort:** 4 hours

---

## Phase 1: Critical Fixes (Week 1 - 5 days)

### 1.1 Enable Supabase File Tracking
**Priority:** CRITICAL  
**Files:** `.env.docker`, `src/providers/kimi_files.py`  
**Changes:**
```bash
# .env.docker
KIMI_UPLOAD_TO_SUPABASE=true  # Changed from false
```

**Actions:**
1. Change environment variable
2. Test file upload
3. Verify file appears in Supabase `files` table
4. Verify `provider_file_uploads` table updated

**Validation:**
- Upload test file
- Check Supabase tables
- Verify bidirectional sync

**Risk:** MEDIUM - May expose service key issue  
**Mitigation:** Monitor logs for auth errors  
**Rollback:** Set back to `false`  
**Effort:** 2 hours

### 1.2 Fix Path Mapping
**Priority:** CRITICAL  
**Files:** `.env.docker`  
**Changes:**
```bash
# .env.docker
EX_DRIVE_MAPPINGS=C:/mnt/project  # Changed from C:/app
```

**Actions:**
1. Update path mapping
2. Restart container
3. Test file upload from Windows path

**Validation:**
- Upload file from `c:\Project\`
- Verify container sees `/mnt/project/`

**Risk:** LOW  
**Rollback:** Revert mapping  
**Effort:** 1 hour

### 1.3 Implement Authentication (JWT)
**Priority:** CRITICAL  
**Files:** Create `src/auth/jwt_validator.py`, modify `server.py`  
**Changes:**
```python
# src/auth/jwt_validator.py
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
    # Extract token from headers
    token = websocket.request_headers.get("Authorization", "").replace("Bearer ", "")
    user = validator.validate_token(token)
    
    if not user:
        await websocket.close(1008, "Unauthorized")
        return
    
    # Continue with authenticated user
```

**Actions:**
1. Create JWT validator
2. Add to WebSocket handler
3. Add `JWT_SECRET_KEY` to `.env.docker`
4. Update client to send JWT

**Validation:**
- Test with valid JWT → success
- Test with invalid JWT → rejected
- Test without JWT → rejected

**Risk:** HIGH - Breaks existing clients  
**Mitigation:** Implement grace period (accept both auth/no-auth)  
**Breaking Change:** YES - requires client updates  
**Migration:** Provide JWT generation script  
**Effort:** 1 day

### 1.4 Fix Path Traversal Vulnerability
**Priority:** CRITICAL  
**Files:** `src/core/env_config.py`, create `src/security/path_validator.py`  
**Changes:**
```python
# src/security/path_validator.py
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

# Usage in file upload tools
validator = PathValidator(["/app", "/mnt/project"])
if not validator.is_allowed(file_path):
    raise SecurityError("Path not allowed")
```

**Actions:**
1. Create path validator
2. Add to all file upload functions
3. Update `.env.docker` with strict allowlist
4. Test with various paths

**Validation:**
- Test allowed paths → success
- Test disallowed paths → rejected
- Test path traversal attempts → rejected

**Risk:** MEDIUM - May break legitimate use cases  
**Mitigation:** Comprehensive allowlist  
**Effort:** 4 hours

### 1.5 Implement Automatic Cleanup
**Priority:** CRITICAL  
**Files:** Create `src/storage/file_cleanup.py`, modify `server.py`  
**Changes:**
```python
# src/storage/file_cleanup.py
import asyncio
from datetime import datetime, timedelta
from src.storage.supabase_client import get_supabase_client

class FileCleanupService:
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.client = get_supabase_client()
    
    async def cleanup_old_files(self):
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        # Query old files
        result = self.client.table("files").select("*").lt("created_at", cutoff).execute()
        
        for file in result.data:
            # Delete from provider
            await self.delete_from_provider(file)
            # Delete from Supabase
            self.client.table("files").delete().eq("id", file["id"]).execute()
    
    async def run_periodic_cleanup(self):
        while True:
            await self.cleanup_old_files()
            await asyncio.sleep(86400)  # Run daily

# server.py - Start cleanup service
cleanup_service = FileCleanupService(retention_days=30)
asyncio.create_task(cleanup_service.run_periodic_cleanup())
```

**Actions:**
1. Create cleanup service
2. Add to server startup
3. Configure retention period
4. Test cleanup logic

**Validation:**
- Upload old test files
- Wait for cleanup cycle
- Verify files deleted

**Risk:** LOW  
**Mitigation:** Start with long retention (90 days)  
**Effort:** 4 hours

---

## Phase 2: Architecture Improvements (Week 2-3 - 10 days)

### 2.1 Create Unified File Manager
**Priority:** HIGH  
**Files:** Create `src/storage/unified_file_manager.py`  
**Changes:**
```python
# src/storage/unified_file_manager.py
from typing import Optional, Dict
from src.providers.glm_files import GLMFileProvider
from src.providers/kimi_files import KimiFileProvider

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
1. Create unified manager
2. Migrate all upload calls
3. Add provider auto-selection
4. Implement Supabase tracking

**Validation:**
- All existing tests pass
- New unified interface works
- Provider selection correct

**Risk:** MEDIUM - Requires refactoring  
**Mitigation:** Gradual migration  
**Effort:** 2 days

### 2.2 Consolidate Provider Code
**Priority:** HIGH  
**Files:** `src/providers/glm_files.py`, `src/providers/kimi_files.py`, `src/providers/file_base.py`  
**Changes:**
- Extract common code to `file_base.py`
- Implement abstract methods in providers
- Remove duplicate code (70% reduction)

**Actions:**
1. Identify common code
2. Move to base class
3. Update providers to inherit
4. Remove duplicates

**Validation:**
- Unit tests for each provider
- Integration tests pass
- Code coverage maintained

**Risk:** MEDIUM - Potential regression  
**Mitigation:** Comprehensive testing  
**Effort:** 3 days

### 2.3 Implement Retry Logic
**Priority:** HIGH  
**Files:** Create `src/providers/retry_handler.py`  
**Changes:**
```python
# src/providers/retry_handler.py
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
                
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
    
    def is_retryable(self, error: Exception) -> bool:
        # Check if error is retryable
        retryable_codes = [429, 500, 502, 503, 504]
        return hasattr(error, 'status_code') and error.status_code in retryable_codes
```

**Actions:**
1. Create retry handler
2. Add to all upload functions
3. Configure retry parameters
4. Test with simulated failures

**Validation:**
- Test with network errors → retries
- Test with auth errors → no retry
- Test with rate limit → exponential backoff

**Risk:** LOW  
**Effort:** 1 day

### 2.4 Add Comprehensive Monitoring
**Priority:** HIGH  
**Files:** Create `src/monitoring/file_upload_metrics.py`  
**Changes:**
```python
# src/monitoring/file_upload_metrics.py
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
2. Add to upload functions
3. Integrate with Prometheus
4. Update monitoring dashboard

**Validation:**
- Metrics appear in Prometheus
- Dashboard shows metrics
- Alerts configured

**Risk:** LOW  
**Effort:** 1 day

### 2.5 Remove Dead Code
**Priority:** MEDIUM  
**Files:** Delete `tools/async_file_upload_refactored.py`, `tools/file_upload_optimizer.py`  
**Actions:**
1. Verify files are unused
2. Check for imports
3. Delete files
4. Update documentation

**Validation:**
- No import errors
- All tests pass
- System functions normally

**Risk:** LOW  
**Effort:** 2 hours

---

## Phase 3: Configuration Cleanup (Week 4 - 5 days)

### 3.1 Consolidate Configuration
**Priority:** MEDIUM  
**Files:** `.env.docker`, create `.env.dev`, `.env.prod`  
**Actions:**
1. Identify common configs
2. Remove duplicates
3. Separate dev/prod configs
4. Reduce to <200 lines

**Validation:**
- All features work
- Dev/prod configs correct
- No missing variables

**Risk:** MEDIUM  
**Mitigation:** Careful migration  
**Effort:** 2 days

### 3.2 Centralize Timeout Configuration
**Priority:** MEDIUM  
**Files:** `src/core/env_config.py`  
**Actions:**
1. Create timeout config class
2. Remove provider-specific timeouts
3. Use centralized config

**Validation:**
- Timeouts work correctly
- Consistent behavior

**Risk:** LOW  
**Effort:** 1 day

### 3.3 Implement Configuration Validation
**Priority:** MEDIUM  
**Files:** Create `src/core/config_validator.py`  
**Actions:**
1. Create validator
2. Add to startup
3. Validate all env vars

**Validation:**
- Invalid configs rejected
- Helpful error messages

**Risk:** LOW  
**Effort:** 1 day

---

## Phase 4: Advanced Features (Week 5-6 - 10 days)

### 4.1 Implement Chunked Upload
**Priority:** LOW  
**Files:** `src/providers/glm_files.py`, `src/providers/kimi_files.py`  
**Actions:**
1. Add chunked upload logic
2. Configure chunk sizes (10MB GLM, 8MB Kimi)
3. Test with large files

**Validation:**
- Upload 1GB file successfully
- Progress tracking works

**Risk:** MEDIUM  
**Effort:** 3 days

### 4.2 Add File Validation
**Priority:** LOW  
**Files:** Create `src/security/file_validator.py`  
**Actions:**
1. Magic number checking
2. MIME type validation
3. File size validation

**Validation:**
- Valid files accepted
- Invalid files rejected

**Risk:** LOW  
**Effort:** 1 day

### 4.3 Implement User Quotas
**Priority:** LOW  
**Files:** Create `src/storage/quota_manager.py`  
**Actions:**
1. Track per-user uploads
2. Enforce quotas
3. Add quota API

**Validation:**
- Quota enforcement works
- Users can check quota

**Risk:** MEDIUM  
**Effort:** 2 days

### 4.4 Add Rate Limiting
**Priority:** LOW  
**Files:** Create `src/middleware/rate_limiter.py`  
**Actions:**
1. Implement rate limiter
2. Add to upload endpoint
3. Configure limits

**Validation:**
- Rate limiting works
- Proper error messages

**Risk:** LOW  
**Effort:** 1 day

---

## Timeline Summary

| Phase | Duration | Effort | Priority |
|-------|----------|--------|----------|
| Phase 0: Preparation | 3 days | 2 days | CRITICAL |
| Phase 1: Critical Fixes | 5 days | 4 days | CRITICAL |
| Phase 2: Architecture | 10 days | 8 days | HIGH |
| Phase 3: Configuration | 5 days | 4 days | MEDIUM |
| Phase 4: Advanced | 10 days | 7 days | LOW |
| **TOTAL** | **6 weeks** | **25 days** | - |

---

## Breaking Changes

### 1.3 JWT Authentication
**Impact:** All clients must send JWT token  
**Migration:** 
1. Generate JWT for each client
2. Update client code to include Authorization header
3. Implement grace period (2 weeks) accepting both auth methods

### 1.4 Path Validation
**Impact:** Some file paths may be rejected  
**Migration:**
1. Audit current file paths
2. Update allowlist
3. Notify users of path restrictions

---

## Rollback Plan

Each phase is independently deployable. If issues arise:

1. **Phase 1:** Revert env vars, disable auth
2. **Phase 2:** Keep old code alongside new (feature flag)
3. **Phase 3:** Keep old config files
4. **Phase 4:** Optional features, easy to disable

---

## Success Criteria

- ✅ All security vulnerabilities fixed
- ✅ Configuration reduced to <200 lines
- ✅ Dead code removed
- ✅ Provider code consolidated (70% reduction)
- ✅ Retry logic implemented
- ✅ Monitoring comprehensive
- ✅ All tests passing
- ✅ Zero regressions


