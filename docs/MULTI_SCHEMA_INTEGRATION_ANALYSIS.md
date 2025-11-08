# Multi-Schema Architecture Analysis & Integration Guide
**EXAI MCP Server Database Integration Strategy**

---

## 🚨 CRITICAL DISCOVERY

**The Problem:**
- **EXAI MCP Server** writes conversations/messages to `public` schema
- **Orchestrator** expects to read from `chat` schema
- **Result**: Data silo - orchestrator cannot see EXAI conversations!

---

## 📊 SCHEMA ORGANIZATION

### Multi-Tenant Design Pattern
```
┌─────────────────────────────────────────────────────────┐
│  chat (ORCHESTRATOR)                                    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│  • conversations      • messages                        │
│  • conversation_files                                 │
│  Purpose: Primary messaging domain for ALL services    │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ Reads
                          │
┌─────────────────────────────────────────────────────────┐
│  public (EXAI MCP SERVER)                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│  • conversations      • files                          │
│  • messages          • secrets                         │
│  • jwt_tokens        • platform_file_registry          │
│  Purpose: EXAI-specific operations & storage           │
└─────────────────────────────────────────────────────────┘
                          │
                          │ Writes
                          │
┌─────────────────────────────────────────────────────────┐
│  ai_manager (AI OPERATIONS)                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                       │
│  • conversations     • memories                        │
│  • tool_usage        • user_profiles                   │
│  • ai_responses                                        │
│  Purpose: AI processing & memory management            │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 STRUCTURE COMPARISON

### conversations table
| chat.conversations | public.conversations |
|-------------------|---------------------|
| `id` (uuid) | `id` (uuid) |
| `continuation_id` (text) | `continuation_id` (text) |
| `title` (text) | `title` (text) |
| `metadata` (jsonb) | `metadata` (jsonb) |
| `created_at` (timestamptz) | `created_at` (timestamptz) |
| `updated_at` (timestamptz) | `updated_at` (timestamptz) |
| **`session_id`** (uuid) ✨ | ❌ |

### messages table
| chat.messages | public.messages |
|---------------|----------------|
| `id` (uuid) | `id` (uuid) |
| `conversation_id` (uuid) | `conversation_id` (uuid) |
| `role` (user-defined) | `role` (user-defined) |
| `content` (text) | `content` (text) |
| `metadata` (jsonb) | `metadata` (jsonb) |
| `created_at` (timestamptz) | `created_at` (timestamptz) |
| `idempotency_key` (text) | `idempotency_key` (text) |
| **`embedding`** (user-defined) ✨ | ❌ |

### Key Differences:
- **chat**: Has `session_id` in conversations, `embedding` in messages
- **public**: Simpler structure, consolidated files with TTL

---

## 🎯 RECOMMENDED SOLUTION

### Option 1: **WRITE TO CHAT SCHEMA** (Recommended)
**Pros:**
- ✅ Orchestrator compatibility
- ✅ Unified messaging domain
- ✅ All systems can see each other's data
- ✅ Follows established pattern

**Cons:**
- ⚠️ Need to add missing columns (session_id, embedding) or make them nullable

**Action Steps:**
1. Modify `storage_manager.py` to use `chat` schema
2. Add missing columns to `public.conversations` if writing to `public`
3. OR make `session_id`, `embedding` nullable in `chat` schema

### Option 2: **KEEP PUBLIC, CREATE BRIDGE**
**Pros:**
- ✅ EXAI has clean isolation
- ✅ File TTL is EXAI-specific enhancement
- ✅ No schema conflicts

**Cons:**
- ⚠️ Orchestrator needs to query both schemas
- ⚠️ Data fragmentation
- ⚠️ More complex query logic

**Action Steps:**
1. Create database view joining chat + public
2. Orchestrator queries unified view
3. OR implement sync mechanism

### Option 3: **HYBRID APPROACH**
**Pros:**
- ✅ Conversations/messages in `chat` (unified)
- ✅ EXAI-specific data in `public` (files, secrets)
- ✅ Best of both worlds

**Cons:**
- ⚠️ More complex implementation
- ⚠️ Need to track which schema for what

---

## 💡 **RECOMMENDATION: OPTION 3 (HYBRID)**

### Why?
1. **chat schema** = Unified messaging (industry standard)
2. **public schema** = Service-specific data (EXAI secrets, files, etc.)
3. **Preserves TTL enhancement** in public.files
4. **Enables orchestrator integration**

### Implementation:
```python
# Conversations & Messages → chat schema
# Files, Secrets, Platform data → public schema

# storage_manager.py modifications needed:
client.table("conversations")  # Should specify 'chat' schema
client.table("messages")       # Should specify 'chat' schema
client.table("files")          # Keep in 'public' schema
```

---

## 🔌 EXTERNAL SYSTEM CONNECTION GUIDE

### For Orchestrator & Other Systems

#### 1. **Supabase Connection**
```python
from supabase import create_client

# Connection to EXAI MCP Server database
url = "https://mxaazuhlqewmkweewyaz.supabase.co"
key = "your-service-role-key"

supabase = create_client(url, key)

# Query conversations (from chat schema)
conversations = supabase.table("conversations", schema="chat").select("*").execute()

# Query messages (from chat schema)
messages = supabase.table("messages", schema="chat").select("*").eq(
    "conversation_id", conversation_id
).execute()

# Query EXAI files (from public schema)
files = supabase.table("files", schema="public").select("*").execute()
```

#### 2. **Schema Specification**
```python
# Supabase Python client supports schema parameter:
client.table("table_name", schema="schema_name")

# Supported schemas:
# - "chat"     → Conversations, Messages
# - "public"   → EXAI files, secrets
# - "ai_manager" → AI operations
# - "exai"     → Issue tracking
```

#### 3. **Connection String Format**
```bash
# Direct PostgreSQL connection
postgresql://postgres:[password]@db.mxaazuhlqewmkweewyaz.supabase.co:5432/postgres

# With schema specification
# Set search_path in connection or use qualified names:
SET search_path TO chat, public, ai_manager;
```

#### 4. **MCP Client Configuration**
For systems connecting to EXAI MCP Server:

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "python",
      "args": ["-u", "path/to/run_ws_shim.py"],
      "env": {
        "ENV_FILE": "path/to/.env",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "3000"
      }
    }
  }
}
```

---

## 📝 ACTION PLAN

### Phase 1: Schema Migration (Recommended)
1. **Update storage_manager.py**:
   - Add schema parameter to table calls
   - `chat` for conversations/messages
   - `public` for files/secrets

2. **Database Updates**:
   - Option A: Add missing columns to `chat` schema
   - Option B: Migrate EXAI data to `chat` schema
   - Keep `public` for EXAI-specific data

3. **Code Changes**:
   ```python
   # Before
   client.table("conversations").select("*").execute()

   # After
   client.table("conversations", schema="chat").select("*").execute()
   ```

### Phase 2: Integration Testing
1. Test orchestrator can read EXAI data from `chat` schema
2. Verify all external systems can connect
3. Validate MCP server works with schema changes

### Phase 3: Documentation
1. Update connection guides
2. Document schema usage patterns
3. Create integration examples

---

## ⚡ QUICK REFERENCE

| Data Type | Schema | Table |
|-----------|--------|-------|
| Conversations | `chat` | `conversations` |
| Messages | `chat` | `messages` |
| Files | `public` | `files` |
| Secrets | `public` | `secrets` |
| AI Data | `ai_manager` | `conversations`, `memories` |
| Issues | `exai` | `exai_issues` |

**Remember:** Always specify schema when querying to avoid ambiguity!

---

**Status:** Analysis Complete ✅
**Next Step:** Architectural decision needed
**Priority:** HIGH - Affects all system integrations
