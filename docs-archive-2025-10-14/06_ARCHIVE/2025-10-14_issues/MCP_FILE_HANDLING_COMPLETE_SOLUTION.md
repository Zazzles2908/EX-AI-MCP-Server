# MCP File Handling - Complete Solution with Supabase Integration

**Date:** 2025-10-14  
**Status:** ✅ READY FOR IMPLEMENTATION  
**Approach:** BytesIO Dual-Path + Supabase Integration

---

## 🎯 Executive Summary

**Problem Solved:** MCP clients (Claude, Cline, Augment) provide file content (bytes/base64) without file paths, but EX-AI requires file paths to upload to Kimi/GLM APIs.

**Solution:** Use **BytesIO** (in-memory file objects) to bridge content-based and path-based approaches.

**Key Discovery:** ✅ Both Kimi and GLM APIs accept BytesIO objects as file handles!

**Supabase Integration:** Track file metadata in Supabase database, with optional long-term storage in Supabase Storage.

---

## ✅ Technical Validation

### **BytesIO Compatibility Confirmed**

After analyzing the existing implementations:

1. **Kimi API (OpenAI-compatible):**
   - Current: `client.files.create(file=Path_object, purpose=...)`
   - Works with: `client.files.create(file=BytesIO_object, purpose=...)`
   - ✅ BytesIO objects accepted

2. **GLM SDK:**
   - Current: `sdk.files.upload(file=file_handle, purpose=...)`
   - Works with: `sdk.files.upload(file=BytesIO_object, purpose=...)`
   - ✅ BytesIO objects accepted

3. **GLM HTTP (multipart):**
   - Current: `files={"file": (name, file_handle, mime)}`
   - Works with: `files={"file": (name, BytesIO_object, mime)}`
   - ✅ BytesIO objects accepted

**Conclusion:** No temp files needed! BytesIO provides a clean, secure bridge.

---

## 🏗️ Implementation Architecture

### **Phase 1: BytesIO Dual-Path (Immediate)**

```python
from io import BytesIO
import hashlib

class FileUploader:
    def upload_content(self, content: bytes, filename: str, mime_type: str) -> str:
        """MCP-native: Upload bytes directly using BytesIO."""
        # Compute SHA256 for caching
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Check cache
        if content_hash in self._cache:
            return self._cache[content_hash]
        
        # Create BytesIO object (in-memory file handle)
        file_obj = BytesIO(content)
        file_obj.name = filename
        
        # Upload to provider (Kimi or GLM)
        file_id = self._upload_to_provider(file_obj, mime_type)
        
        # Cache result
        self._cache[content_hash] = file_id
        return file_id
    
    def upload_file(self, file_path: str) -> str:
        """Legacy: Read file and delegate to upload_content()."""
        with open(file_path, "rb") as f:
            content = f.read()
        return self.upload_content(content, Path(file_path).name, mime_type)
```

**Benefits:**
- ✅ No temp files (no security risks)
- ✅ No disk I/O for MCP uploads (faster)
- ✅ Backwards compatible (existing code works)
- ✅ Clean architecture (single abstraction)

### **Phase 2: Supabase Metadata Tracking (Short-term)**

**Database Schema:**

```sql
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sha256 TEXT NOT NULL,
    filename TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    provider TEXT NOT NULL,  -- 'KIMI' or 'GLM'
    provider_file_id TEXT NOT NULL,
    purpose TEXT NOT NULL,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    uploaded_by TEXT,
    metadata JSONB,
    UNIQUE(sha256, provider)
);

CREATE INDEX idx_file_uploads_sha256 ON file_uploads(sha256);
CREATE INDEX idx_file_uploads_provider_file_id ON file_uploads(provider, provider_file_id);
```

**Integration:**

```python
async def upload_with_tracking(content: bytes, filename: str, mime_type: str):
    # Upload to Kimi/GLM
    file_id = uploader.upload_content(content, filename, mime_type)
    
    # Track in Supabase
    await supabase.table("file_uploads").insert({
        "sha256": hashlib.sha256(content).hexdigest(),
        "filename": filename,
        "mime_type": mime_type,
        "file_size_bytes": len(content),
        "provider": "KIMI",  # or "GLM"
        "provider_file_id": file_id,
        "purpose": "file-extract"
    }).execute()
    
    return file_id
```

**Benefits:**
- ✅ Track all file uploads
- ✅ Query upload history
- ✅ Audit trail
- ✅ Deduplication insights

### **Phase 3: Supabase Storage Integration (Long-term)**

**Dual Storage Strategy:**

1. **Upload to Kimi/GLM** for immediate AI processing
2. **Upload to Supabase Storage** for long-term archival
3. **Track both locations** in database

**Storage Bucket Structure:**

```
supabase-storage/
├── uploads/
│   ├── 2025/
│   │   ├── 10/
│   │   │   ├── {sha256}.pdf
│   │   │   ├── {sha256}.xlsx
```

**Lifecycle Management:**

```python
async def upload_with_dual_storage(content: bytes, filename: str, mime_type: str):
    sha256 = hashlib.sha256(content).hexdigest()
    
    # 1. Upload to Kimi/GLM for AI processing
    kimi_file_id = kimi_uploader.upload_content(content, filename, mime_type)
    
    # 2. Upload to Supabase Storage for archival (async)
    year, month = datetime.now().strftime("%Y/%m").split("/")
    storage_path = f"uploads/{year}/{month}/{sha256}{Path(filename).suffix}"
    
    supabase_url = await supabase.storage.from_("file-uploads").upload(
        storage_path,
        content,
        {"content-type": mime_type}
    )
    
    # 3. Track both locations
    await supabase.table("file_uploads").insert({
        "sha256": sha256,
        "filename": filename,
        "provider": "KIMI",
        "provider_file_id": kimi_file_id,
        "supabase_storage_path": storage_path,
        "supabase_storage_url": supabase_url
    }).execute()
    
    return kimi_file_id
```

**Benefits:**
- ✅ Long-term file archival
- ✅ Cost optimization (delete from Kimi/GLM after processing)
- ✅ File retrieval from Supabase (faster, cheaper)
- ✅ Cross-system file references

---

## 📊 Comparison: All Approaches

| Approach | Security | Performance | MCP-Native | Backwards Compatible | Complexity | Supabase Ready |
|----------|----------|-------------|------------|---------------------|------------|----------------|
| **BytesIO Dual-Path** ✅ | ✅ Excellent | ✅ Excellent | ✅ Yes | ✅ Yes | 🟡 Medium | ✅ Yes |
| Temp File Bridge | ❌ Poor | ❌ Poor | ❌ No | ✅ Yes | 🟡 Medium | 🟡 Partial |
| MCP Resources | ✅ Good | ✅ Good | ✅ Yes | ❌ No | 🔴 High | 🟡 Partial |
| Content-Only | ✅ Excellent | ✅ Excellent | ✅ Yes | ❌ No | 🟢 Low | ✅ Yes |

---

## 🚀 Implementation Roadmap

### **Week 1: BytesIO Dual-Path**

**Day 1-2:** Core Implementation
- Create `src/providers/file_uploader.py`
- Implement `FileUploader` class with BytesIO
- Add `upload_content()` and `upload_file()` methods
- Update `utils/file/cache.py` to add `sha256_bytes()` method

**Day 3-4:** Provider Integration
- Refactor `src/providers/kimi_files.py` to use `FileUploader`
- Refactor `src/providers/glm_files.py` to use `FileUploader`
- Update provider initialization to pass clients

**Day 5:** MCP Integration
- Update `src/server/handlers/request_handler.py`
- Add file parameter processing for content-based uploads
- Support both `{"files": ["/path/to/file"]}` and `{"files": [{"filename": "...", "content": "..."}]}`

**Day 6-7:** Testing
- Test with file paths (existing behavior)
- Test with base64 content (MCP clients)
- Test with binary content (MCP clients)
- Test caching logic
- Test with Claude, Cline, Augment

### **Week 2: Supabase Metadata Tracking**

**Day 1-2:** Database Setup
- Create Supabase project (if not exists)
- Create `file_uploads` table schema
- Set up indexes and constraints
- Configure RLS policies

**Day 3-4:** Integration
- Implement `track_upload_in_supabase()` function
- Integrate with `FileUploader.upload_content()`
- Add error handling and retry logic
- Test end-to-end workflow

**Day 5:** Supabase MCP Tools
- Create `supabase_file_query` tool
- Add file upload history queries
- Add deduplication reports
- Test with MCP clients

**Day 6-7:** Documentation & Testing
- Document Supabase integration
- Create usage examples
- Test all scenarios
- Performance benchmarking

### **Month 1-2: Supabase Storage Integration**

**Week 1:** Storage Setup
- Set up Supabase Storage buckets
- Configure bucket policies
- Implement dual-storage upload logic

**Week 2:** Lifecycle Management
- Add lifecycle policies
- Implement file retrieval with fallback
- Add cost optimization (delete from Kimi/GLM)

**Week 3:** Monitoring & Optimization
- Add monitoring dashboards
- Optimize upload performance
- Add retry logic for failures

**Week 4:** Documentation & Rollout
- Complete documentation
- Create migration guide
- Gradual rollout to production

---

## 📝 MCP Integration Examples

### **Content-Based Upload (MCP Clients)**

```json
{
  "tool": "chat",
  "arguments": {
    "prompt": "Analyze this document",
    "files": [
      {
        "filename": "document.pdf",
        "content": "base64_encoded_content_here",
        "mime_type": "application/pdf"
      }
    ]
  }
}
```

### **Path-Based Upload (Existing Code)**

```json
{
  "tool": "chat",
  "arguments": {
    "prompt": "Analyze this document",
    "files": ["/absolute/path/to/document.pdf"]
  }
}
```

### **Mixed Upload (Both)**

```json
{
  "tool": "chat",
  "arguments": {
    "prompt": "Compare these documents",
    "files": [
      "/path/to/local/file.pdf",
      {
        "filename": "uploaded.xlsx",
        "content": "base64_content",
        "mime_type": "application/vnd.ms-excel"
      }
    ]
  }
}
```

---

## ✅ Success Criteria

- ✅ Claude can upload files via content (no paths required)
- ✅ Existing path-based uploads continue to work
- ✅ No temp files created
- ✅ SHA256 caching works for both methods
- ✅ All tests pass
- ✅ No performance regression
- ✅ Supabase metadata tracking operational
- ✅ File upload history queryable
- ✅ Deduplication working

---

## 📚 Documentation Files

1. **This Document:** Complete solution with Supabase integration
2. **[Implementation Analysis](./MCP_FILE_HANDLING_IMPLEMENTATION_ANALYSIS.md):** BytesIO technical analysis
3. **[Final Solution](./MCP_FILE_HANDLING_FINAL_SOLUTION.md):** Original dual-path proposal
4. **[Known Issue](../known_issues/MCP_FILE_HANDLING_2025-10-14.md):** Issue tracking
5. **[Investigation](../06_PROGRESS/MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md):** Initial investigation

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Next Step:** Begin Week 1 implementation (BytesIO Dual-Path)  
**Estimated Time:** 2 weeks for Phases 1-2, 1-2 months for Phase 3

