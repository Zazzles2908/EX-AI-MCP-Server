# SIMPLETOOL DESIGN INTENT (TOP-DOWN DESIGN - OPTION C)
**Date:** 2025-10-10 4:45 PM AEDT (COMPLETE REWRITE with Top-Down Design)
**File:** `tools/simple/base.py`
**Status:** ✅ **APPROVED BY USER** - Top-Down Design (Option C - Hybrid)
**Next Step:** Complete Phase 1 Discovery (Tasks 1.3-1.10) before implementation

---

## CRITICAL UPDATE: TOP-DOWN DESIGN

**User Feedback:**
> "Should be more like Top-Down Design (Stepwise Refinement or Decomposition) so it like splits into categories."

**Response:** Complete rewrite using **Top-Down Design (Option C - Hybrid)**:
- ✅ Organize by **conceptual responsibility** (what it represents)
- ✅ NOT by implementation details (what code does)
- ✅ Use **domain language**: definition, intake, preparation, execution, delivery
- ✅ Result: **7 files (5 folders)** instead of 9 files (6 folders)

**See also:**
- `SIMPLETOOL_DEPENDENCY_ANALYSIS.md` - Complete dependency graph
- `SIMPLETOOL_TOP_DOWN_ANALYSIS.md` - Bottom-up vs Top-down comparison

---

## FILE INFORMATION

**File Path:** `tools/simple/base.py`  
**Current Size:** `55.3KB`  
**Lines of Code:** `1220 lines`  
**Used By:** `4 simple tools (activity, challenge, chat, recommend)`  
**Impact Radius:** `MEDIUM (4 tools, but foundational for simple tool pattern)`

---

## DEPENDENCY ANALYSIS (SUMMARY)

**See `SIMPLETOOL_DEPENDENCY_ANALYSIS.md` for complete analysis.**

**UPSTREAM (4 tools depend on SimpleTool):**
- ActivityTool, ChallengeTool, ChatTool, RecommendTool
- ChatTool **HEAVILY uses** SimpleTool methods

**DOWNSTREAM (SimpleTool inherits from):**
- WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool

**PUBLIC INTERFACE (CANNOT CHANGE):**
- 9 critical methods that subclasses call
- Class constants: FILES_FIELD, IMAGES_FIELD
- Inheritance chain must be preserved

---

## CURRENT STATE ANALYSIS

**SimpleTool does EVERYTHING (13 distinct responsibilities):**
1. Schema generation (6 methods)
2. Request field access (10 methods)
3. Request validation (2 methods)
4. Prompt building (4 methods)
5. Response formatting (3 methods)
6. Tool execution (2 methods)
7. Plus inherited capabilities from 5 mixins

**Problem:** Monolithic file with multiple responsibilities!

---

## SINGLE RESPONSIBILITY

**SimpleTool's TRUE responsibility:**
> "Orchestrate the execution of simple tools by coordinating tool definition, request intake, prompt preparation, model execution, and response delivery through a clean, extensible interface."

**Key insight:** SimpleTool should be a **THIN ORCHESTRATOR** that delegates to conceptual modules!

---

## REFACTORING APPROACH: FACADE PATTERN + TOP-DOWN DESIGN

**Approach:** SimpleTool becomes a **FACADE** that:
- Keeps ALL public methods (same signatures)
- Delegates to conceptual modules (Top-Down organization)
- Maintains 100% backward compatibility
- Organizes by domain language (definition, intake, preparation, execution, delivery)

**Example:**
```python
class SimpleTool(...):
    """Facade that delegates to conceptual modules"""
    
    # DEFINITION: Tool Contract
    def get_input_schema(self):
        from tools.simple.definition.schema import SchemaBuilder
        return SchemaBuilder.build_schema(self)
    
    # INTAKE: Request Processing
    def get_request_prompt(self, request):
        from tools.simple.intake.accessor import RequestAccessor
        return RequestAccessor.get_prompt(request)
    
    # PREPARATION: Prompt Building
    def build_standard_prompt(self, ...):
        from tools.simple.preparation.prompt import PromptBuilder
        return PromptBuilder.build_standard(...)
    
    # EXECUTION: Model Calling
    def execute(self, arguments):
        from tools.simple.execution.caller import ModelCaller
        return ModelCaller.execute(self, arguments)
    
    # DELIVERY: Response Formatting
    def format_response(self, response, request, model_info=None):
        from tools.simple.delivery.formatter import ResponseFormatter
        return ResponseFormatter.format(response, request, model_info)
```

---

## PROPOSED REFACTORING (TOP-DOWN - OPTION C)

### Target Structure

```
tools/simple/
├── base.py (SimpleTool - ORCHESTRATOR ~150-200 lines)
│
├── definition/         ← "What does this tool promise?"
│   └── schema.py      (~150-200 lines)
│
├── intake/             ← "What did the user ask for?"
│   ├── accessor.py    (~200-250 lines)
│   └── validator.py   (~150-200 lines)
│
├── preparation/        ← "How do we ask the AI?"
│   ├── prompt.py      (~200-250 lines)
│   └── files.py       (~80-100 lines)
│
├── execution/          ← "How do we call the AI?"
│   └── caller.py      (~200-250 lines)
│
└── delivery/           ← "How do we deliver the result?"
    └── formatter.py   (~150-200 lines)
```

**Total:** 7 files across 5 folders (vs 9 files across 6 folders in bottom-up approach)

---

## MODULE BREAKDOWN (TOP-DOWN - CONCEPTUAL CATEGORIES)

### Module 1: definition/ - "What does this tool promise?"

**Conceptual Responsibility:** Tool Contract

**File:** `definition/schema.py` (~150-200 lines)

**Methods (6 total):**
- `get_input_schema()` - Generate JSON schema
- `get_tool_fields()` - Define tool-specific fields
- `get_required_fields()` - Define required fields
- `get_annotations()` - Tool annotations
- `supports_custom_request_model()` - Custom model support
- `get_request_model()` - Request model class

**Design Intent:**
> "Define the contract between the tool and the MCP server. What inputs does this tool accept? What outputs does it produce? What are the constraints?"

**Dependencies:** SchemaBuilder (shared)

**Used by:** MCP Server (tool registration), SimpleTool (schema generation)

---

### Module 2: intake/ - "What did the user ask for?"

**Conceptual Responsibility:** Request Processing

**File 1:** `intake/accessor.py` (~200-250 lines)

**Methods (10 total):**
- `get_request_prompt()` - Extract prompt
- `get_request_files()` - Extract files
- `get_request_images()` - Extract images
- `get_request_model_name()` - Extract model name
- `get_request_temperature()` - Extract temperature
- `get_request_thinking_mode()` - Extract thinking mode
- `get_request_use_websearch()` - Extract websearch flag
- `get_request_continuation_id()` - Extract continuation ID
- `get_request_as_dict()` - Convert to dict
- `set_request_files()` - Set files

**Design Intent:**
> "Safely extract and transform data from the user's request. Provide a clean interface for accessing request fields without exposing internal request structure."

**File 2:** `intake/validator.py` (~150-200 lines)

**Methods (2 total):**
- `_validate_file_paths()` - Validate file paths
- `get_validated_temperature()` - Validate temperature

**Design Intent:**
> "Validate user input to ensure it meets tool requirements. Catch errors early before processing begins."

**Dependencies:** None (pure data access/validation)

**Used by:** All other modules (need request data)

---

### Module 3: preparation/ - "How do we ask the AI?"

**Conceptual Responsibility:** Prompt Building

**File 1:** `preparation/prompt.py` (~200-250 lines)

**Methods (3 total):**
- `build_standard_prompt()` - Build standard prompts
- `prepare_chat_style_prompt()` - Build chat-style prompts
- `get_prompt_content_for_size_validation()` - Size validation

**Design Intent:**
> "Transform user input and context into well-formed prompts for AI models. Handle different prompt styles (standard, chat) and ensure prompts meet size constraints."

**File 2:** `preparation/files.py` (~80-100 lines)

**Methods (1 total):**
- `handle_prompt_file_with_fallback()` - Handle prompt.txt files

**Design Intent:**
> "Handle external prompt files (prompt.txt) with graceful fallback to default prompts when files are missing or invalid."

**Dependencies:** intake/ (for request data), utils/client_info, utils/progress

**Used by:** execution/ (needs prompts to call AI)

---

### Module 4: execution/ - "How do we call the AI?"

**Conceptual Responsibility:** Model Invocation

**File:** `execution/caller.py` (~200-250 lines)

**Methods (2 total):**
- `execute()` - Main execution method
- `_call_with_model()` - Internal model calling

**Design Intent:**
> "Execute the tool's core logic: prepare the prompt, call the AI model, and return the response. This is the main entry point for tool execution."

**Dependencies:** preparation/ (for prompts), BaseTool (for model calling), delivery/ (for formatting)

**Used by:** SimpleTool.execute() (main entry point from MCP server)

---

### Module 5: delivery/ - "How do we deliver the result?"

**Conceptual Responsibility:** Response Formatting

**File:** `delivery/formatter.py` (~150-200 lines)

**Methods (3 total):**
- `_parse_response()` - Parse raw AI response
- `format_response()` - Format for MCP protocol
- `get_actually_processed_files()` - Track processed files

**Design Intent:**
> "Transform raw AI responses into properly formatted MCP responses. Handle response parsing, formatting, and metadata tracking."

**Dependencies:** None (pure formatting)

**Used by:** execution/ (needs to format results before returning)

---

## MIGRATION STRATEGY

**See `SIMPLETOOL_TOP_DOWN_ANALYSIS.md` for detailed migration steps.**

**High-level approach:**
1. Create folder structure (definition/, intake/, preparation/, execution/, delivery/)
2. Extract definition/schema.py (schema generation methods)
3. Extract intake/accessor.py + intake/validator.py (request processing)
4. Extract preparation/prompt.py + preparation/files.py (prompt building)
5. Extract execution/caller.py (model calling)
6. Extract delivery/formatter.py (response formatting)
7. Update base.py to delegate to modules (Facade Pattern)
8. Test all 4 tools after each step

**Estimated effort:** 37-51 hours (5-7 days)

---

## IMPACT ASSESSMENT

**Risk Level:** MEDIUM (was LOW, now MEDIUM after dependency analysis)

**Why MEDIUM:**
- 4 subclasses depend on SimpleTool
- ChatTool calls methods directly
- Must preserve ALL public methods
- Must preserve ALL method signatures

**Mitigation:**
- Use Facade Pattern (keep public interface)
- Test each subclass after refactoring
- Incremental approach (one module at a time)
- Keep rollback option available

**Breaking Changes:** NONE (Facade Pattern ensures backward compatibility)

---

## SUCCESS CRITERIA

**Refactoring is successful when:**
- ✅ All 4 tools (ActivityTool, ChallengeTool, ChatTool, RecommendTool) work without modification
- ✅ All public methods preserved with same signatures
- ✅ All tests passing
- ✅ base.py reduced from 1220 lines to ~150-200 lines
- ✅ 7 focused modules with clear conceptual responsibilities
- ✅ Each module has single responsibility
- ✅ Code organized by domain language (definition, intake, preparation, execution, delivery)
- ✅ Easy to find things ("Where's request validation?" → intake/validator.py)

---

**STATUS:** Design intent complete - ready for implementation with Top-Down Design (Option C)

