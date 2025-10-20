# Performance Fix Status - 2025-10-16 21:30 AEDT

## Issue Tracked in Supabase
**Issue ID**: `926e2c85-98d0-4163-a0c3-7299ee05416c`
**Title**: Performance Regression: 7 Supabase Calls Per Request
**Status**: Code Complete, Deployment Blocked

---

## Problem Summary

### Root Cause
Conversation storage making **7 HTTP calls to Supabase per request**:
1. GET /conversations (resume thread)
2. GET /messages (load history)
3. GET /conversations (DUPLICATE - building context)
4. GET /messages (DUPLICATE - building context)
5. GET /messages (THIRD TIME - generating response)
6. GET /conversations (FOURTH TIME - saving response)
7. POST /messages (save new message)

### Impact
- **350-1050ms overhead** per request from redundant HTTP calls
- Performance regression from **40-60s to 3+ minutes**
- No caching of conversation history
- Storage initialized on every call (lazy initialization bug)

---

## Solution Implemented

### GLM-4.6 Recommendation (with Web Search)
**Recommended Approach**: Option C - Multi-layer cache with singleton pattern

**Architecture**:
```
┌─────────────────┐
│   Application   │
└─────────┬───────┘
          │
┌─────────▼───────┐     ┌─────────────────┐     ┌─────────────────┐
│  L1: In-Memory  │────▶│   L2: Redis     │────▶│  L3: Supabase   │
│  (LRU Cache)    │     │   (Distributed) │     │ (Persistence)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Cache Configuration**:
- **L1**: In-memory TTLCache (5min TTL, 100 items) - fastest
- **L2**: Redis distributed cache (30min TTL) - fast, persistent across restarts
- **L3**: Supabase storage - persistent, source of truth

**Expected Performance**:
- Cache hit: **0 Supabase calls**
- Cache miss: **2 Supabase calls** (1 load, 1 save)
- Overhead reduction: **350-1050ms → 10-50ms**

---

## Code Changes Completed

### 1. Created `utils/conversation/cache_manager.py` ✅
**Purpose**: Multi-layer cache manager for conversation storage

**Features**:
- Singleton pattern with thread-safe initialization
- L1 cache: TTLCache (or fallback dict if cachetools not available)
- L2 cache: Redis with lazy initialization
- Write-through pattern for cache updates
- Cache invalidation support
- Cache statistics tracking

**Key Methods**:
- `get_conversation(conversation_id)` - Check L1 → L2 → None
- `get_messages(conversation_id)` - Check L1 → L2 → None
- `set_conversation(conversation_id, conversation)` - Write to L1 + L2
- `set_messages(conversation_id, messages)` - Write to L1 + L2
- `invalidate(conversation_id)` - Clear from all cache layers
- `get_stats()` - Return cache hit/miss statistics

### 2. Modified `utils/conversation/supabase_memory.py` ✅
**Changes**:
- Added import: `from .cache_manager import get_cache_manager`
- Added cache manager initialization in `__init__`
- Modified `get_thread()` to check cache before Supabase
- Added cache population after Supabase load
- Added cache invalidation after `add_turn()`

**Cache Flow**:
```python
def get_thread(self, continuation_id):
    # Check cache first (L1 → L2)
    cached_conv = self.cache.get_conversation(continuation_id)
    cached_messages = self.cache.get_messages(continuation_id)
    
    if cached_conv and cached_messages:
        # Cache hit - no Supabase calls!
        return build_thread(cached_conv, cached_messages)
    
    # Cache miss - load from Supabase
    conv = self.storage.get_conversation_by_continuation_id(continuation_id)
    messages = self.storage.get_conversation_messages(conv['id'])
    
    # Populate cache for next request
    self.cache.set_conversation(continuation_id, conv)
    self.cache.set_messages(continuation_id, messages)
    
    return build_thread(conv, messages)
```

---

## Deployment Issue - RESOLVED ✅

### Problem
**Docker layer caching was preventing new files from being copied to the container**

### Root Cause
1. **Missing directory in Dockerfile**: The `streaming/` directory was not being copied
2. **Docker layer caching**: The `COPY utils/ ./utils/` layer was being cached even with `--no-cache` flag

### Solution Applied
1. **Updated Dockerfile** to include `streaming/` directory:
   ```dockerfile
   COPY streaming/ ./streaming/
   ```
2. **Complete rebuild** with clean slate:
   ```powershell
   docker-compose down
   docker rmi exai-mcp-server:latest
   docker-compose build --no-cache exai-daemon
   docker-compose up -d
   ```

### Verification
✅ **cache_manager.py** exists in container: `/app/utils/conversation/cache_manager.py`
✅ **supabase_memory.py** has cache integration (CACHE HIT/MISS logging)
✅ **Cache manager initialized** at startup:
```
[CACHE_MANAGER] L1 cache initialized: TTLCache(maxsize=100, ttl=300s)
[CACHE_MANAGER] Conversation cache manager initialized
```

---

## Validation Plan - READY FOR TESTING

### ✅ Pre-Deployment Checks (COMPLETE)

1. **Files in Container** ✅
   ```powershell
   docker exec exai-mcp-daemon ls -la /app/utils/conversation/ | Select-String "cache"
   # Result: cache_manager.py exists (10024 bytes, Oct 16 10:15)
   ```

2. **Cache Manager Initialization** ✅
   ```powershell
   docker logs exai-mcp-daemon --tail 100 | Select-String "CACHE_MANAGER"
   # Result: [CACHE_MANAGER] L1 cache initialized: TTLCache(maxsize=100, ttl=300s)
   #         [CACHE_MANAGER] Conversation cache manager initialized
   ```

### 🧪 Performance Testing (NEXT STEP)

**Test 1: Cache Miss (First Call)**
```powershell
# Make first EXAI chat call with continuation_id
# Expected: CACHE MISS, 2-3 Supabase calls
docker logs exai-mcp-daemon --tail 200 | Select-String "CACHE MISS|HTTP Request.*supabase"
```

**Test 2: Cache Hit (Second Call)**
```powershell
# Make second call with SAME continuation_id
# Expected: CACHE HIT, 0-1 Supabase calls
docker logs exai-mcp-daemon --tail 200 | Select-String "CACHE HIT|HTTP Request.*supabase"
```

**Test 3: Performance Measurement**
```powershell
# Count Supabase calls before and after
docker logs exai-mcp-daemon --since "2025-10-16T10:30:00" | Select-String "HTTP Request.*supabase" | Measure-Object
# Expected reduction: 7 calls → 0 (cache hit) or 2 (cache miss)
```

### 📊 Success Criteria

- ✅ Cache manager initializes at startup
- ⏳ First call shows CACHE MISS + 2-3 Supabase calls
- ⏳ Second call shows CACHE HIT + 0-1 Supabase calls
- ⏳ Response time improves from 3+ minutes to 40-60 seconds
- ⏳ Overhead reduces from 350-1050ms to 10-50ms

---

## Summary

### ✅ Completed
1. Root cause analysis (7 Supabase calls per request)
2. GLM-4.6 consultation for solution design
3. Multi-layer cache implementation
4. Code changes to supabase_memory.py
5. Issue tracking in Supabase

### ⚠️ Blocked
1. Docker deployment (layer caching issue)
2. Testing and validation
3. Performance measurement

### 🎯 Required Action
**Fix Docker deployment** using one of the three options above, then proceed with validation plan.

---

## Complete Docker Configuration

### Dockerfile
```dockerfile
# EXAI MCP Server - Docker Image
# Multi-stage build for optimized image size

# Stage 1: Builder
FROM python:3.13-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Add /app to PYTHONPATH so imports work
ENV PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src/ ./src/
COPY tools/ ./tools/
COPY utils/ ./utils/
COPY systemprompts/ ./systemprompts/
COPY streaming/ ./streaming/
COPY scripts/ws/ ./scripts/ws/
COPY scripts/health_check.py ./scripts/
COPY server.py ./
COPY config.py ./
COPY .env.docker .env

# Create logs directory
RUN mkdir -p logs

# Expose WebSocket port
EXPOSE 8079

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python scripts/health_check.py || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    LOG_LEVEL=INFO \
    EXAI_WS_HOST=0.0.0.0 \
    EXAI_WS_PORT=8079

# Run daemon
CMD ["python", "-u", "scripts/ws/run_ws_daemon.py"]
```

### docker-compose.yml
```yaml
services:
  exai-daemon:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: exai-mcp-daemon
    image: exai-mcp-server:latest

    # Port mapping: host:container
    ports:
      - "8079:8079"

    # Environment variables (override .env.docker)
    environment:
      - PYTHONUNBUFFERED=1
      - PYTHONIOENCODING=utf-8

    # Mount .env.docker as .env in container
    env_file:
      - .env.docker

    # Volume mounts for logs (optional - for debugging)
    volumes:
      - ./logs:/app/logs

    # Depends on Redis for conversation storage
    depends_on:
      - redis

    # Restart policy
    restart: unless-stopped

    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import socket; s = socket.socket(); s.settimeout(2); s.connect(('127.0.0.1', 8079)); s.close(); exit(0)"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

    # File descriptor limits
    ulimits:
      nofile:
        soft: 4096
        hard: 8192

    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis service for conversation persistence
  redis:
    image: redis:7-alpine
    container_name: exai-redis
    command: redis-server /usr/local/etc/redis/redis.conf
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 4G
        reservations:
          cpus: '0.25'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # Redis Commander for monitoring
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: exai-redis-commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    depends_on:
      - redis
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "5m"
        max-file: "2"

# Named volumes for persistence
volumes:
  redis-data:
    driver: local
    name: exai-redis-data

# Networks
networks:
  default:
    name: exai-network
    driver: bridge
```

### Key Directories Copied to Container
- `src/` - Core application code
- `tools/` - EXAI MCP tools
- `utils/` - Utility modules (including conversation storage)
- `systemprompts/` - System prompts for tools
- `streaming/` - Streaming adapter (ADDED in fix)
- `scripts/ws/` - WebSocket daemon scripts
- `scripts/health_check.py` - Health check script
- `server.py` - Main server entry point
- `config.py` - Configuration module

---

**Document Created**: 2025-10-16 21:30 AEDT
**Last Updated**: 2025-10-16 21:45 AEDT
**Status**: ✅ Deployed and ready for testing
**Next Action**: Test cache performance with real EXAI calls

