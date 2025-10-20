# EXAI Tool Selection Guide

**Version:** 1.0  
**Last Updated:** 2025-01-XX (Wave 1, Epic 1.2)  
**Purpose:** Help you choose the right EXAI tool for your task

---

## Quick Reference

| Task Type | Recommended Tool | Alternative |
|-----------|------------------|-------------|
| General questions | `chat_EXAI-WS` | - |
| Web research | `web-search` | `chat_EXAI-WS` (with workaround) |
| Code analysis | `analyze_EXAI-WS` | `codereview_EXAI-WS` |
| Debugging | `debug_EXAI-WS` | `thinkdeep_EXAI-WS` |
| Code review | `codereview_EXAI-WS` | `analyze_EXAI-WS` |
| Security audit | `secaudit_EXAI-WS` | `codereview_EXAI-WS` |
| Pre-commit check | `precommit_EXAI-WS` | `codereview_EXAI-WS` |
| Refactoring | `refactor_EXAI-WS` | `analyze_EXAI-WS` |
| Test generation | `testgen_EXAI-WS` | `codereview_EXAI-WS` |
| Documentation | `docgen_EXAI-WS` | `analyze_EXAI-WS` |
| Code tracing | `tracer_EXAI-WS` | `analyze_EXAI-WS` |
| Planning | `planner_EXAI-WS` | `chat_EXAI-WS` |
| Multi-model consensus | `consensus_EXAI-WS` | `chat_EXAI-WS` |
| Challenge assumptions | `challenge_EXAI-WS` | `chat_EXAI-WS` |

---

## Decision Tree

```
START: What do you need to do?
│
├─ Need information/research?
│  ├─ External documentation? → web-search
│  ├─ General question? → chat_EXAI-WS
│  └─ Code understanding? → analyze_EXAI-WS
│
├─ Need to analyze code?
│  ├─ General analysis? → analyze_EXAI-WS
│  ├─ Security focus? → secaudit_EXAI-WS
│  ├─ Quality review? → codereview_EXAI-WS
│  ├─ Pre-commit check? → precommit_EXAI-WS
│  └─ Trace execution? → tracer_EXAI-WS
│
├─ Need to modify code?
│  ├─ Refactor existing? → refactor_EXAI-WS
│  ├─ Generate tests? → testgen_EXAI-WS
│  └─ Add documentation? → docgen_EXAI-WS
│
├─ Need to debug?
│  ├─ Complex issue? → debug_EXAI-WS
│  └─ Need deep analysis? → thinkdeep_EXAI-WS
│
├─ Need to plan?
│  ├─ Step-by-step planning? → planner_EXAI-WS
│  └─ Multi-perspective? → consensus_EXAI-WS
│
└─ Need to challenge ideas?
   └─ Critical analysis? → challenge_EXAI-WS
```

---

## Tool Categories

### 1. Simple Tools (Direct Interaction)

#### chat_EXAI-WS
**Purpose:** General-purpose conversational AI for questions, brainstorming, and collaborative thinking

**Use for:**
- General questions and explanations
- Brainstorming ideas
- Getting second opinions
- Collaborative problem-solving
- Comparing approaches

**Parameters:**
- `prompt` (required): Your question or request
- `use_websearch` (optional, default: true): Enable web search
- `model` (optional, default: auto): Model selection
- `temperature` (optional, default: 0.5): Response creativity
- `thinking_mode` (optional): Thinking depth
- `continuation_id` (optional): Continue previous conversation

**Example:**
```json
{
  "prompt": "What are the trade-offs between using zai-sdk v0.0.4 vs v0.0.3.3?",
  "use_websearch": false,
  "model": "auto"
}
```

**When NOT to use:**
- ❌ External documentation research (use `web-search` instead)
- ❌ Code analysis (use `analyze_EXAI-WS` instead)
- ❌ Debugging (use `debug_EXAI-WS` instead)

**Known Issues:**
- Web search may not return complete results (see troubleshooting guide)
- Use `web-search` tool directly for reliable research

---

#### web-search
**Purpose:** Search the web for current information and documentation

**Use for:**
- External documentation research
- Current events and news
- API documentation lookup
- Best practices research
- Technology comparisons

**Parameters:**
- `query` (required): Search query
- `num_results` (optional, default: 5): Number of results (1-10)

**Example:**
```json
{
  "query": "zai-sdk version 0.0.4 features and API endpoints",
  "num_results": 5
}
```

**When NOT to use:**
- ❌ Internal code analysis (use `analyze_EXAI-WS` instead)
- ❌ General questions (use `chat_EXAI-WS` instead)

**Tips:**
- Be specific in queries
- Use quotes for exact phrases
- Combine with `chat_EXAI-WS` for synthesis

---

#### challenge_EXAI-WS
**Purpose:** Prevent reflexive agreement and force critical analysis

**Use for:**
- Challenging assumptions
- Critical evaluation of proposals
- Questioning decisions
- Seeking alternative perspectives
- Avoiding confirmation bias

**Parameters:**
- `prompt` (required): Statement or proposal to challenge

**Example:**
```json
{
  "prompt": "We should upgrade to zai-sdk v0.0.4 immediately without testing."
}
```

**When to use:**
- When you disagree with a recommendation
- When questioning assumptions
- When seeking critical analysis
- When avoiding groupthink

**When NOT to use:**
- ❌ For general questions (use `chat_EXAI-WS` instead)
- ❌ When you want agreement (defeats the purpose)

---

### 2. Analysis Tools (Code Understanding)

#### analyze_EXAI-WS
**Purpose:** Comprehensive code analysis with expert validation

**Use for:**
- Architecture assessment
- Performance evaluation
- Code quality review
- Strategic planning
- Pattern detection

**Parameters:**
- `step` (required): Current analysis step
- `step_number` (required): Step index (starts at 1)
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Discoveries in this step
- `relevant_files` (optional): Files to analyze (ABSOLUTE PATHS)
- `analysis_type` (optional): architecture/performance/security/quality/general
- `confidence` (optional): Confidence level
- `model` (optional, default: auto): Model selection

**Example:**
```json
{
  "step": "Analyze the provider architecture and identify improvement opportunities",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial assessment of provider structure",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "analysis_type": "architecture"
}
```

**When NOT to use:**
- ❌ External SDK research (use `web-search` instead)
- ❌ Security-focused audit (use `secaudit_EXAI-WS` instead)
- ❌ Pre-commit validation (use `precommit_EXAI-WS` instead)

**Critical Requirements:**
- ⚠️ ALL file paths must be FULL absolute paths
- ⚠️ Use `c:\\Project\\...` format (double backslashes in JSON)
- ⚠️ Do NOT use relative paths (`.`, `src/`, `./file.py`)

---

#### codereview_EXAI-WS
**Purpose:** Comprehensive code review with quality, security, and maintainability focus

**Use for:**
- Code quality evaluation
- Security review
- Performance analysis
- Maintainability assessment
- Anti-pattern detection

**Parameters:**
- `step` (required): Current review step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Discoveries in this step
- `relevant_files` (optional): Files to review (ABSOLUTE PATHS)
- `review_type` (optional): full/security/performance/quick
- `confidence` (optional): Confidence level

**Example:**
```json
{
  "step": "Review glm_chat.py for code quality and security issues",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern implementation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "review_type": "full"
}
```

**When NOT to use:**
- ❌ Pre-commit validation (use `precommit_EXAI-WS` instead)
- ❌ Security-only audit (use `secaudit_EXAI-WS` instead)

---

#### secaudit_EXAI-WS
**Purpose:** Comprehensive security audit with OWASP Top 10 focus

**Use for:**
- Security vulnerability assessment
- OWASP Top 10 analysis
- Compliance evaluation
- Threat modeling
- Security architecture review

**Parameters:**
- `step` (required): Current audit step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Security discoveries
- `relevant_files` (optional): Files to audit (ABSOLUTE PATHS)
- `audit_focus` (optional): owasp/compliance/infrastructure/dependencies/comprehensive
- `threat_level` (optional): low/medium/high/critical

**Example:**
```json
{
  "step": "Audit authentication and authorization mechanisms",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "Analyzing API key handling and token validation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\core\\auth.py"],
  "audit_focus": "owasp",
  "threat_level": "high"
}
```

**When NOT to use:**
- ❌ General code review (use `codereview_EXAI-WS` instead)
- ❌ Performance analysis (use `analyze_EXAI-WS` instead)

---

#### precommit_EXAI-WS
**Purpose:** Pre-commit validation with change impact assessment

**Use for:**
- Pre-commit validation
- Change impact assessment
- Completeness verification
- Multi-repository analysis
- Git diff analysis

**Parameters:**
- `step` (required): Current validation step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Validation discoveries
- `path` (optional): Starting directory (ABSOLUTE PATH)
- `compare_to` (optional): Git ref to compare against
- `include_staged` (optional, default: true): Include staged changes
- `include_unstaged` (optional, default: true): Include unstaged changes

**Example:**
```json
{
  "step": "Validate all changes before committing to chore/registry-switch-and-docfix",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing staged changes in src/providers/",
  "path": "c:\\Project\\EX-AI-MCP-Server",
  "include_staged": true,
  "include_unstaged": false
}
```

**When NOT to use:**
- ❌ General code review (use `codereview_EXAI-WS` instead)
- ❌ When no git changes exist

---

### 3. Modification Tools (Code Generation)

#### refactor_EXAI-WS
**Purpose:** Refactoring analysis and recommendations

**Use for:**
- Code smell detection
- Decomposition planning
- Modernization opportunities
- Organization improvements
- Complexity reduction

**Parameters:**
- `step` (required): Current refactoring step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Refactoring opportunities
- `relevant_files` (optional): Files to refactor (ABSOLUTE PATHS)
- `refactor_type` (optional): codesmells/decompose/modernize/organization
- `confidence` (optional): incomplete/partial/complete

**Example:**
```json
{
  "step": "Identify code smells and refactoring opportunities in server.py",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing server.py structure for decomposition opportunities",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\server.py"],
  "refactor_type": "decompose"
}
```

---

#### testgen_EXAI-WS
**Purpose:** Comprehensive test generation with edge case coverage

**Use for:**
- Unit test generation
- Integration test creation
- Edge case identification
- Test scaffolding
- Coverage improvement

**Parameters:**
- `step` (required): Current test generation step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Test scenarios identified
- `relevant_files` (optional): Files to test (ABSOLUTE PATHS)

**Example:**
```json
{
  "step": "Generate tests for User.login() method with edge cases",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Identified authentication edge cases and error scenarios",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"]
}
```

**Tips:**
- Be specific about scope (target specific functions/classes)
- Provide existing test examples for pattern matching
- Use higher thinking_mode for complex systems

---

#### docgen_EXAI-WS
**Purpose:** Comprehensive documentation generation

**Use for:**
- Code documentation
- API documentation
- Complexity analysis
- Documentation modernization

**Parameters:**
- `step` (required): Current documentation step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Documentation needs identified
- `num_files_documented` (required): Files completed (starts at 0)
- `total_files_to_document` (required): Total files to document
- `document_complexity` (optional, default: true): Include Big O analysis
- `document_flow` (optional, default: true): Include call flow

**Example:**
```json
{
  "step": "Document all functions in glm_chat.py with complexity analysis",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing function signatures and complexity",
  "num_files_documented": 0,
  "total_files_to_document": 1,
  "document_complexity": true
}
```

---

### 4. Debugging Tools

#### debug_EXAI-WS
**Purpose:** Root cause analysis and debugging

**Use for:**
- Complex bugs
- Mysterious errors
- Performance issues
- Race conditions
- Integration problems

**Parameters:**
- `step` (required): Current debugging step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Debug discoveries
- `hypothesis` (optional): Current theory about the issue
- `relevant_files` (optional): Files involved (ABSOLUTE PATHS)
- `confidence` (optional): exploring/low/medium/high/very_high/almost_certain/certain

**Example:**
```json
{
  "step": "Investigate why web search returns incomplete results in chat_EXAI-WS",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Search executes but results not integrated into response",
  "hypothesis": "Response truncation before search results are synthesized",
  "confidence": "medium"
}
```

---

#### thinkdeep_EXAI-WS
**Purpose:** Multi-stage deep investigation and reasoning

**Use for:**
- Complex problem analysis
- Architecture decisions
- Performance challenges
- Security analysis
- Systematic investigation

**Parameters:**
- `step` (required): Current investigation step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Investigation discoveries
- `hypothesis` (optional): Current theory
- `confidence` (optional): Confidence level

**Example:**
```json
{
  "step": "Investigate optimal architecture for zai-sdk v0.0.4 integration",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern trade-offs",
  "hypothesis": "Dual pattern provides resilience but adds complexity"
}
```

---

### 5. Planning Tools

#### planner_EXAI-WS
**Purpose:** Step-by-step planning with deep reflection

**Use for:**
- Task breakdown
- Project planning
- Sequential thinking
- Plan revision
- Alternative exploration

**Parameters:**
- `step` (required): Current planning step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed

**Example:**
```json
{
  "step": "Plan the implementation of zai-sdk v0.0.4 upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

---

#### consensus_EXAI-WS
**Purpose:** Multi-model consensus with structured analysis

**Use for:**
- Complex decisions
- Architecture choices
- Feature proposals
- Technology evaluations
- Strategic planning

**Parameters:**
- `step` (required): Question/proposal for consensus
- `step_number` (required): Step index
- `total_steps` (required): Number of models to consult
- `next_step_required` (required): Whether more models needed
- `findings` (required): Analysis from this step
- `models` (required): List of models with stances

**Example:**
```json
{
  "step": "Should we upgrade to zai-sdk v0.0.4 now or wait for v0.0.5?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis of upgrade timing trade-offs",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

---

### 6. Specialized Tools

#### tracer_EXAI-WS
**Purpose:** Code execution flow and dependency tracing

**Use for:**
- Method execution flow
- Dependency mapping
- Call chain tracing
- Structural relationships
- Code comprehension

**Parameters:**
- `step` (required): Current tracing step
- `step_number` (required): Step index
- `total_steps` (required): Estimated total steps
- `next_step_required` (required): Whether more steps needed
- `findings` (required): Tracing discoveries
- `target_description` (required): What to trace and why
- `trace_mode` (required): precision/dependencies/ask

**Example:**
```json
{
  "step": "Trace execution flow of chat_with_tools function",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Mapping call chain from entry point to provider",
  "target_description": "Understand how tool calling flows through the system",
  "trace_mode": "precision"
}
```

---

## Common Scenarios

### Scenario 1: Research External Documentation
**Task:** Find information about zai-sdk v0.0.4 features

**Recommended Tool:** `web-search`

**Example:**
```json
{
  "query": "zai-sdk version 0.0.4 features API endpoints changelog",
  "num_results": 5
}
```

**Why NOT chat_EXAI-WS?** Web search issue (incomplete results)

---

### Scenario 2: Understand Internal Code
**Task:** Understand how the provider architecture works

**Recommended Tool:** `analyze_EXAI-WS`

**Example:**
```json
{
  "step": "Analyze provider architecture and design patterns",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial assessment of provider structure",
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\kimi_chat.py"
  ],
  "analysis_type": "architecture"
}
```

**Why NOT web-search?** Internal code, not external documentation

---

### Scenario 3: Debug Complex Issue
**Task:** Figure out why streaming isn't working

**Recommended Tool:** `debug_EXAI-WS`

**Example:**
```json
{
  "step": "Investigate streaming failure in GLM provider",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Checking GLM_STREAM_ENABLED and provider configuration",
  "hypothesis": "Environment variable not set or provider not supporting streaming",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
```

---

### Scenario 4: Pre-Commit Validation
**Task:** Validate changes before committing

**Recommended Tool:** `precommit_EXAI-WS`

**Example:**
```json
{
  "step": "Validate all staged changes for completeness and correctness",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing git diff and impact assessment",
  "path": "c:\\Project\\EX-AI-MCP-Server",
  "include_staged": true,
  "include_unstaged": false
}
```

---

### Scenario 5: Generate Tests
**Task:** Create tests for authentication module

**Recommended Tool:** `testgen_EXAI-WS`

**Example:**
```json
{
  "step": "Generate comprehensive tests for User.login() with edge cases",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Identified authentication flows and error scenarios",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"]
}
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Using analyze for External Research
**Wrong:**
```json
{
  "tool": "analyze_EXAI-WS",
  "step": "Analyze zai-sdk v0.0.4 documentation"
}
```

**Right:**
```json
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 documentation"
}
```

**Why:** analyze is for internal code, not external documentation

---

### ❌ Anti-Pattern 2: Using Relative Paths
**Wrong:**
```json
{
  "relevant_files": ["src/providers/glm_chat.py"]
}
```

**Right:**
```json
{
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
```

**Why:** All paths must be FULL absolute paths

---

### ❌ Anti-Pattern 3: Using chat for Code Review
**Wrong:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Review this code for security issues: [code]"
}
```

**Right:**
```json
{
  "tool": "secaudit_EXAI-WS",
  "step": "Audit authentication code for security vulnerabilities",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"]
}
```

**Why:** Specialized tools provide deeper, systematic analysis

---

### ❌ Anti-Pattern 4: Skipping Step-by-Step Investigation
**Wrong:**
```json
{
  "tool": "debug_EXAI-WS",
  "step": "Fix the bug",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false
}
```

**Right:**
```json
{
  "tool": "debug_EXAI-WS",
  "step": "Investigate symptoms and gather evidence",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true
}
```

**Why:** Systematic investigation yields better results

---

### ❌ Anti-Pattern 5: Using chat_EXAI-WS for Web Search
**Wrong:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Search for GLM-4.6 specifications",
  "use_websearch": true
}
```

**Right:**
```json
{
  "tool": "web-search",
  "query": "GLM-4.6 model specifications context window pricing"
}
```

**Why:** Web search issue in chat tool (see troubleshooting guide)

---

## Tips for Success

1. **Match Tool to Task:** Use the decision tree to select the right tool
2. **Use Absolute Paths:** Always use full paths (c:\\Project\\...)
3. **Be Specific:** Provide detailed context in step descriptions
4. **Iterate Systematically:** Use multi-step workflows for complex tasks
5. **Validate Results:** Use codereview_EXAI-WS to validate outputs
6. **Check Troubleshooting:** See troubleshooting.md for common issues

---

## Next Steps

- **Parameter Reference:** See parameter-reference.md for detailed parameter documentation
- **Web Search Guide:** See web-search-guide.md for web search best practices
- **Query Examples:** See query-examples.md for 20+ working examples
- **Troubleshooting:** See troubleshooting.md for common issues and solutions

---

**Document Status:** ✅ COMPLETE (Task 1.1)  
**Validation:** Pending codereview_EXAI-WS

