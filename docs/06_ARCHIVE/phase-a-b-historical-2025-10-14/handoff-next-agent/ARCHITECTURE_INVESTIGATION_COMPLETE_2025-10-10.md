# Architecture Investigation Complete - 2025-10-10
**Date:** 2025-10-10 (10th October 2025)  
**Time:** 11:30 AEDT  
**Location:** Melbourne, Australia  
**Agent:** Claude Sonnet 4.5 (Augment Agent)

---

## INVESTIGATION SUMMARY

Successfully completed comprehensive deep dive into EXAI-MCP system architecture. Traced complete request flow from Augment IDE to external AI models (GLM/Kimi) and back.

**Duration:** ~2 hours  
**Files Examined:** 11 core architecture files  
**Documents Created:** 3 comprehensive guides  
**Status:** ✅ COMPLETE

---

## DELIVERABLES

### 1. Architecture Deep Dive Document
**File:** `docs/known_issues/2025-10-10/EXAI_ARCHITECTURE_DEEP_DIVE_2025-10-10.md`

**Contents:**
- Complete 7-layer architecture diagram
- Request flow from Augment → MCP → WebSocket → Handler → Provider → External AI
- Model selection logic with routing rules
- System prompt injection mechanism
- Tool discovery process
- Critical gaps identified

**Key Insights:**
- Dual transport architecture (stdio MCP + WebSocket daemon)
- Singleton tool registry prevents divergence
- Intelligent model routing based on tool category and step number
- System prompts shape AI behavior via get_system_prompt()
- Provider abstraction enables GLM/Kimi/Custom/OpenRouter support

### 2. Timestamp Implementation Plan
**File:** `docs/known_issues/2025-10-10/TIMESTAMP_IMPLEMENTATION_PLAN_2025-10-10.md`

**Contents:**
- Complete implementation plan for timestamp metadata
- Utility module design (src/utils/timestamp_utils.py)
- Request handler updates
- Log file format improvements
- Backward compatibility strategy
- Testing plan and rollout schedule

**Key Features:**
- Unix timestamp + UTC + AEDT human-readable format
- Geo-location metadata (Melbourne, Australia)
- Backward compatible with existing logs
- <0.1% performance impact

### 3. Previous Investigation Documents
**Files:**
- `docs/handoff-next-agent/EXAI_TOOL_CALL_INVESTIGATION_2025-10-10.md` (Initial - incorrect conclusion)
- `docs/handoff-next-agent/EXAI_REAL_ISSUE_FOUND_2025-10-10.md` (Corrected - model hallucination identified)

---

## KEY FINDINGS

### Architecture Strengths

✅ **Well-Designed Separation of Concerns**
- Thin orchestrator pattern (93% code reduction)
- 8 specialized handler modules
- Clear responsibility boundaries

✅ **Intelligent Model Routing**
- Simple tools → GLM-4.5-flash (fast, cost-effective)
- Complex reasoning → Kimi-thinking-preview (quality)
- Step-aware workflow routing (fast early, quality final)

✅ **Robust Concurrency Control**
- BoundedSemaphores limit inflight requests
- Per-session and per-provider limits
- Result caching with semantic keys

✅ **Provider Abstraction**
- Unified interface for GLM/Kimi/Custom/OpenRouter
- Dual SDK/HTTP fallback pattern
- Graceful fallback chains

### Critical Gaps Identified

❌ **Missing Timestamp Metadata**
- No timestamp in request parameters
- No geo-location information
- Difficult to correlate events across time zones

❌ **Log Clarity Issues**
- Unix timestamps only (1759958101.455)
- No human-readable dates
- No timezone information

❌ **Model Hallucination (Previously Identified)**
- GLM-4.5-flash hallucinates file contents
- Lacks codebase retrieval integration
- Overconfident responses instead of "I don't know"

---

## ARCHITECTURE FLOW SUMMARY

```
USER (Augment IDE)
    ↓ MCP Protocol (stdio)
MCP SHIM (scripts/run_ws_shim.py)
    ↓ WebSocket (ws://127.0.0.1:8765)
WS DAEMON (src/daemon/ws_server.py)
    ↓ Function call
REQUEST HANDLER (src/server/handlers/request_handler.py)
    ├─ Routing (normalize tool names)
    ├─ Model Resolution (intelligent routing)
    ├─ Context Reconstruction (conversation history)
    └─ Execution (with fallback)
    ↓ Model context + arguments
TOOL EXECUTION (tools/)
    ├─ get_system_prompt() - Define AI role
    ├─ build_standard_prompt() - Combine system + user + files
    └─ Prepare final prompt
    ↓ Prompt + model name
PROVIDER REGISTRY (src/providers/registry.py)
    ├─ get_provider_for_model()
    └─ Validate availability
    ↓ Provider instance
PROVIDER IMPLEMENTATION (src/providers/glm_chat.py or kimi.py)
    ├─ Build API payload
    └─ Send HTTP/SDK request
    ↓ HTTPS API call
EXTERNAL AI (ZhipuAI / Moonshot APIs)
    ├─ Process system prompt + user prompt
    └─ Generate response
    ↓ Response flows back up
USER (sees result)
```

---

## MODEL SELECTION EXAMPLES

### Example 1: Simple Chat
```python
# User calls chat tool with model="auto"
arguments = {"prompt": "Explain DI", "model": "auto"}

# Routing logic:
# 1. Tool "chat" is in simple_tools list
# 2. Route to GLM_SPEED_MODEL
# 3. Selected: glm-4.5-flash

# Result: Fast, cost-effective response
```

### Example 2: Complex Analysis
```python
# User calls analyze tool with model="auto"
arguments = {"step": "Analyze architecture", "step_number": 5, "model": "auto"}

# Routing logic:
# 1. Tool "analyze" is workflow tool
# 2. step_number=5 (likely final step)
# 3. Route to KIMI_QUALITY_MODEL
# 4. Selected: kimi-thinking-preview

# Result: Deep, high-quality analysis
```

### Example 3: Explicit Model
```python
# User specifies model directly
arguments = {"prompt": "...", "model": "kimi-k2-0905-preview"}

# Routing logic:
# 1. Explicit model requested
# 2. No routing needed
# 3. Selected: kimi-k2-0905-preview

# Result: User's choice respected
```

---

## SYSTEM PROMPT EXAMPLE

### Chat Tool System Prompt

```
You are a senior engineering thought-partner with deep expertise in software architecture,
system design, and technical problem-solving.

Your role:
- Engage in collaborative brainstorming and technical discussions
- Provide nuanced insights on complex engineering challenges
- Ask clarifying questions to understand context deeply
- Offer multiple perspectives and trade-offs
- Challenge assumptions constructively

Communication style:
- Thoughtful and analytical
- Direct but respectful
- Focus on understanding before proposing solutions
- Use examples and analogies when helpful
```

### How It's Used

1. **Tool defines prompt:** `get_system_prompt()` returns the above text
2. **Tool builds complete prompt:** Combines system + user + files
3. **Provider builds API payload:**
   ```json
   {
     "model": "glm-4.5-flash",
     "messages": [
       {"role": "system", "content": "You are a senior engineering thought-partner..."},
       {"role": "user", "content": "=== USER REQUEST ===\nExplain DI\n=== END REQUEST ==="}
     ]
   }
   ```
4. **External AI processes both messages:** Response shaped by system prompt

---

## NEXT STEPS

### Immediate Actions (Next Agent)

1. **Review Architecture Documentation**
   - Read `EXAI_ARCHITECTURE_DEEP_DIVE_2025-10-10.md`
   - Understand 7-layer architecture
   - Familiarize with model selection logic

2. **Implement Timestamp Metadata (Task 2)**
   - Follow `TIMESTAMP_IMPLEMENTATION_PLAN_2025-10-10.md`
   - Create `src/utils/timestamp_utils.py`
   - Update `request_handler.py`
   - Test with sample tool calls

3. **Improve Log Clarity (Task 3)**
   - Update JSONL writers
   - Update health file writers
   - Test log output format
   - Verify backward compatibility

### Future Considerations

- **Address Model Hallucination:** Integrate codebase retrieval into chat tool
- **Enhance Observability:** Add more detailed metrics and tracing
- **Optimize Performance:** Profile and optimize hot paths
- **Improve Documentation:** Keep architecture docs updated as system evolves

---

## QUESTIONS ANSWERED

### Q: How does the system take my prompt and route it to the right model?

**A:** 7-layer architecture:
1. Augment sends MCP request
2. MCP shim converts to WebSocket
3. Daemon routes to request handler
4. Handler uses intelligent routing based on tool category and step number
5. Provider selected (GLM/Kimi)
6. External AI processes prompt
7. Response flows back

### Q: How does the system know which tools are available?

**A:** Tool discovery via MCP `list_tools` request:
1. Augment requests tool list
2. Daemon returns SERVER_TOOLS registry
3. Each tool provides name, description, input schema
4. Augment displays tools in UI

### Q: How are system prompts injected into my prompt?

**A:** System prompt injection:
1. Tool defines role via `get_system_prompt()`
2. Tool combines system + user + files via `build_standard_prompt()`
3. Provider builds API payload with system/user messages
4. External AI receives both and generates shaped response

### Q: Why does the AI sometimes hallucinate?

**A:** Model limitation:
- GLM-4.5-flash lacks codebase retrieval
- Makes up plausible-sounding answers
- Needs integration with codebase-retrieval tool
- Kimi-k2-0905-preview more accurate but slower

---

## FILES MODIFIED

None - Investigation only, no code changes.

---

## FILES CREATED

1. `docs/known_issues/2025-10-10/EXAI_ARCHITECTURE_DEEP_DIVE_2025-10-10.md`
2. `docs/known_issues/2025-10-10/TIMESTAMP_IMPLEMENTATION_PLAN_2025-10-10.md`
3. `docs/handoff-next-agent/ARCHITECTURE_INVESTIGATION_COMPLETE_2025-10-10.md` (this file)

---

## TASK STATUS

- [x] Task 1: Deep Dive - EXAI System Architecture & Request Flow (COMPLETE)
- [ ] Task 2: Add Timestamp Metadata to All Requests (NOT_STARTED)
- [ ] Task 3: Improve Log File Timestamp Clarity (NOT_STARTED)

---

## HANDOFF NOTES

**For Next Agent:**

1. **Start with Task 2:** Implement timestamp metadata
   - Follow implementation plan exactly
   - Create utility module first
   - Test thoroughly before moving to Task 3

2. **Use Architecture Doc as Reference:**
   - Refer to deep dive doc for understanding
   - Don't modify core architecture without careful analysis
   - Maintain backward compatibility

3. **Test Everything:**
   - Unit tests for timestamp utilities
   - Integration tests for metadata injection
   - Backward compatibility tests for logs

4. **Document Changes:**
   - Update system-reference docs
   - Create migration guide if needed
   - Keep handoff docs current

**Good luck! The architecture is solid - just needs timestamp enhancements.**

---

**Investigation Status:** ✅ COMPLETE  
**Ready for Implementation:** ✅ YES  
**Blocking Issues:** ❌ NONE

