# API Reference Documentation
**Last Updated:** 2025-10-14 (14th October 2025)  
**Purpose:** Provider API documentation, tool schemas, and environment variables

---

## 📚 Contents

### Provider APIs

#### [GLM_API_REFERENCE.md](GLM_API_REFERENCE.md)
**GLM (ZhipuAI) API Documentation**
- Base URL: `https://api.z.ai/api/paas/v4`
- Models: glm-4.6, glm-4.5, glm-4.5-flash, glm-4.5-air
- Features: Thinking mode, web search, function calling, retrieval
- Tool types: function, retrieval, web_search

#### [KIMI_API_REFERENCE.md](KIMI_API_REFERENCE.md)
**Kimi (Moonshot AI) API Documentation**
- Base URL: `https://api.moonshot.ai/v1`
- **OpenAI SDK Compatible:** Uses OpenAI SDK format for all parameters
- Models: kimi-k2-0905-preview, kimi-k2-turbo-preview, kimi-thinking-preview
- Features: Thinking mode (model-based), web search (builtin_function), file upload
- Streaming: Supports reasoning_content extraction

### Tool Schemas

#### [TOOL_SCHEMAS.md](TOOL_SCHEMAS.md)
**MCP Tool Input/Output Schemas**
- SimpleTool schema (chat, activity, challenge, recommend)
- WorkflowTool schemas (12 workflow tools)
- Parameter validation rules
- Response formats

### Configuration

#### [ENVIRONMENT_VARIABLES.md](ENVIRONMENT_VARIABLES.md)
**Complete Environment Variable Reference**
- Provider configuration (GLM, Kimi)
- Model defaults and routing
- Timeout configuration
- Feature flags
- Streaming settings
- Caching configuration

---

## 🔑 Key Concepts

### Provider Compatibility

**GLM (ZhipuAI):**
- Custom API format (not OpenAI compatible)
- Thinking mode: `thinking: {"type": "enabled"}`
- Web search: Separate `/web_search` endpoint OR tools array with `type: "web_search"`
- Function calling: `tools` array with `type: "function"`

**Kimi (Moonshot AI):**
- **OpenAI SDK Compatible:** All parameters follow OpenAI format
- Thinking mode: Model-based (`kimi-thinking-preview`)
- Web search: `tools` array with `type: "builtin_function"`, `name: "$web_search"`
- Function calling: Standard OpenAI function calling format
- Streaming: Supports `reasoning_content` field extraction

### Thinking Mode

**Three Different Systems:**

1. **GLM Thinking Mode** (Boolean)
   - API: `thinking: {"type": "enabled"}` or `"disabled"`
   - Models: glm-4.6, glm-4.5
   - Response: `reasoning_content` field

2. **Kimi Thinking Mode** (Model-Based)
   - Model: `kimi-thinking-preview`
   - Streaming: Extract `reasoning_content` using `hasattr/getattr`
   - Response: Formatted as `[Reasoning]\n...\n\n[Response]\n...`

3. **Expert Analysis Thinking Mode** (Categories)
   - Parameter: `thinking_mode` (minimal/low/medium/high/max)
   - Controls depth of expert analysis reasoning
   - **NOT related to provider APIs!**

### Web Search

**GLM Web Search:**
- **Method 1:** Separate `/web_search` endpoint (used by `glm_web_search.py` tool)
- **Method 2:** Tools array in chat completions with `type: "web_search"`
- Configuration: search_engine, search_recency_filter, content_size, etc.

**Kimi Web Search:**
- Tools array with `type: "builtin_function"`, `name: "$web_search"`
- OpenAI SDK compatible format
- Configuration: enable_search parameter

---

## 📖 Quick Reference

### GLM API Endpoints

```
POST https://api.z.ai/api/paas/v4/chat/completions
POST https://api.z.ai/api/paas/v4/web_search
POST https://api.z.ai/api/paas/v4/files
```

### Kimi API Endpoints

```
POST https://api.moonshot.ai/v1/chat/completions
POST https://api.moonshot.ai/v1/files
```

### Environment Variables (Quick Reference)

```env
# GLM Configuration
GLM_BASE_URL=https://api.z.ai/api/paas/v4
GLM_API_KEY=your_key_here
GLM_STREAM_ENABLED=true

# Kimi Configuration (OpenAI SDK Compatible)
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_API_KEY=your_key_here
KIMI_STREAM_ENABLED=false
KIMI_EXTRACT_REASONING=true

# Model Defaults
DEFAULT_MODEL=glm-4.5-flash
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_THINKING_MODEL=kimi-thinking-preview

# Timeouts
KIMI_CHAT_TOOL_TIMEOUT_SECS=180
KIMI_CHAT_TOOL_TIMEOUT_WEB_SECS=300
KIMI_STREAM_TIMEOUT_SECS=240
```

---

## 🔗 Related Documentation

- **[System Overview](../01_ARCHITECTURE/SYSTEM_OVERVIEW.md)** - High-level architecture
- **[Provider Architecture](../01_ARCHITECTURE/PROVIDER_ARCHITECTURE.md)** - Provider design
- **[Thinking Mode Implementation](../03_IMPLEMENTATION/THINKING_MODE_IMPLEMENTATION.md)** - How thinking mode works
- **[Web Search Implementation](../03_IMPLEMENTATION/WEB_SEARCH_IMPLEMENTATION.md)** - Web search details

---

## 📝 Contributing

When adding API documentation:
1. Include API endpoint URLs
2. Provide request/response examples
3. Document all parameters
4. Note any provider-specific behavior
5. Update this README

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Maintained By:** EX-AI-MCP-Server Team

