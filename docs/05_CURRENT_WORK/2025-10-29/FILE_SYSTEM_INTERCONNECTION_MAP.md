# File System Interconnection Map

**Date:** 2025-10-29  
**Purpose:** Complete mapping of ALL components involved in file upload operations  
**Status:** COMPREHENSIVE AUDIT

---

## 🎯 **OVERVIEW**

This document maps EVERY script, configuration, and component involved in the file upload system to ensure nothing is missed during consolidation.

---

## 📦 **1. MCP TOOL LAYER (User-Facing)**

### **Current Tools (To Be Consolidated)**

| Tool Name | File Location | Description | Registry Level |
|-----------|---------------|-------------|----------------|
| `kimi_upload_files` | `tools/providers/kimi/kimi_files.py` | Upload files to Kimi/Moonshot | advanced |
| `glm_upload_file` | `tools/providers/glm/glm_files.py` | Upload single file to GLM/Z.ai | advanced |
| `kimi_chat_with_files` | `tools/providers/kimi/kimi_files.py` | Chat with uploaded Kimi files | core |
| `kimi_manage_files` | `tools/providers/kimi/kimi_files.py` | Manage Kimi files (list/delete) | advanced |
| `glm_multi_file_chat` | `tools/providers/glm/glm_files.py` | Upload multiple files + chat (GLM) | advanced |

**Tool Classes:**
- `KimiUploadFilesTool` - Handles Kimi uploads
- `GLMUploadFileTool` - Handles GLM uploads
- `KimiChatWithFilesTool` - Handles Kimi file queries
- `KimiManageFilesTool` - Handles Kimi file management
- `GLMMultiFileChatTool` - Handles GLM multi-file chat

---

## 🔧 **2. TOOL INFRASTRUCTURE**

### **Tool Registry**

**File:** `tools/registry.py`

**Purpose:** Maps tool names to implementation classes

**Key Sections:**
```python
TOOL_MAP = {
    "kimi_upload_files": ("tools.providers.kimi.kimi_files", "KimiUploadFilesTool"),
    "glm_upload_file": ("tools.providers.glm.glm_files", "GLMUploadFileTool"),
    # ... etc
}

TOOL_VISIBILITY = {
    "kimi_upload_files": "advanced",
    "kimi_chat_with_files": "core",
    # ... etc
}
```

**Impact:** Need to add `smart_file_query` to both `TOOL_MAP` and `TOOL_VISIBILITY`

---

### **Tool Base Classes**

**Files:**
- `tools/shared/base_tool.py` - Base tool class
- `tools/shared/base_tool_file_handling.py` - File handling mixin
- `tools/shared/schema_builders.py` - Schema building utilities

**Purpose:** Provide common functionality for all tools

**Impact:** `smart_file_query` should inherit from these base classes

---

## 📝 **3. SYSTEM PROMPTS & GUIDANCE**

### **System Prompt Architecture**

**File:** `systemprompts/base_prompt.py`

**4-Tier Architecture:**
- Tier 0: Utility tools (no prompts)
- Tier 1: Core components (100% usage)
- Tier 2: Optional components (conditional)
- Tier 3: Provider-specific optimizations

**Imports:**
```python
from configurations.file_handling_guidance import FILE_PATH_GUIDANCE, FILE_UPLOAD_GUIDANCE
```

**Impact:** System prompts are centralized in `configurations/file_handling_guidance.py`

---

### **File Handling Guidance**

**File:** `configurations/file_handling_guidance.py`

**Purpose:** Centralized file handling guidance for all tools

**Key Components:**
- `FILE_PATH_GUIDANCE` - Docker path requirements
- `FILE_UPLOAD_GUIDANCE` - Upload strategy guidance

**Current Content:**
```python
FILE_PATH_GUIDANCE = """
🐳 DOCKER ENVIRONMENT CONTEXT
- System runs in Docker with /mnt/project/ mount
- Windows paths NOT accessible
- Only Linux paths work: /mnt/project/...
"""

FILE_UPLOAD_GUIDANCE = """
FILE UPLOAD STRATEGY
- Kimi: 100MB limit, multiple files
- GLM: 20MB limit, single file
- Automatic deduplication via SHA256
"""
```

**Impact:** Need to update with `smart_file_query` guidance

---

### **Chat-Specific Prompts**

**File:** `systemprompts/chat_components.py`

**Purpose:** Chat tool specific prompts (NOT used by other tools)

**Content:**
- `FILE_HANDLING_GUIDANCE` - File handling strategy
- `KIMI_FILE_UPLOAD_GUIDANCE` - Kimi-specific guidance

**Impact:** May need similar guidance for `smart_file_query`

---

## 🔐 **4. PATH VALIDATION & CONVERSION**

### **Path Validation (NEW)**

**File:** `utils/path_validation.py`

**Created:** 2025-10-28 (during security hardening)

**Functions:**
- `validate_upload_path(path: str) -> Tuple[bool, str]`
- `get_path_validation_examples() -> str`

**Features:**
- Windows path detection
- Relative path detection
- Mount point validation
- Path traversal protection
- Comprehensive error messages

**Impact:** `smart_file_query` MUST use this for all path validation

---

### **Cross-Platform Path Handler**

**File:** `utils/file/cross_platform.py`

**Purpose:** Windows ↔ Linux path conversion

**Key Class:** `CrossPlatformPathHandler`

**Methods:**
- `normalize_path()` - Convert Windows → Linux
- `resolve_path()` - Resolve relative paths

**Issue:** Converts to `/app/` instead of `/mnt/project/` when called through MCP

**Impact:** DO NOT use for MCP tool paths - use `validate_upload_path()` instead

---

## 💾 **5. FILE DEDUPLICATION**

### **Deduplication Manager**

**File:** `utils/file/deduplication.py`

**Class:** `FileDeduplicationManager`

**Key Methods:**
- `check_duplicate(path, provider)` - Check if file exists
- `register_new_file()` - Register new upload
- `increment_reference()` - Track usage
- `cleanup_unreferenced_files()` - Cleanup old files

**Features:**
- SHA256-based deduplication
- Reference counting
- Database-backed persistence
- In-memory cache integration
- Atomic operations

**Database Table:** `provider_file_uploads`

**Impact:** `smart_file_query` MUST use this for deduplication

---

### **File Cache**

**File:** `utils/file/cache.py`

**Class:** `FileCache`

**Purpose:** In-memory cache for file metadata

**Methods:**
- `sha256_file()` - Calculate SHA256
- `get()` / `set()` - Cache operations

**Impact:** Used internally by `FileDeduplicationManager`

---

## 🗄️ **6. SUPABASE INTEGRATION**

### **Hybrid Supabase Manager**

**File:** `src/storage/hybrid_supabase_manager.py`

**Class:** `HybridSupabaseManager`

**Purpose:** Unified interface for Supabase operations

**Key Methods:**
- `upload_file()` - Upload to Supabase Storage
- `execute_sql()` - Database operations
- `download_file()` - Download from storage

**Impact:** `smart_file_query` should use this for Supabase operations

---

### **Supabase Storage Manager**

**File:** `src/storage/supabase_client.py`

**Class:** `SupabaseStorageManager`

**Purpose:** Direct Supabase client operations

**Features:**
- Retry logic with exponential backoff
- Progress tracking
- Error handling
- Configurable timeouts

**Impact:** Used internally by `HybridSupabaseManager`

---

### **MCP Storage Adapter**

**File:** `src/file_management/mcp_storage_adapter.py`

**Class:** `MCPStorageAdapter`

**Purpose:** MCP-based storage operations (Phase B/C migration)

**Status:** Currently uses Python client (simulates MCP)

**Impact:** Future consideration - not needed for initial implementation

---

### **Supabase Schema**

**Table:** `provider_file_uploads`

**Columns:**
- `id` - UUID primary key
- `provider` - 'kimi' or 'glm'
- `provider_file_id` - Provider's file ID
- `supabase_file_id` - Supabase Storage file ID
- `sha256` - File hash for deduplication
- `filename` - Original filename
- `file_size_bytes` - File size
- `upload_status` - 'pending', 'completed', 'failed', 'deleted'
- `upload_method` - 'direct', 'supabase_gateway', etc.
- `reference_count` - Usage tracking
- `last_used` - Timestamp
- `created_at` / `updated_at` - Timestamps

**Migrations:**
- `20251017000000_add_provider_file_uploads.sql`
- `002_add_supabase_file_id_to_provider_uploads.sql`
- `20251022000000_enhance_file_schema.sql`

**Impact:** Schema is stable - no changes needed

---

## 🤖 **7. PROVIDER IMPLEMENTATIONS**

### **Provider Layer (src/providers/)**

**Kimi Provider:**
- `src/providers/kimi_files.py` - Low-level Kimi file operations
- `src/providers/kimi.py` - Kimi provider class
- `src/providers/async_kimi.py` - Async Kimi operations

**GLM Provider:**
- `src/providers/glm_files.py` - Low-level GLM file operations
- `src/providers/glm.py` - GLM provider class
- `src/providers/async_glm.py` - Async GLM operations

**Purpose:** Low-level provider SDK interactions

**Impact:** These are DIFFERENT from `tools/providers/` - they're the underlying implementation

---

### **Tool Provider Layer (tools/providers/)**

**Kimi Tools:**
- `tools/providers/kimi/kimi_files.py` - MCP tool implementations
  - `KimiUploadFilesTool`
  - `KimiChatWithFilesTool`
  - `KimiManageFilesTool`
  - Helper functions: `upload_via_supabase_gateway_kimi()`

**GLM Tools:**
- `tools/providers/glm/glm_files.py` - MCP tool implementations
  - `GLMUploadFileTool`
  - `GLMMultiFileChatTool`
  - Helper functions: `upload_via_supabase_gateway_glm()`

**Purpose:** MCP tool wrappers around provider implementations

**Impact:** `smart_file_query` will call these provider classes internally

---

## 📚 **8. DOCUMENTATION**

### **Architecture Docs**

**Location:** `docs/01_Core_Architecture/`
- `01_System_Overview.md` - System architecture
- `02_SDK_Integration.md` - SDK integration
- `03_Supabase_Audit_Trail.md` - Supabase tracking

---

### **Service Component Docs**

**Location:** `docs/02_Service_Components/`
- `06_System_Prompts.md` - System prompt architecture

---

### **Data Management Docs**

**Location:** `docs/03_Data_Management/`
- `03_File_Storage.md` - File storage architecture (CRITICAL)

**Key Content:**
- Upload workflow
- Deduplication strategy
- Supabase integration
- Provider comparison

**Impact:** Should be updated with `smart_file_query` workflow

---

### **Current Work Docs**

**Location:** `docs/05_CURRENT_WORK/2025-10-29/`
- `SMART_FILE_QUERY_IMPLEMENTATION_PLAN.md` - Implementation plan
- `EXAI_CONSULTATION_SUMMARY.md` - EXAI recommendations
- `FILE_UPLOAD_SYSTEM_COMPLETE.md` - Security hardening docs

---

## 🔍 **9. UTILITY FUNCTIONS**

### **File Utilities**

**Location:** `utils/file/`
- `cache.py` - File caching
- `cross_platform.py` - Path conversion
- `deduplication.py` - Deduplication manager
- `expansion.py` - Path expansion
- `helpers.py` - File helpers
- `operations.py` - File operations
- `reading.py` - File reading
- `security.py` - Security checks
- `size_validator.py` - Size validation
- `tokens.py` - Token estimation
- `types.py` - File type detection

**Impact:** Reuse these utilities in `smart_file_query`

---

### **Other Utilities**

- `utils/path_validation.py` - Path validation (NEW)
- `utils/progress.py` - Progress tracking
- `utils/observability.py` - Observability helpers

---

## ⚙️ **10. CONFIGURATION**

### **Environment Variables**

**File:** `.env` / `.env.docker`

**File Upload Related:**
- `KIMI_API_KEY` - Kimi/Moonshot API key
- `GLM_API_KEY` - GLM/Z.ai API key
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase service key
- `TEST_FILES_DIR` - Allowed upload directories

**Impact:** No changes needed

---

### **Docker Configuration**

**File:** `docker-compose.yml`

**Volume Mounts:**
```yaml
volumes:
  - c:\Project:/mnt/project:ro
```

**Impact:** This is WHY paths must be `/mnt/project/...`

---

## 🧪 **11. TESTING**

### **Test Scripts**

- `scripts/test_file_upload_system.py` - File upload validation
- `scripts/test_integration_real_upload.py` - Integration tests

**Impact:** Need to create tests for `smart_file_query`

---

## ✅ **12. CRITICAL DEPENDENCIES**

### **What `smart_file_query` MUST Use:**

1. ✅ `utils/path_validation.py` - Path validation
2. ✅ `utils/file/deduplication.py` - Deduplication
3. ✅ `src/storage/hybrid_supabase_manager.py` - Supabase operations
4. ✅ `src/providers/kimi.py` / `src/providers/glm.py` - Provider operations
5. ✅ `tools/registry.py` - Tool registration

### **What `smart_file_query` Should NOT Use:**

1. ❌ `utils/file/cross_platform.py` - Path conversion (broken for MCP)
2. ❌ `src/file_management/mcp_storage_adapter.py` - Not needed yet (Phase C)

---

## 🚨 **13. GOTCHAS & HIDDEN DEPENDENCIES**

### **1. Duplicate Provider Classes**

**Issue:** There are TWO sets of provider files:
- `src/providers/kimi_files.py` - Low-level SDK operations
- `tools/providers/kimi/kimi_files.py` - MCP tool wrappers

**Resolution:** Use `tools/providers/` for MCP tools, `src/providers/` for internal operations

---

### **2. Path Conversion Trap**

**Issue:** `CrossPlatformPathHandler` converts to `/app/` instead of `/mnt/project/`

**Resolution:** Use `validate_upload_path()` instead

---

### **3. System Prompt Centralization**

**Issue:** File handling guidance is in `configurations/file_handling_guidance.py`, NOT in tool files

**Resolution:** Update centralized guidance, not individual tool prompts

---

### **4. Tool Registry Visibility**

**Issue:** Tools have visibility levels ("core" vs "advanced")

**Resolution:** `smart_file_query` should be "core" (primary interface)

---

## 📊 **SUMMARY**

**Total Components Identified:** 50+

**Critical Path:**
1. Path Validation → Deduplication → Supabase Upload → Provider Upload → Query
2. Tool Registry → System Prompts → MCP Tool → Provider → Database

**Next Steps:**
1. Consult EXAI with this complete map
2. Validate no missing components
3. Get implementation strategy
4. Proceed with implementation


