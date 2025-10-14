# EXAI System Architecture Deep Dive
**Date:** 2025-10-10 (10th October 2025)  
**Location:** Melbourne, Australia (AEDT)  
**Purpose:** Complete architectural analysis of request flow from Augment to external AI models

---

## EXECUTIVE SUMMARY

This document traces the complete journey of a user prompt through the EXAI-MCP system, from initial entry via Augment to final response from external AI models (GLM/Kimi). It documents:

1. **7-Layer Architecture** - Entry point → MCP → WebSocket → Handler → Provider → External AI → Response
2. **Model Selection Logic** - How the system chooses between GLM and Kimi models
3. **System Prompt Injection** - How tool-specific prompts shape AI behavior
4. **Tool Discovery** - How Augment knows which tools are available
5. **Critical Gaps** - Missing timestamp metadata and log clarity issues

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER (Augment IDE)                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ MCP Protocol (stdio)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 1: MCP SHIM (scripts/run_ws_shim.py)                        │
│  - Receives stdio MCP requests from Augment                        │
│  - Converts to WebSocket messages                                  │
│  - Manages connection to daemon (health checks, reconnection)      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ WebSocket (ws://127.0.0.1:8765)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 2: WS DAEMON (src/daemon/ws_server.py)                      │
│  - WebSocket server handling tool calls                            │
│  - Normalizes tool names (strips _EXAI-WS suffix)                  │
│  - Manages sessions and concurrency limits                         │
│  - Routes to SERVER_HANDLE_CALL_TOOL                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ Function call
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: REQUEST HANDLER (src/server/handlers/)                   │
│  - request_handler.py: Thin orchestrator (93% code reduction)      │
│  - request_handler_routing.py: Tool name normalization             │
│  - request_handler_model_resolution.py: Model selection            │
│  - request_handler_context.py: Conversation reconstruction         │
│  - request_handler_execution.py: Tool execution with fallback      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ Model context + arguments
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 4: TOOL EXECUTION (tools/)                                  │
│  - BaseTool.execute(): Main entry point                            │
│  - get_system_prompt(): Defines AI role and behavior               │
│  - build_standard_prompt(): Combines system + user + files         │
│  - Prepares final prompt for provider                              │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ Prompt + model name
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 5: PROVIDER REGISTRY (src/providers/registry.py)            │
│  - get_provider_for_model(): Selects GLM/Kimi/Custom               │
│  - Provider priority: KIMI → GLM → CUSTOM → OPENROUTER             │
│  - Validates model availability                                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ Provider instance
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 6: PROVIDER IMPLEMENTATION (src/providers/)                 │
│  - GLM: glm_chat.py builds payload with system/user messages       │
│  - Kimi: kimi.py delegates to OpenAI-compatible base               │
│  - Sends HTTP/SDK request to external API                          │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTPS API call
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 7: EXTERNAL AI (ZhipuAI / Moonshot APIs)                    │
│  - GLM: https://api.z.ai/api/paas/v4/chat/completions              │
│  - Kimi: https://api.moonshot.ai/v1/chat/completions               │
│  - Processes system prompt + user prompt                           │
│  - Returns generated response                                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ Response flows back up
                                 ▼
                          [User sees result]
```

---

## MODEL SELECTION LOGIC

### How the System Chooses Models

**Entry Point:** `src/server/handlers/request_handler_model_resolution.py`

#### 1. Explicit Model Requests
```python
# User specifies model directly
arguments = {"model": "kimi-k2-0905-preview", "prompt": "..."}
# → System uses kimi-k2-0905-preview (no routing)
```

#### 2. Auto Routing (`model="auto"`)

**Function:** `_route_auto_model(tool_name, requested_model, args)`

**Routing Rules:**

| Tool Category | Condition | Selected Model | Env Var |
|--------------|-----------|----------------|---------|
| **Kimi-specific** | Tool in `{kimi_chat_with_tools, kimi_upload_and_extract}` | kimi-k2-0905-preview | `KIMI_SPEED_MODEL` |
| **Simple tools** | Tool in `{chat, status, provider_capabilities, listmodels, activity, version}` | glm-4.5-flash | `GLM_SPEED_MODEL` |
| **thinkdeep** | Always | kimi-thinking-preview | `KIMI_QUALITY_MODEL` |
| **analyze** | step_number=1 AND next_step_required=true | glm-4.5-flash | `GLM_SPEED_MODEL` |
| **analyze** | Final step OR unknown | kimi-thinking-preview | `KIMI_QUALITY_MODEL` |
| **debug** | step_number=1 AND next_step_required=true | glm-4.5-flash | `GLM_SPEED_MODEL` |
| **debug** | Final step OR unknown | kimi-thinking-preview | `KIMI_QUALITY_MODEL` |
| **Other workflows** | Similar step-aware logic | Fast → Quality progression | - |

#### 3. Fallback Chain

If auto routing fails or model unavailable:

```python
# 1. Check intelligent selection (env-gated)
if ENABLE_INTELLIGENT_SELECTION == "true":
    category = tool.get_model_category()  # EXTENDED_REASONING / FAST_RESPONSE / BALANCED
    if category == EXTENDED_REASONING:
        if has_cjk_content or locale.startswith("zh"):
            → KIMI_QUALITY_MODEL
        else:
            → GLM_QUALITY_MODEL
    elif category in (BALANCED, FAST_RESPONSE):
        → GLM_SPEED_MODEL

# 2. CJK content detection
if has_chinese_characters(prompt):
    → KIMI_DEFAULT_MODEL

# 3. Provider registry fallback
→ ModelProviderRegistry.get_preferred_fallback_model(category)
```

#### 4. Model Validation

**Function:** `validate_and_fallback_model(model_name, tool_name, tool_obj, req_id)`

```python
# Check if model is available
provider = ModelProviderRegistry.get_provider_for_model(model_name)
if not provider:
    # Auto-fallback to suggested model
    suggested = ModelProviderRegistry.get_preferred_fallback_model(tool_category)
    return suggested, None  # No error, graceful fallback
```

---

## SYSTEM PROMPT INJECTION

### How Tool Prompts Shape AI Behavior

**Key Files:**
- `tools/shared/base_tool_core.py` - Defines `get_system_prompt()` abstract method
- `tools/simple/base.py` - Implements `build_standard_prompt()`
- `src/providers/glm_chat.py` - Builds final API payload

### Step-by-Step Process

#### 1. Tool Defines System Prompt

Each tool implements `get_system_prompt()`:

```python
# Example: tools/chat.py
def get_system_prompt(self) -> str:
    return (
        "You are a senior engineering thought-partner with deep expertise in software architecture, "
        "system design, and technical problem-solving.\n\n"
        "Your role:\n"
        "- Engage in collaborative brainstorming and technical discussions\n"
        "- Provide nuanced insights on complex engineering challenges\n"
        "- Ask clarifying questions to understand context deeply\n"
        "- Offer multiple perspectives and trade-offs\n"
        "- Challenge assumptions constructively\n\n"
        "Communication style:\n"
        "- Thoughtful and analytical\n"
        "- Direct but respectful\n"
        "- Focus on understanding before proposing solutions\n"
        "- Use examples and analogies when helpful"
    )
```

#### 2. Tool Builds Complete Prompt

**Function:** `SimpleTool.build_standard_prompt(system_prompt, user_content, request)`

```python
def build_standard_prompt(self, system_prompt, user_content, request):
    # 1. Add file context if provided
    files = self.get_request_files(request)
    if files:
        file_content = self._prepare_file_content_for_prompt(files)
        user_content = f"{user_content}\n\n=== CONTEXT FILES ===\n{file_content}\n=== END CONTEXT ==="
    
    # 2. Add web search instruction if enabled
    websearch_instruction = ""
    if self.get_request_use_websearch(request):
        websearch_instruction = self.get_websearch_instruction()
    
    # 3. Combine everything
    full_prompt = f"""{system_prompt}{websearch_instruction}

=== USER REQUEST ===
{user_content}
=== END REQUEST ===

Please provide a thoughtful, comprehensive response:"""
    
    return full_prompt
```

#### 3. Provider Builds API Payload

**Function:** `glm_chat.build_payload(prompt, system_prompt, model_name, temperature, ...)`

```python
def build_payload(prompt, system_prompt, model_name, temperature, max_output_tokens, **kwargs):
    messages = []
    
    # System message (if provided)
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # User message
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "temperature": temperature
    }
    
    return payload
```

#### 4. External AI Receives Final Payload

**Example API Request to GLM:**

```json
{
  "model": "glm-4.5-flash",
  "messages": [
    {
      "role": "system",
      "content": "You are a senior engineering thought-partner with deep expertise..."
    },
    {
      "role": "user",
      "content": "=== USER REQUEST ===\nExplain how dependency injection works\n=== END REQUEST ===\n\nPlease provide a thoughtful, comprehensive response:"
    }
  ],
  "temperature": 0.5,
  "stream": false
}
```

**The external AI (GLM/Kimi) processes both messages and generates a response shaped by the system prompt.**

---

## TOOL DISCOVERY

### How Augment Knows Which Tools Are Available

#### 1. MCP List Tools Request

When Augment starts, it sends a `list_tools` request via MCP protocol:

```python
# scripts/run_ws_shim.py
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    ws = await _ensure_ws()
    await ws.send(json.dumps({"op": "list_tools"}))
    raw = await ws.recv()
    msg = json.loads(raw)
    
    tools = []
    for t in msg.get("tools", []):
        tools.append(Tool(
            name=t.get("name"),
            description=t.get("description"),
            inputSchema=t.get("inputSchema") or {"type": "object"}
        ))
    return tools
```

#### 2. Daemon Returns Tool Registry

**Source:** `src/daemon/ws_server.py` uses `SERVER_TOOLS` from `server.py`

```python
# Singleton tool registry shared between stdio and WebSocket transports
from server import TOOLS as SERVER_TOOLS

# When list_tools request arrives:
tools_list = [
    {
        "name": tool.get_name(),
        "description": tool.get_description(),
        "inputSchema": tool.get_input_schema()
    }
    for tool in SERVER_TOOLS.values()
]
```

#### 3. Tool Registry Population

**File:** `server.py` (bootstrapped via `src/bootstrap/singletons.py`)

```python
# Tools are discovered and registered at startup
from tools.registry import ToolRegistry

TOOLS = {}  # Singleton dict

def _bootstrap_tools():
    registry = ToolRegistry()
    for tool_class in registry.discover_tools():
        tool_instance = tool_class()
        TOOLS[tool_instance.get_name()] = tool_instance
```

#### 4. Augment Displays Tools

Augment receives the tool list and displays them in the UI with:
- Tool name (e.g., "chat_EXAI-WS")
- Description (from `get_description()`)
- Input schema (from `get_input_schema()`)

When user invokes a tool, Augment sends a `call_tool` request with the tool name and arguments.

---

## CRITICAL GAPS IDENTIFIED

### 1. Missing Timestamp Metadata

**Issue:** Request parameters do not include timestamp or geo-location information.

**Impact:**
- Cannot determine when a request was made
- Cannot correlate requests across time zones
- Difficult to debug timing-related issues

**Required Implementation:**
```python
# Add to all tool requests
arguments["_request_metadata"] = {
    "timestamp_utc": "2025-10-10T00:05:30.123Z",
    "timestamp_local": "2025-10-10 11:05:30 AEDT",
    "timezone": "Australia/Melbourne",
    "geo_location": "Melbourne, Australia"
}
```

### 2. Log Timestamp Clarity

**Issue:** Log files use Unix timestamps without human-readable dates.

**Current:**
```json
{"t": 1760050749.591226, "event": "tool_call", ...}
```

**Required:**
```json
{
  "timestamp_unix": 1760050749.591226,
  "timestamp_utc": "2025-10-10T00:05:49.591Z",
  "timestamp_aedt": "2025-10-10 11:05:49 AEDT",
  "event": "tool_call",
  ...
}
```

---

## NEXT STEPS

1. **Implement Timestamp Metadata** (Task 2)
   - Add timestamp fields to request models
   - Include geo-location information
   - Update all tool call requests

2. **Improve Log Clarity** (Task 3)
   - Update logging configuration
   - Add human-readable timestamps
   - Apply to all log files

3. **Documentation Updates**
   - Update system-reference docs with this architecture
   - Create flow diagrams for visual reference
   - Document model selection decision tree

---

**Document Status:** COMPLETE  
**Next Agent:** Use this as baseline for timestamp implementation

