# EXAI Capabilities and Parameters Analysis

**Date**: 2025-11-03
**Purpose**: Comprehensive documentation of EXAI MCP server capabilities, parameters, and usage guidelines

---

## 🔧 EXAI MCP Server Overview

**Version**: 2.0.0
**Last Updated**: 2025-09-26
**Installation Path**: `/app`
**Platform**: Linux 6.6.87.2-microsoft-standard-WSL2

---

## 📊 Available Providers

### 1. Moonshot Kimi ✅ (Configured)
**Status**: Active and available
**Models**: 14 models total

| Model | Context Window | Type | Status |
|-------|---------------|------|--------|
| `kimi-k2-0905-preview` | 262K | Reasoning | ✅ |
| `kimi-k2-0711-preview` | 131K | Reasoning | ✅ |
| `kimi-k2-turbo-preview` | 262K | High-Speed | ✅ |
| `kimi-thinking-preview` | 131K | Advanced Reasoning | ✅ |
| `kimi-latest` | 128K | General | ✅ |
| `kimi-latest-128k` | 131K | Long Context | ✅ |
| `kimi-latest-32k` | 32K | Standard | ✅ |
| `kimi-latest-8k` | 8K | Fast | ✅ |
| `moonshot-v1-128k` | 128K | General | ✅ |
| `moonshot-v1-32k` | 32K | Standard | ✅ |
| `moonshot-v1-8k` | 8K | Fast | ✅ |
| `moonshot-v1-8k-vision-preview` | 8K | Vision | ✅ |
| `moonshot-v1-32k-vision-preview` | 32K | Vision | ✅ |
| `moonshot-v1-128k-vision-preview` | 128K | Vision | ✅ |

**Aliases**:
- `kimi-k2` → `kimi-k2-0905-preview`
- `kimi-thinking` → `kimi-thinking-preview`

### 2. ZhipuAI GLM ✅ (Configured)
**Status**: Active and available
**Models**: 5 models total

| Model | Context Window | Type | Status |
|-------|---------------|------|--------|
| `glm-4.6` | 200K | Advanced Reasoning | ✅ |
| `glm-4.5` | 128K | General | ✅ |
| `glm-4.5-flash` | 128K | High-Speed | ✅ |
| `glm-4.5-air` | 128K | Lightweight | ✅ |
| `glm-4.5v` | 65K | Vision | ✅ |

**Aliases**:
- `glm-4.5-x` → `glm-4.5-air`

### 3. Other Providers (Not Configured)
- **OpenRouter** ❌ (requires OPENROUTER_API_KEY)
- **Custom/Local API** ❌ (requires CUSTOM_API_URL)
- **Google Gemini** ❌ (not configured)
- **OpenAI** ❌ (not configured)
- **X.AI** ❌ (not configured)

---

## 🛠️ Available Tools and Parameters

### Core Analysis Tools

#### 1. chat
**Purpose**: General chat and collaborative thinking
**Parameters**:
- `prompt` (required): Your question or instruction
- `model` (optional): Model name (default: auto)
- `stream` (optional): Enable streaming (default: false)
- `temperature` (optional): 0.0-1.0, default 0.6
- `files` (optional): Small files <5KB for context
- `images` (optional): Images for visual context
- `continuation_id` (optional): Continue conversation
- `use_websearch` (optional): Enable web search (default: true)
- `kimi_thinking` (optional): Enable extended thinking

**Example**:
```python
chat(
    prompt="What's the difference between list and tuple?",
    model="glm-4.6",
    temperature=0.3
)
```

#### 2. analyze
**Purpose**: Comprehensive code analysis with expert validation
**Parameters**:
- `step` (required): What to analyze or look for
- `step_number` (required): Current step (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): exploring/low/medium/high/very_high/almost_certain/certain
- `findings` (required): Summary of findings
- `analysis_type` (optional): general/architecture/performance/security/quality
- `relevant_files` (optional): Array of relevant file paths
- `files_checked` (optional): Array of files examined
- `issues_found` (optional): Issues identified with severity
- `relevant_context` (optional): Methods/functions involved
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `use_websearch` (optional): Enable web search (default: true)
- `model` (optional): Specific model to use
- `continuation_id` (optional): Continue analysis

**Workflow**: Must investigate code first, then call analyze with findings

#### 3. codereview
**Purpose**: Code review with expert validation
**Parameters**:
- `step` (required): What to review
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `review_type` (optional): full/security/performance/quick
- `severity_filter` (optional): all/critical/high/medium/low
- `standards` (optional): Coding standards to enforce
- `relevant_files` (optional): Files to review
- `files_checked` (optional): Files examined
- `focus_on` (optional): Specific aspects to focus on
- `hypothesis` (optional): Current theory
- `use_assistant_model` (optional): Use expert validation (default: true)
- `model` (optional): Specific model
- `continuation_id` (optional): Continue review

**Workflow**: Must review code first, then call codereview with findings

#### 4. debug
**Purpose**: Debugging and root cause analysis
**Parameters**:
- `step` (required): What to investigate
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `hypothesis` (required): Theory about the issue
- `relevant_files` (optional): Relevant files
- `files_checked` (optional): Files examined
- `issues_found` (optional): Issues identified
- `relevant_context` (optional): Methods/functions involved
- `images` (optional): Screenshots/visuals
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model
- `continuation_id` (optional): Continue investigation

**Workflow**: Must investigate bug first, then call debug with findings

#### 5. thinkdeep
**Purpose**: Investigation & reasoning with expert validation
**Parameters**:
- `step` (required): Current investigation step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): exploring/low/medium/high/very_high/almost_certain/certain
- `findings` (required): Key findings and evidence
- `problem_context` (optional): Additional context
- `focus_areas` (optional): Specific aspects to focus on
- `hypothesis` (optional): Current theory
- `relevant_context` (optional): Methods/functions involved
- `relevant_files` (optional): Relevant files
- `files_checked` (optional): Files examined
- `issues_found` (optional): Issues identified
- `images` (optional): Visual references
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `use_websearch` (optional): Enable web search (default: true)
- `model` (optional): Specific model
- `temperature` (optional): 0.0-1.0
- `continuation_id` (optional): Continue investigation

**Workflow**: Step-by-step investigation with expert validation

#### 6. consensus
**Purpose**: Multi-model consensus workflow
**Parameters**:
- `step` (required): The EXACT question to evaluate
- `step_number` (required): Current step
- `total_steps` (required): Total steps = number of models
- `next_step_required` (required): Boolean
- `models` (required): List of model configurations
- `findings` (required): Your own analysis
- `relevant_files` (optional): Relevant files
- `images` (optional): Visual references
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `continuation_id` (optional): Continue consensus

**Models Format**:
```python
[
    {"model": "glm-4.6", "stance": "for"},
    {"model": "kimi-k2-0905", "stance": "against"},
    {"model": "glm-4.5-flash", "stance": "neutral"}
]
```

### Specialized Tools

#### 7. refactor
**Purpose**: Refactoring analysis
**Parameters**:
- `step` (required): What to investigate for refactoring
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `refactor_type` (optional): codesmells/decompose/modernize/organization
- `focus_areas` (optional): Specific areas to focus
- `relevant_files` (optional): Files requiring refactoring
- `files_checked` (optional): Files examined
- `issues_found` (optional): Refactoring opportunities
- `style_guide_examples` (optional): Reference files for style
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

#### 8. secaudit
**Purpose**: Security audit
**Parameters**:
- `step` (required): What to audit
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `security_scope` (optional): Application context
- `audit_focus` (optional): owasp/compliance/infrastructure/dependencies/comprehensive
- `threat_level` (optional): low/medium/high/critical
- `compliance_requirements` (optional): SOC2, PCI DSS, HIPAA, etc.
- `severity_filter` (optional): all/critical/high/medium/low
- `relevant_files` (optional): Files to audit
- `files_checked` (optional): Files examined
- `issues_found` (optional): Security issues
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

#### 9. testgen
**Purpose**: Test generation
**Parameters**:
- `step` (required): What to test
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `hypothesis` (optional): Current theory
- `relevant_context` (optional): Methods/functions involved
- `relevant_files` (optional): Files needing tests
- `files_checked` (optional): Files examined
- `issues_found` (optional): Issues identified
- `images` (optional): Visual documentation
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

#### 10. docgen
**Purpose**: Documentation generation
**Parameters**:
- `step` (required): Current work step
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `findings` (required): Findings and evidence
- `total_files_to_document` (optional): Total files to document
- `num_files_documented` (optional): Number completed
- `update_existing` (optional): Update existing docs (default: true)
- `comments_on_complex_logic` (optional): Add inline comments (default: true)
- `document_flow` (optional): Include call flow info (default: true)
- `document_complexity` (optional): Include Big O analysis (default: true)
- `relevant_context` (optional): Methods/functions involved
- `relevant_files` (optional): Relevant files
- `issues_found` (optional): Issues found
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `continuation_id` (optional): Continue generation

#### 11. precommit
**Purpose**: Pre-commit validation
**Parameters**:
- `step` (required): What to validate
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `compare_to` (optional): Git ref to compare against
- `include_staged` (optional): Include staged changes (default: true)
- `include_unstaged` (optional): Include unstaged changes (default: true)
- `confidence` (optional): Confidence level
- `findings` (required): Summary of findings
- `focus_on` (optional): Specific aspects
- `hypothesis` (optional): Current theory
- `severity_filter` (optional): all/critical/high/medium/low
- `relevant_files` (optional): Files with changes
- `files_checked` (optional): Files examined
- `issues_found` (optional): Issues identified
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

#### 12. tracer
**Purpose**: Code tracing workflow
**Parameters**:
- `step` (required): Current work step
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `findings` (required): Key findings
- `target_description` (required): What to trace and why
- `trace_mode` (optional): ask/precision/dependencies
- `confidence` (optional): Confidence level
- `relevant_context` (optional): Methods/functions involved
- `relevant_files` (optional): Relevant files
- `files_checked` (optional): Files examined
- `images` (optional): Architecture diagrams
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

#### 13. planner
**Purpose**: Interactive sequential planning
**Parameters**:
- `step` (required): Current planning step
- `step_number` (required): Current step
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Boolean
- `continuation_id` (optional): Continue planning
- `is_branch_point` (optional): Is this a branch point
- `branch_id` (optional): Branch identifier
- `branch_from_step` (optional): Branching point step
- `revises_step_number` (optional): Revised step
- `is_step_revision` (optional): Is this a revision
- `more_steps_needed` (optional): More steps needed
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `model` (optional): Specific model

### File and Utility Tools

#### 14. smart_file_query
**Purpose**: Unified file upload and query
**Parameters**:
- `file_path` (required): Absolute Linux path
- `question` (required): Question about the file
- `provider` (optional): kimi/glm/auto (default: auto)
- `model` (optional): Specific model

**Requirements**:
- Files must be in mounted directories
- Accessible paths: `/mnt/project/EX-AI-MCP-Server/*`, `/mnt/project/Personal_AI_Agent/*`
- Files outside these directories NOT accessible
- Windows paths NOT supported (must use Linux paths)

#### 15. kimi_chat_with_tools
**Purpose**: Kimi chat with tools
**Parameters**:
- `messages` (required): Messages array or string
- `model` (optional): Model name (default: kimi-k2-turbo-preview)
- `stream` (optional): Enable streaming (default: false)
- `temperature` (optional): 0.0-1.0, default 0.6
- `tool_choice` (optional): auto or specific tool
- `tools` (optional): Array of tools
- `use_websearch` (optional): Enable web search (default: false)

#### 16. kimi_intent_analysis
**Purpose**: Intent classification
**Parameters**:
- `prompt` (required): User prompt to classify
- `context` (optional): Additional context
- `use_websearch` (optional): Enable web search (default: true)

**Returns**: JSON with needs_websearch, complexity, domain, recommended_provider, recommended_model, streaming_preferred

#### 17. kimi_manage_files
**Purpose**: File management
**Parameters**:
- `operation` (required): list/delete/cleanup_all/cleanup_orphaned/cleanup_expired
- `file_id` (optional): File ID (required for delete)
- `dry_run` (optional): Preview changes (default: false)
- `limit` (optional): Max files to list (default: 100)

#### 18. glm_payload_preview
**Purpose**: Preview GLM chat.completions payload
**Parameters**:
- `prompt` (required): The prompt
- `model` (optional): Model name (default: glm-4.5-flash)
- `system_prompt` (optional): System prompt
- `temperature` (optional): 0.3 (default)
- `tool_choice` (optional): Tool selection
- `tools` (optional): Array of tools
- `use_websearch` (optional): Enable web search (default: false)

### Status and Version Tools

#### 19. status
**Purpose**: Get server status
**Parameters**:
- `include_tools` (optional): Include tools in output (default: false)
- `doctor` (optional): Health check mode (default: false)
- `probe` (optional): Probe mode (default: false)
- `tail_lines` (optional): Last N lines (default: 30)

#### 20. version
**Purpose**: Get version info
**Parameters**: None

#### 21. listmodels
**Purpose**: List available models
**Parameters**: None

---

## 💡 Best Practices

### File Handling
- Use `files` parameter for small files <5KB
- Use `smart_file_query` for larger files
- Always use FULL absolute paths
- Windows paths: Convert to Linux paths (/mnt/project/...)

### Conversation Continuity
- Use `continuation_id` to maintain context across calls
- Most tools support continuation_id parameter

### Workflow Patterns
1. **Investigation First**: Always investigate/code review first
2. **Tool Escalation**: Call specialized tools (analyze, codereview, etc.) with findings
3. **Expert Validation**: Use `use_assistant_model=true` for comprehensive analysis
4. **Multi-step**: Break complex tasks into multiple steps with `step_number`

### Model Selection
- **GLM 4.6**: Complex reasoning, architecture analysis
- **GLM 4.5-flash**: Fast responses, simple tasks
- **Kimi K2-0905**: Code review, debugging
- **Kimi Thinking**: Extended reasoning, hypothesis testing
- **Auto**: Let system choose best model

### Web Search
- Default: enabled for most tools
- Use `use_websearch=false` for local-only analysis
- Useful for documentation, best practices, current info

---

## 🚀 Quick Start Examples

### Example 1: Code Review
```python
# Step 1: Review code
codereview(
    step="Review user authentication implementation",
    step_number=1,
    total_steps=2,
    next_step_required=true,
    findings="Found potential SQL injection in login_query()",
    review_type="security",
    relevant_files=["/mnt/project/app/auth.py"]
)

# Step 2: Call with findings
codereview(
    step="Complete security review based on findings",
    step_number=2,
    total_steps=2,
    next_step_required=false,
    findings="Security issues identified: SQL injection, weak password hashing",
    # ... other parameters
)
```

### Example 2: Multi-model Consensus
```python
consensus(
    step="Should we use microservices architecture for this project?",
    step_number=1,
    total_steps=3,
    next_step_required=true,
    models=[
        {"model": "glm-4.6", "stance": "for"},
        {"model": "kimi-k2-0905", "stance": "against"},
        {"model": "glm-4.5-flash", "stance": "neutral"}
    ],
    findings="My analysis: Project has 3 services, team of 5, needs scalability"
)
```

### Example 3: Deep Investigation
```python
thinkdeep(
    step="Investigate memory leak in production service",
    step_number=1,
    total_steps=3,
    next_step_required=true,
    findings="Service memory grows 100MB/hour, no clear pattern in logs",
    hypothesis="Memory leak in connection pooling",
    relevant_files=["/mnt/project/app/connection_pool.py"]
)
```

---

## 📝 Summary

**Total Tools**: 21
**Total Models**: 25 (14 Kimi + 5 GLM)
**Providers**: 2 configured (Kimi, GLM)
**Specializations**: Code review, debugging, security, refactoring, testing, documentation, planning

**Key Strengths**:
- Multi-provider redundancy (Kimi + GLM)
- Specialized workflow tools for different tasks
- Expert validation layer
- Continuation support for long-running analysis
- Web search integration

**Common Parameters**:
- `step`, `step_number`, `total_steps`, `next_step_required`
- `findings`, `relevant_files`, `files_checked`
- `confidence`, `use_assistant_model`, `model`
- `continuation_id` for ongoing conversations

---

**Document Version**: 1.0
**Last Updated**: 2025-11-03
