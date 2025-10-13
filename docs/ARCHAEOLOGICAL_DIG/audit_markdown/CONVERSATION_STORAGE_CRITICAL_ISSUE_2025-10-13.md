# CONVERSATION STORAGE - CRITICAL ISSUE
**Date:** 2025-10-13 (13th October 2025, Sunday)  
**Time:** 13:47 AEDT  
**Category:** Critical Bug - Data Loss  
**Status:** 🔴 CRITICAL - Immediate Fix Required

---

## INCIDENT REPORT

### What Happened

**User Action:**
- User was having a conversation with chat tool
- User provided `continuation_id` to continue the conversation
- Server had been restarted (to enable streaming)

**Error:**
```
ERROR: Conversation thread '03bb338d-65fb-4285-92b2-d830a32509d7' was not found or has expired
```

**Impact:**
- User lost entire conversation context
- Had to restart from scratch
- Poor user experience
- Data loss on server restart

---

## ROOT CAUSES

### Issue 1: In-Memory Storage Only

**Code:** `utils/infrastructure/storage_backend.py`

```python
class InMemoryStorage:
    def __init__(self):
        self._store: dict[str, tuple[str, float]] = {}  # ← IN MEMORY ONLY
```

**Problem:**
- Conversations stored in Python dict
- Lost on server restart
- Lost on process crash
- No persistence

### Issue 2: No Redis Configuration

**Code:** `utils/infrastructure/storage_backend.py` lines 132-140

```python
redis_url = os.getenv("REDIS_URL")  # ← NOT SET IN .env
if redis_url and _redis_available:
    _storage_instance = RedisStorage(redis_url, ttl)
else:
    _storage_instance = InMemoryStorage()  # ← FALLBACK TO IN-MEMORY
```

**Problem:**
- `REDIS_URL` not in .env
- System falls back to in-memory storage
- No persistence layer configured

### Issue 3: 3-Hour TTL (Even with Persistence)

**Code:** `utils/infrastructure/storage_backend.py` line 45

```python
timeout_hours = int(os.getenv("CONVERSATION_TIMEOUT_HOURS", "3"))  # ← DEFAULT 3 HOURS
```

**Problem:**
- Conversations expire after 3 hours
- Not configurable (not in .env)
- Too short for long-running conversations
- No warning before expiration

### Issue 4: Poor Error Message

**Code:** `src/server/context/thread_context.py` lines 115-121

```python
raise ValueError(
    f"Conversation thread '{continuation_id}' was not found or has expired. "
    f"This may happen if the conversation was created more than 3 hours ago or if the "
    f"server was restarted. "  # ← MENTIONS RESTART BUT DOESN'T EXPLAIN IT'S PERMANENT
```

**Problem:**
- Doesn't explain data is LOST (not just unavailable)
- Doesn't explain in-memory storage limitation
- Doesn't suggest enabling Redis for persistence

---

## RELATED TO ISSUE #6

### Issue #6: Misleading Progress Reports

**Connection:**
This is part of a broader pattern of **misleading or incomplete information**:

1. **Progress reports** show 2% with 175s ETA but complete in 5s
2. **Error messages** don't explain root cause (in-memory storage)
3. **Configuration** missing from .env (CONVERSATION_TIMEOUT_HOURS, REDIS_URL)
4. **Documentation** doesn't warn about data loss on restart

---

## IMPACT ASSESSMENT

### Severity: 🔴 CRITICAL

**Data Loss:**
- ✅ User conversations lost on restart
- ✅ No warning before loss
- ✅ No recovery possible

**User Experience:**
- ❌ Frustrating (lose context mid-conversation)
- ❌ Confusing (error message unclear)
- ❌ Time-wasting (must restart from scratch)

**Production Readiness:**
- ❌ NOT production-ready (data loss on restart)
- ❌ NOT scalable (in-memory only)
- ❌ NOT reliable (3-hour TTL)

---

## IMMEDIATE FIXES NEEDED

### Fix 1: Add Missing .env Variables

**Add to .env:**
```env
# ============================================================================
# CONVERSATION STORAGE CONFIGURATION
# ============================================================================
# Conversation threads are stored to enable multi-turn conversations with continuation_id
# WARNING: Without Redis, conversations are lost on server restart!
CONVERSATION_TIMEOUT_HOURS=24  # How long to keep conversation threads (24 hours recommended)
REDIS_URL=  # Redis URL for persistent storage (e.g., redis://localhost:6379/0)
# If REDIS_URL is not set, conversations use in-memory storage (LOST ON RESTART)
```

### Fix 2: Update .env.example

**Add to .env.example:**
```env
# ============================================================================
# CONVERSATION STORAGE CONFIGURATION
# ============================================================================
# Conversation threads enable multi-turn conversations with continuation_id parameter
# 
# CRITICAL: Without Redis, conversations are stored in-memory and LOST on server restart!
# For production use, configure Redis for persistent conversation storage.
#
# In-Memory Storage (Development Only):
# - Conversations lost on restart
# - Conversations lost on crash
# - Not suitable for production
#
# Redis Storage (Production):
# - Conversations persist across restarts
# - Conversations survive crashes
# - Scalable and reliable
#
CONVERSATION_TIMEOUT_HOURS=24  # How long to keep conversation threads (default: 3 hours)
REDIS_URL=  # Redis URL for persistent storage (e.g., redis://localhost:6379/0)
# Leave REDIS_URL empty for in-memory storage (development only)
# Set REDIS_URL for persistent storage (production recommended)
```

### Fix 3: Improve Error Message

**Update `src/server/context/thread_context.py` lines 115-121:**

```python
# Determine storage type for better error message
storage_type = "in-memory (lost on restart)" if not os.getenv("REDIS_URL") else "Redis"

raise ValueError(
    f"Conversation thread '{continuation_id}' was not found or has expired.\n\n"
    f"Current storage: {storage_type}\n"
    f"Timeout: {os.getenv('CONVERSATION_TIMEOUT_HOURS', '3')} hours\n\n"
    f"This may happen if:\n"
    f"1. The conversation was created more than {os.getenv('CONVERSATION_TIMEOUT_HOURS', '3')} hours ago\n"
    f"2. The server was restarted (in-memory storage loses all conversations)\n"
    f"3. The conversation was never created\n\n"
    f"To continue, please restart the conversation by providing your full question/prompt "
    f"without the continuation_id parameter. This will create a new conversation thread.\n\n"
    f"For production use, configure REDIS_URL in .env to enable persistent conversation storage."
)
```

### Fix 4: Add Startup Warning

**Add to server startup (ws_server.py or bootstrap):**

```python
# Warn if using in-memory storage
if not os.getenv("REDIS_URL"):
    logger.warning(
        "⚠️  CONVERSATION STORAGE: Using in-memory storage (conversations lost on restart). "
        "For production, set REDIS_URL in .env for persistent storage."
    )
```

---

## LONG-TERM SOLUTIONS

### Option 1: Enable Redis (Recommended for Production)

**Install Redis:**
```bash
# Windows (via Chocolatey)
choco install redis-64

# Or use Docker
docker run -d -p 6379:6379 redis:latest
```

**Configure .env:**
```env
REDIS_URL=redis://localhost:6379/0
```

**Benefits:**
- ✅ Conversations persist across restarts
- ✅ Conversations survive crashes
- ✅ Scalable (can use remote Redis)
- ✅ Production-ready

### Option 2: File-Based Storage (Alternative)

**Create new storage backend:**
```python
class FileStorage:
    def __init__(self, directory: str):
        self._dir = Path(directory)
        self._dir.mkdir(exist_ok=True)
    
    def set_with_ttl(self, key: str, ttl_seconds: int, value: str):
        file_path = self._dir / f"{key}.json"
        data = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }
        file_path.write_text(json.dumps(data))
    
    def get(self, key: str) -> Optional[str]:
        file_path = self._dir / f"{key}.json"
        if not file_path.exists():
            return None
        data = json.loads(file_path.read_text())
        if time.time() > data["expires_at"]:
            file_path.unlink()
            return None
        return data["value"]
```

**Benefits:**
- ✅ No external dependencies
- ✅ Persists across restarts
- ✅ Simple to implement
- ❌ Not as scalable as Redis

### Option 3: Increase TTL + Document Limitation

**Temporary workaround:**
```env
CONVERSATION_TIMEOUT_HOURS=168  # 7 days
```

**Add warning to docs:**
```markdown
## Conversation Storage Limitations

**Current Implementation:**
- Conversations stored in-memory (lost on restart)
- Default timeout: 3 hours (configurable via CONVERSATION_TIMEOUT_HOURS)

**Recommendations:**
- For development: Increase CONVERSATION_TIMEOUT_HOURS to 24-168 hours
- For production: Configure REDIS_URL for persistent storage
- Avoid server restarts during active conversations
```

---

## TESTING CHECKLIST

- [ ] Add CONVERSATION_TIMEOUT_HOURS to .env
- [ ] Add REDIS_URL to .env (empty for now)
- [ ] Update .env.example with detailed comments
- [ ] Improve error message in thread_context.py
- [ ] Add startup warning for in-memory storage
- [ ] Restart server
- [ ] Test conversation continuation (should work within timeout)
- [ ] Test server restart (should show improved error message)
- [ ] Document limitation in user-facing docs

---

## PRIORITY

**Immediate (Today):**
1. ✅ Add missing .env variables
2. ✅ Update .env.example
3. ✅ Improve error message
4. ✅ Add startup warning

**Short-term (This Week):**
1. ⏳ Implement file-based storage OR
2. ⏳ Set up Redis for development

**Long-term (Production):**
1. ⏳ Require Redis for production deployments
2. ⏳ Add health check for storage backend
3. ⏳ Add metrics for conversation storage

---

## CONCLUSION

**This is a CRITICAL issue** that causes data loss and poor user experience. The immediate fixes are simple (add .env variables, improve error message) but the long-term solution requires either Redis or file-based storage.

**User Impact:**
- Lost conversation context mid-discussion
- Had to restart from scratch
- Frustrating experience

**System Impact:**
- Not production-ready
- Data loss on restart
- Poor error messaging

**Next Steps:**
1. Implement immediate fixes (env variables, error message)
2. Restart server
3. Test and verify
4. Plan long-term storage solution

