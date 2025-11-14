# API & Tools Reference

> **Version:** 1.0.0
> **Last Updated:** 2025-11-10
> **Status:** 🟡 **In Progress**

## 🎯 Overview

This section contains the complete API and tools reference for the EX-AI MCP Server, including all 29 MCP tools, provider APIs, integration examples, and endpoint documentation.

## 📚 Documentation Structure

### 🔧 MCP Tools Reference
**Location:** `mcp-tools-reference/`

Complete documentation for all 29 tools:

**Chat Tools (4)**
- `chat` - Primary chat interface
- `chat_with_file` - File-enhanced chat
- `stream_chat` - Streaming responses
- `conversation_summary` - Summarize long conversations

**File Management (8)**
- `upload_file` - Upload to GLM/Kimi providers
- `download_file` - Retrieve files from storage
- `process_file` - Analyze documents, images
- `delete_file` - Clean up uploaded files
- `list_files` - Show uploaded files
- `file_info` - Get file metadata
- `batch_upload` - Upload multiple files
- `file_conversion` - Convert between formats

**Workflow (5)**
- `expert_analysis` - Domain-specific analysis
- `conversation_integration` - Merge multiple conversations
- `workflow_orchestration` - Multi-step automation
- `batch_processing` - Process multiple items
- `task_queue` - Queue and execute tasks

**Provider-Specific (6)**
- `glm_complete` - Direct GLM API access
- `glm_stream` - GLM streaming responses
- `glm_batch` - Batch GLM requests
- `kimi_analyze` - Kimi document analysis
- `kimi_file_chat` - Kimi with file context
- `kimi_vision` - Kimi image analysis

**Storage (4)**
- `save_message` - Persist to Supabase
- `retrieve_messages` - Query message history
- `create_session` - Create new session
- `upload_to_supabase` - Direct Supabase operations

**Utility (2)**
- `health_check` - System health verification
- `list_providers` - Show available providers

**Comprehensive reference** for all available tools.

### 🌐 Provider APIs
**Location:** `provider-apis/`

GLM and Kimi API integration documentation:

**GLM (ZhipuAI) API**
- Available models: glm-4, glm-4.5, glm-4.5-flash, glm-4.6
- API endpoint: `https://api.z.ai/api/paas/v4`
- Authentication: Bearer token
- Rate limits and pricing
- Deep thinking mode
- Streaming support

**Kimi (Moonshot AI) API**
- Available models: moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k
- API endpoint: `https://api.moonshot.ai/v1`
- Authentication: Bearer token
- File processing capabilities
- Large context window (128K tokens)
- Streaming support

**Provider Selection Logic**
- Model selection criteria
- Cost optimization
- Performance considerations
- Fallback mechanisms

**Required for** developers working with AI providers.

### 💻 Integration Examples
**Location:** `integration-examples/`

Code examples for using the API and tools:

**Python Examples**
- WebSocket client implementation
- REST API client
- File upload/download examples
- Streaming response handling
- Error handling patterns

**JavaScript Examples**
- Node.js and browser clients
- WebSocket connections
- Async/await patterns
- Event handling
- File upload with progress

**cURL Examples**
- Command-line usage
- Direct API calls
- Authentication headers
- File uploads
- WebSocket testing

**Real-world Use Cases**
- Chatbot implementation
- File processing pipeline
- Expert analysis workflow
- Multi-provider setup

**Hands-on examples** for quick integration.

## 🔧 MCP Tools Overview (29 Total)

### Tool Categories

#### Chat Tools (4)
- **chat** - Primary chat interface with GLM/Kimi
- **chat_with_file** - Enhanced chat with file context
- **stream_chat** - Real-time streaming responses
- **conversation_summary** - Summarize long conversations

#### File Management (8)
- **upload_file** - Upload to GLM/Kimi providers
- **download_file** - Retrieve files from storage
- **process_file** - Analyze documents, images
- **delete_file** - Clean up uploaded files
- **list_files** - Show uploaded files
- **file_info** - Get file metadata
- **batch_upload** - Upload multiple files
- **file_conversion** - Convert between formats

#### Workflow (5)
- **expert_analysis** - Domain-specific analysis
- **conversation_integration** - Merge multiple conversations
- **workflow_orchestration** - Multi-step automation
- **batch_processing** - Process multiple items
- **task_queue** - Queue and execute tasks

#### Provider-Specific (6)
- **glm_complete** - Direct GLM API access
- **glm_stream** - GLM streaming responses
- **glm_batch** - Batch GLM requests
- **kimi_analyze** - Kimi document analysis
- **kimi_file_chat** - Kimi with file context
- **kimi_vision** - Kimi image analysis

#### Storage (4)
- **save_message** - Persist to Supabase
- **retrieve_messages** - Query message history
- **create_session** - Create new session
- **upload_to_supabase** - Direct Supabase operations

#### Utility (2)
- **health_check** - System health verification
- **list_providers** - Show available providers

## 🌐 API Endpoints

### WebSocket API (Primary Interface)
- **Endpoint**: `ws://localhost:3000` (production: `wss://your-domain.com:3000`)
- **Protocol**: WebSocket with JSON messages
- **Authentication**: JWT Bearer token in headers
- **Bidirectional**: Real-time communication

### HTTP Health API
- **Endpoint**: `http://localhost:3001/health`
- **Purpose**: Health checks and monitoring
- **Response Format**: JSON
- **No Auth Required**: For monitoring tools

### Metrics API
- **Endpoint**: `http://localhost:3002/metrics`
- **Format**: Prometheus-compatible
- **Metrics**: Request count, latency, errors, provider health
- **No Auth Required**: For monitoring systems

## 📚 Related Documentation

- **System Architecture**: [../01-architecture-overview/01_system_architecture.md](../01-architecture-overview/01_system_architecture.md)
- **Security & Authentication**: [../03-security-authentication/](../03-security-authentication/)

## 🔗 Quick Links

- **MCP Tools**: [mcp-tools-reference/](mcp-tools-reference/)
- **Provider APIs**: [provider-apis/](provider-apis/)
- **Integration Examples**: [integration-examples/](integration-examples/)
- **Main Documentation**: [../index.md](../index.md)

---

**Document Version:** 1.0.0
**Created:** 2025-11-10
**Author:** EX-AI MCP Server API Team
**Status:** 🟡 **In Progress - API & Tools documentation being created**
