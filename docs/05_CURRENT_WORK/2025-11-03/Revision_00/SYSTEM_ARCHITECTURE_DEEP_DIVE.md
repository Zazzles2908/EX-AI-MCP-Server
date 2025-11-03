# SYSTEM ARCHITECTURE DEEP DIVE - Tool Registry & Platform Integration

**Date:** 2025-11-03
**Status:** 🔴 CRITICAL ANALYSIS
**EXAI Consultations:** 
- Kimi Thinking: df2dfa72-1e9e-4f49-9537-9a90e654740e (19 turns)
- GLM-4.6: 53734642-81db-4f1f-8932-967066107091 (19 turns)

---

## 🎯 EXECUTIVE SUMMARY

**CRITICAL DISCOVERY:**
Our Week 3 implementation plan is missing a fundamental understanding of how EXAI MCP tool registration and visibility works. We were planning to create platform clients (Moonshot/Z.ai) without understanding where they fit in the architecture.

**KEY FINDINGS:**
1. ✅ **Unified File Interface Exists:** `smart_file_query` tool is designed as the single entry point for ALL file operations
2. ❌ **Platform Integration Pattern Unclear:** No clear pattern for adding platform-specific file APIs
3. ⚠️ **Tool Visibility System:** 4-tier visibility system controls what agents see (essential/core/advanced/hidden)
4. ✅ **Provider Pattern Established:** Kimi/GLM provider pattern can be extended for Moonshot/Z.ai
5. ❌ **Missing Platform Clients:** No dedicated client classes for Moonshot/Z.ai file APIs

**IMPACT ON WEEK 3 PLAN:**
- Tasks A1 & A2 (Platform clients) need architectural redesign
- Should extend existing `smart_file_query` instead of creating new tools
- Need to understand tool registration flow before implementation

---

## 📊 COMPLETE TOOL LIFECYCLE

### **Phase 1: Tool Definition → Schema Generation**

**1.1 Tool Class Hierarchy:**
```
BaseTool (base_tool.py)
├── SimpleTool (simple/base.py) - Request/response tools
│   ├── ChatTool
│   ├── SmartFileQueryTool ⭐ UNIFIED FILE INTERFACE
│   └── ... (other simple tools)
└── WorkflowTool (workflow/base.py) - Multi-step tools
    ├── AnalyzeTool
    ├── DebugTool
    └── ... (other workflow tools)
```

**1.2 Schema Building:**
- **Simple Tools:** Use `SchemaBuilder` in `tools/shared/schema_builders.py`
- **Workflow Tools:** Use `WorkflowSchemaBuilder` in `tools/workflow/schema_builders.py`
- **Common Fields:** temperature, thinking_mode, use_websearch, continuation_id, images
- **Simple-Specific:** files (for embedding content)
- **Workflow-Specific:** step, step_number, findings, relevant_files, confidence

**1.3 Tool Implementation Pattern:**
```python
# Example: Simple Tool
class ChatTool(SimpleTool):
    def get_name(self) -> str:
        return "chat"
    
    def get_description(self) -> str:
        return "GENERAL CHAT & COLLABORATIVE THINKING..."
    
    def get_tool_fields(self) -> dict:
        return {
            "prompt": {"type": "string", "description": "..."},
            "files": SimpleTool.FILES_FIELD,
        }
    
    def get_required_fields(self) -> list[str]:
        return ["prompt"]
    
    async def execute(self, arguments):
        # Implementation
        pass
```

### **Phase 2: Registry Bootstrap (Singleton Pattern)**

**2.1 Initialization Flow:**
```
server.py / run_ws_daemon.py
    ↓
src/bootstrap/singletons.py::bootstrap_all()
    ↓
ensure_providers_configured() → Provider setup
    ↓
ensure_tools_built() → ToolRegistry.build_tools()
    ↓
ensure_provider_tools_registered() → Provider-specific tools
```

**2.2 Tool Registry (tools/registry.py):**
```python
# Tool map with module paths
TOOL_MAP = {
    "chat": ("tools.chat", "ChatTool"),
    "smart_file_query": ("tools.smart_file_query", "SmartFileQueryTool"),
    "analyze": ("tools.workflows.analyze", "AnalyzeTool"),
    # ... 33 total tools
}

# Visibility tiers (4 levels)
TOOL_VISIBILITY = {
    # ESSENTIAL (3 tools): Always visible
    "status": "essential",
    "chat": "essential",
    "planner": "essential",
    
    # CORE (8 tools): Default visibility - 80% use cases
    "analyze": "core",
    "codereview": "core",
    "debug": "core",
    "smart_file_query": "core",  # ⭐ UNIFIED FILE INTERFACE
    
    # ADVANCED (7 tools): Visible on request
    "consensus": "advanced",
    "docgen": "advanced",
    
    # HIDDEN (16 tools): System/diagnostic only
    "provider_capabilities": "hidden",
    "listmodels": "hidden",
}
```

**2.3 Configuration Logic:**
```python
# Step 1: Determine base tool set
if ENABLED_TOOLS env var set:
    active = explicit whitelist
elif TOOL_PROFILE == "lean":
    active = ESSENTIAL + CORE (10 tools)
elif TOOL_PROFILE == "standard":
    active = ESSENTIAL + CORE + ADVANCED (20 tools)
else:  # full
    active = all tools (33 tools)

# Step 2: Apply blacklist
active -= DISABLED_TOOLS

# Step 3: Always expose utility tools
active += ["listmodels", "version"]
```

### **Phase 3: MCP Exposure**

**3.1 MCP Protocol Handlers (src/server/handlers/mcp_handlers.py):**
```python
@server.list_tools()
async def list_tools_handler():
    """Handle MCP list_tools requests."""
    return await handle_list_tools()

@server.call_tool()
async def call_tool_handler(name: str, arguments: dict):
    """Handle MCP call_tool requests."""
    return await handle_call_tool(name, arguments)
```

**3.2 Tool Exposure Flow:**
```
Client requests tools
    ↓
handle_list_tools() in mcp_handlers.py
    ↓
get_registry().list_tools() → Returns active tools
    ↓
Filter by client allow/deny lists (CLIENT_* env vars)
    ↓
Convert to MCP Tool objects with schemas
    ↓
Return to client
```

**3.3 What Agents See:**
```json
{
  "name": "chat",
  "description": "GENERAL CHAT & COLLABORATIVE THINKING...",
  "inputSchema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "prompt": {"type": "string", "description": "..."},
      "files": {"type": "array", "items": {"type": "string"}},
      "model": {"type": "string", "description": "..."},
      "temperature": {"type": "number", "minimum": 0, "maximum": 1},
      "use_websearch": {"type": "boolean", "default": true}
    },
    "required": ["prompt"],
    "additionalProperties": false
  }
}
```

### **Phase 4: Tool Execution**

**4.1 Execution Flow:**
```
Client calls tool
    ↓
handle_call_tool() in mcp_handlers.py
    ↓
normalize_tool_name() → Handle aliases (deepthink → thinkdeep)
    ↓
validate_file_sizes() → Check file size limits
    ↓
inject_optional_features() → Add date, websearch, client defaults
    ↓
execute_tool_with_fallback() → Execute with provider fallback
    ↓
tool.execute(arguments) → Tool-specific implementation
    ↓
format_response() → Normalize response
    ↓
Return to client
```

**4.2 Model Context Resolution:**
```python
# src/server/handlers/execution.py
def create_model_context(model_name: str, model_option: Optional[str]):
    """Create model context with resolved model and option."""
    from utils.model.context import ModelContext
    
    model_context = ModelContext(model_name, model_option)
    # Provides: context_window, capabilities, provider info
    return model_context
```

---

## 🔧 PLATFORM INTEGRATION ANALYSIS

### **Current File Handling Architecture**

**Unified File Interface: `smart_file_query`**
```python
# Location: tools/smart_file_query.py
class SmartFileQueryTool(SimpleTool):
    """
    Unified file upload and query interface with automatic deduplication
    and provider selection.
    
    Features:
    - Automatic SHA256-based deduplication (reuses existing uploads)
    - Intelligent provider selection (ALWAYS Kimi for files)
    - Automatic fallback (GLM fails → Kimi, vice versa)
    - Centralized Supabase tracking
    - Path validation and security checks
    """
```

**Current Capabilities:**
- ✅ File upload to Kimi platform
- ✅ SHA256 deduplication
- ✅ Supabase tracking
- ✅ Provider fallback
- ❌ Moonshot file API integration
- ❌ Z.ai file API integration
- ❌ Cross-platform file sync

### **Provider-Specific Tools Pattern**

**Existing Pattern (Kimi/GLM):**
```python
# src/bootstrap/singletons.py
def ensure_provider_tools_registered(tools_dict: Dict[str, Any]) -> None:
    """Register provider-specific tools after providers are configured."""
    
    # Kimi-specific tools
    kimi_tools = [
        ("kimi_manage_files", ("tools.providers.kimi.kimi_files", "KimiManageFilesTool")),
        ("kimi_intent_analysis", ("tools.providers.kimi.kimi_intent", "KimiIntentAnalysisTool")),
        ("kimi_chat_with_tools", ("tools.providers.kimi.kimi_tools_chat", "KimiChatWithToolsTool")),
    ]
    
    # GLM-specific tools
    glm_tools = [
        ("glm_web_search", ("tools.providers.glm.glm_web_search", "GLMWebSearchTool")),
        ("glm_payload_preview", ("tools.providers.glm.glm_payload_preview", "GLMPayloadPreviewTool")),
    ]
```

**Directory Structure:**
```
tools/providers/
├── kimi/
│   ├── kimi_files.py (KimiManageFilesTool)
│   ├── kimi_intent.py (KimiIntentAnalysisTool)
│   └── kimi_tools_chat.py (KimiChatWithToolsTool)
└── glm/
    ├── glm_web_search.py (GLMWebSearchTool)
    └── glm_payload_preview.py (GLMPayloadPreviewTool)
```

---

## 🚨 CRITICAL GAPS IN WEEK 3 PLAN

### **Gap 1: Architectural Misunderstanding**

**Original Plan (WRONG):**
```
Task A1: Create standalone Moonshot File API Client
Task A2: Create standalone Z.ai Platform Client
```

**Correct Approach:**
```
Option A: Extend smart_file_query with platform selection
Option B: Create provider-specific tools following Kimi/GLM pattern
Option C: Hybrid - Extend smart_file_query + Add platform-specific tools
```

### **Gap 2: Tool Visibility Not Considered**

**Missing from Plan:**
- Where do new tools fit in visibility tiers?
- Should they be CORE (always visible) or ADVANCED (on request)?
- How do they integrate with existing file tools?

### **Gap 3: Schema Integration Unclear**

**Missing from Plan:**
- How do platform-specific fields get added to schemas?
- How does agent know which platform to use?
- How do we maintain backward compatibility?

### **Gap 4: Provider Configuration Incomplete**

**Missing Environment Variables:**
```bash
# Need to add:
MOONSHOT_FILE_API_KEY=your_key
MOONSHOT_FILE_API_URL=https://api.moonshot.cn/v1
Z_AI_FILE_API_KEY=your_key
Z_AI_FILE_API_URL=https://api.z.ai/v1
PLATFORM_FILE_PREFERENCE=moonshot|z.ai|auto
```

---

## ✅ RECOMMENDED IMPLEMENTATION APPROACH

### **Option A: Extend Smart File Query (RECOMMENDED)**

**Advantages:**
- ✅ Single unified interface for all file operations
- ✅ Maintains existing tool visibility (CORE tier)
- ✅ Backward compatible (existing code continues to work)
- ✅ Consistent with "smart" routing philosophy

**Implementation:**
```python
# tools/smart_file_query.py
class SmartFileQueryTool(SimpleTool):
    def get_input_schema(self):
        schema = super().get_input_schema()
        
        # Add platform selection field
        schema["properties"]["platform"] = {
            "type": "string",
            "enum": ["auto", "kimi", "moonshot", "z.ai"],
            "description": "File platform to use (auto selects based on file size)",
            "default": "auto"
        }
        
        return schema
    
    async def execute(self, arguments):
        platform = arguments.get("platform", "auto")
        
        if platform == "auto":
            platform = self._select_platform(arguments)
        
        if platform == "moonshot":
            return await self._upload_to_moonshot(arguments)
        elif platform == "z.ai":
            return await self._upload_to_zai(arguments)
        else:  # kimi (existing)
            return await self._upload_to_kimi(arguments)
```

### **Option B: Provider-Specific Tools (ALTERNATIVE)**

**Advantages:**
- ✅ Follows established Kimi/GLM pattern
- ✅ Clean separation of concerns
- ✅ Platform-specific optimizations possible

**Implementation:**
```python
# tools/providers/moonshot/file_upload.py
class MoonshotFileUploadTool(SimpleTool):
    def get_name(self) -> str:
        return "moonshot_upload_files"
    
    def get_description(self) -> str:
        return "Upload files to Moonshot platform for persistent storage"
    
    async def execute(self, arguments):
        # Moonshot-specific implementation
        pass

# Register in src/bootstrap/singletons.py
moonshot_tools = [
    ("moonshot_upload_files", ("tools.providers.moonshot.file_upload", "MoonshotFileUploadTool")),
]
```

### **Option C: Hybrid Approach (BEST OF BOTH)**

**Advantages:**
- ✅ Unified interface for common use cases
- ✅ Platform-specific tools for advanced features
- ✅ Maximum flexibility

**Implementation:**
1. Extend `smart_file_query` with platform selection (Option A)
2. Add platform-specific tools for advanced features (Option B)
3. Set visibility: `smart_file_query` = CORE, platform tools = ADVANCED

---

## 📋 REVISED WEEK 3 IMPLEMENTATION PLAN

### **Phase A: Core Infrastructure (REVISED)**

**A1: Platform Client Classes (6 hours)**
- Create `src/providers/moonshot_client.py`
- Create `src/providers/zai_client.py`
- Implement upload/download/list/delete methods
- Add error handling and rate limiting

**A2: Extend Smart File Query (4 hours)**
- Add platform selection field to schema
- Implement platform routing logic
- Integrate Moonshot/Z.ai clients
- Add tests

**A3: Provider-Specific Tools (Optional - 4 hours)**
- Create `tools/providers/moonshot/file_upload.py`
- Create `tools/providers/z.ai/file_upload.py`
- Register in singletons.py
- Set visibility to ADVANCED tier

**A4: Configuration & Environment (2 hours)**
- Add platform API keys to .env.docker
- Update provider_config.py
- Add platform selection logic
- Document configuration

---

## 🎯 NEXT IMMEDIATE ACTIONS

1. **Review This Analysis with EXAI**
   - Use continuation_id: 53734642-81db-4f1f-8932-967066107091
   - Validate recommended approach
   - Get implementation guidance

2. **Update Week 3 Plan**
   - Revise tasks A1-A4 based on this analysis
   - Add tool visibility considerations
   - Update time estimates

3. **Create Platform Client Specifications**
   - Document Moonshot API contract
   - Document Z.ai API contract
   - Define error handling strategy

4. **Prototype Smart File Query Extension**
   - Test platform selection logic
   - Validate schema changes
   - Ensure backward compatibility

---

**CONTINUATION IDS:**
- Kimi Thinking: df2dfa72-1e9e-4f49-9537-9a90e654740e (19 turns)
- GLM-4.6: 53734642-81db-4f1f-8932-967066107091 (19 turns)

