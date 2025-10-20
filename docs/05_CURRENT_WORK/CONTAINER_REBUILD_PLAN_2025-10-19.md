# Complete Container Rebuild Plan
**Date:** 2025-10-19  
**Priority:** 🔴 CRITICAL - System Imploded  
**Status:** 🔄 IN PROGRESS

---

## PROBLEM STATEMENT

**User's Assessment:**
> "The system is fully imploded on itself right now"

**Symptoms:**
1. ❌ Tools not working (`kimi_upload_files_EXAI-WS` not found)
2. ❌ GLM connection failures (Connection error)
3. ❌ Conversation history not preserved (continuation_id loses context)
4. ❌ Slow internal data flow (5-10s delays)
5. ❌ Tool cancellations mid-execution
6. ❌ Going in circles trying to fix issues

**Root Cause:**
- Container state is corrupted
- Tool registry may be out of sync
- Connections are unstable
- Cache/storage may be inconsistent

**Solution:**
**COMPLETE REBUILD FROM SCRATCH** with proper volume mounts and clean state.

---

## CURRENT VOLUME MOUNTS (docker-compose.yml)

```yaml
volumes:
  - ./logs:/app/logs                # Logs directory
  - ./docs:/app/docs                # Documentation for file upload tools
  - ./tools:/app/tools              # Tools directory (hot reload)
```

**Missing Critical Mounts:**
- ❌ `./src:/app/src` - Source code (providers, storage, monitoring)
- ❌ `./utils:/app/utils` - Utilities (conversation, caching, file handling)
- ❌ `./scripts:/app/scripts` - Scripts directory
- ❌ `./.env.docker:/app/.env` - Environment configuration (currently using env_file)

---

## REQUIRED VOLUME MOUNTS

### Development Mode (Current Need)
```yaml
volumes:
  # Source code (for hot reload during development)
  - ./src:/app/src
  - ./utils:/app/utils
  - ./tools:/app/tools
  - ./scripts:/app/scripts
  
  # Data directories
  - ./logs:/app/logs
  - ./docs:/app/docs
  
  # Configuration
  - ./.env.docker:/app/.env:ro  # Read-only mount
```

### Production Mode (Future)
```yaml
volumes:
  # Only data directories (code baked into image)
  - ./logs:/app/logs
  - ./docs:/app/docs
  - exai-data:/app/data  # Persistent data volume
```

---

## REBUILD STEPS

### Step 1: Stop and Remove Existing Container ✅
```powershell
docker stop exai-mcp-daemon
docker rm exai-mcp-daemon
```

**Status:** ✅ COMPLETE

### Step 2: Clean Docker Cache (Optional but Recommended)
```powershell
# Remove dangling images
docker image prune -f

# Remove build cache (if needed)
docker builder prune -f
```

### Step 3: Update docker-compose.yml with All Required Mounts
```yaml
services:
  exai-daemon:
    # ... existing config ...
    
    volumes:
      # Source code (development mode)
      - ./src:/app/src
      - ./utils:/app/utils
      - ./tools:/app/tools
      - ./scripts:/app/scripts
      
      # Data directories
      - ./logs:/app/logs
      - ./docs:/app/docs
      
      # Configuration (read-only)
      - ./.env.docker:/app/.env:ro
```

### Step 4: Rebuild Container Image
```powershell
docker-compose build --no-cache exai-daemon
```

**Why `--no-cache`?**
- Ensures fresh build
- Pulls latest base image
- Reinstalls all dependencies
- Clears any corrupted build layers

### Step 5: Start Container with New Configuration
```powershell
docker-compose up -d exai-daemon
```

### Step 6: Verify Container Health
```powershell
# Check container status
docker ps | Select-String "exai-mcp-daemon"

# Check logs for startup
docker logs exai-mcp-daemon --tail 50

# Verify health check
docker inspect exai-mcp-daemon --format='{{.State.Health.Status}}'
```

### Step 7: Verify Tool Registry
```powershell
# Check tool registration
docker exec exai-mcp-daemon python -c "
from src.server.providers.tool_registry import ToolRegistry
registry = ToolRegistry()
tools = registry.list_tools()
print(f'Total tools: {len(tools)}')
for tool in sorted(tools):
    print(f'  - {tool}')
"
```

### Step 8: Test Critical Tools
```powershell
# Test chat_EXAI-WS
docker exec exai-mcp-daemon python -c "
import asyncio
from tools.simple.base import SimpleTool

async def test():
    # Test basic chat
    result = await SimpleTool().execute({
        'tool_name': 'chat_EXAI-WS',
        'prompt': 'Test: What is 2+2?',
        'model': 'kimi-k2-0905-preview'
    })
    print('Chat test:', 'SUCCESS' if result else 'FAILED')

asyncio.run(test())
"
```

### Step 9: Test Provider Connections
```powershell
# Test GLM connection
docker exec exai-mcp-daemon python -c "
from src.providers.glm_chat import GLMChatProvider
provider = GLMChatProvider()
result = provider.generate_content(
    prompt='Test connection',
    model='glm-4.6',
    temperature=0.3
)
print('GLM test:', 'SUCCESS' if result else 'FAILED')
"

# Test Kimi connection
docker exec exai-mcp-daemon python -c "
from src.providers.kimi import KimiModelProvider
provider = KimiModelProvider()
result = provider.generate_content(
    prompt='Test connection',
    model='kimi-k2-0905-preview',
    temperature=0.3
)
print('Kimi test:', 'SUCCESS' if result else 'FAILED')
"
```

### Step 10: Verify Supabase Connection
```powershell
docker exec exai-mcp-daemon python -c "
from src.storage.supabase_client import get_supabase_client
client = get_supabase_client()
result = client.table('conversations').select('id').limit(1).execute()
print('Supabase test:', 'SUCCESS' if result else 'FAILED')
"
```

---

## VERIFICATION CHECKLIST

### Container Health
- [ ] Container is running
- [ ] Health check is passing
- [ ] All ports are exposed (8079, 8080, 8082, 8000)
- [ ] No error logs on startup

### Volume Mounts
- [ ] `/app/src` contains source code
- [ ] `/app/utils` contains utilities
- [ ] `/app/tools` contains tools
- [ ] `/app/scripts` contains scripts
- [ ] `/app/logs` is writable
- [ ] `/app/docs` contains documentation
- [ ] `/app/.env` exists and is readable

### Tool Registry
- [ ] All tools are registered
- [ ] `chat_EXAI-WS` is available
- [ ] `thinkdeep_EXAI-WS` is available
- [ ] `kimi_upload_files_EXAI-WS` is available (if it should exist)
- [ ] No duplicate tool registrations

### Provider Connections
- [ ] GLM connection works
- [ ] Kimi connection works
- [ ] Supabase connection works
- [ ] Redis connection works

### Conversation System
- [ ] Conversation storage works
- [ ] Continuation IDs are preserved
- [ ] History is included in prompts
- [ ] No token explosion

---

## POST-REBUILD TESTING

### Test 1: Simple Chat
```python
# Via MCP client
chat_EXAI-WS(
    prompt="What is 2+2?",
    model="kimi-k2-0905-preview"
)
# Expected: Response with "4"
```

### Test 2: Conversation Continuation
```python
# First call
result1 = chat_EXAI-WS(
    prompt="My favorite color is blue.",
    model="kimi-k2-0905-preview"
)
continuation_id = result1["continuation_offer"]["continuation_id"]

# Second call
result2 = chat_EXAI-WS(
    prompt="What is my favorite color?",
    continuation_id=continuation_id,
    model="kimi-k2-0905-preview"
)
# Expected: Response mentions "blue"
```

### Test 3: File Upload (if tool exists)
```python
# Upload test file
result = kimi_upload_files_EXAI-WS(
    files=["test_file_1.md"],
    purpose="file-extract"
)
# Expected: Returns file_id
```

### Test 4: Web Search
```python
# Chat with web search
result = chat_EXAI-WS(
    prompt="What is the latest version of Python?",
    model="glm-4.6",
    use_websearch=True
)
# Expected: Response with current Python version from web
```

---

## EXPECTED IMPROVEMENTS

### Performance
- ✅ Faster tool execution (no corrupted state)
- ✅ Reliable connections (fresh network stack)
- ✅ No mysterious delays

### Reliability
- ✅ Tools work consistently
- ✅ Conversation history preserved
- ✅ No mid-execution cancellations

### Developer Experience
- ✅ Hot reload works (source code mounted)
- ✅ Clear error messages
- ✅ Predictable behavior

---

## ROLLBACK PLAN

If rebuild fails or causes issues:

```powershell
# Stop new container
docker-compose down

# Restore previous docker-compose.yml from git
git checkout docker-compose.yml

# Rebuild with old config
docker-compose build exai-daemon
docker-compose up -d exai-daemon
```

---

## NEXT STEPS AFTER REBUILD

1. ✅ Verify all systems operational
2. ✅ Test EXAI consultation with file upload approach
3. ✅ Implement architectural upgrades (multi-session, async Supabase)
4. ✅ Implement context engineering (Phase 1)
5. ✅ Document lessons learned

---

**Status:** 🔄 **IN PROGRESS - Step 2/10**

**Current Step:** Update docker-compose.yml with all required volume mounts

