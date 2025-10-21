# 🔵 TRACK 2: PROVIDER ARCHITECTURE FIXES

**Goal:** Fix provider-level timeout and connection pooling issues  
**Status:** 🔍 QA COMPLETE - READY FOR IMPLEMENTATION  
**Estimated Time:** 3.5 hours (2h implementation + 1h testing + 0.5h docs)  
**Priority:** CRITICAL (root cause of all timeout issues)  
**QA Document:** `TRACK_2_QA_FINDINGS_2025-10-16.md`  
**EXAI Conversation:** `debb44af-15b9-456d-9b88-6a2519f81427`  

---

## 🎯 OBJECTIVE

Fix critical provider-level architectural issues identified during comprehensive QA:
- GLM sync provider: NO timeout configuration → can hang indefinitely
- Kimi sync provider: 300s default timeout → allows 5-minute hangs
- No connection pooling in sync providers → poor performance
- No retry logic → no graceful failure handling
- GLM async provider uses sync client → blocks event loop

**Root Cause:** Tool-level timeout system (expert_analysis.py) is correct, but undermined by provider-level issues.

---

## 📋 IMPLEMENTATION PLAN

### **Phase 1: GLM Provider Fixes (1 hour)**

#### **Fix 1: Add Timeout Configuration**

**File:** `src/providers/glm.py` (line 36)

**Current Code:**
```python
self._sdk_client = ZhipuAI(api_key=self.api_key, base_url=self.base_url)
```

**Updated Code:**
```python
self._sdk_client = ZhipuAI(
    api_key=self.api_key,
    base_url=self.base_url,
    timeout=30.0,  # 30s timeout for MCP tools
    max_retries=3,  # Retry logic with exponential backoff
)
```

**Impact:** Prevents indefinite hangs in all GLM-based tools.

---

#### **Fix 2: Add Connection Pooling**

**File:** `src/providers/glm.py` (lines 1-40)

**Add Import:**
```python
import httpx
```

**Update __init__ Method:**
```python
def __init__(self, api_key: str, base_url: Optional[str] = None, **kwargs):
    super().__init__(api_key, **kwargs)
    self.base_url = base_url or self.DEFAULT_BASE_URL
    
    # Initialize HTTP client with connection pooling
    http_client = httpx.Client(
        limits=httpx.Limits(
            max_keepalive_connections=10,
            max_connections=100,
        )
    )
    
    # Initialize HTTP client first (always needed as fallback)
    self.client = HttpClient(
        self.base_url,
        api_key=self.api_key,
        api_key_header="Authorization",
        api_key_prefix="Bearer "
    )
    
    # Prefer official SDK; fallback to HTTP if not available
    try:
        from zhipuai import ZhipuAI
        self._use_sdk = True
        self._sdk_client = ZhipuAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=30.0,
            max_retries=3,
            http_client=http_client,
        )
        logger.info(f"GLM provider using SDK with base_url={self.base_url}, timeout=30s, connection_pooling=enabled")
    except Exception as e:
        logger.warning("zhipuai SDK unavailable or failed to init; falling back to HTTP client: %s", e, exc_info=True)
        self._use_sdk = False
```

**Impact:** Improves performance through connection reuse.

---

### **Phase 2: Kimi Provider Fixes (30 min)**

#### **Fix 3: Reduce Default Timeout**

**File:** `src/providers/kimi.py` (line 48)

**Current Code:**
```python
kwargs["read_timeout"] = float(os.getenv("KIMI_DEFAULT_READ_TIMEOUT_SECS", "300"))
```

**Updated Code:**
```python
kwargs["read_timeout"] = float(os.getenv("KIMI_DEFAULT_READ_TIMEOUT_SECS", "30"))
```

**Impact:** Reduces maximum hang time from 5 minutes to 30 seconds.

---

### **Phase 3: Environment Configuration (15 min)**

#### **Fix 4: Update .env.docker**

**File:** `.env.docker`

**Add:**
```bash
# ============================================================================
# PROVIDER TIMEOUT CONFIGURATION (Track 2 Fixes)
# ============================================================================
# Provider-specific timeouts (30s for MCP tools)
GLM_DEFAULT_TIMEOUT_SECS=30
KIMI_DEFAULT_READ_TIMEOUT_SECS=30

# Connection pooling settings
GLM_MAX_KEEPALIVE_CONNECTIONS=10
GLM_MAX_CONNECTIONS=100
```

---

#### **Fix 5: Update .env.example**

**File:** `.env.example`

**Add same configuration as .env.docker** (without actual API keys)

---

### **Phase 4: Testing & Validation (1 hour)**

#### **Test 1: Simple Tool Test**
```bash
# Test debug tool with confidence="certain"
# Expected: Complete in < 5s
docker exec -it exai-mcp-daemon python -c "
from tools.workflows.debug import DebugIssueTool
import asyncio
tool = DebugIssueTool()
result = asyncio.run(tool.execute({
    'step': 'Test',
    'step_number': 1,
    'total_steps': 1,
    'next_step_required': False,
    'findings': 'Test',
    'confidence': 'certain'
}))
print(result)
"
```

#### **Test 2: Medium Complexity Test**
```bash
# Test analyze tool with simple prompt
# Expected: Complete in < 30s
docker exec -it exai-mcp-daemon python -c "
from tools.workflows.analyze import AnalyzeTool
import asyncio
tool = AnalyzeTool()
result = asyncio.run(tool.execute({
    'step': 'Analyze simple code',
    'step_number': 1,
    'total_steps': 1,
    'next_step_required': False,
    'findings': 'Initial analysis',
    'use_assistant_model': False
}))
print(result)
"
```

#### **Test 3: Timeout Behavior Test**
```bash
# Test that timeout actually triggers at 30s
# Create a mock slow provider call
# Expected: Timeout error after 30s
```

#### **Test 4: Connection Pooling Test**
```bash
# Run multiple tools concurrently
# Expected: Connection reuse, faster performance
```

---

### **Phase 5: Documentation (30 min)**

#### **Update 1: Track 2 Status**
- Mark `TRACK_2_SCALE_PLAN.md` as COMPLETE
- Reference `TRACK_2_QA_FINDINGS_2025-10-16.md`
- Document provider architecture improvements

#### **Update 2: API SDK Reference**
- Add provider timeout configuration examples
- Document connection pooling best practices
- Update troubleshooting section

#### **Update 3: Operational Capabilities**
- Document new timeout behavior (30s max)
- Update performance metrics
- Add provider configuration section

---

## ✅ SUCCESS CRITERIA

After implementation:
- [ ] GLM provider has 30s timeout configured
- [ ] GLM provider has connection pooling enabled
- [ ] GLM provider has retry logic (max 3 retries)
- [ ] Kimi provider default timeout reduced to 30s
- [ ] Environment variables documented in .env.example
- [ ] All simple tools complete in < 5s
- [ ] All medium tools complete in < 30s
- [ ] Timeout errors trigger at 30s (not indefinitely)
- [ ] Connection pooling improves performance
- [ ] Documentation updated

---

## 🎯 EXPECTED OUTCOMES

**Performance Improvements:**
- ✅ No more indefinite hangs (GLM)
- ✅ No more 5-minute waits (Kimi)
- ✅ Faster repeated calls (connection pooling)
- ✅ Graceful failure handling (retry logic)
- ✅ Consistent 30s timeout across all tools

**User Experience:**
- ✅ Tools complete quickly or fail fast
- ✅ Clear error messages on timeout
- ✅ Predictable behavior
- ✅ Better resource utilization

---

## 📚 REFERENCE DOCUMENTATION

- **QA Findings:** `TRACK_2_QA_FINDINGS_2025-10-16.md`
- **API SDK Reference:** `docs/04_GUIDES/API_SDK_REFERENCE.md`
- **Operational Capabilities:** `docs/04_GUIDES/OPERATIONAL_CAPABILITIES_2025-10-16.md`
- **TimeoutConfig:** `config.py` (lines 254-410)
- **Expert Analysis Timeout:** `tools/workflow/expert_analysis.py` (lines 550-636)

---

## 🚀 NEXT STEPS AFTER COMPLETION

1. **Mark Track 2 as COMPLETE**
2. **Update task manager**
3. **Proceed to Supabase UI Dashboard** (next priority)
4. **Monitor for regressions** in production

---

**Document Status:** ✅ READY FOR IMPLEMENTATION  
**Created:** 2025-10-16  
**EXAI Conversation:** `debb44af-15b9-456d-9b88-6a2519f81427`  
**Next Update:** After implementation complete

