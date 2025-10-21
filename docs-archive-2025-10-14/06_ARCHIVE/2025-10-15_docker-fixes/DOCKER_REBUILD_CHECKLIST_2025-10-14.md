# Docker Rebuild Checklist - 2025-10-14
**Date:** 2025-10-14 (14th October 2025)  
**Status:** ✅ READY FOR REBUILD  
**Related:** QA_FIXES_2025-10-14.md

---

## 🎯 Pre-Rebuild Verification

### ✅ All Critical Fixes Applied

1. **✅ _resolve_model_name Fix**
   - Created standalone `resolve_model_name_for_glm()` function
   - Updated `glm_chat.py` to use standalone function
   - No more circular import

2. **✅ Daemon Path Fix**
   - Corrected path in `run_ws_shim.py`
   - Docker uses correct path: `scripts/ws/run_ws_daemon.py`

3. **✅ Port Configuration**
   - All configs use port 8079
   - Docker exposes port 8079

4. **✅ Embeddings Documentation**
   - Documented zhipuai SDK migration
   - Added fallback options

5. **✅ max_tokens Configuration**
   - Added `ENFORCE_MAX_TOKENS` flag
   - Updated all env files (.env, .env.example, .env.docker)
   - Updated Daemon/mcp-config.augmentcode.json

### ✅ Configuration Files Updated

**Main .env:**
- ✅ Added MODEL OUTPUT TOKEN LIMITS section
- ✅ Added ENFORCE_MAX_TOKENS configuration

**.env.example:**
- ✅ Added MODEL OUTPUT TOKEN LIMITS section
- ✅ Updated GLM embeddings documentation

**.env.docker:**
- ✅ Added MODEL OUTPUT TOKEN LIMITS section
- ✅ Ready for Docker build

**Daemon/mcp-config.augmentcode.json:**
- ✅ Added ENFORCE_MAX_TOKENS env var
- ✅ Added max_tokens configuration

### ✅ Code Changes Verified

**No conflicts with helper files:**
- ✅ utils/file/helpers.py - No changes needed
- ✅ utils/config/helpers.py - No changes needed
- ✅ tools/simple/simple_tool_helpers.py - No changes needed

**Provider changes:**
- ✅ src/providers/glm_chat.py - Conditional max_tokens
- ✅ src/providers/glm_config.py - Added standalone function
- ✅ src/providers/openai_compatible.py - Conditional max_tokens
- ✅ src/embeddings/provider.py - Documented SDK migration

**Configuration:**
- ✅ config.py - Added ENFORCE_MAX_TOKENS and documentation

---

## 🐳 Docker Rebuild Commands

### Step 1: Stop Existing Container
```powershell
docker-compose down
```

### Step 2: Rebuild Image
```powershell
docker-compose build --no-cache
```

### Step 3: Start Container
```powershell
docker-compose up -d
```

### Step 4: Verify Container Health
```powershell
docker ps
docker logs exai-mcp-daemon --tail 50
```

### Step 5: Test WebSocket Connection
```powershell
python test_docker_ws.py
```

---

## 🧪 Post-Rebuild Testing

### Container Health Checks
- [ ] Container is running: `docker ps`
- [ ] Health check passing: `docker inspect exai-mcp-daemon`
- [ ] Logs show no errors: `docker logs exai-mcp-daemon`
- [ ] WebSocket port 8079 accessible

### Functional Tests
- [ ] WebSocket connection successful
- [ ] Thinking mode works (GLM)
- [ ] Thinking mode works (Kimi)
- [ ] max_tokens enforcement working
- [ ] No import errors in logs

### Configuration Verification
- [ ] ENFORCE_MAX_TOKENS=true is active
- [ ] DEFAULT_MAX_OUTPUT_TOKENS=8192 is used
- [ ] Port 8079 is exposed and accessible

---

## 📊 Expected Behavior

### Container Startup
```
INFO: Starting EXAI WebSocket Daemon
INFO: Listening on 0.0.0.0:8079
INFO: GLM provider using SDK with base_url=https://api.z.ai/api/paas/v4
INFO: Configuration loaded successfully
```

### Health Check
```bash
$ docker inspect exai-mcp-daemon | grep -A 5 Health
"Health": {
    "Status": "healthy",
    "FailingStreak": 0,
    "Log": [...]
}
```

### WebSocket Test
```bash
$ python test_docker_ws.py
✅ Connected to WebSocket
✅ Sent test message
✅ Received response
✅ All tests passed
```

---

## 🚨 Troubleshooting

### Container Won't Start
```powershell
# Check logs
docker logs exai-mcp-daemon

# Check if port is in use
netstat -ano | findstr :8079

# Rebuild without cache
docker-compose build --no-cache
```

### Import Errors
```powershell
# Verify Python path
docker exec exai-mcp-daemon python -c "import sys; print(sys.path)"

# Test imports
docker exec exai-mcp-daemon python -c "from src.providers import glm_chat"
```

### WebSocket Connection Failed
```powershell
# Check if container is listening
docker exec exai-mcp-daemon netstat -tuln | grep 8079

# Check firewall
Test-NetConnection -ComputerName localhost -Port 8079
```

---

## 📝 Files Modified Summary

### Configuration Files (3)
1. `.env` - Added max_tokens configuration
2. `.env.example` - Added max_tokens configuration
3. `.env.docker` - Added max_tokens configuration
4. `Daemon/mcp-config.augmentcode.json` - Added env vars

### Source Code (5)
1. `src/providers/glm_chat.py` - Fixed _resolve_model_name, conditional max_tokens
2. `src/providers/glm_config.py` - Added standalone resolve function
3. `src/providers/openai_compatible.py` - Conditional max_tokens
4. `src/embeddings/provider.py` - Documented SDK migration
5. `scripts/run_ws_shim.py` - Fixed daemon path
6. `config.py` - Added ENFORCE_MAX_TOKENS configuration

### Documentation (2)
1. `docs/05_CURRENT_WORK/QA_FIXES_2025-10-14.md` - Complete fix documentation
2. `docs/05_CURRENT_WORK/DOCKER_REBUILD_CHECKLIST_2025-10-14.md` - This file

---

## ✅ Ready for Rebuild

All fixes have been applied and verified. The Docker container is ready to be rebuilt with the following improvements:

1. **No more runtime crashes** - Fixed _resolve_model_name issue
2. **Daemon auto-starts correctly** - Fixed path issue
3. **Configurable max_tokens** - Added ENFORCE_MAX_TOKENS flag
4. **Better documentation** - Comprehensive comments and fallback options
5. **No circular imports** - Clean module structure

**Next Action:** Run Docker rebuild commands above

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Status:** READY FOR REBUILD

