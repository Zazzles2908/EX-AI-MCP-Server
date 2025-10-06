# EXAI TOOL PARAMETER REFERENCE

**Date:** 2025-10-04  
**Purpose:** Complete parameter reference for all 11 EXAI tools  
**Status:** ✅ VALIDATED

---

## 📋 PARAMETER CATEGORIES

### Universal Parameters (All Workflow Tools)
- `model`: Model to use (default: "auto")
- `continuation_id`: Thread continuation ID for multi-turn conversations
- `use_websearch`: Enable web search (default: true for most tools)
- `use_assistant_model`: Enable expert validation (default: true)

### Workflow Parameters (Most Tools)
- `step`: Description of current investigation step
- `step_number`: Current step number (starts at 1)
- `total_steps`: Estimated total steps needed
- `next_step_required`: Whether another step is needed
- `findings`: What you've discovered so far
- `confidence`: Your confidence level (exploring, low, medium, high, very_high, almost_certain, certain)

---

## 🔍 TOOL-SPECIFIC PARAMETERS

### 1. debug_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)

**Optional:**
- `hypothesis`: str
- `files_checked`: list[str]
- `relevant_files`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 2. analyze_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)

**Optional:**
- `analysis_type`: str (architecture, performance, security, quality, general)
- `files_checked`: list[str]
- `relevant_files`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `backtrack_from_step`: int
- `output_format`: str (summary, detailed, actionable)
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 3. codereview_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)
- **`relevant_files`: list[str] (REQUIRED - files to review)**

**Optional:**
- `review_type`: str (full, security, performance, quick)
- `severity_filter`: str (critical, high, medium, low, all)
- `standards`: str
- `focus_on`: str
- `files_checked`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `hypothesis`: str
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 4. refactor_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)

**Optional:**
- `refactor_type`: str (codesmells, decompose, modernize, organization)
- `focus_areas`: list[str]
- `style_guide_examples`: list[str]
- `files_checked`: list[str]
- `relevant_files`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `hypothesis`: str
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 5. testgen_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)
- **`relevant_files`: list[str] (REQUIRED - files to generate tests for)**

**Optional:**
- `files_checked`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `hypothesis`: str
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 6. secaudit_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)
- **`relevant_files`: list[str] (REQUIRED - files to audit)**

**Optional but Recommended:**
- `security_scope`: str (application context - web app, API, etc.)
- `audit_focus`: str (owasp, compliance, infrastructure, dependencies, comprehensive)
- `threat_level`: str (low, medium, high, critical)
- `compliance_requirements`: list[str] (SOC2, PCI DSS, HIPAA, GDPR, ISO 27001, NIST)

**Other Optional:**
- `severity_filter`: str (critical, high, medium, low, all)
- `files_checked`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `hypothesis`: str
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 7. precommit_exai

**Required (Step 1):**
- `step`: str
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool
- `findings`: str (non-empty)
- **`path`: str (REQUIRED - git repository path)**

**Optional:**
- `compare_to`: str (git ref to compare against)
- `include_staged`: bool (default: true)
- `include_unstaged`: bool (default: true)
- `severity_filter`: str (critical, high, medium, low, all)
- `focus_on`: str
- `files_checked`: list[str]
- `relevant_files`: list[str]
- `relevant_context`: list[str]
- `issues_found`: list[dict]
- `images`: list[str]
- `hypothesis`: str
- `backtrack_from_step`: int
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 8. consensus_exai

**Required (Step 1):**
- `step`: str (question or proposal)
- `step_number`: int (1)
- `total_steps`: int (number of models)
- `next_step_required`: bool (true for step 1)
- **`findings`: str (REQUIRED and must be non-empty - your initial analysis)**
- **`models`: list[dict] (REQUIRED - models to consult)**

**Models Format:**
```python
[
    {"model": "glm-4.5-flash", "stance": "for"},
    {"model": "kimi-k2-0905-preview", "stance": "against"},
    {"model": "glm-4.6", "stance": "neutral"}
]
```

**Optional:**
- `relevant_files`: list[str]
- `images`: list[str]
- `current_model_index`: int (internal tracking)
- `model_responses`: list[dict] (internal tracking)
- `model`: str (default: "auto")
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 9. planner_exai

**Required (Step 1):**
- `step`: str (task or problem to plan)
- `step_number`: int (1)
- `total_steps`: int
- `next_step_required`: bool

**Optional:**
- `is_step_revision`: bool
- `revises_step_number`: int
- `is_branch_point`: bool
- `branch_from_step`: int
- `branch_id`: str
- `more_steps_needed`: bool
- `model`: str (default: "auto")
- `use_assistant_model`: bool (default: true)
- `continuation_id`: str

---

### 10. chat_exai

**Required:**
- `prompt`: str (your message or question)

**Optional:**
- `files`: list[str] (context files)
- `images`: list[str] (visual context)
- `model`: str (default: "auto")
- `temperature`: float
- `thinking_mode`: str
- `use_websearch`: bool (default: true)
- `stream`: bool (default: false)
- `continuation_id`: str

---

### 11. challenge_exai

**Required:**
- `prompt`: str (statement or question to challenge)

**Optional:**
- No additional parameters

---

## 🚨 VALIDATION RULES

### Step 1 Validators

**Tools requiring `relevant_files` in step 1:**
- codereview_exai
- testgen_exai
- secaudit_exai

**Tools requiring `path` in step 1:**
- precommit_exai

**Tools requiring non-empty `findings` in step 1:**
- consensus_exai (explicitly validated)
- All other workflow tools (implicitly required)

**Tools requiring `models` in step 1:**
- consensus_exai

### General Rules

1. `step_number` must be >= 1
2. `total_steps` must be >= `step_number`
3. File paths should be absolute (relative paths may be resolved)
4. `confidence` values: exploring, low, medium, high, very_high, almost_certain, certain
5. `model` values: auto, glm-4.5-flash, glm-4.6, kimi-k2-0905-preview, etc.

---

## 📚 EXAMPLES

See `docs/guides/EXAI_TOOL_USAGE_GUIDE.md` for complete working examples of all tools.

---

**Last Updated:** 2025-10-04  
**Status:** ✅ VALIDATED  
**Confidence:** VERY HIGH

