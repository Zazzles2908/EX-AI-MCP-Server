# Message Deduplication Fix - 2025-10-22

## Problem Statement

The Supabase `messages` table was allowing unlimited duplicate inserts due to missing unique constraints. This caused duplicate conversation entries in production, visible as multiple identical messages with the same `conversation_id`.

### Root Causes Identified

1. **No Duplicate Prevention**: The `messages` table had NO unique constraints to prevent duplicate inserts
2. **Edge Function Table Mismatch**: The Edge Function tried to insert into non-existent `exai_messages` table
3. **Race Condition Vulnerability**: Async fire-and-forget pattern combined with no duplicate checking
4. **No Idempotency**: System had no idempotency keys or deduplication logic

## Solution Implemented

### EXAI Recommendation

After comprehensive consultation with EXAI (GLM-4.6 with web search), the recommended solution was:

**Idempotency Key Pattern with Unique Constraint**

This approach was chosen because it:
- Scales perfectly from single-user development to multi-tenant production
- Makes deduplication intent explicit in the data model
- Is an industry-standard pattern (used by payment systems, messaging platforms)
- Handles retries gracefully (perfect for async fire-and-forget pattern)
- Provides clear debugging capabilities

## Implementation Details

### 1. Database Schema Changes

**File:** `supabase/schema.sql`

Added `idempotency_key` column to `messages` table:

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  role message_role NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  idempotency_key TEXT UNIQUE,  -- NEW: Prevents duplicates
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2. Migration Script

**File:** `supabase/migrations/20251022_add_idempotency_key.sql`

The migration includes:
- Add `idempotency_key` column (allows NULL initially for safe migration)
- Create function to generate idempotency keys for existing messages
- Backfill existing messages with idempotency keys
- Add unique constraint on `idempotency_key`
- Add partial unique index as additional safety
- Create `upsert_message_with_idempotency()` function for application use

**Key Features:**
- Safe staged migration (no downtime)
- Idempotent (can be run multiple times)
- Includes verification steps
- Comprehensive error handling

### 3. Python Code Updates

**File:** `src/storage/supabase_client.py`

**Added:**
- `generate_idempotency_key()` static method
  - Uses SHA-256 hash (more reliable than MD5)
  - Deterministic: `hash(conversation_id:role:content:timestamp)`
  - Normalizes content to reduce false duplicates

**Updated:**
- `save_message()` method
  - Now generates idempotency key before insert
  - Handles duplicate key errors gracefully
  - Returns existing message ID if duplicate detected
  - Added `client_timestamp` parameter for key generation

**Example:**
```python
# Generate idempotency key
idempotency_key = SupabaseStorageManager.generate_idempotency_key(
    conversation_id="abc-123",
    role="user",
    content="Hello world",
    client_timestamp="2025-10-22T10:30:00Z"
)
# Result: "a1b2c3d4e5f6..." (SHA-256 hash)

# Save message with deduplication
msg_id = storage.save_message(
    conversation_id="abc-123",
    role="user",
    content="Hello world",
    metadata={"model": "glm-4.6"}
)
# If duplicate: Returns existing message ID
# If new: Creates new message and returns ID
```

### 4. Edge Function Fix

**File:** `supabase/functions/exai-chat/index.ts`

**Fixed:**
- Changed `exai_messages` → `messages` (correct table name)
- Changed `exai_sessions` → `conversations` (correct table name)
- Added idempotency key generation using Web Crypto API
- Implemented get-or-create pattern for conversations
- Maps `session_id` to `conversation_id` correctly

**Key Changes:**
- Uses `SUPABASE_SERVICE_ROLE_KEY` for database writes (proper permissions)
- Generates SHA-256 idempotency keys for both user and assistant messages
- Creates conversation if it doesn't exist
- Updates conversation timestamp on each interaction

## Migration Process

### Safe Migration Path

1. **Add Column** (allows NULL initially)
2. **Backfill** existing messages with idempotency keys
3. **Add Constraint** (only after backfill complete)
4. **Verify** migration success

### Running the Migration

```bash
# Dry run (preview only)
python scripts/apply_idempotency_migration.py --dry-run

# Apply migration
python scripts/apply_idempotency_migration.py
```

The script will:
- Read migration SQL from `supabase/migrations/20251022_add_idempotency_key.sql`
- Execute each statement with error handling
- Verify migration success
- Report results

## Testing & Verification

### Manual Testing

1. **Test Duplicate Prevention:**
   ```python
   from src.storage.supabase_client import SupabaseStorageManager
   
   storage = SupabaseStorageManager()
   
   # Insert same message twice
   msg_id_1 = storage.save_message(
       conversation_id="test-conv-123",
       role="user",
       content="Test message",
       client_timestamp="2025-10-22T10:00:00Z"
   )
   
   msg_id_2 = storage.save_message(
       conversation_id="test-conv-123",
       role="user",
       content="Test message",
       client_timestamp="2025-10-22T10:00:00Z"  # Same timestamp
   )
   
   # Should return same ID (duplicate detected)
   assert msg_id_1 == msg_id_2
   ```

2. **Check Logs:**
   Look for: `Duplicate message detected (idempotency key: ...)`

3. **Verify Database:**
   ```sql
   -- Check for duplicates (should return 0)
   SELECT idempotency_key, COUNT(*)
   FROM messages
   GROUP BY idempotency_key
   HAVING COUNT(*) > 1;
   ```

### Automated Testing

The migration script includes verification:
- Checks if `idempotency_key` column exists
- Verifies unique index is created
- Confirms `upsert_message_with_idempotency()` function exists

## Benefits Achieved

1. ✅ **Single Source of Truth** - All messages in one table
2. ✅ **No Duplication** - Database-enforced unique constraint
3. ✅ **Retry-Friendly** - Idempotency keys handle retries gracefully
4. ✅ **Performance** - Minimal overhead (single hash calculation)
5. ✅ **Debuggability** - Clear logs when duplicates are detected
6. ✅ **Scalability** - Pattern scales from dev to production
7. ✅ **Data Integrity** - Edge Function now uses correct tables

## Potential Pitfalls Avoided

1. **Hash Collisions**: Using SHA-256 instead of MD5 minimizes collision risk
2. **Time Precision**: Including client timestamp in key generation handles near-simultaneous messages
3. **Content Normalization**: Standardizing whitespace before hashing
4. **Silent Failures**: Always returning clear success/failure status
5. **Data Fragmentation**: Fixed Edge Function instead of creating parallel tables

## Long-Term Maintainability

### Monitoring

- Add metrics for duplicate attempts
- Track idempotency key collision rate (should be near zero)
- Monitor query performance with new index

### Documentation

- Idempotency key generation is clearly documented
- Migration process is repeatable and safe
- Edge Function mapping is explicit

### Testing

- Include deduplication in integration tests
- Test retry scenarios
- Verify performance under load

## Next Steps

1. ✅ Apply migration to database
2. ✅ Test message insertion with deduplication
3. ✅ Monitor logs for duplicate detection
4. ✅ Verify no duplicate entries in Supabase dashboard
5. 🔄 Move to Task 1.4 - Add Logging Infrastructure

## References

- **EXAI Consultation:** Continuation ID `4193f538-7f0c-46be-8df8-afa7e9788318`
- **Model Used:** GLM-4.6 with web search enabled
- **Date:** 2025-10-22
- **Related Files:**
  - `supabase/schema.sql`
  - `supabase/migrations/20251022_add_idempotency_key.sql`
  - `src/storage/supabase_client.py`
  - `supabase/functions/exai-chat/index.ts`
  - `scripts/apply_idempotency_migration.py`

