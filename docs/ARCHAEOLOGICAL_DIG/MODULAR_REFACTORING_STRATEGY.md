# MODULAR REFACTORING STRATEGY (OPTION D)
**Date:** 2025-10-10 1:35 PM AEDT  
**Task:** Phase 0, Task 0.6 - Modular Refactoring Strategy  
**Status:** ✅ COMPLETE  
**Approval:** ⏳ PENDING USER APPROVAL

---

## EXECUTIVE SUMMARY

**Strategy:** Principled Refactoring based on Single Responsibility Principle  
**Timeline:** 7-12 weeks for Phase 1 execution  
**Approach:** Incremental, tested, documented refactoring  
**Goal:** Long-term stability through modular architecture

**User's Vision:**
> "Each script should have ONE clear purpose. Easy to find which script to modify. Modular design with proper separation of concerns."

**This strategy delivers that vision!** ✅

---

## GUIDING PRINCIPLES

### 1. Single Responsibility Principle (SRP)
- Each module does ONE thing
- Each module does it well
- Easy to find, easy to modify

### 2. Separation of Concerns
- Prompt building ≠ Model calling ≠ Response formatting
- Each concern gets its own module

### 3. Modular Design
- Small, focused modules (50-200 lines ideal)
- Clear interfaces between modules
- Easy to test independently

### 4. Industry-Standard Organization
- Folder structure reflects responsibilities
- Consistent naming conventions
- Clear hierarchy

### 5. Incremental Refactoring
- One module at a time
- Test after each change
- Commit frequently
- Rollback if needed

---

## PHASE 1: MODULAR REFACTORING PLAN

### Overview

**Total Duration:** 7-12 weeks  
**Phases:** 5 major phases  
**Approach:** Bottom-up (foundation first, implementations last)

```
Phase 1.1: Document Design Intent (1-2 weeks)
Phase 1.2: Refactor Foundation (utils/) (1-2 weeks)
Phase 1.3: Refactor SimpleTool Framework (2-3 weeks)
Phase 1.4: Refactor WorkflowTool Framework (2-3 weeks)
Phase 1.5: Cleanup & Consolidation (1-2 weeks)
```

---

## PHASE 1.1: DOCUMENT DESIGN INTENT (1-2 weeks)

### Goal
Document the SINGLE RESPONSIBILITY for each module before refactoring

**CRITICAL:** This is NOT designing a new system - this is **analyzing the existing system** to refactor it safely!

### Tasks

**1.1.1: Dependency Analysis (2-3 days) - NEW! CRITICAL!**
- For each file >10KB, FIRST analyze dependencies:
  - **UPSTREAM:** What calls this file? (subclasses, importers, callers)
  - **DOWNSTREAM:** What does this file call? (parents, imports, dependencies)
  - **PUBLIC INTERFACE:** What methods/constants CANNOT change?
  - **INTEGRATION POINTS:** How does this fit in the system architecture?
- Document complete dependency graph
- Identify all methods called by external code
- Identify all constants referenced externally
- Identify inheritance chain that must be preserved

**1.1.2: Document Large Files (3-4 days)**
- For each file >10KB, document:
  - Current responsibilities (what does it do?)
  - Single responsibility (what SHOULD it do?)
  - Misplaced responsibilities (what doesn't belong?)
  - Proposed module breakdown (how to split it?)
  - **PUBLIC INTERFACE that must be preserved** (NEW!)
  - **Facade pattern approach** (NEW!)

**Files to document:**
- tools/simple/base.py (55.3KB)
- tools/workflow/expert_analysis.py (34.1KB)
- tools/workflow/base.py (30.5KB)
- tools/workflow/orchestration.py (26.9KB)
- tools/shared/base_tool_file_handling.py (26.5KB)
- tools/shared/base_tool_model_management.py (24.4KB)
- [All files >10KB from Task 0.1]

**1.1.3: Create Design Intent Templates (1-2 days)**
- Create template for module documentation
- Include: **Dependency Analysis** (NEW!), Purpose, Responsibilities, Dependencies, Used By, Examples
- Include: **Facade Pattern Approach** (NEW!)
- Apply to systemprompts/ as reference (already perfect!)

**1.1.4: Document Proposed Module Structure (2-3 days)**
- For each large file, propose modular breakdown **using Facade Pattern**
- Create folder structure diagrams
- Document interfaces between modules
- **Document which public methods must be preserved** (NEW!)
- **Show facade delegation examples** (NEW!)
- Estimate effort and risk

**1.1.5: Create Integration Tests (2-3 days) - NEW! CRITICAL!**
- For each file being refactored, create integration tests
- Test all subclasses/callers BEFORE refactoring (baseline)
- Document expected behavior
- These tests will verify no breaking changes after refactoring

**1.1.6: Get User Approval (1 day)**
- Present design intent documents
- Present dependency analysis
- Review proposed module structures with Facade pattern
- Review integration test plans
- Adjust based on feedback
- Get approval to proceed

**Deliverables:**
- **Dependency analysis for each large file** (NEW!)
- Design intent document for each large file (with Facade pattern)
- Proposed module structure diagrams
- **Integration tests for all subclasses/callers** (NEW!)
- Effort and risk estimates
- User approval

---

## PHASE 1.2: REFACTOR FOUNDATION (utils/) (1-2 weeks)

### Goal
Organize utils/ into modular folder structure

### Current State
```
utils/
├── [37 Python files - NO folder structure]
├── file_utils_*.py (9 files)
├── conversation_*.py (4 files)
├── model_*.py (2 files)
├── config_*.py (2 files)
├── token_*.py (2 files)
└── [18 other files]
```

### Target State
```
utils/
├── file/
│   ├── reader.py (SINGLE RESPONSIBILITY: Read files)
│   ├── writer.py (SINGLE RESPONSIBILITY: Write files)
│   ├── validator.py (SINGLE RESPONSIBILITY: Validate files)
│   ├── security.py (SINGLE RESPONSIBILITY: Security checks)
│   ├── tokens.py (SINGLE RESPONSIBILITY: Count tokens)
│   ├── expansion.py (SINGLE RESPONSIBILITY: Expand paths)
│   ├── json_handler.py (SINGLE RESPONSIBILITY: JSON operations)
│   └── helpers.py (SINGLE RESPONSIBILITY: File helpers)
│
├── conversation/
│   ├── history.py (SINGLE RESPONSIBILITY: Manage history)
│   ├── memory.py (SINGLE RESPONSIBILITY: Manage memory)
│   ├── threads.py (SINGLE RESPONSIBILITY: Manage threads)
│   └── models.py (SINGLE RESPONSIBILITY: Data models)
│
├── model/
│   ├── context.py (SINGLE RESPONSIBILITY: Context management)
│   ├── restrictions.py (SINGLE RESPONSIBILITY: Restriction checks)
│   └── info.py (SINGLE RESPONSIBILITY: Model information)
│
├── config/
│   ├── loader.py (SINGLE RESPONSIBILITY: Load config)
│   └── validator.py (SINGLE RESPONSIBILITY: Validate config)
│
├── token/
│   ├── counter.py (SINGLE RESPONSIBILITY: Count tokens)
│   └── estimator.py (SINGLE RESPONSIBILITY: Estimate tokens)
│
└── [core utils - keep at root]
    ├── progress.py (SINGLE RESPONSIBILITY: Progress tracking)
    ├── observability.py (SINGLE RESPONSIBILITY: Logging)
    ├── cache.py (SINGLE RESPONSIBILITY: Caching)
    ├── client_info.py (SINGLE RESPONSIBILITY: Client info)
    └── ...
```

### Tasks

**1.2.1: Create Folder Structure (1 day)**
- Create utils/file/, utils/conversation/, utils/model/, utils/config/, utils/token/
- Create __init__.py for each folder

**1.2.2: Move and Consolidate Files (2-3 days)**
- Move file_utils_*.py → utils/file/ (consolidate where appropriate)
- Move conversation_*.py → utils/conversation/
- Move model_*.py → utils/model/
- Move config_*.py → utils/config/
- Move token_*.py → utils/token/
- Keep high-impact utils at root (progress, observability, cache)

**1.2.3: Update Imports (2-3 days)**
- Update all imports throughout codebase
- Use find/replace with verification
- Test after each batch of changes

**1.2.4: Test Everything (1-2 days)**
- Run all tests
- Verify all tools still work
- Check for import errors
- Fix any issues

**Deliverables:**
- Organized utils/ folder structure
- All imports updated
- All tests passing
- Documentation updated

**Risk:** LOW (just moving files, no logic changes)

---

## PHASE 1.3: REFACTOR SIMPLETOOL FRAMEWORK (2-3 weeks)

### Goal
Split SimpleTool (55.3KB) into focused modules

### Current State
```
tools/simple/
├── base.py (55.3KB - DOES EVERYTHING!)
│   - Schema generation
│   - Prompt preparation
│   - Model calling
│   - Response formatting
│   - File handling
│   - Conversation management
│   - Progress tracking
│   - Web search
│   - Tool calling
│   - Streaming
│   - Continuation
│
└── mixins/ (already modular - keep as-is)
```

### Target State
```
tools/simple/
├── base.py (orchestration only - ~100 lines)
│   class SimpleTool:
│       def execute(self, request):
│           prompt = self.prompt_builder.build(request)
│           response = self.model_caller.call(prompt)
│           return self.response_formatter.format(response)
│
├── prompt/
│   ├── __init__.py
│   ├── builder.py (~50-100 lines)
│   │   SINGLE RESPONSIBILITY: Build prompts
│   │   - Takes request data
│   │   - Constructs prompt string
│   │   - Adds system prompt
│   │   - Returns complete prompt
│   │
│   └── validator.py (~50 lines)
│       SINGLE RESPONSIBILITY: Validate prompts
│
├── model/
│   ├── __init__.py
│   ├── caller.py (~50-100 lines)
│   │   SINGLE RESPONSIBILITY: Call AI models
│   │   - Takes prompt
│   │   - Calls provider
│   │   - Returns raw response
│   │
│   └── selector.py (~50 lines)
│       SINGLE RESPONSIBILITY: Select model
│
├── response/
│   ├── __init__.py
│   ├── formatter.py (~50-100 lines)
│   │   SINGLE RESPONSIBILITY: Format responses
│   │   - Takes raw response
│   │   - Formats for MCP
│   │   - Returns formatted response
│   │
│   └── validator.py (~50 lines)
│       SINGLE RESPONSIBILITY: Validate responses
│
├── execution/
│   ├── __init__.py
│   └── executor.py (~100 lines)
│       SINGLE RESPONSIBILITY: Execute tool logic
│
├── schema/
│   ├── __init__.py
│   └── builder.py (~100 lines)
│       SINGLE RESPONSIBILITY: Build JSON schemas
│
└── mixins/ (existing - keep as-is)
    ├── continuation_mixin.py
    ├── streaming_mixin.py
    ├── tool_call_mixin.py
    ├── web_search_mixin.py
    └── file_mixin.py
```

### Tasks

**1.3.1: Extract Prompt Module (2-3 days)**
- Create tools/simple/prompt/
- Extract prompt building logic from base.py
- Create builder.py and validator.py
- Update base.py to use new modules
- Test all 4 simple tools

**1.3.2: Extract Model Module (2-3 days)**
- Create tools/simple/model/
- Extract model calling logic from base.py
- Create caller.py and selector.py
- Update base.py to use new modules
- Test all 4 simple tools

**1.3.3: Extract Response Module (2-3 days)**
- Create tools/simple/response/
- Extract response formatting logic from base.py
- Create formatter.py and validator.py
- Update base.py to use new modules
- Test all 4 simple tools

**1.3.4: Extract Execution & Schema Modules (2-3 days)**
- Create tools/simple/execution/ and tools/simple/schema/
- Extract remaining logic from base.py
- Update base.py to orchestrate modules
- Test all 4 simple tools

**1.3.5: Final Integration & Testing (2-3 days)**
- Verify base.py is now ~100 lines (orchestration only)
- Run comprehensive tests
- Update documentation
- Commit and push

**Deliverables:**
- Modular SimpleTool framework
- base.py reduced from 55.3KB to ~5-10KB
- All 4 simple tools working
- Documentation updated

**Risk:** MEDIUM (affects 4 tools, but well-tested)

---

## PHASE 1.4: REFACTOR WORKFLOWTOOL FRAMEWORK (2-3 weeks)

### Goal
Split large workflow mixins into focused modules

### Current State
```
tools/workflow/
├── base.py (30.5KB - WorkflowTool)
├── workflow_mixin.py (10.1KB - BaseWorkflowMixin)
├── expert_analysis.py (34.1KB - ExpertAnalysisMixin)
├── orchestration.py (26.9KB - OrchestrationMixin)
├── file_embedding.py (18.1KB - FileEmbeddingMixin)
├── conversation_integration.py (17.8KB - ConversationIntegrationMixin)
└── request_accessors.py (15.9KB - RequestAccessorMixin)
```

### Target State
```
tools/workflow/
├── base/
│   ├── __init__.py
│   ├── tool.py (~100 lines)
│   │   SINGLE RESPONSIBILITY: WorkflowTool base class
│   │
│   └── mixin.py (~100 lines)
│       SINGLE RESPONSIBILITY: BaseWorkflowMixin composition
│
├── mixins/
│   ├── expert/
│   │   ├── __init__.py (exports ExpertAnalysisMixin)
│   │   ├── analyzer.py (~100-150 lines)
│   │   │   SINGLE RESPONSIBILITY: Expert analysis logic
│   │   │
│   │   ├── fallback.py (~50-100 lines)
│   │   │   SINGLE RESPONSIBILITY: Fallback handling
│   │   │
│   │   ├── thinking_mode.py (~50-100 lines)
│   │   │   SINGLE RESPONSIBILITY: Thinking mode selection
│   │   │
│   │   └── integration.py (~100 lines)
│   │       SINGLE RESPONSIBILITY: Model integration
│   │
│   ├── orchestration/
│   │   ├── __init__.py (exports OrchestrationMixin)
│   │   ├── step_manager.py (~100-150 lines)
│   │   │   SINGLE RESPONSIBILITY: Manage workflow steps
│   │   │
│   │   ├── state_manager.py (~100 lines)
│   │   │   SINGLE RESPONSIBILITY: Manage workflow state
│   │   │
│   │   └── validator.py (~50-100 lines)
│   │       SINGLE RESPONSIBILITY: Validate workflow
│   │
│   ├── file_embedding/
│   │   ├── __init__.py (exports FileEmbeddingMixin)
│   │   ├── embedder.py (~100 lines)
│   │   │   SINGLE RESPONSIBILITY: Embed files
│   │   │
│   │   └── uploader.py (~100 lines)
│   │       SINGLE RESPONSIBILITY: Upload files
│   │
│   ├── conversation/
│   │   ├── __init__.py (exports ConversationIntegrationMixin)
│   │   ├── integrator.py (~100 lines)
│   │   │   SINGLE RESPONSIBILITY: Integrate conversations
│   │   │
│   │   └── history.py (~100 lines)
│   │       SINGLE RESPONSIBILITY: Manage history
│   │
│   └── request/
│       ├── __init__.py (exports RequestAccessorMixin)
│       └── accessor.py (~100-150 lines)
│           SINGLE RESPONSIBILITY: Access request data
│
└── schema/
    ├── __init__.py
    └── builder.py (~100 lines)
        SINGLE RESPONSIBILITY: Build workflow schemas
```

### Tasks

**1.4.1: Refactor ExpertAnalysisMixin (3-4 days)**
- Create tools/workflow/mixins/expert/
- Split expert_analysis.py (34.1KB) into 4 modules
- Create analyzer.py, fallback.py, thinking_mode.py, integration.py
- Update imports
- Test all 12 workflow tools

**1.4.2: Refactor OrchestrationMixin (3-4 days)**
- Create tools/workflow/mixins/orchestration/
- Split orchestration.py (26.9KB) into 3 modules
- Create step_manager.py, state_manager.py, validator.py
- Update imports
- Test all 12 workflow tools

**1.4.3: Refactor Other Mixins (2-3 days)**
- Refactor file_embedding.py → mixins/file_embedding/
- Refactor conversation_integration.py → mixins/conversation/
- Refactor request_accessors.py → mixins/request/
- Update imports
- Test all 12 workflow tools

**1.4.4: Reorganize Base Classes (2-3 days)**
- Move base.py → base/tool.py
- Move workflow_mixin.py → base/mixin.py
- Update imports
- Test all 12 workflow tools

**1.4.5: Final Integration & Testing (2-3 days)**
- Run comprehensive tests
- Verify all 12 workflow tools work
- Update documentation
- Commit and push

**Deliverables:**
- Modular WorkflowTool framework
- Large mixins split into focused modules
- All 12 workflow tools working
- Documentation updated

**Risk:** MEDIUM-HIGH (affects 12 tools, complex refactoring)

---

## PHASE 1.5: CLEANUP & CONSOLIDATION (1-2 weeks)

### Goal
Clean up organizational drift and consolidate duplicates

### Tasks

**1.5.1: Delete Empty/Orphaned Directories (1 day)**
- Delete src/server/conversation/ (empty)
- Delete tools/streaming/ (empty)
- Verify and delete src/conf/ (orphaned)
- Verify and delete src/config/ (orphaned)

**1.5.2: Move Misplaced Files (1-2 days)**
- Move root-level tools to appropriate folders
  - activity.py → tools/simple/implementations/
  - challenge.py → tools/simple/implementations/
  - chat.py → tools/simple/implementations/
- Update imports and registry

**1.5.3: Improve Naming Clarity (2-3 days)**
- Consider renaming for clarity:
  - tools/workflow/ → tools/workflow_base/ (if needed)
  - src/server/providers/ → src/server/provider_config/ (if needed)
- Update all imports
- Update documentation

**1.5.4: Create Architecture Documentation (2-3 days)**
- Create docs/architecture/DEPENDENCY_RULES.md
- Create docs/architecture/SHARED_INFRASTRUCTURE.md
- Create docs/architecture/BASE_CLASS_HIERARCHY.md
- Create docs/architecture/MODULE_ORGANIZATION.md
- Document design intent for all modules

**1.5.5: Final Testing & Validation (2-3 days)**
- Run full test suite
- Test all tools manually
- Verify no regressions
- Performance testing
- Fix any issues

**Deliverables:**
- Clean directory structure
- No empty/orphaned directories
- Clear naming conventions
- Complete architecture documentation
- All tests passing

**Risk:** LOW (cleanup and documentation)

---

## SUCCESS CRITERIA

### Phase 1 Complete When:

**1. Modular Structure ✅**
- [ ] utils/ organized into folders by responsibility
- [ ] SimpleTool split into focused modules (<200 lines each)
- [ ] WorkflowTool mixins split into focused modules (<200 lines each)
- [ ] No files >10KB except implementations

**2. Single Responsibility ✅**
- [ ] Each module has ONE clear purpose
- [ ] Easy to find which module to modify
- [ ] Clear separation of concerns

**3. Documentation ✅**
- [ ] Design intent documented for each module
- [ ] Architecture documentation complete
- [ ] Dependency rules documented
- [ ] Module organization documented

**4. Testing ✅**
- [ ] All tests passing
- [ ] All tools working
- [ ] No regressions
- [ ] Performance maintained

**5. Clean Organization ✅**
- [ ] No empty/orphaned directories
- [ ] Clear naming conventions
- [ ] Consistent folder structure
- [ ] Industry-standard layout

---

## RISK MITIGATION

### Risk 1: Breaking Changes
**Mitigation:**
- Incremental refactoring (one module at a time)
- Test after each change
- Commit frequently
- Keep rollback option available

### Risk 2: Import Hell
**Mitigation:**
- Update imports in batches
- Use find/replace with verification
- Test after each batch
- Document import changes

### Risk 3: Scope Creep
**Mitigation:**
- Stick to the plan
- Don't add new features during refactoring
- Focus on structure, not functionality
- Get user approval before deviating

### Risk 4: Time Overrun
**Mitigation:**
- Break into small tasks (2-3 days each)
- Track progress daily
- Adjust timeline if needed
- Communicate with user

---

## TIMELINE ESTIMATE

| Phase | Duration | Risk | Dependencies |
|-------|----------|------|--------------|
| 1.1: Document Design Intent | 1-2 weeks | LOW | None |
| 1.2: Refactor Foundation (utils/) | 1-2 weeks | LOW | 1.1 complete |
| 1.3: Refactor SimpleTool | 2-3 weeks | MEDIUM | 1.2 complete |
| 1.4: Refactor WorkflowTool | 2-3 weeks | MEDIUM-HIGH | 1.2 complete |
| 1.5: Cleanup & Consolidation | 1-2 weeks | LOW | 1.3, 1.4 complete |

**Total: 7-12 weeks**

**Note:** Phases 1.3 and 1.4 can run in parallel after 1.2 is complete, potentially reducing total time to 7-9 weeks.

---

## NEXT STEPS

**Immediate:**
1. ✅ Get user approval for this strategy
2. ✅ Begin Phase 1.1: Document Design Intent
3. ✅ Create design intent template
4. ✅ Document first large file (SimpleTool base.py)

**After Approval:**
1. Execute Phase 1.1 (1-2 weeks)
2. Review design intent documents with user
3. Get approval to proceed with Phase 1.2
4. Execute remaining phases

---

**STATUS:** ✅ TASK 0.6 COMPLETE - AWAITING USER APPROVAL

This strategy delivers the user's vision: modular, single-purpose modules with long-term stability!

