# Agent File Upload Guide for EXAI MCP Server
**Date:** October 26, 2025  
**Version:** 2.4  
**Target Audience:** AI Agents using EXAI MCP Server

---

## 📋 Quick Reference

**When to use each upload method:**

| File Size | Method | Tool | Token Savings | Deduplication |
|-----------|--------|------|---------------|---------------|
| **< 50 KB** | Embedding | `files` parameter | N/A (direct) | N/A |
| **0.5 - 10 MB** | Kimi Upload | `kimi_upload_files` | 70-80% | ✅ SHA256-based |
| **0.5 - 5 MB** | GLM Upload | `glm_upload_file` | Varies | ✅ SHA256-based |
| **> 10 MB** | Supabase Storage | Contact admin | N/A | ✅ SHA256-based |

---

## 🎯 Understanding the System

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│  AI Agent (You)                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 1. Check file size                              │   │
│  │ 2. Select upload method                         │   │
│  │ 3. Execute upload                               │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  EXAI MCP Server (Docker Container)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ File Handler │  │ Kimi Upload  │  │ GLM Upload   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Supabase Storage                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### File Accessibility

**IMPORTANT:** Files must be accessible to the Docker container!

**Mounted Directories (Accessible):**
- `/app/` - Main application directory
- Project files within the container

**Not Mounted (Inaccessible):**
- External Windows paths (C:\Users\..., D:\Data\...)
- Files from other applications

**Solution for External Files:**
- Use file proxy service (if available)
- Copy files to mounted directory
- Contact system administrator

---

## 🔄 File Deduplication (Production-Ready)

### How SHA256-Based Deduplication Works

**Task 1 Status:** ✅ COMPLETE (2025-10-26) - Production-ready

The system automatically prevents duplicate file uploads using SHA256 content hashing:

1. **Hash Calculation** - Each file is hashed using SHA256 algorithm
2. **Database Lookup** - System checks if hash exists for the provider
3. **Cache Check** - Fast in-memory cache for recent files
4. **Reference Counting** - Tracks how many times each file is used
5. **Automatic Cleanup** - Removes unreferenced files after grace period

### Deduplication Benefits

- **Storage Savings** - Prevents duplicate uploads to providers
- **Performance** - Faster uploads for duplicate files (cache hit)
- **Cost Reduction** - Lower API costs for repeated file analysis
- **Bandwidth Efficiency** - Reduces network transfer

### Agent Implementation

```python
from utils.file.deduplication import FileDeduplicationManager

# Initialize deduplication manager
dedup_manager = FileDeduplicationManager(storage_manager)

async def upload_with_deduplication(file_path, provider):
    # Check for duplicates first
    existing = await dedup_manager.check_duplicate_async(file_path, provider)

    if existing:
        # File exists - increment reference and return existing ID
        dedup_manager.increment_reference(existing['provider_file_id'], provider)
        logger.info(f"✅ Using deduplicated file: {existing['provider_file_id']}")
        return existing['provider_file_id']

    # No duplicate - proceed with upload
    if provider == 'kimi':
        result = kimi_upload_files(files=[file_path])
        file_id = result['file_ids'][0]
    else:
        file_id = glm_upload_file(file=file_path)

    # Register new file
    dedup_manager.register_new_file(
        provider_file_id=file_id,
        supabase_file_id=None,
        file_path=file_path,
        provider=provider
    )

    return file_id
```

### Deduplication Metrics

```python
# Get deduplication statistics
metrics = get_dedup_metrics()
print(f"Cache hit rate: {metrics['cache_hit_rate']}%")
print(f"Storage saved: {metrics['storage_saved_bytes']:,} bytes")

# Get database statistics
stats = dedup_manager.get_deduplication_stats()
print(f"Total deduplicated files: {stats['deduplicated_files']}")
print(f"Storage saved: {stats['storage_saved_bytes']:,} bytes")
```

### Best Practices for Deduplication

1. **Always check for duplicates before upload** - Automatic in upload tools
2. **Use async methods for large files (>100MB)** - Better performance
3. **Monitor deduplication metrics regularly** - Track storage savings
4. **Clean up unreferenced files periodically** - Automatic cleanup job
5. **Handle race conditions gracefully** - Built-in UPSERT protection

---

## 🔍 Step-by-Step Guide

### Step 1: Check File Accessibility

```python
from utils.file.cross_platform import get_path_handler
import os

def is_file_accessible(file_path: str) -> tuple[bool, str]:
    """
    Check if file is accessible in Docker container
    
    Returns:
        (accessible: bool, message: str)
    """
    path_handler = get_path_handler()
    normalized, was_converted, error = path_handler.normalize_path(file_path)
    
    if error:
        return False, f"Path normalization failed: {error}"
    
    if normalized.startswith("http"):
        return False, "File requires proxy upload (not mounted)"
    
    if os.path.exists(normalized):
        return True, "File accessible"
    
    return False, "File not found in container"

# Example usage
accessible, message = is_file_accessible("C:\\Project\\file.txt")
if not accessible:
    print(f"⚠️  {message}")
```

### Step 2: Select Upload Method

```python
from utils.file.size_validator import select_upload_method

def choose_upload_method(file_path: str) -> dict:
    """
    Get recommended upload method for file
    
    Returns:
        {
            'method': str,  # 'embedding', 'kimi_upload', 'glm_upload', 'supabase_storage'
            'reason': str,
            'size': int,
            'size_formatted': str,
            'recommendation': str
        }
    """
    return select_upload_method(file_path)

# Example usage
result = choose_upload_method("large_document.pdf")
print(f"Method: {result['method']}")
print(f"Reason: {result['reason']}")
print(f"Recommendation:\n{result['recommendation']}")
```

### Step 3: Execute Upload

#### Method A: Embedding (< 50 KB)

**When to use:** Small text files, configuration files, code snippets

```python
# Direct embedding in prompt
response = chat_EXAI_WS(
    prompt="Analyze this configuration file",
    files=["config.yaml"],  # File embedded directly
    model="glm-4.6"
)
```

**Pros:**
- ✅ Simplest method
- ✅ No upload overhead
- ✅ Immediate availability

**Cons:**
- ❌ Token-intensive for large files
- ❌ Limited to small files

#### Method B: Kimi Upload (0.5 - 10 MB)

**When to use:** Medium-sized documents, PDFs, images

```python
# Step 1: Upload files to Kimi
upload_result = kimi_upload_files(
    files=["document.pdf", "report.docx"],
    purpose="file-extract"
)

# Step 2: Chat with uploaded files
response = kimi_chat_with_files(
    prompt="Summarize these documents",
    file_ids=upload_result['file_ids'],
    model="kimi-k2-0905-preview"
)
```

**Pros:**
- ✅ 70-80% token savings
- ✅ Multi-turn analysis support
- ✅ Persistent file storage

**Cons:**
- ❌ Two-step process
- ❌ Requires file cleanup

#### Method C: GLM Upload (0.5 - 5 MB)

**When to use:** GLM-specific workflows, alternative to Kimi

```python
# Upload file to GLM
file_id = glm_upload_file(
    file="analysis.xlsx",
    purpose="agent"
)

# Use in GLM workflow
# (Integration with GLM tools)
```

**Pros:**
- ✅ GLM-optimized
- ✅ Alternative upload path

**Cons:**
- ❌ Limited to GLM workflows
- ❌ Smaller size limit than Kimi

#### Method D: Supabase Storage (> 10 MB)

**When to use:** Very large files exceeding API limits

```python
# Contact system administrator
# Large files require special handling
```

---

## 🌳 Decision Tree

```
START: Need to upload file
│
├─ Is file accessible in container?
│  ├─ NO → Use proxy upload OR copy to mounted directory
│  └─ YES → Continue
│
├─ What is file size?
│  │
│  ├─ < 50 KB
│  │  └─ Use EMBEDDING (files parameter)
│  │     → chat_EXAI_WS(files=[...])
│  │
│  ├─ 0.5 MB - 10 MB
│  │  └─ Use KIMI UPLOAD
│  │     → kimi_upload_files(files=[...])
│  │     → kimi_chat_with_files(file_ids=[...])
│  │
│  ├─ 0.5 MB - 5 MB (GLM workflow)
│  │  └─ Use GLM UPLOAD
│  │     → glm_upload_file(file=...)
│  │
│  └─ > 10 MB
│     └─ Use SUPABASE STORAGE
│        → Contact administrator
│
END: File uploaded successfully
```

---

## ⚠️ Error Handling

### Common Errors and Solutions

#### Error: "File not accessible in container (not mounted)"

**Cause:** File is outside Docker container's mounted directories

**Solutions:**
1. Copy file to `/app/` directory
2. Use file proxy service (if available)
3. Contact administrator to mount directory

```python
# Solution 1: Copy to mounted directory
import shutil
shutil.copy("C:\\external\\file.txt", "/app/temp/file.txt")
accessible, _ = is_file_accessible("/app/temp/file.txt")
```

#### Error: "Size limit exceeded"

**Cause:** File too large for selected upload method

**Solution:** Use different upload method

```python
# Check recommended method
result = select_upload_method(file_path)
if result['method'] == 'supabase_storage':
    print("File too large for API upload - contact administrator")
else:
    print(f"Use {result['method']} instead")
```

#### Error: "Path normalization failed"

**Cause:** Invalid file path format

**Solution:** Use absolute paths

```python
# ❌ BAD: Relative path
file_path = "../../data/file.txt"

# ✅ GOOD: Absolute path
file_path = "/app/data/file.txt"
```

---

## 📊 Performance Optimization

### Token Savings Comparison

**Example: 2 MB PDF document**

| Method | Tokens Used | Cost | Time |
|--------|-------------|------|------|
| Embedding | ~500,000 | High | Fast |
| Kimi Upload | ~100,000 | Low | Medium |
| **Savings** | **80%** | **80%** | - |

### Best Practices

1. **Always check file size first**
   ```python
   result = select_upload_method(file_path)
   ```

2. **Use Kimi upload for files > 50 KB**
   ```python
   if result['method'] == 'kimi_upload':
       # Use kimi_upload_files
   ```

3. **Clean up uploaded files after use**
   ```python
   # Delete files when done
   kimi_manage_files(operation="delete", file_id=file_id)
   ```

4. **Batch upload multiple files**
   ```python
   # Upload all files at once
   upload_result = kimi_upload_files(files=[file1, file2, file3])
   ```

---

## 🔧 Code Examples

### Complete Workflow Example

```python
from utils.file.size_validator import select_upload_method

def upload_and_analyze(file_path: str, question: str):
    """
    Complete file upload and analysis workflow
    
    Args:
        file_path: Path to file
        question: Question to ask about the file
        
    Returns:
        Analysis result
    """
    # Step 1: Check file accessibility
    accessible, message = is_file_accessible(file_path)
    if not accessible:
        return {"error": message}
    
    # Step 2: Select upload method
    method_info = select_upload_method(file_path)
    
    # Step 3: Execute based on method
    if method_info['method'] == 'embedding':
        # Small file - use direct embedding
        return chat_EXAI_WS(
            prompt=question,
            files=[file_path],
            model="glm-4.6"
        )
    
    elif method_info['method'] == 'kimi_upload':
        # Medium file - use Kimi upload
        upload_result = kimi_upload_files(files=[file_path])
        return kimi_chat_with_files(
            prompt=question,
            file_ids=upload_result['file_ids'],
            model="kimi-k2-0905-preview"
        )
    
    elif method_info['method'] == 'glm_upload':
        # GLM workflow
        file_id = glm_upload_file(file=file_path)
        # Use with GLM tools
        return {"file_id": file_id}
    
    else:
        # Large file - needs admin
        return {"error": "File too large - contact administrator"}

# Usage
result = upload_and_analyze("report.pdf", "Summarize this report")
print(result)
```

---

## 📚 Additional Resources

- **File Size Validator:** `utils/file/size_validator.py`
- **Path Handler:** `utils/file/cross_platform.py`
- **Kimi Upload Tool:** `tools/kimi_upload_files.py`
- **GLM Upload Tool:** `tools/glm_upload_file.py`
- **Architecture Documentation:** `docs/current/FILE_UPLOAD_ARCHITECTURE_AND_MONITORING_IMPROVEMENTS_2025-10-26.md`

---

## 🆘 Getting Help

**If you encounter issues:**

1. Check file accessibility: `is_file_accessible(file_path)`
2. Check recommended method: `select_upload_method(file_path)`
3. Review error messages carefully
4. Check Docker logs: `docker logs exai-mcp-daemon`
5. Contact system administrator for:
   - Files > 10 MB
   - Mounting new directories
   - Proxy service setup

---

**Last Updated:** October 26, 2025  
**EXAI Consultation:** c90cdeec-48bb-4d10-b075-925ebbf39c8a

