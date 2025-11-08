# Cognee Integration Guide
**Coordinating EXAI MCP Server with Cognee for Semantic Search**

---

## 🎯 Purpose

Enable semantic search and knowledge graph capabilities by syncing EXAI operations to Cognee.

---

## 📋 Integration Pattern

### After Each EXAI Operation:

```python
# In your code after save_conversation or save_message
await cognee.add({
    "type": "conversation",
    "continuation_id": "conversation-id",
    "content": "conversation content",
    "schema": "chat",
    "source": "exai_mcp_server",
    "timestamp": "2025-11-08T01:42:07Z"
})

# Build knowledge graph
await cognee.cognify()
```

---

## 🔗 Cognee Coordinates

- **Cognee API Port:** 8001
- **Knowledge Graph Endpoint:** http://localhost:8001/graph
- **Semantic Search:** http://localhost:8001/search

---

## 📊 Data Sync to Cognee

### Conversation Data:
- Continuation ID
- Title
- Metadata
- Schema source (chat)
- Timestamp

### Message Data:
- Conversation reference
- Role (user/assistant/system)
- Content
- Metadata
- Timestamp

### Monitoring Events:
- Event type
- Event category
- Correlation ID
- Event data

---

## 🏗️ Implementation

### Add to save_conversation():
```python
# After successful save
if correlation_id and cognee_client:
    await cognee_client.add({
        "type": "conversation",
        "continuation_id": continuation_id,
        "title": title,
        "metadata": metadata,
        "schema": "chat",
        "source": "exai_mcp_server"
    })
    await cognee_client.cognify()
```

### Add to save_message():
```python
# After successful save
if correlation_id and cognee_client:
    await cognee_client.add({
        "type": "message",
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
        "metadata": metadata,
        "schema": "chat",
        "source": "exai_mcp_server"
    })
    await cognee_client.cognify()
```

---

## 🔍 Search Examples

```python
# Search EXAI conversations in Cognee
results = await cognee_client.search(
    "schema:chat AND source:exai_mcp_server"
)

# Search by continuation_id
conversation = await cognee_client.get(
    "continuation_id:your-conversation-id"
)
```

---

## 📈 Benefits

1. **Semantic Search** - Find conversations by meaning
2. **Knowledge Graph** - Visualize relationships
3. **Cross-System Discovery** - Find related content
4. **Orchestrator Integration** - Share insights between systems

---

**Status:** Documentation Created ✅
**Next Step:** Implement cognee.add() calls in storage_manager.py
**Priority:** Medium - Enhances discovery capabilities
