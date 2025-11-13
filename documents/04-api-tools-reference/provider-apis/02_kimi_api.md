# Kimi (Moonshot AI) API Integration Guide

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This guide covers Kimi (Moonshot AI) provider integration with the EX-AI MCP Server, including available models, file processing, vision capabilities, and best practices.

---

## 📊 Kimi Provider Overview

### Available Models
- **moonshot-v1-128k** - 128K context, 8K output (Recommended)
- **moonshot-v1-32k** - 32K context, 8K output
- **moonshot-v1-8k** - 8K context, 8K output

### API Endpoint
```
https://api.moonshot.ai/v1/chat/completions
```

### Authentication
```python
headers = {
    "Authorization": f"Bearer {KIMI_API_KEY}",
    "Content-Type": "application/json"
}
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Kimi API Integration Guide**
