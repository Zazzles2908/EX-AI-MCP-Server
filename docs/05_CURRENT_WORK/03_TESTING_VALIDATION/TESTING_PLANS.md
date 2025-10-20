# Phase 20: Complete EXAI Tools Testing Plan
**Date:** 2025-10-15  
**Status:** IN PROGRESS  
**EXAI Oversight:** Enabled (Kimi K2-0905-preview + GLM-4.5-flash)

---

## Executive Summary

This plan completes testing of the remaining 17 EXAI tools (out of 29 total) using EXAI-recommended batched testing strategy with proper timeouts and real-world scenarios.

**Current Progress:** 12/29 tools tested (41.4%)  
**Remaining:** 17 tools across 3 categories  
**Strategy:** Batched testing by related functionality with EXAI oversight

---

## Testing Status Overview

```
COMPLETED (12/29 - 41.4%)
├── Utility Tools (9/9) ................ 100% PASS
├── Provider Tools (2/8) ............... 100% PASS (non-file tools)
├── Planning Tools (0/2) ............... 0% (consensus timed out)
└── Workflow Tools (0/10) .............. 0% (3 timed out during testing)

REMAINING (17/29 - 58.6%)
├── Provider Tools (6/8) ............... File upload tools
├── Planning Tools (1/2) ............... Consensus (retry needed)
└── Workflow Tools (7/10) .............. Real scenario testing needed
```

---

## EXAI Strategic Recommendations

**Key Insights from EXAI (Kimi K2-0905-preview):**

1. **Workflow tools are DESIGNED to timeout** - They perform real analysis work that inherently takes time. This isn't a bug; it's expected behavior.

2. **Test them properly or don't test them at all** - Quick validation with `confidence="certain"` would only give false confidence.

3. **Provider tools have complex setup** - Better to discover file upload issues early.

4. **Incremental approach** - Test one workflow tool completely before moving to next.

5. **600s timeout is better than 60s failure** - A successful deep analysis is infinitely better than a quick timeout.

---

## Phase 1: Provider Tools with File Uploads

**Objective:** Test all 6 provider tools requiring file uploads  
**Duration:** 1-2 hours  
**Timeout:** 120s per tool  
**EXAI Oversight:** Document all file handling issues

### Preparation Step: Create Test Files

**Location:** `c:\Project\EX-AI-MCP-Server\test_files\`

**Required Files:**
1. `sample_code.py` (10-20 lines of Python code)
2. `sample_doc.pdf` (1-2 page document)
3. `config.json` (small JSON configuration)

**Creation Script:**
```powershell
New-Item -ItemType Directory -Path "test_files" -Force
# Create sample Python file
@"
def calculate_sum(a, b):
    '''Calculate sum of two numbers'''
    return a + b

def main():
    result = calculate_sum(5, 3)
    print(f'Result: {result}')

if __name__ == '__main__':
    main()
"@ | Out-File -FilePath "test_files\sample_code.py" -Encoding UTF8

# Create sample JSON
@"
{
  "app_name": "EXAI MCP Server",
  "version": "2.0.0",
  "providers": ["kimi", "glm"]
}
"@ | Out-File -FilePath "test_files\config.json" -Encoding UTF8
```

### Batch 1A: Kimi File Operations (3 tools)

**Tools:**
1. `kimi_upload_and_extract` - Upload and extract content from file
2. `kimi_multi_file_chat` - Chat with multiple files as context
3. `kimi_chat_with_tools` - Chat with file + tools integration

**Test Parameters:**
```python
# kimi_upload_and_extract
{
    "files": ["c:\\Project\\EX-AI-MCP-Server\\test_files\\sample_code.py"],
    "purpose": "file-extract"
}

# kimi_multi_file_chat
{
    "files": [
        "c:\\Project\\EX-AI-MCP-Server\\test_files\\sample_code.py",
        "c:\\Project\\EX-AI-MCP-Server\\test_files\\config.json"
    ],
    "prompt": "Summarize the purpose of these files"
}

# kimi_chat_with_tools
{
    "messages": "Analyze the code in sample_code.py",
    "use_websearch": false
}
```

**Success Criteria:**
- Files upload successfully
- Content extraction works
- No memory/size limit errors
- Response contains file content analysis

### Batch 1B: GLM File Operations (2 tools)

**Tools:**
1. `glm_upload_file` - Upload file to GLM
2. `glm_chat_with_tools` - GLM chat with tools integration

**Test Parameters:**
```python
# glm_upload_file
{
    "file": "c:\\Project\\EX-AI-MCP-Server\\test_files\\sample_code.py",
    "purpose": "agent"
}

# glm_chat_with_tools
{
    "messages": "Test GLM tools integration",
    "use_websearch": true
}
```

**Success Criteria:**
- File upload completes
- GLM accepts file format
- Tools integration works
- No authentication errors

### Batch 1C: Kimi Intent Analysis (1 tool)

**Tool:** `kimi_intent_analysis`

**Test Parameters:**
```python
{
    "prompt": "I need to systematically test all EXAI tools",
    "context": "Testing EXAI MCP server tools",
    "use_websearch": false
}
```

**Success Criteria:**
- Intent classification works
- Returns structured JSON
- Routing hints are reasonable

---

## Phase 2: Consensus Tool Retry

**Objective:** Successfully test consensus tool with proper timeout  
**Duration:** 5-10 minutes  
**Timeout:** 180s (3x original)  
**EXAI Oversight:** Document actual execution time

### Test Parameters

```python
{
    "step": "Should we use 600s timeout for workflow tools testing?",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "models": [
        {"model": "kimi-k2-0905-preview", "stance": "for"},
        {"model": "glm-4.5-flash", "stance": "against"}
    ]
}
```

**Success Criteria:**
- Completes within 180s
- Both models provide responses
- Consensus summary generated
- No timeout errors

**Fallback:** If 180s fails, retry with 300s timeout

---

## Phase 3: Workflow Tools - Real Scenarios

**Objective:** Test all 7 remaining workflow tools with real analysis  
**Duration:** 2-3 hours  
**Timeout:** 600s per tool  
**EXAI Oversight:** Document all analysis quality and execution times

### Batch 3A: Code Analysis Tools (3 tools)

**Tools:**
1. `codereview` - Comprehensive code review
2. `secaudit` - Security audit
3. `tracer` - Execution flow tracing

**Test Files:** Use actual EXAI codebase files
- `scripts/test_all_exai_tools.py` (580 lines)
- `scripts/run_ws_shim.py` (347 lines)
- `src/daemon/ws_server.py`

**Test Parameters:**
```python
# codereview
{
    "step": "Review the test_all_exai_tools.py script for code quality",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Initial review of automated testing script",
    "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\scripts\\test_all_exai_tools.py"],
    "review_type": "full",
    "confidence": "medium"
}

# secaudit
{
    "step": "Perform security audit on WebSocket shim",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Security analysis of WebSocket authentication and connection handling",
    "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\scripts\\run_ws_shim.py"],
    "audit_focus": "comprehensive",
    "threat_level": "medium"
}

# tracer
{
    "step": "Trace execution flow of WebSocket connection establishment",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Tracing _ensure_ws() function call chain",
    "target_description": "WebSocket connection establishment in run_ws_shim.py",
    "trace_mode": "precision"
}
```

**Success Criteria:**
- Tools complete within 600s
- Provide meaningful analysis
- Identify real issues/patterns
- Generate actionable recommendations

### Batch 3B: Code Generation Tools (3 tools)

**Tools:**
1. `testgen` - Generate unit tests
2. `refactor` - Suggest refactoring improvements
3. `docgen` - Generate documentation

**Test Parameters:**
```python
# testgen
{
    "step": "Generate unit tests for the EXAIToolTester class",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Test generation for WebSocket testing infrastructure",
    "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\scripts\\test_all_exai_tools.py"]
}

# refactor
{
    "step": "Suggest refactoring improvements for run_ws_shim.py",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Refactoring analysis for WebSocket shim",
    "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\scripts\\run_ws_shim.py"],
    "refactor_type": "codesmells"
}

# docgen
{
    "step": "Generate comprehensive documentation for test_all_exai_tools.py",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Documentation generation for testing infrastructure",
    "num_files_documented": 0,
    "total_files_to_document": 1
}
```

**Success Criteria:**
- Generate usable code/documentation
- Follow project conventions
- Provide clear explanations
- No syntax errors in generated code

### Batch 3C: Integration Tool (1 tool)

**Tool:** `precommit` - Pre-commit validation

**Test Parameters:**
```python
{
    "step": "Validate changes in current working directory for commit readiness",
    "step_number": 1,
    "total_steps": 1,
    "next_step_required": false,
    "findings": "Pre-commit validation of recent changes",
    "path": "c:\\Project\\EX-AI-MCP-Server",
    "include_staged": true,
    "include_unstaged": true
}
```

**Success Criteria:**
- Analyzes git changes
- Identifies potential issues
- Provides commit recommendations
- No false positives

---

## Phase 4: Final Validation & Documentation

**Objective:** Validate all testing complete and document results  
**Duration:** 30 minutes

### Tasks

1. **Generate Final Test Report**
   - Consolidate all test results
   - Document EXAI oversight findings
   - Calculate final success rates
   - Identify any remaining issues

2. **Update Documentation**
   - Update ACTUAL_TESTING_RESULTS_2025-10-15.md
   - Create PHASE_20_COMPLETION_REPORT.md
   - Archive intermediate test reports

3. **Verify Coverage**
   - Confirm all 29 tools tested
   - Document any tools that cannot be tested
   - Provide recommendations for production use

---

## Execution Checklist

```
PREPARATION
[ ] Create test_files directory
[ ] Generate sample_code.py
[ ] Generate config.json
[ ] Verify Docker daemon running
[ ] Confirm WebSocket shim timeout fix applied

PHASE 1: PROVIDER TOOLS (6 tools)
[ ] Batch 1A: kimi_upload_and_extract
[ ] Batch 1A: kimi_multi_file_chat
[ ] Batch 1A: kimi_chat_with_tools
[ ] Batch 1B: glm_upload_file
[ ] Batch 1B: glm_chat_with_tools
[ ] Batch 1C: kimi_intent_analysis

PHASE 2: PLANNING TOOLS (1 tool)
[ ] consensus (180s timeout)
[ ] If failed, retry with 300s timeout

PHASE 3: WORKFLOW TOOLS (7 tools)
[ ] Batch 3A: codereview
[ ] Batch 3A: secaudit
[ ] Batch 3A: tracer
[ ] Batch 3B: testgen
[ ] Batch 3B: refactor
[ ] Batch 3B: docgen
[ ] Batch 3C: precommit

PHASE 4: FINAL VALIDATION
[ ] Generate final test report
[ ] Update documentation
[ ] Verify 100% coverage (29/29 tools)
[ ] Archive test reports
```

---

## EXAI Oversight Documentation Requirements

For each tool tested, document:

1. **Test Execution**
   - Actual timeout used
   - Actual execution time
   - Success/failure status
   - Error messages (if any)

2. **EXAI Analysis**
   - Quality of analysis/output
   - Relevance to test scenario
   - Unexpected behaviors
   - Recommendations for improvement

3. **Issues Identified**
   - Configuration problems
   - Parameter mismatches
   - Timeout inadequacies
   - Documentation gaps

4. **Lessons Learned**
   - Optimal timeout values
   - Best test parameters
   - Common pitfalls
   - Production recommendations

---

## Success Metrics

**Overall Goal:** 100% tool coverage (29/29 tools tested)

**Phase-Specific Goals:**
- Phase 1: 6/6 provider tools working with file uploads
- Phase 2: 1/1 planning tool (consensus) working with proper timeout
- Phase 3: 7/7 workflow tools providing meaningful analysis
- Phase 4: Complete documentation with EXAI oversight findings

**Quality Metrics:**
- All tools respond without errors
- Timeouts are appropriate for tool complexity
- Analysis quality meets expectations
- Documentation is comprehensive

---

**Status:** Ready to execute  
**Next Action:** Begin Phase 1 - Create test files and test provider tools

