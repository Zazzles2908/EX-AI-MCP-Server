# Quick Fix Checklist - EX-AI-MCP-Server

**Priority Order:** Critical Fixes (1h) → Option 3 Integration (4h) → Technical Debt (2h)

---

## ✅ Priority 1: Critical Fixes (1 hour)

### Fix 1: Threading Lock in Async Context ⚠️ **MOST CRITICAL**
**File:** `src/daemon/ws_server.py`

```bash
# Line 386: Change threading.Lock to asyncio.Lock
- _results_cache_lock = threading.Lock()
+ _results_cache_lock = asyncio.Lock()

# Line 390: Make function async
- def _gc_results_cache() -> None:
+ async def _gc_results_cache() -> None:

# Line 392: Use async context manager
-         with _results_cache_lock:
+         async with _results_cache_lock:

# Find and update all callers
- _gc_results_cache()
+ await _gc_results_cache()
```

---

### Fix 2: Config Validation Crash
**File:** `src/core/config.py`

```python
# Line 61: Add null check
- if not self.supabase_url.startswith(("http://", "https://")):
+ if self.supabase_url and not self.supabase_url.startswith(("http://", "https://")):
      raise ValueError(...)
+ elif not self.supabase_url:
+     logger.warning("SUPABASE_URL not set - Supabase features will be unavailable")
```

---

### Fix 3: Remove Duplicate Exception Block
**File:** `src/daemon/ws_server.py`

```bash
# Delete lines 887-897 (duplicate except OSError block)
# Keep only the first block (lines 876-886)
```

---

### Fix 4: Consolidate Timeout Configuration
**Files:** `config/timeouts.py` + `config/operations.py`

```bash
# Step 1: Update all imports
find src/ tools/ -name "*.py" -exec sed -i \
  's/from config.timeouts import/from config.operations import/g' {} \;

# Step 2: Delete old file
rm config/timeouts.py

# Step 3: Standardize default to 46 seconds
# Edit config/operations.py line 74:
- WORKFLOW_TOOL_TIMEOUT_SECS: int = BaseConfig.get_int("WORKFLOW_TOOL_TIMEOUT_SECS", 45)
+ WORKFLOW_TOOL_TIMEOUT_SECS: int = BaseConfig.get_int("WORKFLOW_TOOL_TIMEOUT_SECS", 46)
```

---

## ✅ Priority 2: Complete Option 3 Integration (4 hours)

### Current State
- ✅ Native MCP server code exists (`src/daemon/mcp_server.py` - 382 lines)
- ❌ NOT integrated into main system
- ❌ No imports in `ws_server.py`
- ❌ Not started by daemon

### Integration Steps

#### Step 1: Add CLI Arguments
**File:** `src/daemon/ws_server.py` (add before `main_async()`)

```python
def parse_args():
    """Parse command line arguments."""
    import argparse
    parser = argparse.ArgumentParser(description="EXAI MCP Server")
    parser.add_argument(
        "--mode",
        choices=["websocket", "stdio", "both"],
        default="both",
        help="Server mode"
    )
    return parser.parse_args()
```

#### Step 2: Update main_async()
**File:** `src/daemon/ws_server.py`

```python
# Add import at top
from src.daemon.mcp_server import DaemonMCPServer

# Update main_async() function
async def main_async():
    args = parse_args()
    
    # ... existing initialization ...
    
    tasks = []
    
    # WebSocket server
    if args.mode in ["websocket", "both"]:
        ws_task = asyncio.create_task(run_websocket_server())
        tasks.append(ws_task)
    
    # Native MCP server
    if args.mode in ["stdio", "both"]:
        mcp_server = DaemonMCPServer(tool_registry, provider_registry)
        mcp_task = asyncio.create_task(mcp_server.run_stdio())
        tasks.append(mcp_task)
    
    await asyncio.gather(*tasks)
```

#### Step 3: Update Docker Configuration
**File:** `docker-compose.yml`

```yaml
services:
  # Existing WebSocket service
  exai-mcp-server:
    command: python -m src.daemon.ws_server --mode both
  
  # New STDIO service
  exai-mcp-stdio:
    build: .
    container_name: exai-mcp-stdio
    command: python -m src.daemon.ws_server --mode stdio
    stdin_open: true
    tty: true
    volumes:
      - .:/app
    env_file:
      - .env
```

#### Step 4: Update MCP Configuration
**File:** `.mcp.json` (Claude Code config)

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "docker",
      "args": [
        "exec", "-i", "exai-mcp-stdio",
        "python", "-m", "src.daemon.ws_server", "--mode", "stdio"
      ]
    }
  }
}
```

---

## ✅ Priority 3: Technical Debt Cleanup (2 hours)

### Task 1: Archive Deprecated Files
```bash
# Create archive branch
git checkout -b archive/deprecated-scripts

# Move to archive
git mv scripts/legacy archive_backup/legacy
git mv scripts/archive/deprecated archive_backup/deprecated
git commit -m "Archive 63 deprecated scripts"

# Switch back and delete
git checkout stdio-bridge-work
rm -rf scripts/legacy scripts/archive/deprecated
git commit -m "Remove deprecated scripts"
```

### Task 2: Move Misplaced Scripts
```bash
mv test_mcp_client_connection.py tests/connection/
mv test_ws_response.py tests/websocket/
mv test_manual.sh tests/manual/
mv debug_mcp_stdio.py scripts/diagnostics/
git add tests/ scripts/diagnostics/
git commit -m "Organize test scripts"
```

### Task 3: Consolidate Configuration
```bash
mv configurations/file_handling_guidance.py config/
rmdir configurations/
git add config/
git commit -m "Consolidate configuration"
```

### Task 4: Remove Unused Functions
```bash
# Edit src/daemon/ws_server.py
# Delete lines 359-371 (_lazy_init_provider_registry, _lazy_init_tool_registry)
git add src/daemon/ws_server.py
git commit -m "Remove unused lazy init functions"
```

---

## 🧪 Testing Checklist

### Test 1: Critical Fixes
```bash
# No threading errors
python -m src.daemon.ws_server --mode websocket
tail -f logs/mcp_server.log | grep -i "lock\|block"

# Config validation works without SUPABASE_URL
unset SUPABASE_URL
python -c "from src.core.config import Config; Config()"
```

### Test 2: Option 3 Works
```bash
# Native MCP server starts
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio

# MCP protocol works
echo '{"jsonrpc":"2.0","id":1,"method":"initialize",...}' | docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio
```

### Test 3: Claude Code Integration
```bash
# In Claude Code
@exai-mcp
# Should list 19 tools

# Test chat tool
"Use @exai-mcp chat to analyze this code"
# Should return response
```

---

## 📋 Completion Criteria

### Critical Fixes Complete ✅
- [ ] No `threading.Lock()` in async functions
- [ ] Server starts without SUPABASE_URL
- [ ] No duplicate exception blocks
- [ ] Single timeout configuration

### Option 3 Complete ✅
- [ ] Native MCP server integrated
- [ ] CLI arguments work (--mode stdio/websocket/both)
- [ ] Docker services configured
- [ ] All 19 tools accessible via MCP
- [ ] Claude Code connection works

### Technical Debt Complete ✅
- [ ] 0 deprecated files in scripts/
- [ ] All test scripts in tests/
- [ ] Single config/ directory
- [ ] No unused functions

---

## 🚀 Quick Start Commands

```bash
# Run all Priority 1 fixes
cd /workspace/ex-ai-mcp-server

# Fix 1: Threading lock
sed -i '386s/threading.Lock()/asyncio.Lock()/' src/daemon/ws_server.py
sed -i '390s/def _gc_results_cache/async def _gc_results_cache/' src/daemon/ws_server.py
sed -i '392s/with _results_cache_lock:/async with _results_cache_lock:/' src/daemon/ws_server.py

# Fix 2: Config validation
# (Manual edit required - see detailed instructions)

# Fix 3: Remove duplicate
sed -i '887,897d' src/daemon/ws_server.py

# Fix 4: Consolidate timeouts
find src/ tools/ -name "*.py" -exec sed -i 's/from config.timeouts import/from config.operations import/g' {} \;
rm config/timeouts.py

# Test
python -m src.daemon.ws_server --mode websocket
```

---

**Estimated Total Time:** 7 hours (1h + 4h + 2h)  
**Recommended Approach:** Fix Priority 1 first, test, then proceed to Priority 2

**Full Details:** See `/workspace/docs/COMPREHENSIVE_SYSTEM_ANALYSIS.md`
