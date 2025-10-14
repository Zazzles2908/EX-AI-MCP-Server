# Architecture Documentation
**System design, patterns, and architectural decisions**

---

## 📚 Contents

### Core Documents

- **`DEPENDENCY_MAP.md`** - Complete dependency graph and module relationships
- **`DESIGN_INTENT.md`** - Design philosophy and architectural principles

---

## 🏗️ Architecture Overview

The EX-AI MCP Server follows a modular architecture with:

1. **Provider Layer** - AI model integrations (Kimi, GLM)
2. **Tool Layer** - MCP tools (simple, workflow, provider-specific)
3. **Server Layer** - WebSocket daemon and request handling
4. **Storage Layer** - Supabase integration for persistence

---

## 🔗 Related Documentation

- **API Reference:** `../03_API_REFERENCE/`
- **System Reference:** `../system-reference/`
- **Current Work:** `../05_CURRENT_WORK/`

---

**Last Updated:** 2025-10-14

