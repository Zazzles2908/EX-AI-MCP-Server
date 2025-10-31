# File Tool Architecture Analysis

**Date:** 2025-10-30  
**EXAI Consultation ID:** e403333f-eaf8-41d8-9249-347e2b2ebd3a  
**Status:** ✅ COMPREHENSIVE ANALYSIS COMPLETE

---

## 🎯 EXECUTIVE SUMMARY

The EX-AI-MCP-Server file tool system follows a **Unified Orchestrator Pattern** where `smart_file_query` acts as the primary interface, wrapping all legacy provider-specific tools. The architecture provides automatic deduplication, intelligent provider selection, and centralized Supabase tracking.

**Key Insight:** Kimi is ALWAYS used for file operations due to GLM's lack of file persistence across sessions.

---

## 📊 TOOL INVENTORY

### 1. **smart_file_query** (RECOMMENDED - Unified Interface)
**File:** `tools/smart_file_query.py`  
**Purpose:** Unified file upload and query orchestrator  
**Status:** ✅ Active (Primary Interface)

**Capabilities:**
- Automatic SHA256-based deduplication
- Intelligent provider selection (always Kimi for files)
- Automatic fallback (GLM fails → Kimi, vice versa)
- Centralized Supabase tracking
- Path validation and security checks

**Usage:**
```python
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code for security issues",
    provider="auto",  # Optional: "kimi", "glm", or "auto"
    model="auto"      # Optional: specific model or "auto"
)
```

---

### 2. **kimi_upload_files** (DEPRECATED)
**File:** `tools/providers/kimi/kimi_files.py`  
**Purpose:** Upload files to Moonshot/Kimi platform  
**Status:** ⚠️ Deprecated (use smart_file_query instead)

**Capabilities:**
- Upload multiple files (100MB limit per file)
- Returns file IDs only (no content extraction)
- Persistent file storage across sessions
- SHA256 deduplication via Supabase

**Usage:**
```python
kimi_upload_files(
    files=["/mnt/project/file1.py", "/mnt/project/file2.py"],
    purpose="file-extract"  # or "assistants"
)
# Returns: [{"file_id": "...", "filename": "...", "size_bytes": ...}, ...]
```

---

### 3. **kimi_chat_with_files** (DEPRECATED)
**File:** `tools/providers/kimi/kimi_files.py`  
**Purpose:** Chat with previously uploaded Kimi files  
**Status:** ⚠️ Deprecated (use smart_file_query instead)

**Capabilities:**
- Query uploaded files using file IDs
- Supports multiple files in single query
- Uses Kimi models for analysis

**Usage:**
```python
# Step 1: Upload files
file_ids = kimi_upload_files(files=["file.py"])

# Step 2: Chat with files
kimi_chat_with_files(
    prompt="Explain this code",
    file_ids=[file_ids[0]["file_id"]],
    model="kimi-k2-0905-preview"
)
```

---

### 4. **kimi_manage_files**
**File:** `tools/providers/kimi/kimi_files.py`  
**Purpose:** Manage Kimi files (list, delete, cleanup)  
**Status:** ✅ Active (File Management)

**Operations:**
- `list`: Show all uploaded files
- `delete`: Remove specific file by ID
- `cleanup_all`: Delete ALL files (use with caution!)
- `cleanup_orphaned`: Remove files not tracked in Supabase
- `cleanup_expired`: Remove files unused for 30+ days

**Usage:**
```python
# List all files
kimi_manage_files(operation="list", limit=100)

# Delete specific file
kimi_manage_files(operation="delete", file_id="d41909...")

# Cleanup expired files (dry run)
kimi_manage_files(operation="cleanup_expired", dry_run=True)
```

---

### 5. **kimi_intent_analysis**
**File:** `tools/providers/kimi/kimi_intent.py`  
**Purpose:** Classify user prompts and return routing hints  
**Status:** ✅ Active (Intent Classification)

**Capabilities:**
- Analyzes user prompts for intent
- Returns routing recommendations (provider, model, complexity)
- Determines if web search is needed
- Suggests streaming preference

**Output Schema:**
```json
{
  "needs_websearch": boolean,
  "complexity": "simple" | "moderate" | "deep",
  "domain": string,
  "recommended_provider": "GLM" | "KIMI",
  "recommended_model": string,
  "streaming_preferred": boolean
}
```

**Usage:**
```python
kimi_intent_analysis(
    prompt="Analyze this large codebase for security vulnerabilities",
    context="User is working on a Python project"
)
```

---

### 6. **glm_upload_file** (DEPRECATED)
**File:** `tools/providers/glm/glm_files.py`  
**Purpose:** Upload single file to GLM platform  
**Status:** ⚠️ Deprecated (use smart_file_query instead)

**Capabilities:**
- Upload single file (20MB limit)
- Session-bound files (expire after 24 hours)
- NO file persistence across queries

**Usage:**
```python
glm_upload_file(
    file="/mnt/project/file.py",
    purpose="agent"
)
# Returns: {"file_id": "...", "filename": "...", "size_bytes": ...}
```

---

### 7. **glm_multi_file_chat** (DEPRECATED)
**File:** `tools/providers/glm/glm_files.py`  
**Purpose:** Upload and chat with GLM files in one step  
**Status:** ⚠️ Deprecated (use smart_file_query instead)

**Capabilities:**
- Upload multiple files + query in single operation
- Files are re-uploaded for each query (no persistence)
- 20MB limit per file

**Usage:**
```python
glm_multi_file_chat(
    files=["/mnt/project/file1.py", "/mnt/project/file2.py"],
    prompt="Analyze these files",
    model="glm-4.5",
    temperature=0.3
)
```

---

## 🏗️ ARCHITECTURE OVERVIEW

### Complete Call Flow

```
User Request
    ↓
smart_file_query (UNIFIED ORCHESTRATOR)
    ↓
FileDeduplicationManager (SHA256 deduplication)
    ↓
upload_file_with_provider() (PROVIDER ROUTING)
    ↓
_kimi_upload_adapter() OR _glm_upload_adapter()
    ↓
SupabaseUploadManager (PERSISTENT STORAGE)
    ↓
Provider SDK (Kimi/GLM)
    ↓
FileIdMapper (BIDIRECTIONAL ID MAPPING)
```

### Detailed Flow Steps

1. **Entry Point**: `smart_file_query` receives the request
2. **Path Validation**: Cross-platform path normalization (Windows → Linux)
3. **Deduplication Check**: SHA256 hash calculation against Supabase
4. **Provider Selection**: Always Kimi for files (GLM lacks persistence)
5. **Upload Process**:
   - Supabase storage (persistent)
   - Provider SDK (session/persistent)
   - FileIdMapper stores bidirectional mappings
6. **Query Execution**: Provider-specific chat with file IDs

---

## 🔧 CORE INFRASTRUCTURE

### upload_file_with_provider()
**File:** `tools/supabase_upload.py`  
**Purpose:** Universal upload function with provider routing

**Workflow:**
1. Validate file path and user ID
2. Calculate SHA256 hash
3. Check for existing file (deduplication)
4. Route to provider-specific adapter
5. Store in Supabase + provider platform
6. Create FileIdMapper entry
7. Return unified response

**Provider Adapters:**
- `_kimi_upload_adapter()`: Kimi-specific upload logic
- `_glm_upload_adapter()`: GLM-specific upload logic

---

### upload_file_with_app_context()
**File:** `tools/supabase_upload.py`  
**Purpose:** Application-aware upload with validation (Phase A1)

**Features:**
- Validates application permissions
- Copies files to temp location if needed
- Processes through Supabase integration
- Cleans up temporary files
- Logs application access

**Usage:**
```python
upload_file_with_app_context(
    file_path="/external/app/file.txt",
    bucket="user-files",
    application_id="external-app",
    user_id="user123",
    provider="auto"
)
```

---

## 📈 PROVIDER COMPARISON

| Feature | Kimi (Moonshot) | GLM (Z.ai) |
|---------|----------------|------------|
| **File Persistence** | ✅ Persistent across sessions | ❌ Session-bound (24h expiry) |
| **Max File Size** | ✅ 100MB | ⚠️ 20MB |
| **Multiple Files** | ✅ Supported | ✅ Supported |
| **Async Operations** | ✅ Full support | ✅ Full support |
| **Deduplication** | ✅ SHA256-based | ✅ SHA256-based |
| **Best For** | Document analysis, file queries, long conversations | Quick text queries WITHOUT files |
| **File Operations** | ✅ Full support | ⚠️ SEVERELY LIMITED |

**Critical Constraint:** GLM files must be re-uploaded for each query due to lack of persistence.

---

## 🎯 DESIGN RATIONALE

### 1. Why Keep Deprecated Tools?

Legacy tools (`kimi_*`, `glm_*`) are maintained for:
- **Backward Compatibility**: Existing integrations may depend on them
- **Granular Control**: Advanced users might need direct provider access
- **Fallback Mechanisms**: Smart orchestrator uses them internally
- **Migration Path**: Allows gradual transition to unified interface

### 2. Why Always Use Kimi for Files?

**Critical Design Constraint:**
- **Kimi**: ✅ Persistent file uploads (files remain across sessions)
- **GLM**: ❌ Session-bound files (must re-upload each query)
- **Result**: `smart_file_query` ALWAYS routes to Kimi for file operations

Code evidence:
```python
# CRITICAL: Always use Kimi for file operations
# GLM requires re-uploading files for each query (no file persistence)
return "kimi"  # Always Kimi for file operations
```

### 3. Deduplication Architecture

**Three-Layer Deduplication:**

1. **SHA256 Hash Calculation**: File content fingerprinting
2. **Supabase Metadata Check**: `check_existing_file()` queries by hash
3. **FileIdMapper**: Tracks provider-specific IDs for same content

**Cross-Tool Deduplication:**
- All tools use `upload_file_with_provider()` as core mechanism
- Centralized `SupabaseUploadManager` handles deduplication
- Provider adapters store mappings in `file_id_mappings` table

---

## 🔍 TOOL INTERCONNECTIONS

### Relationship Diagram

```
smart_file_query (ORCHESTRATOR)
    ├── KimiUploadFilesTool (internal)
    ├── KimiChatWithFilesTool (internal)
    ├── GLMUploadFileTool (internal)
    └── GLMMultiFileChatTool (internal)
            ↓
    upload_file_with_provider() (CORE)
            ↓
    SupabaseUploadManager (STORAGE)
            ↓
    FileIdMapper (ID TRACKING)
```

### Dependency Chain

1. **smart_file_query** depends on:
   - `FileDeduplicationManager` (SHA256 deduplication)
   - `HybridSupabaseManager` (storage coordination)
   - `CrossPlatformPathHandler` (path normalization)
   - `KimiUploadFilesTool` (Kimi uploads)
   - `KimiChatWithFilesTool` (Kimi queries)

2. **Provider Tools** depend on:
   - `upload_file_with_provider()` (core upload)
   - `ModelProviderRegistry` (provider instantiation)
   - `SupabaseUploadManager` (persistent storage)

3. **Core Infrastructure** depends on:
   - `FileIdMapper` (bidirectional ID mapping)
   - `Supabase Client` (database operations)
   - `Provider SDKs` (Kimi/GLM APIs)

---

## ⚠️ EDGE CASES & LIMITATIONS

### 1. Async Initialization Race Condition
**Problem:** Multiple concurrent calls could initialize tools multiple times  
**Solution:** Added async lock to prevent race condition
```python
async with self._init_lock:
    if self._tools_initialized:
        return
```

### 2. GLM File Persistence Limitation
**Problem:** GLM files expire after 24 hours  
**Impact:** Session-bound nature requires re-upload for each query  
**Workaround:** System always routes files to Kimi

### 3. Path Security Constraints
**Problem:** Files must be within mounted directories  
**Pattern:** `/mnt/project/(EX-AI-MCP-Server|Personal_AI_Agent)/*`  
**Solution:** External files require copying to project first (Phase A1)

### 4. Timeout Handling
**Problem:** File analysis timeouts with large/complex files  
**Solution:** Exponential backoff retry mechanism + fallback to smaller chunks

---

## 🚀 USAGE RECOMMENDATIONS

### ✅ RECOMMENDED: Use smart_file_query

**For ALL file operations:**
```python
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code",
    provider="auto"  # Automatically selects Kimi for files
)
```

**Benefits:**
- ✅ Automatic deduplication (70-80% token savings)
- ✅ Intelligent provider selection
- ✅ Automatic fallback on failure
- ✅ Centralized Supabase tracking
- ✅ Single unified interface

### ⚠️ LEGACY: Direct Provider Tools

**Only use when:**
- You need granular control over provider selection
- You're maintaining existing integrations
- You need file management operations (kimi_manage_files)

---

## 📊 EXAI CONSULTATION INSIGHTS

**Consultation ID:** e403333f-eaf8-41d8-9249-347e2b2ebd3a  
**Model Used:** glm-4.6  
**Remaining Turns:** 19

**Key Insights from EXAI:**

1. **Architectural Strengths:**
   - Unified interface abstracts provider complexity
   - Intelligent deduplication saves resources
   - Graceful fallbacks handle provider failures
   - Async support throughout
   - Cross-platform path handling

2. **Potential Improvements:**
   - GLM caching strategy for session-bound files
   - Enhanced error context for debugging
   - Performance metrics tracking
   - File preview/thumbnail generation
   - Batch operations support

3. **Hidden Dependencies:**
   - `HybridSupabaseManager`: Central storage coordination
   - `FileIdMapper`: Bidirectional ID mapping
   - `CrossPlatformPathHandler`: Windows→Linux conversion
   - `ModelProviderRegistry`: Dynamic provider instantiation

---

## 🎓 CONCLUSION

The file tool architecture demonstrates thoughtful separation of concerns with clear abstraction layers. The **Unified Orchestrator Pattern** effectively hides provider complexity from end users while maintaining flexibility for advanced use cases.

**Critical Takeaway:** The GLM persistence limitation creates a strong bias toward Kimi for file operations, which is automatically handled by `smart_file_query`.

**Recommendation:** Use `smart_file_query` for ALL file operations unless you have specific requirements for direct provider access.

---

**Document Status:** ✅ COMPLETE  
**Next Steps:** Review and integrate into main documentation

