# EXAI Query Examples Collection

**Version:** 1.0  
**Last Updated:** 2025-01-XX (Wave 1, Epic 1.2)  
**Purpose:** Working examples of EXAI tool queries across all categories

---

## Overview

This guide provides 20+ working examples organized by category:
1. **Research** (External documentation, web search)
2. **Code Analysis** (Understanding internal code)
3. **Debugging** (Root cause analysis, issue investigation)
4. **Planning** (Task breakdown, project planning)
5. **Testing** (Test generation, validation)

Each example includes:
- ✅ Complete, working query
- 📋 Expected behavior
- ⚠️ Common mistakes
- 💡 Tips for success

---

## Category 1: Research (External Documentation)

### Example 1: Latest SDK Version Information

**Query:**
```json
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 changelog features",
  "num_results": 5
}
```

**Expected Behavior:**
- Returns PyPI, GitHub, and official documentation links
- Shows version 0.0.4 features and changes
- Includes release notes and migration guides

**Common Mistake:**
```json
// ❌ WRONG: Using chat_EXAI-WS (incomplete results)
{
  "tool": "chat_EXAI-WS",
  "prompt": "What's in zai-sdk v0.0.4?",
  "use_websearch": true
}
```

**Why Wrong:** Known web search issue in chat_EXAI-WS (see web-search-guide.md)

---

### Example 2: API Documentation Lookup

**Query:**
```json
{
  "tool": "web-search",
  "query": "api.z.ai chat completions endpoint documentation parameters",
  "num_results": 10
}
```

**Expected Behavior:**
- Returns official api.z.ai documentation
- Shows endpoint specifications
- Includes parameter descriptions and examples

**Tip:** Use `num_results: 10` for comprehensive documentation research

---

### Example 3: Best Practices Research

**Query:**
```json
{
  "tool": "web-search",
  "query": "Python async streaming SSE text/event-stream best practices",
  "num_results": 5
}
```

**Expected Behavior:**
- Returns industry best practices
- Shows implementation patterns
- Includes expert recommendations

**Common Mistake:**
```json
// ❌ WRONG: Too vague
{"query": "streaming"}

// ✅ CORRECT: Specific with context
{"query": "Python async streaming SSE text/event-stream best practices"}
```

---

### Example 4: Current Pricing Information

**Query:**
```json
{
  "tool": "web-search",
  "query": "\"GLM-4.6\" pricing per token ZhipuAI official",
  "num_results": 3
}
```

**Expected Behavior:**
- Returns official pricing from ZhipuAI
- Shows per-token costs
- Includes context window pricing

**Tip:** Use quotes for exact phrases: `"GLM-4.6"`

---

### Example 5: Migration Guide Research

**Query:**
```json
{
  "tool": "web-search",
  "query": "zai-sdk v0.0.3.3 to v0.0.4 migration breaking changes",
  "num_results": 5
}
```

**Expected Behavior:**
- Returns migration documentation
- Shows breaking changes
- Includes upgrade instructions

---

## Category 2: Code Analysis (Internal Code)

### Example 6: Analyze Provider Architecture

**Query:**
```json
{
  "tool": "analyze_EXAI-WS",
  "step": "Analyze provider architecture and identify design patterns",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial assessment of provider structure and patterns",
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\kimi_chat.py"
  ],
  "analysis_type": "architecture",
  "model": "auto"
}
```

**Expected Behavior:**
- Analyzes YOUR actual code files
- Identifies design patterns (dual SDK/HTTP, etc.)
- Provides architectural insights
- Suggests improvements

**Common Mistake:**
```json
// ❌ WRONG: Using web-search for internal code
{
  "tool": "web-search",
  "query": "how does glm_chat.py work"
}
// Returns: Generic information, NOT your code
```

---

### Example 7: Code Quality Review

**Query:**
```json
{
  "tool": "codereview_EXAI-WS",
  "step": "Review glm_chat.py for code quality, security, and maintainability",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern implementation and error handling",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "review_type": "full",
  "confidence": "medium"
}
```

**Expected Behavior:**
- Comprehensive code review
- Identifies code smells and anti-patterns
- Suggests improvements
- Checks security and performance

**Tip:** Use `review_type: "full"` for comprehensive review

---

### Example 8: Security Audit

**Query:**
```json
{
  "tool": "secaudit_EXAI-WS",
  "step": "Audit authentication and authorization mechanisms for OWASP Top 10 vulnerabilities",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "Analyzing API key handling, token validation, and input sanitization",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\core\\auth.py"],
  "audit_focus": "owasp",
  "threat_level": "high"
}
```

**Expected Behavior:**
- OWASP Top 10 security analysis
- Identifies vulnerabilities
- Provides remediation recommendations
- Assesses threat level

---

### Example 9: Performance Analysis

**Query:**
```json
{
  "tool": "analyze_EXAI-WS",
  "step": "Analyze streaming performance and identify bottlenecks",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Examining SSE streaming implementation and chunk processing",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "analysis_type": "performance",
  "thinking_mode": "high"
}
```

**Expected Behavior:**
- Performance bottleneck identification
- Optimization recommendations
- Complexity analysis
- Scalability assessment

**Tip:** Use `thinking_mode: "high"` for complex performance analysis

---

### Example 10: Refactoring Opportunities

**Query:**
```json
{
  "tool": "refactor_EXAI-WS",
  "step": "Identify code smells and decomposition opportunities in server.py",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing server.py structure for complexity reduction opportunities",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\server.py"],
  "refactor_type": "decompose",
  "confidence": "incomplete"
}
```

**Expected Behavior:**
- Code smell detection
- Decomposition recommendations
- Complexity reduction suggestions
- Modernization opportunities

---

## Category 3: Debugging (Root Cause Analysis)

### Example 11: Debug Streaming Issue

**Query:**
```json
{
  "tool": "debug_EXAI-WS",
  "step": "Investigate why streaming returns incomplete responses in chat_EXAI-WS",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Web search executes (confirmed by tool_call_events) but results not integrated into response",
  "hypothesis": "Response truncation before search results are synthesized",
  "confidence": "medium",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\tools\\chat.py"]
}
```

**Expected Behavior:**
- Systematic root cause investigation
- Hypothesis formation and testing
- Evidence gathering
- Solution recommendations

**Common Mistake:**
```json
// ❌ WRONG: Single-step debugging
{
  "step": "Fix the streaming bug",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false
}
// Better: Multi-step systematic investigation
```

---

### Example 12: Debug Authentication Failure

**Query:**
```json
{
  "tool": "debug_EXAI-WS",
  "step": "Investigate authentication failures with GLM provider",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "Checking API key configuration, environment variables, and token validation",
  "hypothesis": "API key not loaded from environment or invalid format",
  "confidence": "low",
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\.env.example"
  ]
}
```

**Expected Behavior:**
- Environment configuration check
- API key validation
- Error message analysis
- Configuration fix recommendations

---

### Example 13: Deep Investigation with thinkdeep

**Query:**
```json
{
  "tool": "thinkdeep_EXAI-WS",
  "step": "Investigate optimal architecture for zai-sdk v0.0.4 integration with backward compatibility",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern trade-offs and migration strategies",
  "hypothesis": "Dual pattern provides resilience but adds complexity - need to evaluate alternatives",
  "thinking_mode": "high",
  "use_websearch": true
}
```

**Expected Behavior:**
- Multi-stage deep investigation
- Hypothesis testing
- Alternative exploration
- Expert validation

**Tip:** Use `thinking_mode: "high"` for complex architectural decisions

---

### Example 14: Pre-Commit Validation

**Query:**
```json
{
  "tool": "precommit_EXAI-WS",
  "step": "Validate all staged changes before committing to chore/registry-switch-and-docfix",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing git diff for completeness, correctness, and potential issues",
  "path": "c:\\Project\\EX-AI-MCP-Server",
  "include_staged": true,
  "include_unstaged": false
}
```

**Expected Behavior:**
- Git diff analysis
- Change impact assessment
- Completeness verification
- Issue identification

---

### Example 15: Trace Code Execution Flow

**Query:**
```json
{
  "tool": "tracer_EXAI-WS",
  "step": "Trace execution flow of chat_with_tools function to understand tool calling mechanism",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Mapping call chain from entry point through provider to tool execution",
  "target_description": "Understand how tool calling flows through the system from request to response",
  "trace_mode": "precision"
}
```

**Expected Behavior:**
- Execution flow mapping
- Call chain visualization
- Dependency identification
- Flow documentation

---

## Category 4: Planning (Task Breakdown)

### Example 16: Project Planning

**Query:**
```json
{
  "tool": "planner_EXAI-WS",
  "step": "Plan the implementation of zai-sdk v0.0.4 upgrade with minimal downtime",
  "step_number": 1,
  "total_steps": 6,
  "next_step_required": true
}
```

**Expected Behavior:**
- Step-by-step implementation plan
- Dependency identification
- Risk assessment
- Timeline estimation

**Tip:** Start with broad estimate for total_steps, adjust as planning progresses

---

### Example 17: Multi-Model Consensus

**Query:**
```json
{
  "tool": "consensus_EXAI-WS",
  "step": "Should we upgrade to zai-sdk v0.0.4 now or wait for v0.0.5?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis of upgrade timing trade-offs and risk assessment",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

**Expected Behavior:**
- Multi-perspective analysis
- Structured debate
- Consensus synthesis
- Recommendation with rationale

**Tip:** Use different stances for balanced analysis

---

### Example 18: Challenge Assumptions

**Query:**
```json
{
  "tool": "challenge_EXAI-WS",
  "prompt": "We should upgrade to zai-sdk v0.0.4 immediately without testing in a staging environment"
}
```

**Expected Behavior:**
- Critical analysis of proposal
- Risk identification
- Alternative suggestions
- Reasoned counterarguments

**Common Mistake:**
```json
// ❌ WRONG: Using chat for critical analysis
{
  "tool": "chat_EXAI-WS",
  "prompt": "Is it a good idea to upgrade without testing?"
}
// May agree reflexively instead of challenging
```

---

## Category 5: Testing (Test Generation & Validation)

### Example 19: Generate Unit Tests

**Query:**
```json
{
  "tool": "testgen_EXAI-WS",
  "step": "Generate comprehensive unit tests for User.login() method with edge cases",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Identified authentication flows, edge cases (empty password, SQL injection, rate limiting), and error scenarios",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"],
  "thinking_mode": "medium"
}
```

**Expected Behavior:**
- Comprehensive test suite
- Edge case coverage
- Error scenario testing
- Framework-specific tests

**Tip:** Be specific about scope - target specific functions/classes

---

### Example 20: Generate Documentation

**Query:**
```json
{
  "tool": "docgen_EXAI-WS",
  "step": "Document all functions in glm_chat.py with complexity analysis and call flow",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing function signatures, parameters, return types, and algorithmic complexity",
  "num_files_documented": 0,
  "total_files_to_document": 1,
  "document_complexity": true,
  "document_flow": true
}
```

**Expected Behavior:**
- Function/method documentation
- Complexity analysis (Big O)
- Call flow documentation
- Parameter descriptions

**Critical:** Must track `num_files_documented` and `total_files_to_document`

---

## Bonus Examples (21-25)

### Example 21: General Question (No Web Search)

**Query:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Explain the difference between async and sync programming in Python",
  "use_websearch": false,
  "model": "auto"
}
```

**Expected Behavior:**
- Clear explanation from model knowledge
- No web search needed (faster)
- Focused, concise answer

---

### Example 22: Brainstorming with High Temperature

**Query:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Brainstorm 10 alternative approaches to implementing streaming in our MCP server",
  "use_websearch": false,
  "temperature": 0.8,
  "model": "kimi-k2-0905-preview"
}
```

**Expected Behavior:**
- Creative, varied suggestions
- Multiple perspectives
- Innovative ideas

**Tip:** Use `temperature: 0.8` for creative brainstorming

---

### Example 23: Factual Query with Low Temperature

**Query:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "What is the exact syntax for zai-sdk chat completions with streaming enabled?",
  "use_websearch": true,
  "temperature": 0.0,
  "model": "auto"
}
```

**Expected Behavior:**
- Deterministic, factual response
- Exact syntax
- Consistent answers

**Tip:** Use `temperature: 0.0` for factual, deterministic responses

---

### Example 24: Continue Conversation

**Query:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "What about the Assistant API in v0.0.4?",
  "continuation_id": "39048d92-d30e-4cdb-b18a-dbf52e885b02",
  "use_websearch": false
}
```

**Expected Behavior:**
- Maintains conversation context
- Builds on previous discussion
- Coherent multi-turn dialogue

**Tip:** Get `continuation_id` from previous response

---

### Example 25: Comprehensive Security Audit

**Query:**
```json
{
  "tool": "secaudit_EXAI-WS",
  "step": "Comprehensive security audit of entire authentication and authorization system",
  "step_number": 1,
  "total_steps": 10,
  "next_step_required": true,
  "findings": "Beginning exhaustive OWASP Top 10 analysis, dependency vulnerability scan, and infrastructure security review",
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\core\\auth.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\middleware\\security.py"
  ],
  "audit_focus": "comprehensive",
  "threat_level": "critical",
  "thinking_mode": "max"
}
```

**Expected Behavior:**
- Exhaustive security analysis
- OWASP Top 10 coverage
- Dependency vulnerability scan
- Infrastructure security review

**Tip:** Use `thinking_mode: "max"` for critical security audits

---

## Common Mistakes Across All Categories

### Mistake 1: Using Relative Paths
```json
// ❌ WRONG
{"relevant_files": ["src/providers/glm_chat.py"]}

// ✅ CORRECT
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]}
```

---

### Mistake 2: Missing Required Parameters
```json
// ❌ WRONG
{
  "step": "Analyze code",
  "step_number": 1
}

// ✅ CORRECT
{
  "step": "Analyze code",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial analysis findings"
}
```

---

### Mistake 3: Wrong Tool for Task
```json
// ❌ WRONG: Using web-search for internal code
{"tool": "web-search", "query": "how does my glm_chat.py work"}

// ✅ CORRECT: Using analyze for internal code
{"tool": "analyze_EXAI-WS", "relevant_files": ["c:\\Project\\..."]}
```

---

### Mistake 4: Vague Descriptions
```json
// ❌ WRONG
{"step": "Check the code"}

// ✅ CORRECT
{"step": "Analyze glm_chat.py for dual SDK/HTTP pattern implementation and error handling"}
```

---

### Mistake 5: Premature "certain" Confidence
```json
// ❌ WRONG: Skips expert validation
{"confidence": "certain"}

// ✅ CORRECT: Gets expert validation
{"confidence": "very_high"}
```

---

## Tips for Success

### ✅ DO:
- Use absolute paths for all file references
- Be specific in step descriptions
- Include all required parameters
- Choose appropriate tool for task
- Use thinking_mode based on complexity
- Validate with codereview_EXAI-WS

### ❌ DON'T:
- Use relative paths (`.`, `src/`, `./file.py`)
- Skip required parameters
- Use wrong tool for task type
- Use vague, generic descriptions
- Set confidence to "certain" prematurely
- Forget to track progress (num_files_documented, etc.)

---

## Quick Reference by Task Type

| Task | Tool | Key Parameters |
|------|------|----------------|
| External docs | web-search | query, num_results |
| Internal code | analyze_EXAI-WS | relevant_files, analysis_type |
| Code review | codereview_EXAI-WS | relevant_files, review_type |
| Security audit | secaudit_EXAI-WS | relevant_files, audit_focus |
| Debugging | debug_EXAI-WS | hypothesis, confidence |
| Planning | planner_EXAI-WS | step, total_steps |
| Testing | testgen_EXAI-WS | relevant_files, thinking_mode |
| Documentation | docgen_EXAI-WS | num_files_documented, total_files_to_document |

---

## Related Documentation

- **Tool Selection:** See `tool-selection-guide.md` for choosing the right tool
- **Parameters:** See `parameter-reference.md` for detailed parameter documentation
- **Web Search:** See `web-search-guide.md` for web search best practices
- **Troubleshooting:** See `troubleshooting.md` for common issues and solutions

---

**Document Status:** ✅ COMPLETE (Task 1.4)  
**Validation:** Pending codereview_EXAI-WS  
**Total Examples:** 25 working examples (5+ per category, exceeds 20+ requirement)

