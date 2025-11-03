# K2 MODEL USAGE GUIDE
## How to Effectively Use Kimi K2 for Investigation & Implementation
**Date:** November 3, 2025  
**Model:** kimi-k2-0905-preview  
**Purpose:** Guide for next agent to leverage K2 assistance

---

## WHY USE K2?

Based on this investigation, K2 provides:

1. **Strategic Perspective** - Frames issues as design problems, not just bugs
2. **Professional Recommendations** - Business-level reasoning with technical depth
3. **Comprehensive Analysis** - Synthesizes multiple data sources effectively
4. **Continuation Support** - Maintains context across multiple exchanges
5. **Web Search Integration** - Accesses current documentation and best practices

---

## WHAT WORKED (Proven Approach)

### Using `chat_EXAI-WS` Tool

**Success Pattern:**
```python
chat_EXAI-WS(
    prompt="Your detailed question with full context...",
    files=[
        "c:\\Project\\EX-AI-MCP-Server\\path\\to\\file1.txt",
        "c:\\Project\\EX-AI-MCP-Server\\path\\to\\file2.sql"
    ],
    model="kimi-k2-0905-preview",
    use_websearch=True,
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c"  # Optional
)
```

**Key Success Factors:**
1. ✅ Use `chat_EXAI-WS` (not `smart_file_query`)
2. ✅ Provide ABSOLUTE Windows paths
3. ✅ Use COMPLETE RAW files (no filtering)
4. ✅ Explicitly specify `kimi-k2-0905-preview`
5. ✅ Enable web search for context
6. ✅ Use continuation_id to maintain context

---

## WHAT DIDN'T WORK (Avoid These)

### Failed Approaches

**❌ Using `smart_file_query`:**
- File upload mechanism fails
- Error: "Upload failed with both providers"
- Use `chat_EXAI-WS` instead

**❌ Using `kimi_chat_with_tools`:**
- Wrong tool for this use case
- Use `chat_EXAI-WS` instead

**❌ Filtering/Extracting Data:**
- Introduces human bias
- K2 works better with complete raw data
- Let K2 identify patterns independently

**❌ Relying on Auto Provider Selection:**
- May not select K2
- Always explicitly specify model

---

## FILE HANDLING BEST PRACTICES

### File Embedding vs Upload

| Approach | Tool | Mechanism | Size Limit | Result |
|----------|------|-----------|------------|--------|
| **Upload** | `smart_file_query` | Uploads to platform | 100MB | ❌ FAILED |
| **Embedding** | `chat_EXAI-WS` | Embeds as text | ~5KB warning | ✅ WORKED |

### When to Use Each

**Use `chat_EXAI-WS` (Embedding):**
- Files under ~10KB (warning at 5KB but works)
- Need immediate analysis
- Want to avoid upload failures
- Single-use file reference

**Use File Upload (if working):**
- Files over 10KB
- Need persistent reference
- Multiple queries on same file

### File Size Reality Check

**Official Warning:** Files >5KB trigger warnings  
**Actual Capability:** Successfully handled 1,863-line Docker log  
**Recommendation:** Try embedding first, upload only if fails

---

## CONTINUATION ID USAGE

### What is Continuation ID?

A unique identifier that maintains conversation context across multiple K2 calls.

**Current ID:** `3c6828d7-09e7-4273-8c1a-7385ca32124c`  
**Remaining Exchanges:** 16  
**Model:** kimi-k2-0905-preview

### When to Use Continuation

**Use continuation when:**
- Building on previous K2 analysis
- Need context from earlier conversation
- Asking follow-up questions
- Iterating on implementation plan

**Start new conversation when:**
- Completely different topic
- Want fresh perspective
- Previous context not relevant

### How to Use

```python
# First call (no continuation_id):
result1 = chat_EXAI-WS(
    prompt="Initial question...",
    model="kimi-k2-0905-preview"
)
# Returns: continuation_id in result

# Follow-up calls (with continuation_id):
result2 = chat_EXAI-WS(
    prompt="Follow-up question...",
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview"
)
```

---

## EFFECTIVE PROMPTING FOR K2

### Prompt Structure

**Good Prompt Structure:**
1. **Context:** What you're working on
2. **Current State:** What you've discovered
3. **Specific Question:** What you need help with
4. **Expected Output:** What format you want

**Example:**
```
Context: I'm investigating the confidence-based skipping logic in EXAI workflow tools.

Current State: I've located the should_call_expert_analysis() function in 
src/tools/workflow/base.py. It checks confidence levels and file counts.

Specific Question: Should I disable this entirely or add a force-run flag?

Expected Output: Pros/cons of each approach with implementation recommendations.
```

### What to Include

**Always Include:**
- Current date (forces web search for current info)
- Full context (don't assume K2 remembers)
- Specific files being discussed
- What you've already tried
- What you need help with

**Example Opening:**
```
Today is November 3, 2025.

I'm continuing the investigation of EXAI workflow tools. I've located the 
should_call_expert_analysis() function and need guidance on implementation...
```

---

## COMMON USE CASES

### 1. Code Review

```python
chat_EXAI-WS(
    prompt="Please review this implementation for the confidence skipping fix...",
    files=["c:\\Project\\EX-AI-MCP-Server\\src\\tools\\workflow\\base.py"],
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview"
)
```

### 2. Architecture Questions

```python
chat_EXAI-WS(
    prompt="How does the workflow engine interact with expert analysis? I need to understand the flow...",
    files=[
        "c:\\Project\\EX-AI-MCP-Server\\src\\core\\workflow_engine.py",
        "c:\\Project\\EX-AI-MCP-Server\\src\\agents\\expert_analysis.py"
    ],
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview",
    use_websearch=True
)
```

### 3. Implementation Validation

```python
chat_EXAI-WS(
    prompt="I've implemented the fix. Can you validate this approach and identify any issues?",
    files=["c:\\Project\\EX-AI-MCP-Server\\src\\tools\\workflow\\base.py"],
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview"
)
```

### 4. Testing Strategy

```python
chat_EXAI-WS(
    prompt="What test cases should I create to verify the confidence skipping fix?",
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview",
    use_websearch=True
)
```

---

## INTERPRETING K2 RESPONSES

### What K2 Provides

**Strategic Insights:**
- Design philosophy perspective
- Business-level reasoning
- User value focus
- Professional recommendations

**Technical Details:**
- Implementation approaches
- Code examples
- Architecture explanations
- Testing strategies

**Actionable Plans:**
- Step-by-step instructions
- Priority ordering
- Risk assessment
- Success criteria

### How to Use K2 Output

1. **Read the full response** - K2 provides comprehensive analysis
2. **Extract action items** - Look for specific steps
3. **Validate recommendations** - Cross-check with codebase
4. **Ask follow-ups** - Use continuation for clarification
5. **Document decisions** - Record what you implement

---

## TROUBLESHOOTING

### If K2 Call Fails

**Check:**
1. Model name spelled correctly: `kimi-k2-0905-preview`
2. File paths are absolute Windows paths
3. Files exist at specified paths
4. Continuation ID is valid (if used)

**Try:**
1. Remove `continuation_id` and start fresh
2. Reduce file sizes (split large files)
3. Simplify prompt
4. Check EXAI server logs

### If Response is Unclear

**Ask for clarification:**
```python
chat_EXAI-WS(
    prompt="Can you clarify your recommendation about [specific point]? 
    I need more detail on [specific aspect].",
    continuation_id="3c6828d7-09e7-4273-8c1a-7385ca32124c",
    model="kimi-k2-0905-preview"
)
```

---

## BEST PRACTICES SUMMARY

### DO:
✅ Use `chat_EXAI-WS` for K2 calls  
✅ Provide complete raw data  
✅ Use absolute Windows paths  
✅ Explicitly specify model  
✅ Enable web search  
✅ Use continuation for context  
✅ Include current date in prompts  
✅ Ask specific questions  

### DON'T:
❌ Use `smart_file_query` (upload fails)  
❌ Filter or extract data  
❌ Rely on auto model selection  
❌ Assume K2 remembers context  
❌ Skip continuation_id for follow-ups  
❌ Use vague prompts  
❌ Ignore K2's strategic insights  

---

## CONTINUATION ID REFERENCE

**Current Active Continuation:**
- **ID:** `3c6828d7-09e7-4273-8c1a-7385ca32124c`
- **Model:** kimi-k2-0905-preview
- **Remaining:** 16 exchanges
- **Context:** EXAI workflow tools investigation and fix
- **Started:** November 3, 2025

**Use this for:**
- Implementation questions
- Code review
- Architecture clarification
- Testing strategy
- Validation of fixes

---

## EXAMPLE WORKFLOW

### Complete Investigation Flow

**Step 1: Initial Analysis**
```python
result = chat_EXAI-WS(
    prompt="Analyze this issue...",
    files=["raw_data.txt"],
    model="kimi-k2-0905-preview"
)
continuation_id = result['continuation_offer']['continuation_id']
```

**Step 2: Follow-up Questions**
```python
chat_EXAI-WS(
    prompt="Based on your analysis, how should I...",
    continuation_id=continuation_id,
    model="kimi-k2-0905-preview"
)
```

**Step 3: Implementation Review**
```python
chat_EXAI-WS(
    prompt="I've implemented your recommendation. Please review...",
    files=["modified_file.py"],
    continuation_id=continuation_id,
    model="kimi-k2-0905-preview"
)
```

**Step 4: Final Validation**
```python
chat_EXAI-WS(
    prompt="The fix is complete. Can you validate the approach?",
    continuation_id=continuation_id,
    model="kimi-k2-0905-preview"
)
```

---

**K2 is a powerful tool for strategic analysis and implementation guidance. Use it wisely!**

