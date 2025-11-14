# MCP Server Troubleshooting Guide

## Quick Start

**First, try the automated fix:**
```bash
python scripts/fix_mcp_servers.py
```

**If that doesn't work, follow this guide.**

---

## Problem Categories

### 1. WS Shim Not Running ❌

**Symptoms:**
- `exai-mcp` server fails to connect
- Port 3005 is available (not in use)
- Error: "Failed to connect to MCP server 'exai-mcp'"

**Diagnosis:**
```bash
# Check if WS Shim is running
netstat -tlnp | grep 3005

# Should show: 127.0.0.1:3005 LISTENING
# If nothing, the shim is not running
```

**Fix Steps:**

#### Method 1: Automated Fix
```bash
python scripts/fix_mcp_servers.py
```

#### Method 2: Manual Fix
```bash
# 1. Clean up any orphaned processes
python scripts/runtime/cleanup_orphaned_shims.py

# 2. Start the WS Shim
python scripts/runtime/start_ws_shim_safe.py

# 3. In a separate terminal, verify it's running
netstat -tlnp | grep 3005
```

#### Method 3: Check Logs
```bash
# Check WS Shim logs
tail -f logs/ws-shim.log

# Look for errors like:
# - "Failed to connect to daemon"
# - "Permission denied"
# - "Module not found"
```

**Common Causes:**
1. Python environment not activated (use .venv)
2. Missing dependencies (install with pip)
3. Port 3005 already in use by another process
4. EXAI daemon not running

---

### 2. EXAI Daemon Not Running ❌

**Symptoms:**
- Health check fails
- Error: "Failed to connect to MCP server 'exai-mcp'"
- WS Shim can't connect to daemon

**Diagnosis:**
```bash
# Check daemon status
curl http://127.0.0.1:3002/health
# Expected: {"status": "healthy", ...}

# Check Docker containers
docker-compose ps
```

**Fix Steps:**

#### Method 1: Restart Daemon
```bash
# Restart all services
docker-compose restart

# Check status
docker-compose ps
curl http://127.0.0.1:3002/health
```

#### Method 2: Rebuild and Restart
```bash
# If daemon is broken, rebuild without cache
docker-compose build --no-cache
docker-compose up -d

# Verify
curl http://127.0.0.1:3002/health
```

#### Method 3: Check Daemon Logs
```bash
# View daemon logs
docker-compose logs -f exai-mcp-daemon

# Look for errors:
# - "Port already in use"
# - "Environment variable not set"
# - "Failed to connect to Redis"
```

---

### 3. Filesystem MCP Failing ❌

**Symptoms:**
- Error: "Failed to connect to MCP server 'filesystem-mcp'"
- VS Code shows red icon for filesystem-mcp

**Diagnosis:**
```bash
# Test filesystem-mcp directly
npx -y @modelcontextprotocol/server-filesystem C:/ 2>&1 &
sleep 2
# Should show: "Secure MCP Filesystem Server running on stdio"
```

**Fix Steps:**

#### Method 1: Check npm/npx
```bash
# Verify npm and npx are installed
npm --version
npx --version

# If not installed, install Node.js from nodejs.org
```

#### Method 2: Check Paths in .mcp.json
```bash
# Check .mcp.json configuration
cat .mcp.json

# filesystem-mcp section should look like:
# "filesystem-mcp": {
#   "command": "npx",
#   "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:/", "C:/Users", "C:/Project"]
# }

# Paths must exist and be accessible
```

#### Method 3: Clear npm Cache
```bash
# Clear npm cache
npm cache clean --force

# Reinstall package
npm install -g @modelcontextprotocol/server-filesystem
```

---

### 4. Mermaid MCP Failing ❌

**Symptoms:**
- Error: "Failed to connect to MCP server 'mermaid-mcp'"
- Diagram generation not working

**Diagnosis:**
```bash
# Test mermaid-mcp directly
npx -y @narasimhaponnada/mermaid-mcp-server --help
# Should show help message
```

**Fix Steps:**

#### Method 1: Reinstall Package
```bash
npm install -g @narasimhaponnada/mermaid-mcp-server
```

#### Method 2: Check Version
```bash
# Check if package exists
npm list -g @narasimhaponnada/mermaid-mcp-server

# If not installed, install it
npm install -g @narasimhaponnada/mermaid-mcp-server@latest
```

---

### 5. Provider Errors (listmodels failing) ❌

**Symptoms:**
- `listmodels` tool returns error
- Error: "AttributeError: 'GLMProvider' object has no attribute 'get_model_configurations'"

**Diagnosis:**
```python
# Test in Python
from src.providers.glm_provider import GLMProvider
provider = GLMProvider()
print(hasattr(provider, 'get_model_configurations'))
# Should output: True
```

**Fix Steps:**

#### Method 1: Check Python Path
```bash
# Make sure you're in the right directory
cd C:/Project/EX-AI-MCP-Server

# Run from project root, not from scripts/
cd ..
python -c "from src.providers.glm_provider import GLMProvider; print('OK')"
```

#### Method 2: Check Imports
```bash
# Try importing all provider modules
python -c "
import sys
sys.path.insert(0, '.')
from src.providers import glm_provider
from src.providers import kimi
print('All imports OK')
"
```

---

### 6. Log File Bloat 📁

**Symptoms:**
- Hundreds of `ws_shim_*.log` files
- Running out of disk space
- Slow performance

**Diagnosis:**
```bash
# Count shim log files
find logs/ -name "ws_shim_*.log" | wc -l
# If > 50, cleanup needed
```

**Fix Steps:**

#### Method 1: Manual Cleanup
```bash
# Keep only 10 most recent logs
cd logs/
ls -t ws_shim_*.log | tail -n +11 | xargs rm -f

# Or delete all old logs
find logs/ -name "ws_shim_*.log" -mtime +1 -delete
```

#### Method 2: Automated Cleanup
```bash
# Run cleanup script
python scripts/runtime/cleanup_orphaned_shims.py
```

#### Method 3: Reduce Logging
```bash
# Edit .env file
LOG_LEVEL=WARNING  # instead of INFO or DEBUG
```

---

## Diagnostic Commands

### System Status
```bash
# Check all ports
netstat -tlnp | grep -E "3002|3003|3005|3010"

# Check EXAI health
curl http://127.0.0.1:3002/health

# Check Docker
docker-compose ps

# Check Python environment
C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe --version
```

### MCP Servers
```bash
# List all MCP servers
cat .mcp.json | jq '.mcpServers | keys'

# Test each MCP server
# git-mcp
uvx mcp-server-git --help

# filesystem-mcp
npx -y @modelcontextprotocol/server-filesystem C:/ --help

# mermaid-mcp
npx -y @narasimhaponnada/mermaid-mcp-server --help

# sequential-thinking
npx -y @modelcontextprotocol/server-sequential-thinking --help

# memory-mcp
npx -y @modelcontextprotocol/server-memory --help
```

### Logs
```bash
# Watch all relevant logs
tail -f logs/ws_daemon.log
tail -f logs/ws-shim.log

# Search for errors
grep -i error logs/ws_daemon.log | tail -20
```

---

## Complete Reset Procedure

If everything is broken, do a complete reset:

```bash
# 1. Stop all services
docker-compose down

# 2. Clean up orphaned processes
python scripts/runtime/cleanup_orphaned_shims.py

# 3. Remove old logs
find logs/ -name "ws_shim_*.log" -delete

# 4. Rebuild Docker (without cache)
docker-compose build --no-cache

# 5. Start services
docker-compose up -d

# 6. Wait for daemon to start
sleep 10

# 7. Check health
curl http://127.0.0.1:3002/health

# 8. Start WS Shim
python scripts/fix_mcp_servers.py

# 9. Verify all MCP servers
# Restart Claude Code and check MCP status
```

---

## MCP Server Status Reference

### Working Servers ✅
1. **git-mcp**
   - Command: `uvx mcp-server-git`
   - Status: Working
   - Test: `uvx mcp-server-git --help`

2. **sequential-thinking**
   - Command: `npx -y @modelcontextprotocol/server-sequential-thinking`
   - Status: Working
   - Test: `npx -y @modelcontextprotocol/server-sequential-thinking --help`

3. **memory-mcp**
   - Command: `npx -y @modelcontextprotocol/server-memory`
   - Status: Working
   - Test: `npx -y @modelcontextprotocol/server-memory --help`

### Failing Servers ❌
1. **exai-mcp**
   - Command: `python scripts/runtime/start_ws_shim_safe.py`
   - Status: Not running
   - Fix: Run `python scripts/fix_mcp_servers.py`

2. **filesystem-mcp**
   - Command: `npx -y @modelcontextprotocol/server-filesystem C:/ C:/Users C:/Project`
   - Status: Installed but not connecting
   - Fix: Check npm, reinstall package

3. **mermaid-mcp**
   - Command: `npx -y @narasimhaponnada/mermaid-mcp-server`
   - Status: Installed but not connecting
   - Fix: Reinstall package

---

## When to Restart Services

### Restart Docker Services
```bash
docker-compose restart
```
**Do this when:**
- Daemon health check fails
- Docker logs show errors
- After changing .env file

### Restart WS Shim
```bash
# Kill existing shim
python scripts/runtime/cleanup_orphaned_shims.py

# Start new shim
python scripts/runtime/start_ws_shim_safe.py
```
**Do this when:**
- exai-mcp server fails to connect
- WS Shim logs show errors
- Port 3005 is in use

### Restart Claude Code
**Do this when:**
- MCP servers not appearing
- MCP protocol errors
- After fixing WS Shim issues

---

## Getting Help

### Check Documentation
- `MCP_QA_REPORT.md` - Detailed QA report
- `CLAUDE.md` - Project configuration
- `README.md` - Project overview

### Check Logs
- `logs/ws_daemon.log` - Main daemon logs
- `logs/ws-shim.log` - WS Shim logs
- `logs/ws_shim_*.log` - Individual shim logs

### Common Log Messages

**"Port 3005 is in use"**
- Fix: `python scripts/runtime/cleanup_orphaned_shims.py`

**"Daemon appears healthy"**
- Status: Daemon is OK, problem is with MCP client

**"Failed to connect to daemon"**
- Fix: Check EXAI daemon is running (`docker-compose ps`)

**"Module not found"**
- Fix: Activate virtual environment (`.venv\Scripts\python.exe`)

**"Permission denied"**
- Fix: Run as administrator or check file permissions

---

## Prevention Tips

1. **Regular Cleanup**
   ```bash
   # Run weekly
   python scripts/runtime/cleanup_orphaned_shims.py
   find logs/ -name "ws_shim_*.log" -mtime +7 -delete
   ```

2. **Monitor Disk Space**
   ```bash
   # Check log directory size
   du -sh logs/
   # If > 1GB, cleanup needed
   ```

3. **Check Health Regularly**
   ```bash
   # Daily health check
   curl http://127.0.0.1:3002/health
   docker-compose ps
   ```

4. **Keep Dependencies Updated**
   ```bash
   # Monthly
   npm update -g
   pip install -r config/pyproject.toml --upgrade
   ```

---

## Contact

If you're still having issues after trying all these steps:

1. Check `MCP_QA_REPORT.md` for more details
2. Review logs in `logs/` directory
3. Run diagnostic: `python scripts/diagnose_mcp_servers.py`
4. Create an issue with:
   - Output of diagnostic script
   - Relevant log snippets
   - Steps you've already tried

---

**Last Updated**: 2025-11-13
**Version**: 1.0
