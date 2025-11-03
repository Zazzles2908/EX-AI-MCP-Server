# LEGACY CODE REMOVAL PLAN

**Date:** 2025-11-03
**Status:** 🔴 PENDING
**Priority:** 🟡 MEDIUM (Phase C - After core infrastructure complete)
**EXAI Consultation:** Continuation ID: be344ed8-2dc5-41a8-b99b-f5d288d1a3d6

---

## 🎯 OBJECTIVE

Remove all legacy code and dead files identified in the comprehensive master checklist to:
- Reduce codebase complexity
- Eliminate confusion from duplicate implementations
- Improve maintainability
- Clean up configuration bloat

---

## 📋 LEGACY FILES TO REMOVE

### **Configuration Files (3 files)**

#### 1. `config/timeouts.py`
**Status:** ❌ DELETE
**Reason:** Consolidated into `config/operations.py`
**Risk:** LOW - Already migrated
**Validation:**
- Verify `config/operations.py` contains all timeout configurations
- Search codebase for imports of `config.timeouts`
- Update any remaining imports to `config.operations`

#### 2. `config/migration.py`
**Status:** ❌ DELETE
**Reason:** No longer needed (migration complete)
**Risk:** LOW - Migration Phase 1 complete
**Validation:**
- Verify no active migrations reference this file
- Search codebase for imports of `config.migration`
- Confirm backward compatibility wrapper is sufficient

#### 3. `config/file_handling.py`
**Status:** ❌ DELETE
**Reason:** Consolidated into `config/file_management.py`
**Risk:** LOW - Already migrated
**Validation:**
- Verify `config/file_management.py` contains all file handling config
- Search codebase for imports of `config.file_handling`
- Update any remaining imports to `config/file_management`

### **Legacy Wrapper (1 file - KEEP for now)**

#### 4. `src/storage/unified_file_manager.py`
**Status:** ⏳ KEEP (Phase 1 of migration)
**Reason:** Backward compatibility wrapper (deprecation warnings active)
**Timeline:**
- Phase 1 (Current): Keep wrapper, emit deprecation warnings
- Phase 2 (Week 4-5): Update all internal code to use new manager
- Phase 3 (Week 6): Remove wrapper after migration complete
**Risk:** MEDIUM - Breaking change if removed too early

---

## 🔍 DEAD CODE IDENTIFICATION

### **Search Strategy**

1. **Find all imports of legacy files:**
```bash
# Search for config.timeouts imports
grep -r "from config.timeouts" src/
grep -r "import config.timeouts" src/

# Search for config.migration imports
grep -r "from config.migration" src/
grep -r "import config.migration" src/

# Search for config.file_handling imports
grep -r "from config.file_handling" src/
grep -r "import config.file_handling" src/
```

2. **Verify no runtime usage:**
```bash
# Check if files are imported in __init__.py
grep -r "timeouts" config/__init__.py
grep -r "migration" config/__init__.py
grep -r "file_handling" config/__init__.py
```

3. **Check for indirect references:**
```bash
# Search for string references
grep -r "timeouts.py" .
grep -r "migration.py" .
grep -r "file_handling.py" .
```

---

## 🛡️ SAFE REMOVAL PROCESS

### **Step 1: Create Backup Branch**
```bash
git checkout -b backup/pre-legacy-removal
git push origin backup/pre-legacy-removal
```

### **Step 2: Remove Files in Small Batches**

**Batch 1: config/timeouts.py**
1. Search for all imports
2. Update imports to `config.operations`
3. Delete file
4. Run tests
5. Docker rebuild
6. Validate functionality

**Batch 2: config/migration.py**
1. Search for all imports
2. Remove imports (no replacement needed)
3. Delete file
4. Run tests
5. Docker rebuild
6. Validate functionality

**Batch 3: config/file_handling.py**
1. Search for all imports
2. Update imports to `config.file_management`
3. Delete file
4. Run tests
5. Docker rebuild
6. Validate functionality

### **Step 3: Validation After Each Batch**

**Automated Checks:**
```bash
# Run full test suite
pytest tests/

# Check for import errors
python -m py_compile src/**/*.py

# Verify Docker build
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Check logs for errors
docker logs exai-mcp-daemon --tail 100
```

**Manual Checks:**
- [ ] All containers start successfully
- [ ] No import errors in logs
- [ ] All tools accessible via MCP
- [ ] File upload functionality works
- [ ] Circuit breaker functionality works
- [ ] Monitoring metrics available

### **Step 4: EXAI Validation**

After all batches complete:
1. Create completion markdown
2. Upload to EXAI with Docker logs
3. Address any issues identified
4. Get final approval

---

## 📊 CONFIGURATION CLEANUP

### **Current State: .env.docker (776 lines)**

**Target:** <200 lines

### **Cleanup Strategy**

#### **Phase 1: Move Defaults to Python Config (Reduce by ~300 lines)**

Move non-sensitive defaults from .env.docker to Python config classes:

**Example:**
```python
# config/file_management.py
class FileManagementConfig(BaseConfig):
    max_file_size: int = 512 * 1024 * 1024  # 512MB (default)
    max_concurrent_uploads: int = 10  # default
    default_retention_days: int = 30  # default
    allowed_mime_types: List[str] = [
        "image/jpeg", "image/png", "application/pdf", ...
    ]
```

**Remove from .env.docker:**
```bash
# These become Python defaults
MAX_FILE_SIZE_MB=512
MAX_CONCURRENT_UPLOADS=10
DEFAULT_RETENTION_DAYS=30
ALLOWED_MIME_TYPES=image/jpeg,image/png,...
```

#### **Phase 2: Consolidate Duplicate Settings (Reduce by ~200 lines)**

**Duplicates to Remove:**
- Provider-specific timeouts (use single timeout config)
- Duplicate Redis settings
- Duplicate Supabase settings
- Duplicate monitoring settings

#### **Phase 3: Remove Dev-Only Settings (Reduce by ~100 lines)**

**Settings to Remove:**
- Debug flags (keep only essential ones)
- Development-specific overrides
- Commented-out settings
- Unused feature flags

#### **Phase 4: Environment-Specific Overrides (Reduce by ~100 lines)**

Create separate files for environment-specific settings:
- `.env.docker.production` (minimal overrides)
- `.env.docker.development` (dev-specific settings)
- `.env.docker.testing` (test-specific settings)

### **Target .env.docker Structure (<200 lines)**

```bash
# ============================================================================
# CORE SETTINGS (10 lines)
# ============================================================================
EXAI_ENV=production
EXAI_LOG_LEVEL=INFO
EXAI_WS_PORT=8079
DEFAULT_MODEL=glm-4.5-flash
ROUTER_ENABLED=true
GLM_ENABLE_WEB_BROWSING=true
LEAN_MODE=true

# ============================================================================
# AUTHENTICATION (20 lines)
# ============================================================================
JWT_SECRET=${JWT_SECRET}
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_SERVICE_KEY=${SUPABASE_SERVICE_KEY}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

# ============================================================================
# PROVIDER APIs (20 lines)
# ============================================================================
MOONSHOT_API_KEY=${MOONSHOT_API_KEY}
GLM_API_KEY=${GLM_API_KEY}

# ============================================================================
# REDIS (15 lines)
# ============================================================================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=${REDIS_PASSWORD}
REDIS_DB=0

# ============================================================================
# FILE UPLOAD SETTINGS (20 lines)
# ============================================================================
# Only overrides from Python defaults
MAX_FILE_SIZE_MB=512  # Override if needed
MAX_CONCURRENT_UPLOADS=10  # Override if needed

# ============================================================================
# SECURITY (20 lines)
# ============================================================================
EX_ALLOW_EXTERNAL_PATHS=false
EX_ALLOWED_EXTERNAL_PREFIXES=/app,/mnt/project

# ============================================================================
# MONITORING (15 lines)
# ============================================================================
PROMETHEUS_ENABLED=true
METRICS_PORT=8000

# ============================================================================
# WEBSOCKET (20 lines)
# ============================================================================
EXAI_WS_HOST=0.0.0.0
EXAI_WS_PORT=8079
EXAI_WS_PING_INTERVAL=45
EXAI_WS_PING_TIMEOUT=240

# ============================================================================
# TIMEOUTS (20 lines)
# ============================================================================
SIMPLE_TOOL_TIMEOUT_SECS=30
WORKFLOW_TOOL_TIMEOUT_SECS=300
EXPERT_ANALYSIS_TIMEOUT_SECS=300

# ============================================================================
# CIRCUIT BREAKER (20 lines)
# ============================================================================
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_SUCCESS_THRESHOLD=2
CIRCUIT_BREAKER_TIMEOUT=60

# Total: ~180 lines (within target)
```

---

## ✅ VALIDATION CHECKLIST

### **Before Removal**
- [ ] Create backup branch
- [ ] Document all files to be removed
- [ ] Search for all imports
- [ ] Identify replacement locations

### **During Removal**
- [ ] Remove files in small batches
- [ ] Update imports after each batch
- [ ] Run tests after each batch
- [ ] Docker rebuild after each batch
- [ ] Check logs for errors

### **After Removal**
- [ ] All tests passing
- [ ] No import errors
- [ ] All containers running
- [ ] All functionality working
- [ ] EXAI validation passed
- [ ] Configuration reduced to <200 lines

---

## 🚀 EXECUTION TIMELINE

**Week 3 - Phase C (1-2 days):**
- Day 1 Morning: Remove config files (3 batches)
- Day 1 Afternoon: Configuration cleanup (reduce to <200 lines)
- Day 2 Morning: Validation and testing
- Day 2 Afternoon: EXAI final validation

**Dependencies:**
- Must complete Phase A & B first
- All platform clients working
- All stub implementations complete
- Integration tests passing

---

**NEXT STEP:** Wait for Phase A & B completion before starting legacy removal

