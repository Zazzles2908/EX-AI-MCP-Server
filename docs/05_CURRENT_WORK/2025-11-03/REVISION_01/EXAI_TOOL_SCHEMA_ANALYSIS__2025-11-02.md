# EXAI Tool Schema Analysis - What Tools ACTUALLY Support

**Date:** 2025-11-02  
**Purpose:** Document ACTUAL tool schemas vs what I tested  
**Status:** 🚨 CRITICAL - My testing was INCOMPLETE!

---

## 🔍 SCHEMA INVESTIGATION RESULTS

### Chat Tool (chat_EXAI-WS)

**ACTUAL Schema:**
```python
class ChatRequest(ToolRequest):
    prompt: str
    files: Optional[list[str]] = []  # ✅ SUPPORTS FILES!
    images: Optional[list[str]] = []  # ✅ SUPPORTS IMAGES!
    continuation_id: Optional[str] = None
    use_websearch: Optional[bool] = True
    model: Optional[str] = None
    temperature: Optional[float] = None
    thinking_mode: Optional[str] = None
```

**What I Tested:** ✅ Files and images (CORRECT)
**Verdict:** ✅ My testing was accurate

---

### Debug Tool (debug_EXAI-WS)

**ACTUAL Schema:**
```python
class DebugInvestigationRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: str
    files_checked: list[str] = []
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    relevant_context: list[str] = []
    hypothesis: Optional[str] = None
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    confidence: Optional[str] = None
    # temperature, use_websearch EXCLUDED from schema
```

**First Step Requirements:**
```python
def get_first_step_required_fields(self) -> list[str]:
    return ["relevant_files"]  # 🚨 MANDATORY IN STEP 1!
```

**What I Tested:** ❌ Did NOT provide relevant_files!
**Verdict:** ⚠️ My test was INVALID - should have failed validation!

---

### Analyze Tool (analyze_EXAI-WS)

**ACTUAL Schema:**
```python
class AnalyzeWorkflowRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: str
    files_checked: list[str] = []
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    relevant_context: list[str] = []
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    analysis_type: Optional[str] = "general"
    output_format: Optional[str] = "detailed"
    # temperature, use_websearch available
```

**First Step Requirements:**
```python
@model_validator(mode="after")
def validate_step_one_requirements(self):
    # Relaxed validation - allows step 1 without relevant_files
```

**What I Tested:** ❌ Did NOT provide relevant_files!
**Verdict:** ⚠️ Test was incomplete - should test with files

---

### Thinkdeep Tool (thinkdeep_EXAI-WS)

**ACTUAL Schema:**
```python
class ThinkDeepWorkflowRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: str
    files_checked: list[str] = []
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    relevant_context: list[str] = []
    hypothesis: Optional[str] = None
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    problem_context: Optional[str] = None
    focus_areas: Optional[list[str]] = None
    # temperature, use_websearch available
```

**What I Tested:** ❌ Did NOT provide relevant_files!
**Verdict:** ✅ Correctly returned "files_required_to_continue"

---

### Codereview Tool (codereview_EXAI-WS)

**ACTUAL Schema:**
```python
class CodeReviewRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: str
    files_checked: list[str] = []
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    relevant_context: list[str] = []
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    review_type: Optional[str] = "full"
    focus_on: Optional[str] = None
    standards: Optional[str] = None
    severity_filter: Optional[str] = "all"
    # temperature, use_websearch EXCLUDED
```

**First Step Requirements:**
```python
@model_validator(mode="after")
def validate_step_one_requirements(self):
    if self.step_number == 1 and not self.relevant_files:
        raise ValueError("Code review requires files to review...")
```

**What I Tested:** ✅ Provided relevant_files
**Verdict:** ⚠️ But tool still skipped expert analysis (low confidence)

---

### Testgen Tool (testgen_EXAI-WS)

**ACTUAL Schema:**
```python
class TestGenRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: str
    files_checked: list[str] = []
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    relevant_context: list[str] = []
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    # temperature, use_websearch EXCLUDED
```

**First Step Requirements:**
```python
@model_validator(mode="after")
def validate_step_one_requirements(self):
    if self.step_number == 1 and not self.relevant_files:
        raise ValueError("Step 1 requires 'relevant_files' field...")
```

**What I Tested:** ❌ Did NOT provide relevant_files!
**Verdict:** ✅ Correctly failed validation

---

### Consensus Tool (consensus_EXAI-WS)

**ACTUAL Schema:**
```python
class ConsensusRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    findings: Optional[str] = None  # Optional except step 1
    relevant_files: list[str] = []  # ✅ SUPPORTS FILES!
    images: Optional[list[str]] = None  # ✅ SUPPORTS IMAGES!
    models: list[dict]  # Required
    current_model_index: Optional[int] = 0
    model_responses: Optional[list] = []
```

**What I Tested:** ❌ Did NOT provide relevant_files or images!
**Verdict:** ⚠️ Test was incomplete - should test with files

---

### Planner Tool (planner_EXAI-WS)

**ACTUAL Schema:**
```python
class PlannerRequest(WorkflowRequest):
    step: str
    step_number: int
    total_steps: int
    next_step_required: bool
    # NO findings field!
    # NO files_checked, relevant_files, relevant_context!
    # NO images field!
    is_step_revision: Optional[bool] = False
    revises_step_number: Optional[int] = None
    is_branch_point: Optional[bool] = False
    branch_from_step: Optional[int] = None
    branch_id: Optional[str] = None
    more_steps_needed: Optional[bool] = False
```

**What I Tested:** ✅ Correct - planner doesn't support files
**Verdict:** ✅ My testing was accurate

---

## 🚨 CRITICAL FINDINGS

### 1. ALL Workflow Tools Support Files & Images! (Except Planner)

**Tools with file/image support:**
- ✅ chat - files, images
- ✅ debug - relevant_files, images
- ✅ analyze - relevant_files, images
- ✅ thinkdeep - relevant_files, images
- ✅ codereview - relevant_files, images
- ✅ testgen - relevant_files, images
- ✅ consensus - relevant_files, images
- ❌ planner - NO file support

### 2. My Testing Was INCOMPLETE!

**What I Did Wrong:**
- ❌ Tested debug WITHOUT relevant_files (should have failed!)
- ❌ Tested analyze WITHOUT relevant_files (incomplete test)
- ❌ Tested thinkdeep WITHOUT relevant_files (correct behavior)
- ❌ Tested consensus WITHOUT relevant_files (incomplete test)

**What I Did Right:**
- ✅ Tested chat WITH files (correct)
- ✅ Tested codereview WITH relevant_files (correct)
- ✅ Tested testgen WITHOUT relevant_files (correctly failed)
- ✅ Tested planner WITHOUT files (correct - not supported)

### 3. Mandatory vs Optional Files

**MANDATORY in Step 1:**
- debug - relevant_files REQUIRED
- codereview - relevant_files REQUIRED
- testgen - relevant_files REQUIRED

**OPTIONAL:**
- analyze - relevant_files optional (relaxed validation)
- thinkdeep - relevant_files optional (but returns files_required_to_continue)
- consensus - relevant_files optional

---

## 📝 NEXT STEPS

1. **Re-test ALL tools WITH files/images** ✅ PRIORITY
2. **Rebuild Docker container** 🐳 REQUIRED
3. **Create revision testing document** 📄 REQUIRED
4. **Validate actual behavior vs schema** 🔍 CRITICAL

---

**Status:** 🚨 TESTING INCOMPLETE - MUST RE-TEST WITH FILES!

