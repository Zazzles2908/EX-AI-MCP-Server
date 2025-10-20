# CRITICAL ISSUES INVESTIGATION - 2025-10-19

## Issue 1: Massive Token Usage ($2.81 for Single Call)

### Symptoms
- Single chat call consumed **4,686,292 tokens**
- Cost: **$2.81** for one call
- Model used: `glm-4.6` (NOT the intended model)
- Duration: 22.47s
- Session: `6582d37d-9413-46a4-b9f5-9e5b11e5ed4f`
- Request ID: `7487a7a3-6e45-4360-ad49-16d4839b18d7`

### Evidence from Logs
```
DAY-dfef4cfbc00dadb1ceaf792d9d12436b-RAW0NTY52X4XKYAK
2025-10-18 90c4...d250 inference std glm-4.6 INPUT 0.0006kToken 1 4686292 token 0 token 0 token 131 2.8117752$ 0$ 0$
```

### Root Cause Hypotheses
1. **Conversation history explosion**: Entire conversation history being included in every call
2. **Model fallback**: Switched from `kimi-k2-0905-preview` to `glm-4.6` unexpectedly
3. **Continuation ID bug**: Not properly maintaining conversation context
4. **Message duplication**: History being duplicated or appended incorrectly

### Investigation Needed
- [ ] Check `conversations` table for this session
- [ ] Check `messages` table for message count
- [ ] Review conversation_manager.py for history handling
- [ ] Check if there's a token limit before truncation
- [ ] Verify continuation_id is being passed correctly

---

## Issue 2: Continuation ID Not Working Properly

### Symptoms
- Multiple calls using DIFFERENT session IDs instead of continuing same conversation
- Model switching unexpectedly (Kimi K2 → GLM 4.6)
- Continuation ID `8b5fce66-a561-45ec-b412-68992147882c` not maintaining context

### Evidence from Logs

**Call 1 (Kimi K2 - Correct):**
```
Duration: 84.53s
Model: kimi-k2-0905-preview
Session: ee031434-2bf7-4345-8114-8ef3ef6a1277
Request ID: 66735997-559d-440b-91d2-93cc429b5aa4
```

**Call 2 (GLM - WRONG!):**
```
Duration: 22.47s
Model: glm-4.6 (WRONG!)
Session: 6582d37d-9413-46a4-b9f5-9e5b11e5ed4f (DIFFERENT!)
Request ID: 7487a7a3-6e45-4360-ad49-16d4839b18d7
```

### Root Cause Hypotheses
1. **Session ID mismatch**: New session created instead of continuing existing
2. **Continuation ID not passed**: Parameter not being sent to subsequent calls
3. **Model selection override**: Fallback logic overriding user-specified model
4. **Storage retrieval failure**: Unable to retrieve conversation history

### Investigation Needed
- [ ] Check how continuation_id is passed between calls
- [ ] Verify conversation retrieval logic in conversation_manager.py
- [ ] Check if there's a fallback to GLM when Kimi fails
- [ ] Review session creation vs continuation logic

---

## Issue 3: Supabase Conversation Schema Issues

### Current Schema
```sql
conversations table:
- id (uuid, primary key)
- continuation_id (text, unique)
- title (text, nullable)
- metadata (jsonb)
- created_at (timestamptz)
- updated_at (timestamptz)

messages table:
- id (uuid, primary key)
- conversation_id (uuid, foreign key)
- role (enum: user, assistant, system)
- content (text)
- metadata (jsonb)
- created_at (timestamptz)
```

### Potential Issues
1. **No provider/model tracking**: Can't filter by model used
2. **No token counting**: Can't track token usage per conversation
3. **No message size limits**: Could lead to massive history accumulation
4. **No automatic truncation**: Old messages never removed

### Investigation Needed
- [ ] Query conversations table for continuation_id `8b5fce66-a561-45ec-b412-68992147882c`
- [ ] Count messages for this conversation
- [ ] Check total content size
- [ ] Verify metadata contains model/provider info

---

## Immediate Actions Required

### 1. Start New Conversation ID
- **OLD:** `8b5fce66-a561-45ec-b412-68992147882c`
- **NEW:** Generate fresh continuation_id for this investigation
- **Reason:** Avoid contaminating investigation with broken conversation

### 2. Query Supabase for Evidence
```sql
-- Find the problematic conversation
SELECT * FROM conversations 
WHERE continuation_id = '8b5fce66-a561-45ec-b412-68992147882c';

-- Count messages
SELECT COUNT(*), SUM(LENGTH(content)) as total_chars
FROM messages 
WHERE conversation_id IN (
  SELECT id FROM conversations 
  WHERE continuation_id = '8b5fce66-a561-45ec-b412-68992147882c'
);

-- Check metadata
SELECT metadata FROM conversations 
WHERE continuation_id = '8b5fce66-a561-45ec-b412-68992147882c';
```

### 3. Review Code
- `tools/simple/base.py` - Chat tool implementation
- `src/providers/orchestration/conversation_manager.py` - Conversation handling
- `utils/conversation/storage_factory.py` - Storage backend
- `utils/conversation/supabase_storage.py` - Supabase integration

### 4. Implement Safeguards
- [ ] Add token limit before including history
- [ ] Add message count limit (e.g., last 20 messages only)
- [ ] Add total character limit for history
- [ ] Add warning when history exceeds threshold
- [ ] Implement automatic truncation strategy

---

## Prevention Strategies

### Short-term
1. **Token limit check**: Before including history, check total tokens
2. **Message truncation**: Only include last N messages
3. **Model validation**: Ensure specified model is used, not fallback
4. **Continuation ID validation**: Verify continuation_id is passed correctly

### Long-term
1. **Conversation summarization**: Summarize old messages instead of including full text
2. **Sliding window**: Keep only recent messages in active memory
3. **Cost monitoring**: Alert when single call exceeds cost threshold
4. **Schema updates**: Add provider/model/tokens columns to conversations table

---

## Status
- **Issue 1 (Token Usage):** 🔴 CRITICAL - Under investigation
- **Issue 2 (Continuation ID):** 🔴 CRITICAL - Under investigation
- **Issue 3 (Schema):** 🟡 MEDIUM - Needs improvement

## Next Steps
1. Query Supabase for evidence
2. Review conversation_manager.py code
3. Identify exact root cause
4. Implement fixes
5. Test with new conversation ID
6. Document findings and prevention measures

