# SIMPLETOOL DESIGN INTENT
**Date:** 2025-10-10 2:15 PM AEDT (REVISED after dependency analysis)
**File:** `tools/simple/base.py`
**Status:** REVISED - Phase 1.1 (Facade Pattern Approach)

---

## ⚠️ CRITICAL UPDATE

**User Feedback:** "It appeared you were building a template and filling it in afterwards... it looked like you were just building brand new."

**Response:** CORRECT! I was designing a "new system" instead of **refactoring the existing system**.

**Revised Approach:** Use **Facade Pattern** to refactor internal implementation while preserving 100% backward compatibility.

**See:** `SIMPLETOOL_DEPENDENCY_ANALYSIS.md` for complete dependency graph.

---

## FILE INFORMATION

**File Path:** `tools/simple/base.py`
**Current Size:** `55.3KB`
**Lines of Code:** `1220 lines`
**Used By:** `4 simple tools (activity, challenge, chat, recommend)`
**Impact Radius:** `MEDIUM (4 tools, but foundational for simple tool pattern)`

---

## DEPENDENCY ANALYSIS (CRITICAL!)

### UPSTREAM: What Inherits FROM SimpleTool?

**Direct Subclasses (4 tools):**
- ActivityTool (tools/activity.py)
- ChallengeTool (tools/challenge.py)
- ChatTool (tools/chat.py) ← **HEAVILY uses SimpleTool methods!**
- RecommendTool (tools/capabilities/recommend.py)

**What They Call (from ChatTool analysis):**
- `prepare_chat_style_prompt(request)` ← **CRITICAL!**
- `build_standard_prompt(...)` ← **CRITICAL!**
- `get_chat_style_websearch_guidance()` ← **CRITICAL!**
- All `get_request_*()` methods (13 methods) ← **CRITICAL!**
- `get_validated_temperature()` ← **CRITICAL!**

**Key Finding:** Subclasses **DEPEND ON** many SimpleTool methods - cannot remove them!

### DOWNSTREAM: What Does SimpleTool INHERIT FROM?

**Inheritance Chain:**
```
SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool)
└── BaseTool(BaseToolCore, FileHandlingMixin, ModelManagementMixin, ResponseFormattingMixin)
```

**What SimpleTool USES:**
- File processing (from BaseTool)
- Model calling (from BaseTool)
- Web search (from WebSearchMixin)
- Streaming (from StreamingMixin)
- Conversation continuation (from ContinuationMixin)

### PUBLIC INTERFACE: What CANNOT Change?

**Methods Called by Subclasses (MUST PRESERVE):**
- `prepare_chat_style_prompt(request, system_prompt=None)` ← ChatTool calls this
- `build_standard_prompt(...)` ← Multiple tools call this
- `handle_prompt_file_with_fallback(request)` ← File handling
- All `get_request_*()` methods (13 methods) ← All tools use these
- `get_validated_temperature(request, model_context)` ← Temperature handling
- `get_input_schema()` ← Schema generation
- `get_tool_fields()` ← Abstract method (subclasses implement)
- `get_required_fields()` ← Abstract method (subclasses implement)
- `format_response()` ← Hook method (subclasses override)

**Class Constants (MUST PRESERVE):**
- `FILES_FIELD` ← Referenced by subclasses
- `IMAGES_FIELD` ← Referenced by subclasses

**Inheritance Chain (MUST PRESERVE):**
- `SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool)` ← Cannot change!

---

## CURRENT STATE ANALYSIS

### What Does This File Currently Do?

**ALL Responsibilities (exhaustive list):**

1. **Schema Generation** (lines 142-163)
   - Generate complete input schema using SchemaBuilder
   - Combine tool-specific fields with common fields
   - Handle required fields and model field schema

2. **Request Attribute Access** (lines 176-283)
   - Safe attribute access without hasattr/getattr
   - Get model name, images, continuation_id, prompt, temperature, thinking_mode
   - Get files, use_websearch, convert request to dict
   - Set files on request
   - Track actually processed files

3. **Temperature Validation** (lines 211-228)
   - Extract temperature from request
   - Validate against model constraints
   - Apply default if not provided

4. **File Path Validation** (lines 1100-1180)
   - Validate all file paths are absolute
   - Check against allowed roots (TEST_FILES_DIR)
   - Security measure against path traversal

5. **Prompt Building** (lines 966-1018)
   - Build standard prompts with system prompt + user content
   - Add file context if files provided
   - Add client info if available
   - Format with proper structure

6. **Prompt File Handling** (lines 1046-1085)
   - Handle prompt.txt files with fallback to request field
   - Extract user content from files or request
   - Validate prompt size

7. **Size Validation** (lines 1020-1044)
   - Get prompt content for size validation
   - Handle conversation history embedding
   - Use original user prompt when available

8. **Chat-Style Prompt Preparation** (lines 1182-1220)
   - Prepare prompts using Chat tool patterns
   - Handle prompt.txt files
   - Add file context
   - Add client info

9. **Response Parsing** (lines 880-963)
   - Parse raw AI response
   - Format using format_response hook
   - Handle conversation continuation
   - Create ToolOutput with metadata

10. **Tool Execution** (lines 285-878)
    - Main execute() method
    - Progress tracking
    - File processing
    - Model calling
    - Error handling
    - Response formatting

11. **Abstract Methods** (lines 71-96, 98-108)
    - get_tool_fields() - tool-specific field definitions
    - get_required_fields() - required field names

12. **Hook Methods** (lines 110-140, 165-172)
    - get_annotations() - tool annotations
    - format_response() - response formatting
    - get_request_model() - request model class

13. **Mixin Integration** (inherited from 5 mixins)
    - WebSearchMixin - web search capabilities
    - ToolCallMixin - tool calling capabilities
    - StreamingMixin - streaming capabilities
    - ContinuationMixin - conversation continuation
    - BaseTool - core tool functionality

**Current Structure:**
```
class SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool):
    - Class constants: FILES_FIELD, IMAGES_FIELD
    - Abstract methods: get_tool_fields(), get_required_fields()
    - Hook methods: get_annotations(), format_response(), get_request_model()
    - Schema generation: get_input_schema()
    - Request accessors: 13 methods for safe attribute access
    - Temperature validation: get_validated_temperature()
    - File validation: _validate_file_paths()
    - Prompt building: build_standard_prompt(), prepare_chat_style_prompt()
    - Prompt file handling: handle_prompt_file_with_fallback()
    - Size validation: get_prompt_content_for_size_validation()
    - Response parsing: _parse_response()
    - Tool execution: execute() (main method)
    - Utility: supports_custom_request_model()
```

**Dependencies:**
- Imports from: tools/shared/, tools/simple/mixins/, utils/, mcp.types
- Used by: activity.py, challenge.py, chat.py, recommend.py

---

## SINGLE RESPONSIBILITY ANALYSIS

### What SHOULD This File Do? (Single Responsibility)

**Primary Responsibility:**
> "Orchestrate the execution of simple tools by coordinating prompt preparation, model calling, and response formatting through a clean, extensible interface."

**In other words:**
- SimpleTool should be the **orchestrator** that coordinates different concerns
- It should **delegate** specific responsibilities to focused modules
- It should provide a **clean interface** for simple tool implementations

---

### What Doesn't Belong Here? (Misplaced Responsibilities)

**Responsibilities that should be elsewhere:**

1. **Prompt Building Logic** (lines 966-1018, 1182-1220) → Should be in: `tools/simple/prompt/builder.py`
   - Building standard prompts
   - Adding file context
   - Adding client info
   - Chat-style prompt preparation
   - **Why:** Prompt construction is a distinct concern from orchestration

2. **Request Attribute Access** (lines 176-283) → Should be in: `tools/simple/request/accessor.py`
   - Safe attribute access methods
   - Request to dict conversion
   - File setting on request
   - **Why:** Request handling is a distinct concern from orchestration

3. **File Path Validation** (lines 1100-1180) → Should be in: `tools/simple/validation/file_validator.py`
   - Absolute path validation
   - Allowed roots checking
   - Security validation
   - **Why:** Validation is a distinct concern from orchestration

4. **Prompt File Handling** (lines 1046-1085) → Should be in: `tools/simple/prompt/file_handler.py`
   - Extracting prompts from files
   - Fallback to request field
   - Size validation
   - **Why:** File handling is a distinct concern from prompt building

5. **Size Validation** (lines 1020-1044) → Should be in: `tools/simple/validation/size_validator.py`
   - Prompt size validation
   - Conversation history handling
   - Original prompt extraction
   - **Why:** Validation is a distinct concern from orchestration

6. **Response Parsing** (lines 880-963) → Should be in: `tools/simple/response/parser.py`
   - Parsing raw AI response
   - Formatting response
   - Creating ToolOutput
   - **Why:** Response handling is a distinct concern from orchestration

7. **Schema Generation** (lines 142-163) → Should be in: `tools/simple/schema/generator.py`
   - Combining field schemas
   - Handling required fields
   - Model field schema
   - **Why:** Schema generation is a distinct concern from orchestration

8. **Temperature Validation** (lines 211-228) → Should be in: `tools/simple/validation/temperature_validator.py`
   - Temperature extraction
   - Validation against model constraints
   - Default application
   - **Why:** Validation is a distinct concern from orchestration

---

## REFACTORING APPROACH: FACADE PATTERN

**CRITICAL:** This is NOT building a new system - this is **refactoring the existing system**!

**Approach:** SimpleTool becomes a **FACADE**
- Keeps ALL public methods (same signatures)
- Delegates to internal modules for implementation
- Maintains 100% backward compatibility
- Subclasses see NO changes

**Why Facade Pattern?**
- ✅ Public interface unchanged (ChatTool, ActivityTool, etc. work without modification)
- ✅ Internal code is modular (easy to maintain)
- ✅ Easy to test modules independently
- ✅ Zero breaking changes
- ✅ Can refactor incrementally (one module at a time)

**Example:**
```python
# BEFORE (current - monolithic):
class SimpleTool:
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # 50 lines of implementation
        client_info = get_cached_client_info()
        if client_info:
            full_prompt += f"\n\n## CLIENT CONTEXT\n{format_client_info(client_info)}"
        # ... more code ...
        return full_prompt

# AFTER (refactored - facade):
class SimpleTool:
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # Same signature, delegate to module
        from tools.simple.prompt.builder import PromptBuilder
        return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)
```

**ChatTool sees NO difference:**
```python
# ChatTool code - UNCHANGED!
def prepare_prompt(self, request):
    base_prompt = self.build_standard_prompt(...)  # ✅ Still works exactly the same!
```

---

## PROPOSED REFACTORING

### Target State: Modular Structure with Facade

**Proposed folder structure:**
```
tools/simple/
├── base.py (~150-200 lines)
│   SINGLE RESPONSIBILITY: Orchestrate simple tool execution
│   - Coordinate prompt preparation
│   - Coordinate model calling
│   - Coordinate response formatting
│   - Provide clean interface for simple tools
│
├── prompt/
│   ├── __init__.py
│   ├── builder.py (~100-150 lines)
│   │   SINGLE RESPONSIBILITY: Build prompts for simple tools
│   │   - Build standard prompts
│   │   - Add file context
│   │   - Add client info
│   │
│   └── file_handler.py (~80-100 lines)
│       SINGLE RESPONSIBILITY: Handle prompt.txt files
│       - Extract prompts from files
│       - Fallback to request field
│       - Size validation integration
│
├── request/
│   ├── __init__.py
│   └── accessor.py (~120-150 lines)
│       SINGLE RESPONSIBILITY: Safe request attribute access
│       - Get model, images, continuation_id, prompt, etc.
│       - Convert request to dict
│       - Set files on request
│
├── validation/
│   ├── __init__.py
│   ├── file_validator.py (~100-120 lines)
│   │   SINGLE RESPONSIBILITY: Validate file paths
│   │   - Check absolute paths
│   │   - Validate against allowed roots
│   │   - Security checks
│   │
│   ├── size_validator.py (~50-80 lines)
│   │   SINGLE RESPONSIBILITY: Validate prompt sizes
│   │   - Check prompt size limits
│   │   - Handle conversation history
│   │   - Extract original prompts
│   │
│   └── temperature_validator.py (~40-60 lines)
│       SINGLE RESPONSIBILITY: Validate temperature
│       - Extract temperature from request
│       - Validate against model constraints
│       - Apply defaults
│
├── response/
│   ├── __init__.py
│   └── parser.py (~100-120 lines)
│       SINGLE RESPONSIBILITY: Parse and format responses
│       - Parse raw AI response
│       - Format using hook method
│       - Create ToolOutput
│       - Handle conversation continuation
│
├── schema/
│   ├── __init__.py
│   └── generator.py (~60-80 lines)
│       SINGLE RESPONSIBILITY: Generate input schemas
│       - Combine tool-specific and common fields
│       - Handle required fields
│       - Model field schema
│
├── execution/
│   ├── __init__.py
│   └── executor.py (~200-250 lines)
│       SINGLE RESPONSIBILITY: Execute tool logic
│       - Progress tracking
│       - File processing
│       - Model calling
│       - Error handling
│
└── mixins/ (existing - keep as-is)
    ├── continuation_mixin.py
    ├── streaming_mixin.py
    ├── tool_call_mixin.py
    ├── web_search_mixin.py
    └── file_mixin.py
```

---

## MODULE BREAKDOWN

### Module 1: Prompt Building

**Purpose:** Build prompts for simple tools  
**Files:**
- `prompt/builder.py` - Build standard prompts with system prompt, user content, files, client info
- `prompt/file_handler.py` - Handle prompt.txt files with fallback to request field

**Size estimate:** ~180-250 lines total  
**Dependencies:** utils/client_info, utils/file_utils  
**Used by:** base.py (SimpleTool.execute)

### Module 2: Request Access

**Purpose:** Safe request attribute access  
**Files:**
- `request/accessor.py` - Get/set request attributes safely

**Size estimate:** ~120-150 lines total  
**Dependencies:** None (pure accessor methods)  
**Used by:** base.py, prompt/builder.py, validation modules

### Module 3: Validation

**Purpose:** Validate inputs (files, size, temperature)  
**Files:**
- `validation/file_validator.py` - Validate file paths and security
- `validation/size_validator.py` - Validate prompt sizes
- `validation/temperature_validator.py` - Validate temperature

**Size estimate:** ~190-260 lines total  
**Dependencies:** utils/model_restrictions, utils/file_utils  
**Used by:** base.py, execution/executor.py

### Module 4: Response Handling

**Purpose:** Parse and format AI responses  
**Files:**
- `response/parser.py` - Parse raw response, format, create ToolOutput

**Size estimate:** ~100-120 lines total  
**Dependencies:** tools/shared/base_models, mcp.types  
**Used by:** base.py (SimpleTool.execute)

### Module 5: Schema Generation

**Purpose:** Generate input schemas  
**Files:**
- `schema/generator.py` - Combine fields, handle required fields

**Size estimate:** ~60-80 lines total  
**Dependencies:** tools/shared/schema_builders  
**Used by:** base.py (SimpleTool.get_input_schema)

### Module 6: Execution

**Purpose:** Execute tool logic  
**Files:**
- `execution/executor.py` - Main execution logic with progress, file processing, model calling

**Size estimate:** ~200-250 lines total  
**Dependencies:** All other modules  
**Used by:** base.py (SimpleTool.execute)

---

## DESIGN INTENT DOCUMENTATION (Per Module)

### prompt/builder.py

```python
"""
SINGLE RESPONSIBILITY: Build prompts for simple tools

DESIGN INTENT:
- Takes system prompt, user content, and optional files/client info
- Constructs complete prompt string with proper formatting
- Adds file context section if files provided
- Adds client info section if available
- Returns formatted prompt ready for AI model

DOES NOT:
- Call AI models (that's execution/executor.py)
- Validate file paths (that's validation/file_validator.py)
- Handle response formatting (that's response/parser.py)

DEPENDENCIES:
- utils/client_info (for client context)
- utils/file_utils (for file reading)

USED BY:
- tools/simple/base.py (SimpleTool)
- tools/simple/execution/executor.py

EXAMPLE USAGE:
    from tools.simple.prompt.builder import PromptBuilder
    
    builder = PromptBuilder()
    prompt = builder.build_standard_prompt(
        system_prompt="You are a helpful assistant",
        user_content="What is Python?",
        files=["file1.txt", "file2.txt"],
        include_client_info=True
    )
    # Returns: Complete formatted prompt string
"""
```

### request/accessor.py

```python
"""
SINGLE RESPONSIBILITY: Safe request attribute access

DESIGN INTENT:
- Provides safe methods to access request attributes
- Handles AttributeError gracefully (no hasattr/getattr)
- Returns sensible defaults when attributes missing
- Converts request to dictionary format
- Sets attributes on request safely

DOES NOT:
- Validate attribute values (that's validation modules)
- Build prompts (that's prompt/builder.py)
- Execute tools (that's execution/executor.py)

DEPENDENCIES:
- None (pure accessor methods)

USED BY:
- tools/simple/base.py
- tools/simple/prompt/builder.py
- tools/simple/validation modules

EXAMPLE USAGE:
    from tools.simple.request.accessor import RequestAccessor
    
    accessor = RequestAccessor()
    model_name = accessor.get_model_name(request)  # Returns None if missing
    temperature = accessor.get_temperature(request)  # Returns None if missing
    files = accessor.get_files(request)  # Returns [] if missing
```

[Continue for each module...]

---

## MIGRATION STRATEGY

### Step-by-Step Refactoring Plan

**Step 1: Create Module Structure** (2-3 hours)
- [ ] Create folders: prompt/, request/, validation/, response/, schema/, execution/
- [ ] Create `__init__.py` files for each folder
- [ ] Set up imports structure

**Step 2: Extract Request Accessor** (4-6 hours)
- [ ] Create `request/accessor.py`
- [ ] Move all get_request_* methods (lines 176-283)
- [ ] Create RequestAccessor class
- [ ] Update base.py to use RequestAccessor
- [ ] Test: All 4 simple tools still work

**Step 3: Extract Validation Modules** (6-8 hours)
- [ ] Create `validation/file_validator.py` (lines 1100-1180)
- [ ] Create `validation/size_validator.py` (lines 1020-1044)
- [ ] Create `validation/temperature_validator.py` (lines 211-228)
- [ ] Update base.py to use validators
- [ ] Test: All 4 simple tools still work

**Step 4: Extract Prompt Building** (6-8 hours)
- [ ] Create `prompt/builder.py` (lines 966-1018, 1182-1220)
- [ ] Create `prompt/file_handler.py` (lines 1046-1085)
- [ ] Update base.py to use prompt modules
- [ ] Test: All 4 simple tools still work

**Step 5: Extract Response Parser** (4-6 hours)
- [ ] Create `response/parser.py` (lines 880-963)
- [ ] Update base.py to use ResponseParser
- [ ] Test: All 4 simple tools still work

**Step 6: Extract Schema Generator** (3-4 hours)
- [ ] Create `schema/generator.py` (lines 142-163)
- [ ] Update base.py to use SchemaGenerator
- [ ] Test: All 4 simple tools still work

**Step 7: Extract Execution Logic** (8-10 hours)
- [ ] Create `execution/executor.py` (lines 285-878)
- [ ] Move main execute() logic
- [ ] Update base.py to orchestrate executor
- [ ] Test: All 4 simple tools still work

**Step 8: Final Integration** (4-6 hours)
- [ ] Verify base.py is ~150-200 lines (orchestration only)
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Commit and push

**Total Estimated Time:** 37-51 hours (5-7 days)

---

## IMPACT ASSESSMENT

### Breaking Changes

**Import Path Changes:**
- Old: `from tools.simple.base import SimpleTool`
- New: `from tools.simple.base import SimpleTool` (NO CHANGE - same interface!)

**Internal Changes Only:**
- SimpleTool interface remains the same
- All public methods remain the same
- Only internal implementation changes

**Affected Files:**
- activity.py, challenge.py, chat.py, recommend.py
- NO import changes needed (internal refactoring only)

**Risk Level:** LOW (internal refactoring, same interface)

---

## TESTING STRATEGY

**Unit Tests:**
- [ ] Test RequestAccessor: All get/set methods
- [ ] Test FileValidator: Path validation, security checks
- [ ] Test SizeValidator: Size limits, conversation history
- [ ] Test TemperatureValidator: Validation, defaults
- [ ] Test PromptBuilder: Standard prompts, file context, client info
- [ ] Test PromptFileHandler: File extraction, fallback
- [ ] Test ResponseParser: Parsing, formatting, ToolOutput creation
- [ ] Test SchemaGenerator: Field combination, required fields
- [ ] Test Executor: Progress, file processing, model calling
- [ ] Test SimpleTool orchestration: All modules work together

**Integration Tests:**
- [ ] Test activity tool: Full execution
- [ ] Test challenge tool: Full execution
- [ ] Test chat tool: Full execution
- [ ] Test recommend tool: Full execution

**Manual Testing:**
- [ ] Run each tool with various inputs
- [ ] Test file handling
- [ ] Test conversation continuation
- [ ] Test error handling

---

## EFFORT ESTIMATE

**Total Effort:** 37-51 hours (5-7 days)

**Breakdown:**
- Module structure creation: 2-3 hours
- Request accessor extraction: 4-6 hours
- Validation modules extraction: 6-8 hours
- Prompt building extraction: 6-8 hours
- Response parser extraction: 4-6 hours
- Schema generator extraction: 3-4 hours
- Execution logic extraction: 8-10 hours
- Final integration: 4-6 hours

**Risk Factors:**
- Import hell: Mitigate with careful planning and testing
- Breaking changes: Mitigate with same interface guarantee
- Test failures: Mitigate with incremental testing

---

## SUCCESS CRITERIA

**Refactoring Complete When:**
- [ ] base.py is ~150-200 lines (orchestration only)
- [ ] Each module is <200 lines
- [ ] Each module has ONE clear responsibility
- [ ] All imports updated internally
- [ ] All 4 simple tools working
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No regressions

---

## ROLLBACK PLAN

**If refactoring fails:**
1. Revert to commit before refactoring
2. Document what went wrong
3. Adjust strategy
4. Try again with lessons learned

**Rollback triggers:**
- Tests fail and can't be fixed within 4 hours
- Performance degradation >10%
- Breaking changes affect tools
- User requests rollback

---

## NOTES

**Additional considerations:**
- Keep mixins as-is (already modular)
- Maintain backward compatibility
- Document all modules thoroughly
- Consider performance impact

**Questions for user:**
- Any specific concerns about this refactoring?
- Any modules to prioritize?
- Any edge cases to consider?

---

**STATUS:** DRAFT - Ready for review and approval

