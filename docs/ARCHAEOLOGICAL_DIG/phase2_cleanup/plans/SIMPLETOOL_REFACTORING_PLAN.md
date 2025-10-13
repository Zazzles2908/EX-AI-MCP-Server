# SIMPLETOOL REFACTORING PLAN
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Status:** IN PROGRESS - Baseline Tests Complete ✅  
**Goal:** Refactor SimpleTool from 1,220-line monolith to modular architecture using Facade Pattern

---

## 🎯 OBJECTIVES

1. **Reduce Complexity:** Break 1,220-line SimpleTool into 5 focused modules
2. **Improve Maintainability:** Single Responsibility Principle for each module
3. **Maintain Compatibility:** 100% backward compatibility - all 25 public methods unchanged
4. **Enable Testing:** Easier unit testing of individual modules
5. **Facilitate Future Changes:** Cleaner architecture for future enhancements

---

## ✅ COMPLETED WORK

### Baseline Tests Created (32 passing, 1 skipped)
**File:** `tests/integration/test_simpletool_baseline.py`

**Coverage:**
- ✅ All 3 SimpleTool subclasses (ChatTool, ChallengeTool, ActivityTool)
- ✅ Tool instantiation
- ✅ Abstract methods (get_tool_fields, get_required_fields)
- ✅ Hook methods (get_annotations, format_response, get_request_model, supports_custom_request_model)
- ✅ Schema & validation (get_input_schema, get_model_field_schema, get_prompt_content_for_size_validation)
- ✅ Request accessors (13 methods: get_request_model_name, get_request_images, etc.)
- ✅ Prompt building (build_standard_prompt, handle_prompt_file_with_fallback, prepare_chat_style_prompt)
- ✅ Execution (execute)
- ⏭️ Skipped: get_validated_temperature (requires complex model_context setup)

**Test Results:**
```
32 passed, 1 skipped in 0.41s
```

---

## 📋 REFACTORING STRATEGY

### Facade Pattern Architecture

**SimpleTool (base.py)** becomes a thin facade (~150-200 lines):
- Maintains all 25 public methods with exact signatures
- Delegates to internal modules
- Provides backward compatibility layer
- Coordinates between modules

**5 Internal Modules:**

1. **tools/simple/definition/** - Tool Contract & Schema
   - `schema.py` - Schema generation (SchemaBuilder integration)
   - Handles: get_input_schema(), get_model_field_schema()

2. **tools/simple/intake/** - Request Processing
   - `accessor.py` - Request field accessors (13 methods)
   - `validator.py` - Request validation
   - Handles: get_request_*() methods, set_request_files()

3. **tools/simple/preparation/** - Prompt Building
   - `prompt.py` - Prompt construction
   - `files.py` - File handling and context
   - Handles: build_standard_prompt(), handle_prompt_file_with_fallback(), prepare_chat_style_prompt()

4. **tools/simple/execution/** - Model Calling
   - `caller.py` - AI model execution
   - Handles: execute(), model calling logic

5. **tools/simple/response/** - Response Formatting
   - `formatter.py` - Response formatting and post-processing
   - Handles: format_response()

---

## 🔒 CONSTRAINTS (CANNOT CHANGE)

### 25 Public Methods - Exact Signatures Required

**Abstract Methods (2):**
1. `get_tool_fields() -> dict[str, dict[str, Any]]`
2. `get_required_fields() -> list[str]`

**Hook Methods (4):**
3. `get_annotations() -> dict`
4. `format_response(response: str, request, model_info: Optional[dict] = None) -> str`
5. `get_request_model()`
6. `supports_custom_request_model() -> bool`

**Schema & Validation (3):**
7. `get_input_schema() -> dict`
8. `get_model_field_schema() -> dict`
9. `get_prompt_content_for_size_validation(user_content: str) -> str`

**Request Accessors (13):**
10. `get_request_model_name(request) -> Optional[str]`
11. `get_request_images(request) -> list`
12. `get_request_continuation_id(request) -> Optional[str]`
13. `get_request_prompt(request) -> str`
14. `get_request_temperature(request) -> Optional[float]`
15. `get_validated_temperature(request, model_context: Any) -> tuple[float, list[str]]`
16. `get_request_thinking_mode(request) -> Optional[str]`
17. `get_request_files(request) -> list`
18. `get_request_use_websearch(request) -> bool`
19. `get_request_as_dict(request) -> dict`
20. `set_request_files(request, files: list) -> None`
21. `get_actually_processed_files() -> list`

**Prompt Building (3):**
22. `build_standard_prompt(system_prompt: str, user_content: str, request, file_context_title: str = "CONTEXT FILES") -> str`
23. `handle_prompt_file_with_fallback(request) -> str`
24. `prepare_chat_style_prompt(request) -> str`

**Execution (1):**
25. `execute(arguments: Dict[str, Any]) -> List`

### 3 Subclasses Must Continue Working
- ChatTool (tools/chat.py)
- ChallengeTool (tools/challenge.py)
- ActivityTool (tools/activity.py)

### 4 Mixins Must Remain Integrated
- WebSearchMixin
- ToolCallMixin
- StreamingMixin
- ContinuationMixin

---

## 📝 IMPLEMENTATION PLAN

### Phase 1: Extract Definition Module (Day 1-2) ✅ COMPLETE
- [x] Create `tools/simple/definition/schema.py`
- [x] Move schema generation logic
- [x] Update SimpleTool to delegate to schema module
- [x] Run baseline tests - must pass
- [x] Document changes

### Phase 2: Extract Intake Module (Day 3-5) ✅ COMPLETE
- [x] Create `tools/simple/intake/accessor.py`
- [x] Move 10 request accessor methods (3 kept in SimpleTool due to instance state)
- [x] Skipped `tools/simple/intake/validator.py` (validation stays in SimpleTool)
- [x] Update SimpleTool to delegate to intake module
- [x] Run baseline tests - must pass (33/33 passing)
- [x] Fixed skipped test for get_validated_temperature
- [x] Document changes

### Phase 3: Extract Preparation Module (Day 6-8)
- [ ] Create `tools/simple/preparation/prompt.py`
- [ ] Move prompt building methods
- [ ] Create `tools/simple/preparation/files.py`
- [ ] Move file handling logic
- [ ] Update SimpleTool to delegate to preparation module
- [ ] Run baseline tests - must pass
- [ ] Document changes

### Phase 4: Extract Execution Module (Day 9-11)
- [ ] Create `tools/simple/execution/caller.py`
- [ ] Move execute() and model calling logic
- [ ] Update SimpleTool to delegate to execution module
- [ ] Run baseline tests - must pass
- [ ] Document changes

### Phase 5: Extract Response Module (Day 12-14)
- [ ] Create `tools/simple/response/formatter.py`
- [ ] Move format_response() logic
- [ ] Update SimpleTool to delegate to response module
- [ ] Run baseline tests - must pass
- [ ] Document changes

### Phase 6: Final Cleanup & Validation (Day 15-16)
- [ ] Simplify SimpleTool to pure facade (~150-200 lines)
- [ ] Add module-level documentation
- [ ] Run full test suite
- [ ] Verify all 3 subclasses work
- [ ] Performance testing
- [ ] User acceptance testing

---

## 🧪 TESTING STRATEGY

### Continuous Testing
- Run baseline tests after EACH module extraction
- All 32 tests must pass before proceeding to next phase
- No regressions allowed

### Integration Testing
- Test all 3 SimpleTool subclasses after each phase
- Verify ChatTool, ChallengeTool, ActivityTool still work
- Test with real MCP protocol

### Performance Testing
- Measure execution time before/after refactoring
- Ensure no performance degradation
- Target: <5% overhead from delegation

---

## 📊 SUCCESS CRITERIA

- [ ] All 32 baseline tests pass
- [ ] All 3 SimpleTool subclasses work unchanged
- [ ] SimpleTool base.py reduced to ~150-200 lines
- [ ] 5 modules created with clear responsibilities
- [ ] 100% backward compatibility maintained
- [ ] No performance degradation
- [ ] Documentation updated
- [ ] User approval obtained

---

## 🚨 RISKS & MITIGATION

**Risk 1: Breaking Backward Compatibility**
- Mitigation: Baseline tests run after each change
- Mitigation: Facade pattern maintains exact public API

**Risk 2: Performance Degradation**
- Mitigation: Performance testing after each phase
- Mitigation: Minimize delegation overhead

**Risk 3: Mixin Integration Issues**
- Mitigation: Test mixin functionality after each change
- Mitigation: Keep mixins in SimpleTool inheritance chain

**Risk 4: Subclass Breakage**
- Mitigation: Test all 3 subclasses after each phase
- Mitigation: No changes to abstract method contracts

---

## 📅 TIMELINE

**Total Estimated Time:** 16 days (2-3 weeks)

- Phase 1: 2 days
- Phase 2: 3 days
- Phase 3: 3 days
- Phase 4: 3 days
- Phase 5: 3 days
- Phase 6: 2 days

**Current Status:** Baseline tests complete, ready to begin Phase 1

---

**Next Step:** Begin Phase 1 - Extract Definition Module

