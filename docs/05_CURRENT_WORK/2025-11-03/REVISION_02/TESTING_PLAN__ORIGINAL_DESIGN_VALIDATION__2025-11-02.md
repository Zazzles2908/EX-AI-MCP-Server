# EXAI Tool Testing Plan - Original Design Validation
**Date:** 2025-11-02  
**Status:** 🔄 PLANNING  
**Purpose:** Validate tools against ORIGINAL DESIGN INTENT from documentation

---

## 🚨 CRITICAL REALIZATION

**I've been testing INCORRECTLY!** The original design documentation clearly states:

### Original Design Intent (from AGENT_CAPABILITIES.md):

```
**Core Principle: "YOU Investigate First"**

Step 1: YOU investigate (using view, codebase-retrieval, etc.)
Step 2: YOU call workflow tool with YOUR findings
Step 3: Tool auto-executes internally (no AI calls)
Step 4: Tool calls expert analysis at END (one AI call)
Step 5: You receive comprehensive analysis with recommendations
```

### What I Was Doing Wrong:

❌ **Calling workflow tools WITHOUT investigating first**
❌ **Expecting tools to analyze files FOR me**
❌ **Testing tools in isolation without proper investigation**
❌ **Not following the "YOU Investigate First" pattern**

---

## 🎯 CORRECT TESTING METHODOLOGY

### Phase 1: Investigation (BEFORE calling tool)

**For Each Tool Test:**

1. **Use view/codebase-retrieval to investigate**
   - Read relevant files
   - Understand code structure
   - Identify patterns, issues, or opportunities
   - Form hypotheses

2. **Document YOUR findings**
   - What YOU discovered
   - What YOU analyzed
   - What YOU concluded

3. **THEN call workflow tool with YOUR findings**
   - Tool validates YOUR investigation
   - Expert analysis confirms or corrects YOUR findings
   - Tool provides recommendations based on YOUR work

---

## 📋 REVISED TEST CASES - FOLLOWING ORIGINAL DESIGN

### Test 1: DEBUG TOOL (Proper Pattern)

**Step 1: I INVESTIGATE FIRST**
```python
# Use view to read the file
view(path="tools/workflows/debug.py", type="file")

# Use codebase-retrieval to understand context
codebase-retrieval(information_request="How does debug tool handle file parameters?")

# MY FINDINGS:
# - Debug tool requires relevant_files in step 1
# - get_first_step_required_fields() returns ['relevant_files']
# - Tool description states "MANDATORY: Pass relevant_files"
# - Initial testing didn't provide files, should have failed
```

**Step 2: CALL DEBUG TOOL WITH MY FINDINGS**
```python
debug_EXAI-WS(
    step="Investigating why initial testing didn't include file parameters",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="I investigated debug.py and found that get_first_step_required_fields() explicitly returns ['relevant_files'], making it mandatory for step 1. The tool description also states 'MANDATORY: Pass relevant_files (absolute paths) in step 1'. Initial testing should have failed without files.",
    hypothesis="Testing methodology was flawed because files weren't provided despite being mandatory",
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\tools\\workflows\\debug.py"],
    confidence="high",  # High because I investigated and found evidence
    model="glm-4.6"
)
```

**Expected Outcome:**
- ✅ Tool validates MY findings
- ✅ Expert analysis confirms MY hypothesis
- ✅ Recommendations align with MY investigation

---

### Test 2: ANALYZE TOOL (Proper Pattern)

**Step 1: I INVESTIGATE FIRST**
```python
# Read the analyze tool implementation
view(path="tools/workflows/analyze.py", type="file")
view(path="tools/workflow/schema_builders.py", type="file")

# Search for file parameter integration
codebase-retrieval(information_request="How are file parameters integrated in workflow tools?")

# MY FINDINGS:
# - Analyze tool inherits from WorkflowRequest base class
# - WorkflowRequest provides relevant_files and images support
# - Schema builder defines standard workflow fields
# - File parameters are optional for analyze (no mandatory requirement)
# - Files enhance analysis but aren't required
```

**Step 2: CALL ANALYZE TOOL WITH MY FINDINGS**
```python
analyze_EXAI-WS(
    step="Analyzing workflow tool architecture for file parameter integration",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="I investigated analyze.py and schema_builders.py and found that all workflow tools inherit from WorkflowRequest base class, which provides relevant_files and images support. The schema builder standardizes these fields across all workflow tools. File parameters are optional for analyze tool (no get_first_step_required_fields method), but they enhance analysis quality.",
    relevant_files=[
        "c:\\Project\\EX-AI-MCP-Server\\tools\\workflows\\analyze.py",
        "c:\\Project\\EX-AI-MCP-Server\\tools\\workflow\\schema_builders.py"
    ],
    confidence="high",  # High because I investigated code structure
    model="glm-4.6"
)
```

**Expected Outcome:**
- ✅ Tool validates MY architectural analysis
- ✅ Expert analysis confirms file parameter integration pattern
- ✅ Recommendations for best practices

---

### Test 3: CHAT TOOL (Simple Tool - No Investigation Required)

**Chat tool is DIFFERENT - it's NOT a workflow tool!**

From documentation:
- Chat is a "simple tool" (no workflow)
- No "YOU investigate first" requirement
- Direct question/answer pattern

**Correct Usage:**
```python
chat_EXAI-WS(
    prompt="Analyze the schema findings in this document and summarize key discoveries",
    files=["c:\\Project\\EX-AI-MCP-Server\\docs\\05_CURRENT_WORK\\2025-11-03\\REVISION_01\\EXAI_TOOL_SCHEMA_ANALYSIS__2025-11-02.md"],
    model="glm-4.6"
)
```

**Expected Outcome:**
- ✅ Direct analysis of file content
- ✅ No investigation required beforehand
- ✅ Simple request/response pattern

---

## 🔍 VALIDATION CRITERIA - BASED ON ORIGINAL DESIGN

### For Workflow Tools:

**Investigation Phase:**
- [ ] Did I use view/codebase-retrieval BEFORE calling tool?
- [ ] Did I document MY findings from investigation?
- [ ] Did I form MY hypothesis based on evidence?
- [ ] Did I identify relevant files through MY investigation?

**Tool Call Phase:**
- [ ] Did I pass MY findings to the tool?
- [ ] Did I include relevant_files I identified?
- [ ] Did I set appropriate confidence based on MY investigation?
- [ ] Did I provide MY hypothesis, not ask tool to investigate?

**Validation Phase:**
- [ ] Did tool validate MY findings (not discover new ones)?
- [ ] Did expert analysis confirm or correct MY investigation?
- [ ] Did recommendations build on MY work?
- [ ] Was there only ONE AI call at the end?

### For Simple Tools (chat, challenge, activity):

**Direct Usage:**
- [ ] Did I call tool directly without investigation?
- [ ] Did I provide clear question/request?
- [ ] Did I include necessary files for context?
- [ ] Did tool respond directly without workflow?

---

## 📊 TESTING MATRIX - ORIGINAL DESIGN VALIDATION

| Tool | Type | Investigation Required? | Test Status |
|------|------|------------------------|-------------|
| chat | Simple | ❌ No | ✅ CORRECT (tested properly) |
| debug | Workflow | ✅ YES | ❌ WRONG (didn't investigate first) |
| analyze | Workflow | ✅ YES | ❌ WRONG (didn't investigate first) |
| thinkdeep | Workflow | ✅ YES | ⏳ PENDING |
| codereview | Workflow | ✅ YES | ⏳ PENDING |
| testgen | Workflow | ✅ YES | ⏳ PENDING |
| consensus | Workflow | ✅ YES | ⏳ PENDING |
| planner | Workflow | ✅ YES | ⏳ PENDING |

---

## 🚀 NEXT STEPS

### Immediate Actions:

1. **Re-test debug tool** following "YOU Investigate First" pattern
2. **Re-test analyze tool** following "YOU Investigate First" pattern
3. **Test remaining workflow tools** with proper investigation
4. **Document findings** comparing original design vs actual behavior

### Questions to Answer:

1. **Do tools work as designed when I investigate first?**
2. **What happens if I DON'T investigate first?**
3. **Is the "YOU Investigate First" pattern enforced or just recommended?**
4. **Do tools provide better results when I investigate first?**

---

## 💡 KEY INSIGHTS

**What I Learned:**
1. ✅ **Original design is well-documented** - I should have read this FIRST
2. ✅ **Workflow tools expect investigation** - not discovery
3. ✅ **Simple tools are different** - direct usage pattern
4. ✅ **File parameters enhance analysis** - but investigation is key
5. ✅ **Confidence progression matters** - based on MY investigation

**What This Means:**
- My previous testing was **fundamentally flawed**
- I was using tools **opposite to their design**
- Need to **re-test everything** following original design
- Original design intent was **lost during upgrades**

---

**Status:** 🔄 READY TO RE-TEST WITH CORRECT METHODOLOGY

