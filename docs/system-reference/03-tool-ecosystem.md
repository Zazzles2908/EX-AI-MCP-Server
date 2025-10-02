# Tool Ecosystem

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `01-system-overview.md`, `docs/guides/tool-selection-guide.md`

---

## Overview

The EX-AI-MCP-Server provides a comprehensive **tool ecosystem** with two categories of tools: **Simple Tools** (request/response) and **Workflow Tools** (multi-step with pause enforcement). All workflow tools include **agentic enhancements** for self-assessment, early termination, and dynamic step adjustment.

---

## Tool Categories

### Simple Tools (Request/Response)

**Characteristics:**
- Single request/response cycle
- No multi-step workflow
- Immediate results
- No pause enforcement

**Available Tools:**
- `chat` - General conversation with web search
- `thinkdeep` - Multi-stage investigation
- `planner` - Sequential planning
- `consensus` - Multi-model consensus
- `challenge` - Critical analysis

### Workflow Tools (Multi-Step with Pause Enforcement)

**Characteristics:**
- Multi-step investigation process
- Pause enforcement between steps
- Agentic enhancements (self-assessment, early termination, dynamic steps)
- Structured findings and evidence tracking

**Available Tools:**
- `analyze` - Comprehensive code analysis
- `debug` - Root cause analysis
- `codereview` - Systematic code review
- `precommit` - Pre-commit validation
- `refactor` - Refactoring analysis
- `testgen` - Test generation
- `tracer` - Code tracing
- `secaudit` - Security audit
- `docgen` - Documentation generation

---

## Simple Tools

### chat_EXAI-WS

**Purpose:** General conversation and collaborative thinking

**Use Cases:**
- Bouncing ideas during analysis
- Getting second opinions
- Collaborative brainstorming
- Validating checklists and approaches
- Exploring alternatives
- Explanations and comparisons

**Key Parameters:**
- `prompt` (required): Your question or idea
- `use_websearch` (optional): Enable web search (default: true)
- `model` (optional): Model to use (default: auto)
- `temperature` (optional): Response creativity (0-1, default: 0.5)
- `thinking_mode` (optional): Thinking depth (minimal, low, medium, high, max)
- `files` (optional): Files for context (absolute paths)
- `images` (optional): Images for visual context (absolute paths or base64)

**Example:**
```json
{
  "prompt": "What are the best practices for implementing streaming in Python?",
  "use_websearch": true,
  "model": "auto",
  "temperature": 0.5
}
```

**Web Search Integration:**
- Automatically triggered by query content
- No manual search required
- Integrated into responses
- Configurable via `use_websearch` parameter

---

### thinkdeep_EXAI-WS

**Purpose:** Multi-stage investigation and reasoning

**Use Cases:**
- Complex problem analysis
- Architecture decisions
- Performance challenges
- Security analysis
- Systematic hypothesis testing
- Expert validation

**Key Parameters:**
- `step` (required): Current investigation step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Important findings from this step
- `hypothesis` (optional): Current theory about the issue
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `thinking_mode` (optional): Thinking depth (low, medium, high, max)

**Workflow:**
1. Step 1: Describe investigation plan
2. STOP and investigate
3. Step 2+: Report findings with evidence
4. Continue until investigation complete
5. Receive expert analysis

**Example:**
```json
{
  "step": "Evaluate routing options for agentic system",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Identified three routing strategies: manager-first, direct routing, and hybrid approach",
  "confidence": "medium",
  "thinking_mode": "high"
}
```

---

### planner_EXAI-WS

**Purpose:** Sequential step-by-step planning

**Use Cases:**
- Breaking down complex tasks
- Project planning
- Implementation roadmaps
- Task sequencing
- Dependency mapping

**Key Parameters:**
- `step` (required): Current planning step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `is_step_revision` (optional): True if revising a previous step
- `revises_step_number` (optional): Which step is being revised
- `is_branch_point` (optional): True if branching from a previous step
- `branch_from_step` (optional): Which step is the branching point
- `branch_id` (optional): Identifier for the current branch

**Features:**
- Sequential thinking
- Deep reflection for complex plans
- Branching into alternative approaches
- Revisions of previous steps
- Dynamic step adjustment

**Example:**
```json
{
  "step": "Outline goals and constraints for zai-sdk upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

---

### consensus_EXAI-WS

**Purpose:** Multi-model consensus workflow

**Use Cases:**
- Complex decisions
- Architectural choices
- Feature proposals
- Technology evaluations
- Strategic planning

**Key Parameters:**
- `step` (required): Current consensus step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Total steps (equals number of models)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings from this step
- `models` (required): List of model configurations to consult

**Workflow:**
1. Step 1: Provide your own neutral analysis
2. Tool consults each model one by one
3. Track and synthesize perspectives
4. Final step: Present comprehensive consensus

**Example:**
```json
{
  "step": "Should we build a search component in SwiftUI for use in an AppKit app?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis suggests SwiftUI integration is feasible but has trade-offs",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

---

### challenge_EXAI-WS

**Purpose:** Critical analysis and truth-seeking

**Use Cases:**
- Preventing reflexive agreement
- Critical evaluation
- Truth verification
- Assumption challenging
- Reasoning validation

**Key Parameters:**
- `prompt` (required): The user's message to analyze critically

**Automatic Invocation:**
Automatically triggered when user:
- Questions or disagrees with previous statements
- Challenges assumptions
- Expresses confusion
- Believes an error was made
- Seeks justification

**Example:**
```json
{
  "prompt": "But I don't think that approach will work because..."
}
```

---

## Workflow Tools

### analyze_EXAI-WS

**Purpose:** Comprehensive code analysis

**Use Cases:**
- Code analysis
- Architectural assessment
- Performance evaluation
- Security analysis
- Maintainability review
- Pattern detection
- Strategic planning

**Key Parameters:**
- `step` (required): Current analysis step
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `analysis_type` (optional): Type of analysis (architecture, performance, security, quality, general)
- `confidence` (optional): Confidence level
- `files_checked` (optional): Files examined (absolute paths)
- `relevant_files` (optional): Files relevant to analysis (absolute paths)

**Workflow:**
1. Step 1: Describe analysis plan
2. STOP and investigate code
3. Step 2+: Report findings with evidence
4. Continue until analysis complete
5. Receive expert validation

---

### debug_EXAI-WS

**Purpose:** Root cause analysis and debugging

**Use Cases:**
- Complex bugs
- Mysterious errors
- Performance issues
- Race conditions
- Memory leaks
- Integration problems

**Key Parameters:**
- `step` (required): Current debugging step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `hypothesis` (required): Current theory about the issue
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)

**Workflow:**
1. Step 1: Describe the issue to investigate
2. STOP and investigate using tools
3. Step 2+: Report findings with evidence
4. Continue until root cause identified
5. Receive expert analysis

**Valid Hypotheses:**
- "No bug found - possible user misunderstanding"
- "Symptoms appear unrelated to any code issue"
- Concrete theories about failures or incorrect assumptions

---

### codereview_EXAI-WS

**Purpose:** Systematic code review

**Use Cases:**
- Comprehensive code review
- Security audits
- Performance analysis
- Architectural assessment
- Code quality evaluation
- Anti-pattern detection

**Key Parameters:**
- `step` (required): Current review step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `review_type` (optional): Type of review (full, security, performance, quick)
- `confidence` (optional): Confidence level
- `relevant_files` (optional): Files to review (absolute paths)

**Workflow:**
1. Step 1: Describe review plan and pass files in `relevant_files`
2. STOP and investigate code
3. Step 2+: Report findings with evidence
4. Continue until review complete
5. Receive expert analysis

**Focus Areas:**
- Code quality
- Security implications
- Performance concerns
- Architectural patterns
- Over-engineering
- Unnecessary complexity

---

### precommit_EXAI-WS

**Purpose:** Pre-commit validation

**Use Cases:**
- Comprehensive pre-commit validation
- Multi-repository analysis
- Security review
- Change impact assessment
- Completeness verification

**Key Parameters:**
- `step` (required): Current validation step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `path` (optional): Starting directory path (absolute)
- `compare_to` (optional): Git ref to compare against
- `include_staged` (optional): Include staged changes (default: true)
- `include_unstaged` (optional): Include unstaged changes (default: true)

**Workflow:**
1. Step 1: Describe validation plan
2. STOP and investigate git changes
3. Step 2+: Report findings with evidence
4. Continue until validation complete
5. Receive expert analysis

---

### refactor_EXAI-WS

**Purpose:** Refactoring analysis and recommendations

**Use Cases:**
- Comprehensive refactoring analysis
- Code smell detection
- Decomposition planning
- Modernization opportunities
- Organization improvements
- Maintainability enhancements

**Key Parameters:**
- `step` (required): Current refactoring step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `refactor_type` (optional): Type of refactoring (codesmells, decompose, modernize, organization)
- `confidence` (optional): Confidence level (exploring, incomplete, partial, complete)

**Workflow:**
1. Step 1: Describe refactoring plan
2. STOP and investigate code
3. Step 2+: Report findings with evidence
4. Continue until analysis complete
5. Receive expert analysis (unless confidence=complete)

---

### testgen_EXAI-WS

**Purpose:** Test generation with edge case coverage

**Use Cases:**
- Generating tests for code
- Creating test scaffolding
- Improving test coverage
- Edge case identification
- Framework-specific tests

**Key Parameters:**
- `step` (required): Current test generation step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `confidence` (optional): Confidence level

**Workflow:**
1. Step 1: Describe what to test (be specific!)
2. STOP and investigate code
3. Step 2+: Report findings with evidence
4. Continue until test plan complete
5. Receive expert analysis

**Best Practices:**
- Be specific about scope (target specific functions/classes/modules)
- Avoid vague requests like "test everything"
- Provide test pattern examples if available

---

### tracer_EXAI-WS

**Purpose:** Code tracing and dependency mapping

**Use Cases:**
- Method execution flow analysis
- Dependency mapping
- Call chain tracing
- Structural relationship analysis
- Architectural understanding
- Code comprehension

**Key Parameters:**
- `step` (required): Current tracing step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `target_description` (required): What to trace and WHY
- `trace_mode` (required): Type of tracing (precision, dependencies, ask)

**Trace Modes:**
- `ask` - Prompts you to choose between precision or dependencies
- `precision` - For methods/functions (execution flow, call chains, usage patterns)
- `dependencies` - For classes/modules (structural relationships, bidirectional dependencies)

---

### secaudit_EXAI-WS

**Purpose:** Security audit and vulnerability assessment

**Use Cases:**
- Comprehensive security assessment
- OWASP Top 10 analysis
- Compliance evaluation
- Vulnerability identification
- Threat modeling
- Security architecture review

**Key Parameters:**
- `step` (required): Current audit step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `audit_focus` (optional): Focus areas (owasp, compliance, infrastructure, dependencies, comprehensive)
- `threat_level` (optional): Threat level (low, medium, high, critical)

**Workflow:**
1. Step 1: Describe security audit plan and pass files in `relevant_files`
2. STOP and investigate security aspects
3. Step 2+: Report findings with evidence
4. Continue until audit complete
5. Receive expert security analysis

---

### docgen_EXAI-WS

**Purpose:** Documentation generation

**Use Cases:**
- Comprehensive documentation generation
- Code documentation analysis
- Complexity assessment
- Documentation modernization
- API documentation

**Key Parameters:**
- `step` (required): Current documentation step
- `step_number` (required): Current step number
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings
- `num_files_documented` (required): Number of files completely documented (starts at 0)
- `total_files_to_document` (required): Total files needing documentation
- `document_complexity` (optional): Include Big O analysis (default: true)
- `document_flow` (optional): Include call flow info (default: true)
- `update_existing` (optional): Update existing docs (default: true)
- `comments_on_complex_logic` (optional): Add inline comments (default: true)

**Critical Counters:**
- `num_files_documented`: Increment by 1 only when file is 100% documented
- `total_files_to_document`: Set in step 1 after discovering all files
- Cannot set `next_step_required=false` unless `num_files_documented == total_files_to_document`

---

## Agentic Enhancements (Phase 1)

### Self-Assessment

**Purpose:** Evaluate information sufficiency

**Implementation:**
```python
def assess_information_sufficiency(self) -> dict:
    """Assess if enough information has been gathered."""
    
    findings_sufficient = len(self.findings) >= self.MINIMUM_FINDINGS_LENGTH
    files_sufficient = len(self.relevant_files) >= self.MINIMUM_RELEVANT_FILES
    
    return {
        "sufficient": findings_sufficient and files_sufficient,
        "findings_length": len(self.findings),
        "files_count": len(self.relevant_files)
    }
```

**Configurable Thresholds:**
```python
MINIMUM_FINDINGS_LENGTH = 100  # Minimum characters in findings
MINIMUM_RELEVANT_FILES = 0     # Minimum relevant files
```

---

### Early Termination

**Purpose:** Complete investigation early when goals achieved

**Implementation:**
```python
def should_terminate_early(self) -> dict:
    """Determine if investigation can terminate early."""
    
    if self.confidence == "certain":
        return {"should_terminate": True, "reason": "High confidence achieved"}
    
    if self.step_number >= self.total_steps:
        return {"should_terminate": True, "reason": "All steps completed"}
    
    return {"should_terminate": False}
```

**Confidence Levels:**
- `exploring` - Just starting
- `low` - Early investigation
- `medium` - Some evidence
- `high` - Strong evidence
- `very_high` - Very strong evidence
- `almost_certain` - Nearly confirmed
- `certain` - 100% confidence (triggers early termination)

---

### Dynamic Step Adjustment

**Purpose:** Request additional steps mid-workflow

**Implementation:**
```python
def request_additional_steps(self, additional_steps: int, reason: str) -> dict:
    """Request additional investigation steps."""
    
    if additional_steps <= 0:
        raise ValueError("additional_steps must be positive")
    
    self.total_steps += additional_steps
    self.step_adjustment_history.append({
        "step_number": self.step_number,
        "additional_steps": additional_steps,
        "reason": reason
    })
    
    return {
        "new_total_steps": self.total_steps,
        "adjustment_history": self.step_adjustment_history
    }
```

**Usage:**
```json
{
  "step": "Need more investigation into authentication flow",
  "step_number": 3,
  "total_steps": 5,
  "next_step_required": true,
  "findings": "Discovered additional complexity requiring 2 more steps",
  "request_additional_steps": 2,
  "adjustment_reason": "Authentication flow more complex than initially estimated"
}
```

---

## Tool Selection Guide

### When to Use Which Tool

**General Questions:**
- Use `chat` for quick questions, brainstorming, explanations

**Complex Investigation:**
- Use `thinkdeep` for multi-stage investigation with expert validation

**Planning:**
- Use `planner` for breaking down complex tasks into steps

**Decision Making:**
- Use `consensus` for multi-model perspectives on decisions

**Code Analysis:**
- Use `analyze` for comprehensive code analysis
- Use `codereview` for systematic code review
- Use `refactor` for refactoring recommendations

**Debugging:**
- Use `debug` for root cause analysis and bug hunting

**Testing:**
- Use `testgen` for generating tests with edge case coverage

**Security:**
- Use `secaudit` for security audits and vulnerability assessment

**Documentation:**
- Use `docgen` for generating comprehensive documentation

**Code Understanding:**
- Use `tracer` for understanding execution flow and dependencies

**Pre-Commit:**
- Use `precommit` for validating changes before committing

---

**Next:** Read `04-features-and-capabilities.md` for detailed feature documentation

