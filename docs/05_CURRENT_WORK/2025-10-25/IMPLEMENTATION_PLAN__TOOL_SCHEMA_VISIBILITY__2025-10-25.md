# Implementation Plan - Tool Schema Visibility Enhancement - 2025-10-25

**Date:** 2025-10-25  
**Purpose:** Implement EXAI's recommendations for enhancing tool schema visibility  
**EXAI Continuation ID:** `823af7e0-30d4-4842-b328-9736d2ed0b18` (13 turns remaining)

---

## 🎯 **OBJECTIVE**

Enhance tool schemas so Claude (AI agent) can discover capabilities like file uploads, continuation_id, model selection, etc. **directly from tool schemas** without needing markdown documentation.

---

## 📋 **EXAI'S IMPLEMENTATION STRATEGY**

### **Phase 1: Enhanced Field Descriptions** (Immediate Impact)

**File:** `tools/shared/base_models.py`

**Changes:**
- Enhance `COMMON_FIELD_DESCRIPTIONS` with decision matrices
- Add `files` parameter: <5KB threshold, 70-80% token savings
- Add `continuation_id`: Multi-turn conversation patterns
- Add `model`: Selection guide (glm-4.6 vs glm-4.5-flash)
- Add `use_websearch`: When to enable

**Example:**
```python
COMMON_FIELD_DESCRIPTIONS = {
    "files": (
        "Optional files for context - EMBEDS CONTENT AS TEXT in prompt. "
        "DECISION MATRIX: Use 'files' for <5KB files. "
        "For >5KB files, use 'kimi_upload_files' tool instead. "
        "BENEFITS: Saves 70-80% tokens, enables persistent reference. "
        "EXAMPLE: files=['/app/src/main.py'] for quick review."
    ),
    "continuation_id": (
        "Thread continuation ID for multi-turn conversations. "
        "USAGE PATTERN: Maintains context across multiple tool calls. "
        "HOW IT WORKS: Automatically retrieves conversation history. "
        "EXAMPLE: First call returns continuation_id='abc123', "
        "subsequent calls include this parameter. "
        "BENEFIT: Enables coherent multi-turn workflows."
    ),
    ...
}
```

---

### **Phase 2: Enhanced Input Schema** (High Impact)

**File:** `tools/shared/base_tool_core.py`

**Changes:**
- Add `get_enhanced_input_schema()` method
- Extend base schema with:
  - `x-capability-hints`: Usage guidance for complex parameters
  - `x-related-tools`: Suggested tool transitions
  - `x-decision-matrix`: Clear decision criteria
  - `x-examples`: Common usage patterns

**Example:**
```python
def get_enhanced_input_schema(self) -> dict[str, Any]:
    base_schema = self.get_input_schema()
    
    # Add capability hints to file parameters
    if "files" in base_schema.get("properties", {}):
        base_schema["properties"]["files"]["x-capability-hints"] = {
            "threshold": "5KB",
            "alternative_tool": "kimi_upload_files",
            "benefit": "Saves 70-80% tokens"
        }
    
    # Add tool relationship metadata
    base_schema["x-related-tools"] = {
        "escalation": ["analyze", "codereview", "debug"],
        "alternatives": ["thinkdeep", "planner"]
    }
    
    return base_schema
```

---

### **Phase 3: Tool Description Enhancement** (Polish)

**File:** `tools/chat.py` (and similar for other tools)

**Changes:**
- Add capability sections to `get_description()`
- Include usage examples
- Document escalation patterns
- Add anti-patterns

**Example:**
```python
def get_description(self) -> str:
    return (
        "GENERAL CHAT & COLLABORATIVE THINKING\\n\\n"
        "✅ USE THIS FOR:\\n"
        "- General questions and explanations\\n"
        "- Brainstorming and ideation\\n\\n"
        "❌ DON'T USE THIS FOR:\\n"
        "- Code review (use codereview_EXAI-WS instead)\\n\\n"
        "🔧 CAPABILITIES:\\n"
        "- File context: Use 'files' for <5KB files\\n"
        "- Multi-turn: Use 'continuation_id' to maintain context\\n"
        "- Web search: Enable with 'use_websearch=true'\\n\\n"
        "📊 WORKFLOW ESCALATION: chat → analyze → codereview → debug"
    )
```

---

### **Phase 4: Integration Point**

**File:** `src/server/handlers/mcp_handlers.py`

**Changes:**
- Use `get_enhanced_input_schema()` if available
- Fallback to `get_input_schema()` for compatibility

**Example:**
```python
async def handle_list_tools() -> list[Tool]:
    tools = []
    for tool in registry.list_tools().values():
        # Use enhanced schema if available
        if hasattr(tool, 'get_enhanced_input_schema'):
            input_schema = tool.get_enhanced_input_schema()
        else:
            input_schema = tool.get_input_schema()
        
        tools.append(Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=input_schema
        ))
    return tools
```

---

## 🎯 **IMPLEMENTATION PRIORITY**

1. **Phase 1** (Immediate): Enhance field descriptions in `base_models.py`
2. **Phase 2** (High Impact): Add `get_enhanced_input_schema()` to `base_tool_core.py`
3. **Phase 3** (Polish): Update tool descriptions with capability sections
4. **Phase 4** (Integration): Modify `mcp_handlers.py` to use enhanced schemas

---

## ✅ **VALIDATION APPROACH**

### **1. Schema Validation Test**
```python
def test_enhanced_schema_validity():
    tools = get_registry().list_tools()
    for name, tool in tools.items():
        if hasattr(tool, 'get_enhanced_input_schema'):
            schema = tool.get_enhanced_input_schema()
            # Validate against JSON Schema draft-07
            validate(schema, METASCHEMA_07)
```

### **2. Capability Visibility Test**
```python
def test_capability_hints_present():
    chat_tool = get_registry().get_tool("chat")
    schema = chat_tool.get_enhanced_input_schema()
    
    assert "x-capability-hints" in schema["properties"]["files"]
    assert "x-related-tools" in schema
    assert "x-decision-matrix" in schema
```

### **3. Manual Verification**
- Call `listmodels_EXAI-WS` and verify enhanced descriptions
- Check that tool schemas include capability hints
- Verify decision matrices are visible

---

## ⚠️ **RISKS & MITIGATIONS**

### **Risk 1: Breaking Changes**
- **Risk:** Existing clients may not handle extended schema fields
- **Mitigation:** Keep base `get_input_schema()` unchanged, add `get_enhanced_input_schema()`

### **Risk 2: Schema Size**
- **Risk:** Enhanced schemas may become too verbose
- **Mitigation:** Keep hints concise, use structured metadata

### **Risk 3: Maintenance Overhead**
- **Risk:** Keeping capability hints synchronized with actual functionality
- **Mitigation:** Centralize common hints in `base_models.py`, use inheritance

---

## 📁 **FILES TO MODIFY**

1. `tools/shared/base_models.py` - Enhanced field descriptions
2. `tools/shared/base_tool_core.py` - Add `get_enhanced_input_schema()` method
3. `tools/chat.py` - Enhanced tool description
4. `src/server/handlers/mcp_handlers.py` - Use enhanced schemas
5. Other workflow tools (analyze, debug, codereview, etc.) - Enhanced descriptions

---

## 🎯 **EXPECTED OUTCOME**

**Before:**
```json
{
  "name": "chat_EXAI-WS",
  "inputSchema": {
    "properties": {
      "files": {
        "type": "array",
        "description": "Optional files for context..."
      }
    }
  }
}
```

**After:**
```json
{
  "name": "chat_EXAI-WS",
  "inputSchema": {
    "properties": {
      "files": {
        "type": "array",
        "description": "Optional files for context - EMBEDS CONTENT AS TEXT. DECISION MATRIX: Use 'files' for <5KB files. For >5KB files, use 'kimi_upload_files' tool. BENEFITS: Saves 70-80% tokens...",
        "x-capability-hints": {
          "threshold": "5KB",
          "alternative_tool": "kimi_upload_files",
          "benefit": "Saves 70-80% tokens"
        }
      }
    },
    "x-related-tools": {
      "escalation": ["analyze", "codereview", "debug"]
    },
    "x-decision-matrix": {
      "file_handling": {
        "<5KB": "Use 'files' parameter",
        ">5KB": "Use 'kimi_upload_files' tool"
      }
    }
  }
}
```

---

## 📊 **SUCCESS METRICS**

**Discovery Time:**
- **Before:** 2 hours (trial and error)
- **After:** 5-10 minutes (immediate visibility)
- **Improvement:** 92% reduction

**Capability Understanding:**
- **Before:** Requires reading markdown documentation
- **After:** Visible directly in tool schemas
- **Improvement:** Zero external documentation needed

---

## 🔗 **RELATED DOCUMENTATION**

- `docs/SYSTEM_CAPABILITIES_OVERVIEW.md` - Quick reference (created earlier)
- `docs/AGENT_CAPABILITIES.md` - Comprehensive guide (created earlier)
- `docs/05_CURRENT_WORK/2025-10-25/SESSION_SUMMARY__ACHIEVEMENTS_AND_NEXT_STEPS__2025-10-25.md`

---

## 📝 **NEXT STEPS**

1. ✅ **EXAI Consultation** - COMPLETE (received comprehensive strategy)
2. ⏳ **Implement Phase 1** - Enhance field descriptions
3. ⏳ **Implement Phase 2** - Add enhanced schema method
4. ⏳ **Implement Phase 3** - Update tool descriptions
5. ⏳ **Implement Phase 4** - Integrate enhanced schemas
6. ⏳ **Validation** - Test schema validity and visibility
7. ⏳ **Git Commit** - Create snapshot on current branch
8. ⏳ **GitHub Push** - Push to remote (NOT to main)

---

**Created:** 2025-10-25  
**Status:** Ready for implementation  
**EXAI Continuation ID:** `823af7e0-30d4-4842-b328-9736d2ed0b18` (13 turns remaining)  
**Next Agent:** Implement phases 1-4, validate, then commit and push to GitHub

