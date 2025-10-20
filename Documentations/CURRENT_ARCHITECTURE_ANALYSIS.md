# Current Architecture Analysis

**Date:** 2025-10-20  
**Status:** Analysis Complete - Ready for Refactoring

---

## Current Conversation Management Flow

### How It Works Now

```
User Request (with continuation_id)
         ↓
Load conversation from Supabase
         ↓
Convert to TEXT STRING with markers
         ↓
Embed in user prompt
         ↓
Send SINGLE message to SDK
         ↓
SDK Response
         ↓
Store in Supabase
```

### Code Evidence

**File:** `utils/conversation/supabase_memory.py`

```python
def build_conversation_history(self, continuation_id: str) -> str:
    """Builds conversation history as TEXT STRING"""
    thread = self.get_thread(continuation_id)
    
    history = "=== CONVERSATION HISTORY ===\n"
    for turn in thread.get('messages', []):
        history += f"Turn {turn['turn']}: {turn['role']} said: {turn['content']}\n"
    
    return history  # ← Returns TEXT, not message array!
```

**File:** `src/server/handlers/request_handler.py`

```python
# Load conversation history as TEXT
if continuation_id:
    history_text = memory.build_conversation_history(continuation_id)
    # Embed in user prompt
    full_prompt = f"{history_text}\n\n{user_prompt}"
else:
    full_prompt = user_prompt

# Send SINGLE message
arguments['prompt'] = full_prompt
```

**File:** `src/providers/kimi_chat.py`

```python
# Receives single message with embedded history
messages = [
    {"role": "user", "content": prompt}  # ← prompt contains history text!
]

response = client.chat.completions.create(
    model=model,
    messages=messages  # ← Only ONE message!
)
```

---

## Three Critical Issues

### Issue 1: Blocks SDK Native Features

**Kimi Context Caching:**
- Requires proper message array format
- Caches repeated system/assistant messages
- Our text embedding prevents this

**GLM Web Search:**
- Requires proper role separation
- Needs clean user messages
- Our text embedding confuses the system

**GLM Thinking Mode:**
- Requires structured conversation
- Needs proper turn tracking
- Our text format breaks this

### Issue 2: Inefficient Token Usage

**Text Markers Waste Tokens:**
```
=== CONVERSATION HISTORY ===
Turn 1: User said: ...
Turn 1: Assistant said: ...
Turn 2: User said: ...
```

**Proper Format is Cleaner:**
```python
[
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "user", "content": "..."}
]
```

### Issue 3: Supabase as Blocking Gateway

**Current Flow:**
1. User request arrives
2. **WAIT** for Supabase query (50-120ms)
3. Build text history
4. Send to SDK
5. **WAIT** for Supabase write (50-120ms)
6. Return response

**Problem:** Every request waits for Supabase twice!

---

## Proposed New Architecture

### Message Array Approach

```
User Request (with continuation_id)
         ↓
Build message array from continuation_id
         ↓
Send message array to SDK
         ↓
SDK Response (FAST)
         ↓
[PARALLEL] Async store to Supabase
         ↓
Return to user
```

### Key Changes

**1. Message Array Builder**
```python
def get_messages_array(self, continuation_id: str) -> List[Dict]:
    """Get messages as proper array"""
    thread = self.get_thread(continuation_id)
    messages = []
    
    for turn in thread.get('messages', []):
        messages.append({
            "role": turn['role'],
            "content": turn['content']
        })
    
    return messages  # ← Returns array!
```

**2. Request Handler Update**
```python
if continuation_id:
    # Build message array
    messages = memory.get_messages_array(continuation_id)
    messages.append({"role": "user", "content": user_prompt})
    arguments['_messages'] = messages
else:
    arguments['_messages'] = [{"role": "user", "content": user_prompt}]
```

**3. SDK Provider Update**
```python
# Use message array directly
messages = kwargs.get('_messages') or [
    {"role": "user", "content": prompt}
]

response = client.chat.completions.create(
    model=model,
    messages=messages  # ← Proper array!
)
```

**4. Async Supabase Storage**
```python
async def store_response_async(
    continuation_id: str,
    user_message: str,
    assistant_response: str
):
    """Store asynchronously (fire-and-forget)"""
    asyncio.create_task(
        self.add_turn(continuation_id, "user", user_message)
    )
    asyncio.create_task(
        self.add_turn(continuation_id, "assistant", assistant_response)
    )
```

---

## Migration Strategy

### Phase 1: Add Message Array Support
- Add `get_messages_array()` to `utils/conversation/supabase_memory.py`
- Keep existing `build_conversation_history()` for backward compatibility
- Test message array building

### Phase 2: Update Tool Handlers
- Modify `src/server/handlers/request_handler.py` to build message arrays
- Pass via `_messages` parameter
- Keep text embedding as fallback

### Phase 3: Update SDK Providers
- Modify `src/providers/kimi_chat.py` to use `_messages`
- Modify `src/providers/glm_chat.py` to use `_messages`
- Test with both approaches

### Phase 4: Move Supabase to Async
- Implement async storage in `utils/conversation/supabase_memory.py`
- Remove blocking Supabase calls from request path
- Keep sync fallback for errors

### Phase 5: Enable SDK Native Features
- Test Kimi context caching
- Test GLM web search
- Test GLM thinking mode
- Verify file upload works

---

## Files Requiring Changes

1. `utils/conversation/supabase_memory.py` - Add message array methods
2. `utils/conversation/storage_factory.py` - Update interface
3. `src/server/handlers/request_handler.py` - Build message arrays
4. `src/server/handlers/request_handler_context.py` - Update context handling
5. `tools/simple/mixins/continuation_mixin.py` - Remove text marker checks
6. `tools/simple/base.py` - Update continuation handling
7. `tools/simple/simple_tool_execution.py` - Update execution flow
8. `src/providers/kimi_chat.py` - Use message arrays
9. `src/providers/glm_chat.py` - Use message arrays
10. `src/providers/openai_compatible.py` - Update interface
11. `utils/conversation/history.py` - Update history building
12. `utils/conversation/memory.py` - Update memory interface

---

## Expected Benefits

### Performance
- ✅ Remove blocking Supabase calls from request path
- ✅ Reduce latency by 100-240ms per request
- ✅ Enable parallel processing

### SDK Features
- ✅ Kimi context caching (faster responses, lower costs)
- ✅ GLM web search (better research capabilities)
- ✅ GLM thinking mode (deeper reasoning)
- ✅ File upload integration (document analysis)

### Token Efficiency
- ✅ Remove text markers (save ~50-100 tokens per request)
- ✅ Better context quality (SDKs understand turns)
- ✅ Proper role separation (system/user/assistant)

### Reliability
- ✅ Supabase as audit trail (not blocking gateway)
- ✅ Fallback to Supabase if SDK fails
- ✅ Async storage (fire-and-forget)

