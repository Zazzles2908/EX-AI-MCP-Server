# EXAI Web Search Usage Guide

**Version:** 1.0  
**Last Updated:** 2025-01-XX (Wave 1, Epic 1.2)  
**Purpose:** Guide to using web search effectively with EXAI tools

---

## Overview

EXAI tools support web search through two mechanisms:
1. **Direct web-search tool** - Reliable, recommended approach
2. **chat_EXAI-WS with use_websearch=true** - Has known issues (see below)

**Recommendation:** Use the `web-search` tool directly for reliable results.

---

## Tool Autonomy Explanation

### Why chat_EXAI-WS Doesn't Auto-Search Reliably

**Expected Behavior:**
When `use_websearch=true` is set, the chat tool should autonomously:
1. Detect when web search is needed
2. Execute searches without user intervention
3. Integrate search results into responses
4. Provide complete, synthesized answers

**Actual Behavior (Known Issue):**
- ✅ Web search DOES execute (confirmed by metadata)
- ❌ Results are NOT integrated into response
- ❌ Response ends with "AGENT'S TURN" message
- ❌ User receives incomplete information

**Root Cause:**
Response truncation occurs before search results are synthesized. The search executes successfully (visible in `tool_call_events` metadata), but the results aren't extracted and integrated into the final response.

**Example of Issue:**
```json
// Request
{
  "prompt": "What are the latest features in zai-sdk version 0.0.4?",
  "use_websearch": true
}

// Response (Incomplete)
{
  "content": "I'll help you find information about zai-sdk v0.0.4...
  
  ---
  
  AGENT'S TURN: Evaluate this perspective...",
  "metadata": {
    "tool_call_events": [
      {"tool_name": "web_search", "provider": "kimi"}  // Search DID execute
    ]
  }
}
```

**Impact:**
- MEDIUM severity (slows workflow but doesn't block)
- Affects all research tasks using chat_EXAI-WS
- Workaround available (use web-search tool directly)

**Status:**
- Documented in: `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 1
- Planned fix: Wave 2 (Epic 2.2 - Web Search Prompt Injection Fix)
- Priority: CRITICAL (highest priority for Wave 2)

---

## Recommended Approach: Use web-search Tool

### Basic Usage

**Tool:** `web-search`  
**Parameters:**
- `query` (required): Search query string
- `num_results` (optional, default: 5): Number of results (1-10)

**Example:**
```json
{
  "query": "zai-sdk version 0.0.4 features and API endpoints",
  "num_results": 5
}
```

**Response:**
Returns markdown-formatted search results with:
- URL
- Title
- Snippet (if available)

---

## Query Types and Expected Behavior

### Queries That Should Trigger Web Search

#### 1. Current Information Queries
**Characteristics:** Time-sensitive, recent events, latest versions

**Examples:**
```json
// Example 1: Latest version information
{"query": "zai-sdk version 0.0.4 changelog"}

// Example 2: Current specifications
{"query": "GLM-4.6 model specifications context window"}

// Example 3: Recent updates
{"query": "api.z.ai latest API endpoints 2025"}

// Example 4: Current pricing
{"query": "ZhipuAI GLM-4.6 pricing per token"}

// Example 5: Latest documentation
{"query": "Moonshot Kimi API documentation latest"}
```

**Expected Behavior:**
- ✅ Returns current, up-to-date information
- ✅ Includes official documentation links
- ✅ Shows recent changes and updates

---

#### 2. External Documentation Queries
**Characteristics:** SDK docs, API references, official guides

**Examples:**
```json
// Example 6: SDK documentation
{"query": "zai-sdk Python installation guide"}

// Example 7: API reference
{"query": "api.z.ai chat completions endpoint documentation"}

// Example 8: Official examples
{"query": "ZhipuAI GLM streaming examples"}

// Example 9: Integration guides
{"query": "Kimi API integration best practices"}

// Example 10: Migration guides
{"query": "zai-sdk v0.0.3.3 to v0.0.4 migration guide"}
```

**Expected Behavior:**
- ✅ Returns official documentation
- ✅ Includes code examples
- ✅ Shows API specifications

---

#### 3. Best Practices and Patterns
**Characteristics:** Industry standards, design patterns, recommendations

**Examples:**
```json
// Example 11: Best practices
{"query": "Python async streaming best practices"}

// Example 12: Design patterns
{"query": "dual SDK HTTP fallback pattern implementation"}

// Example 13: Security practices
{"query": "API key management best practices Python"}

// Example 14: Performance optimization
{"query": "WebSocket server performance optimization"}

// Example 15: Error handling
{"query": "Python error handling patterns for API clients"}
```

**Expected Behavior:**
- ✅ Returns industry best practices
- ✅ Includes expert recommendations
- ✅ Shows real-world examples

---

### Queries That Should NOT Trigger Web Search

#### 1. Internal Code Questions
**Characteristics:** Questions about YOUR codebase, local implementation

**Examples:**
```json
// Example 1: Internal architecture
{"prompt": "How does our provider architecture work?"}
// Use: analyze_EXAI-WS instead

// Example 2: Local implementation
{"prompt": "Explain the dual SDK/HTTP pattern in glm_chat.py"}
// Use: analyze_EXAI-WS instead

// Example 3: Code review
{"prompt": "Review our authentication implementation"}
// Use: codereview_EXAI-WS instead

// Example 4: Debugging
{"prompt": "Why is streaming not working in our code?"}
// Use: debug_EXAI-WS instead

// Example 5: Local file analysis
{"prompt": "What functions are in server.py?"}
// Use: view tool or analyze_EXAI-WS instead
```

**Why NOT web search:**
- Your internal code is not indexed on the web
- Web search returns generic information, not YOUR implementation
- Use code analysis tools instead

---

#### 2. General Knowledge Questions
**Characteristics:** Well-established concepts, definitions, explanations

**Examples:**
```json
// Example 6: Definitions
{"prompt": "What is a WebSocket?"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 7: Concepts
{"prompt": "Explain the difference between async and sync"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 8: Comparisons
{"prompt": "Compare REST API vs WebSocket"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 9: Explanations
{"prompt": "How does token-based authentication work?"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 10: Tutorials
{"prompt": "Explain Python async/await"}
// Use: chat_EXAI-WS with use_websearch=false
```

**Why NOT web search:**
- Model already has this knowledge
- Faster response without web search
- More concise, focused answers

---

#### 3. Hypothetical or Opinion Questions
**Characteristics:** Brainstorming, what-if scenarios, trade-off analysis

**Examples:**
```json
// Example 11: Trade-offs
{"prompt": "What are the trade-offs of using zai-sdk vs direct HTTP?"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 12: Brainstorming
{"prompt": "What are alternative approaches to streaming?"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 13: Opinions
{"prompt": "Should we upgrade to zai-sdk v0.0.4 now?"}
// Use: consensus_EXAI-WS for multi-perspective analysis

// Example 14: Hypotheticals
{"prompt": "What if we switched from WebSocket to HTTP polling?"}
// Use: chat_EXAI-WS with use_websearch=false

// Example 15: Evaluations
{"prompt": "Is our current architecture scalable?"}
// Use: analyze_EXAI-WS for code-based analysis
```

**Why NOT web search:**
- Requires reasoning, not facts
- Context-specific to your situation
- Better handled by model's reasoning capabilities

---

## Workaround for chat_EXAI-WS Web Search Issue

### Problem
When using `chat_EXAI-WS` with `use_websearch=true`, you get incomplete responses.

### Solution: Use web-search Tool Directly

**Step 1: Execute Web Search**
```json
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 features",
  "num_results": 5
}
```

**Step 2: Use Results with chat_EXAI-WS**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Based on these search results about zai-sdk v0.0.4: [paste results], summarize the key features",
  "use_websearch": false
}
```

**Alternative: Use chat_EXAI-WS for Synthesis Only**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "I found these features in zai-sdk v0.0.4 documentation: GLM-4.6 support, video generation, assistant API. Explain how these compare to v0.0.3.3",
  "use_websearch": false
}
```

---

## Query Optimization Tips

### 1. Be Specific
**Bad:** `{"query": "SDK"}`  
**Good:** `{"query": "zai-sdk version 0.0.4 Python installation guide"}`

### 2. Use Exact Phrases
**Bad:** `{"query": "GLM model info"}`  
**Good:** `{"query": "\"GLM-4.6\" specifications context window pricing"}`

### 3. Include Version Numbers
**Bad:** `{"query": "zai-sdk features"}`  
**Good:** `{"query": "zai-sdk version 0.0.4 new features changelog"}`

### 4. Specify Source When Needed
**Bad:** `{"query": "API documentation"}`  
**Good:** `{"query": "api.z.ai official documentation chat completions"}`

### 5. Combine Related Terms
**Bad:** `{"query": "streaming"}`  
**Good:** `{"query": "Python async streaming SSE text/event-stream"}`

---

## Expected Behavior by Query Type

| Query Type | Tool | use_websearch | Expected Result |
|------------|------|---------------|-----------------|
| Latest SDK version | web-search | N/A | Current version info from PyPI/GitHub |
| API documentation | web-search | N/A | Official docs with examples |
| Internal code | analyze_EXAI-WS | N/A | Code analysis from YOUR files |
| General concept | chat_EXAI-WS | false | Explanation from model knowledge |
| Best practices | web-search | N/A | Industry recommendations |
| Debugging | debug_EXAI-WS | N/A | Root cause analysis |
| Trade-offs | chat_EXAI-WS | false | Reasoning-based analysis |
| Current pricing | web-search | N/A | Latest pricing from official sources |

---

## Common Mistakes and Solutions

### Mistake 1: Using chat_EXAI-WS for External Research
**Problem:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "What are the latest features in zai-sdk v0.0.4?",
  "use_websearch": true
}
// Result: Incomplete response
```

**Solution:**
```json
{
  "tool": "web-search",
  "query": "zai-sdk version 0.0.4 features changelog"
}
// Result: Complete search results
```

---

### Mistake 2: Using web-search for Internal Code
**Problem:**
```json
{
  "tool": "web-search",
  "query": "how does glm_chat.py work"
}
// Result: Generic information, not YOUR code
```

**Solution:**
```json
{
  "tool": "analyze_EXAI-WS",
  "step": "Analyze glm_chat.py implementation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
// Result: Analysis of YOUR actual code
```

---

### Mistake 3: Vague Search Queries
**Problem:**
```json
{
  "query": "API"
}
// Result: Too broad, irrelevant results
```

**Solution:**
```json
{
  "query": "api.z.ai chat completions endpoint documentation parameters"
}
// Result: Specific, relevant results
```

---

### Mistake 4: Using Web Search for Definitions
**Problem:**
```json
{
  "tool": "web-search",
  "query": "what is async programming"
}
// Result: Slower, unnecessary web search
```

**Solution:**
```json
{
  "tool": "chat_EXAI-WS",
  "prompt": "Explain async programming in Python",
  "use_websearch": false
}
// Result: Faster, focused explanation
```

---

### Mistake 5: Not Specifying num_results
**Problem:**
```json
{
  "query": "zai-sdk documentation"
}
// Result: Default 5 results (might miss important info)
```

**Solution:**
```json
{
  "query": "zai-sdk documentation",
  "num_results": 10
}
// Result: More comprehensive results
```

---

## Troubleshooting

### Issue: "AGENT'S TURN" Message in chat_EXAI-WS
**Symptom:** Response ends with "AGENT'S TURN: Evaluate this perspective..."

**Cause:** Known web search integration issue

**Solution:** Use `web-search` tool directly instead

**Status:** Fix planned for Wave 2 (Epic 2.2)

---

### Issue: No Results Found
**Symptom:** Web search returns empty or irrelevant results

**Possible Causes:**
1. Query too specific or contains typos
2. Searching for internal/private information
3. Using wrong terminology

**Solutions:**
1. Broaden query or check spelling
2. Use code analysis tools for internal code
3. Try alternative search terms

---

### Issue: Results Not Relevant
**Symptom:** Search results don't match what you need

**Solutions:**
1. Add more specific terms to query
2. Use exact phrases in quotes
3. Include version numbers or product names
4. Specify source (e.g., "official documentation")

---

## Best Practices

### ✅ DO:
- Use `web-search` tool for external documentation
- Be specific in search queries
- Include version numbers when relevant
- Use exact phrases for technical terms
- Specify num_results for comprehensive research
- Combine web search with chat for synthesis

### ❌ DON'T:
- Use `chat_EXAI-WS` with `use_websearch=true` (known issue)
- Search for internal code (use analyze tools instead)
- Use vague, generic queries
- Search for well-known concepts (use chat instead)
- Forget to specify source when needed

---

## Quick Reference

**For External Documentation:**
```json
{"tool": "web-search", "query": "specific search terms", "num_results": 5}
```

**For Internal Code:**
```json
{"tool": "analyze_EXAI-WS", "relevant_files": ["c:\\Project\\..."]}
```

**For General Knowledge:**
```json
{"tool": "chat_EXAI-WS", "prompt": "question", "use_websearch": false}
```

**For Synthesis:**
```json
// Step 1: Search
{"tool": "web-search", "query": "..."}

// Step 2: Synthesize
{"tool": "chat_EXAI-WS", "prompt": "Based on these results: ...", "use_websearch": false}
```

---

## Related Documentation

- **Tool Selection:** See `tool-selection-guide.md` for choosing the right tool
- **Parameters:** See `parameter-reference.md` for detailed parameter documentation
- **Examples:** See `query-examples.md` for 20+ working examples
- **Troubleshooting:** See `troubleshooting.md` for common issues
- **UX Issues:** See `docs/upgrades/international-users/exai-tool-ux-issues.md` Section 1 for detailed web search issue analysis

---

## Future Improvements (Wave 2)

**Epic 2.2: Web Search Prompt Injection Fix**
- Fix response completion in chat_EXAI-WS
- Ensure search results are integrated
- Test single-turn vs multi-turn usage
- Eliminate "AGENT'S TURN" incomplete responses

**Priority:** CRITICAL (highest priority for Wave 2)

**Expected Timeline:** Wave 2 (Weeks 1-2)

---

**Document Status:** ✅ COMPLETE (Task 1.3)  
**Validation:** Pending codereview_EXAI-WS  
**Query Examples:** 15+ trigger search, 15+ don't trigger search (30+ total)

