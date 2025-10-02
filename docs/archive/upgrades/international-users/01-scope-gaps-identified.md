# Scope Gaps Identified: EXAI Tools for Research & Implementation

**Date:** 2025-10-01  
**Target:** International Users (api.z.ai, zai-sdk package)  
**Investigation Method:** Systematic EXAI tool testing  
**Status:** 🚨 CRITICAL GAPS FOUND

---

## 🎯 Purpose of This Investigation

To systematically test EXAI MCP tools and identify gaps in functionality that need to be addressed during the zai-sdk upgrade implementation. This ensures we understand what works, what doesn't, and what needs to be fixed.

---

## 🚨 SCOPE GAP #1: Native Web Search Not Working in Chat Tool

### Issue Description
The `chat_EXAI-WS` tool with `use_websearch=true` parameter does NOT perform native web browsing as expected.

### Expected Behavior
```python
chat_EXAI-WS(
    prompt="Research zai-sdk latest version",
    model="glm-4.5",
    use_websearch=true  # Should trigger GLM native web search
)
```

**Expected:** GLM model performs web search and returns results with sources

### Actual Behavior
**Actual:** GLM model responds with:
> "Please perform a web search on 'zai-sdk PyPI latest version' and then continue this analysis using the continuation_id from this response."

The model is asking ME to do the web search instead of doing it itself!

### Root Cause
Based on previous investigation (glm-web-search-investigation.md):
1. `GLM_ENABLE_WEB_BROWSING=true` is set in .env ✅
2. Chat tool has `use_websearch` parameter ✅
3. GLMCapabilities.get_websearch_tool_schema() exists ✅
4. **BUT:** The web_search tool schema may not be properly injected into the API payload

### Impact
- **HIGH** - Cannot use EXAI chat tool for web research
- Forces fallback to Augment's web-search tool
- Defeats the purpose of native GLM web browsing
- Makes research workflows inefficient

### Required Fix
1. Debug the tool schema injection flow in chat tool
2. Verify web_search tool is added to GLM API payload
3. Test with glm_payload_preview tool to inspect actual payload
4. Ensure GLM API receives and uses the web_search tool

---

## 🚨 SCOPE GAP #2: Workflow Tools Require Manual Investigation

### Issue Description
EXAI workflow tools (analyze, thinkdeep, etc.) are designed to pause and require manual investigation between steps, rather than performing autonomous research.

### Expected Behavior (What I Thought)
```python
analyze_EXAI-WS(
    step="Research zai-sdk features",
    use_websearch=true  # Should autonomously research
)
```

**Expected:** Tool performs web research and returns comprehensive findings

### Actual Behavior
**Actual:** Tool responds with:
```json
{
  "status": "pause_for_analysis",
  "required_actions": [
    "Read and understand the code files",
    "Map the tech stack and architecture",
    "Identify main components"
  ],
  "next_steps": "DO NOT call analyze again. You MUST first examine files..."
}
```

The tool expects ME to do the investigation work between steps!

### Design Intent
This is actually BY DESIGN:
- Workflow tools guide systematic investigation
- They enforce proper methodology (investigate → report → investigate → report)
- They prevent "hallucination" by requiring actual evidence
- They ensure thorough, step-by-step analysis

### Impact
- **MEDIUM** - Not a bug, but a workflow difference
- Cannot use for autonomous web research
- Requires agent to do investigation between steps
- Good for code analysis, not ideal for web research

### Implications for Upgrade
1. EXAI workflow tools are for CODE ANALYSIS, not web research
2. For web research, need to use Augment's web-search tool
3. For code analysis during upgrade, EXAI tools are perfect
4. Need to document this workflow clearly

---

## 🚨 SCOPE GAP #3: No Direct Web Research Tool in EXAI

### Issue Description
There is no EXAI tool specifically designed for autonomous web research.

### Available Tools Analysis

#### chat_EXAI-WS
- **Purpose:** General chat and collaborative thinking
- **Web Search:** Has `use_websearch` parameter but NOT WORKING (Gap #1)
- **Best For:** Discussions, explanations, brainstorming
- **NOT For:** Autonomous web research (currently)

#### thinkdeep_EXAI-WS
- **Purpose:** Multi-stage investigation workflow
- **Web Search:** Has `use_websearch` parameter
- **Best For:** Complex problem analysis with code
- **NOT For:** Simple web research (requires step-by-step workflow)

#### analyze_EXAI-WS
- **Purpose:** Code analysis workflow
- **Web Search:** Has `use_websearch` parameter
- **Best For:** Architectural assessment, code review
- **NOT For:** Web research (designed for code analysis)

### What's Missing
A dedicated EXAI tool for autonomous web research that:
1. Takes a research query
2. Performs web searches autonomously
3. Synthesizes information from multiple sources
4. Returns comprehensive findings with citations
5. Doesn't require step-by-step workflow

### Current Workaround
Use Augment's built-in tools:
- `web-search` - Search the web
- `web-fetch` - Fetch webpage content
- Manual synthesis of results

### Impact
- **MEDIUM** - Can work around with Augment tools
- Less integrated workflow
- More manual work required
- Not using GLM's native capabilities

---

## 🚨 SCOPE GAP #4: File Path Requirements

### Issue Description
EXAI tools require FULL absolute paths, not relative paths.

### Example Error
```python
analyze_EXAI-WS(
    relevant_files=["."]  # Relative path
)
```

**Error:** "All file paths must be FULL absolute paths. Invalid path: '.'"

### Correct Usage
```python
analyze_EXAI-WS(
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\requirements.txt"]
)
```

### Impact
- **LOW** - Easy to fix
- Just need to use absolute paths
- Augment provides workspace root: `c:\Project\EX-AI-MCP-Server`

---

## 📊 Summary of Gaps

| Gap # | Issue | Severity | Status | Fix Required |
|-------|-------|----------|--------|--------------|
| 1 | Native web search not working in chat | HIGH | 🔴 BROKEN | YES - Debug tool injection |
| 2 | Workflow tools require manual steps | MEDIUM | ⚠️ BY DESIGN | NO - Document workflow |
| 3 | No autonomous web research tool | MEDIUM | ⚠️ MISSING | MAYBE - Consider adding |
| 4 | Requires absolute file paths | LOW | ⚠️ LIMITATION | NO - Use absolute paths |

---

## 🔧 Required Fixes for Upgrade Implementation

### Priority 1: Fix Native Web Search (Gap #1)
**Must Fix Before Upgrade:**
1. Debug chat tool's web_search tool injection
2. Verify GLMCapabilities.get_websearch_tool_schema() is called
3. Test with glm_payload_preview to inspect payload
4. Ensure web_search tool reaches GLM API
5. Test with actual web search queries
6. Document working configuration

**Acceptance Criteria:**
- `chat_EXAI-WS(prompt="...", use_websearch=true)` performs actual web search
- Results include current information with sources
- No manual intervention required

### Priority 2: Document EXAI Workflow (Gap #2)
**Must Document:**
1. EXAI tools are for CODE ANALYSIS, not web research
2. Workflow requires investigation between steps
3. Use Augment tools for web research
4. Use EXAI tools for code analysis during upgrade
5. Provide examples of correct usage

**Acceptance Criteria:**
- Clear documentation of when to use which tools
- Examples of EXAI workflow for code analysis
- Examples of web research workflow

### Priority 3: Consider Web Research Tool (Gap #3)
**Optional Enhancement:**
1. Create dedicated web research tool
2. Or fix chat tool's web search (Priority 1)
3. Or document Augment tools as primary method

**Decision:** Fix Priority 1 first, then decide if dedicated tool is needed

---

## 🎯 Implications for zai-sdk Upgrade

### What We CAN Do with Current EXAI Tools
✅ Code analysis of existing provider implementations  
✅ Architectural assessment of current SDK integration  
✅ Step-by-step migration planning  
✅ Code review of upgrade changes  
✅ Security audit of new features  
✅ Testing strategy development  

### What We CANNOT Do with Current EXAI Tools
❌ Autonomous web research on zai-sdk features  
❌ Real-time API documentation lookup  
❌ Automated discovery of breaking changes  
❌ Quick fact-checking without manual steps  

### Recommended Approach for Upgrade
1. **Use Augment tools** for web research:
   - web-search for finding information
   - web-fetch for reading documentation
   - Manual synthesis of findings

2. **Use EXAI tools** for code analysis:
   - analyze for architectural assessment
   - codereview for reviewing changes
   - refactor for identifying improvements
   - secaudit for security review

3. **Fix web search** (Priority 1) to enable:
   - Integrated research workflow
   - Native GLM capabilities
   - More efficient process

---

## 📝 Action Items for Implementation Checklist

### Before Starting Upgrade
- [ ] Fix native web search in chat tool (Gap #1)
- [ ] Test web search with actual queries
- [ ] Document EXAI workflow patterns
- [ ] Create examples of correct tool usage

### During Upgrade
- [ ] Use Augment tools for web research
- [ ] Use EXAI tools for code analysis
- [ ] Document any additional gaps found
- [ ] Test new features with EXAI tools

### After Upgrade
- [ ] Verify web search works with new SDK
- [ ] Update tool documentation
- [ ] Create upgrade guide for future reference

---

## 🔍 Testing Performed

### Test 1: chat_EXAI-WS with use_websearch=true
**Result:** ❌ FAILED - Model asked me to perform search  
**Evidence:** Response: "Please perform a web search on..."  
**Conclusion:** Native web search not working

### Test 2: thinkdeep_EXAI-WS with use_websearch=true
**Result:** ⚠️ PAUSED - Workflow requires manual investigation  
**Evidence:** Status: "pause_for_thinkdeep", required_actions list  
**Conclusion:** By design, not a bug

### Test 3: analyze_EXAI-WS with use_websearch=true
**Result:** ⚠️ PAUSED - Workflow requires file examination  
**Evidence:** Status: "pause_for_analysis", required_actions list  
**Conclusion:** By design, not a bug

### Test 4: Relative vs Absolute Paths
**Result:** ❌ ERROR - Relative paths not accepted  
**Evidence:** Error: "Invalid path: '.'"  
**Conclusion:** Must use absolute paths

---

## 📚 References

- Previous investigation: `glm-web-search-investigation.md`
- Web search config: `.env` line 17, `.env.example` line 10
- GLM capabilities: `src/providers/capabilities.py` lines 80-88
- Chat tool: `tools/chat.py` line 52

---

**Investigation Status:** ✅ COMPLETE  
**Gaps Identified:** 4 (1 HIGH, 2 MEDIUM, 1 LOW)  
**Fixes Required:** 1 (Priority 1: Native web search)  
**Ready for Implementation:** ⏳ AFTER FIXING GAP #1

