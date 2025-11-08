# Troubleshooting Guide

This guide helps you diagnose and fix common issues with EXAI MCP Server.

## 🚨 Quick Diagnostics

### Check Server Status
```bash
# Docker containers
docker ps --filter name=exai-mcp-daemon

# Expected output:
# CONTAINER ID   IMAGE              STATUS
# exai-mcp-daemon  exai-mcp-server   Up (healthy)
```

### Check Port Status
```bash
# Port 3000 (host)
netstat -ano | findstr :3000

# Should show ESTABLISHED connections
```

### Check Logs
```bash
# Shim logs (most recent)
ls -lt logs/ws_shim_*.log | head -1 | awk '{print $NF}' | xargs tail -50

# Daemon logs
tail -50 logs/ws_daemon.log
```

## ❌ Common Issues

### Issue 1: "Connection Refused" Error

**Symptoms:**
```
WebSocket connection to ws://127.0.0.1:3000 failed
Error: Connection refused
```

**Diagnosis:**
1. Check if Docker is running: `docker ps`
2. Verify port mapping: `docker port exai-mcp-daemon 8079`
3. Check if port 3000 is free: `netstat -ano | findstr :3000`

**Solutions:**

**If Docker is not running:**
```bash
# Start Docker Desktop
# Or via command line (if available)
docker-compose up -d
```

**If port mapping is wrong:**
```bash
# Recreate container
docker-compose down
docker-compose up -d

# Verify mapping
docker port exai-mcp-daemon 8079
# Should output: 0.0.0.0:3000
```

**If port 3000 is in use:**
```bash
# Find process
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
# From: "3000:8079"
# To: "3001:8079"
# And update claude_desktop_config.json accordingly
```

### Issue 2: "Tools Not Loading" (0 tools)

**Symptoms:**
```
@exai-mcp status
# Returns: {"tools_loaded": []}
```

**Diagnosis:**
1. Check shim logs: `tail -f logs/ws_shim_*.log`
2. Look for: `"[LIST_TOOLS] Received 21 tools from daemon"`
3. Check for errors in daemon logs: `tail -f logs/ws_daemon.log`

**Solutions:**

**If shim is not connected:**
```bash
# Restart Claude Desktop
# (Close all windows, reopen)
```

**If daemon has errors:**
```bash
# Restart daemon
docker-compose restart exai-daemon

# Check logs for errors
tail -100 logs/ws_daemon.log
```

### Issue 3: "Event Loop Closed" Error

**Symptoms:**
```
Task got Future attached to a different loop
Event loop is closed
```

**Diagnosis:**
This is a Python asyncio issue when multiple event loops conflict.

**Solutions:**
1. **Restart Claude Desktop completely**
   - Close all windows
   - Wait 5 seconds
   - Reopen Claude Desktop

2. **Kill orphaned shim processes:**
```bash
# Find shim processes
tasklist | findstr python

# Kill specific PID
taskkill /PID <PID> /F
```

### Issue 4: "Port 8079 Already in Use"

**Symptoms:**
```
Error starting EXAI daemon: Address already in use
```

**Diagnosis:**
Port 8079 (inside container) is being used by another process.

**Solutions:**
```bash
# Check for conflicting containers
docker ps -a

# Stop conflicting containers
docker stop <container_name>

# Or restart the daemon
docker-compose restart exai-daemon
```

### Issue 5: Authentication Errors

**Symptoms:**
```
JWT token invalid
Auth token mismatch
```

**Diagnosis:**
JWT or auth tokens are missing or incorrect.

**Solutions:**
1. **Check JWT token in config:**
```bash
cat C:/Users/Jazeel-Home/AppData/Roaming/Claude/claude_desktop_config.json | grep JWT
```

2. **Verify token in .env:**
```bash
grep EXAI_JWT_TOKEN .env
```

3. **Regenerate tokens:**
```bash
# If you have the generation script
python scripts/generate_all_jwt_tokens.py
```

## 🔧 Configuration Issues

### Wrong Port in Config

**Problem:** Using port 8079 instead of 3000

**Check:**
```bash
grep EXAI_WS_PORT C:/Users/Jazeel-Home/AppData/Roaming/Claude/claude_desktop_config.json
```

**Fix:**
```json
// In claude_desktop_config.json
"EXAI_WS_PORT": "3000"  // ✅ Correct
```

### Missing Environment Variables

**Check required variables:**
```bash
# In .env file
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3000
EXAI_WS_TOKEN=test-token-12345
EXAI_JWT_TOKEN=...
```

**Fix missing variables:**
```bash
# Add to .env
echo "EXAI_WS_TOKEN=test-token-12345" >> .env
echo "EXAI_JWT_TOKEN=eyJ..." >> .env

# Restart Docker
docker-compose restart exai-daemon
```

## 📊 Performance Issues

### Slow Tool Execution

**Symptoms:**
- Tools take >30 seconds to respond
- Timeouts occurring

**Diagnosis:**
1. Check provider timeouts in config
2. Check network connectivity to AI providers
3. Check daemon resource usage

**Solutions:**
```bash
# Increase timeouts in .env
SIMPLE_TOOL_TIMEOUT_SECS=120
WORKFLOW_TOOL_TIMEOUT_SECS=300
GLM_TIMEOUT_SECS=120
KIMI_TIMEOUT_SECS=150

# Restart
docker-compose restart exai-daemon
```

### High Memory Usage

**Symptoms:**
- Docker container using >2GB RAM
- System slowdown

**Diagnosis:**
```bash
# Check container stats
docker stats exai-mcp-daemon
```

**Solutions:**
```bash
# Restart daemon to clear memory
docker-compose restart exai-daemon

# Or increase resource limits
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 4G
```

## 🐛 Debug Mode

### Enable Debug Logging

**Shim debug:**
```bash
# In claude_desktop_config.json
"LOG_LEVEL": "DEBUG"
```

**Daemon debug:**
```bash
# In .env
LOG_LEVEL=DEBUG

# Restart
docker-compose restart exai-daemon
```

### Trace Message Flow

1. **Start tailing logs:**
```bash
# Terminal 1: Shim
tail -f logs/ws_shim_*.log

# Terminal 2: Daemon
tail -f logs/ws_daemon.log
```

2. **Execute a tool:**
```
@exai-mcp status
```

3. **Trace the flow:**
   - Look for request in shim log
   - Look for forwarded message in daemon log
   - Look for response back to shim
   - Look for final response to Claude

### WebSocket Frame Inspection

**Check WebSocket activity:**
```bash
# Watch for WebSocket messages
tail -f logs/ws_daemon.log | grep "WebSocket"
```

**Look for:**
```
WebSocket connection established
Received message: {"op":"list_tools",...}
Sending response: {"op":"list_tools_res",...}
```

## 🆘 Emergency Recovery

### Complete Reset

If all else fails, perform a complete reset:

```bash
# 1. Stop everything
docker-compose down

# 2. Remove containers
docker-compose rm -f

# 3. Remove images
docker rmi exai-mcp-server:latest

# 4. Clean logs
rm -rf logs/ws_shim_*.log
rm -f logs/ws_daemon.log

# 5. Rebuild and start
docker-compose build
docker-compose up -d

# 6. Verify
docker ps --filter name=exai-mcp-daemon
@exai-mcp status
```

### Backup Before Reset

```bash
# Backup configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# Backup logs (if needed for debugging)
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

## 📞 Getting Help

### Information to Collect

When reporting an issue, include:

1. **System information:**
```bash
# Docker version
docker --version

# Python version
python --version

# OS version
ver
```

2. **Configuration:**
```bash
# Port mapping
docker port exai-mcp-daemon

# Environment
cat .env | grep EXAI_WS
```

3. **Logs:**
```bash
# Recent daemon errors
tail -100 logs/ws_daemon.log | grep ERROR

# Recent shim activity
tail -50 logs/ws_shim_*.log
```

4. **Status:**
```bash
# Container status
docker ps --filter name=exai-mcp-daemon

# Port status
netstat -ano | findstr :3000
```

### Useful Commands Reference

```bash
# Check server
@exai-mcp status

# Check Docker
docker ps --filter name=exai-mcp-daemon

# Check ports
docker port exai-mcp-daemon 8079
netstat -ano | findstr :3000

# Check logs
tail -50 logs/ws_daemon.log
tail -50 logs/ws_shim_*.log

# Restart
docker-compose restart exai-daemon

# Complete reset
docker-compose down && docker-compose up -d
```

## ✅ Success Checklist

After troubleshooting, verify:

- [ ] `@exai-mcp status` returns server info
- [ ] `@exai-mcp chat "test"` responds
- [ ] 21 tools are available
- [ ] No ERROR logs in shim
- [ ] No ERROR logs in daemon
- [ ] Port 3000 shows ESTABLISHED connections
- [ ] Docker container is healthy

## 📚 Related Documentation

- **[Architecture Guide](../architecture/exai-mcp-architecture.md)** - Understand the system
- **[Configuration Guide](../development/configuration.md)** - Configure properly
- **[Getting Started](../getting-started/)** - Verify installation

---

**Remember**: Most issues are port-related. If in doubt, check port 3000! 🔌
