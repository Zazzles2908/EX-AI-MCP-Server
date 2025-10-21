# API Endpoints Reference

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [02-provider-architecture.md](02-provider-architecture.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

This document provides an overview of all API endpoints available in the EX-AI-MCP-Server. For detailed documentation on each endpoint, see the linked pages below.

---

## Base URLs

### International Users (api.z.ai)

**Primary Base URL:**
```
https://api.z.ai/v1
```

**Full API Path:**
```
https://api.z.ai/api/paas/v4/
```

**Alternative Endpoints:**
- **Anthropic-compatible:** `https://api.z.ai/api/anthropic`
- **Coding-specific:** `https://api.z.ai/api/coding/paas/v4`

---

## API Endpoints

### Authentication
Bearer token authentication for all API requests.

**📖 For complete authentication documentation, see:** [api/authentication.md](api/authentication.md)

---

### Chat Completions
Primary endpoint for conversational AI interactions.

**📖 For complete chat completions documentation, see:** [api/chat-completions.md](api/chat-completions.md)

---

### Embeddings
Generate vector embeddings for text.

**📖 For complete embeddings documentation, see:** [api/embeddings.md](api/embeddings.md)

---

### Files
Upload, manage, and extract content from files.

**📖 For complete files documentation, see:** [api/files.md](api/files.md)

---

### Web Search
Native web search integration (GLM provider only).

**📖 For complete web search documentation, see:** [api/web-search.md](api/web-search.md)

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/completions` | POST | Conversational AI |
| `/embeddings` | POST | Vector embeddings |
| `/files` | POST | Upload files |
| `/files/{id}` | GET | Retrieve file |
| `/files/{id}/content` | GET | Extract file content |
| `/files/{id}` | DELETE | Delete file |

---

## Related Documentation

- [api/authentication.md](api/authentication.md) - Authentication details
- [api/chat-completions.md](api/chat-completions.md) - Chat completions endpoint
- [api/embeddings.md](api/embeddings.md) - Embeddings endpoint
- [api/files.md](api/files.md) - Files management
- [api/web-search.md](api/web-search.md) - Web search integration
- [02-provider-architecture.md](02-provider-architecture.md) - Provider details
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Feature details

