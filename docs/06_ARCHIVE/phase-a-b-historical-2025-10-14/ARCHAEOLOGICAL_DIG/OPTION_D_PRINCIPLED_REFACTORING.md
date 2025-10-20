# OPTION D: PRINCIPLED REFACTORING STRATEGY (TOP-DOWN DESIGN)
**Date:** 2025-10-10 3:30 PM AEDT (UPDATED with Top-Down Design)
**Status:** ✅ APPROVED BY USER with Top-Down Design (Option C - Hybrid)
**Timeline:** 7-12 weeks for Phase 1 execution

---

## CRITICAL UPDATE: TOP-DOWN DESIGN

**User Feedback:**
> "Should be more like Top-Down Design (Stepwise Refinement or Decomposition) so it like splits into categories."

> "I would consider the top being even to the point of the entrance point, which is the daemon and mcp server point right?"

**Response:** User is 100% correct! Updated Option D to use **Top-Down Design (Option C - Hybrid)**:
- ✅ Organize by **conceptual responsibility**, not implementation details
- ✅ Use **domain language**: definition, intake, preparation, execution, delivery
- ✅ TRUE top-down starts from **entry points**: User → IDE → MCP Server → Daemon → Tools
- ✅ Result: **7 files (5 folders)** instead of 9 files (6 folders) - SMARTER organization!

---

## USER'S VISION

**Core Principles:**
1. **Single Responsibility Principle (SRP)**
2. **Top-Down Design (Stepwise Refinement)**
3. **Conceptual Categories** (not implementation details)

> "A script's purpose, for example, is to import a system prompt - it should just focus on that and have the libraries and other requirements to be imported and it is just managing those items. Then the script being called should focus on having the function call of the dynamic prompt retriever, and from that another script would be the dynamic maker of the prompt generator."

**Translation:**
- Each module has ONE clear purpose
- Easy to find which script to modify
- Modular design with clear separation
- Long-term stability through proper architecture

---

## WHAT'S WRONG WITH CURRENT ARCHITECTURE?

### Problem 1: "God Objects" - Files That Do Everything

**Example: SimpleTool (55.3KB, 1220 lines)**
```python
class SimpleTool:
    # Does EVERYTHING:
    - Schema generation
    - Prompt preparation
    - Model calling
    - Response formatting
    - File handling
    - Conversation management
    - Progress tracking
    - Web search
    - Tool calling
    - Streaming
    - Continuation
```

**Issue:** Want to change "how prompts are prepared"? Dig through 1220 lines!

---

### Problem 2: Utils Chaos - No Organization

**Current:**
```
utils/
├── file_utils.py
├── file_utils_expansion.py
├── file_utils_helpers.py
├── file_utils_json.py
├── file_utils_reading.py
├── file_utils_security.py
├── file_utils_tokens.py
# 9 files - which one does what?!
```

**Issue:** Want to change file reading? Which file? Unclear!

---

### Problem 3: Unclear Responsibilities

**Example: ExpertAnalysisMixin (34.1KB)**
- Location: `tools/workflow/expert_analysis.py`
- Used by: ALL 12 workflow tools
- Issue: Looks "workflow-specific" but it's SHARED INFRASTRUCTURE!

---

## OPTION D: PRINCIPLED REFACTORING

### Core Principles

**1. Single Responsibility Principle (SRP)**
- Each module does ONE thing
- Each module does it well
- Easy to find, easy to modify

**2. Separation of Concerns**
- Prompt building ≠ Model calling ≠ Response formatting
- Each concern gets its own module

**3. Modular Design**
- Small, focused modules
- Clear interfaces
- Easy to test

**4. Clear Organization**
- Folder structure reflects responsibilities
- Easy to navigate
- Industry-standard layout

---

## EXAMPLE: REFACTORING SimpleTool

### Current (Monolithic)

```python
# tools/simple/base.py (55.3KB, 1220 lines)
class SimpleTool:
    def execute(self, request):
        # 200 lines of prompt building
        # 300 lines of model calling
        # 150 lines of response formatting
        # 200 lines of file handling
        # 370 lines of other stuff
```

**Problem:** Everything in one file!

---

### After Refactoring (Modular)

```
tools/simple/
├── base.py (orchestration only - ~100 lines)
│   class SimpleTool:
│       def execute(self, request):
│           prompt = PromptBuilder().build(request)
│           response = ModelCaller().call(prompt)
│           return ResponseFormatter().format(response)
│
├── prompt/
│   ├── builder.py (~50 lines)
│   │   SINGLE RESPONSIBILITY: Build prompts
│   │   - Takes request data
│   │   - Constructs prompt string
│   │   - Returns complete prompt
│   │
│   └── validator.py (~50 lines)
│       SINGLE RESPONSIBILITY: Validate prompts
│       - Checks prompt structure
│       - Validates required fields
│       - Returns validation result
│
├── model/
│   ├── caller.py (~50 lines)
│   │   SINGLE RESPONSIBILITY: Call AI models
│   │   - Takes prompt
│   │   - Calls model provider
│   │   - Returns raw response
│   │
│   └── selector.py (~50 lines)
│       SINGLE RESPONSIBILITY: Select appropriate model
│       - Analyzes request
│       - Selects best model
│       - Returns model name
│
├── response/
│   ├── formatter.py (~50 lines)
│   │   SINGLE RESPONSIBILITY: Format responses
│   │   - Takes raw response
│   │   - Formats for MCP
│   │   - Returns formatted response
│   │
│   └── validator.py (~50 lines)
│       SINGLE RESPONSIBILITY: Validate responses
│       - Checks response structure
│       - Validates content
│       - Returns validation result
│
└── mixins/ (existing - already modular!)
    ├── continuation_mixin.py
    ├── streaming_mixin.py
    ├── tool_call_mixin.py
    └── web_search_mixin.py
```

**Benefits:**
- ✅ Want to change prompt building? → Edit `prompt/builder.py` (50 lines)
- ✅ Want to change model calling? → Edit `model/caller.py` (50 lines)
- ✅ Want to change formatting? → Edit `response/formatter.py` (50 lines)
- ✅ Each file has ONE clear purpose!
- ✅ Easy to find, easy to test, easy to modify!

---

## EXAMPLE: ORGANIZING utils/

### Current (Chaos)

```
utils/
├── file_utils.py
├── file_utils_expansion.py
├── file_utils_helpers.py
├── file_utils_json.py
├── file_utils_reading.py
├── file_utils_security.py
├── file_utils_tokens.py
├── conversation_history.py
├── conversation_memory.py
├── conversation_models.py
├── conversation_threads.py
# 37 files, no folders!
```

**Problem:** Flat structure, unclear organization!

---

### After Refactoring (Organized)

```
utils/
├── file/
│   ├── reader.py
│   │   SINGLE RESPONSIBILITY: Read files
│   │   - Opens files
│   │   - Reads content
│   │   - Returns file data
│   │
│   ├── writer.py
│   │   SINGLE RESPONSIBILITY: Write files
│   │   - Takes file data
│   │   - Writes to disk
│   │   - Returns success/failure
│   │
│   ├── validator.py
│   │   SINGLE RESPONSIBILITY: Validate files
│   │   - Checks file exists
│   │   - Validates format
│   │   - Returns validation result
│   │
│   ├── security.py
│   │   SINGLE RESPONSIBILITY: Security checks
│   │   - Checks file permissions
│   │   - Validates paths
│   │   - Returns security status
│   │
│   └── tokens.py
│       SINGLE RESPONSIBILITY: Count tokens
│       - Takes file content
│       - Counts tokens
│       - Returns token count
│
├── conversation/
│   ├── history.py
│   │   SINGLE RESPONSIBILITY: Manage conversation history
│   │
│   ├── memory.py
│   │   SINGLE RESPONSIBILITY: Manage conversation memory
│   │
│   ├── threads.py
│   │   SINGLE RESPONSIBILITY: Manage conversation threads
│   │
│   └── models.py
│       SINGLE RESPONSIBILITY: Conversation data models
│
├── model/
│   ├── context.py
│   │   SINGLE RESPONSIBILITY: Manage model context
│   │
│   └── restrictions.py
│       SINGLE RESPONSIBILITY: Check model restrictions
│
└── [core utils]
    ├── progress.py (SINGLE RESPONSIBILITY: Progress tracking)
    ├── observability.py (SINGLE RESPONSIBILITY: Logging/observability)
    ├── cache.py (SINGLE RESPONSIBILITY: Caching)
    └── ...
```

**Benefits:**
- ✅ Want to change file reading? → `utils/file/reader.py`
- ✅ Want to change security checks? → `utils/file/security.py`
- ✅ Want to change conversation history? → `utils/conversation/history.py`
- ✅ Clear organization by responsibility!

---

## DESIGN INTENT DOCUMENTATION

**For each module, document:**

```python
# tools/simple/prompt/builder.py
"""
SINGLE RESPONSIBILITY: Build prompts for simple tools

DESIGN INTENT:
- Takes request data
- Constructs prompt string
- Adds system prompt
- Adds user context
- Returns complete prompt

DOES NOT:
- Call models (that's model/caller.py)
- Format responses (that's response/formatter.py)
- Handle files (that's inherited from BaseTool)

DEPENDENCIES:
- systemprompts/ (for system prompts)
- utils/client_info (for client context)

USED BY:
- tools/simple/base.py (SimpleTool.execute)

EXAMPLE USAGE:
    builder = PromptBuilder()
    prompt = builder.build(request)
    # Returns: "You are a helpful assistant...\n\nUser: {request.prompt}"
"""
```

---

## PHASE 1: MODULAR REFACTORING PLAN

### 1.1: Document Design Intent (1-2 weeks)
- For each large file, document:
  - What is its SINGLE responsibility?
  - What responsibilities does it currently have that don't belong?
  - Where should those responsibilities go?
- Create design intent documents
- Get user approval on the plan

### 1.2: Refactor SimpleTool (2-3 weeks)
- Split into focused modules (prompt/, model/, response/)
- Each module has ONE clear purpose
- Update tests
- Verify all 4 simple tools still work

### 1.3: Refactor WorkflowTool (2-3 weeks)
- Split ExpertAnalysisMixin into focused modules
- Split OrchestrationMixin into focused modules
- Each module has ONE clear purpose
- Update tests
- Verify all 12 workflow tools still work

### 1.4: Refactor utils/ (1-2 weeks)
- Organize into folders by responsibility
- Each file has ONE clear purpose
- Update imports
- Verify all tools still work

### 1.5: Consolidate Duplicates (1-2 weeks)
- Based on Task 0.4 findings
- Merge duplicates following single responsibility
- Update imports
- Verify system still works

**Total time:** 7-12 weeks

---

## BENEFITS

### 1. Long-Term Stability ✅
- Each module has ONE clear purpose
- Changes are isolated
- Easy to test
- Easy to maintain

### 2. Easy to Find Things ✅
- Want to change prompts? → `tools/simple/prompt/`
- Want to change model calling? → `tools/simple/model/`
- Want to change file reading? → `utils/file/reader.py`
- **No more digging through 1220 lines!**

### 3. Easy to Extend ✅
- Want to add new prompt type? → Add to `prompt/`
- Want to add new model provider? → Add to `model/`
- Want to add new file format? → Add to `file/`
- **Clear where new code goes!**

### 4. Easy to Test ✅
- Each module is small and focused
- Easy to write unit tests
- Easy to mock dependencies
- **Better test coverage!**

### 5. Follows Best Practices ✅
- Single Responsibility Principle
- Separation of Concerns
- Modular Design
- **Industry-standard architecture!**

---

## USER APPROVAL

**User confirmed:**
1. ✅ This aligns with their vision
2. ✅ Comfortable with 7-12 week timeline
3. ✅ Wants uniformed clean approach
4. ✅ Typical developer approach with clean arrangement

**Next steps:**
1. Complete Phase 0 (Tasks 0.4-0.6)
2. Create detailed design intent documents
3. Execute Phase 1: Modular Refactoring

---

**STATUS:** ✅ APPROVED - Ready to proceed with Phase 0 completion

