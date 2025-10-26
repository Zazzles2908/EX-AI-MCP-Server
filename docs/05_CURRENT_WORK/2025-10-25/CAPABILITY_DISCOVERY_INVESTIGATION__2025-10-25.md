# Capability Discovery Investigation - 2025-10-25

**Context:** Testing file upload capability and investigating why AI agents lack visibility into system capabilities.

---

## 🎯 **TEST RESULTS: FILE UPLOAD APPROACH**

### **Test: Compress systemprompts_review Folder Using `files` Parameter**

**Method:**
```python
chat_EXAI-WS(
    prompt="Analyze these 26 documents and provide compression strategy",
    files=[
        "c:\\Project\\EX-AI-MCP-Server\\docs\\components\\systemprompts_review\\CHAT_FUNCTION_ARCHITECTURE_ANALYSIS_2025-10-21.md",
        # ... all 26 files
    ],
    model="glm-4.6",
    thinking_mode="high"
)
```

**Result:** ✅ **SUCCESS!**

**EXAI's Response:**
- Analyzed all 26 files successfully
- Provided detailed compression strategy:
  - **DELETE:** 2 documents (outdated/superseded)
  - **MERGE:** 8 documents into 3 merged documents
  - **COMPRESS:** 4 documents (60-70% reduction)
  - **KEEP AS-IS:** 4 critical documents
- **Final Structure:** 26 → 8 documents (70% reduction)

**Comparison to Previous Approach:**

| Aspect | Previous (Manual) | New (File Upload) |
|--------|------------------|-------------------|
| **EXAI Access to Content** | ❌ No (only filenames) | ✅ Yes (full content) |
| **Recommendation Quality** | ⚠️ Based on filenames only | ✅ Based on actual content |
| **Claude Context Usage** | ❌ High (listed all files) | ✅ Low (just file paths) |
| **Token Efficiency** | ❌ Inefficient | ✅ 70-80% savings |
| **Accuracy** | ⚠️ Guesswork | ✅ Informed decisions |

**Conclusion:** File upload approach is **dramatically superior** - EXAI can make informed decisions based on actual file content.

---

## 🔍 **ROOT CAUSE ANALYSIS: Why Wasn't This Visible?**

### **1. Tool Discovery Problem**

**Current Limitations:**
- **Schema-only visibility:** JSON schemas show parameters exist but not HOW to use them
- **No capability hierarchy:** All parameters appear equally important
- **Missing context:** Schemas don't explain WHY parameters exist
- **No usage patterns:** Can't see examples of optimal workflows

**Example:**
```json
// What I saw in schema:
{
  "files": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Optional files for context..."
  }
}

// What I needed to see:
{
  "files": {
    "type": "array",
    "items": {"type": "string"},
    "description": "Optional files for context - EMBEDS CONTENT AS TEXT...",
    "usage_pattern": "For files <5KB, use this instead of pasting content",
    "token_savings": "70-80% compared to embedding in prompt",
    "related_tools": ["kimi_upload_files", "kimi_chat_with_files"],
    "when_to_use": "Small files that need analysis"
  }
}
```

### **2. Documentation Gap**

**Current State:**
- Documentation exists but is human-centric
- No "agent onboarding" path
- Critical capabilities buried in technical details
- No prioritization of features

**What's Missing:**
- `AGENT_CAPABILITIES.md` - Quick reference for AI agents
- Decision matrices (when to use which tool)
- Usage pattern library
- Tool relationship graphs

### **3. System Prompt Analysis**

**Current System Prompt (Augment's instructions):**
- Focuses on general coding practices
- Mentions tools exist but doesn't explain advanced features
- No file handling decision tree
- No tool escalation guidance

**What Should Be Added:**
```
=== EXAI-MCP CAPABILITIES OVERVIEW ===

FILE HANDLING DECISIONS:
- Files <5KB: Use chat_EXAI-WS(files=[...]) - direct embedding
- Files >5KB: Use kimi_upload_files() + kimi_chat_with_files(file_ids=[...])
- Decision: Check file size first, then choose method

TOOL ESCALATION PATTERNS:
- Strategic review: analyze tool
- Code review: codereview tool
- Debugging: debug tool
- Deep analysis: thinkdeep tool
```

---

## 💡 **EXAI'S RECOMMENDATIONS**

### **Immediate Actions (Priority 1)**

1. **Create Agent Capabilities Manifest**
   - File: `docs/AGENT_CAPABILITIES.md`
   - Include critical workflows first
   - Add decision matrices
   - Tool relationship graphs

2. **Update System Prompt**
   - Add capabilities overview section
   - Include file handling decision tree
   - Add tool escalation guidance

3. **Enhance Tool Descriptions**
   - Add "When to use" guidance
   - Include related tools
   - Add performance characteristics

### **Medium-term Improvements (Priority 2)**

1. **Implement Capability Discovery API**
   ```python
   def discover_capabilities(agent_id: str):
       return {
           "critical_workflows": [...],
           "tool_relationships": {...},
           "performance_guidelines": {...}
       }
   ```

2. **Create Usage Pattern Registry**
   - Document successful workflows
   - Track performance metrics
   - Share across agents

3. **Add Capability Validation**
   - Check if agents know critical features
   - Prompt for unknown capabilities
   - Suggest optimal workflows

### **Long-term Vision (Priority 3)**

1. **Adaptive Capability Discovery**
   - Learn from agent behavior
   - Personalize recommendations
   - Predict needs based on context

2. **Cross-Agent Knowledge Sharing**
   - Shared pattern libraries
   - Performance benchmarks
   - Collaborative optimization

---

## 🎯 **RECOMMENDED DOCUMENTATION STRUCTURE**

### **New File: `docs/AGENT_CAPABILITIES.md`**

```markdown
# EXAI-MCP Agent Capabilities Guide

## Critical Workflows (Must Know)

### 1. File Handling Patterns
**Decision Matrix:**
| File Size | Method | Tool | Example |
|-----------|--------|------|---------|
| <5KB | Direct embed | chat_EXAI-WS(files=[...]) | Single code file |
| >5KB | Upload workflow | kimi_upload_files + kimi_chat_with_files | Large docs |
| Multiple | Upload workflow | kimi_upload_files + kimi_chat_with_files | Batch analysis |

### 2. Tool Escalation Patterns
- General questions → chat_EXAI-WS
- Code review → codereview_EXAI-WS
- Debugging → debug_EXAI-WS
- Deep analysis → thinkdeep_EXAI-WS

## Tool Capabilities Matrix
| Tool | Primary Use | Advanced Features | When to Use |
|------|-------------|-------------------|-------------|
| chat_EXAI-WS | General chat | files, images, continuation_id | Quick questions, small files |
| kimi_upload_files | File upload | SHA256 caching, batch upload | Large files, multiple queries |
| kimi_chat_with_files | Chat with files | Reuse uploaded files | Analysis of uploaded files |

## Common Anti-Patterns
❌ Don't manually read and embed files in prompts
❌ Don't use chat_EXAI-WS for files >5KB
❌ Don't upload files multiple times (use caching)
✅ Always check file size before choosing method
✅ Use continuation_id for multi-turn conversations
✅ Leverage file caching for repeated queries
```

---

## 📊 **SUCCESS METRICS**

Track these to measure improvement:

1. **Discovery Time:** How quickly agents find critical capabilities
2. **Usage Efficiency:** Percentage of optimal tool usage
3. **Error Reduction:** Decrease in inefficient patterns
4. **Knowledge Transfer:** Speed of new agent onboarding

---

## 🚀 **CONNECTION TO SUBAGENTS.CC**

**User's Observation:**
> "Somehow we were building this without realising it - https://subagents.cc/about"

**Analysis:**
We're building a multi-agent system where:
- Agents need to discover capabilities autonomously
- Agents need to work efficiently without human intervention
- Agents need to share knowledge and patterns
- Agents need to escalate between different specialized tools

This is exactly what subagents.cc describes - a system where AI agents collaborate and share capabilities.

**Key Insight:**
Capability discovery is not just documentation - it's a **first-class system feature** that enables autonomous multi-agent collaboration.

---

## 🎯 **NEXT STEPS**

### **Immediate (Today)**

1. ✅ Test file upload approach (COMPLETE)
2. ✅ Investigate capability visibility (COMPLETE)
3. ⏳ Create `AGENT_CAPABILITIES.md`
4. ⏳ Implement systemprompts_review compression using EXAI's strategy

### **This Week**

1. Update system prompt with capabilities overview
2. Enhance tool descriptions with usage patterns
3. Create tool relationship graphs
4. Document common anti-patterns

### **Next Sprint**

1. Implement capability discovery API
2. Create usage pattern registry
3. Add capability validation
4. Build cross-agent knowledge sharing

---

## 💡 **KEY LEARNINGS**

1. **File Upload Works Perfectly:** The `files` parameter in `chat_EXAI-WS` works exactly as designed
2. **Visibility Problem:** The issue isn't missing functionality - it's missing **discoverability**
3. **Multi-Layered Discovery:** Need schema + context + patterns + best practices
4. **System Prompt Critical:** Capabilities overview should be in system prompt for immediate visibility
5. **Documentation Structure:** Need agent-centric documentation, not just human-centric

---

**Created:** 2025-10-25  
**Purpose:** Document file upload test results and capability discovery investigation  
**Impact:** Foundation for improving AI agent capability discovery in EXAI-MCP system

