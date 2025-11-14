# Critical Configuration Issues Report

**Date**: 2025-11-12 19:55:00
**Severity**: CRITICAL - Blocking WebSocket functionality
**Status**: Requires immediate fixes

---

## 🚨 CRITICAL BUGS

### 1. **BUG #1: Logger Used Before Definition** (Pylance Error)
**File**: `scripts/runtime/run_ws_shim.py:34`
**Issue**:
```python
try:
    from src.bootstrap import load_env
    load_env()
except Exception as e:
    logger.warning(f"Could not load env from bootstrap: {e}")  # ❌ logger not defined yet!
    # Try loading .env manually
    from dotenv import load_dotenv
    env_file = os.getenv('ENV_FILE', '.env')
    load_dotenv(env_file)

logger = logging.getLogger(__name__)  # ← Defined AFTER being used!
```

**Impact**: Script will crash on startup with `NameError: name 'logger' is not defined`

**Fix Required**: Move logger definition before the try/except block

---

### 2. **BUG #2: Wrong Default Port in run_ws_shim.py**
**File**: `scripts/runtime/run_ws_shim.py:45`
**Issue**:
```python
DAEMON_PORT = int(os.getenv("EXAI_WS_PORT", "3004"))  # ❌ Default is 3004!
```

**Problem**:
- `.env` has `EXAI_WS_PORT=3010`
- `.env.docker` has `EXAI_WS_PORT=8079` (inside container)
- `docker-compose.yml` maps `3010:8079`
- **But default in script is 3004** - Port mismatch!

**Impact**: If environment variable is missing, will try to connect to wrong port

**Fix Required**: Change default to match expected port (3010)

---

## 🔧 CONFIGURATION ISSUES

### 3. **Port Configuration Inconsistency**
**Issue**: Multiple configuration files with different values

| Config File | EXAI_WS_PORT | Context |
|-------------|--------------|---------|
| `.env` | 3010 | Host machine |
| `.env.docker` | 8079 | Inside Docker |
| `docker-compose.yml` | 3010:8079 | Port mapping |
| `run_ws_shim.py` | 3004 (default!) | Script default |

**Impact**: Confusing configuration, potential connection failures

---

### 4. **Exposed API Keys in Configuration**
**Issue**: Multiple API keys visible in .env files
```
GLM_API_KEY=95c42879e5c247beb7d9d30f3ba7b28f.uA2184L5axjigykH
KIMI_API_KEY=sk-AbCh3IrxmB5Bsx4JV0pnoqb0LajNdkwFvxfwR8KpDXB66qyB
MINIMAX_M2_KEY=eyJhbGci... (JWT token)
```

**Impact**: Security risk if shared or version controlled

---

## 📁 PROJECT BLOAT

### 5. **Excessive Script Count**
**Location**: `/scripts/` directory
**Count**: 95 Python scripts, 180 total files

**Examples of Bloat**:
- `apply_idempotency_migration.py*`
- `archive/` (entire directory)
- `batch_analyze_archive_docs.py*`
- `database/` (entire directory)
- `docs_cleanup/`
- `MIGRATION_EXECUTION_GUIDE.md`
- `MANUAL_MIGRATION_EXECUTION.md`
- `RUN_BACKFILL.md`
- `sdk_comparison/`
- `supabase/` (entire directory)
- And many more...

**Impact**:
- Hard to find actual needed scripts
- Maintenance burden
- Confuses new developers
- Slower development environment

**Recommendation**: 90% of these scripts should be archived or deleted

---

## 🔍 DOCKER ISSUES

### 6. **Unnecessary Port Mappings**
**File**: `docker-compose.yml`
**Issue**: Maps 4 ports but only 1 is actually needed:
- `3010:8079` ✅ **NEEDED** - WebSocket daemon
- `3001:8080` ❌ **UNUSED** - Monitoring Dashboard
- `3002:8082` ❌ **NOT RESPONDING** - Health Check
- `3003:8000` ❌ **UNUSED** - Prometheus Metrics

**Impact**: Exposes unnecessary services, clutters port space

---

### 7. **Health Check Not Working**
**File**: `docker-compose.yml:69-74`
**Issue**: Health check configured but HTTP server not running on port 8082
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import socket; s = socket.socket(); s.settimeout(2); s.connect(('127.0.0.1', 8079)); s.close(); exit(0)"]
```

**Impact**: Health check will fail, Docker marks container as unhealthy

---

## 🎯 REQUIRED FIXES (Priority Order)

### **Priority 1 (BLOCKING)** - Fix within 30 minutes
1. **Fix logger bug** in `run_ws_shim.py` line 34
2. **Fix default port** in `run_ws_shim.py` line 45 (3004 → 3010)

### **Priority 2 (HIGH)** - Fix today
3. **Verify port mapping** works correctly (3010 → 8079)
4. **Remove unused port mappings** from docker-compose.yml
5. **Add HTTP health endpoint** to daemon OR remove health check

### **Priority 3 (MEDIUM)** - Fix this week
6. **Archive old scripts** - Move 80+ scripts to `/archive/` or delete
7. **Review API key exposure** - Ensure not in version control
8. **Document actual needed scripts** - Create a minimal script list

---

## 📊 IMPACT ASSESSMENT

### What's Actually Working
✅ Docker daemon running on port 8079 inside container
✅ WebSocket shim running on port 3005 (host)
✅ Port mapping 3010:8079 functional
✅ MCP protocol translation working

### What's Broken
❌ WebSocket shim crashes if env vars missing (logger bug)
❌ Potential connection issues if EXAI_WS_PORT not set (wrong default)
❌ Health check failing (Docker marks unhealthy)
❌ Excess bloat slows development

### Estimated Fix Time
- **Priority 1**: 15 minutes
- **Priority 2**: 1 hour
- **Priority 3**: 2-4 hours

---

## 🎯 IMMEDIATE ACTION ITEMS

1. **Fix `run_ws_shim.py`**:
   - Move logger definition before try/except (line 30)
   - Change default port from 3004 to 3010

2. **Test WebSocket connection** after fixes

3. **Clean up scripts directory** - Archive 80% of scripts

4. **Remove unused ports** from docker-compose.yml

---

**Bottom Line**: The WebSocket connection **works** but has critical bugs that could cause crashes. The project has severe bloat (95 scripts!) that needs addressing.
