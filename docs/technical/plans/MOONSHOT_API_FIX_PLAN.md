# Moonshot API Implementation Fix Plan

**Date:** 2025-10-03  
**Status:** 🚨 READY FOR IMPLEMENTATION  
**Priority:** CRITICAL - 84-96% cost savings opportunity

---

## 📋 **EXECUTIVE SUMMARY**

User identified critical gaps in Moonshot API implementation. Research confirmed:
- ✅ Found official context caching documentation
- ✅ Identified proper headers and pricing model
- ✅ Calculated 84-96% cost savings opportunity
- ❌ Current implementation missing all caching features

**Estimated Savings:** ¥81 (~$11 USD) per full project review

---

## 🎯 **IMPLEMENTATION PHASES**

### Phase 1: Fix Context Caching (CRITICAL)
**Priority:** P0 - Immediate  
**Impact:** 84-96% cost savings  
**Effort:** 2-3 hours

### Phase 2: Fix Documentation (HIGH)
**Priority:** P1 - This week  
**Impact:** Accuracy and trust  
**Effort:** 1-2 hours

### Phase 3: Investigate Conversation ID (MEDIUM)
**Priority:** P2 - Next week  
**Impact:** Better context management  
**Effort:** 3-4 hours (research + implementation)

### Phase 4: Fix VSCode Settings (LOW)
**Priority:** P3 - When convenient  
**Impact:** Developer experience  
**Effort:** 30 minutes

---

## 🔧 **PHASE 1: FIX CONTEXT CACHING**

### 1.1 Update `src/providers/kimi_chat.py`

**Current Code (Lines 45-50):**
```python
def chat_completions_create(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    **kwargs
) -> dict:
    """Wrapper that injects idempotency and Kimi context-cache headers..."""
```

**Required Changes:**
```python
def chat_completions_create(
    client: Any,
    *,
    model: str,
    messages: list[dict[str, Any]],
    tools: Optional[list[Any]] = None,
    tool_choice: Optional[Any] = None,
    temperature: float = 0.6,
    cache_id: Optional[str] = None,  # NEW
    reset_cache_ttl: bool = False,   # NEW
    **kwargs
) -> dict:
    """Wrapper that injects idempotency and Kimi context-cache headers."""
    
    # Build extra headers
    extra_headers = kwargs.pop("extra_headers", {})
    
    # Add context caching headers if cache_id provided
    if cache_id:
        extra_headers["X-Msh-Context-Cache"] = cache_id
        if reset_cache_ttl:
            extra_headers["X-Msh-Context-Cache-Reset-TTL"] = "3600"
    
    # Add idempotency header (existing logic)
    # ... existing code ...
    
    # Call API with headers
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice=tool_choice,
        temperature=temperature,
        extra_headers=extra_headers,
        **kwargs
    )
    
    return response
```

### 1.2 Update `tools/providers/kimi/kimi_upload.py`

**Current Code (Lines 301-337):**
```python
def run(self, **kwargs) -> Dict[str, Any]:
    files = kwargs.get("files") or []
    prompt = kwargs.get("prompt") or ""
    model = kwargs.get("model") or os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
    temperature = float(kwargs.get("temperature") or 0.3)
    
    # ... upload files ...
    
    # Call Kimi
    resp = prov.chat_completions_create(
        model=model,
        messages=messages,
        temperature=temperature
    )
```

**Required Changes:**
```python
def run(self, **kwargs) -> Dict[str, Any]:
    files = kwargs.get("files") or []
    prompt = kwargs.get("prompt") or ""
    model = kwargs.get("model") or os.getenv("KIMI_DEFAULT_MODEL", "kimi-k2-0711-preview")
    temperature = float(kwargs.get("temperature") or 0.3)
    cache_id = kwargs.get("cache_id")  # NEW
    reset_cache_ttl = kwargs.get("reset_cache_ttl", False)  # NEW
    
    # ... upload files ...
    
    # Call Kimi with caching
    resp = prov.chat_completions_create(
        model=model,
        messages=messages,
        temperature=temperature,
        cache_id=cache_id,  # NEW
        reset_cache_ttl=reset_cache_ttl,  # NEW
    )
```

### 1.3 Update `scripts/kimi_code_review.py`

**Current Code (Lines 42-60):**
```python
class KimiCodeReviewer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.batch_size = 5
        self.design_context_file = None
```

**Required Changes:**
```python
class KimiCodeReviewer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.batch_size = 5
        self.design_context_file = None
        self.cache_id = None  # NEW - Track cache across batches
        
    def upload_design_context(self) -> str:
        """Upload consolidated design context and initialize cache."""
        logger.info("📚 Uploading consolidated design context to Kimi...")
        context_file = self.project_root / "docs" / "KIMI_DESIGN_CONTEXT.md"
        
        if not context_file.exists():
            raise FileNotFoundError(f"Design context file not found: {context_file}")
        
        # Generate cache ID for this review session
        import time
        self.cache_id = f"design_context_{int(time.time())}"  # NEW
        
        logger.info(f"✅ Design context file ready: {context_file}")
        logger.info(f"🔑 Cache ID: {self.cache_id}")  # NEW
        
        return str(context_file)
```

**Current Code (Lines 269-274):**
```python
result = kimi_tool.run(
    files=all_files,
    prompt=prompt,
    model="kimi-k2-0905-preview",
    temperature=0.3
)
```

**Required Changes:**
```python
result = kimi_tool.run(
    files=all_files,
    prompt=prompt,
    model="kimi-k2-0905-preview",
    temperature=0.3,
    cache_id=self.cache_id,  # NEW - Reuse cache across batches
    reset_cache_ttl=True,    # NEW - Keep cache alive
)
```

### 1.4 Testing Plan

**Test 1: Verify Headers**
```python
# Add debug logging to kimi_chat.py
logger.info(f"Cache headers: {extra_headers}")

# Expected output:
# Cache headers: {
#   'X-Msh-Context-Cache': 'design_context_1696348800',
#   'X-Msh-Context-Cache-Reset-TTL': '3600'
# }
```

**Test 2: Verify Cost Savings**
```python
# Run code review and check logs for cache hits
# Expected: First batch creates cache, subsequent batches hit cache
# Cost: ~¥5.39 instead of ~¥33.6 (84% savings)
```

**Test 3: Verify Cache Persistence**
```python
# Run two batches with 5-minute delay
# Expected: Cache still valid, second batch hits cache
```

---

## 📝 **PHASE 2: FIX DOCUMENTATION**

### 2.1 Fix Platform URLs

**Files to Update:**
- `docs/KIMI_CODE_REVIEW_WHERE_IS_THE_DATA.md`
- `docs/KIMI_INVESTIGATION_COMPLETE.md`
- `docs/KIMI_CODE_REVIEW_FINAL_SUCCESS.md`
- All system-reference docs

**Changes:**
```markdown
# WRONG:
Check Kimi platform at https://kimi.moonshot.cn/

# CORRECT:
Check Moonshot platform at https://platform.moonshot.ai/
(Note: https://kimi.moonshot.cn/ is the consumer chat interface)
```

### 2.2 Add Context Caching Documentation

**Create:** `docs/system-reference/api/context-caching.md`

**Content:**
```markdown
# Context Caching

**Version:** 1.0  
**Last Updated:** 2025-10-03  
**Source:** https://platform.moonshot.cn/blog/posts/how-to-save-90-percent-with-context-caching

## Overview

Moonshot AI's context caching feature can reduce API costs by up to 90% for repeated context.

## Headers

### X-Msh-Context-Cache
Cache identifier for this context.

### X-Msh-Context-Cache-Reset-TTL
Time-to-live in seconds (e.g., "3600" for 1 hour).

## Pricing

- **Create Cache:** ¥24/M tokens (one-time)
- **Storage:** ¥10/M tokens/minute
- **Cache Hit:** ¥0.02 per call
- **Regular Input:** ¥60/M tokens

## Best Practices

1. **Use for repeated context** (e.g., system prompts, documentation)
2. **Enable during peak hours** (>11 calls/hour)
3. **Disable during low traffic** (<11 calls/hour)
4. **Reset TTL regularly** to keep cache alive

## Example

```python
response = client.chat.completions.create(
    model="moonshot-v1-128k",
    messages=messages,
    extra_headers={
        "X-Msh-Context-Cache": "my_cache_id",
        "X-Msh-Context-Cache-Reset-TTL": "3600",
    },
)
```
```

---

## 🔍 **PHASE 3: INVESTIGATE CONVERSATION ID**

### 3.1 Research Tasks

1. **Check Moonshot API docs** for conversation threading
2. **Test API responses** for conversation_id field
3. **Review Kimi platform** for conversation management
4. **Check if cache_id** can serve as conversation identifier

### 3.2 Implementation (If Supported)

**If conversation_id exists:**
```python
# First call
response = client.chat.completions.create(...)
conversation_id = response.get("conversation_id")

# Subsequent calls
response = client.chat.completions.create(
    conversation_id=conversation_id,
    ...
)
```

**If not supported:**
- Use cache_id as conversation identifier
- Track conversation state locally
- Document limitation

---

## ⚙️ **PHASE 4: FIX VSCODE SETTINGS**

### 4.1 Investigation

Check these settings:
```json
// .vscode/settings.json
{
  "python.terminal.activateEnvironment": false,  // Add this
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe"  // Check this
}
```

### 4.2 PowerShell Profile

Check if `$PROFILE` auto-activates venv:
```powershell
# Check profile
Test-Path $PROFILE

# View profile
Get-Content $PROFILE

# Look for .venv activation
```

---

## ✅ **ACCEPTANCE CRITERIA**

### Phase 1: Context Caching
- [ ] Headers added to kimi_chat.py
- [ ] cache_id parameter added to kimi_upload.py
- [ ] cache_id tracking added to kimi_code_review.py
- [ ] Debug logging shows correct headers
- [ ] Cost reduced by 84%+ (verified in logs)
- [ ] All tests pass

### Phase 2: Documentation
- [ ] All platform URLs corrected
- [ ] Context caching docs created
- [ ] Cost optimization guide added
- [ ] All links verified

### Phase 3: Conversation ID
- [ ] Research complete
- [ ] Implementation plan created
- [ ] If supported: Implemented and tested
- [ ] If not: Documented limitation

### Phase 4: VSCode Settings
- [ ] Terminal activation investigated
- [ ] Settings corrected if needed
- [ ] Documented in project README

---

## 🚀 **NEXT STEPS**

1. **Get user approval** for this plan
2. **Implement Phase 1** (context caching)
3. **Test with EXAI validation**
4. **Run full code review** with caching enabled
5. **Verify cost savings** in logs
6. **Complete remaining phases**

---

**Ready to proceed with implementation?**

