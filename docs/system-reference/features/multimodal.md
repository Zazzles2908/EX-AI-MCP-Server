# Multimodal Support

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/glm.md](../providers/glm.md)

---

## Overview

Process images, audio, video, and files alongside text for comprehensive AI interactions. Multimodal support is available for GLM provider only.

**Note:** Multimodal support is only available for GLM provider, not Kimi.

---

## Supported Modalities

### Images
- **Models:** GLM-4.5V, GLM-4.5V-plus
- **Formats:** JPEG, PNG, GIF, WebP
- **Max Size:** 20MB per image
- **Use Cases:** Image analysis, OCR, visual Q&A

### Audio
- **Models:** GLM-4-audio
- **Formats:** MP3, WAV, FLAC
- **Max Duration:** 30 minutes
- **Use Cases:** Transcription, audio analysis

### Video
- **Models:** GLM-4V-flash
- **Formats:** MP4, AVI, MOV
- **Max Duration:** 10 minutes
- **Use Cases:** Video analysis, content extraction

### Files
- **Models:** All GLM models
- **Formats:** PDF, DOCX, TXT, MD
- **Max Size:** 100MB per file
- **Use Cases:** Document analysis, content extraction

---

## Usage

### Image Analysis

```python
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://..."}}
            ]
        }
    ]
)
```

### File Upload

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
```

---

## Provider Support

| Provider | Multimodal Support |
|----------|-------------------|
| GLM | ✅ Images, audio, video, files |
| Kimi | ❌ Text only |

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [../api/files.md](../api/files.md) - File management API

