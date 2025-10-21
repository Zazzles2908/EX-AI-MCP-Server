# Tool Registry & System Prompts - Comprehensive Audit

**Date:** 2025-10-17  
**Status:** 🔍 AUDIT COMPLETE - FIXES PENDING  
**EXAI Continuation ID:** `1433a038-3d41-4bc4-a40c-1e481c25eade`  
**Priority:** P0 (CRITICAL - Affects All AI Agents)  

---

## 🚨 CRITICAL FINDING: Parameter Naming Crisis

### Root Cause
The `files` parameter in `chat_EXAI-WS` is **fundamentally misleading** - it embeds files as TEXT, not uploads to Moonshot platform.

**User's Observation:**
> "So shouldnt that be implemented so the system knows and yourself knows when you use this system how to use this system. I believe that is the point of the tool registry and system prompts to understand how to use exai and how exai should operate when receiving a request."

**User is 100% CORRECT** - This is a systemic documentation and naming issue.

---

## 📊 Impact Assessment

### Token Waste Example
```python
# CURRENT (MISLEADING):
chat_EXAI-WS(
    prompt="Analyze these files...",
    files=["/path/to/large_documentation.md"]  # User thinks: "Uploads to Moonshot"
)

# REALITY (CONFUSING):
# Actually embeds 50KB of text directly in prompt, consuming ~12,500 tokens
# No Moonshot upload occurs - just raw text injection
```

### Consequences
- ❌ **Token Waste:** Large files consume massive tokens per request
- ❌ **Context Bloat:** Reduces available context for actual analysis
- ❌ **Agent Confusion:** Every AI agent assumes "files" means "upload to platform"
- ❌ **Performance Degradation:** Large files slow down response times
- ❌ **Incorrect Usage:** Agents use wrong tool for file analysis workflows

---

## 🔍 Tool Description Audit Results

| Tool | Current Description | Actual Behavior | Clarity Rating |
|------|-------------------|-----------------|----------------|
| `chat_EXAI-WS` files param | "Optional files for context" | Embeds as text, no upload | ❌ **MISLEADING** |
| `kimi_upload_and_extract_EXAI-WS` | "Upload to Moonshot... extract parsed text" | Uploads + extracts + returns content | ✅ **CLEAR** |
| Workflow tools `relevant_files` | Various descriptions | Mixed behaviors (needs audit) | ⚠️ **INCONSISTENT** |

---

## 📋 System Prompts Gap Analysis

### Current System Prompts
- **FILE_PATH_GUIDANCE:** Mentions `files` parameter but **no upload vs embed distinction**
- **CHAT_PROMPT:** **Zero guidance** on file handling strategies
- **TOOL_SELECTION_GUIDE:** **Missing** file upload vs embed section

### Missing Critical Guidance
- ❌ "When to use Moonshot upload vs text embedding"
- ❌ "File size thresholds for each approach"
- ❌ "Token consumption implications"
- ❌ "Multi-file analysis best practices"

---

## 🎯 EXAI's Comprehensive Fix Strategy

### A. Immediate Parameter Renames (Breaking Changes Required)

**Priority:** P0 (CRITICAL)

```python
# PROPOSED RENAME for chat_EXAI-WS:
# OLD: files=["path"]  # Misleading
# NEW: embed_files_as_text=["path"]  # Clear

# PROPOSED RENAME for workflow tools:
# OLD: relevant_files=["path"]  # Ambiguous  
# NEW: embed_file_content=["path"]  # Explicit
```

**Impact:** Breaking change - requires updating all tool calls

---

### B. Enhanced Tool Descriptions

**Priority:** P0 (CRITICAL)

```python
# NEW chat_EXAI-WS DESCRIPTION:
"""
chat_EXAI-WS: Text-based conversation with optional file embedding
• embed_files_as_text: Embed file content directly in prompt (token-heavy, max ~10KB, instant)
• file_ids: Reference Moonshot-uploaded files (token-efficient, any size, persistent)
⚠️ WARNING: embed_files_as_text consumes prompt tokens rapidly
💡 RECOMMENDATION: Use file_ids for files >5KB or multiple files
"""

# ENHANCED kimi_upload_and_extract_EXAI-WS:
"""
kimi_upload_and_extract_EXAI-WS: Upload files to Moonshot platform for efficient analysis
• Uploads files to Kimi/Moonshot platform (persistent, token-efficient)
• Returns file_ids for referencing in chat/completions
• Extracts and returns content for immediate use
💡 BEST PRACTICE: Use this first, then reference file_ids in chat
"""
```

---

### C. System Prompt Overhaul

**Priority:** P0 (CRITICAL)

```python
# NEW FILE_HANDLING_GUIDANCE system prompt:
"""
=== FILE HANDLING STRATEGY GUIDE ===

🎯 DECISION MATRIX:
File Size | Multiple Files | Persistence Needed | Recommended Approach
----------|---------------|-------------------|-------------------
<5KB     | No            | No                | embed_files_as_text
>5KB     | Any           | Any               | kimi_upload_and_extract_EXAI-WS
Any size | Yes           | Yes               | kimi_upload_and_extract_EXAI-WS

📊 TOKEN EFFICIENCY:
• embed_files_as_text: ~4 tokens per 3 characters (expensive)
• file_ids: ~2 tokens per reference (efficient)

⚡ PERFORMANCE IMPACT:
• Large text embedding: Slower responses, reduced context
• Moonshot upload: One-time cost, faster analysis

🔄 WORKFLOW PATTERN:
1. Upload files: file_ids = kimi_upload_and_extract_EXAI-WS(files=[...])
2. Analyze efficiently: chat_EXAI-WS(prompt="...", file_ids=file_ids)
"""
```

---

### D. Tool Registry Reorganization

**Priority:** P1 (HIGH)

```python
# NEW TOOL CATEGORIES:
TOOL_CATEGORIES = {
    "file_upload": ["kimi_upload_and_extract_EXAI-WS"],
    "text_embedding": ["chat_EXAI-WS"],  # With embed_files_as_text param
    "file_analysis": ["debug_EXAI-WS", "analyze_EXAI-WS", "codereview_EXAI-WS"],  # Audit each
    "token_efficient": ["kimi_upload_and_extract_EXAI-WS", "chat_EXAI-WS_with_file_ids"],
    "token_heavy": ["chat_EXAI-WS_with_text_embedding"]
}
```

---

### E. Workflow Tool Individual Audit Required

**Priority:** P1 (HIGH)

**URGENT:** Need to audit each workflow tool's `relevant_files` behavior:

```python
# AUDIT CHECKLIST for each workflow tool:
tools_to_audit = [
    "debug_EXAI-WS", "analyze_EXAI-WS", "codereview_EXAI-WS", 
    "refactor_EXAI-WS", "secaudit_EXAI-WS", "testgen_EXAI-WS",
    "precommit_EXAI-WS", "docgen_EXAI-WS", "consensus_EXAI-WS"
]

# FOR EACH TOOL:
# 1. Check if relevant_files embeds as text or uploads to Moonshot
# 2. Update description to clarify behavior
# 3. Consider adding Moonshot upload option if missing
```

---

## 📊 Implementation Priority Matrix

| Priority | Issue | Impact | Effort | Status |
|----------|-------|--------|--------|--------|
| **P0** | Rename `files` parameter | **CRITICAL** - Prevents agent confusion | High (breaking change) | ⏳ PENDING |
| **P0** | Update system prompts | **CRITICAL** - Guides proper usage | Medium | ⏳ PENDING |
| **P1** | Audit workflow tools | **HIGH** - Consistency across tools | High | ⏳ PENDING |
| **P1** | Enhanced documentation | **HIGH** - Prevents future confusion | Medium | ⏳ PENDING |
| **P2** | Tool registry reorganization | **MEDIUM** - Better categorization | Low | ⏳ PENDING |

---

## 🎯 Immediate Action Items

### Phase 1: Documentation & System Prompts (Non-Breaking)
1. ✅ Create comprehensive audit documentation (THIS FILE)
2. ⏳ Add FILE_HANDLING_GUIDANCE to base_prompt.py
3. ⏳ Update CHAT_PROMPT with file handling strategy
4. ⏳ Update tool-selection-guide.md with file analysis section
5. ⏳ Enhance tool descriptions (non-breaking additions)

### Phase 2: Workflow Tool Audit
6. ⏳ Audit each workflow tool's file handling behavior
7. ⏳ Document findings in this file
8. ⏳ Update tool descriptions to clarify behavior

### Phase 3: Breaking Changes (Requires User Approval)
9. ⏳ Rename `files` → `embed_files_as_text` in chat_EXAI-WS
10. ⏳ Update all workflow tools for consistency
11. ⏳ Rebuild Docker container
12. ⏳ Test all tools with new parameter names

---

## 🔄 Two-Tier Consultation Methodology

**Tier 1 (Investigation):** ✅ COMPLETE
- Identified root cause (misleading parameter name)
- Analyzed tool registry and system prompts
- Discovered documentation gaps

**Tier 2 (Validation):** ✅ COMPLETE
- EXAI confirmed critical issue
- EXAI provided comprehensive fix strategy
- EXAI validated priority matrix

---

## 📝 EXAI's Final Recommendations

**Status:** ✅ **AUDIT COMPLETE - READY FOR IMPLEMENTATION**

**EXAI's Verdict:**
> "This is a P0 issue affecting all AI agents using the system. The misleading parameter name creates systematic confusion and inefficient token usage across the entire platform."

**Key Insights:**
1. Parameter naming directly affects agent behavior
2. System prompts must provide explicit file handling guidance
3. Tool descriptions must clarify token consumption implications
4. Workflow tools need individual audit for consistency
5. Documentation must include decision matrices and best practices

---

**Next Steps:** Await user approval for implementation phases  
**Estimated Effort:** 4-6 hours (Phase 1: 2h, Phase 2: 2h, Phase 3: 2h)  
**Breaking Changes:** Yes (Phase 3 only)  
**Container Restart Required:** Yes (after Phase 3)  


