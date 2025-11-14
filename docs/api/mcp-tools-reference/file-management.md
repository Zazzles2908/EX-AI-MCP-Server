# MCP File Management Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 8 File Management Tools available in the EX-AI MCP Server. These tools provide comprehensive file upload, download, processing, and management capabilities for both GLM and Kimi providers.

---

## 📚 Tool Categories

### 💾 File Management Tools (8 Total)
- **upload_file** - Upload files to GLM/Kimi providers
- **download_file** - Retrieve files from provider storage
- **process_file** - Analyze documents, images, and code
- **delete_file** - Clean up uploaded files
- **list_files** - Show uploaded files with metadata
- **file_info** - Get detailed file information
- **batch_upload** - Upload multiple files efficiently
- **file_conversion** - Convert between file formats

---

## 💾 Tool Details

### 1. upload_file

**Description:** Upload files to GLM and Kimi providers for processing

**Parameters:**
- `file_path` (string, required) - Local file path
- `provider` (string, optional) - 'glm' or 'kimi' (auto-selects)
- `file_type` (string, optional) - Type: 'document', 'image', 'code', 'data'
- `metadata` (object, optional) - Additional metadata to store

**Example Usage:**
```python
# Upload document
result = exai_mcp.upload_file(
    file_path="/path/to/document.pdf",
    provider="kimi",
    file_type="document"
)

# Upload with metadata
result = exai_mcp.upload_file(
    file_path="/path/to/code.py",
    provider="glm",
    file_type="code",
    metadata={
        "language": "python",
        "purpose": "authentication"
    }
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "provider": "kimi",
    "url": "https://api.moonshot.ai/files/abc123",
    "size": 1024576,
    "type": "document",
    "upload_time": "2025-11-10T10:30:00Z",
    "expires_at": "2025-12-10T10:30:00Z"
  }
}
```

**Supported File Types:**
- **Documents**: .pdf, .docx, .txt, .md
- **Images**: .png, .jpg, .jpeg, .gif
- **Code**: .py, .js, .ts, .java, .cpp, .c, .go, .rs
- **Data**: .csv, .xlsx, .json, .xml
- **Max size**: 100MB per file

---

### 2. download_file

**Description:** Download files from provider storage to local filesystem

**Parameters:**
- `file_id` (string, required) - Provider file ID
- `output_path` (string, required) - Local output path
- `provider` (string, optional) - Provider (auto-detects)

**Example Usage:**
```python
# Download by file_id
exai_mcp.download_file(
    file_id="file_abc123",
    output_path="/downloads/document.pdf"
)

# Download with provider specified
exai_mcp.download_file(
    file_id="file_xyz789",
    output_path="/downloads/image.png",
    provider="kimi"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "output_path": "/downloads/document.pdf",
    "size": 1024576,
    "checksum": "sha256:abc123...",
    "download_time": "2025-11-10T10:35:00Z"
  }
}
```

---

### 3. process_file

**Description:** Analyze and extract insights from uploaded files

**Parameters:**
- `file_id` (string, required) - Provider file ID or local path
- `analysis_type` (string, required) - Type: 'content', 'summary', 'extract', 'translate'
- `options` (object, optional):
  - `language` (string) - Target language for translation
  - `extract_fields` (array) - Fields to extract from documents
  - `max_summary_length` (int) - Maximum summary length

**Example Usage:**
```python
# Extract text content
content = exai_mcp.process_file(
    file_id="file_abc123",
    analysis_type="content"
)

# Generate summary
summary = exai_mcp.process_file(
    file_id="file_abc123",
    analysis_type="summary",
    options={
        "max_summary_length": 500
    }
)

# Extract specific data
data = exai_mcp.process_file(
    file_id="invoice.pdf",
    analysis_type="extract",
    options={
        "extract_fields": ["amount", "date", "vendor"]
    }
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "analysis_type": "summary",
    "content": "This document discusses...",
    "insights": [
      "Key finding 1",
      "Key finding 2"
    ],
    "metadata": {
      "page_count": 5,
      "word_count": 1250,
      "language": "en"
    },
    "processing_time": 2.3
  }
}
```

---

### 4. delete_file

**Description:** Remove files from provider storage

**Parameters:**
- `file_id` (string, required) - Provider file ID
- `provider` (string, optional) - Provider (auto-detects)
- `force` (boolean, optional) - Force deletion even if in use

**Example Usage:**
```python
# Delete single file
result = exai_mcp.delete_file(
    file_id="file_abc123"
)

# Force delete
result = exai_mcp.delete_file(
    file_id="file_abc123",
    force=True
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "deleted_at": "2025-11-10T10:40:00Z",
    "freed_space": 1024576
  }
}
```

---

### 5. list_files

**Description:** List all uploaded files with metadata

**Parameters:**
- `provider` (string, optional) - Filter by provider
- `file_type` (string, optional) - Filter by type
- `limit` (int, optional) - Maximum files to return (default: 100)
- `offset` (int, optional) - Pagination offset

**Example Usage:**
```python
# List all files
files = exai_mcp.list_files()

# Filter by provider
files = exai_mcp.list_files(
    provider="kimi"
)

# Filter by type
files = exai_mcp.list_files(
    file_type="document"
)

# Paginate results
files = exai_mcp.list_files(
    limit=50,
    offset=0
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "files": [
      {
        "file_id": "file_abc123",
        "provider": "kimi",
        "filename": "document.pdf",
        "size": 1024576,
        "type": "document",
        "uploaded_at": "2025-11-10T10:30:00Z",
        "expires_at": "2025-12-10T10:30:00Z"
      }
    ],
    "total": 45,
    "has_more": true
  }
}
```

---

### 6. file_info

**Description:** Get detailed information about a specific file

**Parameters:**
- `file_id` (string, required) - Provider file ID
- `provider` (string, optional) - Provider (auto-detects)

**Example Usage:**
```python
# Get file details
info = exai_mcp.file_info(
    file_id="file_abc123"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "file_id": "file_abc123",
    "provider": "kimi",
    "filename": "document.pdf",
    "size": 1024576,
    "type": "document",
    "mime_type": "application/pdf",
    "uploaded_at": "2025-11-10T10:30:00Z",
    "expires_at": "2025-12-10T10:30:00Z",
    "download_count": 5,
    "last_accessed": "2025-11-10T10:35:00Z",
    "metadata": {
      "page_count": 15,
      "language": "en"
    }
  }
}
```

---

### 7. batch_upload

**Description:** Upload multiple files efficiently in a single request

**Parameters:**
- `file_paths` (array, required) - List of file paths
- `provider` (string, optional) - Provider (auto-selects per file)
- `file_types` (array, optional) - List of file types
- `parallel` (boolean, optional) - Upload in parallel (default: true)

**Example Usage:**
```python
# Batch upload files
results = exai_mcp.batch_upload(
    file_paths=[
        "/path/to/file1.pdf",
        "/path/to/file2.png",
        "/path/to/file3.py"
    ]
)

# With type specification
results = exai_mcp.batch_upload(
    file_paths=["/path/to/doc1.pdf", "/path/to/doc2.pdf"],
    file_types=["document", "document"]
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "uploaded": [
      {
        "file_path": "/path/to/file1.pdf",
        "file_id": "file_abc123",
        "status": "success"
      }
    ],
    "failed": [
      {
        "file_path": "/path/to/file2.pdf",
        "error": "File too large",
        "status": "failed"
      }
    ],
    "total": 3,
    "successful": 2,
    "failed_count": 1
  }
}
```

---

### 8. file_conversion

**Description:** Convert files between different formats

**Parameters:**
- `file_id` (string, required) - Source file ID or path
- `target_format` (string, required) - Target format
- `output_path` (string, optional) - Output file path
- `options` (object, optional) - Conversion options

**Example Usage:**
```python
# Convert PDF to text
result = exai_mcp.file_conversion(
    file_id="file_abc123",
    target_format="txt",
    output_path="/converted/document.txt"
)

# Convert image format
result = exai_mcp.file_conversion(
    file_id="image.png",
    target_format="jpg",
    options={
        "quality": 90
    }
)
```

**Supported Conversions:**
- **PDF → TXT, MD, JSON**
- **DOCX → TXT, PDF**
- **Images → PNG, JPG, WEBP**
- **CSV → JSON, XLSX**
- **JSON → CSV, YAML**

**Response Format:**
```json
{
  "success": true,
  "data": {
    "source_file": "document.pdf",
    "target_format": "txt",
    "output_path": "/converted/document.txt",
    "conversion_time": 1.5,
    "size_reduction": "85%"
  }
}
```

---

## 🔄 Workflow Examples

### Example 1: Document Analysis Pipeline
```python
# 1. Upload document
upload_result = exai_mcp.upload_file(
    file_path="/docs/contract.pdf",
    provider="kimi",
    file_type="document"
)

# 2. Process for content extraction
content = exai_mcp.process_file(
    file_id=upload_result.data.file_id,
    analysis_type="extract",
    options={
        "extract_fields": ["party_names", "dates", "amounts"]
    }
)

# 3. Generate summary
summary = exai_mcp.process_file(
    file_id=upload_result.data.file_id,
    analysis_type="summary"
)

# 4. Get file info
info = exai_mcp.file_info(
    file_id=upload_result.data.file_id
)
```

### Example 2: Code Review Workflow
```python
# 1. Batch upload code files
results = exai_mcp.batch_upload(
    file_paths=[
        "/src/auth.py",
        "/src/api.py",
        "/src/config.py"
    ],
    file_types=["code", "code", "code"]
)

# 2. Process each file
for file_result in results.data.uploaded:
    analysis = exai_mcp.process_file(
        file_id=file_result.file_id,
        analysis_type="content"
    )
    # Store analysis results

# 3. Clean up
for file_result in results.data.uploaded:
    exai_mcp.delete_file(
        file_id=file_result.file_id
    )
```

### Example 3: Image Processing Pipeline
```python
# 1. Upload images
upload_result = exai_mcp.upload_file(
    file_path="/images/screenshot.png",
    provider="kimi",
    file_type="image"
)

# 2. Process for OCR/text extraction
text = exai_mcp.process_file(
    file_id=upload_result.data.file_id,
    analysis_type="content"
)

# 3. Convert to different format
converted = exai_mcp.file_conversion(
    file_id=upload_result.data.file_id,
    target_format="jpg",
    output_path="/images/screenshot.jpg",
    options={
        "quality": 85
    }
)
```

---

## ⚙️ Advanced Configuration

### File Metadata Schema
```python
metadata = {
    "project": "exai-mcp",
    "version": "1.0.0",
    "author": "user@example.com",
    "tags": ["security", "audit"],
    "custom_fields": {
        "classification": "confidential",
        "retention": "90_days"
    }
}
```

### Provider-Specific Options
```python
# GLM provider options
glm_options = {
    "model": "glm-4.5",
    "language": "en",
    "region": "us-east"
}

# Kimi provider options
kimi_options = {
    "model": "moonshot-v1-128k",
    "ocr_enabled": True,
    "language_detection": True
}
```

---

## 📊 Performance Metrics

### Upload Performance
- **Small files** (<1MB): 500-1000ms
- **Medium files** (1-10MB): 1-3 seconds
- **Large files** (10-100MB): 5-15 seconds
- **Batch upload**: 2-5x faster with parallel processing

### Processing Times
- **Text extraction**: 0.5-2 seconds
- **Image OCR**: 1-3 seconds
- **Document analysis**: 2-8 seconds
- **Code review**: 3-10 seconds

### Storage Limits
- **Per provider**: 10GB storage
- **Per file**: 100MB maximum
- **Retention period**: 30 days (auto-delete)
- **Batch limit**: 50 files per request

---

## 🔍 Troubleshooting

### Common Issues

**Issue: "File too large"**
- Maximum file size: 100MB
- Solution: Compress file or split into smaller parts
- Use batch_upload for multiple smaller files

**Issue: "Unsupported file type"**
- Check supported types in documentation
- Convert file to supported format using file_conversion
- Use process_file with appropriate analysis_type

**Issue: "File not found"**
- Verify file_id is correct
- Check if file still exists (retention: 30 days)
- Ensure proper permissions

**Issue: "Upload timeout"**
- Large files may timeout
- Use chunked upload (automatic for >10MB)
- Check network stability
- Retry with smaller files

### Error Codes
- `400`: Invalid file or parameters
- `413`: File too large
- `415`: Unsupported file type
- `422`: File corrupted or invalid
- `429`: Rate limit exceeded
- `500`: Provider error
- `503`: Storage service unavailable

---

## 📚 Related Documentation

- **Chat Tools**: [01_chat_tools.md](01_chat_tools.md)
- **Workflow Tools**: [03_workflow.md](03_workflow.md)
- **Provider APIs**: [../../provider-apis/](../../provider-apis/)
- **System Architecture**: [../../../../01-architecture-overview/01_system_architecture.md](../../../../01-architecture-overview/01_system_architecture.md)

---

## 🔗 Quick Links

- **Chat Tools**: [01_chat_tools.md](01_chat_tools.md)
- **File Management**: This document
- **Workflow Tools**: [03_workflow.md](03_workflow.md)
- **Provider APIs**: [../../provider-apis/../../provider-apis/)
- **Main Documentation**: [../../../../index.md](../../../../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - File Management Tools Reference**
