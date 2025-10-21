# Task A: GLM Text Format Handler Implementation Plan
**Date:** 2025-10-04  
**Status:** AWAITING EXAI VALIDATION  
**Priority:** HIGH

---

## 🎯 OBJECTIVE

Implement text format handler in `src/providers/glm_chat.py` to parse and execute web_search from text responses when GLM models (especially glm-4.5-flash) return tool calls as TEXT instead of in the tool_calls array.

---

## 📊 PROBLEM ANALYSIS

### Current Behavior
```python
# src/providers/glm_chat.py lines 209-212
elif has_tool_call_text:
    # GLM returned tool call as TEXT instead of executing it
    logger.warning(f"GLM returned tool call as TEXT (not executed): {text[:200]}")
    # TODO: Implement text format handler to execute search ourselves
```

**Result:** Text format responses are logged but NOT executed, causing web search to fail.

### Text Formats to Handle

**Format B:**
```
<tool_call>web_search
<think>query
<arg_value>current Bitcoin price USD
</tool_call>
```

**Format C:**
```
<tool_code>
{"name": "web_search", "parameters": {"query": "Ethereum price USD current live"}}
</tool_code>
```

**Format D (Acknowledgment Only):**
```
I'll search for the current temperature in London to provide you with real-time weather data.
```

---

## 🔧 PROPOSED IMPLEMENTATION

### Strategy

1. **Parse Text Formats:** Use regex to extract query from Formats B and C
2. **Execute Search:** Use existing DuckDuckGo fallback system
3. **Format Results:** Append search results to content in same format as tool_calls array
4. **Error Handling:** Graceful fallback if parsing or search fails
5. **Logging:** Track success/failure rates for monitoring

### Implementation Location

**File:** `src/providers/glm_chat.py`  
**Lines:** 209-212 (replace TODO)  
**Scope:** Both SDK path (lines 180-213) and HTTP path (lines 281-299)

### Proposed Code

```python
elif has_tool_call_text:
    # GLM returned tool call as TEXT - parse and execute it
    logger.warning(f"GLM returned tool call as TEXT: {text[:200]}")
    
    try:
        import re
        import json as _json
        
        query = None
        
        # Format B: <tool_call>web_search...<arg_value>query</tool_call>
        match_b = re.search(
            r'<tool_call>web_search.*?<arg_value>(.*?)</tool_call>',
            text,
            re.DOTALL | re.IGNORECASE
        )
        if match_b:
            query = match_b.group(1).strip()
            logger.debug(f"Parsed Format B: query='{query}'")
        
        # Format C: <tool_code>{"name": "web_search", "parameters": {"query": "..."}}
        if not query:
            match_c = re.search(
                r'<tool_code>\s*\{[^}]*"name"\s*:\s*"web_search"[^}]*"query"\s*:\s*"([^"]+)"',
                text,
                re.DOTALL | re.IGNORECASE
            )
            if match_c:
                query = match_c.group(1).strip()
                logger.debug(f"Parsed Format C: query='{query}'")
        
        # Alternative Format C: Look for JSON object
        if not query:
            match_c_alt = re.search(
                r'<tool_code>\s*(\{.*?\})\s*</tool_code>',
                text,
                re.DOTALL
            )
            if match_c_alt:
                try:
                    tool_data = _json.loads(match_c_alt.group(1))
                    if tool_data.get("name") == "web_search":
                        params = tool_data.get("parameters", {})
                        query = params.get("query", "").strip()
                        logger.debug(f"Parsed Format C (JSON): query='{query}'")
                except Exception as e:
                    logger.debug(f"Failed to parse Format C JSON: {e}")
        
        if query:
            # Execute web search using DuckDuckGo fallback
            logger.info(f"Executing web_search via text format handler: query='{query}'")
            
            # Import fallback search function
            from src.utils.web_search_fallback import execute_duckduckgo_search
            
            search_results = execute_duckduckgo_search(query, max_results=5)
            
            if search_results:
                # Format results similar to tool_calls array format
                results_text = "\n\n[Web Search Results]\n" + _json.dumps(
                    search_results,
                    indent=2,
                    ensure_ascii=False
                )
                text = text + results_text
                logger.info(f"GLM web_search executed successfully via text format handler")
            else:
                logger.warning(f"Web search returned no results for query: {query}")
        else:
            logger.warning(f"Could not extract query from text format response")
            
    except Exception as e:
        logger.error(f"Error in text format handler: {e}", exc_info=True)
        # Continue with original text - don't break the response
```

---

## 🔍 VALIDATION REQUIREMENTS

### EXAI Codereview Should Validate:

1. **Regex Patterns:**
   - Are the regex patterns correct and robust?
   - Do they handle edge cases (multiline, special chars, etc.)?
   - Are there better/simpler patterns?

2. **Fallback Integration:**
   - Is `execute_duckduckgo_search` the right function to use?
   - Should we check if it exists before importing?
   - Are there other fallback options to consider?

3. **Error Handling:**
   - Is the try/except scope appropriate?
   - Should we catch specific exceptions?
   - What happens if search fails?

4. **Code Duplication:**
   - This code needs to be in BOTH SDK and HTTP paths
   - Should we extract to a helper function?
   - How to avoid duplication?

5. **Performance:**
   - Is regex search efficient enough?
   - Should we cache compiled patterns?
   - Any performance concerns?

6. **Security:**
   - Are there injection risks with the query?
   - Should we sanitize the extracted query?
   - Any other security concerns?

7. **Testing:**
   - How to test this without live API calls?
   - Should we add unit tests?
   - What test cases are critical?

8. **Alternative Approaches:**
   - Is there a better way to handle this?
   - Should we ask GLM to retry with proper format?
   - Should we use a different parsing library?

---

## 📋 IMPLEMENTATION CHECKLIST

- [ ] EXAI validation complete
- [ ] Address EXAI feedback
- [ ] Implement in SDK path (lines 209-212)
- [ ] Implement in HTTP path (lines 281-299)
- [ ] Extract to helper function if recommended
- [ ] Add error handling
- [ ] Add logging
- [ ] Test with Format B examples
- [ ] Test with Format C examples
- [ ] Test with Format D (should gracefully skip)
- [ ] Test with both glm-4.6 and glm-4.5-flash
- [ ] Verify no regressions in tool_calls array path
- [ ] Update documentation
- [ ] Update FIXES_CHECKLIST.md

---

## 🎯 SUCCESS CRITERIA

1. **Functionality:**
   - Format B responses execute web search successfully
   - Format C responses execute web search successfully
   - Format D responses handled gracefully (no crash)
   - Proper tool_calls array responses still work

2. **Reliability:**
   - glm-4.5-flash web search success rate >80%
   - glm-4.6 web search success rate >90%
   - No crashes or exceptions in production

3. **Observability:**
   - Clear logging of which format was detected
   - Success/failure metrics trackable
   - Easy to debug issues

4. **Maintainability:**
   - Code is clear and well-commented
   - No duplication between SDK/HTTP paths
   - Easy to add new formats if needed

---

## 🚨 RISKS & MITIGATION

### Risk 1: Regex Patterns Don't Match All Variations
**Mitigation:** EXAI validation + comprehensive testing + fallback to original text

### Risk 2: DuckDuckGo Search Fails
**Mitigation:** Error handling + logging + return original text

### Risk 3: Performance Impact
**Mitigation:** Regex is fast, search is async, minimal impact expected

### Risk 4: Breaking Existing Functionality
**Mitigation:** Only affects text format path, tool_calls array path unchanged

---

## 📝 NOTES FOR EXAI REVIEW

**Key Questions:**
1. Is this the right approach, or should we handle this differently?
2. Are there edge cases we're missing?
3. Should we extract the query parsing to a separate function?
4. Is the error handling sufficient?
5. Are there security concerns with executing searches from parsed text?
6. Should we add rate limiting or caching?
7. How should we handle Format D (acknowledgment only)?

**Context:**
- This is a workaround for GLM API behavior
- Official docs confirm both models support web_search
- The issue is response format inconsistency, not capability
- We want to maintain compatibility with future API changes

