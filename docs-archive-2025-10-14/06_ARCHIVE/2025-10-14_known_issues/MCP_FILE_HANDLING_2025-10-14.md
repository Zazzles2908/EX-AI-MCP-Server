# MCP File Handling Issue - 2025-10-14

**Status:** ✅ APPROVED - Ready for Implementation  
**Priority:** High  
**Impact:** MCP Client Compatibility (Claude, Cline, Augment, etc.)

---

## 📋 Issue Summary

**Problem:** MCP clients (Claude, Cline, Augment) provide file content (bytes/base64) without file paths, but EX-AI requires absolute file paths to upload files to Kimi/GLM APIs.

**User Report:**
> "I was using claude to connect to exai, but this issue occurred: 'The exai tool requires full absolute file paths, not just filenames. I need to figure out the absolute paths to these files. However, since these are uploaded files to Claude, I don't actually have access to their absolute file system paths.'"

---

## 🔍 Root Cause Analysis

### **Architecture Mismatch**

1. **MCP Protocol:** Designed for content-based data passing
   - MCP clients provide file content (base64 or bytes)
   - No file paths available in MCP protocol
   - Content-first approach

2. **EX-AI Current Implementation:** Requires file paths
   - `upload_file(file_path: str)` requires absolute paths
   - Files must exist on disk
   - Path-based approach

3. **Gap:** Content-based (MCP) vs Path-based (EX-AI)

---

## ✅ Approved Solution: Dual-Path Upload Architecture

### **Solution Overview**

Implement a dual-path upload system that:
1. **Accepts content directly** (MCP-native, primary method)
2. **Supports file paths** (backwards compatibility, legacy method)
3. **No temp files** (eliminates security risks)
4. **SHA256 caching** (works for both methods)

### **Validation**

**Confirmed by:**
- ✅ EX-AI Analysis (Kimi K2 model with web search + high thinking mode)
- ✅ Supabase MCP Implementation Study
- ✅ MCP Ecosystem Best Practices

**Supabase Evidence:**
```javascript
// Supabase accepts File/Blob objects directly, NOT file paths
const { data, error } = await supabase.storage
  .from('bucket_name')
  .upload('file_path', file)  // 'file' is a File/Blob object
```

---

## 🏗️ Implementation Plan

### **Phase 1: Core Abstraction** (2-3 hours)

**Create:** `src/providers/file_uploader.py`

```python
class FileUploader:
    def upload_content(
        self,
        content: bytes,
        filename: str,
        mime_type: str,
        purpose: str = "file-extract"
    ) -> str:
        """Upload file content directly (MCP-native)."""
        # Compute SHA256, check cache, upload to provider
        
    def upload_file(self, file_path: str, purpose: str = "file-extract") -> str:
        """Upload file from path (legacy support)."""
        # Read file, delegate to upload_content()
```

### **Phase 2: Provider Integration** (1-2 hours)

**Update:**
- `src/providers/kimi_files.py` - Add `upload_content()` function
- `src/providers/glm_files.py` - Add `upload_content()` function

### **Phase 3: MCP Integration** (1 hour)

**Update:** `src/server/handlers/request_handler.py`

```python
# Process file parameters from MCP clients
if isinstance(file_param, dict) and "content" in file_param:
    # MCP content upload (new)
    file_id = upload_content(...)
elif isinstance(file_param, str):
    # Path-based upload (existing)
    file_id = upload_file(...)
```

### **Phase 4: Testing** (2-3 hours)

- Test with file paths (existing behavior)
- Test with base64 content (MCP clients)
- Test with binary content (MCP clients)
- Test caching logic
- Test with Claude, Cline, Augment

---

## 📝 Supported Input Formats

### **After Implementation**

```python
# Option 1: File Paths (Existing - Unchanged)
{"files": ["/absolute/path/to/file.pdf"]}

# Option 2: File Content (New - MCP Support)
{"files": [{"filename": "document.pdf", "content": "<base64>", "mime_type": "application/pdf"}]}

# Option 3: Mixed (Both)
{"files": [
    "/path/to/local/file.pdf",
    {"filename": "uploaded.xlsx", "content": "<base64>"}
]}
```

---

## 🚫 Rejected Alternatives

### **1. Temporary File Bridge**
- ❌ Security risks (directory traversal, symlink attacks)
- ❌ Performance overhead from disk I/O
- ❌ Cleanup complexity
- ❌ Not MCP-native

### **2. MCP Resources Protocol**
- ⚠️ Not widely adopted yet
- ⚠️ Supabase doesn't use it
- ✅ Can be added later when ecosystem matures

### **3. Content-Only Approach**
- ❌ Breaks existing path-based integrations
- ❌ No backwards compatibility

---

## 📈 Benefits

### **Security**
- ✅ No temp file vulnerabilities
- ✅ No directory traversal risks
- ✅ No symlink attack surface

### **Performance**
- ✅ No disk I/O for MCP uploads
- ✅ Direct memory-to-API transfer
- ✅ Faster upload times

### **Compatibility**
- ✅ Works with ALL MCP clients
- ✅ Backwards compatible
- ✅ No breaking changes

---

## 🎯 Success Criteria

- ✅ Claude can upload files via content (no paths required)
- ✅ Existing path-based uploads continue to work
- ✅ No temp files created
- ✅ SHA256 caching works for both methods
- ✅ All tests pass

---

## 📚 Related Documentation

- **Detailed Solution:** [../05_ISSUES/MCP_FILE_HANDLING_FINAL_SOLUTION.md](../05_ISSUES/MCP_FILE_HANDLING_FINAL_SOLUTION.md)
- **Investigation Report:** [../06_PROGRESS/MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md](../06_PROGRESS/MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md)
- **Original Proposal:** [../05_ISSUES/MCP_FILE_HANDLING_SOLUTION.md](../05_ISSUES/MCP_FILE_HANDLING_SOLUTION.md)

---

## ✅ Next Steps

1. **Review** the detailed solution document
2. **Implement** Phase 1 (Core Abstraction)
3. **Test** with MCP clients
4. **Deploy** to production
5. **Monitor** for edge cases

---

**Approved by:** EX-AI (Kimi K2 Model)  
**Validation:** Supabase MCP Analysis  
**Status:** Ready for Implementation  
**Estimated Time:** 6-9 hours total

