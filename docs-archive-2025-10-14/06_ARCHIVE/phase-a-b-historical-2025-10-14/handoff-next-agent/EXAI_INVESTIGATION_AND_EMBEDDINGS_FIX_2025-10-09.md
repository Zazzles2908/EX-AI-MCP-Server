# EXAI Tool Call Investigation & Embeddings Fix

**Date:** 2025-10-09 16:40 AEDT  
**Issues:** EXAI-WS tool call confusion + GLM embeddings base URL  
**Status:** ✅ BOTH ISSUES RESOLVED

---

## 🔍 Issue #1: EXAI Tool Call Confusion

### Problem
I was struggling to use EXAI-WS MCP tools correctly, getting validation errors.

### Root Cause
**NOT a fundamental system issue** - just confusion about parameter format!

### ✅ CORRECT Usage Pattern

**Simple Tools (chat):**
```xml
<invoke name="chat_EXAI-WS">
<parameter name="prompt">Your question here
