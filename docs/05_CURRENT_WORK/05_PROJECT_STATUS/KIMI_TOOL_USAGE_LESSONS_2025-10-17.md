# Kimi Tool Usage Lessons Learned - 2025-10-17

**UPDATE 2025-10-17:** Tools have been completely redesigned! See [Kimi Tools Redesign](#kimi-tools-redesign-2025-10-17) below.

---

**Date:** 2025-10-17 (Melbourne/Australia AEDT)  
**Status:** ✅ LESSONS DOCUMENTED  
**Kimi Consultation ID:** 53bf5b39-82ad-4014-bd71-36e91ed79215

---

## 🎯 What Happened

Attempted to use Kimi file upload tools for comprehensive documentation analysis but encountered:
1. **Massive truncated output** from `kimi_upload_and_extract`
2. **8-second timeout cancellation** on `kimi_multi_file_chat`
3. **Background API completion** 56 seconds after cancellation

---

## 🔍 Root Cause Analysis (via Kimi K2)

### **Issue #1: Tool Misuse Pattern**

**What I Did Wrong:**
- Used `kimi_upload_and_extract` expecting it to just upload files for later use
- Got back FULL extracted content of all 8 files as system messages
- This caused massive output that was truncated by Augment Code

**What I Should Have Done:**
- Understood that `kimi_upload_and_extract` is for **immediate content extraction**, not pre-uploading

---

### **Issue #2: MCP Timeout vs API Completion**

**What Happened:**
```
16:18:53 - kimi_multi_file_chat started
16:19:01 - TOOL_CANCELLED (8 seconds elapsed) ← MCP timeout
16:19:56 - Kimi API completed (56 seconds total) ← API kept running!
```

**Root Cause:**
- MCP server timeout (8-10 seconds) kills the tool call
- But the underlying Kimi API request continues in background
- Cancellation only affects MCP layer, not Kimi service

---

## 📚 Kimi Tool Comparison

### **`kimi_upload_and_extract`**
- **Purpose:** Upload files AND immediately extract their content as text
- **Output:** Returns full extracted content of all files
- **Use Case:** When you want file content as text in current context
- **NOT For:** Pre-uploading files to reference later
- **Limitation:** Output can be massive (causes truncation)

### **`kimi_multi_file_chat`**
- **Purpose:** Upload files AND immediately chat about them
- **Output:** Returns conversation response
- **Use Case:** Single-turn file analysis with questions
- **Limitation:** Must complete within MCP timeout (~8-10 seconds)

### **`kimi_chat_with_tools`**
- **Purpose:** Chat with tool calling capabilities
- **Output:** Conversation response with tool results
- **Use Case:** Complex multi-step analysis with tool usage
- **Limitation:** Requires file IDs if referencing files

---

## ✅ Correct Workflow Patterns

### **Pattern 1: Simple Quick Analysis (< 8 seconds)**

**Use:** `kimi_multi_file_chat` directly

```python
kimi_multi_file_chat(
    files=["file1.md", "file2.md"],
    prompt="Quick focused question that completes fast",
    model="kimi-k2-0905-preview"
)
```

**Pros:**
- Single call
- Simple workflow
- No file ID management

**Cons:**
- Must complete within timeout
- Can't do complex analysis
- Re-uploads files each time

---

### **Pattern 2: Complex Analysis (> 8 seconds)**

**Phase 1: Upload and Get File IDs**
```python
# Upload files and get IDs only (no content extraction)
result = kimi_upload_and_extract(
    files=["file1.md", "file2.md"],
    purpose="file-extract"
)

# Extract file IDs from result
file_ids = [msg["_file_id"] for msg in result if "_file_id" in msg]
```

**Phase 2: Chat with File IDs**
```python
# Use regular chat with file IDs in context
chat(
    prompt="Analyze the uploaded files focusing on X, Y, Z",
    files=file_ids,  # Reference by ID, not path
    model="kimi-k2-0905-preview"
)
```

**Pros:**
- Upload once, query multiple times
- No timeout issues (chat is separate from upload)
- Efficient token usage

**Cons:**
- Two-phase workflow
- Need to manage file IDs
- More complex

---

### **Pattern 3: Iterative Analysis**

**Step 1: Upload Once**
```python
file_ids = upload_files_get_ids(["doc1.md", "doc2.md", "doc3.md"])
```

**Step 2: Ask Multiple Questions**
```python
# Question 1
chat(prompt="What's missing in the documentation?", files=file_ids)

# Question 2
chat(prompt="What redundancies exist?", files=file_ids)

# Question 3
chat(prompt="What should be archived?", files=file_ids)
```

**Pros:**
- Upload once, ask many questions
- No re-upload overhead
- Efficient for exploration

**Cons:**
- Requires file ID caching
- More setup complexity

---

## 🚫 What NOT To Do

### **DON'T: Use `kimi_upload_and_extract` for Pre-Upload**
```python
# ❌ WRONG - This extracts full content!
result = kimi_upload_and_extract(files=["huge_file.md"])
# Result: Massive truncated output
```

### **DON'T: Use `kimi_multi_file_chat` for Complex Analysis**
```python
# ❌ WRONG - Will timeout after 8 seconds!
kimi_multi_file_chat(
    files=["file1.md", "file2.md", "file3.md"],
    prompt="Comprehensive analysis with 10 detailed questions..."
)
# Result: TOOL_CANCELLED after 8 seconds
```

### **DON'T: Ignore MCP Timeout Constraints**
```python
# ❌ WRONG - Assuming long-running analysis will complete
kimi_multi_file_chat(
    files=many_files,
    prompt=very_complex_prompt
)
# Result: Timeout, but API keeps running in background (wasted tokens!)
```

---

## ✅ What TO Do

### **DO: Break Complex Analysis into Chunks**
```python
# ✅ CORRECT - Multiple focused questions
kimi_multi_file_chat(files=files, prompt="Question 1: Organization gaps?")
kimi_multi_file_chat(files=files, prompt="Question 2: Missing docs?")
kimi_multi_file_chat(files=files, prompt="Question 3: Redundancies?")
```

### **DO: Use File IDs for Iterative Work**
```python
# ✅ CORRECT - Upload once, query many times
file_ids = upload_and_cache(files)
chat(prompt="Question 1", files=file_ids)
chat(prompt="Question 2", files=file_ids)
```

### **DO: Respect Timeout Constraints**
```python
# ✅ CORRECT - Keep prompts focused and quick
kimi_multi_file_chat(
    files=files,
    prompt="Single focused question with clear scope"
)
```

---

## 📊 Timeout Hierarchy

**MCP Server Timeout:** ~8-10 seconds (Augment Code limit)  
**Tool Timeout:** 180 seconds (EXAI-WS configuration)  
**Provider Timeout:** 180 seconds (Kimi API)  
**Daemon Timeout:** 270 seconds (WebSocket daemon)

**Critical Insight:** MCP timeout is the BOTTLENECK (8-10s), not tool/provider timeouts!

---

## 🎯 Recommended Approach for Documentation Analysis

### **Option A: Multiple Focused Questions (Recommended)**

```python
# Question 1: Organization
kimi_multi_file_chat(
    files=key_docs,
    prompt="Analyze documentation organization. What's missing?"
)

# Question 2: Gaps
kimi_multi_file_chat(
    files=key_docs,
    prompt="What critical documentation gaps exist?"
)

# Question 3: Redundancies
kimi_multi_file_chat(
    files=key_docs,
    prompt="What redundancies should be consolidated?"
)
```

**Pros:**
- Stays within timeout
- Focused answers
- Easy to implement

**Cons:**
- Multiple API calls
- More token usage
- Less holistic view

---

### **Option B: File ID Caching (Advanced)**

```python
# Phase 1: Upload and cache
file_ids = upload_docs_to_kimi([
    "README.md",
    "DEPENDENCY_MAP.md",
    "DESIGN_INTENT.md",
    # ... more files
])

# Phase 2: Iterative analysis
chat(prompt="Comprehensive analysis question 1", files=file_ids)
chat(prompt="Comprehensive analysis question 2", files=file_ids)
chat(prompt="Comprehensive analysis question 3", files=file_ids)
```

**Pros:**
- Upload once
- Unlimited questions
- Efficient tokens

**Cons:**
- Requires implementation
- File ID management
- More complex

---

## 🔧 Implementation Recommendations

### **Immediate (Today):**
1. ✅ Use `kimi_multi_file_chat` with focused questions
2. ✅ Break complex analysis into 3-5 separate questions
3. ✅ Keep each question focused and quick (<8 seconds)

### **Short Term (Next Session):**
1. ⏭️ Implement file ID caching helper function
2. ⏭️ Create wrapper for upload-once-query-many pattern
3. ⏭️ Document file ID lifecycle management

### **Medium Term (Future):**
1. ⏭️ Build file upload cache in Supabase
2. ⏭️ Implement automatic file ID reuse
3. ⏭️ Create documentation analysis workflow templates

---

## 📝 Key Takeaways

1. **`kimi_upload_and_extract` ≠ Pre-upload**
   - It extracts full content immediately
   - Use only when you want content as text
   - Not for file ID caching

2. **MCP Timeout is the Bottleneck**
   - 8-10 seconds max for tool calls
   - API continues in background after cancellation
   - Must design workflows around this limit

3. **Two-Tier Strategy Still Applies**
   - Tier 1: Use EXAI tools for investigation
   - Tier 2: Consult Kimi for validation/analysis
   - But respect timeout constraints!

4. **Break Complex Analysis into Chunks**
   - Multiple focused questions > One comprehensive question
   - Stays within timeout
   - More manageable responses

---

## 🎉 Success Metrics

**Before (What I Did Wrong):**
- ❌ Massive truncated output
- ❌ 8-second timeout cancellation
- ❌ Wasted API call (ran for 56s in background)
- ❌ No useful results

**After (What I Should Do):**
- ✅ Focused questions with complete responses
- ✅ No timeouts
- ✅ Efficient token usage
- ✅ Actionable insights

---

## 🚀 Kimi Tools Redesign (2025-10-17)

**Status:** ✅ IMPLEMENTED
**EXAI Consultation ID:** 3d505bba-a1b7-41d9-b12d-d527fe6b84ff

Based on user feedback and EXAI consultation, the Kimi file tools have been completely redesigned with single-purpose architecture.

---

### **NEW TOOL ARCHITECTURE**

#### **Tool 1: `kimi_upload_files`** (Upload Only)
```python
kimi_upload_files(files=["doc1.md", "doc2.md"])
# Returns: [{"filename": "doc1.md", "file_id": "abc123", "size_bytes": 5000}, ...]
```

**Purpose:** Upload files and return file IDs only (no content extraction)
**Output:** JSON array with file metadata
**Features:**
- SHA256-based deduplication (cached uploads)
- Parallel uploads (configurable)
- Size limits and validation
- Supabase tracking integration

---

#### **Tool 2: `kimi_chat_with_files`** (Chat with Files)
```python
kimi_chat_with_files(
    prompt="Analyze these files",
    file_ids=["abc123", "def456"],
    model="kimi-k2-0905-preview"
)
# Returns: {"model": "kimi-k2-0905-preview", "content": "..."}
```

**Purpose:** Chat with previously uploaded files using their IDs
**Output:** Kimi's response
**Features:**
- References files by ID (no re-upload)
- Configurable model and temperature
- Updates last_used timestamp in Supabase

---

#### **Tool 3: `kimi_manage_files`** (File Management)
```python
# List all files
kimi_manage_files(operation="list", limit=100)

# Delete specific file
kimi_manage_files(operation="delete", file_id="abc123")

# Cleanup all files
kimi_manage_files(operation="cleanup_all", dry_run=True)

# Cleanup orphaned files (not in Supabase)
kimi_manage_files(operation="cleanup_orphaned")

# Cleanup expired files (unused 30+ days)
kimi_manage_files(operation="cleanup_expired")
```

**Purpose:** Manage file lifecycle
**Operations:**
- `list` - Show all uploaded files
- `delete` - Remove specific file
- `cleanup_all` - Delete ALL files (with dry-run)
- `cleanup_orphaned` - Remove files not tracked in Supabase
- `cleanup_expired` - Remove files unused for 30+ days

---

### **SUPABASE INTEGRATION**

**New Table: `provider_file_uploads`**
```sql
CREATE TABLE provider_file_uploads (
  id UUID PRIMARY KEY,
  provider TEXT NOT NULL,  -- 'kimi', 'glm'
  provider_file_id TEXT NOT NULL,
  sha256 TEXT,
  filename TEXT,
  file_size_bytes INTEGER,
  last_used TIMESTAMP WITH TIME ZONE,
  upload_status TEXT,  -- 'pending', 'completed', 'failed', 'deleted'
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  UNIQUE(provider, provider_file_id)
);
```

**Features:**
- Tracks all provider uploads
- Supports multiple providers (Kimi, GLM)
- SHA256 deduplication
- Last used tracking for cleanup
- Bidirectional sync (Supabase ↔ Moonshot)

---

### **CORRECT WORKFLOW (NEW TOOLS)**

#### **Pattern 1: Upload Once, Query Many**
```python
# Step 1: Upload files
result = kimi_upload_files(files=["doc1.md", "doc2.md", "doc3.md"])
file_ids = [f["file_id"] for f in result]

# Step 2: Ask multiple questions
kimi_chat_with_files(prompt="Question 1?", file_ids=file_ids)
kimi_chat_with_files(prompt="Question 2?", file_ids=file_ids)
kimi_chat_with_files(prompt="Question 3?", file_ids=file_ids)
```

**Benefits:**
- ✅ Upload once, query unlimited times
- ✅ No timeout issues (upload and chat are separate)
- ✅ Efficient token usage
- ✅ Automatic deduplication via SHA256

---

#### **Pattern 2: File Lifecycle Management**
```python
# List all uploaded files
files = kimi_manage_files(operation="list")

# Preview cleanup (dry-run)
report = kimi_manage_files(operation="cleanup_all", dry_run=True)

# Execute cleanup
result = kimi_manage_files(operation="cleanup_all", dry_run=False)
```

**Benefits:**
- ✅ Full visibility into uploaded files
- ✅ Safe cleanup with dry-run preview
- ✅ Automatic orphan detection
- ✅ Automatic expiration cleanup

---

### **ENVIRONMENT CONFIGURATION**

**New Variables (added to `.env.example` and `.env.docker`):**
```bash
KIMI_FILES_MAX_SIZE_MB=20              # Max file size (MB)
KIMI_FILES_PARALLEL_UPLOADS=true       # Enable parallel uploads
KIMI_FILES_MAX_PARALLEL=3              # Max concurrent uploads
KIMI_FILES_UPLOAD_TIMEOUT_SECS=90      # Upload timeout
KIMI_FILES_FETCH_TIMEOUT_SECS=25       # Fetch timeout
KIMI_FILES_MAX_COUNT=0                 # Max files per upload (0 = no limit)
KIMI_FILES_BEHAVIOR_ON_OVERSIZE=skip   # Behavior: skip or fail
KIMI_FILES_FETCH_RETRIES=3             # Retry count
KIMI_FILES_FETCH_BACKOFF=0.8           # Backoff multiplier
KIMI_FILES_FETCH_INITIAL_DELAY=0.5     # Initial delay (seconds)
KIMI_MF_CHAT_TIMEOUT_SECS=180          # Chat timeout
```

---

### **MIGRATION NOTES**

**Old Tools (REMOVED):**
- ❌ `kimi_upload_and_extract` - Deleted
- ❌ `kimi_multi_file_chat` - Deleted

**New Tools (ADDED):**
- ✅ `kimi_upload_files` - Upload only
- ✅ `kimi_chat_with_files` - Chat with files
- ✅ `kimi_manage_files` - File management

**Breaking Changes:**
- Old tools no longer available
- Must use new two-phase workflow (upload → chat)
- File IDs must be managed explicitly

**Benefits:**
- ✅ No more confusion about tool purposes
- ✅ No more massive truncated outputs
- ✅ No more timeout issues
- ✅ Upload once, query many times
- ✅ Full file lifecycle management
- ✅ Supabase integration for tracking

---

**Status:** Tools redesigned and implemented! Ready for testing after Docker restart. 🎯

