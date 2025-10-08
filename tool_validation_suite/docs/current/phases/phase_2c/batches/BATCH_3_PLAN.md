# Phase 2C - Batch 3: Configuration Migration

**Date:** 2025-10-07  
**Status:** 🚧 IN PROGRESS  
**Time Estimate:** 1 hour  
**Time Spent:** 0 hours  
**Completion:** 0%

---

## 🎯 **OBJECTIVE**

Migrate remaining hardcoded configuration values to centralized config system and validate all environment variables.

---

## 📋 **SCOPE**

### **From Phase 1 Audit:**
- **72 hardcoded configuration values** identified across codebase
- **31 hardcoded values** in server scripts (URLs, paths, timeouts)
- **41 hardcoded values** in other files

### **Already Migrated (Phase 2A):**
- ✅ MESSAGE_BUS_* configuration (5 variables)
- ✅ CIRCUIT_BREAKER_* configuration (4 variables)
- ✅ SUPABASE_* configuration (3 variables)
- ✅ ENVIRONMENT configuration (1 variable)

**Total Migrated:** 13 variables

---

## 🔍 **REMAINING HARDCODED VALUES TO MIGRATE**

### **Priority 1: Critical Configuration (10 values)**

1. **WebSocket Configuration**
   - `EXAI_WS_HOST` - Currently hardcoded as "127.0.0.1"
   - `EXAI_WS_PORT` - Currently hardcoded as 8079
   - `HELLO_TIMEOUT` - Currently hardcoded as 10.0
   - `CALL_TIMEOUT` - Currently hardcoded as 600

2. **Concurrency Configuration**
   - `GLOBAL_MAX_INFLIGHT` - Currently hardcoded as 16
   - `SESSION_MAX_INFLIGHT` - Currently hardcoded as 8
   - `PROVIDER_MAX_INFLIGHT` - Currently hardcoded as 8

3. **Metrics Configuration**
   - `METRICS_PATH` - Currently hardcoded path
   - `HEALTH_PATH` - Currently hardcoded path
   - `PID_PATH` - Currently hardcoded path

---

### **Priority 2: Provider Configuration (8 values)**

1. **Kimi Configuration**
   - `KIMI_MAX_HEADER_LEN` - Already in env ✅
   - `KIMI_API_KEY` - Already in env ✅
   - `KIMI_BASE_URL` - Already in env ✅

2. **GLM Configuration**
   - `GLM_STREAM_ENABLED` - Already in env ✅
   - `GLM_API_KEY` - Already in env ✅
   - `GLM_BASE_URL` - Already in env ✅

3. **Model Selection**
   - Default model selection logic - hardcoded
   - Model fallback logic - hardcoded

---

### **Priority 3: Optional Configuration (10 values)**

1. **Feature Flags**
   - `EX_ENSURE_NONEMPTY_FIRST` - Already in env ✅
   - `EXAI_WS_COMPAT_TEXT` - Already in env ✅
   - `EXAI_WS_DISABLE_COALESCE_FOR_TOOLS` - Already in env ✅

2. **Logging Configuration**
   - Log level - hardcoded
   - Log format - hardcoded
   - Log rotation - hardcoded

3. **Cache Configuration**
   - Cache TTL - hardcoded
   - Cache size - hardcoded

---

## 📊 **ANALYSIS**

### **Current State:**
- ✅ 13 critical variables already in .env
- ✅ Most provider configuration already in .env
- ✅ Most feature flags already in .env
- ⏳ WebSocket configuration needs migration
- ⏳ Concurrency configuration needs migration
- ⏳ Metrics paths need migration

### **Observation:**
**Most configuration is already migrated!** The Phase 1 audit counted 72 values, but many were:
- Already in .env files
- Already using environment variables
- Already centralized in config.py

**Actual Remaining Work:** ~10-15 critical values need migration

---

## 🎯 **IMPLEMENTATION PLAN**

### **Step 1: Audit Current .env Files (15 minutes)**
1. Review .env and .env.example
2. Identify what's already there
3. Identify what's missing
4. Create list of values to add

### **Step 2: Add Missing Variables to .env (15 minutes)**
1. Add WebSocket configuration
2. Add concurrency configuration
3. Add metrics paths
4. Update .env.example to match

### **Step 3: Update config.py (15 minutes)**
1. Add new configuration fields
2. Add validation for new fields
3. Add default values
4. Test configuration loading

### **Step 4: Update Code to Use Config (15 minutes)**
1. Replace hardcoded values in ws_server.py
2. Replace hardcoded values in other files
3. Test all changes
4. Restart server and validate

---

## 🚀 **EXPECTED OUTCOMES**

**Configuration Centralization:**
- Before: ~15 hardcoded values scattered in code
- After: All values in .env and config.py

**Maintainability:**
- Before: Need to edit code to change configuration
- After: Edit .env file only

**Validation:**
- Before: No validation of configuration values
- After: Type validation and range checking in config.py

---

## 📋 **SUCCESS CRITERIA**

1. ✅ All critical configuration in .env
2. ✅ .env.example matches .env structure
3. ✅ config.py validates all values
4. ✅ No hardcoded configuration in code
5. ✅ Server restarts successfully
6. ✅ All functionality working

---

**Status:** Ready to begin  
**Confidence:** HIGH - Most work already done, just need to migrate remaining values  
**Next:** Audit current .env files and identify missing values

