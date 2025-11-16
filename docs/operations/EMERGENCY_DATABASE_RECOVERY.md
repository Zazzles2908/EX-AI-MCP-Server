# 🚨 EMERGENCY DATABASE RECOVERY GUIDE

## Situation
**The database was completely wiped** by another AI. All tables are missing:
- ❌ `public.conversations` - **MISSING**
- ❌ `public.messages` - **MISSING**
- ❌ `public.files` - **MISSING**
- ❌ `public.conversation_files` - **MISSING**
- ❌ All monitoring tables - **MISSING**
- ❌ Unified schema - **NOT EXECUTED**

**Daemon Status**: Running but cannot function - getting `PGRST205` errors (tables not found)

## Recovery Plan (5-10 minutes)

### Step 1: Create Base Tables (3 minutes)

1. **Open Supabase Dashboard**:
   - Go to: https://supabase.com/dashboard
   - Navigate to project: `gqokjxqfjcwxfhvtnmcf`
   - Click **SQL Editor**

2. **Execute Base Schema**:
   ```bash
   # Copy entire contents of supabase/schema.sql (154 lines)
   # Paste into SQL Editor
   # Click Run
   ```

3. **Verify Success**:
   ```sql
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public'
   ORDER BY table_name;
   ```
   Should show: conversations, messages, files, conversation_files, schema_version

### Step 2: Execute Unified Schema Migration (2 minutes)

1. **In Same SQL Editor**, create new query

2. **Execute Unified Schema**:
   ```bash
   # Copy entire contents of supabase/migrations/20251108_unified_schema.sql (427 lines)
   # Paste into SQL Editor
   # Click Run
   ```

3. **Verify Success**:
   ```sql
   -- Check schema created
   SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'unified';

   -- Check unified table
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'unified' AND table_name = 'event_metric_events';

   -- Check sessions table
   SELECT table_name FROM information_schema.tables
   WHERE table_schema = 'public' AND table_name = 'sessions';
   ```

4. **Expected Output**:
   ```
   NOTICE: ========================================
   NOTICE: Unified Database Schema Created Successfully!
   NOTICE: ========================================
   NOTICE: Schema: unified
   NOTICE: Table: event_metric_events (replaces 5 tables)
   NOTICE: Table: public.sessions (NEW - session persistence)
   NOTICE: Partitions: Monthly (2025_11, 2025_12, ...)
   NOTICE: Indexes: 8 indexes for performance
   NOTICE: Materialized Views: 3 views for common queries
   NOTICE: Retention: 90 days (automatic cleanup)
   NOTICE: ========================================
   NOTICE: Storage Reduction: 80% (5GB → 1GB)
   NOTICE: Query Performance: 60% improvement
   NOTICE: Next Step: Migrate data from old tables
   NOTICE: ========================================
   ```

### Step 3: Verify Daemon Recovery (1 minute)

1. **Check Daemon Logs**:
   ```bash
   docker logs exai-mcp-daemon --tail 30
   ```

2. **Expected Result**:
   - No more `PGRST205` errors
   - Daemon successfully creating sessions
   - No "table not found" errors

3. **Test Connection**:
   - Daemon should be accessible on ports 3000, 3001, 3002, 3003
   - WebSocket connections should work
   - Session creation should succeed

## Quick Validation Query

Run this to verify everything is working:

```sql
-- Verify all tables exist
SELECT
  table_schema,
  table_name
FROM information_schema.tables
WHERE table_schema IN ('public', 'unified')
  AND table_type = 'BASE TABLE'
ORDER BY table_schema, table_name;
```

**Expected Results**:
```
public | conversations
public | files
public | messages
public | conversation_files
public | schema_version
public | sessions
unified | event_metric_events
unified | event_metric_events_2025_11
unified | event_metric_events_2025_12
```

**Plus 3 materialized views in unified schema**

## What Was Lost

**Wiped Tables** (now being recreated):
- 5 monitoring tables (unified into 1)
- All existing conversation/message data
- Session data
- All metrics and monitoring history

**What Survived**:
- ✅ Source code (infrastructure/ directory)
- ✅ Migration files
- ✅ Docker containers
- ✅ Configuration files

## Prevention

**To prevent this in the future**:
1. Never let AI run `DROP TABLE` or `DROP SCHEMA` commands
2. Always backup before major operations
3. Use `IF NOT EXISTS` in all DDL
4. Keep schema_version table to track migrations
5. Document all database operations

## Rollback Plan

If something goes wrong:

```sql
-- Drop unified schema (start fresh)
DROP SCHEMA IF EXISTS unified CASCADE;

-- Keep base tables
-- (conversations, messages, files, conversation_files, schema_version, sessions)
```

## Files Involved

**Base Schema**: `supabase/schema.sql` (154 lines)
**Unified Migration**: `supabase/migrations/20251108_unified_schema.sql` (427 lines)
**Session Code**: `src/infrastructure/session_service.py` (12.9 KB)
**Enhanced Manager**: `src/infrastructure/session_manager_enhanced.py` (17.7 KB)

## Next Steps After Recovery

1. ✅ Database recreated
2. ⏳ Test session persistence: `python scripts/test_session_persistence.py`
3. ⏳ Validate daemon functionality
4. ⏳ Run full test suite
5. ⏳ Document any data that was lost

---

## Emergency Contact

If you need help:
1. Check logs: `docker logs exai-mcp-daemon --tail 50`
2. Verify tables: Run the validation query above
3. Restart daemon if needed: `docker restart exai-mcp-daemon`

**Recovery Time**: 5-10 minutes
**Risk Level**: Low (all code exists, just need to recreate tables)
**Data Loss**: All previous database data (was wiped by other AI)
