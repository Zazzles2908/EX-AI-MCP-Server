# EXAI Tool Testing: Schema vs Documentation Analysis
**Date:** 2025-11-02
**Purpose:** Identify contradictions between tool schemas (what I see) and documentation (what docs say)
**Status:** 🔄 IN PROGRESS

---

## 🚨 CRITICAL ISSUE TO INVESTIGATE LATER

### Supabase Messages Table Storing Wrong Data

**Discovery Date:** 2025-11-02
**Severity:** HIGH
**Status:** ⏳ DEFERRED (finish tool testing first)

**Problem:**
- Messages table is storing **internal tool execution data** (step_info, expert_analysis JSON)
- NOT storing actual **conversation between user and assistant**
- This is **audit trail of tool calls**, not **conversation persistence**

**Evidence from Database:**
```json
{
  "step_info": {
    "step": "",
    "step_number": 1,
    "total_steps": 1
  }
}
```

**What SHOULD Be Stored:**
- User's actual question/request
- Assistant's actual response to user
- Conversation context and flow

**Impact:**
- Conversation persistence not working as intended
- Audit trail is tool-centric, not conversation-centric
- Cannot reconstruct actual user conversations from database

**Next Steps (After Tool Testing):**
1. Investigate where conversation messages should be stored
2. Determine if this is by design or a bug
3. Fix storage logic to capture actual conversations
4. Update schema if needed

---

## 🎯 TESTING METHODOLOGY

### Two Sources of Truth:

1. **SCHEMA (What I See)** - Tool descriptions and parameters shown when calling functions
2. **DOCS (What Docs Say)** - AGENT_CAPABILITIES.md & SYSTEM_CAPABILITIES_OVERVIEW.md

### Testing Process:

For each tool:
1. **Document what SCHEMA shows me** (parameters, descriptions, requirements)
2. **Document what DOCS tell me** (usage patterns, workflow, requirements)
3. **Identify contradictions** (where schema ≠ docs)
4. **Follow docs' story** (use tool as docs describe)
5. **Record actual behavior** (does it work as docs say or as schema says?)
6. **Classify issues** (contradiction, hidden requirement, not working, missing info)

---

## 📊 TOOL-BY-TOOL ANALYSIS

### TOOL 1: chat_EXAI-WS

#### What SCHEMA Shows Me:
```
Tool: chat_EXAI-WS
Description: "GENERAL CHAT & COLLABORATIVE THINKING - Use the AI model as your thinking partner!"

Parameters:
- prompt (REQUIRED): "You MUST provide a thorough, expressive question..."
- files (OPTIONAL): "Optional files for context - EMBEDS CONTENT AS TEXT..."
- images (OPTIONAL): "Optional images for visual context..."
- model (OPTIONAL): "Model to use. Native models: 'auto', 'kimi-k2-0905-preview'..."
- continuation_id (OPTIONAL): "Thread continuation ID for multi-turn conversations..."
- use_websearch (OPTIONAL): "Enable provider-native web browsing"
- temperature (OPTIONAL): "Response creativity (0-1, default 0.5)"

Key Points from Schema:
- Simple request/response pattern
- Files parameter embeds content as text
- Warning about >5KB files
- No mention of "investigate first"
```

#### What DOCS Tell Me:
```
From AGENT_CAPABILITIES.md (Lines 234-241):
- "Quick question or brainstorming?" → chat_EXAI-WS
- Listed under "Simple Tools (No Workflow)"
- "Primary Use: General chat, brainstorming"
- "When to Use: Quick questions, small files"

From SYSTEM_CAPABILITIES_OVERVIEW.md (Lines 39-49):
- Example shows direct usage with files parameter
- No investigation required
- Simple request/response pattern
```

#### Contradictions/Gaps:
- ✅ **NO CONTRADICTIONS** - Schema and docs align perfectly
- ✅ Both say: Direct usage, no investigation required
- ✅ Both say: Use files parameter for context
- ✅ Both say: Simple tool, not workflow

#### Test Following Docs:
```python
# Docs say: Direct usage with files
chat_EXAI-WS(
    prompt="Analyze the schema findings in this document",
    files=["c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_01\\EXAI_TOOL_SCHEMA_ANALYSIS__2025-11-02.md"],
    model="glm-4.6"
)
```

#### Actual Behavior:
- ✅ **WORKS AS DOCUMENTED** - Tool analyzed file directly
- ✅ No investigation required
- ✅ Simple request/response
- ✅ File content correctly referenced

#### Classification:
- **Status:** ✅ ALIGNED (Schema matches docs, works as expected)

---

### TOOL 2: debug_EXAI-WS

#### What SCHEMA Shows Me:
```
Tool: debug_EXAI-WS
Description: "DEBUG & ROOT CAUSE ANALYSIS - Structured debugging workflow with expert validation.

⚠️ CRITICAL: This tool CANNOT investigate for you! YOU (Claude) must investigate FIRST.

HOW THIS TOOL WORKS:
1. YOU investigate using view/codebase-retrieval tools to gather evidence
2. YOU call this tool with your findings and hypothesis
3. Tool auto-executes internally (NO AI calls during steps 2-N)
4. Tool calls expert analysis at END (ONE AI call for validation)
5. You receive structured analysis and recommendations"

Parameters:
- step (REQUIRED): "Describe what you're currently investigating..."
- step_number (REQUIRED): "The index of the current step..."
- total_steps (REQUIRED): "Your current estimate..."
- next_step_required (REQUIRED): "Set to true if you plan to continue..."
- findings (REQUIRED): "Summarize everything discovered in this step..."
- hypothesis (OPTIONAL): "A concrete theory for what's causing the issue..."
- relevant_files (OPTIONAL): "Subset of files_checked (as full absolute paths)..."
- files_checked (OPTIONAL): "List all files (as absolute paths)..."
- confidence (OPTIONAL): "Indicate your current confidence..."

Key Points from Schema:
- ⚠️ "This tool CANNOT investigate for you!"
- ⚠️ "YOU (Claude) must investigate FIRST"
- Workflow pattern: investigate → call tool → expert analysis
- relevant_files is OPTIONAL in schema
```

#### What DOCS Tell Me:
```
From AGENT_CAPABILITIES.md (Lines 112-148):
"### **Core Principle: 'YOU Investigate First'**

Step 1: YOU investigate (using view, codebase-retrieval, etc.)
Step 2: YOU call workflow tool with YOUR findings
Step 3: Tool auto-executes internally (no AI calls)
Step 4: Tool calls expert analysis at END (one AI call)
Step 5: You receive comprehensive analysis with recommendations"

Example (Lines 136-148):
# Step 1: YOU investigate first
view(path="src/server.py", type="file")
codebase-retrieval(information_request="How is authentication handled?")

# Step 2: Call workflow tool with YOUR findings
debug_EXAI-WS(
    step="Investigating authentication bug",
    findings="Found that JWT validation is missing expiry check in validate_token()",
    hypothesis="Authentication bypass due to missing token expiration validation",
    relevant_files=["c:\\Project\\src\\auth.py"],
    confidence="exploring"
)
```

#### Contradictions/Gaps:

**🚨 CONTRADICTION #1: relevant_files requirement**
- **Schema says:** relevant_files is OPTIONAL
- **Docs say:** "relevant_files=["c:\\Project\\src\\auth.py"]" (shown in example)
- **My earlier finding:** get_first_step_required_fields() returns ['relevant_files'] (MANDATORY in step 1)
- **Gap:** Schema doesn't show it's MANDATORY in step 1

**🚨 HIDDEN REQUIREMENT #1: Investigation before calling**
- **Schema says:** "YOU must investigate FIRST" (in description)
- **Docs say:** "Step 1: YOU investigate (using view, codebase-retrieval, etc.)"
- **Gap:** Schema description mentions it, but parameters don't enforce it
- **Question:** What happens if I DON'T investigate first?

**✅ ALIGNMENT #1: Workflow pattern**
- **Schema says:** "Tool auto-executes internally (NO AI calls during steps 2-N)"
- **Docs say:** "Tool auto-executes internally (no AI calls)"
- **Aligned:** Both describe same workflow

#### Test Following Docs (Correct Pattern):
```python
# Step 1: I investigate first (as docs say)
view(path="tools/workflows/debug.py", type="file")
codebase-retrieval(information_request="How does debug tool handle file parameters?")

# Step 2: Call tool with MY findings (as docs say)
debug_EXAI-WS(
    step="Investigating why initial testing didn't include file parameters",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="I investigated debug.py and found that get_first_step_required_fields() explicitly returns ['relevant_files'], making it mandatory for step 1.",
    hypothesis="Testing methodology was flawed because files weren't provided despite being mandatory",
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\tools\\workflows\\debug.py"],
    confidence="high",
    model="glm-4.6"
)
```

#### Test WITHOUT Following Docs (Wrong Pattern):
```python
# What happens if I DON'T investigate first?
debug_EXAI-WS(
    step="Investigate authentication bug",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Please investigate the auth system",  # Not MY findings!
    confidence="exploring",
    model="glm-4.6"
)
```

#### Actual Behavior (TESTED - Following Docs Pattern):
- ✅ **WORKS WHEN I INVESTIGATE FIRST** - Tool accepted my findings
- ✅ **Expert analysis validated my investigation** - Confirmed schema vs implementation mismatch
- ✅ **Tool provided comprehensive analysis** - Identified root cause and fix recommendations

**Expert Analysis Findings:**
- **Root Cause:** "Schema vs Implementation Mismatch" (High confidence)
- **Evidence:** get_first_step_required_fields() returns ['relevant_files'], but schema shows it as optional
- **Minimal Fix:** "Update schema generation to include 'relevant_files' in required array when step_number == 1"
- **Key Finding:** "The generated schema doesn't reflect this requirement, showing it as optional"

**What This Proves:**
1. ✅ Tool WORKS when following docs pattern (investigate first, then call with findings)
2. 🚨 **CRITICAL CONTRADICTION CONFIRMED:** Schema says OPTIONAL, implementation requires MANDATORY
3. ✅ Expert analysis validates MY investigation (I found the same issue)
4. ✅ Tool provides actionable fix recommendations

#### Classification:
- **Status:** 🚨 **CRITICAL CONTRADICTION CONFIRMED**
  - **Issue Type:** Schema vs Implementation Mismatch
  - **Severity:** HIGH - Causes confusion about tool requirements
  - **Evidence:** get_first_step_required_fields() returns ['relevant_files'] but schema doesn't mark it required
  - **Impact:** Users don't know relevant_files is mandatory in step 1
  - **Fix Required:** Update schema generation to reflect mandatory requirement
  - **Docs Alignment:** Docs show correct usage, schema is misleading

---

### TOOL 3: analyze_EXAI-WS

#### What SCHEMA Shows Me:
```
Tool: analyze_EXAI-WS
Description: "COMPREHENSIVE CODE ANALYSIS - Structured analysis workflow with expert validation.

⚠️ CRITICAL: This tool CANNOT analyze code for you! YOU (Claude) must analyze FIRST.

HOW THIS TOOL WORKS:
1. YOU analyze code using view/codebase-retrieval tools
2. YOU call this tool with your analysis findings
3. Tool auto-executes internally (NO AI calls during steps 2-N)
4. Tool calls expert analysis at END (ONE AI call for validation)
5. You receive comprehensive analysis with strategic insights"

Parameters:
- step (REQUIRED): "What to analyze or look for in this step..."
- step_number (REQUIRED): "The index of the current step..."
- total_steps (REQUIRED): "Your current estimate..."
- next_step_required (REQUIRED): "Set to true if you plan to continue..."
- findings (REQUIRED): "Summarize everything discovered in this step..."
- relevant_files (OPTIONAL): "Subset of files_checked (as full absolute paths)..."
- analysis_type (OPTIONAL): "Type of analysis to perform (architecture, performance, security, quality, general)"
- confidence (OPTIONAL): "Your confidence level in the current analysis findings..."

Key Points from Schema:
- ⚠️ "This tool CANNOT analyze code for you!"
- ⚠️ "YOU (Claude) must analyze FIRST"
- Workflow pattern: analyze → call tool → expert validation
- relevant_files is OPTIONAL in schema
```

#### What DOCS Tell Me:
```
From AGENT_CAPABILITIES.md (Lines 234-241):
- "Need to understand architecture?" → analyze_EXAI-WS
- Listed under "Workflow Tools (Multi-Step)"
- "Primary Use: Code analysis"
- "Key Parameters: step, findings, relevant_files, confidence"

From SYSTEM_CAPABILITIES_OVERVIEW.md (Lines 172-177):
- Listed under "Investigation & Analysis"
- "Code analysis, architectural assessment"
```

#### Contradictions/Gaps:

**✅ ALIGNMENT #1: Investigation requirement**
- **Schema says:** "YOU must analyze FIRST"
- **Docs say:** "YOU investigate first using view/codebase-retrieval tools"
- **Aligned:** Both require investigation before calling

**🚨 HIDDEN REQUIREMENT #2: relevant_files usage**
- **Schema says:** relevant_files is OPTIONAL
- **Docs say:** Example shows relevant_files in usage
- **Gap:** Not clear if files are required or just recommended
- **Question:** Does analysis quality differ with/without files?

#### Test Following Docs (Correct Pattern):
```python
# Step 1: I analyze first (as docs say)
view(path="tools/workflows/analyze.py", type="file")
view(path="tools/workflow/schema_builders.py", type="file")
codebase-retrieval(information_request="How are file parameters integrated in workflow tools?")

# Step 2: Call tool with MY analysis (as docs say)
analyze_EXAI-WS(
    step="Analyzing workflow tool architecture for file parameter integration",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="I analyzed analyze.py and schema_builders.py and found that all workflow tools inherit from WorkflowRequest base class...",
    relevant_files=[
        "c:\\Project\\EX-AI-MCP-Server\\tools\\workflows\\analyze.py",
        "c:\\Project\\EX-AI-MCP-Server\\tools\\workflow\\schema_builders.py"
    ],
    confidence="high",
    model="glm-4.6"
)
```

#### Actual Behavior:
- ⏳ **PENDING TEST** - Need to test with proper investigation
- ❓ Does tool work better when I analyze first?
- ❓ Does tool provide different results with/without files?

#### Classification:
- **Status:** ⚠️ POTENTIAL GAPS
  - Investigation requirement clear in both
  - File parameter usage not clearly documented
  - Need to test actual behavior

---

## 📋 TESTING QUEUE

### Tools to Test:

1. ✅ **chat_EXAI-WS** - TESTED, ALIGNED
2. ⏳ **debug_EXAI-WS** - CONTRADICTIONS FOUND, NEEDS TESTING
3. ⏳ **analyze_EXAI-WS** - POTENTIAL GAPS, NEEDS TESTING
4. ⏳ **thinkdeep_EXAI-WS** - NOT ANALYZED YET
5. ⏳ **codereview_EXAI-WS** - NOT ANALYZED YET
6. ⏳ **testgen_EXAI-WS** - NOT ANALYZED YET
7. ⏳ **consensus_EXAI-WS** - NOT ANALYZED YET
8. ⏳ **planner_EXAI-WS** - NOT ANALYZED YET

---

## 🔍 ISSUE CLASSIFICATION

### Categories:

1. **✅ ALIGNED** - Schema and docs match, works as expected
2. **🚨 CONTRADICTION** - Schema says one thing, docs say another
3. **⚠️ HIDDEN REQUIREMENT** - Requirement exists but not clearly shown in schema
4. **❌ NOT WORKING** - Tool doesn't work as documented
5. **📝 MISSING INFO** - Documentation incomplete or unclear

### Issues Found So Far:

| Issue | Tool | Type | Description | Severity | Status |
|-------|------|------|-------------|----------|--------|
| #1 | debug | 🚨 CONTRADICTION | Schema says relevant_files OPTIONAL, implementation requires MANDATORY in step 1 | HIGH | ✅ CONFIRMED |
| #2 | debug | ⚠️ NOT ENFORCED | Investigation requirement in description but tool works without it | MEDIUM | ✅ CONFIRMED |
| #3 | debug | ⚠️ HIDDEN | Tool works WITHOUT relevant_files despite get_first_step_required_fields() | HIGH | ✅ CONFIRMED |
| #4 | analyze | ⚠️ HIDDEN | File parameter usage not clearly documented | LOW | ⏳ PENDING |

### Critical Discovery #1: Debug Tool Works WITHOUT Investigation! 🚨

**Test Results:**
- ✅ **WITH investigation:** Tool works, validates findings, provides expert analysis
- ✅ **WITHOUT investigation:** Tool STILL works, expert analysis tries to help anyway
- 🚨 **CRITICAL:** "YOU Investigate First" pattern is NOT ENFORCED

**What This Means:**
1. Documentation says "YOU must investigate FIRST" but tool doesn't enforce it
2. Tool will accept "Please investigate" as findings (opposite of design intent)
3. Expert analysis tries to help even with poor input
4. No validation error when investigation is skipped

**Impact:**
- Users can misuse tool by expecting it to investigate FOR them
- Contradicts documented design pattern
- May lead to poor quality results
- Documentation vs implementation mismatch

---

## 🚀 NEXT STEPS

1. **Complete schema vs docs analysis** for remaining 5 tools
2. **Test debug tool** with both patterns (investigate first vs don't investigate)
3. **Test analyze tool** with both patterns (with files vs without files)
4. **Document actual behavior** for each contradiction/gap
5. **Create fix recommendations** for schema/docs alignment

---

**Status:** 🔄 IN PROGRESS - Analyzing tool schemas vs documentation

