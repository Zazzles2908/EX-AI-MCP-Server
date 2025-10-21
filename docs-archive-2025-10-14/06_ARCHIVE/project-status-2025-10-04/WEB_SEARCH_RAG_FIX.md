# Web Search RAG Failure - Root Cause & Fix

**Date:** 2025-10-03  
**Severity:** CRITICAL  
**Status:** Root cause identified, fix in progress

---

## Problem Summary

**External AI Report:**
- GLM: 18x wrong on pricing (claimed ¥20/M vs actual $0.15/M)
- Kimi: 80x wrong on pricing (claimed $12/M vs actual $0.15/M)
- Both providers execute web search (metadata confirms)
- **Models ignore search results and hallucinate from training data**

---

## Root Cause Analysis

### What's Happening

1. ✅ **Web search executes** - Metadata confirms tool_calls triggered
2. ✅ **Search results returned** - Provider API returns results in response
3. ❌ **Results not re-injected** - We send empty acknowledgment `{"status": "executed_server_side"}`
4. ❌ **Model ignores results** - Follow-up response uses training data instead

### The Code Flow

**Current (BROKEN):**
```
1. User: "What is Kimi K2 pricing?"
2. Model returns: tool_calls=[{type: "builtin_function", function: {name: "$web_search"}}]
   + content: "Search results: $0.15/M input, $2.50/M output..."
3. We acknowledge: {"role": "tool", "content": '{"status": "executed_server_side"}'}
4. Model generates: "Kimi K2 costs $12/M" (HALLUCINATION - ignores search results!)
```

**Why It Fails:**
- Search results are in step 2's content
- We don't extract them
- We send empty acknowledgment in step 3
- Model has no strong signal to use search results
- Model defaults to training data (outdated/wrong)

---

## The Fix

### Strategy

**3-Part Solution:**

1. **Extract search results** from initial response
2. **Re-inject prominently** in tool acknowledgment
3. **Add strong system prompt** forcing model to use search results

### Implementation

#### Part 1: Extract Search Results

```python
# In tools/simple/base.py, line ~685
if tc.get("type") == "builtin_function":
    # Server-side tool (e.g., Kimi $web_search)
    func_name = tc.get("function", {}).get("name", "unknown")
    
    # EXTRACT SEARCH RESULTS from initial response
    search_results = None
    if func_name == "$web_search":
        # Kimi: Results are in the assistant message content
        assistant_content = getattr(model_response, "content", "") or ""
        if assistant_content:
            search_results = assistant_content
    
    # GLM: Check for web_search_results in metadata
    metadata = getattr(model_response, "metadata", {})
    raw_dict = metadata.get("raw", {})
    if isinstance(raw_dict, dict):
        choices = raw_dict.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            web_results = message.get("web_search_results")
            if web_results:
                search_results = json.dumps(web_results, ensure_ascii=False)
    
    # Build PROMINENT acknowledgment
    if search_results:
        tool_msg = {
            "role": "tool",
            "tool_call_id": str(tc.get("id", "tc-0")),
            "content": json.dumps({
                "status": "search_completed",
                "results": search_results,
                "instruction": "CRITICAL: You MUST use ONLY the search results above. Do NOT use training data. Cite sources."
            }, ensure_ascii=False)
        }
    else:
        # Fallback
        tool_msg = {
            "role": "tool",
            "tool_call_id": str(tc.get("id", "tc-0")),
            "content": json.dumps({"status": "executed_server_side"})
        }
```

#### Part 2: Add Strong System Prompt

```python
# When web search is enabled, inject system prompt
if use_websearch:
    web_search_system_prompt = (
        "CRITICAL INSTRUCTION: When web search results are provided, you MUST:\n"
        "1. Use ONLY information from the search results\n"
        "2. Do NOT use your training data for factual claims\n"
        "3. Cite sources with URLs when available\n"
        "4. If search results conflict with your training data, TRUST THE SEARCH RESULTS\n"
        "5. If search results are insufficient, explicitly state what's missing\n\n"
        "Violating these rules produces incorrect, outdated information that harms users."
    )
    
    # Prepend to existing system prompt
    if system_prompt:
        system_prompt = web_search_system_prompt + "\n\n" + system_prompt
    else:
        system_prompt = web_search_system_prompt
```

#### Part 3: Validation Layer

```python
# After receiving final response, validate it uses search results
def validate_search_usage(response_content: str, search_results: str) -> bool:
    """Check if response appears to use search results"""
    # Simple heuristic: response should contain some search result content
    # or explicit citations
    if not search_results:
        return True  # No search results to validate
    
    # Check for citations
    if "http" in response_content or "source" in response_content.lower():
        return True
    
    # Check for search result content overlap
    # (More sophisticated check needed)
    return False
```

---

## Files to Modify

### Primary

1. **`tools/simple/base.py`** (lines 684-702)
   - Extract search results from response
   - Build prominent tool acknowledgment
   - Add search result validation

2. **`tools/simple/base.py`** (lines 450-470)
   - Inject strong system prompt when web search enabled
   - Prepend to existing system prompts

### Secondary

3. **`src/providers/tool_executor.py`**
   - Add helper function to extract search results
   - Support both Kimi and GLM formats

4. **`utils/search_validation.py`** (NEW)
   - Validation logic for search result usage
   - Heuristics to detect hallucination

---

## Testing Plan

### Test Cases

1. **Kimi Pricing Query**
   - Query: "What is Kimi K2 pricing?"
   - Expected: $0.15/M input, $2.50/M output
   - Current: $12/M (WRONG)
   - After fix: Should match expected

2. **GLM Pricing Query**
   - Query: "What is GLM-4.5 pricing?"
   - Expected: Correct pricing from official docs
   - Current: ¥20/M (WRONG market)
   - After fix: Should match expected

3. **Verifiable Facts**
   - Query: "What is the current date?"
   - Expected: 2025-10-03
   - Test: Model should use search, not training cutoff

### Validation

```python
# Test script
def test_search_accuracy():
    result = chat(
        prompt="What is Kimi K2 pricing?",
        model="kimi-k2-0905-preview",
        use_websearch=True
    )
    
    # Check for correct pricing
    assert "$0.15" in result or "0.15" in result
    assert "$12" not in result  # Should NOT hallucinate
    
    # Check for citations
    assert "http" in result or "source" in result.lower()
```

---

## Rollout Plan

### Phase 1: Implement Fix (30 min)
- Modify `tools/simple/base.py`
- Add search result extraction
- Add strong system prompt

### Phase 2: Test (15 min)
- Run test_websearch_rag_failure.py
- Verify Kimi pricing query
- Verify GLM pricing query

### Phase 3: Validate (15 min)
- Test with multiple queries
- Check citation quality
- Verify no regressions

### Phase 4: Document (10 min)
- Update web-search.md
- Add troubleshooting guide
- Document validation approach

---

## Success Criteria

✅ **Kimi pricing query returns $0.15/M** (not $12/M)  
✅ **GLM pricing query returns correct market pricing** (not ¥20/M)  
✅ **Responses include citations/sources**  
✅ **No hallucinations on verifiable facts**  
✅ **Backward compatibility maintained**

---

## Risk Assessment

**Low Risk:**
- Changes are isolated to web search flow
- Only affects tool acknowledgment content
- System prompt addition is non-breaking
- Easy to revert if issues

**Mitigation:**
- Test thoroughly before deploying
- Keep old code commented for quick rollback
- Monitor for regressions

---

## Next Steps

1. ✅ Root cause identified
2. 🔄 Implement Part 1: Extract search results
3. ⏳ Implement Part 2: Strong system prompt
4. ⏳ Implement Part 3: Validation
5. ⏳ Test with pricing queries
6. ⏳ Deploy and monitor

---

**Status:** Ready to implement  
**Estimated Time:** 1 hour  
**Priority:** CRITICAL

