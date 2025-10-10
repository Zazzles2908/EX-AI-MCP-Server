# SIMPLETOOL CONNECTION MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.5 - SimpleTool Connection Analysis (CRITICAL for Phase 3)  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

**CRITICAL FOR PHASE 3 REFACTORING!**

Map all connections to/from SimpleTool to understand:
- Which tools inherit from SimpleTool (upstream dependencies)
- Which SimpleTool methods they call (critical public interface)
- What SimpleTool inherits from (downstream dependencies)
- What SimpleTool imports (external dependencies)

This analysis is **ESSENTIAL** before Phase 3 refactoring to ensure we don't break any tools.

---

## 📊 SIMPLETOOL OVERVIEW

**File:** `tools/simple/base.py`  
**Size:** 55.3KB (1,220 lines)  
**Purpose:** Base class for simple (non-workflow) tools  
**Pattern:** Request → AI model → Response  

**Inheritance Chain:**
```
SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool)
└── BaseTool(BaseToolCore, FileHandlingMixin, ModelManagementMixin, ResponseFormattingMixin)
```

---

## 🔼 UPSTREAM: TOOLS INHERITING FROM SIMPLETOOL

### Direct Subclasses (3 tools) ✅ VALIDATED

1. **ChatTool** (`tools/chat.py`) - 292 lines
2. **ChallengeTool** (`tools/challenge.py`) - 237 lines
3. **ActivityTool** (`tools/activity.py`) - ~200 lines

**VALIDATION NOTE:** RecommendTool was initially documented but does NOT exist in TOOL_MAP registry (tools/registry.py). Count corrected from 4 to 3 tools.

---

## 🔍 CRITICAL PUBLIC INTERFACE (25 METHODS - CANNOT CHANGE) ✅ VALIDATED

**These 25 public methods form the critical interface that CANNOT CHANGE during Phase 3 refactoring.**

All 3 tools (ChatTool, ChallengeTool, ActivityTool) depend on this interface.

### Abstract Methods (Subclasses MUST Implement)

**1. get_tool_fields() → dict[str, dict[str, Any]]**
- **Purpose:** Return tool-specific field definitions
- **Used By:** All 3 tools
- **Example:**
```python
def get_tool_fields(self) -> dict[str, dict[str, Any]]:
    return {
        "prompt": {"type": "string", "description": "..."},
        "files": SimpleTool.FILES_FIELD,  # Reuse common field
    }
```

**2. get_required_fields() → list[str]**
- **Purpose:** Return list of required field names
- **Used By:** All 3 tools
- **Example:**
```python
def get_required_fields(self) -> list[str]:
    return ["prompt"]
```

---

### Hook Methods (Subclasses CAN Override)

**3. get_annotations() → Optional[dict[str, Any]]**
- **Purpose:** Return tool annotations (readOnlyHint, etc.)
- **Default:** `{"readOnlyHint": True}` (simple tools are read-only)
- **Used By:** All tools (default behavior)

**4. format_response(response, request, model_info) → str**
- **Purpose:** Format AI response before returning
- **Default:** Returns response as-is
- **Overridden By:** ChatTool (adds conversation history)

**5. get_request_model() → Type[ToolRequest]**
- **Purpose:** Return tool-specific request model class
- **Default:** Returns base ToolRequest
- **Overridden By:** ChatTool (ChatRequest), ChallengeTool (ChallengeRequest)

---

### Schema Generation Methods

**6. get_input_schema() → dict[str, Any]**
- **Purpose:** Generate complete JSON schema for tool
- **Used By:** All tools (via MCP protocol)
- **Implementation:** Uses SchemaBuilder + get_tool_fields()
- **Overridden By:** ChatTool (for exact compatibility)

**7. get_model_field_schema() → dict[str, Any]**
- **Purpose:** Generate model field schema
- **Used By:** get_input_schema()
- **Implementation:** Delegates to SchemaBuilder

---

### Request Field Accessors (13 methods) 🔥

**CRITICAL:** These are heavily used by all tools!

**8. get_request_prompt(request) → str**
- **Purpose:** Safely extract prompt from request
- **Used By:** All tools

**9. get_request_files(request) → list[str]**
- **Purpose:** Safely extract files from request
- **Used By:** ChatTool, ActivityTool

**10. get_request_images(request) → list[str]**
- **Purpose:** Safely extract images from request
- **Used By:** ChatTool

**11. get_request_continuation_id(request) → Optional[str]**
- **Purpose:** Safely extract continuation_id from request
- **Used By:** ChatTool

**12. get_request_use_websearch(request) → bool**
- **Purpose:** Safely extract use_websearch flag
- **Used By:** ChatTool

**13. get_request_stream(request) → Optional[bool]**
- **Purpose:** Safely extract stream flag
- **Used By:** ChatTool

**14. get_request_temperature(request) → Optional[float]**
- **Purpose:** Safely extract temperature from request
- **Used By:** All tools

**15. get_request_thinking_mode(request) → Optional[str]**
- **Purpose:** Safely extract thinking_mode from request
- **Used By:** All tools

**16-20. Additional accessors:**
- `get_request_model(request)` - Extract model name
- `get_request_max_output_tokens(request)` - Extract max tokens
- `get_request_system_prompt(request)` - Extract system prompt
- `get_request_tool_choice(request)` - Extract tool choice
- `get_request_tools(request)` - Extract tools list

---

### Temperature Validation

**21. get_validated_temperature(request, model_context) → tuple[float, list[str]]**
- **Purpose:** Get and validate temperature against model constraints
- **Used By:** All tools
- **Returns:** (validated_temperature, warning_messages)

---

### Prompt Building Methods 🔥

**CRITICAL:** These are core SimpleTool functionality!

**22. build_standard_prompt(system_prompt, user_content, request, file_context_title) → str**
- **Purpose:** Build standard prompt with system prompt, user content, and files
- **Used By:** All tools that call AI models
- **Implementation:**
  - Adds file content if present
  - Checks token limits
  - Adds web search instructions
  - Combines into well-formatted prompt

**23. prepare_chat_style_prompt(request, system_prompt) → str**
- **Purpose:** Prepare chat-style prompt with conversation context
- **Used By:** ChatTool
- **Implementation:**
  - Handles conversation continuation
  - Adds client info
  - Builds complete prompt

**24. handle_prompt_file_with_fallback(request) → str**
- **Purpose:** Handle prompt file with fallback to direct prompt
- **Used By:** Tools with prompt_file support

**25. get_chat_style_websearch_guidance() → str**
- **Purpose:** Get web search guidance for chat-style tools
- **Used By:** ChatTool

---

### File Tracking

**26. get_actually_processed_files() → list**
- **Purpose:** Get list of actually processed files
- **Used By:** All tools with file support

---

### Execution Method

**27. execute(arguments) → list**
- **Purpose:** Main execution method (inherited from BaseTool)
- **Used By:** All tools (via MCP protocol)
- **Implementation:** Comprehensive flow with validation, model calling, response formatting

---

## 🔽 DOWNSTREAM: WHAT SIMPLETOOL INHERITS FROM

### Mixin Composition (4 mixins)

**1. WebSearchMixin** (`tools/simple/mixins/web_search_mixin.py`)
- **Purpose:** Web search instruction generation
- **Methods:**
  - `get_websearch_guidance()` - Generate web search instructions
  - `get_chat_style_websearch_guidance()` - Chat-style guidance

**2. ToolCallMixin** (`tools/simple/mixins/tool_call_mixin.py`)
- **Purpose:** Tool call detection and execution
- **Methods:**
  - `detect_tool_calls()` - Detect tool calls in response
  - `execute_tool_calls()` - Execute detected tool calls

**3. StreamingMixin** (`tools/simple/mixins/streaming_mixin.py`)
- **Purpose:** Streaming support configuration
- **Methods:**
  - `supports_streaming()` - Check if streaming is supported
  - `get_streaming_config()` - Get streaming configuration

**4. ContinuationMixin** (`tools/simple/mixins/continuation_mixin.py`)
- **Purpose:** Conversation continuation and caching
- **Methods:**
  - `get_continuation_context()` - Get conversation context
  - `save_continuation()` - Save conversation state

---

### BaseTool Inheritance

**BaseTool** (`tools/shared/base_tool.py`)
- **Composed From:**
  - BaseToolCore - Core tool infrastructure
  - FileHandlingMixin - File processing
  - ModelManagementMixin - Model context and selection
  - ResponseFormattingMixin - Response formatting

**Inherited Methods (from BaseTool):**
- `get_name()` - Tool name
- `get_description()` - Tool description
- `get_system_prompt()` - System prompt
- `get_default_temperature()` - Default temperature
- `get_model_category()` - Model category
- `requires_model()` - Whether tool needs AI model
- `process_files()` - File processing
- `resolve_model_context()` - Model context resolution
- `call_model()` - AI model calling
- `format_text_content()` - Format response as TextContent

---

## 📦 EXTERNAL DEPENDENCIES

### Direct Imports

**From tools/shared:**
```python
from tools.shared.base_models import ToolRequest
from tools.shared.base_tool import BaseTool
from tools.shared.schema_builders import SchemaBuilder
```

**From tools/simple/mixins:**
```python
from tools.simple.mixins import WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin
```

**From MCP:**
```python
from mcp.types import TextContent
```

**From utils:**
```python
from utils.client_info import get_current_session_fingerprint, get_cached_client_info, format_client_info
from utils.progress import send_progress
from utils.progress_utils.messages import ProgressMessages
```

---

## 🔒 REFACTORING CONSTRAINTS

### CANNOT CHANGE (Breaking Changes)

1. **Class Name:** `SimpleTool` must remain
2. **Inheritance Chain:** Must preserve mixin composition and BaseTool inheritance
3. **Public Method Signatures:** All 25 public methods must keep exact signatures
4. **Class Constants:** `FILES_FIELD`, `IMAGES_FIELD` must remain
5. **Abstract Methods:** `get_tool_fields()`, `get_required_fields()` must remain abstract
6. **Hook Methods:** `get_annotations()`, `format_response()`, `get_request_model()` must remain overridable

### CAN CHANGE (Internal Implementation)

1. **Internal Methods:** Methods starting with `_` can be refactored
2. **Implementation Details:** How methods work internally can change
3. **File Organization:** Can split into multiple files using Facade pattern
4. **Helper Functions:** Can extract to separate modules

---

## 🎯 PHASE 3 REFACTORING STRATEGY

### Facade Pattern (Recommended)

**SimpleTool becomes a FACADE that:**
1. Keeps ALL public methods (same signatures)
2. Delegates to internal modules for implementation
3. Maintains 100% backward compatibility

**Example:**
```python
# tools/simple/base.py (Facade)
class SimpleTool(...):
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        from tools.simple.preparation.prompt import PromptBuilder
        return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)
    
    def get_request_prompt(self, request):
        from tools.simple.intake.accessor import RequestAccessor
        return RequestAccessor.get_prompt(request)
```

### Proposed Module Structure (Top-Down Design)

**tools/simple/**
- `base.py` - SimpleTool facade (keeps all public methods)
- `definition/` - Tool contract (schema generation)
- `intake/` - Request processing (field accessors)
- `preparation/` - Prompt building
- `execution/` - Model calling
- `response/` - Response formatting

---

## ✅ TASK 2.5 COMPLETE

**Deliverable:** SIMPLETOOL_CONNECTION_MAP.md ✅

**Key Findings:**
- 3 tools inherit from SimpleTool (ChatTool, ChallengeTool, ActivityTool)
- 25 public methods in critical interface (CANNOT CHANGE)
- 13 request accessor methods heavily used
- Facade pattern recommended for Phase 2 Cleanup
- 100% backward compatibility required

**Next Task:** Task 2.6 - WorkflowTool Connection Analysis

**Time Taken:** ~45 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All SimpleTool connections mapped with refactoring constraints identified

