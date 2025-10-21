# Files API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Upload, manage, and extract content from files. Both GLM and Kimi providers support file operations.

---

## Endpoints

### Upload File

**POST** `/files`

**Base URLs:**
- GLM: `https://api.z.ai/v1/files`
- Kimi: `https://api.moonshot.ai/v1/files`

### Retrieve File

**GET** `/files/{file_id}`

### Extract File Content

**GET** `/files/{file_id}/content`

### Delete File

**DELETE** `/files/{file_id}`

---

## Upload File

### Request

```python
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677652288,
  "filename": "document.pdf",
  "purpose": "file-extract"
}
```

---

## Retrieve File

### Request

```python
file = client.files.retrieve("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677652288,
  "filename": "document.pdf",
  "purpose": "file-extract"
}
```

---

## Extract File Content

### Request

```python
content = client.files.content("file-abc123")
```

### Response

```json
{
  "content": "Extracted text content from the file...",
  "file_id": "file-abc123"
}
```

---

## Delete File

### Request

```python
client.files.delete("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

---

## Use with Chat Completions

```python
# Upload file
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

# Use in chat
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": file.id},
        {"role": "user", "content": "Summarize this document"}
    ]
)

# Delete file after use
client.files.delete(file.id)
```

---

## Supported File Types

### GLM Provider
- PDF, DOCX, TXT, MD
- Images (JPEG, PNG, GIF, WebP)
- Audio (MP3, WAV, FLAC)
- Video (MP4, AVI, MOV)

### Kimi Provider
- PDF, DOCX, TXT, MD
- Text-based files only

---

## Best Practices

### File Management
- **Delete files after use** to avoid accumulation
- **Track file IDs** for cleanup
- **Verify cleanup** with `files.list()` API
- **Use batch uploads** for multiple files

### Size Limits
- **GLM:** 100MB per file
- **Kimi:** 100MB per file

---

## Provider Support

| Provider | Files Support |
|----------|--------------|
| GLM | ✅ Full support |
| Kimi | ✅ Full support |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../features/multimodal.md](../features/multimodal.md) - Multimodal support
- [../providers/kimi.md](../providers/kimi.md) - Kimi file management best practices

