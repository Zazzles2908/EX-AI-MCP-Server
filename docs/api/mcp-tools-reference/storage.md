# MCP Storage Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 4 Storage Tools available in the EX-AI MCP Server. These tools provide direct access to Supabase database operations, including message persistence, session management, and data retrieval.

---

## 📚 Tool Categories

### 💾 Storage Tools (4 Total)
- **save_message** - Persist messages to Supabase
- **retrieve_messages** - Query message history
- **create_session** - Create new session
- **upload_to_supabase** - Direct Supabase operations

---

## 💾 Tool Details

### 1. save_message

**Description:** Save chat messages to Supabase database

**Parameters:**
- `session_id` (string, required) - Session identifier
- `content` (string, required) - Message content
- `role` (string, required) - Role: 'user', 'assistant', 'system'
- `metadata` (object, optional) - Additional metadata
- `model` (string, optional) - AI model used
- `provider` (string, optional) - Provider used

**Example Usage:**
```python
# Save user message
exai_mcp.save_message(
    session_id="session_123",
    content="Explain quantum computing",
    role="user",
    metadata={
        "timestamp": "2025-11-10T10:00:00Z"
    }
)

# Save assistant response
exai_mcp.save_message(
    session_id="session_123",
    content="Quantum computing is a revolutionary technology...",
    role="assistant",
    model="glm-4.6",
    provider="glm"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "message_id": "msg_abc123",
    "session_id": "session_123",
    "saved_at": "2025-11-10T10:00:00Z"
  }
}
```

---

### 2. retrieve_messages

**Description:** Query message history from Supabase

**Parameters:**
- `session_id` (string, required) - Session identifier
- `limit` (int, optional) - Maximum messages (default: 100)
- `offset` (int, optional) - Pagination offset
- `role` (string, optional) - Filter by role
- `since` (string, optional) - Return messages since timestamp

**Example Usage:**
```python
# Get session messages
messages = exai_mcp.retrieve_messages(
    session_id="session_123",
    limit=50
)

# Get recent messages
recent = exai_mcp.retrieve_messages(
    session_id="session_123",
    since="2025-11-10T10:00:00Z"
)
```

---

### 3. create_session

**Description:** Create new chat session

**Parameters:**
- `session_id` (string, optional) - Custom session ID
- `metadata` (object, optional) - Session metadata
- `user_id` (string, optional) - Associated user ID

**Example Usage:**
```python
# Create session
session = exai_mcp.create_session(
    metadata={
        "project": "security_audit",
        "created_by": "alice@example.com"
    }
)
```

---

### 4. upload_to_supabase

**Description:** Direct Supabase database operations

**Parameters:**
- `table` (string, required) - Table name
- `data` (object, required) - Data to insert
- `operation` (string, optional) - Operation: 'insert', 'update', 'upsert'

**Example Usage:**
```python
# Insert custom data
result = exai_mcp.upload_to_supabase(
    table="custom_data",
    data={
        "key": "value",
        "metadata": {}
    }
)
```

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Storage Tools Reference**
