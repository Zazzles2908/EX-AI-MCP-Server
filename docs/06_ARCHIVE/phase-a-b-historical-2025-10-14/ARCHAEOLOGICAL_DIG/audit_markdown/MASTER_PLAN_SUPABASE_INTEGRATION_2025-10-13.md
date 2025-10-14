# MASTER PLAN - SUPABASE INTEGRATION FOR CONVERSATION STORAGE
**Date:** 2025-10-13 (13th October 2025, Sunday)  
**Time:** 17:55 AEDT  
**Category:** Master Implementation Plan  
**Status:** 🎯 READY FOR EXECUTION

---

## EXECUTIVE SUMMARY

**What:** Replace in-memory conversation storage with Supabase persistent storage  
**Why:** Conversations currently lost on server restart (critical data loss bug)  
**How:** Implement SupabaseStorage backend using existing Supabase infrastructure  
**When:** 3-phase implementation (2 hours total)  
**Impact:** Conversations persist across restarts, production-ready storage

---

## CONTEXT & BACKGROUND

### The Problem You Identified

**User's Experience:**
```
ERROR: Conversation thread '03bb338d-65fb-4285-92b2-d830a32509d7' was not found or has expired
```

**Root Cause:**
- Conversations stored in-memory only (Python dict)
- Lost on every server restart
- Lost on process crash
- 3-hour TTL (now 24 hours after fix)
- Not production-ready

### What We Discovered

**1. Supabase Already Configured ✅**
- URL: https://rvqxqxqxqxqxqxqx.supabase.co
- Project ID: mxaazuhlqewmkweewyaz
- API Key: Configured in .env
- Status: Configured but MESSAGE_BUS_ENABLED=false

**2. Existing Infrastructure ✅**
- Message Bus Client implemented (src/core/message_bus_client.py)
- Circuit breaker for reliability
- Compression support (gzip/zstd)
- Checksum verification
- Automatic fallback to WebSocket

**3. Supabase Tables Exist ✅**
- conversations (for chat history)
- test_runs, test_results (for testing)
- issues, issue_occurrences (for issue tracking)
- users, core_memory, week_memory (for user data)

**4. Documentation Exists ✅**
- SUPABASE_MESSAGE_BUS_DESIGN.md (design intent)
- CRITICAL_PATHS.md (execution flow)
- DATA_FLOW_MAP.md (data flow)
- ENTRY_POINTS_FLOW_MAP.md (entry points)

---

## ARCHITECTURAL DECISION

### Why NOT Use Message Bus for Conversation Storage

**Message Bus Design:**
- Purpose: Large tool responses (>1MB) with guaranteed integrity
- Schema: Requires transaction_id, session_id, tool_name, provider_name
- TTL: 48 hours (MESSAGE_BUS_TTL_HOURS)
- Complexity: Circuit breaker, compression, checksum
- Use Case: Tool execution, not conversation storage

**Conversation Storage Needs:**
- Purpose: Simple key-value storage for conversation threads
- Schema: thread_id → conversation_data
- TTL: 24 hours (CONVERSATION_TIMEOUT_HOURS)
- Simplicity: Direct Supabase access
- Use Case: Conversation persistence

**Decision:** Create separate SupabaseStorage backend (clean separation of concerns)

---

## IMPLEMENTATION PLAN

### Phase 1: Schema & Configuration (30 minutes)

**Step 1.1: Create Supabase Schema**
```sql
CREATE TABLE conversation_threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id TEXT NOT NULL UNIQUE,
    user_id TEXT,
    conversation_data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    accessed_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_conversation_threads_thread_id ON conversation_threads(thread_id);
CREATE INDEX idx_conversation_threads_expires_at ON conversation_threads(expires_at);
CREATE INDEX idx_conversation_threads_user_id ON conversation_threads(user_id);
```

**Step 1.2: Update .env**
```env
# Add new variable
CONVERSATION_STORAGE_BACKEND=supabase  # Options: memory, supabase

# Keep existing
CONVERSATION_TIMEOUT_HOURS=24
SUPABASE_URL=https://rvqxqxqxqxqxqxqx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_PROJECT_ID=mxaazuhlqewmkweewyaz
```

**Step 1.3: Update .env.example**
```env
# ============================================================================
# CONVERSATION STORAGE CONFIGURATION
# ============================================================================
# Backend for conversation thread storage
# - memory: In-memory storage (LOST ON RESTART) - development only
# - supabase: Persistent Supabase storage (RECOMMENDED for production)
CONVERSATION_STORAGE_BACKEND=supabase  # Options: memory, supabase

# How long to keep conversation threads
CONVERSATION_TIMEOUT_HOURS=24  # 24 hours recommended

# Supabase configuration (required when CONVERSATION_STORAGE_BACKEND=supabase)
SUPABASE_URL=  # Your Supabase project URL
SUPABASE_KEY=  # Your Supabase anon key
SUPABASE_PROJECT_ID=  # Your Supabase project ID
```

---

### Phase 2: Implementation (60 minutes)

**Step 2.1: Implement SupabaseStorage Class**

**File:** `utils/infrastructure/storage_backend.py`

**Add imports:**
```python
try:
    from supabase import create_client
    _supabase_available = True
except ImportError:
    _supabase_available = False
```

**Add class:**
```python
class SupabaseStorage:
    """Supabase-backed storage for conversation threads."""
    
    def __init__(self, url: str, key: str, ttl_seconds: int):
        self._client = create_client(url, key)
        self._ttl = ttl_seconds
        self._table = "conversation_threads"
        logger.info(f"Supabase storage initialized (ttl={ttl_seconds}s)")
    
    def set_with_ttl(self, key: str, ttl_seconds: int, value: str):
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._client.table(self._table).upsert({
            "thread_id": key,
            "conversation_data": json.loads(value),
            "accessed_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": expires_at.isoformat()
        }).execute()
    
    def get(self, key: str) -> Optional[str]:
        result = self._client.table(self._table).select("*").eq("thread_id", key).execute()
        if not result.data:
            return None
        record = result.data[0]
        expires_at = datetime.fromisoformat(record["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            self._client.table(self._table).delete().eq("thread_id", key).execute()
            return None
        self._client.table(self._table).update({
            "accessed_at": datetime.now(timezone.utc).isoformat()
        }).eq("thread_id", key).execute()
        return json.dumps(record["conversation_data"])
    
    def delete(self, key: str):
        self._client.table(self._table).delete().eq("thread_id", key).execute()
```

**Step 2.2: Update get_storage() Function**

**Replace existing function:**
```python
def get_storage():
    """Get storage backend (Supabase or in-memory fallback)."""
    global _storage_instance
    
    if _storage_instance is not None:
        return _storage_instance
    
    timeout_hours = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))
    ttl = timeout_hours * 3600
    
    storage_backend = os.getenv("CONVERSATION_STORAGE_BACKEND", "memory").lower()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if storage_backend == "supabase" and supabase_url and supabase_key and _supabase_available:
        try:
            _storage_instance = SupabaseStorage(supabase_url, supabase_key, ttl)
            logger.info(f"✅ Using Supabase storage (ttl={timeout_hours}h)")
        except Exception as e:
            logger.warning(f"⚠️  Supabase storage failed, falling back to in-memory: {e}")
            _storage_instance = InMemoryStorage()
    else:
        _storage_instance = InMemoryStorage()
        if storage_backend == "supabase":
            logger.warning("⚠️  Supabase requested but not configured, using in-memory storage")
    
    return _storage_instance
```

**Step 2.3: Add Startup Warning**

**File:** `src/daemon/ws_server.py` (after line 45)

```python
# Warn about storage backend
storage_backend = os.getenv("CONVERSATION_STORAGE_BACKEND", "memory").lower()
if storage_backend == "memory":
    logger.warning(
        "⚠️  CONVERSATION STORAGE: Using in-memory storage (conversations lost on restart). "
        "Set CONVERSATION_STORAGE_BACKEND=supabase in .env for persistent storage."
    )
else:
    logger.info(f"✅ CONVERSATION STORAGE: Using {storage_backend} backend (persistent)")
```

---

### Phase 3: Testing & Validation (30 minutes)

**Step 3.1: Create Test Script**

**File:** `scripts/testing/test_supabase_storage.py`

```python
"""Test Supabase conversation storage."""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.infrastructure.storage_backend import get_storage

def test_supabase_storage():
    print("Testing Supabase Storage...")
    storage = get_storage()
    print(f"Storage backend: {type(storage).__name__}")
    
    # Test 1: Store and retrieve
    test_key = "test-thread-123"
    test_value = '{"messages": ["Hello", "World"]}'
    storage.set_with_ttl(test_key, 3600, test_value)
    retrieved = storage.get(test_key)
    assert retrieved == test_value
    print("✅ Test 1: Store and retrieve - PASSED")
    
    # Test 2: Expiration
    storage.set_with_ttl("expire-test", 5, test_value)
    time.sleep(6)
    expired = storage.get("expire-test")
    assert expired is None
    print("✅ Test 2: Expiration - PASSED")
    
    # Test 3: Delete
    storage.delete(test_key)
    deleted = storage.get(test_key)
    assert deleted is None
    print("✅ Test 3: Delete - PASSED")
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_supabase_storage()
```

**Step 3.2: Integration Test**
1. Set CONVERSATION_STORAGE_BACKEND=supabase in .env
2. Restart server
3. Start conversation with chat tool
4. Get continuation_id
5. Restart server again
6. Continue conversation with same continuation_id
7. Verify conversation persists ✅

**Step 3.3: Verify Supabase Data**
```python
# Use Supabase MCP to query
from supabase_mcp import execute_sql_supabase_mcp_full

result = execute_sql_supabase_mcp_full(
    project_id="mxaazuhlqewmkweewyaz",
    query="SELECT * FROM conversation_threads ORDER BY created_at DESC LIMIT 10"
)
print(result)
```

---

## TASK BREAKDOWN FOR TASK MANAGER

### Task 7: Supabase Schema Setup
- Create conversation_threads table
- Create indexes
- Test table creation
- Verify with Supabase MCP

### Task 8: SupabaseStorage Implementation
- Add Supabase imports to storage_backend.py
- Implement SupabaseStorage class
- Update get_storage() function
- Add startup warning

### Task 9: Configuration Updates
- Update .env with CONVERSATION_STORAGE_BACKEND
- Update .env.example with documentation
- Restart server
- Verify configuration

### Task 10: Testing & Validation
- Create test_supabase_storage.py
- Run unit tests
- Run integration test (restart persistence)
- Verify Supabase data
- Update all documentation

---

## SUCCESS CRITERIA

**✅ Phase 1 Complete When:**
- conversation_threads table exists in Supabase
- .env has CONVERSATION_STORAGE_BACKEND=supabase
- .env.example documented

**✅ Phase 2 Complete When:**
- SupabaseStorage class implemented
- get_storage() updated
- Startup warning added
- Server restarts successfully

**✅ Phase 3 Complete When:**
- All tests pass
- Conversation persists across restart
- Supabase data verified
- Documentation updated

**✅ Project Complete When:**
- Issue #6 marked complete
- All 10 issues resolved
- System production-ready

---

## ROLLBACK PLAN

**If Supabase Integration Fails:**
1. Set CONVERSATION_STORAGE_BACKEND=memory in .env
2. Restart server
3. System falls back to in-memory storage
4. No data loss (graceful degradation)

---

## NEXT ACTIONS

**Immediate (You Decide):**
1. Review this plan
2. Approve approach
3. I'll execute Phase 1 (schema setup)
4. Then Phase 2 (implementation)
5. Then Phase 3 (testing)

**Or:**
- Modify plan if needed
- Ask questions
- Request clarification

---

**STATUS: PLAN READY 🎯 | AWAITING YOUR APPROVAL 👍**

