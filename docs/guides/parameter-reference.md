# EXAI Tool Parameter Reference

**Version:** 1.0  
**Last Updated:** 2025-01-XX (Wave 1, Epic 1.2)  
**Purpose:** Comprehensive reference for all EXAI tool parameters

---

## Quick Reference: Common Parameters

| Parameter | Type | Required | Default | Used By | Description |
|-----------|------|----------|---------|---------|-------------|
| `prompt` | string | ✅ Yes | - | chat, challenge | Your question or request |
| `step` | string | ✅ Yes | - | All workflow tools | Current work step description |
| `step_number` | integer | ✅ Yes | - | All workflow tools | Current step index (starts at 1) |
| `total_steps` | integer | ✅ Yes | - | All workflow tools | Estimated total steps |
| `next_step_required` | boolean | ✅ Yes | - | All workflow tools | Whether more steps needed |
| `findings` | string | ✅ Yes | - | All workflow tools | Discoveries in this step |
| `model` | string | ❌ No | "auto" | All tools | Model selection |
| `continuation_id` | string | ❌ No | - | All tools | Continue previous conversation |
| `use_websearch` | boolean | ❌ No | true | chat | Enable web search |
| `temperature` | float | ❌ No | 0.5 | Most tools | Response creativity (0-1) |
| `thinking_mode` | string | ❌ No | varies | Most tools | Thinking depth |

---

## Common Parameters (Detailed)

### prompt (string, required)
**Used by:** `chat_EXAI-WS`, `challenge_EXAI-WS`  
**Description:** Your question, request, or statement to analyze  
**Type:** string  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: General question
{"prompt": "What are the trade-offs between zai-sdk v0.0.4 and v0.0.3.3?"}

// Example 2: Research request
{"prompt": "Explain the dual SDK/HTTP fallback pattern in glm_chat.py"}

// Example 3: Brainstorming
{"prompt": "What are alternative approaches to implementing streaming?"}
```

**Tips:**
- Be specific and provide context
- Include relevant background information
- Ask follow-up questions using continuation_id

---

### step (string, required)
**Used by:** All workflow tools (analyze, debug, thinkdeep, etc.)  
**Description:** Description of what you're investigating in this step  
**Type:** string  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: Analysis step
{"step": "Analyze provider architecture and identify design patterns"}

// Example 2: Debug step
{"step": "Investigate why streaming returns incomplete responses"}

// Example 3: Planning step
{"step": "Break down the zai-sdk v0.0.4 upgrade into implementation phases"}
```

**Tips:**
- Be descriptive and specific
- Explain WHAT you're doing and WHY
- Reference specific files/functions when relevant

---

### step_number (integer, required)
**Used by:** All workflow tools  
**Description:** Current step index in the investigation sequence  
**Type:** integer (minimum: 1)  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: First step
{"step_number": 1}

// Example 2: Third step
{"step_number": 3}

// Example 3: Final step
{"step_number": 5}
```

**Tips:**
- Always starts at 1 (not 0)
- Increment by 1 for each subsequent step
- Must be ≤ total_steps

---

### total_steps (integer, required)
**Used by:** All workflow tools  
**Description:** Your estimate for total steps needed  
**Type:** integer (minimum: 1)  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: Simple analysis (2 steps)
{"total_steps": 2}

// Example 2: Complex investigation (5 steps)
{"total_steps": 5}

// Example 3: Comprehensive audit (10 steps)
{"total_steps": 10}
```

**Tips:**
- Can be adjusted mid-workflow if needed
- Start conservative, increase if needed
- Consider complexity when estimating

---

### next_step_required (boolean, required)
**Used by:** All workflow tools  
**Description:** Whether another step is needed after this one  
**Type:** boolean  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: More steps needed
{"next_step_required": true}

// Example 2: Investigation complete
{"next_step_required": false}

// Example 3: Ready for expert validation
{"next_step_required": false, "confidence": "high"}
```

**Tips:**
- Set to `false` when investigation complete
- Set to `true` to continue multi-step workflow
- Consider confidence level when deciding

---

### findings (string, required)
**Used by:** All workflow tools  
**Description:** Summary of discoveries in this step  
**Type:** string  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: Analysis findings
{"findings": "Identified dual SDK/HTTP pattern in glm_chat.py lines 52-61. Pattern provides resilience but adds complexity."}

// Example 2: Debug findings
{"findings": "Web search executes (confirmed by tool_call_events) but results not integrated into response. Hypothesis: response truncation."}

// Example 3: Review findings
{"findings": "Code quality is good overall. Found 2 medium-severity issues: missing input validation and hardcoded timeout values."}
```

**Tips:**
- Be specific and evidence-based
- Include line numbers when referencing code
- Document both positive and negative findings

---

### model (string, optional)
**Used by:** All EXAI tools  
**Description:** Model selection for this request  
**Type:** string  
**Required:** ❌ No  
**Default:** "auto"

**Available Models:**
- `auto` - Server selects best model (recommended)
- `kimi-k2-0905-preview` - Kimi K2 (256K context, best for tool use/coding) **[RECOMMENDED]**
- `kimi-k2-0711-preview` - Kimi K2 earlier version (256K context)
- `glm-4.6` - GLM 4.6 (200K context, cost-effective)
- `glm-4.5` - GLM 4.5 (128K context)
- `glm-4.5-flash` - GLM 4.5 Flash (128K context, faster)
- `glm-4.5-air` - GLM 4.5 Air (128K context, lightweight)

**Examples:**
```json
// Example 1: Auto selection (recommended)
{"model": "auto"}

// Example 2: Specific Kimi K2 model (version pinned for stability)
{"model": "kimi-k2-0905-preview"}

// Example 3: Fast GLM model
{"model": "glm-4.5-flash"}
```

**Tips:**
- Use "auto" unless you have specific requirements
- Kimi K2 models: Best for tool use, coding, agentic workflows (256K context)
- GLM models: Best for web search, speed, cost optimization
- **Production:** Use version-pinned models (kimi-k2-0905-preview) not aliases (kimi-latest)
- GLM models: Better for web search and speed

---

### continuation_id (string, optional)
**Used by:** All EXAI tools  
**Description:** Continue a previous conversation thread  
**Type:** string (UUID format)  
**Required:** ❌ No  
**Default:** None

**Examples:**
```json
// Example 1: New conversation (no continuation_id)
{"prompt": "What is zai-sdk?"}

// Example 2: Continue conversation
{
  "prompt": "What about version 0.0.4?",
  "continuation_id": "39048d92-d30e-4cdb-b18a-dbf52e885b02"
}

// Example 3: Multi-turn workflow
{
  "step": "Continue analysis from previous step",
  "step_number": 2,
  "continuation_id": "fde1185b-127d-4f02-9689-74793f41a4fa"
}
```

**Tips:**
- Get continuation_id from previous response
- Maintains conversation context
- Useful for follow-up questions

---

### use_websearch (boolean, optional)
**Used by:** `chat_EXAI-WS`, workflow tools with web search support  
**Description:** Enable provider-native web browsing  
**Type:** boolean  
**Required:** ❌ No  
**Default:** true

**Examples:**
```json
// Example 1: Enable web search (default)
{"prompt": "What are GLM-4.6 features?", "use_websearch": true}

// Example 2: Disable web search
{"prompt": "Explain the code I just showed you", "use_websearch": false}

// Example 3: Research with web search
{"prompt": "Latest zai-sdk documentation", "use_websearch": true}
```

**Known Issues:**
- ⚠️ Web search may return incomplete results in chat_EXAI-WS
- ✅ Workaround: Use `web-search` tool directly for reliable results
- See troubleshooting.md for details

---

### temperature (float, optional)
**Used by:** Most EXAI tools  
**Description:** Response creativity level (0.0 = deterministic, 1.0 = creative)  
**Type:** float (0.0 to 1.0)  
**Required:** ❌ No  
**Default:** 0.5 (varies by tool)

**Examples:**
```json
// Example 1: Deterministic (factual responses)
{"temperature": 0.0}

// Example 2: Balanced (default)
{"temperature": 0.5}

// Example 3: Creative (brainstorming)
{"temperature": 0.8}
```

**Tips:**
- Lower (0.0-0.3): Factual, consistent, deterministic
- Medium (0.4-0.6): Balanced, general use
- Higher (0.7-1.0): Creative, brainstorming, varied

---

### thinking_mode (string, optional)
**Used by:** Most workflow tools  
**Description:** Thinking depth (affects reasoning quality and speed)  
**Type:** string  
**Required:** ❌ No  
**Default:** Varies by tool (usually "medium")

**Options:**
- `minimal` - 0.5% of model max (fastest)
- `low` - 8% of model max
- `medium` - 33% of model max (default)
- `high` - 67% of model max
- `max` - 100% of model max (deepest reasoning)

**Examples:**
```json
// Example 1: Quick analysis
{"thinking_mode": "low"}

// Example 2: Standard analysis (default)
{"thinking_mode": "medium"}

// Example 3: Complex problem requiring deep reasoning
{"thinking_mode": "high"}

// Example 4: Critical system requiring exhaustive analysis
{"thinking_mode": "max"}
```

**Tips:**
- Higher modes = deeper reasoning but slower
- Use "low" for simple tasks
- Use "high" or "max" for complex problems

---

## File Path Parameters

### relevant_files (array of strings, optional but recommended)
**Used by:** All code analysis tools  
**Description:** Files to analyze, review, or reference  
**Type:** array of strings (ABSOLUTE PATHS ONLY)  
**Required:** ❌ No (but highly recommended for code tools)  
**Default:** Empty array

**CRITICAL PATH REQUIREMENTS:**
- ✅ MUST be FULL absolute paths
- ✅ Windows: `c:\\Project\\EX-AI-MCP-Server\\src\\file.py`
- ✅ Linux: `/home/user/project/src/file.py`
- ❌ NO relative paths: `src/file.py`, `./file.py`, `.`
- ❌ NO environment variables: `%USERPROFILE%`, `~`
- ❌ NO current directory: `.`, `..`

**Examples:**
```json
// Example 1: Single file (Windows)
{
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}

// Example 2: Multiple files (Windows)
{
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\kimi_chat.py"
  ]
}

// Example 3: Single file (Linux)
{
  "relevant_files": ["/home/user/EX-AI-MCP-Server/src/providers/glm_chat.py"]
}
```

**Common Mistakes:**
```json
// ❌ WRONG: Relative path
{"relevant_files": ["src/providers/glm_chat.py"]}

// ❌ WRONG: Current directory
{"relevant_files": ["."]}

// ❌ WRONG: Relative with ./
{"relevant_files": ["./src/providers/glm_chat.py"]}

// ✅ CORRECT: Full absolute path
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]}
```

**Error Message:**
If you use relative paths, you'll see:
```
All file paths must be FULL absolute paths. Invalid path: 'src/providers'
```

**How to Fix:**
1. Get workspace root: `c:\Project\EX-AI-MCP-Server`
2. Append your relative path: `src\providers\glm_chat.py`
3. Combine: `c:\Project\EX-AI-MCP-Server\src\providers\glm_chat.py`
4. Escape backslashes in JSON: `c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py`

---

### files_checked (array of strings, optional)
**Used by:** All workflow tools  
**Description:** Files examined during investigation (tracking)  
**Type:** array of strings (ABSOLUTE PATHS)  
**Required:** ❌ No  
**Default:** Empty array

**Examples:**
```json
// Example 1: Track examined files
{
  "files_checked": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\kimi_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\server.py"
  ]
}
```

**Tips:**
- Include even files ruled out (tracks exploration)
- Helps avoid re-examining same files
- Useful for progress tracking

---

### path (string, optional)
**Used by:** `precommit_EXAI-WS`  
**Description:** Starting directory for git repository search  
**Type:** string (ABSOLUTE PATH)  
**Required:** ❌ No  
**Default:** Current working directory

**Examples:**
```json
// Example 1: Specific project directory
{"path": "c:\\Project\\EX-AI-MCP-Server"}

// Example 2: Multi-repo parent directory
{"path": "c:\\Project"}
```

---

## Analysis-Specific Parameters

### analysis_type (string, optional)
**Used by:** `analyze_EXAI-WS`  
**Description:** Type of analysis to perform  
**Type:** string  
**Required:** ❌ No  
**Default:** "general"

**Options:**
- `architecture` - Architecture assessment
- `performance` - Performance evaluation
- `security` - Security analysis
- `quality` - Code quality review
- `general` - General analysis

**Examples:**
```json
// Example 1: Architecture analysis
{"analysis_type": "architecture"}

// Example 2: Performance analysis
{"analysis_type": "performance"}

// Example 3: General analysis (default)
{"analysis_type": "general"}
```

---

### confidence (string, optional)
**Used by:** Most workflow tools  
**Description:** Your confidence level in findings  
**Type:** string  
**Required:** ❌ No  
**Default:** Varies by tool

**Options:**
- `exploring` - Just starting analysis
- `low` - Early investigation
- `medium` - Some evidence gathered
- `high` - Strong evidence
- `very_high` - Very strong evidence
- `almost_certain` - Nearly complete confidence
- `certain` - 100% confidence (disables expert validation)

**Examples:**
```json
// Example 1: Early investigation
{"confidence": "low"}

// Example 2: Strong evidence
{"confidence": "high"}

// Example 3: Complete confidence (skip validation)
{"confidence": "certain"}
```

**Warning:**
- Using `"certain"` disables expert validation
- Only use when 100% confident
- When in doubt, use `"very_high"` or `"almost_certain"`

---

## Review-Specific Parameters

### review_type (string, optional)
**Used by:** `codereview_EXAI-WS`  
**Description:** Type of code review to perform  
**Type:** string  
**Required:** ❌ No  
**Default:** "full"

**Options:**
- `full` - Comprehensive review
- `security` - Security-focused review
- `performance` - Performance-focused review
- `quick` - Quick review

**Examples:**
```json
// Example 1: Full review (default)
{"review_type": "full"}

// Example 2: Security focus
{"review_type": "security"}

// Example 3: Quick review
{"review_type": "quick"}
```

---

### audit_focus (string, optional)
**Used by:** `secaudit_EXAI-WS`  
**Description:** Primary security focus area  
**Type:** string  
**Required:** ❌ No  
**Default:** "comprehensive"

**Options:**
- `owasp` - OWASP Top 10 analysis
- `compliance` - Compliance evaluation
- `infrastructure` - Infrastructure security
- `dependencies` - Dependency vulnerabilities
- `comprehensive` - All areas

**Examples:**
```json
// Example 1: OWASP focus
{"audit_focus": "owasp"}

// Example 2: Comprehensive audit (default)
{"audit_focus": "comprehensive"}
```

---

## Refactoring Parameters

### refactor_type (string, optional)
**Used by:** `refactor_EXAI-WS`  
**Description:** Type of refactoring analysis  
**Type:** string  
**Required:** ❌ No  
**Default:** "codesmells"

**Options:**
- `codesmells` - Code smell detection
- `decompose` - Decomposition planning
- `modernize` - Modernization opportunities
- `organization` - Organization improvements

**Examples:**
```json
// Example 1: Code smells (default)
{"refactor_type": "codesmells"}

// Example 2: Decomposition
{"refactor_type": "decompose"}
```

---

## Documentation Parameters

### document_complexity (boolean, optional)
**Used by:** `docgen_EXAI-WS`  
**Description:** Include algorithmic complexity (Big O) analysis  
**Type:** boolean  
**Required:** ❌ No  
**Default:** true

**Examples:**
```json
// Example 1: Include complexity (default)
{"document_complexity": true}

// Example 2: Skip complexity
{"document_complexity": false}
```

---

### document_flow (boolean, optional)
**Used by:** `docgen_EXAI-WS`  
**Description:** Include call flow and dependency information  
**Type:** boolean  
**Required:** ❌ No  
**Default:** true

**Examples:**
```json
// Example 1: Include flow (default)
{"document_flow": true}

// Example 2: Skip flow
{"document_flow": false}
```

---

### num_files_documented (integer, required for docgen)
**Used by:** `docgen_EXAI-WS`  
**Description:** Counter for files completed (prevents premature completion)  
**Type:** integer (minimum: 0)  
**Required:** ✅ Yes (for docgen)  
**Default:** None

**Examples:**
```json
// Example 1: Starting documentation
{"num_files_documented": 0, "total_files_to_document": 5}

// Example 2: Progress tracking
{"num_files_documented": 3, "total_files_to_document": 5}

// Example 3: All files complete
{"num_files_documented": 5, "total_files_to_document": 5}
```

**Rules:**
- Start at 0
- Increment by 1 when file 100% documented
- Cannot set next_step_required=false unless num_files_documented == total_files_to_document

---

## Tracing Parameters

### trace_mode (string, required for tracer)
**Used by:** `tracer_EXAI-WS`  
**Description:** Type of tracing to perform  
**Type:** string  
**Required:** ✅ Yes (for tracer)  
**Default:** None

**Options:**
- `ask` - Prompt user to choose mode
- `precision` - Execution flow tracing (for methods/functions)
- `dependencies` - Structural relationships (for classes/modules)

**Examples:**
```json
// Example 1: Ask for mode
{"trace_mode": "ask"}

// Example 2: Precision tracing
{"trace_mode": "precision"}

// Example 3: Dependency mapping
{"trace_mode": "dependencies"}
```

---

### target_description (string, required for tracer)
**Used by:** `tracer_EXAI-WS`  
**Description:** What to trace and WHY  
**Type:** string  
**Required:** ✅ Yes (for tracer)  
**Default:** None

**Examples:**
```json
// Example 1: Method tracing
{"target_description": "Trace chat_with_tools function to understand tool calling flow"}

// Example 2: Dependency mapping
{"target_description": "Map dependencies of Provider class to understand architecture"}
```

---

## Consensus Parameters

### models (array of objects, required for consensus)
**Used by:** `consensus_EXAI-WS`  
**Description:** Models to consult with optional stances  
**Type:** array of objects  
**Required:** ✅ Yes (for consensus)  
**Default:** None

**Object Structure:**
```json
{
  "model": "string (required)",
  "stance": "for|against|neutral (optional, default: neutral)",
  "stance_prompt": "string (optional)"
}
```

**Examples:**
```json
// Example 1: Three models, different stances
{
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}

// Example 2: Same model, different stances
{
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "kimi-k2-0905-preview", "stance": "against"}
  ]
}
```

**Rules:**
- Each model + stance combination must be unique
- total_steps = number of models
- Same model can be used with different stances

---

## Web Search Parameters

### query (string, required for web-search)
**Used by:** `web-search` tool  
**Description:** Search query  
**Type:** string  
**Required:** ✅ Yes  
**Default:** None

**Examples:**
```json
// Example 1: Specific query
{"query": "zai-sdk version 0.0.4 features"}

// Example 2: Exact phrase
{"query": "\"GLM-4.6\" specifications"}

// Example 3: Multiple terms
{"query": "api.z.ai endpoints documentation"}
```

---

### num_results (integer, optional)
**Used by:** `web-search` tool  
**Description:** Number of results to return  
**Type:** integer (1-10)  
**Required:** ❌ No  
**Default:** 5

**Examples:**
```json
// Example 1: Default results
{"num_results": 5}

// Example 2: More results
{"num_results": 10}

// Example 3: Quick search
{"num_results": 3}
```

---

## Advanced Parameters

### use_assistant_model (boolean, optional)
**Used by:** All workflow tools  
**Description:** Use assistant model for expert analysis  
**Type:** boolean  
**Required:** ❌ No  
**Default:** true

**Examples:**
```json
// Example 1: Enable expert validation (default)
{"use_assistant_model": true}

// Example 2: Skip expert validation
{"use_assistant_model": false}
```

**Tips:**
- Set to false to skip expert analysis
- Useful when you want faster results
- Default is true for comprehensive validation

---

### hypothesis (string, optional)
**Used by:** `debug_EXAI-WS`, `thinkdeep_EXAI-WS`  
**Description:** Current theory about the issue  
**Type:** string  
**Required:** ❌ No  
**Default:** None

**Examples:**
```json
// Example 1: Debug hypothesis
{"hypothesis": "Response truncation before search results are synthesized"}

// Example 2: Investigation theory
{"hypothesis": "Dual SDK/HTTP pattern provides resilience but adds complexity"}
```

---

### issues_found (array of objects, optional)
**Used by:** All workflow tools  
**Description:** Issues identified during investigation  
**Type:** array of objects  
**Required:** ❌ No  
**Default:** Empty array

**Object Structure:**
```json
{
  "severity": "critical|high|medium|low",
  "description": "string"
}
```

**Examples:**
```json
// Example 1: Security issues
{
  "issues_found": [
    {"severity": "high", "description": "Missing input validation on user input"},
    {"severity": "medium", "description": "Hardcoded timeout values"}
  ]
}
```

---

## Parameter Validation Rules

### Required Parameters
All workflow tools require:
- `step` (string)
- `step_number` (integer, ≥ 1)
- `total_steps` (integer, ≥ 1)
- `next_step_required` (boolean)
- `findings` (string)

### Optional But Recommended
- `relevant_files` (for code analysis tools)
- `model` (defaults to "auto")
- `confidence` (helps with validation decisions)

### Path Requirements
**CRITICAL:** All file paths MUST be absolute
- ✅ `c:\\Project\\EX-AI-MCP-Server\\src\\file.py`
- ❌ `src/file.py`
- ❌ `./file.py`
- ❌ `.`

### Type Requirements
- Strings: Use quotes `"value"`
- Integers: No quotes `123`
- Booleans: `true` or `false` (lowercase, no quotes)
- Arrays: `["item1", "item2"]`
- Objects: `{"key": "value"}`

---

## 30+ Complete Examples

### Example 1: Simple Chat
```json
{
  "prompt": "What is zai-sdk?"
}
```

### Example 2: Chat with Web Search
```json
{
  "prompt": "What are the latest features in GLM-4.6?",
  "use_websearch": true,
  "model": "auto"
}
```

### Example 3: Chat with Specific Model
```json
{
  "prompt": "Explain the dual SDK/HTTP pattern",
  "use_websearch": false,
  "model": "kimi-k2-0905-preview"
}
```

### Example 4: Continue Conversation
```json
{
  "prompt": "What about version 0.0.4?",
  "continuation_id": "39048d92-d30e-4cdb-b18a-dbf52e885b02"
}
```

### Example 5: Web Search
```json
{
  "query": "zai-sdk version 0.0.4 changelog",
  "num_results": 5
}
```

### Example 6: Challenge Assumption
```json
{
  "prompt": "We should upgrade to zai-sdk v0.0.4 immediately without testing"
}
```

### Example 7: Analyze Architecture
```json
{
  "step": "Analyze provider architecture and design patterns",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial assessment of provider structure",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "analysis_type": "architecture",
  "model": "auto"
}
```

### Example 8: Code Review
```json
{
  "step": "Review glm_chat.py for code quality and security",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern implementation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "review_type": "full",
  "confidence": "medium"
}
```

### Example 9: Security Audit
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

### Example 10: Pre-Commit Validation
```json
{
  "step": "Validate all staged changes before committing",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing git diff and impact assessment",
  "path": "c:\\Project\\EX-AI-MCP-Server",
  "include_staged": true,
  "include_unstaged": false
}
```

### Example 11: Debug Investigation
```json
{
  "step": "Investigate why web search returns incomplete results",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Search executes but results not integrated",
  "hypothesis": "Response truncation before synthesis",
  "confidence": "medium",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\tools\\chat.py"]
}
```

### Example 12: Deep Investigation
```json
{
  "step": "Investigate optimal architecture for zai-sdk integration",
  "step_number": 1,
  "total_steps": 4,
  "next_step_required": true,
  "findings": "Analyzing dual SDK/HTTP pattern trade-offs",
  "hypothesis": "Dual pattern provides resilience but adds complexity",
  "thinking_mode": "high"
}
```

### Example 13: Refactor Analysis
```json
{
  "step": "Identify code smells in server.py",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing structure for decomposition opportunities",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\server.py"],
  "refactor_type": "decompose",
  "confidence": "incomplete"
}
```

### Example 14: Test Generation
```json
{
  "step": "Generate tests for User.login() with edge cases",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Identified authentication edge cases",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\auth\\user.py"],
  "thinking_mode": "medium"
}
```

### Example 15: Documentation Generation
```json
{
  "step": "Document all functions in glm_chat.py",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing function signatures and complexity",
  "num_files_documented": 0,
  "total_files_to_document": 1,
  "document_complexity": true,
  "document_flow": true
}
```

### Example 16: Code Tracing (Precision)
```json
{
  "step": "Trace execution flow of chat_with_tools function",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Mapping call chain from entry to provider",
  "target_description": "Understand tool calling flow through system",
  "trace_mode": "precision"
}
```

### Example 17: Code Tracing (Dependencies)
```json
{
  "step": "Map dependencies of Provider class",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing structural relationships",
  "target_description": "Understand provider architecture dependencies",
  "trace_mode": "dependencies"
}
```

### Example 18: Planning
```json
{
  "step": "Plan implementation of zai-sdk v0.0.4 upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

### Example 19: Consensus (3 Models)
```json
{
  "step": "Should we upgrade to zai-sdk v0.0.4 now?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis of upgrade timing",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

### Example 20: High Temperature (Creative)
```json
{
  "prompt": "Brainstorm alternative approaches to streaming",
  "temperature": 0.8,
  "use_websearch": false
}
```

### Example 21: Low Temperature (Factual)
```json
{
  "prompt": "What is the exact syntax for zai-sdk chat completions?",
  "temperature": 0.0,
  "use_websearch": true
}
```

### Example 22: Minimal Thinking Mode
```json
{
  "step": "Quick check of file structure",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Basic structure looks good",
  "thinking_mode": "minimal"
}
```

### Example 23: Max Thinking Mode
```json
{
  "step": "Comprehensive security analysis of authentication system",
  "step_number": 1,
  "total_steps": 10,
  "next_step_required": true,
  "findings": "Beginning exhaustive security audit",
  "thinking_mode": "max",
  "audit_focus": "comprehensive"
}
```

### Example 24: Multiple Files Analysis
```json
{
  "step": "Analyze all provider implementations",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Comparing provider patterns",
  "relevant_files": [
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\kimi_chat.py",
    "c:\\Project\\EX-AI-MCP-Server\\src\\providers\\provider_base.py"
  ]
}
```

### Example 25: Skip Expert Validation
```json
{
  "step": "Quick syntax check",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Syntax is correct",
  "use_assistant_model": false
}
```

### Example 26: With Issues Found
```json
{
  "step": "Security review complete",
  "step_number": 3,
  "total_steps": 3,
  "next_step_required": false,
  "findings": "Found 2 security issues",
  "issues_found": [
    {"severity": "high", "description": "Missing input validation"},
    {"severity": "medium", "description": "Weak password requirements"}
  ],
  "confidence": "high"
}
```

### Example 27: Certain Confidence (Skip Validation)
```json
{
  "step": "Final validation complete",
  "step_number": 5,
  "total_steps": 5,
  "next_step_required": false,
  "findings": "All checks passed, no issues found",
  "confidence": "certain"
}
```

### Example 28: Pre-Commit with Comparison
```json
{
  "step": "Compare current branch with main",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing differences from main branch",
  "path": "c:\\Project\\EX-AI-MCP-Server",
  "compare_to": "main"
}
```

### Example 29: Refactor with Style Guide
```json
{
  "step": "Refactor following project style guide",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Analyzing code against style patterns",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\utils\\helpers.py"],
  "style_guide_examples": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"],
  "refactor_type": "organization"
}
```

### Example 30: Documentation Progress Tracking
```json
{
  "step": "Continue documenting provider files",
  "step_number": 3,
  "total_steps": 5,
  "next_step_required": true,
  "findings": "Completed glm_chat.py and kimi_chat.py documentation",
  "num_files_documented": 2,
  "total_files_to_document": 5,
  "document_complexity": true
}
```

### Example 31: Consensus with Custom Stance
```json
{
  "step": "Evaluate database migration approach",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial assessment of migration strategies",
  "models": [
    {
      "model": "kimi-k2-0905-preview",
      "stance": "for",
      "stance_prompt": "Argue for immediate migration with minimal downtime"
    },
    {
      "model": "glm-4.6",
      "stance": "against",
      "stance_prompt": "Argue for gradual migration with extensive testing"
    }
  ]
}
```

### Example 32: Images for Visual Context
```json
{
  "step": "Review UI component architecture",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Analyzing component structure and design patterns",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\ui\\components.py"],
  "images": ["c:\\Project\\EX-AI-MCP-Server\\docs\\diagrams\\architecture.png"]
}
```

---

## Common Mistakes and Solutions

### Mistake 1: Using Relative Paths
**Error:**
```json
{"relevant_files": ["src/providers/glm_chat.py"]}
```

**Solution:**
```json
{"relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]}
```

---

### Mistake 2: Wrong Type for Boolean
**Error:**
```json
{"next_step_required": "true"}  // String, not boolean
```

**Solution:**
```json
{"next_step_required": true}  // Boolean
```

---

### Mistake 3: Missing Required Parameters
**Error:**
```json
{
  "step": "Analyze code",
  "step_number": 1
  // Missing: total_steps, next_step_required, findings
}
```

**Solution:**
```json
{
  "step": "Analyze code",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial analysis findings"
}
```

---

### Mistake 4: Using "certain" Prematurely
**Error:**
```json
{
  "confidence": "certain"  // Skips expert validation
}
```

**Solution:**
```json
{
  "confidence": "very_high"  // Still gets expert validation
}
```

---

### Mistake 5: Forgetting to Escape Backslashes
**Error:**
```json
{"path": "c:\Project\EX-AI-MCP-Server"}  // Invalid JSON
```

**Solution:**
```json
{"path": "c:\\Project\\EX-AI-MCP-Server"}  // Escaped backslashes
```

---

## Next Steps

- **Tool Selection:** See tool-selection-guide.md for choosing the right tool
- **Web Search:** See web-search-guide.md for web search best practices
- **Examples:** See query-examples.md for 20+ working examples
- **Troubleshooting:** See troubleshooting.md for common issues

---

**Document Status:** ✅ COMPLETE (Task 1.2)  
**Validation:** Pending codereview_EXAI-WS  
**Total Examples:** 32+ complete parameter examples

