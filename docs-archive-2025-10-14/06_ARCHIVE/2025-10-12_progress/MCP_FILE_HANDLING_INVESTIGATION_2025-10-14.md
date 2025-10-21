# MCP File Handling Investigation
**Date:** 2025-10-14 (14th October 2025)  
**Issue:** Claude MCP clients can't provide absolute file paths  
**Status:** Investigation Complete - Solution Designed  
**Priority:** HIGH

---

## 🎯 User Report

**Problem:**
> "The exai tool requires full absolute file paths, not just filenames. I need to figure out the absolute paths to these files. However, since these are uploaded files to Claude, I don't actually have access to their absolute file system paths.
> 
> Instead, I should:
> 1. Read the Excel file content using window.fs.readFile in the analysis tool
> 2. Already have the PDF content in the documents
> 3. Use exai chat with the actual data extracted, not file paths"

**User's Workaround:**
- Extract file content manually in Claude
- Compile information into text
- Use exai chat with compiled data instead of file references

**Problem:** This defeats the purpose of EX-AI's file handling capabilities!

---

## 🔍 Investigation Results

### Root Cause Analysis

**1. Architecture Mismatch:**
- **MCP Clients (Claude):** Provide file *content* without absolute paths
- **EX-AI:** Requires absolute file *paths* to upload to Kimi/GLM APIs
- **Gap:** No bridge between content-based and path-based approaches

**2. Current EX-AI File Handling:**

```python
# src/providers/kimi_files.py
def upload_file(client: Any, file_path: str, purpose: str = "file-extract") -> str:
    """Upload a local file to Moonshot (Kimi) and return file_id."""
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Upload file to Kimi API
    with p.open("rb") as f:
        # ... upload logic
```

**Problem:** Requires `file_path` to exist on disk

**3. MCP Protocol:**
- MCP has "Resources" concept for exposing data to LLMs
- Resources can be text or binary content
- Resources identified by URIs (e.g., `file:///path/to/file`)
- **MCP clients can upload file content without providing paths**

**4. Current Gap:**
- EX-AI doesn't implement MCP Resources protocol
- EX-AI only accepts file paths, not file content
- No temporary file storage for MCP-uploaded content

---

## ✅ Solution Design

### Recommended: Temporary File Bridge

**Concept:** Create temporary files from MCP content, then use existing upload logic

**Why This Approach:**
1. ✅ **Minimal Changes:** Works with existing upload logic
2. ✅ **Backward Compatible:** Existing file paths still work
3. ✅ **File Caching Works:** Temp files have paths, so caching logic unchanged
4. ✅ **Easy to Test:** Can test with both paths and content
5. ✅ **Cleanup Handled:** Automatic temp file cleanup after use

**Architecture:**

```
MCP Client (Claude)
    ↓
    Provides file content (base64 or bytes)
    ↓
MCPFileBridge
    ↓
    Creates temporary file with content
    ↓
    Returns absolute path to temp file
    ↓
Existing EX-AI Upload Logic
    ↓
    Uploads temp file to Kimi/GLM
    ↓
    Returns file_id
    ↓
MCPFileBridge Cleanup
    ↓
    Removes temporary file
```

**Key Components:**

1. **MCPFileBridge Class:**
   - Processes file parameters (paths or content)
   - Creates temporary files for content
   - Tracks temp files for cleanup
   - Cleans up after tool execution

2. **Integration Points:**
   - `src/server/handlers/request_handler.py` - Process files before tool execution
   - `src/server/handlers/request_handler.py` - Cleanup after tool execution

3. **Supported Input Formats:**
   - Absolute file paths (existing)
   - Relative file paths (existing)
   - Base64-encoded content (new)
   - Raw bytes content (new)
   - Mixed (paths + content) (new)

---

## 📊 Implementation Plan

### Phase 1: Core Bridge (1-2 hours)
- [x] Design MCPFileBridge class
- [ ] Create `src/server/handlers/mcp_file_bridge.py`
- [ ] Implement file processing logic
- [ ] Add unit tests

### Phase 2: Integration (1 hour)
- [ ] Integrate bridge into `request_handler.py`
- [ ] Add cleanup logic after tool execution
- [ ] Test with existing file-based tools

### Phase 3: MCP Client Support (1 hour)
- [ ] Update documentation for MCP clients
- [ ] Add examples of file content upload
- [ ] Test with Claude MCP client

### Phase 4: Testing & Validation (1 hour)
- [ ] Test with file paths (existing behavior)
- [ ] Test with base64 content
- [ ] Test with binary content
- [ ] Test cleanup logic
- [ ] Test mixed content (paths + content)

**Total Estimated Time:** 4-5 hours

---

## 🧪 Test Cases

### Test Case 1: Existing Behavior (File Paths)
```python
# Should work unchanged
arguments = {
    "files": ["/absolute/path/to/file.pdf", "relative/path/to/file.txt"]
}
```

**Expected:** Files uploaded normally, no changes

### Test Case 2: Base64 Content
```python
# New: MCP client provides base64
arguments = {
    "files": [
        {
            "filename": "document.pdf",
            "content": "JVBERi0xLjQK..."  # base64 PDF content
        }
    ]
}
```

**Expected:** 
1. Temp file created with content
2. File uploaded to Kimi/GLM
3. Temp file cleaned up after use

### Test Case 3: Mixed Content
```python
# Mix of paths and content
arguments = {
    "files": [
        "/path/to/existing/file.pdf",
        {"filename": "uploaded.xlsx", "content": "<base64>"}
    ]
}
```

**Expected:**
1. Existing file uploaded normally
2. Temp file created for content
3. Both files uploaded
4. Temp file cleaned up

---

## 📚 Files Analyzed

### Provider Upload Functions
1. `src/providers/kimi_files.py` - Kimi file upload (requires path)
2. `src/providers/glm_files.py` - GLM file upload (requires path)
3. `src/providers/kimi.py` - Kimi provider wrapper
4. `src/providers/glm.py` - GLM provider wrapper

### Request Handling
1. `src/server/handlers/request_handler.py` - Main request handler
2. `src/server/handlers/request_handler_execution.py` - File size validation
3. `src/server/handlers/request_handler_post_processing.py` - File auto-continue

### Tool Integration
1. `tools/chat.py` - Chat tool with file support
2. `tools/providers/kimi/kimi_upload.py` - Kimi multi-file upload
3. `tools/shared/base_tool_file_handling.py` - Base file handling

### File Utilities
1. `utils/file/reading.py` - File reading utilities
2. `utils/file/cache.py` - File caching (SHA256-based)
3. `utils/file/helpers.py` - File helper functions

---

## 🎯 Key Insights

### 1. File Caching Implications
**Current:** File cache uses SHA256 of file content
```python
# utils/file/cache.py
sha = FileCache.sha256_file(pth)  # Requires file path
```

**With Temp Files:** Caching still works!
- Temp file has same content as original
- SHA256 will be same
- Cache hit/miss logic unchanged

### 2. File Size Validation
**Current:** Validates file sizes before upload
```python
# src/server/handlers/request_handler_execution.py
def validate_file_sizes(arguments, model_name, env_true_func):
    if "files" in arguments:
        # Check file sizes
```

**With Temp Files:** Validation still works!
- Temp file has same size as content
- Size checks unchanged

### 3. Security Implications
**Current:** Secure input validation for file paths
```python
# tools/chat.py
if SECURE_INPUTS_ENFORCED:
    v = SecureInputValidator(repo_root=str(repo_root))
    normalized_files = []
    for f in request.files:
        p = v.normalize_and_check(f)
        normalized_files.append(str(p))
```

**With Temp Files:** Security maintained!
- Temp files created in controlled directory
- No path traversal risk
- Content validation can be added

---

## ✅ Benefits

### For Users
1. **Claude Integration:** Can use EX-AI directly from Claude
2. **No Workarounds:** Don't need to extract content manually
3. **Full Features:** Access all EX-AI file handling capabilities
4. **Seamless UX:** Upload files in Claude, use in EX-AI

### For Developers
1. **Backward Compatible:** Existing code unchanged
2. **Minimal Changes:** Single bridge class
3. **Easy Testing:** Clear test cases
4. **Maintainable:** Isolated in one module

### For System
1. **No Breaking Changes:** Existing tools work unchanged
2. **File Caching Works:** SHA256-based caching preserved
3. **Security Maintained:** Controlled temp directory
4. **Automatic Cleanup:** No temp file leaks

---

## 🚀 Next Steps

### Immediate
1. **Get User Approval** for Temporary File Bridge approach
2. **Implement MCPFileBridge** class
3. **Integrate into Request Handler**
4. **Test with Claude MCP Client**

### Follow-up
1. **Update Documentation** for MCP clients
2. **Add Examples** to API reference
3. **Create Integration Guide** for Claude users
4. **Monitor Temp File Usage** in production

---

## 📝 Documentation Created

1. **Solution Document:** `docs/05_ISSUES/MCP_FILE_HANDLING_SOLUTION.md`
   - Complete solution design
   - Implementation details
   - Code examples
   - Testing strategy

2. **Investigation Report:** `docs/06_PROGRESS/MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md` (this file)
   - Problem analysis
   - Root cause investigation
   - Solution rationale
   - Implementation plan

---

## 🎊 Conclusion

**Status:** ✅ Investigation Complete - Solution Designed

**Summary:**
- Identified root cause: MCP content vs EX-AI path mismatch
- Designed Temporary File Bridge solution
- Validated approach with existing architecture
- Created comprehensive implementation plan
- Estimated 4-5 hours for full implementation

**Recommendation:** Proceed with Temporary File Bridge implementation

**Priority:** HIGH (blocks Claude MCP integration)

---

**Investigation Completed:** 2025-10-14 (14th October 2025)  
**Time Spent:** ~1 hour  
**Documents Created:** 2 (Solution + Investigation)  
**Status:** ✅ READY FOR IMPLEMENTATION

