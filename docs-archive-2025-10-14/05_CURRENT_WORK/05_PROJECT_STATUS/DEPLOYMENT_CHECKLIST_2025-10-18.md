# Deployment Checklist - P0 Bug Fixes (2025-10-18)

## Pre-Deployment Verification ✅

### Configuration Audit
- [x] **Environment Variables**: All new variables in `.env.docker`
  - [x] `KIMI_UPLOAD_TO_SUPABASE=true`
  - [x] `KIMI_SUPABASE_TIMEOUT=30.0`
  - [x] `KIMI_SEMAPHORE_TIMEOUT=0.001`
  - [x] `REDIS_URL` with authentication
  - [x] `SUPABASE_URL` and credentials

- [x] **Configuration Files**:
  - [x] `.env.example` updated with new variables
  - [x] Duplicate Supabase credentials removed from `.env.docker`
  - [x] `docker-compose.yml` uses `.env.docker` as env_file

- [x] **Code Integration**:
  - [x] `tools/providers/kimi/kimi_files.py` reads `KIMI_UPLOAD_TO_SUPABASE`
  - [x] `src/daemon/ws_server.py` reads `KIMI_SEMAPHORE_TIMEOUT`
  - [x] All imports present (`import os`)
  - [x] No hardcoded timeouts

### Database Migration
- [x] **Migration Applied**: `002_add_supabase_file_id_to_provider_uploads.sql`
  - [x] Column `supabase_file_id` added to `provider_file_uploads` table
  - [x] Index `idx_provider_file_uploads_supabase_file_id` created
  - [x] Verified via Supabase MCP tools

### EXAI Validation
- [x] **Tier 1**: Debug workflow investigation complete
  - Continuation ID: `4a9af892-df0e-4cb9-a161-70e78c620dbe`
  - Confidence: `very_high`

- [x] **Tier 2**: EXAI validation complete
  - Continuation ID: `b760f363-3469-4459-a1f6-0de73c597eb6`
  - Model: `kimi-k2-0905-preview`
  - Status: **APPROVED FOR DEPLOYMENT**

---

## Deployment Steps

### 1. Rebuild Docker Container
```bash
# Stop containers
docker-compose down

# Rebuild with new code
docker-compose build

# Start containers
docker-compose up -d
```

### 2. Verify Container Health
```bash
# Check container status
docker-compose ps

# Verify all containers are running
docker ps | grep exai
```

### 3. Monitor Startup Logs
```bash
# Watch daemon logs for errors
docker logs -f exai-mcp-daemon | grep -E "(ERROR|WARNING|CRITICAL)"

# Check for successful startup
docker logs exai-mcp-daemon | grep -E "(Supabase|Redis|WebSocket)"
```

---

## Post-Deployment Testing

### Phase 1: Infrastructure Validation

#### 1.1 Database Connectivity
```bash
# Verify Supabase connection
docker-compose exec exai-mcp-daemon python -c "
from src.storage.supabase_client import get_storage_manager
storage = get_storage_manager()
print('✅ Supabase connection established' if storage.enabled else '❌ Supabase not enabled')
"
```

#### 1.2 Environment Variable Propagation
```bash
# Verify new variables are loaded
docker-compose exec exai-mcp-daemon env | grep -E "(KIMI_|SUPABASE_)" | sort
```

Expected output:
```
KIMI_SEMAPHORE_TIMEOUT=0.001
KIMI_SUPABASE_TIMEOUT=30.0
KIMI_UPLOAD_TO_SUPABASE=true
SUPABASE_ANON_KEY=eyJ...
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
```

#### 1.3 Redis Connectivity
```bash
# Verify Redis connection
docker-compose exec exai-mcp-daemon python -c "
from utils.infrastructure.storage_backend import get_storage_backend
storage = get_storage_backend()
print('✅ Redis connection established' if hasattr(storage, 'redis_client') else '❌ Redis not connected')
"
```

### Phase 2: Feature Toggle Testing

#### 2.1 Test with Supabase Upload Disabled
```bash
# Temporarily disable Supabase upload
docker-compose exec exai-mcp-daemon sh -c "export KIMI_UPLOAD_TO_SUPABASE=false"

# Upload a small test file via Kimi tools
# Verify: File uploaded to Moonshot only, no Supabase storage entry
```

#### 2.2 Test with Supabase Upload Enabled
```bash
# Re-enable Supabase upload (default)
docker-compose restart exai-mcp-daemon

# Upload a small test file via Kimi tools
# Verify: File uploaded to both Moonshot AND Supabase storage
```

### Phase 3: End-to-End Validation

#### 3.1 File Upload Test
**Test Case**: Upload small markdown file

**Steps**:
1. Use `kimi_upload_files` tool to upload a test markdown file
2. Verify file uploaded to Moonshot (check logs for `file_id`)
3. Verify file uploaded to Supabase Storage (check logs for `supabase_file_id`)
4. Query database to verify metadata:
   ```sql
   SELECT provider_file_id, supabase_file_id, filename, upload_status 
   FROM provider_file_uploads 
   WHERE filename LIKE '%test%' 
   ORDER BY created_at DESC 
   LIMIT 5;
   ```

**Expected Result**:
- `provider_file_id`: Moonshot file ID (e.g., `file-abc123`)
- `supabase_file_id`: Supabase file UUID (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- `upload_status`: `completed`

#### 3.2 Timeout Test
**Test Case**: Verify Supabase upload timeout

**Steps**:
1. Monitor logs during file upload
2. Check for timeout-related messages
3. Verify timeout is 30 seconds (from `KIMI_SUPABASE_TIMEOUT`)

**Expected Result**:
- No timeout errors for small files
- Graceful handling if timeout occurs

#### 3.3 Semaphore Test
**Test Case**: Concurrent file uploads

**Steps**:
1. Upload 10 files concurrently via Kimi tools
2. Monitor semaphore health logs
3. Verify no semaphore leaks

**Expected Result**:
```
SEMAPHORE HEALTH: Global semaphore: expected 24, got 24 ✅
SEMAPHORE HEALTH: Provider KIMI semaphore: expected 6, got 6 ✅
```

#### 3.4 Rollback Test
**Test Case**: Graceful degradation

**Steps**:
1. Set `KIMI_UPLOAD_TO_SUPABASE=false` in `.env.docker`
2. Restart container
3. Upload test file
4. Verify file uploaded to Moonshot only

**Expected Result**:
- File uploaded successfully to Moonshot
- No Supabase storage errors
- `supabase_file_id` is `NULL` in database
- `upload_status`: `completed`

### Phase 4: Monitoring & Health Checks

#### 4.1 Semaphore Health
```bash
# Check for semaphore leaks
docker logs exai-mcp-daemon | grep "SEMAPHORE HEALTH" | tail -10
```

**Expected**: No warnings about semaphore leaks

#### 4.2 Supabase Upload Success Rate
```bash
# Check upload success rate
docker logs exai-mcp-daemon | grep -i "supabase.*upload" | tail -20
```

**Expected**: All uploads successful, no 404 errors

#### 4.3 Database Verification
```sql
-- Verify supabase_file_id is being populated
SELECT 
  COUNT(*) as total_uploads,
  COUNT(supabase_file_id) as supabase_uploads,
  COUNT(*) - COUNT(supabase_file_id) as failed_uploads
FROM provider_file_uploads
WHERE created_at > NOW() - INTERVAL '1 hour';
```

**Expected**: `failed_uploads` should be 0 (or minimal if testing rollback)

---

## Rollback Plan

If issues are detected:

### Quick Rollback (Feature Toggle)
```bash
# Disable Supabase upload immediately
docker-compose exec exai-mcp-daemon sh -c "
echo 'KIMI_UPLOAD_TO_SUPABASE=false' >> /app/.env.docker
"
docker-compose restart exai-mcp-daemon
```

### Full Rollback (Code Revert)
```bash
# Stop containers
docker-compose down

# Revert code changes
git revert <commit-hash>

# Rebuild and restart
docker-compose build
docker-compose up -d
```

### Database Rollback (if needed)
```sql
-- Remove the column (only if absolutely necessary)
ALTER TABLE provider_file_uploads DROP COLUMN IF EXISTS supabase_file_id;
DROP INDEX IF EXISTS idx_provider_file_uploads_supabase_file_id;
```

---

## Success Criteria

- [x] All containers start successfully
- [ ] No CRITICAL errors in logs
- [ ] Semaphore health checks pass (no leaks)
- [ ] File uploads succeed to both Moonshot and Supabase
- [ ] `supabase_file_id` populated in database
- [ ] No 404 errors when retrieving files
- [ ] Feature toggle works (can disable Supabase upload)
- [ ] Graceful degradation on Supabase failures

---

## Post-Deployment Actions

1. **Monitor for 24 hours**:
   - Check logs every 4 hours
   - Monitor semaphore health
   - Track upload success rate

2. **Update Documentation**:
   - Mark P0 fixes as deployed
   - Update operational runbook
   - Document any issues encountered

3. **Plan P1/P2 Fixes**:
   - Duplicate primary key in `conversation_files`
   - Redis cache pollution investigation
   - Background cleanup job for orphaned files

---

## Contact & Escalation

**If issues are detected**:
1. Check logs: `docker logs exai-mcp-daemon | tail -100`
2. Verify configuration: `docker-compose exec exai-mcp-daemon env | grep KIMI`
3. Test rollback: Set `KIMI_UPLOAD_TO_SUPABASE=false`
4. Escalate if needed: Document issue and revert changes

---

## Deployment Sign-Off

- **Deployed By**: _________________
- **Deployment Date**: 2025-10-18
- **Deployment Time**: _________________
- **Verification Complete**: [ ] Yes [ ] No
- **Issues Encountered**: _________________
- **Rollback Required**: [ ] Yes [ ] No

---

## References

- **P0 Bug Fixes Documentation**: `docs/05_CURRENT_WORK/05_PROJECT_STATUS/P0_BUG_FIXES_2025-10-18.md`
- **Tier 1 Investigation**: Continuation ID `4a9af892-df0e-4cb9-a161-70e78c620dbe`
- **Tier 2 Validation**: Continuation ID `b760f363-3469-4459-a1f6-0de73c597eb6`
- **Database Migration**: `supabase/migrations/002_add_supabase_file_id_to_provider_uploads.sql`

