# ARCHAEOLOGICAL DIG - Phase 3 MASTER CHECKLIST
**Branch:** archaeological-dig/phase1-discovery-and-cleanup
**Started:** TBD (After Phase 2 & 3 complete)
**Purpose:** Plan SimpleTool refactoring using Facade Pattern for modular architecture

---

## 🎯 Phase 3 GOAL

**Refactor SimpleTool (55.3KB monolithic file) into modular architecture:**
- Split into 5 conceptual modules using Top-Down Design
- Maintain 100% backward compatibility (25 public methods CANNOT CHANGE)
- Use Facade Pattern (base.py delegates to modules)
- Ensure all 3 SimpleTool subclasses continue working
- Reduce base.py from 1,220 lines to ~150-200 lines
- Each module: 150-250 lines with single responsibility

**WHY THIS IS CRITICAL:**
- SimpleTool is used by 3 tools (ChatTool, ChallengeTool, ActivityTool)
- 25 public methods form critical interface that CANNOT break
- Current 55.3KB file is hard to maintain and extend
- Modular design enables easier testing and future enhancements
- Foundation for long-term system stability

---

## ✅ PREREQUISITES (MUST BE COMPLETE)

**Phase 0: Architectural Mapping** ✅ COMPLETE
- [x] Complete system inventory (433 Python files)
- [x] Shared infrastructure identification
- [x] Dependency mapping
- [x] Architecture pattern recognition
- [x] Modular refactoring strategy created

**Phase 1: Discovery & Classification** ✅ COMPLETE
- [x] All components classified (ACTIVE/ORPHANED/PLANNED)
- [x] Orphaned directories deleted
- [x] Utils folder reorganized
- [x] All changes committed and pushed

**Phase 2: Map Connections** ⏳ TO BE COMPLETED
- [ ] All 10 Phase 2 tasks to be completed
- [ ] SimpleTool connections to be mapped (CRITICAL)
- [ ] Public methods to be identified and validated
- [ ] SimpleTool subclasses to be verified
- [ ] Facade pattern strategy to be validated
- [ ] Expert validation to be performed

**Phase 3: Execute Phase 2 Findings** ⏳ TO BE COMPLETED
- [ ] Execute Phase 2 cleanup tasks
- [ ] Optimize identified bottlenecks
- [ ] Fix connection issues
- [ ] Prepare for SimpleTool refactoring

---

## 🔒 CRITICAL CONSTRAINTS (CANNOT CHANGE)

### SimpleTool Public Interface (25 Methods - VALIDATED)

**Abstract Methods (2):**
1. get_tool_fields() → dict[str, dict[str, Any]]
2. get_required_fields() → list[str]

**Hook Methods (3):**
3. get_annotations() → Optional[dict[str, Any]]
4. format_response(response, request, model_info) → str
5. get_request_model() → Type[ToolRequest]

**Schema & Validation (3):**
6. get_input_schema() → dict[str, Any]
7. supports_custom_request_model() → bool
8. get_prompt_content_for_size_validation() → str

**Request Accessors (13):**
9. get_request_model_name(request) → str
10. get_request_images(request) → list[str]
11. get_request_continuation_id(request) → Optional[str]
12. get_request_prompt(request) → str
13. get_request_temperature(request) → Optional[float]
14. get_validated_temperature(request, model_context) → tuple[float, list[str]]
15. get_request_thinking_mode(request) → Optional[str]
16. get_request_files(request) → list[str]
17. get_request_use_websearch(request) → bool
18. get_request_as_dict(request) → dict
19. set_request_files(request, files) → None
20. get_actually_processed_files() → list
21. get_request_stream(request) → Optional[bool]

**Prompt Building (3):**
22. build_standard_prompt(system_prompt, user_content, request, file_context_title) → str
23. handle_prompt_file_with_fallback(request) → str
24. prepare_chat_style_prompt(request, system_prompt) → str

**Execution (1):**
25. execute(arguments) → list

### Inheritance Chain (CANNOT CHANGE)
```
SimpleTool(WebSearchMixin, ToolCallMixin, StreamingMixin, ContinuationMixin, BaseTool)
└── BaseTool(BaseToolCore, FileHandlingMixin, ModelManagementMixin, ResponseFormattingMixin)
```

### Subclasses (3 Tools - MUST CONTINUE WORKING)
1. ChatTool (tools/chat.py)
2. ChallengeTool (tools/challenge.py)
3. ActivityTool (tools/activity.py)

---

## 📋 Phase 3 REFACTORING TASKS

### Task 3.0: Setup & Planning (1 day)

**Goal:** Establish Phase 3 workspace and review all documentation

**Tasks:**
- [ ] Create Phase 3 master checklist (this document)
- [ ] Review Phase 2 comprehensive summary
- [ ] Review SimpleTool connection map
- [ ] Review validation corrections
- [ ] Understand all 25 public methods
- [ ] Understand facade pattern strategy
- [ ] Create Phase 3 working branch
- [ ] Set up task tracking

**Deliverable:**
- [ ] Phase 3 master checklist created
- [ ] All Phase 2 documentation reviewed
- [ ] Working branch created
- [ ] Ready to begin refactoring

**Time Estimate:** 1 day

---

### Task 3.1: Pre-Refactoring Validation (2-3 days)

**Goal:** Create comprehensive integration tests BEFORE refactoring

**Tasks:**
- [ ] Create tests/integration/simpletool/ directory
- [ ] Create baseline tests for ChatTool
  - [ ] Test all 25 public methods
  - [ ] Test chat-specific functionality
  - [ ] Test conversation continuation
  - [ ] Test file handling
- [ ] Create baseline tests for ChallengeTool
  - [ ] Test all 25 public methods
  - [ ] Test challenge-specific functionality
- [ ] Create baseline tests for ActivityTool
  - [ ] Test all 25 public methods
  - [ ] Test activity-specific functionality
- [ ] Run all tests and document baseline behavior
- [ ] Commit baseline tests

**Deliverable:**
- [ ] Comprehensive integration test suite
- [ ] All tests passing (baseline)
- [ ] Test documentation
- [ ] Tests committed to git

**Time Estimate:** 2-3 days

---

### Task 3.2: Extract Definition Module (2-3 days)

**Goal:** Extract schema generation logic into definition/ module

**Tasks:**
- [ ] Create tools/simple/definition/ directory
- [ ] Create tools/simple/definition/__init__.py
- [ ] Create tools/simple/definition/schema.py
- [ ] Extract schema generation methods:
  - [ ] get_input_schema()
  - [ ] get_tool_fields() (abstract)
  - [ ] get_required_fields() (abstract)
  - [ ] get_annotations()
  - [ ] get_model_field_schema()
- [ ] Update SimpleTool base.py to delegate to definition module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/definition/schema.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to definition module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.3: Extract Intake Module (3-4 days)

**Goal:** Extract request accessor and validation logic into intake/ module

**Tasks:**
- [ ] Create tools/simple/intake/ directory
- [ ] Create tools/simple/intake/__init__.py
- [ ] Create tools/simple/intake/accessor.py
- [ ] Extract 13 request accessor methods
- [ ] Create tools/simple/intake/validator.py
- [ ] Extract validation logic (temperature, files, etc.)
- [ ] Update SimpleTool base.py to delegate to intake module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/intake/accessor.py (~200-250 lines)
- [ ] tools/simple/intake/validator.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to intake module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 3-4 days

---

### Task 3.4: Extract Preparation Module (3-4 days)

**Goal:** Extract prompt building logic into preparation/ module

**Tasks:**
- [ ] Create tools/simple/preparation/ directory
- [ ] Create tools/simple/preparation/__init__.py
- [ ] Create tools/simple/preparation/prompt.py
- [ ] Extract prompt building methods:
  - [ ] build_standard_prompt()
  - [ ] prepare_chat_style_prompt()
- [ ] Create tools/simple/preparation/files.py
- [ ] Extract prompt file handling:
  - [ ] handle_prompt_file_with_fallback()
- [ ] Update SimpleTool base.py to delegate to preparation module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/preparation/prompt.py (~200-250 lines)
- [ ] tools/simple/preparation/files.py (~80-100 lines)
- [ ] SimpleTool base.py delegates to preparation module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 3-4 days

---

### Task 3.5: Extract Execution Module (2-3 days)

**Goal:** Extract model calling logic into execution/ module

**Tasks:**
- [ ] Create tools/simple/execution/ directory
- [ ] Create tools/simple/execution/__init__.py
- [ ] Create tools/simple/execution/caller.py
- [ ] Extract execution logic:
  - [ ] execute() method
  - [ ] Model invocation logic
  - [ ] Error handling
- [ ] Update SimpleTool base.py to delegate to execution module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/execution/caller.py (~200-250 lines)
- [ ] SimpleTool base.py delegates to execution module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.6: Extract Response Module (2-3 days)

**Goal:** Extract response formatting logic into response/ module

**Tasks:**
- [ ] Create tools/simple/response/ directory
- [ ] Create tools/simple/response/__init__.py
- [ ] Create tools/simple/response/formatter.py
- [ ] Extract response formatting methods:
  - [ ] format_response()
  - [ ] get_actually_processed_files()
  - [ ] Response parsing logic
- [ ] Update SimpleTool base.py to delegate to response module
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] tools/simple/response/formatter.py (~150-200 lines)
- [ ] SimpleTool base.py delegates to response module
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.7: Finalize Facade Pattern (2-3 days)

**Goal:** Ensure SimpleTool base.py is clean facade maintaining all public methods

**Tasks:**
- [ ] Review SimpleTool base.py
- [ ] Verify all 25 public methods present with exact signatures
- [ ] Verify all methods delegate to appropriate modules
- [ ] Verify inheritance chain unchanged
- [ ] Verify class constants preserved (FILES_FIELD, IMAGES_FIELD)
- [ ] Target: base.py ~150-200 lines (down from 1,220)
- [ ] Add comprehensive docstrings
- [ ] Run integration tests (must pass)
- [ ] Commit changes

**Deliverable:**
- [ ] SimpleTool base.py is clean facade (~150-200 lines)
- [ ] All 25 public methods preserved
- [ ] 100% backward compatibility verified
- [ ] All integration tests passing
- [ ] Changes committed

**Time Estimate:** 2-3 days

---

### Task 3.8: Integration Testing & Validation (2-3 days)

**Goal:** Comprehensive testing to verify no breaking changes

**Tasks:**
- [ ] Run full integration test suite
- [ ] Test ChatTool thoroughly
  - [ ] All 25 public methods
  - [ ] Chat-specific features
  - [ ] Conversation continuation
  - [ ] File handling
  - [ ] Web search integration
- [ ] Test ChallengeTool thoroughly
  - [ ] All 25 public methods
  - [ ] Challenge-specific features
- [ ] Test ActivityTool thoroughly
  - [ ] All 25 public methods
  - [ ] Activity-specific features
- [ ] Performance testing
  - [ ] Compare before/after performance
  - [ ] Ensure no regressions
- [ ] Manual testing of all tools
- [ ] Document any issues found
- [ ] Fix any issues
- [ ] Re-run tests until all pass

**Deliverable:**
- [ ] All integration tests passing
- [ ] Performance metrics documented
- [ ] No breaking changes confirmed
- [ ] All 3 SimpleTool subclasses working correctly
- [ ] Test results documented

**Time Estimate:** 2-3 days

---

### Task 3.9: Documentation & Cleanup (2-3 days)

**Goal:** Update all documentation and clean up

**Tasks:**
- [ ] Create design intent documents for each module:
  - [ ] tools/simple/definition/DESIGN_INTENT.md
  - [ ] tools/simple/intake/DESIGN_INTENT.md
  - [ ] tools/simple/preparation/DESIGN_INTENT.md
  - [ ] tools/simple/execution/DESIGN_INTENT.md
  - [ ] tools/simple/response/DESIGN_INTENT.md
- [ ] Update SimpleTool base.py docstring
- [ ] Update architecture documentation
- [ ] Create visual diagrams (Mermaid)
  - [ ] New SimpleTool module structure
  - [ ] Facade pattern implementation
  - [ ] Module dependencies
- [ ] Update SIMPLETOOL_CONNECTION_MAP.md
- [ ] Clean up any temporary files
- [ ] Update README files
- [ ] Commit documentation

**Deliverable:**
- [ ] Design intent documents for all 5 modules
- [ ] Updated architecture documentation
- [ ] Visual diagrams created
- [ ] All documentation committed

**Time Estimate:** 2-3 days

---

### Task 3.10: Expert Validation & Summary (1-2 days)

**Goal:** Get expert validation and create comprehensive summary

**Tasks:**
- [ ] Use EXAI codereview tool to validate refactoring
- [ ] Use EXAI analyze tool for architectural assessment
- [ ] Address any issues found by expert analysis
- [ ] Create PHASE3_COMPREHENSIVE_SUMMARY.md
  - [ ] Document refactoring approach
  - [ ] Document module structure
  - [ ] Document lessons learned
  - [ ] Include metrics (before/after)
  - [ ] Include visual diagrams
- [ ] Get user approval
- [ ] Prepare for merge to main

**Deliverable:**
- [ ] Expert validation complete
- [ ] PHASE3_COMPREHENSIVE_SUMMARY.md created
- [ ] User approval obtained
- [ ] Ready for merge

**Time Estimate:** 1-2 days

---

## 📊 PROGRESS TRACKER

### Overall Progress
- Setup: 0/1 (0%) ⏳
- Refactoring: 0/9 (0%) ⏳
- **Total: 0/10 (0%)**

### Current Status
- ⏳ Task 3.0: Setup & Planning - NOT STARTED
- ⏳ Task 3.1: Pre-Refactoring Validation - NOT STARTED
- ⏳ Task 3.2: Extract Definition Module - NOT STARTED
- ⏳ Task 3.3: Extract Intake Module - NOT STARTED
- ⏳ Task 3.4: Extract Preparation Module - NOT STARTED
- ⏳ Task 3.5: Extract Execution Module - NOT STARTED
- ⏳ Task 3.6: Extract Response Module - NOT STARTED
- ⏳ Task 3.7: Finalize Facade Pattern - NOT STARTED
- ⏳ Task 3.8: Integration Testing - NOT STARTED
- ⏳ Task 3.9: Documentation & Cleanup - NOT STARTED
- ⏳ Task 3.10: Expert Validation - NOT STARTED

### Time Estimates
- Task 3.0: ~1 day
- Task 3.1: ~2-3 days
- Task 3.2: ~2-3 days
- Task 3.3: ~3-4 days
- Task 3.4: ~3-4 days
- Task 3.5: ~2-3 days
- Task 3.6: ~2-3 days
- Task 3.7: ~2-3 days
- Task 3.8: ~2-3 days
- Task 3.9: ~2-3 days
- Task 3.10: ~1-2 days
- **Total: ~23-32 days (4-6 weeks)**

---

## 🎯 SUCCESS CRITERIA

### Phase 3 Complete When:
- [ ] SimpleTool base.py reduced from 1,220 lines to ~150-200 lines
- [ ] 5 conceptual modules created (definition, intake, preparation, execution, response)
- [ ] All 25 public methods preserved with exact signatures
- [ ] All 3 SimpleTool subclasses working correctly
- [ ] 100% backward compatibility verified
- [ ] All integration tests passing
- [ ] No performance regressions
- [ ] Comprehensive documentation created
- [ ] Expert validation complete
- [ ] User approval obtained

### Ready for Merge When:
- [ ] All tasks complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Expert validation positive
- [ ] User approves changes
- [ ] No breaking changes confirmed

---

## 🎨 TARGET ARCHITECTURE

### Current State (Monolithic)
```
tools/simple/
├── base.py (55.3KB, 1,220 lines - DOES EVERYTHING!)
└── mixins/ (already modular)
```

### Target State (Modular - Top-Down Design)
```
tools/simple/
├── base.py (FACADE - ~150-200 lines)
│   class SimpleTool:
│       """Facade that delegates to conceptual modules"""
│       # All 25 public methods preserved
│       # Each method delegates to appropriate module
│
├── definition/          ← "What does this tool promise?"
│   ├── __init__.py
│   └── schema.py (~150-200 lines)
│       - get_input_schema()
│       - get_tool_fields()
│       - get_required_fields()
│       - get_annotations()
│
├── intake/              ← "What did the user ask for?"
│   ├── __init__.py
│   ├── accessor.py (~200-250 lines)
│   │   - 13 request accessor methods
│   └── validator.py (~150-200 lines)
│       - get_validated_temperature()
│       - Validation logic
│
├── preparation/         ← "How do we ask the AI?"
│   ├── __init__.py
│   ├── prompt.py (~200-250 lines)
│   │   - build_standard_prompt()
│   │   - prepare_chat_style_prompt()
│   └── files.py (~80-100 lines)
│       - handle_prompt_file_with_fallback()
│
├── execution/           ← "How do we call the AI?"
│   ├── __init__.py
│   └── caller.py (~200-250 lines)
│       - execute()
│       - Model invocation
│
├── response/            ← "How do we deliver the result?"
│   ├── __init__.py
│   └── formatter.py (~150-200 lines)
│       - format_response()
│       - get_actually_processed_files()
│
└── mixins/ (existing - keep as-is)
    ├── continuation_mixin.py
    ├── streaming_mixin.py
    ├── tool_call_mixin.py
    └── web_search_mixin.py
```

---

## 📝 NOTES

- Use Facade Pattern: base.py keeps all public methods, delegates to modules
- Incremental approach: Extract one module at a time
- Test after EACH module extraction
- Commit frequently (after each successful module extraction)
- 100% backward compatibility is NON-NEGOTIABLE
- All 25 public methods must maintain exact signatures
- Integration tests are CRITICAL - create before refactoring
- Follow Top-Down Design principles (conceptual categories)
- Each module has single responsibility
- Target: 150-250 lines per module

---

## 🚨 RISK MITIGATION

### Risk 1: Breaking Changes
**Mitigation:**
- Create comprehensive integration tests BEFORE refactoring
- Test after each module extraction
- Maintain exact method signatures
- Use facade pattern to preserve public interface

### Risk 2: Import Complexity
**Mitigation:**
- Use lazy imports in facade methods
- Clear module boundaries
- Document import patterns

### Risk 3: Performance Regression
**Mitigation:**
- Benchmark before refactoring
- Test performance after each module
- Optimize if needed

### Risk 4: Scope Creep
**Mitigation:**
- Stick to the plan
- No new features during refactoring
- Focus on structure, not functionality

---

**STATUS: READY TO BEGIN**

Next: Task 3.0 - Setup & Planning

