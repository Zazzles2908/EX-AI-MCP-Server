# Task B.1: Complete WorkflowTools Testing - Implementation Plan

**Date**: 2025-10-13  
**Status**: 🔄 IN_PROGRESS  
**Task**: Test all 12 WorkflowTools individually with realistic scenarios

---

## Summary

Comprehensive test scripts have been created for all 12 WorkflowTools. The testing infrastructure is ready for execution.

---

## Test Scripts Created

### 1. `scripts/testing/test_all_workflow_tools.py`
**Coverage**: Tools 1-7
- analyze - Code analysis workflow
- codereview - Code review workflow
- thinkdeep - Deep investigation workflow
- testgen - Test generation workflow
- debug - Debugging workflow
- refactor - Refactoring workflow
- secaudit - Security audit workflow

### 2. `scripts/testing/test_workflow_tools_part2.py`
**Coverage**: Tools 8-12
- precommit - Pre-commit checks workflow
- docgen - Documentation generation workflow
- tracer - Code tracing workflow
- consensus - Multi-model consensus workflow
- planner - Planning workflow

---

## Test Methodology

### Test Approach
Each tool is tested with:
1. **Realistic Scenario**: Real-world use case matching tool's purpose
2. **File Context**: Actual project files where applicable
3. **Expert Analysis**: Enabled to verify full workflow
4. **Timeout Handling**: 120-second timeout per tool
5. **Error Handling**: Comprehensive exception catching

### Test Parameters
All tests use:
- **Model**: `glm-4.5-flash` (fast, reliable)
- **Expert Analysis**: Enabled (`use_assistant_model=True`)
- **Step-based Workflow**: Single-step completion for speed
- **File Embedding**: Respects new limits (max 20 files)

### Success Criteria
For each tool:
- ✅ Tool completes without errors
- ✅ Expert analysis executes successfully
- ✅ No daemon crashes
- ✅ Response time < 120 seconds
- ✅ File embedding respects limits

---

## Tool-Specific Test Scenarios

### 1. analyze
**Scenario**: Analyze test_system_stability.py for code quality  
**Files**: `scripts/testing/test_system_stability.py`  
**Focus**: Code patterns, architecture, quality assessment

### 2. codereview
**Scenario**: Review critical issues test script  
**Files**: `scripts/testing/test_critical_issues_7_to_10.py`  
**Focus**: Code quality, potential issues, best practices

### 3. thinkdeep
**Scenario**: Investigate best approach for testing WorkflowTools  
**Files**: None (conceptual investigation)  
**Focus**: Deep reasoning, strategy exploration

### 4. testgen
**Scenario**: Generate tests for env_loader module  
**Files**: `src/bootstrap/env_loader.py`  
**Focus**: Test coverage, edge cases, test generation

### 5. debug
**Scenario**: Debug intermittent test failures  
**Files**: None (conceptual debugging)  
**Focus**: Root cause analysis, debugging strategies

### 6. refactor
**Scenario**: Suggest refactoring for env_loader  
**Files**: `src/bootstrap/env_loader.py`  
**Focus**: Code improvement, maintainability, patterns

### 7. secaudit
**Scenario**: Security audit of WebSocket authentication  
**Files**: `src/daemon/ws_server.py`  
**Focus**: Security vulnerabilities, auth validation

### 8. precommit
**Scenario**: Pre-commit checks on test script  
**Files**: `scripts/testing/test_system_stability.py`  
**Focus**: Code quality, linting, pre-commit validation

### 9. docgen
**Scenario**: Generate documentation for env_loader  
**Files**: `src/bootstrap/env_loader.py`  
**Focus**: Documentation generation, API docs

### 10. tracer
**Scenario**: Trace WebSocket authentication flow  
**Files**: None (code tracing)  
**Focus**: Execution flow, call chains, dependencies

### 11. consensus
**Scenario**: Multi-model consensus on async/await usage  
**Files**: None (architectural decision)  
**Focus**: Multi-model consultation, consensus building

### 12. planner
**Scenario**: Plan rate limiting implementation  
**Files**: None (planning)  
**Focus**: Implementation planning, task breakdown

---

## Test Infrastructure

### WebSocket Testing Framework
```python
class WorkflowToolTester:
    - connect(): Establish authenticated WebSocket connection
    - call_tool(): Send tool call and wait for response
    - test_<tool>(): Individual tool test methods
```

### Features
- ✅ Async WebSocket communication
- ✅ Authentication handling
- ✅ Timeout management
- ✅ Progress message filtering
- ✅ Error handling and reporting
- ✅ Performance metrics collection

---

## Expected Results

### Performance Expectations
Based on Phase A fixes:
- **analyze**: 15-30s (with expert analysis)
- **codereview**: 15-30s (with expert analysis)
- **thinkdeep**: 10-20s (conceptual, less file I/O)
- **testgen**: 15-30s (with expert analysis)
- **debug**: 10-20s (conceptual)
- **refactor**: 15-30s (with expert analysis)
- **secaudit**: 15-30s (with expert analysis)
- **precommit**: 15-30s (with expert analysis)
- **docgen**: 15-30s (with expert analysis)
- **tracer**: 15-30s (with expert analysis)
- **consensus**: 20-40s (multi-model)
- **planner**: 15-30s (with expert analysis)

### File Embedding Expectations
With new limits (Issue #8 fix):
- **Max files**: 20 (configurable via `EXPERT_ANALYSIS_MAX_FILE_COUNT`)
- **Max file size**: 10KB (configurable via `EXPERT_ANALYSIS_MAX_FILE_SIZE_KB`)
- **File inclusion**: Disabled by default (`EXPERT_ANALYSIS_INCLUDE_FILES=false`)

### Model Auto-Upgrade Expectations
With new configuration (Issue #10 fix):
- **Auto-upgrade**: Enabled by default (`EXPERT_ANALYSIS_AUTO_UPGRADE=true`)
- **Warning**: Clear message when upgrade occurs
- **User control**: Can disable via env var

---

## Verification Checklist

### Pre-Test Verification
- [x] Test scripts created
- [x] All 12 tools covered
- [x] Realistic scenarios defined
- [x] WebSocket infrastructure ready
- [x] Server running and stable
- [x] Phase A fixes applied (.env updated)

### Post-Test Verification (Pending Execution)
- [ ] All 12 tools tested
- [ ] Test results documented
- [ ] Performance metrics collected
- [ ] No daemon crashes observed
- [ ] File embedding limits respected
- [ ] Expert analysis working correctly
- [ ] Evidence documented

---

## Next Steps

1. **Execute Part 1 Tests** (Tools 1-7)
   - Run `python scripts/testing/test_all_workflow_tools.py`
   - Monitor daemon stability
   - Collect performance metrics
   - Document results

2. **Execute Part 2 Tests** (Tools 8-12)
   - Run `python scripts/testing/test_workflow_tools_part2.py`
   - Monitor daemon stability
   - Collect performance metrics
   - Document results

3. **Create Comprehensive Report**
   - Consolidate results from both parts
   - Document any issues found
   - Create evidence file with full results
   - Update task status

4. **Fix Any Issues Found**
   - Address failures before marking complete
   - Re-test after fixes
   - Ensure 100% pass rate

---

## Files Created

1. **`scripts/testing/test_all_workflow_tools.py`** (NEW)
   - Tests tools 1-7
   - Comprehensive WebSocket testing framework
   - Performance metrics collection

2. **`scripts/testing/test_workflow_tools_part2.py`** (NEW)
   - Tests tools 8-12
   - Same testing framework
   - Completes full coverage

3. **`docs/consolidated_checklist/evidence/B1_WORKFLOWTOOLS_TESTING_PLAN.md`** (THIS FILE)
   - Test plan documentation
   - Tool scenarios
   - Success criteria

---

## Conclusion

**Status**: 🔄 **IN_PROGRESS**

Test infrastructure is complete and ready for execution. All 12 WorkflowTools have dedicated test scenarios with realistic use cases.

**Next Action**: Execute test scripts and document results.

