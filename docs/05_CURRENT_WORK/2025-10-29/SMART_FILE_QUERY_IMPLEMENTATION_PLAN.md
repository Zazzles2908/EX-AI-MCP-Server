# Smart File Query - Implementation Plan

**Date:** 2025-10-29  
**Status:** PLANNING  
**EXAI Consultation:** Continuation ID `ed0f9ee4-906a-4cd7-848e-4a49bb93de6b`  
**Model Used:** GLM-4.6

---

## 🎯 **OBJECTIVE**

Consolidate 6+ file upload tools into ONE intelligent tool: `smart_file_query`

**Current Tools (To Be Consolidated):**
- `kimi_upload_files` - Upload to Kimi/Moonshot
- `glm_upload_file` - Upload to GLM/Z.ai
- `kimi_chat_with_files` - Chat with Kimi files
- `kimi_manage_files` - Manage Kimi files
- Various Supabase tools

**New Tool:**
- `smart_file_query` - Upload (with deduplication) + Query in one call

---

## 🏗️ **ARCHITECTURE (Per EXAI Recommendation)**

**Pattern:** Orchestrator (NOT monolithic rewrite)

**Rationale:**
- Preserves existing deduplication infrastructure
- Reuses validation and provider-specific code
- Adds intelligent routing layer
- Avoids code duplication
- Keeps scripts maintainable

**LangChain:** ❌ NO
- Overkill for simple upload-query workflow
- Adds unnecessary abstraction
- We have only 2 providers
- No complex RAG needs

---

## 📋 **5-STEP IMPLEMENTATION PLAN**

### **Step 1: Create Core Orchestrator**

**File:** `tools/smart_file_query.py`

**Function Signature:**
```python
def smart_file_query(
    file_path: str,
    question: str,
    provider: Optional[str] = None,  # "glm", "kimi", or None (auto)
    model: Optional[str] = None  # Override default model
) -> Dict[str, Any]:
    """
    Intelligent file upload + query in one call.
    
    Features:
    - Automatic path validation
    - SHA256 deduplication (reuses existing files)
    - Intelligent provider selection (GLM <20MB, Kimi <100MB)
    - Automatic fallback on failure
    - Supabase tracking
    
    Returns:
        {
            "answer": str,
            "provider_used": str,
            "file_id": str,
            "deduplicated": bool,
            "metadata": {...}
        }
    """
```

**Logic Flow:**
1. Validate path using `validate_upload_path()` from `utils/path_validation.py`
2. Calculate SHA256 and check duplicates via `FileDeduplicationManager.check_duplicate()`
3. Route to `upload_or_reuse_file()`
4. Query using `query_with_fallback()`
5. Return structured response

---

### **Step 2: Extract Upload Logic**

**Function:** `upload_or_reuse_file()`

**Location:** `tools/smart_file_query.py` (internal helper)

**Logic:**
```python
def upload_or_reuse_file(file_path: str, provider: str) -> Tuple[str, bool]:
    """
    Upload file or reuse existing.
    
    Returns:
        (provider_file_id, was_deduplicated)
    """
    # Check duplicate using FileDeduplicationManager
    existing = dedup_manager.check_duplicate(file_path, provider)
    
    if existing:
        # Increment reference count
        dedup_manager.increment_reference(existing['provider_file_id'], provider)
        return (existing['provider_file_id'], True)
    
    # Upload to Supabase Storage first
    supabase_file_id = hybrid_manager.upload_file(...)
    
    # Upload to AI provider
    if provider == "glm":
        provider_file_id = glm_provider.upload_file(file_path)
    else:
        provider_file_id = kimi_provider.upload_file(file_path)
    
    # Register in database
    dedup_manager.register_new_file(
        provider_file_id=provider_file_id,
        supabase_file_id=supabase_file_id,
        file_path=file_path,
        provider=provider
    )
    
    return (provider_file_id, False)
```

---

### **Step 3: Implement Provider Router**

**Function:** `route_to_provider()`

**Location:** `tools/smart_file_query.py` (internal helper)

**Strategy (Per EXAI):**
1. **User preference first** (if specified)
2. **File size fallback** (GLM <20MB, Kimi <100MB)
3. **Automatic fallback** on failure

**Logic:**
```python
def route_to_provider(
    file_path: str,
    preferred_provider: Optional[str],
    file_size: int
) -> str:
    """
    Intelligent provider selection.
    
    Priority:
    1. User preference (if valid for file size)
    2. File size based routing
    3. Default to GLM
    """
    # User preference
    if preferred_provider:
        if preferred_provider == "glm" and file_size < 20 * 1024 * 1024:
            return "glm"
        elif preferred_provider == "kimi" and file_size < 100 * 1024 * 1024:
            return "kimi"
        # Fall through to automatic selection if preference invalid
    
    # Automatic selection
    if file_size < 20 * 1024 * 1024:  # 20MB
        return "glm"
    elif file_size < 100 * 1024 * 1024:  # 100MB
        return "kimi"
    else:
        raise ValueError(f"File too large: {file_size} bytes (max 100MB)")
```

---

### **Step 4: Add Fallback Mechanism**

**Function:** `query_with_fallback()`

**Location:** `tools/smart_file_query.py` (internal helper)

**Logic:**
```python
def query_with_fallback(
    file_id: str,
    question: str,
    primary_provider: str,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query file with automatic fallback.
    
    If primary provider fails, automatically try alternate provider.
    """
    try:
        # Try primary provider
        if primary_provider == "glm":
            result = glm_provider.query_file(file_id, question, model)
        else:
            result = kimi_provider.query_file(file_id, question, model)
        
        return {
            "answer": result,
            "provider_used": primary_provider,
            "fallback_used": False
        }
    
    except Exception as e:
        logger.warning(f"Primary provider {primary_provider} failed: {e}")
        
        # Fallback to alternate provider
        fallback = "kimi" if primary_provider == "glm" else "glm"
        fallback_model = "kimi-k2-0905-preview" if fallback == "kimi" else "glm-4.6"
        
        try:
            if fallback == "glm":
                result = glm_provider.query_file(file_id, question, fallback_model)
            else:
                result = kimi_provider.query_file(file_id, question, fallback_model)
            
            return {
                "answer": result,
                "provider_used": fallback,
                "fallback_used": True,
                "primary_error": str(e)
            }
        
        except Exception as fallback_error:
            raise Exception(f"Both providers failed. Primary: {e}, Fallback: {fallback_error}")
```

---

### **Step 5: Integrate and Test**

**Tasks:**
1. Add to tool registry
2. Create MCP tool definition
3. Update tool descriptions
4. Test with various file sizes
5. Test deduplication
6. Test fallback mechanism
7. Update documentation

---

## 🗂️ **WHAT TO KEEP VS DELETE**

### **KEEP (Reuse as Internal Functions):**

✅ `utils/path_validation.py` - Core validation logic  
✅ `utils/file/deduplication.py` - FileDeduplicationManager  
✅ `tools/providers/kimi/kimi_files.py` - Keep as internal provider class  
✅ `tools/providers/glm/glm_files.py` - Keep as internal provider class  
✅ Supabase `provider_file_uploads` table  
✅ `src/storage/hybrid_supabase_manager.py` - Supabase operations

### **DELETE/DEPRECATE:**

❌ Individual MCP tool endpoints (expose only `smart_file_query`)  
❌ Duplicate validation logic in provider tools (already centralized)  
❌ Redundant file handling utilities

### **OPTIONAL (Mark as Deprecated):**

⚠️ Keep individual tools as "advanced" options for power users  
⚠️ Add deprecation warnings in tool descriptions  
⚠️ Document migration path to `smart_file_query`

---

## 📝 **TOOL DESCRIPTION TEMPLATE**

```markdown
# smart_file_query

**ONE intelligent tool for file upload + query**

## What It Does

Uploads a file (with automatic deduplication) and queries it with your question.

Features:
- ✅ Automatic path validation (Docker-aware)
- ✅ SHA256 deduplication (reuses existing files)
- ✅ Intelligent provider selection (GLM <20MB, Kimi <100MB)
- ✅ Automatic fallback on failure
- ✅ Supabase tracking and storage

## Parameters

- `file_path` (required): Linux container path (e.g., `/mnt/project/EX-AI-MCP-Server/file.txt`)
- `question` (required): Your question about the file
- `provider` (optional): "glm" or "kimi" (auto-selected if not specified)
- `model` (optional): Override default model

## Example

```python
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/README.md",
    question="What is this project about?",
    provider="glm"  # Optional
)
```

## Returns

```json
{
    "answer": "This project is...",
    "provider_used": "glm",
    "file_id": "abc123",
    "deduplicated": true,
    "metadata": {
        "file_size": 1024,
        "upload_time": "2025-10-29T..."
    }
}
```
```

---

## 🚀 **NEXT STEPS**

1. ✅ Create this implementation plan
2. ⏳ Implement Step 1: Core orchestrator
3. ⏳ Implement Step 2: Upload logic
4. ⏳ Implement Step 3: Provider router
5. ⏳ Implement Step 4: Fallback mechanism
6. ⏳ Implement Step 5: Integration and testing
7. ⏳ Update documentation
8. ⏳ Clean up dead code

---

## 📊 **EXAI ASSESSMENT**

**Architecture:** ✅ Orchestrator pattern (recommended)  
**LangChain:** ❌ Not needed (overkill)  
**Provider Selection:** ✅ Hybrid (user preference + file size)  
**Fallback:** ✅ Automatic with alternate provider  
**Code Reuse:** ✅ Maximum reuse of existing infrastructure

**Estimated Complexity:** Medium  
**Estimated Time:** 2-3 hours  
**Risk Level:** Low (reusing proven components)

