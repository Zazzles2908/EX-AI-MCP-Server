# MCP Chat Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** ✅ **Complete**

## 🎯 Overview

This section documents the 4 Chat Tools available in the EX-AI MCP Server. These tools provide primary chat interfaces with GLM-4.6 and Kimi K2 models, including file-enhanced chat, streaming responses, and conversation management.

---

## 📚 Tool Categories

### 🔧 Chat Tools (4 Total)
- **chat** - Primary chat interface with intelligent provider routing
- **chat_with_file** - Enhanced chat with file context and analysis
- **stream_chat** - Real-time streaming responses for interactive conversations
- **conversation_summary** - Summarize long conversations for context

---

## 💬 Tool Details

### 1. chat

**Description:** Primary chat interface with GLM-4.6 and Kimi K2 models

**Parameters:**
- `message` (string, required) - The user's message
- `model` (string, optional) - Specific model to use (auto-selects if not specified)
- `provider` (string, optional) - 'glm' or 'kimi' (auto-routes if not specified)
- `session_id` (string, optional) - Session identifier for context
- `stream` (boolean, optional) - Enable streaming responses (default: false)

**Example Usage:**
```python
# Basic chat
response = exai_mcp.chat("Explain quantum computing")

# With specific model
response = exai_mcp.chat(
    message="Analyze this code",
    model="glm-4.6",
    provider="glm"
)

# With session context
response = exai_mcp.chat(
    message="Continue our discussion",
    session_id="session_123"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "response": "Quantum computing is a revolutionary technology...",
    "model": "glm-4.6",
    "provider": "glm",
    "session_id": "sess_abc123",
    "tokens_used": 245,
    "response_time": 1.2
  }
}
```

**Intelligent Routing:**
- **GLM-4.6**: Used for complex reasoning, coding, and analysis
- **Kimi K2**: Used for file processing, document analysis, and large context tasks
- Auto-selection based on message complexity and file attachments

---

### 2. chat_with_file

**Description:** Enhanced chat interface with file context and AI-powered analysis

**Parameters:**
- `message` (string, required) - The user's message
- `files` (array, optional) - List of file paths to analyze
- `model` (string, optional) - Model to use (auto-selects)
- `analysis_type` (string, optional) - Type of analysis: 'general', 'security', 'performance', 'architecture'
- `language` (string, optional) - Programming language if applicable

**Example Usage:**
```python
# Analyze code files
response = exai_mcp.chat_with_file(
    message="Review this code for security issues",
    files=["/path/to/app.py", "/path/to/config.py"],
    analysis_type="security"
)

# Analyze documents
response = exai_mcp.chat_with_file(
    message="Summarize these requirements",
    files=["/path/to/requirements.pdf", "/path/to/specs.docx"]
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "response": "Security analysis complete. Found 3 issues...",
    "files_analyzed": 2,
    "issues_found": [
      {
        "file": "app.py",
        "line": 42,
        "severity": "high",
        "type": "SQL Injection",
        "description": "User input not sanitized"
      }
    ],
    "model": "glm-4.6",
    "analysis_time": 3.4
  }
}
```

**File Support:**
- **Text files**: .txt, .md, .py, .js, .ts, .java, .cpp, .c, .go, .rs
- **Documents**: .pdf, .docx, .xlsx, .csv
- **Images**: .png, .jpg, .jpeg (via Kimi vision)
- **Max file size**: 100MB per file
- **Max files**: 10 per request

---

### 3. stream_chat

**Description:** Real-time streaming chat for interactive conversations

**Parameters:**
- `message` (string, required) - The user's message
- `model` (string, optional) - Model to use
- `stream_options` (object, optional):
  - `chunk_size` (int) - Size of each chunk (default: 10 tokens)
  - `delay_ms` (int) - Delay between chunks (default: 50ms)
- `session_id` (string, optional) - Session identifier

**Example Usage:**
```python
# Streaming response
stream = exai_mcp.stream_chat(
    message="Write a detailed explanation of machine learning",
    stream_options={
        "chunk_size": 15,
        "delay_ms": 100
    }
)

# Consume stream
for chunk in stream:
    print(chunk, end="", flush=True)
```

**Stream Event Format:**
```json
{
  "event": "token",
  "data": {
    "token": "Machine",
    "sequence": 1,
    "timestamp": "2025-11-10T10:30:00Z"
  }
}

{
  "event": "complete",
  "data": {
    "total_tokens": 450,
    "response_time": 2.1,
    "session_id": "sess_stream_001"
  }
}
```

**Use Cases:**
- Interactive coding sessions
- Real-time analysis feedback
- Conversational AI applications
- Educational content delivery

---

### 4. conversation_summary

**Description:** Summarize long conversations and extract key insights

**Parameters:**
- `session_id` (string, required) - Session to summarize
- `summary_type` (string, optional) - Type: 'brief', 'detailed', 'action_items', 'decisions'
- `max_length` (int, optional) - Maximum summary length in words (default: 500)
- `language` (string, optional) - Summary language (default: 'en')

**Example Usage:**
```python
# Brief summary
summary = exai_mcp.conversation_summary(
    session_id="session_123",
    summary_type="brief"
)

# Action items extraction
actions = exai_mcp.conversation_summary(
    session_id="session_123",
    summary_type="action_items"
)
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "summary": "The conversation covered three main topics: security audit findings...",
    "summary_type": "detailed",
    "key_points": [
      "Found 3 critical security issues in web_ui/index.html",
      "Created comprehensive documentation structure",
      "Fixed exposed Supabase credentials"
    ],
    "action_items": [
      {
        "task": "Rotate exposed Supabase credentials",
        "priority": "critical",
        "assigned_to": "security_team"
      }
    ],
    "decisions": [
      "Use kimi-k2-thinking for documentation generation",
      "Replace all index.md with unique filenames"
    ],
    "message_count": 45,
    "summary_length": 320
  }
}
```

**Summary Types:**
- **brief**: 2-3 sentence overview
- **detailed**: Comprehensive summary with key points
- **action_items**: Extract all tasks and to-dos
- **decisions**: Track decisions made in conversation

---

## 🔄 Workflow Examples

### Example 1: Multi-Turn Chat with Context
```python
# Start conversation
response1 = exai_mcp.chat(
    message="I need to analyze my codebase",
    session_id="audit_session"
)

# Continue with files
response2 = exai_mcp.chat_with_file(
    message="Now analyze these security-critical files",
    files=["/path/to/auth.py", "/path/to/api.py"],
    session_id="audit_session"
)

# Get summary
summary = exai_mcp.conversation_summary(
    session_id="audit_session",
    summary_type="action_items"
)
```

### Example 2: Interactive Coding Session
```python
# Start coding session
stream = exai_mcp.stream_chat(
    message="Help me write a Python authentication module with JWT",
    model="glm-4.6"
)

# Stream response for real-time feedback
for chunk in stream:
    print(chunk)
```

### Example 3: Document Analysis Workflow
```python
# Upload and analyze documents
response = exai_mcp.chat_with_file(
    message="Analyze these requirements and suggest architecture",
    files=["/path/to/requirements.pdf"],
    analysis_type="architecture"
)

# Follow-up questions
response2 = exai_mcp.chat(
    message="Can you elaborate on the microservices suggestion?",
    session_id=response.data.session_id
)
```

---

## ⚙️ Advanced Configuration

### Custom Model Selection
```python
# Force specific model
response = exai_mcp.chat(
    message="Complex architectural analysis",
    model="glm-4.6",
    provider="glm"
)

# Use Kimi for file-heavy tasks
response = exai_mcp.chat_with_file(
    message="Analyze 10 code files for patterns",
    files=["file1.py", "file2.py", ...],
    model="moonshot-v1-128k",
    provider="kimi"
)
```

### Session Management
```python
# Create named session
response = exai_mcp.chat(
    message="Start security audit",
    session_id="security_audit_2025"
)

# All subsequent calls with same session_id maintain context
# Session data stored in Supabase for persistence
```

---

## 📊 Performance Metrics

### Response Times (95th percentile)
- **Simple chat**: 1-3 seconds
- **File analysis**: 5-15 seconds
- **Streaming**: 100-500ms first token
- **Summary generation**: 2-5 seconds

### Token Limits
- **GLM-4.6**: 128K tokens context, 8K output
- **Kimi K2**: 128K tokens context, 8K output
- **Streaming**: No output limit (streams until complete)

### Rate Limits
- **Per session**: 100 requests/minute
- **Global**: 1000 requests/minute
- **Files**: 50 uploads/hour per session

---

## 🔍 Troubleshooting

### Common Issues

**Issue: "Model not available"**
- Check if API keys are set correctly
- Verify provider status: GLM or Kimi
- Ensure model name is valid

**Issue: "File upload failed"**
- Check file size (<100MB)
- Verify file type is supported
- Ensure file path is accessible

**Issue: "Session expired"**
- Sessions expire after 24 hours of inactivity
- Use session_id to maintain context
- Reinitialize session for new conversations

**Issue: "Streaming interrupted"**
- Connection timeout: 30 seconds
- Retry with smaller chunk_size
- Check network stability

### Error Codes
- `400`: Invalid parameters
- `401`: Authentication failed
- `429`: Rate limit exceeded
- `500`: Provider error
- `503`: Service unavailable

---

## 📚 Related Documentation

- **API Reference**: [../API_TOOLS_REFERENCE.md](../API_TOOLS_REFERENCE.md)
- **Provider APIs**: [../provider-apis/](../provider-apis/)
- **Integration Examples**: [../integration-examples/](../integration-examples/)
- **System Architecture**: [../../01-architecture-overview/01_system_architecture.md](../../01-architecture-overview/01_system_architecture.md)

---

## 🔗 Quick Links

- **Chat Tools**: This document
- **File Management**: [02_file_management.md](02_file_management.md)
- **Workflow Tools**: [03_workflow.md](03_workflow.md)
- **Provider APIs**: [../provider-apis/](../provider-apis/)
- **Main Documentation**: [../../../index.md../../../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** ✅ **Complete - Chat Tools Reference**
