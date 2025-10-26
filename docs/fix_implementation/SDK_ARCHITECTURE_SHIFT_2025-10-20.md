# SDK Architecture Shift & Documentation Restructure

**Date:** 2025-10-20  
**Branch:** feat/sdk-architecture-and-docs-restructure  
**Status:** Planning Phase Complete

---

## 📋 EXECUTIVE SUMMARY

**Critical Insight:** We've been over-engineering Supabase integration when Kimi/GLM SDKs already provide native conversation management.

**EXAI's Assessment:**
- ✅ SDKs handle multi-turn conversations natively
- ✅ Built-in context window handling
- ✅ Automatic token-aware message pruning
- ✅ Session persistence across API calls

**Architectural Shift:**
- **FROM:** Supabase as primary conversation storage
- **TO:** SDKs as primary, Supabase as audit trail & fallback

**Documentation Consolidation:**
- **FROM:** 80+ scattered markdown files
- **TO:** 12 focused component docs

---

## 🎯 ARCHITECTURAL REALIGNMENT

### Current Over-Engineering

**What We Built:**
```python
# Custom Supabase conversation management
class SupabaseConversationMemory:
    def build_conversation_history(self, continuation_id):
        # Load from Supabase
        # Custom context pruning (5 msgs, 4K tokens)
        # Manual token counting
        # Sliding window approach
        # Hard token limits
```

**Problems:**
1. Duplicating SDK functionality
2. Growing to 30 msgs/290K chars per conversation
3. Complex pruning logic (aggressive context engineering)
4. Performance overhead (Supabase queries)
5. Maintenance burden

### SDK Native Capabilities

**What SDKs Already Provide:**

**Kimi SDK (Moonshot):**
```python
from zai import ZaiClient

client = ZaiClient(api_key="your-api-key")

# Multi-turn conversation - SDK handles context!
conversation = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me more"}
]

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=conversation  # SDK manages context window
)
```

**GLM SDK (Z.AI):**
```python
from zhipuai import ZhipuAI

client = ZhipuAI(api_key="your-api-key")

# SDK handles conversation state
response = client.chat.completions.create(
    model="glm-4.6",
    messages=conversation  # Automatic context management
)
```

**SDK Features We're Duplicating:**
- ✅ Conversation state management
- ✅ Automatic context window handling
- ✅ Token-aware message pruning
- ✅ Session persistence
- ✅ Conversation history retrieval

### Proposed Architecture

**SDKs as Primary:**
```
User Request
    ↓
MCP Server
    ↓
Tool Execution
    ↓
SDK Native Conversation Management  ← PRIMARY
    ├─ Kimi SDK: conversation state
    ├─ GLM SDK: conversation state
    └─ Automatic context handling
    ↓
AI Provider API
```

**Supabase as Audit Trail:**
```
SDK Response
    ↓
Fire-and-Forget Async Write  ← AUDIT ONLY
    ├─ Log interaction
    ├─ Store for analytics
    ├─ Backup for recovery
    └─ Historical retention
    ↓
Supabase (Audit Trail)
```

**Supabase Role Redefinition:**

| Function | Current | Proposed |
|----------|---------|----------|
| **Conversation Storage** | Primary | Audit trail |
| **Context Management** | Custom logic | SDK native |
| **Message Pruning** | Manual (5 msgs, 4K tokens) | SDK automatic |
| **Session Persistence** | Supabase queries | SDK built-in |
| **Recovery** | Primary source | Fallback only |
| **Analytics** | Not implemented | Primary use case |
| **Audit Logging** | Side effect | Primary purpose |

---

## 📚 DOCUMENTATION RESTRUCTURE

### Current State (80+ Files)

**Problems:**
- Scattered across multiple directories
- Redundant information
- Hard to find relevant docs
- No clear hierarchy
- Overwhelming for new contributors

**Example:**
```
docs/
├── 01_ARCHITECTURE/ (4 files)
├── 02_IMPLEMENTATION_STATUS/ (many files)
├── 03_EXECUTIVE_SUMMARIES/ (many files)
├── 05_CURRENT_WORK/ (30+ files)
├── 07_LOGS/ (log files)
├── 08_FUNCTION-TESTING/ (test docs)
├── current/ (recent work)
└── [many more scattered files]
```

### EXAI's Recommended Structure (12 Components)

**New Structure:**
```
Documentations/
├── 01_Core_Architecture/
│   ├── System_Overview.md
│   ├── SDK_Integration_Guide.md
│   └── Supabase_Audit_Trail.md
│
├── 02_Service_Components/
│   ├── Daemon_WebSocket_Management.md
│   ├── Docker_Containerization.md
│   ├── MCP_Server_Integration.md
│   ├── Testing_Framework.md
│   ├── UI_Components.md
│   └── System_Prompts_Management.md
│
└── 03_Data_Management/
    ├── User_Management_Auth.md
    ├── Tools_Function_Calling.md
    └── File_Management_Storage.md
```

**Benefits:**
- Clear hierarchy (3 categories, 12 docs)
- Easy to navigate
- No redundancy
- Follows 4-tier architecture
- Single source of truth per component

---

## 🔄 MIGRATION STRATEGY

### Phase 1: SDK Integration (HIGH PRIORITY)

**Goal:** Use SDK native conversation management

**Tasks:**
1. Update Kimi provider to use SDK conversation state
2. Update GLM provider to use SDK conversation state
3. Remove custom context pruning logic
4. Simplify conversation memory to audit-only

**Expected Benefits:**
- 70% reduction in conversation management code
- Eliminate 30 msgs/290K chars growth issue
- Automatic context window handling
- Better SDK feature utilization

### Phase 2: Supabase Refactor (MEDIUM PRIORITY)

**Goal:** Redefine Supabase as audit trail

**Tasks:**
1. Create audit logging schema
2. Implement fire-and-forget async writes
3. Add analytics queries
4. Implement recovery fallback logic

**Expected Benefits:**
- Clear separation of concerns
- Reduced operational complexity
- Better observability
- Historical data retention

### Phase 3: Documentation Consolidation (HIGH PRIORITY)

**Goal:** Consolidate 80+ files into 12 focused docs

**Tasks:**
1. Create Documentations/ folder structure
2. Consolidate existing docs by component
3. Remove redundant information
4. Update references in code

**Expected Benefits:**
- Easier onboarding
- Clearer architecture understanding
- Reduced maintenance burden
- Better knowledge retention

---

## 📊 IMPACT ANALYSIS

### Code Changes

**Files to Modify:**
- `src/providers/kimi_chat.py` - Use SDK conversation state
- `src/providers/glm_chat.py` - Use SDK conversation state
- `utils/conversation/supabase_memory.py` - Simplify to audit-only
- `utils/conversation/memory_policy.py` - Remove custom pruning

**Files to Remove:**
- Custom context pruning logic
- Manual token counting utilities
- Sliding window implementation

**Estimated LOC Reduction:** ~1,500 lines (70% of conversation management)

### Performance Impact

**Expected Improvements:**
- Faster conversation loading (SDK in-memory vs Supabase queries)
- Reduced database load (audit-only writes)
- Better context handling (SDK optimized)
- Lower latency (fewer round trips)

### Risk Assessment

**Low Risk:**
- SDK conversation management is battle-tested
- Supabase still available as fallback
- Gradual migration possible
- Easy rollback if needed

**Medium Risk:**
- Need to understand SDK limitations
- May need custom logic for edge cases
- Analytics queries need redesign

---

## ✅ NEXT STEPS

### Immediate Actions:

1. **Create Documentations/ folder structure**
   - Set up 3 main categories
   - Create 12 component docs (templates)

2. **Consult EXAI for detailed migration plan**
   - SDK integration specifics
   - Supabase schema redesign
   - Documentation consolidation strategy

3. **Begin SDK integration**
   - Start with Kimi provider
   - Test conversation state management
   - Verify context handling

4. **Document as we go**
   - Update component docs with findings
   - Track migration progress
   - Note any issues/learnings

---

## 🎯 SUCCESS CRITERIA

**Architecture:**
- [ ] SDKs handle all conversation state
- [ ] Supabase used only for audit/analytics
- [ ] No custom context pruning logic
- [ ] Conversation growth issue resolved

**Documentation:**
- [ ] 80+ files consolidated to 12
- [ ] Clear component hierarchy
- [ ] No redundant information
- [ ] Easy to navigate and understand

**Performance:**
- [ ] Faster conversation loading
- [ ] Reduced database queries
- [ ] Better context handling
- [ ] Lower operational complexity

---

**Status:** 🟢 **READY TO PROCEED**  
**Next:** Consult EXAI for detailed implementation plan

