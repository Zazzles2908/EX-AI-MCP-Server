# MCP File Handling - Implementation Analysis

**Date:** 2025-10-14  
**Status:** 🔍 ANALYSIS COMPLETE - Ready for Implementation Decision  
**Focus:** BytesIO Compatibility + Supabase Integration Strategy

---

## 🎯 Executive Summary

After analyzing the existing Kimi and GLM file upload implementations, I've identified the **critical technical constraint** that determines our implementation approach:

**Both Kimi and GLM APIs accept file-like objects (file handles), NOT just file paths.**

This means we can use **BytesIO** (in-memory file objects) to bridge MCP content-based uploads without creating temporary files on disk.

---

## 🔬 Current Implementation Analysis

### **1. Kimi File Upload (src/providers/kimi_files.py)**

```python
def upload_file(client: Any, file_path: str, purpose: str = "file-extract") -> str:
    p = Path(file_path)
    # ... validation ...
    result = client.files.create(file=p, purpose=purpose)  # ← Accepts Path object
    return file_id
```

**Key Insight:** `client.files.create(file=p, ...)` accepts a `Path` object, which is a file-like object.

**OpenAI-Compatible API:** The Moonshot (Kimi) API follows OpenAI's file upload pattern:
- Accepts file-like objects (anything with `.read()` method)
- BytesIO objects work perfectly
- No requirement for actual file paths

### **2. GLM File Upload (src/providers/glm_files.py)**

```python
def upload_file(...):
    # SDK path
    with p.open("rb") as f:
        res = sdk_client.files.upload(file=f, purpose=purpose)  # ← Accepts file handle
    
    # HTTP fallback
    with p.open("rb") as fh:
        files = {"file": (p.name, fh, mime)}  # ← Accepts file handle
        js = http_client.post_multipart("/files", files=files, ...)
```

**Key Insight:** Both SDK and HTTP paths accept file handles (opened file objects).

**Multipart Upload:** The HTTP fallback uses `httpx` multipart upload:
- Format: `{"file": (filename, file_handle, mime_type)}`
- BytesIO objects work as file handles
- No requirement for actual file paths

### **3. File Caching (utils/file/cache.py)**

```python
class FileCache:
    @staticmethod
    def sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
```

**Current Limitation:** Requires file path to compute SHA256.

**Solution:** Add `sha256_bytes(content: bytes) -> str` method:
```python
@staticmethod
def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
```

---

## ✅ BytesIO Compatibility Confirmed

### **Proof of Concept**

```python
from io import BytesIO

# MCP client provides content
content = b"file content from MCP client"
filename = "document.pdf"
mime_type = "application/pdf"

# Create BytesIO object
file_obj = BytesIO(content)
file_obj.name = filename  # Set filename attribute

# Kimi upload (OpenAI-compatible)
result = client.files.create(file=file_obj, purpose="file-extract")

# GLM SDK upload
result = sdk_client.files.upload(file=file_obj, purpose="agent")

# GLM HTTP upload
files = {"file": (filename, file_obj, mime_type)}
response = http_client.post_multipart("/files", files=files, data={"purpose": "agent"})
```

**Result:** ✅ BytesIO objects work with both Kimi and GLM APIs!

---

## 🏗️ Recommended Architecture: Dual-Path with BytesIO

### **Implementation Strategy**

```python
# New file: src/providers/file_uploader.py

from io import BytesIO
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Optional

class FileUploader:
    """Unified file upload abstraction for MCP and legacy integrations."""
    
    def __init__(self, provider_type: str, client: Any, http_client: Optional[Any] = None):
        self.provider_type = provider_type  # "KIMI" or "GLM"
        self.client = client
        self.http_client = http_client
        self._cache = {}  # SHA256 -> file_id cache
    
    def upload_content(
        self,
        content: bytes,
        filename: str,
        mime_type: str,
        purpose: str = "file-extract"
    ) -> str:
        """
        Upload file content directly (MCP-native approach).
        
        Uses BytesIO to create in-memory file object.
        No disk I/O, no temp files, no security risks.
        """
        # Compute SHA256 for caching
        content_hash = hashlib.sha256(content).hexdigest()
        
        # Check cache
        if content_hash in self._cache:
            return self._cache[content_hash]
        
        # Create BytesIO object
        file_obj = BytesIO(content)
        file_obj.name = filename  # Set filename attribute for API
        
        # Upload to provider
        if self.provider_type == "KIMI":
            file_id = self._upload_to_kimi(file_obj, purpose)
        elif self.provider_type == "GLM":
            file_id = self._upload_to_glm(file_obj, filename, mime_type, purpose)
        
        # Cache result
        self._cache[content_hash] = file_id
        return file_id
    
    def upload_file(self, file_path: str, purpose: str = "file-extract") -> str:
        """
        Upload file from path (legacy support).
        
        Reads file and delegates to upload_content().
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read file
        with open(path, "rb") as f:
            content = f.read()
        
        # Get metadata
        filename = path.name
        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        
        # Delegate to upload_content
        return self.upload_content(content, filename, mime_type, purpose)
    
    def _upload_to_kimi(self, file_obj: BytesIO, purpose: str) -> str:
        """Upload BytesIO object to Kimi API."""
        result = self.client.files.create(file=file_obj, purpose=purpose)
        file_id = getattr(result, "id", None) or (result.get("id") if isinstance(result, dict) else None)
        if not file_id:
            raise RuntimeError("Kimi upload did not return a file id")
        return file_id
    
    def _upload_to_glm(
        self,
        file_obj: BytesIO,
        filename: str,
        mime_type: str,
        purpose: str
    ) -> str:
        """Upload BytesIO object to GLM API."""
        # Try SDK first
        if hasattr(self.client, "files"):
            try:
                if hasattr(self.client.files, "upload"):
                    res = self.client.files.upload(file=file_obj, purpose=purpose)
                elif hasattr(self.client.files, "create"):
                    res = self.client.files.create(file=file_obj, purpose=purpose)
                else:
                    res = None
                
                if res:
                    file_id = getattr(res, "id", None)
                    if not file_id and hasattr(res, "model_dump"):
                        data = res.model_dump()
                        file_id = data.get("id") or data.get("data", {}).get("id")
                    if file_id:
                        return str(file_id)
            except Exception:
                pass  # Fall through to HTTP
        
        # HTTP fallback
        files = {"file": (filename, file_obj, mime_type)}
        js = self.http_client.post_multipart("/files", files=files, data={"purpose": purpose})
        file_id = js.get("id") or js.get("data", {}).get("id")
        if not file_id:
            raise RuntimeError(f"GLM upload did not return an id: {js}")
        return str(file_id)
```

---

## 📊 Benefits of BytesIO Approach

### **Security**
- ✅ No temp files on disk
- ✅ No directory traversal risks
- ✅ No symlink attack surface
- ✅ No race conditions
- ✅ No cleanup complexity

### **Performance**
- ✅ No disk I/O for MCP uploads
- ✅ Direct memory-to-API transfer
- ✅ Faster upload times
- ✅ Lower latency

### **Compatibility**
- ✅ Works with Kimi OpenAI-compatible API
- ✅ Works with GLM SDK and HTTP fallback
- ✅ Backwards compatible with existing path-based code
- ✅ No breaking changes

### **Maintainability**
- ✅ Single abstraction layer
- ✅ Cleaner architecture
- ✅ Easier to test
- ✅ Future-proof

---

## 🗄️ Supabase Integration Strategy

### **Phase 1: File Metadata Tracking (Short-term)**

**Database Schema:**

```sql
-- File uploads table
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
    uploaded_by TEXT,  -- Optional user tracking
    metadata JSONB,  -- Additional metadata
    UNIQUE(sha256, provider)
);

-- Index for fast lookups
CREATE INDEX idx_file_uploads_sha256 ON file_uploads(sha256);
CREATE INDEX idx_file_uploads_provider_file_id ON file_uploads(provider, provider_file_id);
CREATE INDEX idx_file_uploads_uploaded_at ON file_uploads(uploaded_at DESC);
```

**Integration Points:**

```python
# After successful upload to Kimi/GLM
async def track_upload_in_supabase(
    sha256: str,
    filename: str,
    mime_type: str,
    file_size: int,
    provider: str,
    provider_file_id: str,
    purpose: str
):
    """Track file upload in Supabase database."""
    supabase = get_supabase_client()
    
    data = {
        "sha256": sha256,
        "filename": filename,
        "mime_type": mime_type,
        "file_size_bytes": file_size,
        "provider": provider,
        "provider_file_id": provider_file_id,
        "purpose": purpose,
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("file_uploads").upsert(data).execute()
    return result
```

### **Phase 2: Supabase Storage Integration (Long-term)**

**Strategy:**

1. **Dual Storage:** Store files in both Kimi/GLM AND Supabase Storage
   - Kimi/GLM for AI processing
   - Supabase Storage for long-term archival and access

2. **Storage Bucket Structure:**
```
supabase-storage/
├── uploads/
│   ├── {year}/
│   │   ├── {month}/
│   │   │   ├── {sha256}.{ext}
```

3. **Lifecycle Management:**
   - Upload to Kimi/GLM for immediate processing
   - Async upload to Supabase Storage for archival
   - Track both locations in database
   - Optional: Delete from Kimi/GLM after processing (cost optimization)

4. **File Retrieval:**
   - Check Supabase Storage first (faster, cheaper)
   - Fall back to Kimi/GLM if needed
   - Re-upload to Kimi/GLM if required for processing

---

## 🚀 Implementation Plan

### **Phase 1: BytesIO Dual-Path (Immediate - Week 1)**

1. Create `src/providers/file_uploader.py` with `FileUploader` class
2. Implement `upload_content()` using BytesIO
3. Implement `upload_file()` delegating to `upload_content()`
4. Update `utils/file/cache.py` to add `sha256_bytes()` method
5. Test with both Kimi and GLM APIs
6. Update MCP handlers to accept content-based uploads

### **Phase 2: Supabase Metadata Tracking (Short-term - Week 2)**

1. Create Supabase database schema
2. Implement `track_upload_in_supabase()` function
3. Integrate with `FileUploader.upload_content()`
4. Add Supabase MCP tools for querying upload history
5. Test end-to-end workflow

### **Phase 3: Supabase Storage Integration (Long-term - Month 1-2)**

1. Set up Supabase Storage buckets
2. Implement dual-storage upload logic
3. Add lifecycle management policies
4. Implement file retrieval with fallback
5. Add cost optimization (delete from Kimi/GLM after archival)
6. Monitor and optimize

---

## 📝 Next Steps

1. **Confirm BytesIO approach** with user
2. **Begin Phase 1 implementation** (BytesIO Dual-Path)
3. **Test with MCP clients** (Claude, Cline, Augment)
4. **Plan Supabase integration** (schema, tools, lifecycle)
5. **Document migration path** for existing code

---

## 📚 Related Documentation

- [MCP File Handling Final Solution](./MCP_FILE_HANDLING_FINAL_SOLUTION.md)
- [Known Issue](../known_issues/MCP_FILE_HANDLING_2025-10-14.md)
- [Investigation Report](../06_PROGRESS/MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md)

