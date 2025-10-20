# WORKFLOWTOOL CONNECTION MAP
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Phase:** Phase 2 - Map Connections  
**Task:** 2.6 - WorkflowTool Connection Analysis  
**Status:** ✅ COMPLETE

---

## 🎯 PURPOSE

Map all connections to/from WorkflowTool to understand:
- Which tools inherit from WorkflowTool (upstream dependencies)
- Which WorkflowTool methods they call (critical public interface)
- What WorkflowTool inherits from (downstream dependencies)
- What WorkflowTool imports (external dependencies)

---

## 📊 WORKFLOWTOOL OVERVIEW

**File:** `tools/workflow/base.py`  
**Size:** 30.5KB (741 lines)  
**Purpose:** Base class for workflow (multi-step) tools  
**Pattern:** Multi-step investigation → Expert analysis → Structured response  

**Inheritance Chain:**
```
WorkflowTool(BaseTool, BaseWorkflowMixin)
└── BaseWorkflowMixin(RequestAccessorMixin, ConversationIntegrationMixin, 
                      FileEmbeddingMixin, ExpertAnalysisMixin, OrchestrationMixin)
```

---

## 🔼 UPSTREAM: TOOLS INHERITING FROM WORKFLOWTOOL

### Direct Subclasses (12 workflow tools)

1. **DebugIssueTool** (`tools/workflows/debug.py`) - Root cause analysis
2. **AnalyzeTool** (`tools/workflows/analyze.py`) - Code analysis
3. **CodeReviewTool** (`tools/workflows/codereview.py`) - Code review
4. **RefactorTool** (`tools/workflows/refactor.py`) - Refactoring analysis
5. **SecauditTool** (`tools/workflows/secaudit.py`) - Security audit
6. **PlannerTool** (`tools/workflows/planner.py`) - Sequential planning
7. **TracerTool** (`tools/workflows/tracer.py`) - Code tracing
8. **TestGenTool** (`tools/workflows/testgen.py`) - Test generation
9. **ConsensusTool** (`tools/workflows/consensus.py`) - Multi-model consensus
10. **ThinkDeepTool** (`tools/workflows/thinkdeep.py`) - Deep reasoning
11. **DocgenTool** (`tools/workflows/docgen.py`) - Documentation generation
12. **PrecommitTool** (`tools/workflows/precommit.py`) - Pre-commit validation

---

## 🔍 CRITICAL PUBLIC INTERFACE (CANNOT CHANGE)

### Abstract Methods (Subclasses MUST Implement)

**1. get_required_actions(step_number, confidence, findings, total_steps) → list[str]**
- **Purpose:** Define required actions for each work phase
- **Used By:** All 12 workflow tools
- **Called By:** Orchestration engine to guide next steps
- **Example:**
```python
def get_required_actions(self, step_number, confidence, findings, total_steps):
    return [
        "Examine relevant code files",
        "Trace execution flow",
        "Check error logs"
    ]
```

**2. should_call_expert_analysis(consolidated_findings) → bool**
- **Purpose:** Decide when to call external model based on tool-specific criteria
- **Used By:** All 12 workflow tools
- **Called By:** Orchestration engine to determine completion
- **Example:**
```python
def should_call_expert_analysis(self, consolidated_findings):
    return len(consolidated_findings.relevant_files) > 0
```

**3. prepare_expert_analysis_context(consolidated_findings) → str**
- **Purpose:** Prepare context for external model call
- **Used By:** All 12 workflow tools
- **Called By:** Expert analysis engine
- **Example:**
```python
def prepare_expert_analysis_context(self, consolidated_findings):
    return f"Analyze these findings: {consolidated_findings.findings}"
```

---

### Hook Methods (Subclasses CAN Override)

**4. get_tool_fields() → dict[str, dict[str, Any]]**
- **Purpose:** Return tool-specific field definitions
- **Default:** Returns empty dict (workflow fields added automatically)
- **Overridden By:** Most workflow tools (add custom fields)

**5. get_first_step_required_fields() → list[str]**
- **Purpose:** Return fields required in step 1
- **Default:** Returns standard workflow fields
- **Overridden By:** Tools with custom first-step requirements

**6. get_minimum_steps_for_tool() → int**
- **Purpose:** Return minimum steps required for this tool
- **Default:** Returns 1
- **Overridden By:** Tools with multi-step requirements

**7. get_workflow_request_model() → Type[WorkflowRequest]**
- **Purpose:** Return tool-specific request model class
- **Default:** Returns base WorkflowRequest
- **Overridden By:** All workflow tools (custom request models)

---

### Workflow Orchestration Methods

**8. execute_workflow(arguments) → list**
- **Purpose:** Main workflow execution engine
- **Used By:** All workflow tools (via execute())
- **Implementation:** OrchestrationMixin
- **Flow:**
  1. Validate request
  2. Process step data
  3. Consolidate findings
  4. Check completion criteria
  5. Call expert analysis if needed
  6. Return structured response

**9. execute(arguments) → list**
- **Purpose:** Execute workflow with timeout and error handling
- **Used By:** All workflow tools (via MCP protocol)
- **Implementation:** WorkflowTool.execute()
- **Timeout:** 120s (base), 240s (final step with expert analysis)

---

### Step Management Methods

**10. process_step_data(request, consolidated_findings) → None**
- **Purpose:** Process current step data and update consolidated findings
- **Used By:** Orchestration engine
- **Implementation:** OrchestrationMixin

**11. handle_backtracking(request, consolidated_findings) → None**
- **Purpose:** Handle backtracking to earlier step
- **Used By:** Orchestration engine
- **Implementation:** OrchestrationMixin

**12. check_work_completion(request, consolidated_findings) → bool**
- **Purpose:** Check if work is complete
- **Used By:** Orchestration engine
- **Implementation:** OrchestrationMixin

---

### Expert Analysis Methods

**13. call_expert_analysis(context, model_name, temperature) → str**
- **Purpose:** Call external AI model for expert analysis
- **Used By:** Orchestration engine
- **Implementation:** ExpertAnalysisMixin

**14. get_expert_analysis_model() → str**
- **Purpose:** Get model name for expert analysis
- **Default:** Returns "auto"
- **Overridden By:** Tools with specific model requirements

---

### File Embedding Methods

**15. embed_files_with_budget(files, budget_tokens, model_name) → tuple[list, int]**
- **Purpose:** Embed files within token budget
- **Used By:** Expert analysis engine
- **Implementation:** FileEmbeddingMixin

**16. estimate_file_tokens(file_path) → int**
- **Purpose:** Estimate tokens for a file
- **Used By:** File embedding engine
- **Implementation:** FileEmbeddingMixin

---

### Conversation Integration Methods

**17. get_conversation_thread(continuation_id) → Optional[dict]**
- **Purpose:** Get conversation thread for continuation
- **Used By:** Orchestration engine
- **Implementation:** ConversationIntegrationMixin

**18. save_workflow_turn(request, response, continuation_id) → None**
- **Purpose:** Save workflow turn to conversation memory
- **Used By:** Orchestration engine
- **Implementation:** ConversationIntegrationMixin

---

### Request Accessor Methods

**19. get_request_step(request) → str**
- **Purpose:** Extract step from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

**20. get_request_step_number(request) → int**
- **Purpose:** Extract step_number from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

**21. get_request_total_steps(request) → int**
- **Purpose:** Extract total_steps from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

**22. get_request_next_step_required(request) → bool**
- **Purpose:** Extract next_step_required from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

**23. get_request_findings(request) → str**
- **Purpose:** Extract findings from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

**24. get_request_confidence(request) → str**
- **Purpose:** Extract confidence from request
- **Used By:** Orchestration engine
- **Implementation:** RequestAccessorMixin

---

## 🔽 DOWNSTREAM: WHAT WORKFLOWTOOL INHERITS FROM

### Mixin Composition (5 mixins via BaseWorkflowMixin)

**BaseWorkflowMixin** (`tools/workflow/workflow_mixin.py`)
- **Composed From:**
  1. **RequestAccessorMixin** (`tools/workflow/request_accessors.py`) - 15.9KB
  2. **ConversationIntegrationMixin** (`tools/workflow/conversation_integration.py`) - 17.8KB
  3. **FileEmbeddingMixin** (`tools/workflow/file_embedding.py`) - 18.1KB
  4. **ExpertAnalysisMixin** (`tools/workflow/expert_analysis.py`) - 34.1KB
  5. **OrchestrationMixin** (`tools/workflow/orchestration.py`) - 26.9KB

**Total Mixin Code:** ~112KB (5 mixins)

---

### BaseTool Inheritance

**BaseTool** (`tools/shared/base_tool.py`)
- **Composed From:**
  - BaseToolCore - Core tool infrastructure
  - FileHandlingMixin - File processing
  - ModelManagementMixin - Model context and selection
  - ResponseFormattingMixin - Response formatting

**Inherited Methods (from BaseTool):**
- `get_name()` - Tool name
- `get_description()` - Tool description
- `get_system_prompt()` - System prompt
- `get_default_temperature()` - Default temperature
- `get_model_category()` - Model category
- `requires_model()` - Whether tool needs AI model
- `process_files()` - File processing
- `resolve_model_context()` - Model context resolution
- `call_model()` - AI model calling
- `format_text_content()` - Format response as TextContent

---

## 📦 EXTERNAL DEPENDENCIES

### Direct Imports

**From tools/shared:**
```python
from tools.shared.base_models import WorkflowRequest
from tools.shared.base_tool import BaseTool
```

**From tools/workflow:**
```python
from .schema_builders import WorkflowSchemaBuilder
from .workflow_mixin import BaseWorkflowMixin
```

**From config:**
```python
from config import TimeoutConfig
```

**From utils:**
```python
from utils.conversation.memory import create_thread, save_turn, load_thread
from utils.progress import send_progress
from utils.file.operations import expand_paths, read_file_content
from utils.model.token_utils import estimate_tokens
```

---

## 🔒 REFACTORING CONSTRAINTS

### CANNOT CHANGE (Breaking Changes)

1. **Class Name:** `WorkflowTool` must remain
2. **Inheritance Chain:** Must preserve BaseWorkflowMixin and BaseTool inheritance
3. **Abstract Methods:** 3 abstract methods must remain (get_required_actions, should_call_expert_analysis, prepare_expert_analysis_context)
4. **Public Method Signatures:** All 24 public methods must keep exact signatures
5. **Workflow Pattern:** Multi-step pattern with pause/resume must be preserved
6. **Expert Analysis Integration:** External model calling must remain

### CAN CHANGE (Internal Implementation)

1. **Internal Methods:** Methods starting with `_` can be refactored
2. **Mixin Implementation:** How mixins work internally can change
3. **File Organization:** Can reorganize mixin files
4. **Helper Functions:** Can extract to separate modules

---

## ✅ TASK 2.6 COMPLETE

**Deliverable:** WORKFLOWTOOL_CONNECTION_MAP.md ✅

**Key Findings:**
- 12 workflow tools inherit from WorkflowTool
- 24 public methods in critical interface (CANNOT CHANGE)
- 3 abstract methods (MUST implement)
- 5 mixins compose BaseWorkflowMixin (~112KB total)
- Timeout coordination: 120s (base), 240s (final step)

**Next Task:** Task 2.7 - Data Flow Mapping

**Time Taken:** ~45 minutes (as estimated)

---

**Status:** ✅ COMPLETE - All WorkflowTool connections mapped with mixin composition documented

