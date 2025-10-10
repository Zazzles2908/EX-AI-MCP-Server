# DESIGN INTENT TEMPLATE
**Date:** 2025-10-10  
**Purpose:** Template for documenting design intent before refactoring

---

## HOW TO USE THIS TEMPLATE

For each large file (>10KB), create a design intent document using this template.

**Steps:**
1. Copy this template
2. Fill in all sections
3. Review with user if needed
4. Use as guide for refactoring

---

## FILE INFORMATION

**File Path:** `[path/to/file.py]`
**Current Size:** `[XX.XKB]`
**Lines of Code:** `[XXXX lines]`
**Used By:** `[X tools/modules]`
**Impact Radius:** `[LOW/MEDIUM/HIGH/CRITICAL]`

---

## ⚠️ CRITICAL: DEPENDENCY ANALYSIS FIRST!

**BEFORE analyzing the file's internal structure, MUST analyze:**

### 1. UPSTREAM: What Calls This File?

**Direct Callers/Subclasses:**
- [List all classes that inherit from this class]
- [List all modules that import from this file]
- [List all functions that call methods from this file]

**What They Use:**
- [List specific methods/functions they call]
- [List specific attributes they access]
- [List specific constants they reference]

**Example:**
```
ChatTool (tools/chat.py)
├── Inherits from: SimpleTool
├── Calls: prepare_chat_style_prompt(request)
├── Calls: build_standard_prompt(...)
└── Overrides: prepare_prompt(), format_response()
```

### 2. DOWNSTREAM: What Does This File Call?

**Parent Classes:**
- [List all classes this inherits from]
- [List methods inherited from each parent]

**Imports:**
- [List all external modules imported]
- [List specific functions/classes used from each import]

**Example:**
```
SimpleTool inherits from:
├── WebSearchMixin (provides web search methods)
├── ToolCallMixin (provides tool calling methods)
├── StreamingMixin (provides streaming methods)
├── ContinuationMixin (provides conversation continuation)
└── BaseTool (provides core tool functionality)

SimpleTool imports:
├── tools.shared.base_models.ToolRequest
├── tools.shared.schema_builders.SchemaBuilder
├── utils.client_info (get_current_session_fingerprint, etc.)
└── utils.progress (send_progress)
```

### 3. PUBLIC INTERFACE: What CANNOT Change?

**Methods Called by External Code:**
- [List all public methods that external code calls]
- [Mark which are CRITICAL to preserve]

**Class Constants:**
- [List all class-level constants]
- [Mark which are referenced externally]

**Inheritance Chain:**
- [Document the exact inheritance chain]
- [Mark if this CANNOT change]

**Example:**
```
CANNOT CHANGE:
❌ prepare_chat_style_prompt(request, system_prompt=None) - Called by ChatTool
❌ build_standard_prompt(...) - Called by multiple tools
❌ get_request_*() methods (13 methods) - Called by all subclasses
❌ FILES_FIELD constant - Referenced by subclasses
❌ Inheritance: SimpleTool(WebSearchMixin, ToolCallMixin, ..., BaseTool)

CAN CHANGE:
✅ Internal implementation of methods
✅ Private methods (starting with _)
✅ Internal helper functions
```

### 4. INTEGRATION POINTS: How Does This Fit in the System?

**Architecture Layer:**
- [Which layer is this in? Foundation/Core/Framework/Implementation]
- [What depends on this layer?]
- [What does this layer depend on?]

**Data Flow:**
- [How does data flow through this file?]
- [What comes in? What goes out?]

**Example:**
```
SimpleTool is in: Framework Layer (Tier 3)
├── Above: 4 tool implementations (ActivityTool, ChatTool, etc.)
├── Below: BaseTool (Tier 2), Mixins (Tier 2), Utils (Tier 1)
└── Data Flow: Request → Prompt Prep → Model Call → Response Format → Output
```

---

## CURRENT STATE ANALYSIS

### What Does This File Currently Do?

**List ALL responsibilities (be exhaustive):**
1. [Responsibility 1]
2. [Responsibility 2]
3. [Responsibility 3]
4. ...

**Current Structure:**
```
[Describe current class/function structure]
- Class/Function 1: [purpose]
- Class/Function 2: [purpose]
- ...
```

**Dependencies:**
- Imports from: [list modules]
- Used by: [list tools/modules]

---

## SINGLE RESPONSIBILITY ANALYSIS

### What SHOULD This File Do? (Single Responsibility)

**Primary Responsibility:**
> [One clear sentence describing the SINGLE responsibility]

**Example:**
> "Orchestrate the execution of simple tools by coordinating prompt building, model calling, and response formatting."

---

### What Doesn't Belong Here? (Misplaced Responsibilities)

**Responsibilities that should be elsewhere:**
1. [Misplaced responsibility 1] → Should be in: `[target module]`
2. [Misplaced responsibility 2] → Should be in: `[target module]`
3. ...

**Why these don't belong:**
- [Explanation of why each responsibility is misplaced]

---

## REFACTORING APPROACH: FACADE PATTERN

**CRITICAL:** This is NOT building a new system - this is REFACTORING the existing system!

**Approach:** Use the **Facade Pattern**
- Keep ALL public methods in the original file (same signatures)
- Delegate to internal modules for implementation
- Maintain 100% backward compatibility
- External code sees NO changes

**Why Facade Pattern?**
- ✅ Public interface unchanged (subclasses/callers work without modification)
- ✅ Internal code is modular (easy to maintain)
- ✅ Easy to test modules independently
- ✅ Zero breaking changes
- ✅ Incremental refactoring (can do one module at a time)

**Example:**
```python
# BEFORE (monolithic):
class SimpleTool:
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # 50 lines of implementation here
        client_info = get_cached_client_info()
        # ... more code ...
        return full_prompt

# AFTER (facade):
class SimpleTool:
    def build_standard_prompt(self, system_prompt, user_content, request, file_context_title="CONTEXT FILES"):
        # Delegate to module (same signature, different implementation)
        from tools.simple.prompt.builder import PromptBuilder
        return PromptBuilder.build_standard(system_prompt, user_content, request, file_context_title)
```

**External code (ChatTool) sees NO difference:**
```python
# ChatTool code - UNCHANGED!
def prepare_prompt(self, request):
    base_prompt = self.build_standard_prompt(...)  # ✅ Still works!
```

---

## PROPOSED REFACTORING

### Target State: Modular Structure

**Proposed folder structure:**
```
[parent_folder]/
├── [main_file].py (~100-200 lines)
│   SINGLE RESPONSIBILITY: [description]
│   - [What it does]
│   - [What it orchestrates]
│
├── [module_1]/
│   ├── __init__.py
│   ├── [file_1].py (~50-150 lines)
│   │   SINGLE RESPONSIBILITY: [description]
│   │
│   └── [file_2].py (~50-150 lines)
│       SINGLE RESPONSIBILITY: [description]
│
├── [module_2]/
│   ├── __init__.py
│   └── [file_3].py (~50-150 lines)
│       SINGLE RESPONSIBILITY: [description]
│
└── ...
```

---

### Module Breakdown

**Module 1: [Name]**
- **Purpose:** [Single responsibility]
- **Files:**
  - `[file_1].py` - [Specific responsibility]
  - `[file_2].py` - [Specific responsibility]
- **Size estimate:** [XX lines total]
- **Dependencies:** [What it imports]
- **Used by:** [What uses it]

**Module 2: [Name]**
- **Purpose:** [Single responsibility]
- **Files:**
  - `[file_3].py` - [Specific responsibility]
- **Size estimate:** [XX lines total]
- **Dependencies:** [What it imports]
- **Used by:** [What uses it]

[Repeat for each module...]

---

### Design Intent Documentation (Per Module)

**For each module, document:**

```python
# [module]/[file].py
"""
SINGLE RESPONSIBILITY: [One clear sentence]

DESIGN INTENT:
- [What this module does]
- [How it does it]
- [What it returns]

DOES NOT:
- [What this module explicitly does NOT do]
- [Responsibilities that belong elsewhere]

DEPENDENCIES:
- [Module 1] (for [purpose])
- [Module 2] (for [purpose])

USED BY:
- [Tool/Module 1]
- [Tool/Module 2]

EXAMPLE USAGE:
    [code example showing how to use this module]
"""
```

---

## MIGRATION STRATEGY

### Step-by-Step Refactoring Plan

**Step 1: Create Module Structure**
- [ ] Create folders: `[list folders]`
- [ ] Create `__init__.py` files
- [ ] Estimated time: [X hours/days]

**Step 2: Extract Module 1**
- [ ] Create `[module_1]/[file_1].py`
- [ ] Move [specific code] from main file
- [ ] Update imports in main file
- [ ] Test: [specific tests]
- [ ] Estimated time: [X hours/days]

**Step 3: Extract Module 2**
- [ ] Create `[module_2]/[file_2].py`
- [ ] Move [specific code] from main file
- [ ] Update imports in main file
- [ ] Test: [specific tests]
- [ ] Estimated time: [X hours/days]

[Repeat for each module...]

**Step N: Final Integration**
- [ ] Update main file to orchestrate modules
- [ ] Verify main file is ~100-200 lines
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Estimated time: [X hours/days]

---

## IMPACT ASSESSMENT

### Breaking Changes

**Import Path Changes:**
- Old: `from [old_path] import [class]`
- New: `from [new_path] import [class]`

**Affected Files:**
- [List all files that import from this module]
- Estimated files to update: [X files]

**Risk Level:** [LOW/MEDIUM/HIGH]

---

### Testing Strategy

**Unit Tests:**
- [ ] Test module 1: [specific tests]
- [ ] Test module 2: [specific tests]
- [ ] Test main orchestration: [specific tests]

**Integration Tests:**
- [ ] Test tool 1: [specific tests]
- [ ] Test tool 2: [specific tests]
- [ ] Test all affected tools: [X tools]

**Manual Testing:**
- [ ] [Specific manual test 1]
- [ ] [Specific manual test 2]

---

## EFFORT ESTIMATE

**Total Effort:** [X-Y days/weeks]

**Breakdown:**
- Module structure creation: [X hours]
- Module 1 extraction: [X hours]
- Module 2 extraction: [X hours]
- [...]
- Import updates: [X hours]
- Testing: [X hours]
- Documentation: [X hours]

**Risk Factors:**
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

---

## SUCCESS CRITERIA

**Refactoring Complete When:**
- [ ] Main file is ~100-200 lines (orchestration only)
- [ ] Each module is <200 lines
- [ ] Each module has ONE clear responsibility
- [ ] All imports updated
- [ ] All tests passing
- [ ] Documentation updated
- [ ] No regressions

---

## ROLLBACK PLAN

**If refactoring fails:**
1. Revert to commit: `[commit hash before refactoring]`
2. Document what went wrong
3. Adjust strategy
4. Try again with lessons learned

**Rollback triggers:**
- Tests fail and can't be fixed within [X hours]
- Performance degradation >10%
- Breaking changes affect >X files
- User requests rollback

---

## NOTES

**Additional considerations:**
- [Any special notes]
- [Edge cases to consider]
- [Dependencies on other refactoring]

**Questions for user:**
- [Question 1]
- [Question 2]

---

**STATUS:** [DRAFT / IN REVIEW / APPROVED / IN PROGRESS / COMPLETE]

