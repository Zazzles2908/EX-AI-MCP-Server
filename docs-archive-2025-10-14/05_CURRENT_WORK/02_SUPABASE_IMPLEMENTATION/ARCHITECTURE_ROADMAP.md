# SUPABASE ARCHITECTURE ROADMAP FOR EXAI MCP SERVER

**Date:** 2025-10-16 (Updated with New Designs)
**Original Research:** `05660144-c47c-4b0b-b2b0-83012e53dd46`
**Redis Integration:** `debb44af-15b9-456d-9b88-6a2519f81427`
**Performance Tracking:** `0a6d1ef3-1311-4bfd-8230-57cb8e1d09ff`
**Unified File Handling:** `a0bdb843-a6e8-46b8-962b-0ad5deca73ba`
**Status:** ✅ Phase 1 Complete + New Architectural Designs Ready

---

## 🎯 EXECUTIVE SUMMARY

This document outlines the comprehensive Supabase integration strategy for EXAI MCP Server, based on extensive research of Supabase Pro features, best practices, and Docker integration patterns.

**Current Status (2025-10-16):**
- ✅ **Phase 1 Complete:** Dual storage (Redis + Supabase) fully operational
- ✅ **Redis Persistence:** 24-hour TTL with AOF+RDB persistence
- ✅ **Supabase Database:** Conversations table with permanent storage
- ✅ **Docker Integration:** All containers on exai-network with health checks
- ✅ **QA Validation:** 4 EXAI findings validated (2 valid, 2 not bugs)
- ✅ **Performance Tracking Design:** Complete Supabase schema with time-series aggregation
- ✅ **Unified File Handling Design:** Comprehensive Docker-compatible architecture
- ⏳ **Next Priority:** Implement new designs (Performance Tracking + File Handling)

**Key Findings:**
- **Free Tier:** Sufficient for current development (500MB DB, 1GB bandwidth)
- **Pro Tier ($25/mo):** Required for Phase 2+ (Edge Functions, pgvector, PITR)
- **Critical Features:** Edge Functions, Realtime, pgvector, RLS, Connection Pooling
- **Docker Integration:** ✅ Implemented with Redis, health checks, connection pooling ready
- **New Designs:** Performance tracking and unified file handling architectures complete

---

## 📊 FREE VS PRO TIER COMPARISON

### Free Tier (Current)
- ✅ 500MB database storage
- ✅ 1GB bandwidth/month
- ✅ 2 Edge Functions
- ✅ 50,000 monthly active users
- ❌ No point-in-time recovery
- ❌ No custom domain
- ❌ Limited pgvector support

### Pro Tier ($25/month)
- ✅ 8GB database storage
- ✅ 100GB bandwidth/month
- ✅ 100 Edge Functions
- ✅ 100,000 monthly active users
- ✅ Point-in-time recovery (7 days)
- ✅ Custom domain support
- ✅ Priority support
- ✅ Full pgvector support

**Recommendation:** Upgrade to Pro when implementing Phase 2 (Edge Functions + pgvector)

---

## 🏗️ ARCHITECTURAL COMPONENTS

### 1. EDGE FUNCTIONS (Serverless AI Workflows)

**Purpose:** Pre/post-process AI requests, background jobs, webhooks

**Recommended Functions:**
1. **message-preprocess** - Clean/format messages before storage
2. **conversation-summarize** - Generate summaries after N messages
3. **file-processor** - Image optimization, document parsing
4. **analytics-tracker** - Track usage patterns
5. **cleanup-old** - Archive conversations older than 30 days

**Example Implementation:**
```typescript
// supabase/functions/message-preprocess/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
  const { message, conversation_id } = await req.json()
  
  // Preprocess message (sanitize, format, validate)
  const processed = await preprocessMessage(message)
  
  // Store in database
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )
  
  await supabase.from('messages').insert({
    conversation_id,
    content: processed,
    metadata: { processed: true, timestamp: new Date() }
  })
  
  return new Response(JSON.stringify({ success: true }))
})
```

**Integration with EXAI:**
- Call Edge Function before storing messages
- Use for background summarization
- Implement scheduled cleanup jobs

---

### 2. REALTIME SUBSCRIPTIONS (Live Updates)

**Purpose:** WebSocket-based live conversation updates, presence tracking

**Use Cases:**
- Real-time conversation updates across multiple clients
- Live file upload progress
- Presence indicators (who's using which conversation)
- System status broadcasts

**Python Implementation:**
```python
# src/realtime/supabase_realtime.py
from supabase import create_client
import asyncio

class SupabaseRealtime:
    def __init__(self, url, key):
        self.client = create_client(url, key)
        self.subscriptions = {}
    
    async def subscribe_to_conversation(self, conversation_id, callback):
        """Subscribe to real-time updates for a specific conversation"""
        channel = self.client.channel(f'conversation:{conversation_id}')
        
        channel.on_postgres_changes(
            event='*',
            schema='public',
            table='messages',
            filter=f'conversation_id=eq.{conversation_id}',
            callback=callback
        ).subscribe()
        
        self.subscriptions[conversation_id] = channel
    
    async def broadcast_status(self, status_message):
        """Broadcast system status to all clients"""
        channel = self.client.channel('system-status')
        await channel.send({
            'type': 'broadcast',
            'event': 'status-update',
            'payload': status_message
        })
```

**Integration with EXAI:**
- Subscribe to conversation updates in WebSocket daemon
- Broadcast AI processing status
- Implement presence tracking for multi-user scenarios

---

### 3. PGVECTOR (Semantic Search)

**Purpose:** Vector embeddings for semantic search, similarity matching

**Database Setup:**
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Add vector column to messages table
ALTER TABLE messages ADD COLUMN embedding vector(1536);

-- Create index for similarity search (IVFFlat for speed)
CREATE INDEX ON messages USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Semantic search function
CREATE OR REPLACE FUNCTION semantic_search(
  query_embedding vector(1536),
  similarity_threshold float DEFAULT 0.7,
  match_count int DEFAULT 5
)
RETURNS TABLE(
  id uuid,
  content text,
  similarity float
)
LANGUAGE sql
AS $$
  SELECT
    m.id,
    m.content,
    1 - (m.embedding <=> query_embedding) AS similarity
  FROM messages m
  WHERE 1 - (m.embedding <=> query_embedding) > similarity_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
$$;
```

**Python Integration:**
```python
# src/storage/vector_search.py
import numpy as np
from supabase import create_client

class VectorSearch:
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    async def store_embedding(self, message_id, embedding):
        """Store message embedding (from Kimi/GLM)"""
        self.client.table('messages').update({
            'embedding': embedding.tolist()
        }).eq('id', message_id).execute()
    
    async def find_similar_messages(self, query_embedding, limit=5):
        """Find semantically similar messages"""
        result = self.client.rpc('semantic_search', {
            'query_embedding': query_embedding.tolist(),
            'similarity_threshold': 0.7,
            'match_count': limit
        }).execute()
        
        return result.data
```

**Integration with EXAI:**
- Generate embeddings using Kimi/GLM models
- Store embeddings with messages
- Implement semantic search for context retrieval
- Find similar conversations for deduplication

---

### 4. ROW-LEVEL SECURITY (Multi-User Auth)

**Purpose:** Secure multi-user access with conversation ownership

**RLS Policies:**
```sql
-- Enable RLS on all tables
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE files ENABLE ROW LEVEL SECURITY;

-- Users can only access their own conversations
CREATE POLICY "Users can view own conversations" ON conversations
  FOR SELECT USING (auth.uid()::text = user_id);

CREATE POLICY "Users can create own conversations" ON conversations
  FOR INSERT WITH CHECK (auth.uid()::text = user_id);

CREATE POLICY "Users can update own conversations" ON conversations
  FOR UPDATE USING (auth.uid()::text = user_id);

-- Messages inherit conversation ownership
CREATE POLICY "Users can view own messages" ON messages
  FOR SELECT USING (
    conversation_id IN (
      SELECT id FROM conversations WHERE user_id = auth.uid()::text
    )
  );
```

**Authentication Flow:**
```python
# src/auth/supabase_auth.py
from supabase import create_client
import jwt
from datetime import datetime, timedelta

class SupabaseAuth:
    def __init__(self, url, service_key, jwt_secret):
        self.client = create_client(url, service_key)
        self.jwt_secret = jwt_secret
    
    def generate_user_token(self, user_id):
        """Generate JWT token for user"""
        payload = {
            'uid': user_id,
            'exp': datetime.now() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        return jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
```

**When to Enable:**
- Phase 3: Multi-user support
- After single-user development is stable
- When deploying to production

---

### 5. DOCKER INTEGRATION WITH CONNECTION POOLING

**Purpose:** Optimize database connections, improve performance

**Docker Compose with pgbouncer:**
```yaml
# docker-compose.yml
version: '3.8'
services:
  exai-mcp:
    build: .
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_SERVICE_ROLE_KEY=${SUPABASE_SERVICE_ROLE_KEY}
      - DATABASE_POOL_URL=postgres://postgres:${POSTGRES_PASSWORD}@pgbouncer:6432/postgres
    ports:
      - "8079:8079"
    depends_on:
      - pgbouncer
    healthcheck:
      test: ["CMD", "python", "scripts/health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  pgbouncer:
    image: pgbouncer/pgbouncer:latest
    environment:
      DATABASES_HOST: ${SUPABASE_HOST}
      DATABASES_PORT: 5432
      DATABASES_USER: postgres
      DATABASES_PASSWORD: ${POSTGRES_PASSWORD}
      DATABASES_DBNAME: postgres
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 100
      DEFAULT_POOL_SIZE: 20
    ports:
      - "6432:6432"
```

**Health Check Implementation:**
```python
# scripts/health_check.py
import sys
from src.storage.supabase_client import get_storage_manager

def check_supabase_health():
    """Check Supabase connectivity"""
    try:
        manager = get_storage_manager()
        if not manager.enabled:
            return False
        
        # Test database connection
        client = manager.get_client()
        result = client.table("schema_version").select("*").limit(1).execute()
        
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    sys.exit(0 if check_supabase_health() else 1)
```

---

## 🎨 NEW ARCHITECTURAL DESIGNS (2025-10-16)

### 1. PERFORMANCE TRACKING SYSTEM ✅ DESIGNED

**Conversation ID:** `0a6d1ef3-1311-4bfd-8230-57cb8e1d09ff`
**Model:** GLM-4.6 with web search (53.4s response time)
**Documentation:** `PERFORMANCE_TRACKING_DESIGN_2025-10-16.md`

**Purpose:** Track model response times and performance metrics across all providers

**Key Features:**
- **Time-series tables:** Raw data, hourly aggregates, daily aggregates
- **Statistical aggregation:** avg, p50, p95, p99 instead of storing every call
- **Smart parameter hashing:** Only performance-affecting params (model, temperature, etc.)
- **Retention policy:** 7d raw, 90d hourly, 2y daily (automatic cleanup)
- **Automated aggregation:** PostgreSQL functions for hourly/daily rollups
- **Query interface:** Performance trends, model comparisons, bottleneck identification

**Supabase Schema:**
```sql
-- Raw performance data (7-day retention)
CREATE TABLE performance_metrics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  tool_name TEXT NOT NULL,
  model_name TEXT NOT NULL,
  provider TEXT NOT NULL,
  duration_ms INTEGER NOT NULL,
  token_count INTEGER,
  param_hash TEXT NOT NULL,  -- Hash of performance-affecting params
  conversation_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Hourly aggregates (90-day retention)
CREATE TABLE performance_hourly (
  hour TIMESTAMPTZ NOT NULL,
  tool_name TEXT NOT NULL,
  model_name TEXT NOT NULL,
  provider TEXT NOT NULL,
  param_hash TEXT NOT NULL,
  call_count INTEGER NOT NULL,
  avg_duration_ms NUMERIC(10,2),
  p50_duration_ms INTEGER,
  p95_duration_ms INTEGER,
  p99_duration_ms INTEGER,
  total_tokens BIGINT,
  PRIMARY KEY (hour, tool_name, model_name, provider, param_hash)
);

-- Daily aggregates (2-year retention)
CREATE TABLE performance_daily (
  day DATE NOT NULL,
  tool_name TEXT NOT NULL,
  model_name TEXT NOT NULL,
  provider TEXT NOT NULL,
  param_hash TEXT NOT NULL,
  call_count INTEGER NOT NULL,
  avg_duration_ms NUMERIC(10,2),
  p50_duration_ms INTEGER,
  p95_duration_ms INTEGER,
  p99_duration_ms INTEGER,
  total_tokens BIGINT,
  PRIMARY KEY (day, tool_name, model_name, provider, param_hash)
);
```

**Implementation Status:** ⏳ Design complete, ready for Phase 2 implementation

---

### 2. UNIFIED FILE HANDLING ARCHITECTURE ✅ DESIGNED

**Conversation ID:** `a0bdb843-a6e8-46b8-962b-0ad5deca73ba`
**Model:** GLM-4.6 with web search (38.8s response time)
**Documentation:** `UNIFIED_FILE_HANDLING_ARCHITECTURE_2025-10-16.md`

**Purpose:** Unified file handling for Docker-based EXAI with multiple storage backends

**Problem Statement:**
- EXAI runs in Docker container and can't access local files directly
- Multiple file handling systems (Moonshot, GLM, Supabase) with no unified strategy
- EXAI tools expect file paths but container has no access to host filesystem

**Solution Architecture:**

**Storage Strategy:**
1. **Supabase Storage (Primary):** Permanent storage for all files
2. **Provider-specific uploads (On-demand):** Moonshot/GLM file IDs when needed
3. **Local volume mount (Cache):** `./files:/app/files` for fast access
4. **Three-tier fallback:** Supabase → Local → In-memory

**Unified API:**
```python
class UnifiedFileHandler:
    async def upload_file(self, file_path: str, content: bytes) -> FileMetadata:
        """Upload file to Supabase and optionally to providers"""
        # 1. Upload to Supabase Storage (primary)
        supabase_url = await self.supabase.upload(file_path, content)

        # 2. Cache locally in volume mount
        local_path = await self.cache_locally(file_path, content)

        # 3. Store metadata in database
        metadata = await self.store_metadata(file_path, supabase_url, local_path)

        return metadata

    async def get_provider_file_id(self, file_path: str, provider: str) -> str:
        """Get provider-specific file ID (upload on-demand)"""
        # Check cache first
        if cached_id := await self.get_cached_provider_id(file_path, provider):
            return cached_id

        # Upload to provider and cache ID
        if provider == "moonshot":
            file_id = await self.moonshot.upload(file_path)
        elif provider == "glm":
            file_id = await self.glm.upload(file_path)

        await self.cache_provider_id(file_path, provider, file_id)
        return file_id
```

**Docker Volume Strategy:**
```yaml
# docker-compose.yml
services:
  exai-mcp-daemon:
    volumes:
      - ./logs:/app/logs
      - ./files:/app/files  # NEW: File cache volume
```

**Supabase Metadata Schema:**
```sql
CREATE TABLE file_metadata (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  file_path TEXT NOT NULL,
  supabase_url TEXT NOT NULL,
  local_path TEXT,
  moonshot_file_id TEXT,
  glm_file_id TEXT,
  file_size BIGINT,
  mime_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Implementation Plan:** 4-week phased rollout
- **Week 1:** Core infrastructure (UnifiedFileHandler, Supabase integration)
- **Week 2:** Provider integration (Moonshot, GLM)
- **Week 3:** Tool integration (EXAI tools)
- **Week 4:** Testing & migration

**Implementation Status:** ⏳ Design complete, ready for Phase 2 implementation

---

## 🗺️ IMPLEMENTATION ROADMAP

### PHASE 1: FOUNDATION ✅ COMPLETE (2025-10-16)
**Status:** ✅ 100% Complete - Dual Storage Operational

**Completed:**
- [x] Database schema deployed (conversations, messages, files tables)
- [x] Storage buckets created (conversation-files, user-uploads)
- [x] Environment configuration (.env.docker with all required variables)
- [x] Dual storage manager (Redis + Supabase)
- [x] Redis persistence (AOF + RDB, 24-hour TTL)
- [x] Health checks implemented
- [x] Docker integration with exai-network
- [x] Connection pooling ready (Redis 6.4.0)
- [x] Full validation testing complete

**Deliverables:**
- ✅ Working conversation persistence (dual storage)
- ✅ File upload/download (Supabase ready)
- ✅ Production Docker integration
- ✅ Redis Commander monitoring (http://localhost:8081)
- ✅ Backup scripts (PowerShell + Bash)

---

### PHASE 2: ENHANCED FEATURES (Weeks 2-3) - REQUIRES PRO TIER

**Prerequisites:**
- Upgrade to Supabase Pro ($25/month)
- Phase 1 complete and tested

**Tasks:**
1. **Edge Functions** (3 days)
   - Deploy message-preprocess function
   - Deploy conversation-summarize function
   - Deploy file-processor function
   - Integrate with EXAI tools

2. **Realtime Subscriptions** (2 days)
   - Implement Python realtime client
   - Subscribe to conversation updates
   - Add presence tracking
   - Integrate with WebSocket daemon

3. **pgvector Integration** (3 days)
   - Enable pgvector extension
   - Add embedding column to messages
   - Implement vector search
   - Integrate with Kimi/GLM embeddings

4. **Connection Pooling** (1 day)
   - Add pgbouncer to Docker Compose
   - Configure connection pooling
   - Test performance improvements

**Deliverables:**
- Serverless AI preprocessing
- Live conversation updates
- Semantic search capability
- Optimized database connections

---

### PHASE 3: ADVANCED FEATURES (Weeks 4-6)

**Tasks:**
1. **Multi-User Auth & RLS** (5 days)
   - Implement JWT authentication
   - Enable RLS policies
   - Add user management
   - Test multi-user scenarios

2. **Storage Enhancements** (3 days)
   - Enable image transformations
   - Implement resumable uploads
   - Add CDN configuration
   - Optimize file access

3. **Webhooks & Integrations** (3 days)
   - Implement database webhooks
   - Add webhook handler Edge Function
   - Integrate with external services
   - Add event-driven workflows

4. **Analytics & Monitoring** (2 days)
   - Implement usage tracking
   - Add performance monitoring
   - Create analytics dashboard
   - Set up alerting

**Deliverables:**
- Multi-user support with secure access
- Advanced file handling
- External integrations
- Comprehensive monitoring

---

### PHASE 4: PRODUCTION HARDENING (Weeks 7-8)

**Tasks:**
1. **Performance Optimization** (3 days)
   - Optimize database queries
   - Add caching layer
   - Implement rate limiting
   - Load testing

2. **Security Hardening** (2 days)
   - Audit RLS policies
   - Implement API key rotation
   - Add audit logging
   - Security testing

3. **Disaster Recovery** (2 days)
   - Configure point-in-time recovery
   - Implement backup automation
   - Test restore procedures
   - Document recovery process

4. **Documentation & Training** (1 day)
   - Update all documentation
   - Create deployment guides
   - Write troubleshooting guides
   - Team training

**Deliverables:**
- Production-ready system
- Comprehensive security
- Disaster recovery plan
- Complete documentation

---

## 💰 COST OPTIMIZATION STRATEGY

### Free Tier Optimization (Phase 1)
- Implement conversation cleanup after 30 days
- Compress file uploads before storage
- Optimize query patterns to reduce bandwidth
- Monitor usage with custom tracking

### Pro Tier Benefits (Phase 2+)
- pgvector for semantic search (critical feature)
- 100 Edge Functions (vs 2 on Free)
- Point-in-time recovery (data safety)
- 100GB bandwidth (vs 1GB)
- Priority support

### Usage Monitoring
```python
# src/monitoring/usage_tracker.py
class UsageTracker:
    def __init__(self, supabase_client):
        self.client = supabase_client
    
    async def track_usage(self, metric, value):
        """Track usage metrics"""
        await self.client.table('usage_metrics').insert({
            'metric': metric,
            'value': value,
            'timestamp': datetime.now()
        }).execute()
    
    async def get_monthly_usage(self):
        """Get current month usage"""
        result = await self.client.table('usage_metrics').select('*').gte(
            'timestamp', datetime.now().replace(day=1)
        ).execute()
        return result.data
```

---

## 🔒 SECURITY BEST PRACTICES

### 1. API Key Management
- Store keys in environment variables only
- Never commit keys to git
- Rotate service role key quarterly
- Use separate keys for dev/staging/prod

### 2. RLS Policy Design
- Enable RLS on all user-facing tables
- Test policies thoroughly before production
- Use service role key only for admin operations
- Implement audit logging for sensitive operations

### 3. Docker Secrets
```dockerfile
# Use Docker secrets for sensitive data
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy application
COPY --chown=appuser:appuser . /app
WORKDIR /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s \
  CMD python scripts/health_check.py

CMD ["python", "-m", "src.main"]
```

---

## 📋 NEXT IMMEDIATE ACTIONS

### Priority 1: Fix Library Compatibility (Today)
1. Try upgrading: `pip install --upgrade supabase`
2. If fails, downgrade: `pip install supabase==2.4.0`
3. Run connection test: `python scripts/testing/test_supabase_connection.py`
4. Verify all 6 tests pass

### Priority 2: Add Health Checks (Tomorrow)
1. Create `scripts/health_check.py`
2. Add to Dockerfile as HEALTHCHECK
3. Test health check functionality
4. Document health check endpoints

### Priority 3: Plan Pro Tier Upgrade (This Week)
1. Review Pro tier features needed
2. Calculate ROI for $25/month
3. Plan Phase 2 implementation timeline
4. Prepare upgrade checklist

---

## 🎯 SUCCESS METRICS

### Phase 1 Success Criteria
- ✅ All 6 connection tests passing
- ✅ Conversation persistence working
- ✅ File upload/download working
- ✅ Health checks implemented
- ✅ Docker container stable

### Phase 2 Success Criteria
- ✅ Edge Functions deployed and working
- ✅ Realtime subscriptions active
- ✅ pgvector semantic search functional
- ✅ Connection pooling optimized
- ✅ Performance benchmarks met

### Phase 3 Success Criteria
- ✅ Multi-user auth working
- ✅ RLS policies tested
- ✅ Webhooks integrated
- ✅ Analytics dashboard live

### Phase 4 Success Criteria
- ✅ Production deployment successful
- ✅ Security audit passed
- ✅ Disaster recovery tested
- ✅ Documentation complete

---

**Document Status:** COMPREHENSIVE ARCHITECTURE PLAN  
**Next Review:** After Phase 1 completion  
**Owner:** EXAI Development Team  
**GLM-4.6 Research:** Complete ✅

