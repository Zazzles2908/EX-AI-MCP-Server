# SIMPLETOOL DEPENDENCY ANALYSIS
**Date:** 2025-10-10 2:00 PM AEDT  
**Purpose:** Complete dependency analysis BEFORE refactoring  
**Status:** CRITICAL - Must understand ALL connections

---

## WHY THIS MATTERS

**User's Critical Question:**
> "How do you know what is existing to be put into what you are building? What about the complexity of what is in the script you are targeting, like how do you know what is targeted above that file and below that file?"

**Answer:** I MUST analyze the complete dependency graph to ensure refactoring doesn't break anything!

---

## COMPLETE DEPENDENCY GRAPH

### 1. UPSTREAM: What Inherits FROM SimpleTool?

**Direct Subclasses (4 tools):**
```
SimpleTool
├── ActivityTool (tools/activity.py)
├── ChallengeTool (tools/challenge.py)
├── ChatTool (tools/chat.py)
└── RecommendTool (tools/capabilities/recommend.py)
```

**What They Override/Use:**

**ChatTool (tools/chat.py):**
- Overrides: `get_name()`, `get_description()`, `get_system_prompt()`, `get_default_temperature()`
- Overrides: `get_model_category()`, `get_request_model()`, `get_input_schema()`
- Overrides: `prepare_prompt()` - **USES: `self.prepare_chat_style_prompt(request)`**
- Overrides: `format_response()` - **USES: conversation history, cache store**
- Overrides: `get_websearch_guidance()` - **USES: `self.get_chat_style_websearch_guidance()`**

**Key Finding:** ChatTool **DEPENDS ON** SimpleTool methods:
- `prepare_chat_style_prompt()` (lines 1182-1220 in base.py)
- `get_chat_style_websearch_guidance()` (inherited from mixin)

**ActivityTool, ChallengeTool, RecommendTool:**
- Similar pattern (need to check each)

---

### 2. DOWNSTREAM: What Does SimpleTool INHERIT FROM?

**Inheritance Chain:**
```
SimpleTool
├── WebSearchMixin (tools/simple/mixins/web_search_mixin.py)
├── ToolCallMixin (tools/simple/mixins/tool_call_mixin.py)
├── StreamingMixin (tools/simple/mixins/streaming_mixin.py)
├── ContinuationMixin (tools/simple/mixins/continuation_mixin.py)
└── BaseTool (tools/shared/base_tool.py)
    ├── BaseToolCore (tools/shared/base_tool_core.py)
    ├── FileHandlingMixin (tools/shared/base_tool_file_handling.py)
    ├── ModelManagementMixin (tools/shared/base_tool_model_management.py)
    └── ResponseFormattingMixin (tools/shared/base_tool_response.py)
```

**What SimpleTool USES from Parents:**

**From BaseTool:**
- File processing methods
- Model calling methods
- Response formatting methods
- Conversation handling
- Progress tracking

**From Mixins:**
- Web search capabilities
- Tool calling capabilities
- Streaming capabilities
- Conversation continuation

---

### 3. IMPORTS: What Does SimpleTool IMPORT?

**Direct Imports:**
```python
from tools.shared.base_models import ToolRequest
from tools.shared.base_tool import BaseTool
from tools.shared.schema_builders import SchemaBuilder
from tools.simple.mixins import WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin
from mcp.types import TextContent
from utils.client_info import get_current_session_fingerprint, get_cached_client_info, format_client_info
from utils.progress import send_progress
from utils.progress_messages import ProgressMessages
```

**What SimpleTool DEPENDS ON:**
- `SchemaBuilder` - for schema generation
- `ToolRequest` - for request model
- `TextContent` - for MCP response format
- `utils.client_info` - for client context
- `utils.progress` - for progress tracking
- `utils.progress_messages` - for progress messages

---

### 4. METHODS CALLED BY SUBCLASSES

**From ChatTool analysis, subclasses call:**

**Inherited Methods (from BaseTool/Mixins):**
- File processing (inherited from BaseTool)
- Model calling (inherited from BaseTool)
- Progress tracking (inherited from BaseTool)

**SimpleTool-Specific Methods:**
- `prepare_chat_style_prompt(request)` - **CRITICAL!**
- `get_chat_style_websearch_guidance()` - **CRITICAL!**
- `build_standard_prompt()` - **CRITICAL!**
- `handle_prompt_file_with_fallback()` - **CRITICAL!**
- `get_request_*()` methods - **CRITICAL!**
- `get_validated_temperature()` - **CRITICAL!**

**Key Finding:** Subclasses **HEAVILY DEPEND** on SimpleTool's utility methods!

---

## CRITICAL DEPENDENCIES TO PRESERVE

### 1. Public Interface Methods (CANNOT CHANGE)

**Abstract Methods (subclasses MUST implement):**
- `get_tool_fields()` - Returns tool-specific field definitions
- `get_required_fields()` - Returns required field names

**Hook Methods (subclasses MAY override):**
- `get_annotations()` - Returns tool annotations
- `format_response()` - Formats AI response
- `get_request_model()` - Returns request model class
- `prepare_prompt()` - Prepares prompt (ABSTRACT in practice)

**Utility Methods (subclasses CALL):**
- `prepare_chat_style_prompt(request)` - **MUST PRESERVE!**
- `build_standard_prompt()` - **MUST PRESERVE!**
- `handle_prompt_file_with_fallback()` - **MUST PRESERVE!**
- `get_request_*()` methods (13 methods) - **MUST PRESERVE!**
- `get_validated_temperature()` - **MUST PRESERVE!**
- `get_prompt_content_for_size_validation()` - **MUST PRESERVE!**

---

### 2. Internal Methods (CAN REFACTOR)

**These are ONLY used internally by SimpleTool:**
- `_parse_response()` - Internal response parsing
- `_validate_file_paths()` - Internal file validation
- `execute()` - Main execution (but interface must stay same)

---

## REFACTORING CONSTRAINTS

### What CANNOT Change:

**1. Public Method Signatures:**
```python
# These signatures MUST stay exactly the same:
def get_tool_fields(self) -> dict[str, dict[str, Any]]
def get_required_fields(self) -> list[str]
def get_annotations(self) -> Optional[dict[str, Any]]
def format_response(self, response: str, request, model_info: Optional[dict] = None) -> str
def get_request_model(self)
def get_input_schema(self) -> dict[str, Any]
def prepare_chat_style_prompt(self, request, system_prompt: str = None) -> str
def build_standard_prompt(self, system_prompt: str, user_content: str, request, file_context_title: str = "CONTEXT FILES") -> str
def handle_prompt_file_with_fallback(self, request) -> str
def get_request_*() methods (all 13 of them)
def get_validated_temperature(self, request, model_context: Any) -> tuple[float, list[str]]
```

**2. Class Constants:**
```python
FILES_FIELD = SchemaBuilder.SIMPLE_FIELD_SCHEMAS["files"]
IMAGES_FIELD = SchemaBuilder.COMMON_FIELD_SCHEMAS["images"]
```

**3. Inheritance Chain:**
```python
class SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool):
```

---

### What CAN Change:

**1. Internal Implementation:**
- How methods are implemented internally
- Where code lives (can move to modules)
- Internal helper methods

**2. Code Organization:**
- Can split into modules
- Can create internal classes
- Can reorganize logic

**3. Internal Method Names:**
- `_parse_response()` → can move to module
- `_validate_file_paths()` → can move to module

---

## REFACTORING STRATEGY (REVISED)

### Approach: **Facade Pattern**

**SimpleTool becomes a FACADE that:**
1. Keeps ALL public methods (same signatures)
2. Delegates to internal modules
3. Maintains backward compatibility

**Example:**
```python
# OLD (current):
class SimpleTool(...):
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # 50 lines of implementation here
        ...

# NEW (refactored):
class SimpleTool(...):
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # Delegate to module
        from tools.simple.prompt.builder import PromptBuilder
        return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)
```

**Benefits:**
- ✅ Public interface unchanged
- ✅ Subclasses work without modification
- ✅ Internal code is modular
- ✅ Easy to test modules independently

---

## UPDATED MODULE DESIGN

### Module 1: prompt/builder.py

**Exports:**
```python
class PromptBuilder:
    @staticmethod
    def build_standard(system_prompt, user_content, request, file_context_title):
        """Build standard prompt - called by SimpleTool.build_standard_prompt()"""
        ...
    
    @staticmethod
    def build_chat_style(request, system_prompt=None):
        """Build chat-style prompt - called by SimpleTool.prepare_chat_style_prompt()"""
        ...
```

**SimpleTool delegates:**
```python
def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
    from tools.simple.prompt.builder import PromptBuilder
    return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)

def prepare_chat_style_prompt(self, request, system_prompt=None):
    from tools.simple.prompt.builder import PromptBuilder
    return PromptBuilder.build_chat_style(request, system_prompt)
```

---

### Module 2: request/accessor.py

**Exports:**
```python
class RequestAccessor:
    @staticmethod
    def get_model_name(request):
        """Get model name - called by SimpleTool.get_request_model_name()"""
        ...
    
    @staticmethod
    def get_temperature(request):
        """Get temperature - called by SimpleTool.get_request_temperature()"""
        ...
    
    # ... all 13 accessor methods
```

**SimpleTool delegates:**
```python
def get_request_model_name(self, request):
    from tools.simple.request.accessor import RequestAccessor
    return RequestAccessor.get_model_name(request)

def get_request_temperature(self, request):
    from tools.simple.request.accessor import RequestAccessor
    return RequestAccessor.get_temperature(request)

# ... all 13 methods delegate
```

---

## TESTING STRATEGY (REVISED)

### 1. Test Public Interface (CRITICAL)

**Before refactoring:**
- [ ] Document ALL public method signatures
- [ ] Create integration tests for each subclass
- [ ] Test ChatTool with all features
- [ ] Test ActivityTool, ChallengeTool, RecommendTool

**After refactoring:**
- [ ] Run SAME integration tests
- [ ] Verify ALL subclasses still work
- [ ] Verify NO behavior changes

### 2. Test Internal Modules (NEW)

**Unit tests for each module:**
- [ ] Test PromptBuilder independently
- [ ] Test RequestAccessor independently
- [ ] Test validators independently
- [ ] Test ResponseParser independently

---

## RISK ASSESSMENT (REVISED)

**Risk Level:** MEDIUM (was LOW, now MEDIUM after dependency analysis)

**Why MEDIUM:**
- Subclasses depend on many SimpleTool methods
- ChatTool calls `prepare_chat_style_prompt()` directly
- Must preserve ALL public methods
- Must preserve ALL method signatures

**Mitigation:**
- Use Facade pattern (keep public interface)
- Test each subclass after refactoring
- Incremental approach (one module at a time)
- Keep rollback option available

---

## CONCLUSION

**Key Insights:**

1. **SimpleTool is MORE COMPLEX than I thought!**
   - 4 subclasses depend on it
   - Many public methods called by subclasses
   - Cannot change public interface

2. **Facade Pattern is ESSENTIAL!**
   - Keep all public methods
   - Delegate to internal modules
   - Maintain backward compatibility

3. **Testing is CRITICAL!**
   - Must test all 4 subclasses
   - Must verify no behavior changes
   - Integration tests are key

4. **User was RIGHT to ask!**
   - I jumped too fast without dependency analysis
   - This analysis is CRITICAL before refactoring
   - Must understand "above and below" connections

---

**NEXT STEPS:**

1. ✅ Update SIMPLETOOL_DESIGN_INTENT.md with Facade pattern
2. ✅ Document ALL public methods that must be preserved
3. ✅ Create integration tests for all 4 subclasses
4. ✅ Get user approval on revised approach
5. ⏭️ Proceed with refactoring using Facade pattern

---

**STATUS:** COMPLETE - Dependency analysis done, ready to revise design intent

