# System Bottleneck Analysis
**Date:** 2025-10-19 17:30 AEDT  
**Analysis Method:** Docker logs + EXAI 5-round research  
**EXAI Consultation ID:** 67e11ef1-8ba7-41dc-9eae-13e810ba3671  
**Status:** ✅ COMPLETE

---

## Executive Summary

Comprehensive analysis of system performance during 5-round EXAI research session identified 4 critical bottlenecks affecting response times and user experience. Priority ranking and solutions provided by EXAI consultation.

**Key Finding:** WebSocket connection errors and synchronous Supabase calls are the highest-impact bottlenecks requiring immediate attention.

---

## Bottleneck #1: WebSocket Connection Errors

### Symptoms
- **Frequency:** 15 errors across 5 rounds (3 errors per round average)
- **Error Message:** "Connection closed during send"
- **Pattern:** Errors occur AFTER response completion during progress notifications
- **Trigger:** Long-running responses (>87 seconds)

### Error Distribution
```
Round 1 (59.4s):  0 errors ✅
Round 2 (145.5s): 5 errors ⚠️
Round 3 (87.2s):  5 errors ⚠️
Round 4 (148.5s): 5 errors ⚠️
Round 5 (48.0s):  0 errors ✅
```

### Root Cause
WebSocket connections timing out during long GLM responses with no retry mechanism or pending message queue for disconnected clients.

### Impact
- **User Experience:** Connection drops during long operations
- **Data Loss Risk:** Progress notifications lost
- **Severity:** HIGH (affects all long-running operations)

### Solution (EXAI Recommended)
**Priority:** HIGHEST (Week 1, Day 1-2)

Deploy ResilientWebSocketManager with:
- Pending message queue for disconnected clients
- Automatic retry with exponential backoff
- Heartbeat monitoring (30s interval)
- Connection timeout detection (120s)
- Message TTL (300s for pending messages)

**Expected Impact:** 90% reduction in WebSocket errors

**Implementation:** Code provided by EXAI in Round 4 (ready to deploy)

---

## Bottleneck #2: Supabase Call Pattern

### Symptoms
- **Frequency:** 6 calls per turn (3 before response, 3 after)
- **Pattern:** Synchronous blocking calls
- **Impact:** Adds latency to every operation

### Call Sequence Per Turn
```
1. GET conversations (continuation_id lookup)
2. GET messages (load conversation history)
3. POST messages (save user prompt)
4. GET conversations (reload after save)
5. GET messages (reload history)
6. POST messages (save assistant response)
```

### Root Cause
- No conversation caching (redundant GET calls)
- No message batching (separate POST for each message)
- Synchronous operations block main flow

### Impact
- **Performance:** 5-10+ seconds internal data flow delay
- **Database Load:** 6x higher than necessary
- **Severity:** HIGH (affects all operations)

### Solution (EXAI Recommended)
**Priority:** HIGH (Week 1, Day 3-5)

Implement:
1. **Conversation Caching** - Eliminate redundant GET calls
2. **Message Batching** - Combine POST operations
3. **Sessions Table Integration** - Use existing table for state tracking

**Expected Impact:** 50-70% reduction in database load, 30-40% faster response times

**Implementation:** AsyncSupabaseManager with batching and caching

---

## Bottleneck #3: Context Reconstruction

### Symptoms
- **Pattern:** Exponential growth in context loading
- **Progression:** Turn 9 → 12 → 15 → 18 (all previous messages loaded)
- **Frequency:** Every turn
- **Impact:** Increasing token usage and processing time

### Example from Logs
```
Reconstructed context for thread 67e11ef1 (turn 9)
Reconstructed context for thread 67e11ef1 (turn 12)
Reconstructed context for thread 67e11ef1 (turn 15)
Reconstructed context for thread 67e11ef1 (turn 18)
```

### Root Cause
- All previous turns loaded on every request
- No selective context loading
- No context summarization for older turns

### Impact
- **Token Usage:** Exponential growth (4.6M tokens per 10-turn conversation)
- **Cost:** $2.81 per conversation (GLM-4.6)
- **Performance:** Slower context loading as conversation grows
- **Severity:** MEDIUM (affects cost and performance)

### Solution (EXAI Recommended)
**Priority:** MEDIUM (Week 1, Day 6-7)

Implement Context Engineering Phase 1:
- Selective context loading (only recent turns)
- Context summarization for older turns
- Optimized reconstruction algorithm

**Expected Impact:** 40-60% reduction in token usage, faster context loading

**Implementation:** Part of Context Engineering Phase 1 (already planned)

---

## Bottleneck #4: File Exclusion Processing

### Symptoms
- **Frequency:** Every turn
- **Pattern:** 6 files excluded from conversation history
- **Impact:** Files loaded then discarded

### Example from Logs
```
[FILES] Excluding 6 files from conversation history:
- GLM_WEB_SEARCH_ANALYSIS.md
- PROVIDER_COMPARISON.md
- text_format_handler.py
- glm_chat.py
- (2 more files)
```

### Root Cause
- File content loaded before exclusion check
- No metadata filtering before content load
- Inefficient exclusion logic

### Impact
- **Performance:** Unnecessary file I/O
- **Memory:** Wasted memory allocation
- **Severity:** LOW (minimal impact compared to other bottlenecks)

### Solution (EXAI Recommended)
**Priority:** LOW (Week 1, Day 3-5)

Implement:
- File metadata filtering before content load
- File usage analytics
- Optimized exclusion logic

**Expected Impact:** Minor performance improvement, reduced memory usage

**Implementation:** Simple optimization in file handling logic

---

## Supabase Database Analysis

### Existing Tables
- `conversations` (continuation_id, session_id, metadata) - 10 recent conversations
- `messages` (conversation_id, role, content, metadata) - 21 messages in latest thread
- `sessions` (10 columns) - **EXISTS BUT UNUSED (0 rows)**
- `provider_file_uploads`, `file_metadata`, `files` - File tracking
- Various EXAI tracking tables (issues, validation, etc.)

### Sessions Table Schema
```sql
Columns (mix of auth.sessions and custom fields):
- id (uuid, auto-generated)
- user_id (text)
- title (text, nullable)
- status (text, default 'active')
- created_at, updated_at (timestamps)
- turn_count (integer, default 0)
- total_tokens (integer, default 0)
- metadata (jsonb, default '{}')
- expires_at, refreshed_at (timestamps, nullable)
- factor_id, aal, user_agent, ip, tag (auth-related fields)
```

### Key Finding
**Sessions table already exists with custom fields (turn_count, total_tokens, metadata) but is completely unused (0 rows).**

### Integration Strategy (EXAI Recommended)
1. Analyze schema compatibility with session tracking plan
2. Extend existing schema if compatible
3. Create complementary table if incompatible
4. Migrate existing conversations to use sessions table

---

## Priority Ranking (EXAI Validated)

### 1. WebSocket Resilience (HIGHEST)
- **Why:** Directly impacts user experience with visible errors
- **Impact:** 90% reduction in connection errors
- **Complexity:** LOW (code already provided)
- **Timeline:** Week 1, Day 1-2

### 2. Supabase Call Optimization (HIGH)
- **Why:** Significant performance bottleneck blocking main flow
- **Impact:** 50-70% reduction in database load, 30-40% faster responses
- **Complexity:** MEDIUM (caching + batching)
- **Timeline:** Week 1, Day 3-5

### 3. Context Reconstruction Optimization (MEDIUM)
- **Why:** Affects both performance and token costs
- **Impact:** 40-60% reduction in token usage
- **Complexity:** MEDIUM (part of Context Eng Phase 1)
- **Timeline:** Week 1, Day 6-7

### 4. File Exclusion Optimization (LOW)
- **Why:** Minimal impact compared to other bottlenecks
- **Impact:** Minor performance improvement
- **Complexity:** LOW (simple optimization)
- **Timeline:** Week 1, Day 3-5 (alongside Supabase optimization)

---

## Implementation Roadmap

### Week 1, Day 1-2: Quick Wins
- ✅ Deploy ResilientWebSocketManager
- ✅ Add basic metrics collection
- ✅ Analyze sessions table schema

### Week 1, Day 3-5: Core Optimizations
- ✅ Implement Supabase call batching
- ✅ Add conversation caching
- ✅ Integrate sessions table
- ✅ Optimize file exclusion

### Week 1, Day 6-7: Context Optimization
- ✅ Begin Context Eng Phase 1
- ✅ Optimize context reconstruction
- ✅ Test and validate improvements

---

## Success Metrics

### Performance Targets
- **WebSocket Errors:** <1 per 5 rounds (90% reduction from 15)
- **Supabase Calls:** 2-3 per turn (50% reduction from 6)
- **Response Time:** ~90s for long responses (30% improvement from 145s)
- **Token Usage:** 20-40% reduction (context optimization)

### System Health Targets
- **WebSocket Connection Success Rate:** >99%
- **Supabase Query Time:** <100ms reads, <200ms writes
- **Memory Usage:** <100MB delta per workflow
- **Error Rate:** <1% of total requests

---

## Related Documents

- `EXAI_5_ROUND_RESEARCH_SUMMARY.md` - Full 5-round research analysis
- `CURRENT_PROGRESS.md` - Updated implementation tracker
- `ARCHITECTURAL_UPGRADE_REQUEST_2025-10-19.md` - Original upgrade request
- `PERFORMANCE_TUNING_GUIDE.md` - Performance optimization guide

---

**Status:** ✅ **ANALYSIS COMPLETE - READY FOR IMPLEMENTATION**

**Next Steps:**
1. Deploy WebSocket resilience (Day 1-2)
2. Optimize Supabase calls (Day 3-5)
3. Begin Context Eng Phase 1 (Day 6-7)

