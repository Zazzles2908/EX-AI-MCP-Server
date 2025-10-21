# Kimi File Tools Architectural Redesign - 2025-10-17

**Date:** 2025-10-17 (Melbourne/Australia AEDT)  
**Status:** 🚧 IMPLEMENTATION PLANNED  
**EXAI Consultation ID:** fbb0b93d-e9c3-42ba-b967-3b52e454e38a  
**Confidence:** Very High

---

## 🎯 Problem Statement

**User Feedback (Verbatim):**
> "The fundamental core actually sounds pretty bad dont you believe, the way those two functions are designed.
> 
> Like in my head it should be for only kimi models
> function 1 - Just purely upload
> function 2 - to reference that file and ask only kimi models information about that
> function 3 - should be like all the other features, like delete, search etc etc."

**Current Issues:**
1. `kimi_upload_and_extract` - Dual purpose (upload + extract content) → Massive truncated output
2. `kimi_multi_file_chat` - Dual purpose (upload + chat) → MCP timeout after 8 seconds
3. Confusing tool purposes
4. No clean file ID management
5. No file lifecycle management

---

## 🏗️ Proposed Architecture

### **Three Single-Purpose Tools:**

#### **Tool 1: `kimi_upload_files` (Upload Only)**
```python
kimi_upload_files(
    files: List[str],  # File paths
    purpose: str = "file-extract"
) -> List[Dict[str, Any]]  # [{filename, file_id, size_bytes, upload_timestamp}]
```

**Purpose:** Upload files to Moonshot, return file IDs only  
**Output:** Clean JSON array with file metadata  
**No Content Extraction:** Just IDs for later reference  
**Fast:** ~3-5 seconds for 10 files (parallel uploads)

---

#### **Tool 2: `kimi_chat_with_files` (Chat with File IDs)**
```python
kimi_chat_with_files(
    prompt: str,
    file_ids: List[str],  # Previously uploaded file IDs
    model: str = "kimi-k2-0905-preview",
    temperature: float = 0.3
) -> Dict[str, Any]  # {model, content}
```

**Purpose:** Chat with previously uploaded files  
**Input:** File IDs (not paths)  
**No Upload Overhead:** Files already on Moonshot servers  
**Fast:** ~5-15 seconds depending on complexity

---

#### **Tool 3: `kimi_manage_files` (File Management)**
```python
kimi_manage_files(
    operation: str,  # "list", "delete", "get_info"
    file_id: Optional[str] = None,  # Required for delete/get_info
    limit: int = 100  # For list operation
) -> Dict[str, Any]  # Operation-specific response
```

**Purpose:** Manage uploaded files  
**Operations:**
- `list` - List all uploaded files
- `delete` - Delete specific file by ID
- `get_info` - Get metadata for specific file

**Fast:** <2 seconds for all operations

---

## 📊 Architecture Comparison

### **BEFORE (Flawed):**
```
User → kimi_upload_and_extract → Upload + Extract → Massive Output (TRUNCATED!)
User → kimi_multi_file_chat → Upload + Extract + Chat → TIMEOUT after 8s!
```

### **AFTER (Clean):**
```
User → kimi_upload_files → Upload Only → File IDs
User → kimi_chat_with_files(file_ids) → Chat → Response
User → kimi_manage_files("list") → File List
User → kimi_manage_files("delete", file_id) → Deleted
```

---

## 🔧 Implementation Plan

### **Phase 1: Create New Tools (2-3 hours)**

**File:** `tools/providers/kimi/kimi_files.py`

**Tasks:**
1. ✅ Create `KimiUploadFilesTool` class
   - Upload files in parallel (max 3 concurrent)
   - Return file IDs with metadata
   - Use existing FileCache for SHA256 deduplication
   - No content extraction

2. ✅ Create `KimiChatWithFilesTool` class
   - Accept file_ids parameter
   - Format messages with file IDs in system role
   - Call Kimi chat completion
   - Return response

3. ✅ Create `KimiManageFilesTool` class
   - Implement list operation
   - Implement delete operation
   - Implement get_info operation
   - Use existing kimi_files_cleanup.py utilities

---

### **Phase 2: Supabase Integration (1 hour)**

**Table:** `kimi_file_uploads`

**Schema:**
```sql
CREATE TABLE kimi_file_uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id TEXT NOT NULL,  -- Moonshot file ID
    filename TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'KIMI',
    file_size_bytes BIGINT,
    upload_timestamp TIMESTAMPTZ DEFAULT NOW(),
    last_used TIMESTAMPTZ DEFAULT NOW(),
    purpose TEXT DEFAULT 'file-extract',
    UNIQUE(sha256, provider)
);

CREATE INDEX idx_kimi_file_uploads_file_id ON kimi_file_uploads(file_id);
CREATE INDEX idx_kimi_file_uploads_sha256 ON kimi_file_uploads(sha256);
CREATE INDEX idx_kimi_file_uploads_last_used ON kimi_file_uploads(last_used);
```

**Tasks:**
1. ✅ Create Supabase migration
2. ✅ Implement tracking in `kimi_upload_files`
3. ✅ Implement auto-cleanup (>30 days unused)
4. ✅ Update last_used on chat operations

---

### **Phase 3: Deprecation (30 mins)**

**Tasks:**
1. ✅ Add deprecation warnings to `kimi_upload_and_extract`
2. ✅ Add deprecation warnings to `kimi_multi_file_chat`
3. ✅ Update tool registry
4. ✅ Update system prompts with migration guidance

**Deprecation Message:**
```
⚠️ DEPRECATED: This tool will be removed in a future release.
Use kimi_upload_files + kimi_chat_with_files instead.
See docs/MIGRATION_GUIDE.md for details.
```

---

### **Phase 4: Documentation (1 hour)**

**Files to Update:**
1. ✅ `docs/03_API_REFERENCE/02_API_REFERENCE/KIMI_API_REFERENCE.md`
2. ✅ `docs/04_GUIDES/API_SDK_REFERENCE.md`
3. ✅ `docs/system-reference/providers/kimi.md`
4. ✅ Create `docs/05_CURRENT_WORK/04_MIGRATION_GUIDES/KIMI_FILE_TOOLS_MIGRATION.md`
5. ✅ Update `docs/05_CURRENT_WORK/05_PROJECT_STATUS/KIMI_TOOL_USAGE_LESSONS_2025-10-17.md`

---

## 🎯 Edge Cases & Considerations

### **1. File ID Persistence**
- Moonshot files persist on their servers
- Supabase tracks uploads for reuse
- Auto-cleanup after 30 days unused
- Manual cleanup via `kimi_manage_files("delete")`

### **2. Backward Compatibility**
- Keep old tools for 1-2 releases
- Add deprecation warnings
- Provide migration guide
- Update all examples

### **3. File ID Format**
- Moonshot returns IDs like "d3ot38amisdua6g4is7g"
- Pass in system messages: `{"role": "system", "content": file_id}`
- Kimi automatically loads file content

### **4. MCP Timeout Safety**
- Upload: 3-5 seconds for 10 files (parallel)
- Chat: 5-15 seconds (no upload overhead)
- Management: <2 seconds (quick operations)
- All within 8-10 second MCP timeout

### **5. Caching Strategy**
- FileCache already exists (utils/file/cache.py)
- Check cache before upload (by SHA256)
- Return cached file_id if exists
- Supabase tracks all uploads

---

## 📝 Usage Examples

### **Example 1: Upload and Chat**
```python
# Step 1: Upload files
result = kimi_upload_files(
    files=["docs/README.md", "docs/DESIGN_INTENT.md"]
)
# Returns: [
#   {"filename": "README.md", "file_id": "abc123", "size_bytes": 5000},
#   {"filename": "DESIGN_INTENT.md", "file_id": "def456", "size_bytes": 8000}
# ]

# Step 2: Chat with files
response = kimi_chat_with_files(
    prompt="What's the main purpose of this project?",
    file_ids=["abc123", "def456"],
    model="kimi-k2-0905-preview"
)
# Returns: {"model": "kimi-k2-0905-preview", "content": "The project..."}
```

### **Example 2: Iterative Analysis**
```python
# Upload once
files = kimi_upload_files(files=["doc1.md", "doc2.md", "doc3.md"])
file_ids = [f["file_id"] for f in files]

# Ask multiple questions
q1 = kimi_chat_with_files("What's missing?", file_ids)
q2 = kimi_chat_with_files("What redundancies exist?", file_ids)
q3 = kimi_chat_with_files("What should be archived?", file_ids)
```

### **Example 3: File Management**
```python
# List all uploaded files
files = kimi_manage_files(operation="list", limit=50)

# Get info about specific file
info = kimi_manage_files(operation="get_info", file_id="abc123")

# Delete old file
result = kimi_manage_files(operation="delete", file_id="abc123")
```

---

## ✅ Success Criteria

**Before Implementation:**
- ❌ Dual-purpose tools causing confusion
- ❌ Massive truncated outputs
- ❌ MCP timeouts after 8 seconds
- ❌ No file lifecycle management
- ❌ Re-upload files for each question

**After Implementation:**
- ✅ Three single-purpose tools
- ✅ Clean file ID outputs
- ✅ No MCP timeouts
- ✅ Supabase file tracking
- ✅ Upload once, query many times
- ✅ File management capabilities

---

## 🚀 Next Steps

1. **Implement Phase 1** - Create new tools
2. **Test with real files** - Verify MCP timeout compliance
3. **Implement Phase 2** - Supabase integration
4. **Implement Phase 3** - Deprecation warnings
5. **Implement Phase 4** - Documentation updates
6. **User Testing** - Retry markdown reorganization task

---

**Status:** Ready for implementation! 🎯

