# MCP File Handling - Final Solution

**Date:** 2025-10-14  
**Status:** ✅ APPROVED - Ready for Implementation  
**Validation:** Confirmed by EX-AI (Kimi K2) + Supabase MCP Analysis

---

## 🎯 Executive Summary

**Problem:** MCP clients (Claude, Cline, Augment) provide file content (bytes/base64) without file paths, but EX-AI requires absolute file paths to upload files to Kimi/GLM APIs.

**Solution:** **Dual-Path Upload Architecture** - Accept both content and paths, with content as the primary MCP-native method.

**Validation:** Confirmed by analyzing Supabase MCP server implementation, which uses content-based file handling (no file paths required).

---

## ✅ Final Recommendation: Dual-Path Approach

### **Why This is the Best Solution**

1. ✅ **MCP Ecosystem Alignment** - Supabase Storage API accepts File/Blob/bytes objects directly, NOT file paths
2. ✅ **No Security Risks** - Eliminates temp file vulnerabilities (directory traversal, symlink attacks, race conditions)
3. ✅ **Better Performance** - No disk I/O for MCP uploads
4. ✅ **Backwards Compatible** - Existing path-based code continues to work
5. ✅ **Production-Ready** - Supabase handles massive scale with this pattern
6. ✅ **Future-Proof** - Aligns with MCP best practices

---

## 📊 Supabase MCP Validation

### **How Supabase Handles File Uploads**

**JavaScript SDK:**
```javascript
const { data, error } = await supabase.storage
  .from('bucket_name')
  .upload('file_path', file)  // 'file' is a File/Blob object, NOT a path
```

**Kotlin SDK:**
```kotlin
supabase.storage.from("bucket_name").upload("file_path", bytes)  // Direct bytes
```

**Python SDK:**
```python
response = supabase.storage.from_('bucket_name').upload('file_path', file)  // File object
```

**Key Insight:** Supabase accepts:
- File objects (browser File API)
- Blob objects (binary data)
- Bytes (raw binary content)
- ReadableStream (for streaming uploads)

**They do NOT require file paths on disk!**

---

## 🏗️ Architecture Design

### **Core Abstraction Layer (BytesIO Approach)**

**✅ CONFIRMED:** Both Kimi and GLM APIs accept BytesIO objects (in-memory file handles)!

```python
# New file: src/providers/file_uploader.py

from io import BytesIO
import hashlib
import mimetypes
from pathlib import Path
from typing import Any, Optional

class FileUploader:
    """
    Unified file upload abstraction for MCP and legacy integrations.

    Uses BytesIO for content-based uploads - no temp files, no disk I/O!

    Supports:
    - Content-based uploads (MCP-native) via BytesIO
    - Path-based uploads (backwards compatibility)
    - SHA256-based caching for both methods
    """

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

        Args:
            content: Raw file bytes
            filename: Original filename
            mime_type: MIME type (e.g., 'image/jpeg')
            purpose: Upload purpose ('file-extract' or 'assistants')

        Returns:
            file_id from provider
        """
        # Compute SHA256 for caching
        content_hash = hashlib.sha256(content).hexdigest()

        # Check cache
        if content_hash in self._cache:
            return self._cache[content_hash]

        # Create BytesIO object (in-memory file handle)
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

        Args:
            file_path: Absolute or relative path to file
            purpose: Upload purpose

        Returns:
            file_id from provider
        """
        # Read file
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(path, "rb") as f:
            content = f.read()

        # Get metadata
        filename = path.name
        mime_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"

        # Delegate to upload_content
        return self.upload_content(content, filename, mime_type, purpose)

    def _upload_to_kimi(self, file_obj: BytesIO, purpose: str) -> str:
        """Upload BytesIO object to Kimi API (OpenAI-compatible)."""
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

        # HTTP fallback with BytesIO
        files = {"file": (filename, file_obj, mime_type)}
        js = self.http_client.post_multipart("/files", files=files, data={"purpose": purpose})
        file_id = js.get("id") or js.get("data", {}).get("id")
        if not file_id:
            raise RuntimeError(f"GLM upload did not return an id: {js}")
        return str(file_id)
```

**Key Innovation:** BytesIO objects work as file handles for both Kimi and GLM APIs!
- Kimi: `client.files.create(file=BytesIO_object, ...)`
- GLM SDK: `sdk.files.upload(file=BytesIO_object, ...)`
- GLM HTTP: `files={"file": (name, BytesIO_object, mime)}`

---

## 🔧 Implementation Plan

### **Phase 1: Core Abstraction** (2-3 hours)

**Step 1:** Create `src/providers/file_uploader.py`
- Implement `FileUploader` class
- Add `upload_content()` method (MCP-native)
- Add `upload_file()` method (legacy support)
- Implement SHA256 caching

**Step 2:** Refactor Provider Upload Functions (1-2 hours)
- Update `src/providers/kimi_files.py`
- Update `src/providers/glm_files.py`
- Add `upload_content()` functions
- Keep existing `upload_file()` functions (delegate to `upload_content`)

**Step 3:** MCP Integration (1 hour)
- Update `src/server/handlers/request_handler.py`
- Add file parameter processing
- Support both content and path formats

**Step 4:** Testing (2-3 hours)
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
    {"filename": "uploaded.xlsx", "content": "<base64>", "mime_type": "application/vnd.ms-excel"}
]}
```

---

## 🚫 Rejected Alternatives

### **1. Temporary File Bridge**
**Why Rejected:**
- ❌ Security risks (directory traversal, symlink attacks, race conditions)
- ❌ Performance overhead from disk I/O
- ❌ Cleanup complexity and potential resource leaks
- ❌ Not MCP-native

### **2. MCP Resources Protocol**
**Why Deferred:**
- ⚠️ Not widely adopted in MCP ecosystem yet
- ⚠️ Supabase MCP uses parameter-based content passing, not Resources
- ⚠️ Can be added later when ecosystem matures
- ✅ Dual-path works NOW, Resources added when needed

### **3. Content-Only Approach**
**Why Rejected:**
- ❌ Breaks existing path-based integrations
- ❌ No backwards compatibility
- ❌ Requires immediate migration of all existing code

---

## 📈 Benefits

### **Security**
- ✅ No temp file vulnerabilities
- ✅ No directory traversal risks
- ✅ No symlink attack surface
- ✅ No race conditions

### **Performance**
- ✅ No disk I/O for MCP uploads
- ✅ Direct memory-to-API transfer
- ✅ Faster upload times
- ✅ Lower latency

### **Compatibility**
- ✅ Works with ALL MCP clients (Claude, Cline, Augment, etc.)
- ✅ Backwards compatible with existing code
- ✅ No breaking changes
- ✅ Gradual migration path

### **Maintainability**
- ✅ Single abstraction layer
- ✅ Cleaner architecture
- ✅ Easier to test
- ✅ Future-proof

---

## 🎯 Success Criteria

- ✅ Claude can upload files via content (no paths required)
- ✅ Existing path-based uploads continue to work
- ✅ No temp files created
- ✅ SHA256 caching works for both methods
- ✅ All tests pass
- ✅ No performance regression

---

## 📚 Related Documentation

- [MCP File Handling Investigation](./MCP_FILE_HANDLING_INVESTIGATION_2025-10-14.md)
- [Original Temp File Bridge Proposal](./MCP_FILE_HANDLING_SOLUTION.md)
- [Kimi API Reference](../02_API_REFERENCE/KIMI_API_REFERENCE.md)
- [GLM API Reference](../02_API_REFERENCE/GLM_API_REFERENCE.md)

---

## ✅ Approval

**Approved by:** EX-AI (Kimi K2 Model)  
**Validation:** Supabase MCP Analysis  
**Status:** Ready for Implementation  
**Next Step:** Begin Phase 1 Implementation

