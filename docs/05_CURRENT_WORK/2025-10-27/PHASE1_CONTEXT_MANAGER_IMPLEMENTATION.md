# Phase 1.1: Context Manager Implementation

**Created:** 2025-10-27 18:00 AEDT  
**EXAI Consultation:** Continuation ID `5be79d08-1552-4467-a446-da24c8019a16` (GLM-4.6, high thinking mode)  
**Purpose:** Implement Context Manager to fix token explosion issue  
**Status:** 🔄 IN PROGRESS - Implementation plan complete

---

## 🎯 **OBJECTIVE**

Fix the critical token explosion issue where conversation context grows exponentially, causing:
- 108K token conversations (target: <10K)
- Unsustainable API costs
- Performance degradation
- Previous fix achieved only 0.5% reduction (need 60-70%)

---

## 🔍 **ROOT CAUSE ANALYSIS**

### **Current Architecture Issues:**

1. **No Intelligent Context Management**
   - `MAX_MESSAGES_TO_LOAD = 5` (hard limit, not intelligent)
   - `HARD_TOKEN_LIMIT = 4000` (aggressive pruning, loses context)
   - No summarization or compression
   - Full history loaded every time

2. **Token Explosion Pattern:**
   - Conversation grows: 1,279 → 29,818 tokens
   - Each turn adds full context to next turn
   - No separation between "working context" and "full history"
   - Supabase loads everything, passes everything to AI

3. **Incomplete Pruning:**
   - Current pruning is "too gentle" (EXAI assessment)
   - Only removes file contents from old messages
   - Doesn't summarize or compress message content
   - Still passes too many messages to AI

---

## 🏗️ **SOLUTION ARCHITECTURE**

### **EXAI's Recommended Approach:**

**Create `ContextManager` class that wraps existing storage layer**

**Key Principles:**
1. **Separation of Concerns**: Storage vs. context management
2. **Working Context vs Full History**: Only recent messages + summaries passed to AI
3. **Intelligent Compression**: Automatic summarization when threshold reached
4. **Backward Compatible**: Works with existing storage backends

---

## 📋 **IMPLEMENTATION PLAN**

### **Phase 1: Create ContextManager Wrapper** (Week 1)

**File**: `utils/context/context_manager.py`

```python
class ContextManager:
    def __init__(self, storage_backend, max_working_context=10, compression_threshold=20):
        """
        Args:
            storage_backend: Existing storage (SupabaseConversationMemory)
            max_working_context: Messages to keep in active context
            compression_threshold: When to trigger summarization
        """
        self.storage = storage_backend
        self.max_working_context = max_working_context
        self.compression_threshold = compression_threshold
        self.summarizer = MessageSummarizer()
    
    async def get_working_context(self, conversation_id):
        """Get recent messages + summaries for working context"""
        # Returns only what AI needs to see
        pass
    
    async def add_message(self, conversation_id, message):
        """Add message and trigger compression if needed"""
        # Stores in full history, manages working context
        pass
    
    async def compress_context(self, conversation_id):
        """Summarize old messages and store separately"""
        # Intelligent summarization of old messages
        pass
```

**Core Responsibilities:**
- ✅ Get working context (recent messages + summaries)
- ✅ Add messages with automatic compression
- ✅ Compress old messages into summaries
- ✅ Manage working context vs full history

---

### **Phase 2: Integration with Storage Factory** (Week 1)

**File**: `utils/conversation/storage_factory.py`

```python
def create_conversation_storage(config):
    """Wrap storage backend with ContextManager"""
    base_storage = SupabaseConversationMemory(config)
    return ContextManager(
        base_storage, 
        max_working_context=config.get('max_context', 10),
        compression_threshold=config.get('compression_threshold', 20)
    )
```

**Changes:**
- ✅ Wrap existing storage with ContextManager
- ✅ Pass configuration for context limits
- ✅ Maintain backward compatibility

---

### **Phase 3: Update Conversation Integration** (Week 1)

**File**: `tools/workflow/conversation_integration.py`

```python
# Replace direct storage calls with context_manager
context_manager = create_conversation_storage(config)
working_context = await context_manager.get_working_context(conversation_id)
```

**Changes:**
- ✅ Use ContextManager instead of direct storage
- ✅ Get working context (not full history)
- ✅ Update all conversation integration points

---

### **Phase 4: Context Compression Implementation** (Week 2)

**File**: `utils/context/message_summarizer.py`

```python
async def compress_context(self, conversation_id):
    """Compress old messages into summaries"""
    # Get all messages
    all_messages = await self.storage.get_messages(conversation_id)
    
    if len(all_messages) <= self.compression_threshold:
        return  # No compression needed
    
    # Split into working context and old messages
    working_messages = all_messages[-self.max_working_context:]
    old_messages = all_messages[:-self.max_working_context]
    
    # Generate summary of old messages
    summary = await self.summarizer.summarize_messages(old_messages)
    
    # Store summary and update working context
    await self.storage.store_summary(conversation_id, summary)
    await self.storage.update_working_context(conversation_id, working_messages)
```

**Key Features:**
- ✅ Automatic summarization when threshold reached
- ✅ Keep recent messages in working context
- ✅ Store summaries separately
- ✅ Reduce token usage by 60-70%

---

## 🗄️ **DATABASE SCHEMA CHANGES**

**Supabase Schema Updates:**

```sql
-- Add summary columns to conversations table
ALTER TABLE conversations ADD COLUMN context_summary TEXT;
ALTER TABLE conversations ADD COLUMN summary_created_at TIMESTAMP;
ALTER TABLE conversations ADD COLUMN summary_message_count INTEGER DEFAULT 0;
```

**Purpose:**
- Store compressed summaries of old messages
- Track when summaries were created
- Count messages included in summary

---

## ⚙️ **CONFIGURATION UPDATES**

**File**: `config.py` or `.env.docker`

```python
# Context Management Configuration
MAX_WORKING_CONTEXT = 10  # Recent messages to keep in working context
COMPRESSION_THRESHOLD = 20  # Total messages before compression triggers
SUMMARY_MODEL = "glm-4.5-flash"  # Cheaper model for summaries (FREE)
ENABLE_CONTEXT_COMPRESSION = True  # Feature flag
```

**Rationale:**
- `MAX_WORKING_CONTEXT = 10`: Balance between context and tokens
- `COMPRESSION_THRESHOLD = 20`: Trigger before token explosion
- `SUMMARY_MODEL = glm-4.5-flash`: Use free model for cost efficiency

---

## 🚀 **QUICK WIN IMPLEMENTATION**

**Immediate Fix** (can implement today):

**File**: `utils/conversation/supabase_memory.py`

```python
async def get_conversation_history(self, conversation_id):
    """Get conversation history with intelligent truncation"""
    messages = await self._fetch_messages(conversation_id)
    
    # Simple truncation for immediate fix
    if len(messages) > self.MAX_MESSAGES_TO_LOAD:
        # Keep recent messages + one summary message
        recent_messages = messages[-self.MAX_MESSAGES_TO_LOAD+1:]
        summary_msg = {
            "role": "system", 
            "content": f"[Conversation summary: {len(messages)-len(recent_messages)} earlier messages omitted]"
        }
        return [summary_msg] + recent_messages
    
    return messages
```

**Benefits:**
- ✅ Immediate token reduction
- ✅ No schema changes required
- ✅ Backward compatible
- ✅ Buys time for full ContextManager implementation

---

## 📊 **IMPLEMENTATION PRIORITY**

### **Week 1: Foundation**
1. ✅ Create `utils/context/context_manager.py`
2. ✅ Implement basic message truncation
3. ✅ Integrate with storage factory
4. ✅ Update conversation integration

### **Week 2: Intelligence**
1. ✅ Add intelligent summarization
2. ✅ Implement async background compression
3. ✅ Add database schema changes
4. ✅ Update configuration

### **Week 3: Optimization**
1. ✅ Add context-aware retrieval (RAG-style)
2. ✅ Implement caching for summaries
3. ✅ Add monitoring and metrics
4. ✅ Performance testing

---

## ✅ **SUCCESS CRITERIA**

**Token Reduction:**
- ✅ Reduce 108K token conversations to <10K
- ✅ Achieve 60-70% token reduction (EXAI target)
- ✅ Maintain conversation quality

**Performance:**
- ✅ No increase in latency
- ✅ Async compression doesn't block responses
- ✅ Cache hit rate >80%

**Compatibility:**
- ✅ Existing conversations continue to work
- ✅ No breaking changes to API
- ✅ Gradual migration path

---

## 🧪 **TESTING PLAN**

### **Unit Tests:**
- ✅ ContextManager message truncation
- ✅ Summarization logic
- ✅ Working context extraction
- ✅ Compression threshold triggers

### **Integration Tests:**
- ✅ Storage factory integration
- ✅ Conversation integration updates
- ✅ Database schema changes
- ✅ End-to-end conversation flow

### **Performance Tests:**
- ✅ Token usage before/after
- ✅ Latency impact
- ✅ Memory usage
- ✅ Compression effectiveness

---

## 📝 **NEXT STEPS**

1. ✅ Implement Quick Win fix (immediate token reduction)
2. ⏳ Create `utils/context/context_manager.py`
3. ⏳ Implement `MessageSummarizer` class
4. ⏳ Update storage factory integration
5. ⏳ Add database schema changes
6. ⏳ Test with EXAI validation
7. ⏳ Update documentation

---

**EXAI Consultation Summary:**
- **Model**: GLM-4.6 (high thinking mode)
- **Continuation ID**: `5be79d08-1552-4467-a446-da24c8019a16` (14 turns remaining)
- **Key Insight**: Separate "working context" from "full history" - only pass recent messages + summaries to AI
- **Recommendation**: Implement in phases - Quick Win first, then full ContextManager

**Status**: 🔄 IN PROGRESS - Ready to implement Quick Win and ContextManager

