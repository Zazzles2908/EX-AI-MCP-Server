# GLM Native Web Search Investigation

**Date:** 2025-10-01  
**Investigator:** Augment Agent  
**Issue:** GLM native web search not functioning as expected in EXAI-WS MCP calls

---

## Problem Statement

When calling EXAI-WS MCP tools (like `chat_EXAI-WS` or `planner_EXAI-WS`) with `use_websearch=true`, the GLM model does not appear to perform native web browsing. Instead, the model returns responses without web search results.

---

## Investigation Findings

### 1. Code Analysis

#### Chat Tool Configuration (`tools/chat.py`)
```python
# Line 52: use_websearch defaults to True
use_websearch: Optional[bool] = Field(
    default=True, 
    description="Enable provider-native web browsing when available"
)

# Line 116: Schema includes use_websearch parameter
"use_websearch": {
    "type": "boolean", 
    "description": "Enable provider-native web browsing", 
    "default": True
}
```

**Finding:** The chat tool is configured to enable web search by default.

#### GLM Capabilities (`src/providers/capabilities.py`)
```python
# Lines 80-88
class GLMCapabilities(ProviderCapabilitiesBase):
    def supports_websearch(self) -> bool:
        return os.getenv("GLM_ENABLE_WEB_BROWSING", "true").strip().lower() == "true"
    
    def get_websearch_tool_schema(self, config: Dict[str, Any]) -> WebSearchSchema:
        if not self.supports_websearch() or not config.get("use_websearch"):
            return WebSearchSchema(None, None)
        # GLM requires non-null web_search object in tool spec
        tools = [{"type": "web_search", "web_search": {}}]
        return WebSearchSchema(tools=tools, tool_choice="auto")
```

**Finding:** GLM capabilities check for `GLM_ENABLE_WEB_BROWSING` environment variable with a **default of "true"**.

#### Environment Configuration

**`.env` file:**
- ❌ `GLM_ENABLE_WEB_BROWSING` is **NOT SET**
- Only `KIMI_ENABLE_INTERNET_SEARCH=true` is present

**`.env.example` file:**
- ❌ `GLM_ENABLE_WEB_BROWSING` is **NOT DOCUMENTED**
- Only Kimi web search settings are documented

**Finding:** The environment variable is missing from both files, but the code defaults to "true" when not set.

#### GLM Chat Implementation (`src/providers/glm_chat.py`)
```python
# Lines 51-61: Tools are passed through to the API
try:
    tools = kwargs.get("tools")
    if tools:
        payload["tools"] = tools
    tool_choice = kwargs.get("tool_choice")
    if tool_choice:
        payload["tool_choice"] = tool_choice
except Exception:
    # be permissive
    pass
```

**Finding:** The GLM chat implementation passes tools through to the API, but relies on upstream code to inject the web_search tool schema.

---

## Root Cause Analysis

### Primary Issue: Missing Environment Variable Documentation

1. **Configuration Gap:**
   - `GLM_ENABLE_WEB_BROWSING` is not documented in `.env.example`
   - Users don't know this variable exists or how to configure it
   - The variable is missing from the actual `.env` file

2. **Default Behavior:**
   - Code defaults to `"true"` when variable is not set
   - This means web search **should** be enabled by default
   - However, the lack of documentation makes it unclear

### Secondary Issue: Tool Schema Injection Flow

The web search tool schema injection follows this path:

```
1. User calls chat_EXAI-WS with use_websearch=true
   ↓
2. Request handler checks use_websearch parameter
   ↓
3. GLMCapabilities.get_websearch_tool_schema() is called
   ↓
4. If enabled, returns: tools=[{"type": "web_search", "web_search": {}}]
   ↓
5. Tools are added to the GLM API payload
   ↓
6. GLM API receives the web_search tool and should use it
```

**Potential Break Points:**
- Request handler may not be calling capabilities layer correctly
- Web search tool schema may not be properly injected
- GLM API may not be receiving the tools parameter

### Tertiary Issue: Validation Gap

There's no easy way to verify:
1. Whether the web_search tool is actually being sent to the GLM API
2. Whether the GLM API is actually using the web_search tool
3. What the actual API payload looks like

---

## Testing Strategy

### Test 1: Verify Default Behavior
```python
# Check if GLM_ENABLE_WEB_BROWSING defaults to true
import os
from src.providers.capabilities import GLMCapabilities

caps = GLMCapabilities()
print(f"Web search supported: {caps.supports_websearch()}")
# Expected: True (because default is "true")
```

### Test 2: Verify Tool Schema Injection
```python
# Check if web_search tool schema is generated correctly
config = {"use_websearch": True}
schema = caps.get_websearch_tool_schema(config)
print(f"Tools: {schema.tools}")
print(f"Tool choice: {schema.tool_choice}")
# Expected: tools=[{"type": "web_search", "web_search": {}}], tool_choice="auto"
```

### Test 3: Verify API Payload
Use the `glm_payload_preview` tool to inspect the actual payload:
```python
# Via EXAI-WS MCP
glm_payload_preview_EXAI-WS(
    prompt="Test web search",
    model="glm-4.5-flash",
    use_websearch=true
)
# Should show tools=[{"type": "web_search", "web_search": {}}] in payload
```

### Test 4: Live Web Search Test
```python
# Via EXAI-WS MCP
chat_EXAI-WS(
    prompt="What is the current date and latest news about AI? Use web search.",
    model="glm-4.5-flash",
    use_websearch=true
)
# Should return current information from web search
```

---

## Recommendations

### Immediate Actions

1. **Add GLM_ENABLE_WEB_BROWSING to .env.example:**
```bash
# -------- GLM (ZhipuAI/Z.ai) Provider Settings --------
# Enable GLM native web browsing (default: true)
GLM_ENABLE_WEB_BROWSING=true
```

2. **Add GLM_ENABLE_WEB_BROWSING to .env:**
```bash
GLM_ENABLE_WEB_BROWSING=true
```

3. **Test with glm_payload_preview tool:**
   - Verify that web_search tool is being injected
   - Inspect the actual API payload

4. **Test with live chat call:**
   - Ask a time-sensitive question that requires web search
   - Verify the response includes current information

### Medium-Term Actions

1. **Add Payload Logging:**
   - Add debug logging in `glm_chat.py` to log the full payload before API call
   - Make it easy to verify what's being sent to GLM API

2. **Add Web Search Validation:**
   - Create a validation script that tests web search functionality
   - Include in the test suite

3. **Improve Documentation:**
   - Document all GLM environment variables in `.env.example`
   - Add examples of web search usage
   - Document the tool schema injection flow

### Long-Term Actions

1. **Unified Provider Configuration:**
   - Standardize web search configuration across providers
   - Use consistent naming (e.g., `{PROVIDER}_ENABLE_WEB_SEARCH`)

2. **Enhanced Diagnostics:**
   - Add a diagnostic tool that shows:
     - Which providers support web search
     - Current web search configuration
     - Test web search functionality

3. **Better Error Messages:**
   - If web search fails, provide clear error messages
   - Indicate whether web search was attempted

---

## Next Steps

1. ✅ Document the issue (this file)
2. ⏳ Add `GLM_ENABLE_WEB_BROWSING` to `.env.example`
3. ⏳ Add `GLM_ENABLE_WEB_BROWSING` to `.env`
4. ⏳ Test with `glm_payload_preview` tool
5. ⏳ Test with live chat call
6. ⏳ Verify web search is working
7. ⏳ Update implementation plan if needed

---

## Related Files

- `tools/chat.py` - Chat tool with use_websearch parameter
- `src/providers/capabilities.py` - GLM capabilities and web search schema
- `src/providers/glm_chat.py` - GLM chat implementation
- `tools/providers/glm/glm_web_search.py` - Direct GLM web search tool
- `tools/providers/glm/glm_payload_preview.py` - Payload preview tool
- `.env.example` - Environment variable template
- `.env` - Actual environment configuration

---

**Status:** Investigation Complete - Ready for Testing and Fixes  
**Priority:** High - Affects core functionality  
**Impact:** Medium - Web search is a key feature for GLM models

