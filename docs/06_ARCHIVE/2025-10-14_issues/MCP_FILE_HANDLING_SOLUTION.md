# MCP File Handling Solution
**Date:** 2025-10-14 (14th October 2025)  
**Issue:** Claude MCP clients can't provide absolute file paths  
**Status:** Solution Designed - Implementation Pending  
**Priority:** HIGH

---

## 🎯 Problem Statement

**User Report:**
> "The exai tool requires full absolute file paths, not just filenames. I need to figure out the absolute paths to these files. However, since these are uploaded files to Claude, I don't actually have access to their absolute file system paths."

**Root Cause:**
- **Claude (MCP client)** uploads files but doesn't provide absolute paths - only file content
- **EX-AI** requires absolute file paths to upload files to Kimi/GLM APIs
- There's a fundamental mismatch between MCP's content-based approach and EX-AI's path-based approach

---

## 📋 Current Architecture

### How EX-AI Handles Files

**1. File Upload Flow:**
```python
# src/providers/kimi_files.py
def upload_file(client: Any, file_path: str, purpose: str = "file-extract") -> str:
    """Upload a local file to Moonshot (Kimi) and return file_id."""
    p = Path(file_path)
    if not p.is_absolute():
        project_root = Path.cwd()
        p = (project_root / p).resolve()
    
    if not p.exists():
        raise FileNotFoundError(f"File not found: {file_path} (cwd={cwd})")
    
    # Upload file to Kimi API
    with p.open("rb") as f:
        # ... upload logic
```

**Problem:** Requires `file_path` to exist on disk

**2. Current File Handling:**
- Tools receive `files` parameter as list of file paths
- Files must exist on local filesystem
- Files are read and uploaded to provider APIs
- Provider returns `file_id` for use in chat

**3. Supported Providers:**
- **Kimi:** `client.files.create(file=open(...), purpose="file-extract")`
- **GLM:** `client.files.upload(file=open(...), purpose="agent")`

---

## 🔍 MCP File Resources Specification

### How MCP Handles Files

**MCP Resources:**
- MCP has a "Resources" concept for exposing data to LLMs
- Resources are identified by URIs (e.g., `file:///path/to/file`)
- Resources can be text or binary content
- **MCP clients (like Claude) can upload file content without providing paths**

**Current Gap:**
- EX-AI doesn't implement MCP Resources protocol
- EX-AI only accepts file paths, not file content
- No temporary file storage for MCP-uploaded content

---

## ✅ Solution Design

### Option 1: Temporary File Bridge (RECOMMENDED)

**Concept:** Create temporary files from MCP content, then use existing upload logic

**Implementation:**

```python
# New file: src/server/handlers/mcp_file_bridge.py

import tempfile
import base64
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MCPFileBridge:
    """
    Bridge between MCP file content and EX-AI file path requirements.
    
    Handles:
    1. MCP clients that provide file content without paths
    2. Creating temporary files for content-based uploads
    3. Cleanup of temporary files after use
    """
    
    def __init__(self, temp_dir: Optional[Path] = None):
        """Initialize file bridge with temporary directory."""
        self.temp_dir = temp_dir or Path(tempfile.gettempdir()) / "exai_mcp_files"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._temp_files: Dict[str, Path] = {}
        logger.info(f"MCP File Bridge initialized: {self.temp_dir}")
    
    def process_file_parameter(
        self,
        file_param: Any,
        filename: Optional[str] = None
    ) -> str:
        """
        Process a file parameter that could be:
        1. Absolute path (existing behavior)
        2. Relative path (existing behavior)
        3. File content (base64 or raw bytes)
        4. MCP resource URI
        
        Returns:
            Absolute path to file (either existing or temporary)
        """
        # Case 1: Already a valid file path
        if isinstance(file_param, str):
            p = Path(file_param)
            if p.exists():
                return str(p.resolve())
            
            # Check if it's a relative path
            if not p.is_absolute():
                project_root = Path.cwd()
                resolved = (project_root / p).resolve()
                if resolved.exists():
                    return str(resolved)
        
        # Case 2: File content (base64 or bytes)
        if isinstance(file_param, dict):
            content = file_param.get("content")
            filename = file_param.get("filename") or filename or "uploaded_file"
            
            if content:
                return self._create_temp_file(content, filename)
        
        # Case 3: Direct bytes/base64 string
        if isinstance(file_param, bytes):
            filename = filename or "uploaded_file"
            return self._create_temp_file(file_param, filename)
        
        # Case 4: Base64 string
        if isinstance(file_param, str) and self._is_base64(file_param):
            filename = filename or "uploaded_file"
            content = base64.b64decode(file_param)
            return self._create_temp_file(content, filename)
        
        # Fallback: treat as path and let existing error handling work
        return str(file_param)
    
    def _create_temp_file(self, content: bytes, filename: str) -> str:
        """Create a temporary file with the given content."""
        import hashlib
        
        # Create unique filename based on content hash
        content_hash = hashlib.sha256(content).hexdigest()[:16]
        safe_filename = Path(filename).name  # Remove any path components
        temp_filename = f"{content_hash}_{safe_filename}"
        temp_path = self.temp_dir / temp_filename
        
        # Write content to temp file
        temp_path.write_bytes(content)
        
        # Track for cleanup
        self._temp_files[str(temp_path)] = temp_path
        
        logger.info(f"Created temporary file: {temp_path} ({len(content)} bytes)")
        return str(temp_path)
    
    def _is_base64(self, s: str) -> bool:
        """Check if string is valid base64."""
        try:
            if len(s) < 4:
                return False
            base64.b64decode(s, validate=True)
            return True
        except Exception:
            return False
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """Remove a temporary file if it was created by this bridge."""
        if file_path in self._temp_files:
            try:
                self._temp_files[file_path].unlink(missing_ok=True)
                del self._temp_files[file_path]
                logger.debug(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    def cleanup_all(self) -> None:
        """Remove all temporary files created by this bridge."""
        for file_path in list(self._temp_files.keys()):
            self.cleanup_temp_file(file_path)
```

**Integration Points:**

```python
# src/server/handlers/request_handler.py

# Add at module level
from .mcp_file_bridge import MCPFileBridge

_file_bridge = MCPFileBridge()

# In handle_call_tool function, before file processing:
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    # ... existing code ...
    
    # Process files parameter to handle MCP content
    if "files" in arguments and arguments["files"]:
        processed_files = []
        for file_param in arguments["files"]:
            try:
                file_path = _file_bridge.process_file_parameter(file_param)
                processed_files.append(file_path)
            except Exception as e:
                logger.warning(f"Failed to process file parameter: {e}")
                # Keep original parameter for existing error handling
                processed_files.append(file_param)
        arguments["files"] = processed_files
    
    # ... rest of existing code ...
    
    # After tool execution, cleanup temp files
    try:
        if "files" in arguments:
            for file_path in arguments["files"]:
                _file_bridge.cleanup_temp_file(file_path)
    except Exception as e:
        logger.debug(f"Temp file cleanup failed: {e}")
```

---

### Option 2: Direct Content Upload (ALTERNATIVE)

**Concept:** Modify upload functions to accept content directly

**Pros:**
- No temporary files needed
- More efficient (no disk I/O)

**Cons:**
- Requires modifying all provider upload functions
- Breaks existing file caching logic (based on file paths)
- More invasive changes

**Implementation:**

```python
# src/providers/kimi_files.py

def upload_file(
    client: Any,
    file_path: Optional[str] = None,
    file_content: Optional[bytes] = None,
    filename: Optional[str] = None,
    purpose: str = "file-extract"
) -> str:
    """
    Upload a file to Moonshot (Kimi) and return file_id.
    
    Args:
        client: OpenAI-compatible client instance
        file_path: Path to a local file (mutually exclusive with file_content)
        file_content: Raw file content (mutually exclusive with file_path)
        filename: Filename to use (required if file_content is provided)
        purpose: Moonshot purpose tag
    """
    if file_path and file_content:
        raise ValueError("Provide either file_path or file_content, not both")
    
    if not file_path and not file_content:
        raise ValueError("Must provide either file_path or file_content")
    
    # Existing path-based logic
    if file_path:
        p = Path(file_path)
        # ... existing code ...
    
    # New content-based logic
    if file_content:
        if not filename:
            raise ValueError("filename required when providing file_content")
        
        # Upload directly from bytes
        import io
        file_obj = io.BytesIO(file_content)
        file_obj.name = filename
        
        # ... upload logic ...
```

---

## 🎯 Recommended Approach

**Use Option 1 (Temporary File Bridge)** because:

1. ✅ **Minimal Changes:** Works with existing upload logic
2. ✅ **Backward Compatible:** Existing file paths still work
3. ✅ **File Caching Works:** Temp files have paths, so caching logic unchanged
4. ✅ **Easy to Test:** Can test with both paths and content
5. ✅ **Cleanup Handled:** Automatic temp file cleanup after use

---

## 📝 Implementation Plan

### Phase 1: Core Bridge (1-2 hours)
1. Create `src/server/handlers/mcp_file_bridge.py`
2. Implement `MCPFileBridge` class
3. Add unit tests for file processing logic

### Phase 2: Integration (1 hour)
1. Integrate bridge into `request_handler.py`
2. Add cleanup logic after tool execution
3. Test with existing file-based tools

### Phase 3: MCP Client Support (1 hour)
1. Update documentation for MCP clients
2. Add examples of file content upload
3. Test with Claude MCP client

### Phase 4: Testing & Validation (1 hour)
1. Test with file paths (existing behavior)
2. Test with base64 content
3. Test with binary content
4. Test cleanup logic

**Total Estimated Time:** 4-5 hours

---

## 🧪 Testing Strategy

### Test Cases

**1. Existing Behavior (File Paths):**
```python
# Should work unchanged
arguments = {
    "files": ["/absolute/path/to/file.pdf", "relative/path/to/file.txt"]
}
```

**2. Base64 Content:**
```python
# New: MCP client provides base64
arguments = {
    "files": [
        {
            "filename": "document.pdf",
            "content": "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8PC9UeXBlL1BhZ2UvTWVkaWFCb3hbMCAwIDYxMiA3OTJdL1BhcmVudCAyIDAgUi9SZXNvdXJjZXM8PC9Gb250PDwvRjEgNCAwIFI+Pj4+L0NvbnRlbnRzIDUgMCBSPj4KZW5kb2JqCjQgMCBvYmoKPDwvVHlwZS9Gb250L1N1YnR5cGUvVHlwZTEvQmFzZUZvbnQvSGVsdmV0aWNhPj4KZW5kb2JqCjUgMCBvYmoKPDwvTGVuZ3RoIDQ0Pj4Kc3RyZWFtCkJUCi9GMSA0OCBUZgoxMCA3MDAgVGQKKEhlbGxvIFdvcmxkKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxNSAwMDAwMCBuIAowMDAwMDAwMDY0IDAwMDAwIG4gCjAwMDAwMDAxMjEgMDAwMDAgbiAKMDAwMDAwMDI0NiAwMDAwMCBuIAowMDAwMDAwMzI1IDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA2L1Jvb3QgMSAwIFI+PgpzdGFydHhyZWYKNDE3CiUlRU9GCg=="
        }
    ]
}
```

**3. Mixed Content:**
```python
# Mix of paths and content
arguments = {
    "files": [
        "/path/to/existing/file.pdf",
        {"filename": "uploaded.xlsx", "content": base64_content}
    ]
}
```

---

## 📚 Documentation Updates

### For MCP Clients (Claude, etc.)

**New: File Content Upload**

```markdown
## File Upload Options

### Option 1: File Paths (Existing)
```python
{
    "files": ["/absolute/path/to/file.pdf"]
}
```

### Option 2: File Content (New - MCP Support)
```python
{
    "files": [
        {
            "filename": "document.pdf",
            "content": "<base64-encoded-content>"
        }
    ]
}
```

### Option 3: Mixed (Both)
```python
{
    "files": [
        "/path/to/local/file.pdf",
        {"filename": "uploaded.xlsx", "content": "<base64>"}
    ]
}
```
```

---

## ✅ Benefits

1. **MCP Compatibility:** Works with Claude and other MCP clients
2. **Backward Compatible:** Existing file paths still work
3. **Transparent:** Tools don't need to change
4. **Automatic Cleanup:** Temp files removed after use
5. **Flexible:** Supports paths, content, or both

---

## 🚀 Next Steps

1. **Get User Approval** for Option 1 (Temporary File Bridge)
2. **Implement Core Bridge** (`mcp_file_bridge.py`)
3. **Integrate into Request Handler**
4. **Test with Claude MCP Client**
5. **Update Documentation**

---

**Status:** ✅ Solution Designed - Ready for Implementation  
**Estimated Time:** 4-5 hours  
**Priority:** HIGH (blocks Claude MCP integration)

