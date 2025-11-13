# EX-AI-MCP-Server - Claude Code Configuration
**Last Updated**: 2025-11-13
**Status**: WebSocket MCP Server Development Platform 🚀
**Version**: 2.3 (Post-Cleanup & Fixes)

---

## ⚠️ CRITICAL: Recent Fixes (2025-11-13)

### **Issues Fixed:**
1. **Stdout Redirection Bug** - Wrapper was logging MCP protocol messages (FIXED)
2. **Timeout Configuration** - Increased from 10s to 30s (FIXED)
3. **Docker Layer Caching** - Rebuild without cache required (FIXED)
4. **ModelCapabilities Class** - Missing parameters added (FIXED)
5. **Environment Path Resolution** - Corrected .env loading (FIXED)
6. **Logging Pollution** - MCP loggers set to ERROR only (FIXED)

### **Rebuild Command (CRITICAL):**
```bash
# From root directory
docker-compose build --no-cache

# Start services
docker-compose up -d

# Verify health
curl http://127.0.0.1:3002/health
```

### **Directory Structure (Cleaned 2025-11-13):**
```
c:\Project\EX-AI-MCP-Server\
├── Dockerfile               ← Docker build file (ROOT)
├── docker-compose.yml       ← Container orchestration (ROOT)
├── config/
│   ├── pyproject.toml       ← Python dependencies
│   ├── pytest.ini          ← Test config
│   └── redis.conf          ← Redis config
├── scripts/                ← All operational scripts
└── docs/                   ← Documentation
    ├── integration/        ← Integration guides
    └── reports/           ← Temporary fix files (moved here)
```

### **Critical Files (DO NOT MODIFY WITHOUT CARE):**
- `scripts/runtime/run_ws_shim.py` - MCP stdio bridge
- `scripts/runtime/start_ws_shim_safe.py` - Wrapper script (FIXED for stdout)
- `src/providers/base.py` - ModelCapabilities class (FIXED)
- `.mcp.json` - MCP client configuration
- `.env` - Local environment variables
- `.env.docker` - Container environment variables

---

## Project Overview

**EX-AI-MCP-Server** is a **WebSocket-based Model Context Protocol (MCP) server** that bridges standard MCP protocol with EX-AI's custom WebSocket protocol. This project serves as the foundation for intelligent AI agent coordination and tool orchestration.

### Core Purpose

This project implements:
- **WebSocket Protocol Translation**: Converts MCP standard to custom EX-AI protocol
- **AI Provider Integration**: GLM, KIMI, and MiniMax API orchestration
- **Session Management**: Multi-user, multi-session coordination
- **Tool Execution Framework**: Distributed tool execution across AI providers
- **Real-time Monitoring**: Performance metrics, health checks, and observability

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Claude Code (MCP Client)                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  WebSocket Shim (Port 3005) - run_ws_shim.py                │
│  • Protocol Translation                                     │
│  • Message Routing                                          │
│  • Session Management                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  EX-AI Daemon (Docker) - Port 3010                           │
│  • Provider Integration (GLM, KIMI, MiniMax)                │
│  • Tool Execution                                           │
│  • Route Management                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────┴───────────┐
         ▼                       ▼
    AI Providers            Tool Ecosystem
    • GLM                   • Analysis Tools
    • KIMI                  • Planning Tools
    • MiniMax               • Routing Intelligence
```

### Port Configuration

| Port | Service | Purpose |
|------|---------|---------|
| 3005 | WebSocket Shim | MCP client connections |
| 3010 | EX-AI Daemon | Internal WebSocket daemon |
| 3001 | Monitoring Dashboard | Web UI for system status |
| 3002 | Health Check | HTTP health endpoint |
| 3003 | Prometheus Metrics | Metrics collection |

---

## 🛠️ Available MCP Tools

### Current Status ⚠️
- ✅ **git-mcp** - Connected (uvx version)
- ✅ **sequential-thinking** - Connected
- ✅ **memory-mcp** - Connected
- ❌ **exai-mcp** - Failed (check if daemon is running)
- ❌ **filesystem-mcp** - Failed (check npx dependencies)
- ❌ **mermaid-mcp** - Failed (check package installation)

### Tool Details

#### 1. exai-mcp (⚠️ Requires Daemon)
**Purpose**: The core WebSocket MCP server
**Command**: Python WebSocket shim
**Configuration**:
- Port: 3010 (daemon) / 3005 (shim)
- Environment: Full GLM, KIMI, MiniMax config
- Token: Configured for authentication

**Troubleshooting**:
- Check if Docker daemon is running: `docker ps | grep exai-mcp-server`
- Verify port 3010 is open: `curl http://127.0.0.1:3002/health`
- Check .venv activation: Ensure `C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe` exists

#### 2. git-mcp (✅ Working)
**Purpose**: Version control operations
**Command**: uvx mcp-server-git
**Usage**: Standard git operations through MCP protocol

#### 3. sequential-thinking (✅ Working)
**Purpose**: Deep analysis and problem-solving
**Command**: npx @modelcontextprotocol/server-sequential-thinking
**Usage**: Complex reasoning, multi-step analysis

#### 4. memory-mcp (✅ Working)
**Purpose**: Knowledge graph and persistent memory
**Command**: npx @modelcontextprotocol/server-memory
**Usage**: Store and retrieve contextual information

#### 5. filesystem-mcp (❌ Check Required)
**Purpose**: File system access
**Command**: npx @modelcontextprotocol/server-filesystem
**Paths**: /c, /c/Users, /c/Project, /c/Project/EX-AI-MCP-Server, etc.

**Troubleshooting**:
- Install package: `npx -y @modelcontextprotocol/server-filesystem`
- Check npm: `npm --version`
- Verify npx: `npx --version`

#### 6. mermaid-mcp (❌ Check Required)
**Purpose**: Generate architecture diagrams
**Command**: npx @narasimhaponnada/mermaid-mcp-server
**Usage**: Visualize flows, architecture, system diagrams

**Troubleshooting**:
- Package detected: mermaid-mcp 1.0.2 ✅
- Test directly: `npx -y @narasimhaponnada/mermaid-mcp-server`

---

## 🎯 Agent Responsibilities in EX-AI-MCP-Server

### Primary Tasks

#### 1. **WebSocket Protocol Development**
- Debug protocol translation issues
- Optimize message routing performance
- Implement new MCP features
- Fix connection stability issues

#### 2. **AI Provider Integration**
- Integrate new AI providers (GLM, KIMI, MiniMax)
- Optimize routing algorithms
- Implement load balancing
- Manage API key rotation

#### 3. **Tool Execution Framework**
- Develop new tool execution engines
- Implement timeout and retry logic
- Create monitoring and alerting
- Optimize execution performance

#### 4. **Session & State Management**
- Multi-user session coordination
- State persistence and recovery
- Memory leak detection
- Resource cleanup

#### 5. **Monitoring & Observability**
- Real-time performance metrics
- Health check endpoints
- Prometheus integration
- Dashboard development

### Development Workflow

#### Daily Tasks
1. **Check System Health**
   ```bash
   curl http://127.0.0.1:3002/health
   docker ps | grep exai-mcp-server
   ```

2. **Monitor Metrics**
   ```bash
   curl http://127.0.0.1:3003/metrics
   ```

3. **Review Logs**
   ```bash
   tail -f C:/Project/EX-AI-MCP-Server/logs/
   ```

4. **Test MCP Connections**
   - Verify all MCP tools are connected
   - Test protocol translation
   - Check message routing

#### When Debugging Issues

1. **MCP Connection Failures**
   - Check if daemon is running: `docker ps`
   - Verify port availability: `netstat -tlnp | grep 3010`
   - Check Python venv: `C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe --version`
   - Review logs: `tail -f logs/exai-mcp.log`

2. **WebSocket Errors**
   - Monitor Shim logs: `tail -f logs/ws-shim.log`
   - Check protocol translation
   - Verify client connections
   - Test message routing

3. **Provider Integration Issues**
   - Check API keys: `grep API_KEY .env`
   - Test provider connectivity
   - Monitor rate limits
   - Review routing decisions

#### Code Development

1. **Core Changes**
   - `src/core/` - Protocol implementation
   - `src/daemon/` - WebSocket daemon
   - `src/providers/` - AI provider integrations
   - `src/orchestrator/` - Route management

2. **Testing**
   - Unit tests: `pytest tests/`
   - Integration: `python scripts/test_*.py`
   - MCP validation: `python scripts/validate_mcp_connection.py`

3. **Deployment**
   - Docker build: `docker-compose build`
   - Service restart: `docker-compose restart exai-mcp-daemon`
   - Health verification: `curl http://127.0.0.1:3002/health`

---

## 🔧 Common Operations

### Starting the System
```bash
# Start EX-AI-MCP-Server
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d exai-mcp-daemon

# Verify startup
docker-compose ps
curl http://127.0.0.1:3002/health
```

### Checking MCP Status
```bash
# All services
docker-compose ps

# Logs
docker-compose logs -f exai-mcp-daemon
docker-compose logs -f ws-shim

# Health
curl http://127.0.0.1:3002/health
```

### Testing Protocol
```bash
# Test WebSocket connection
python scripts/ws/ws_chat_once.py

# Test MCP protocol
python scripts/validate_mcp_connection.py

# Full test suite
python scripts/run_all_tests.py
```

### Debugging Tools
```bash
# MCP validation
python scripts/validation/validate_mcp_configs.py

# Port availability
python scripts/check_port.py --port 3010

# Environment validation
python scripts/validate_environment.py
```

---

## 📊 Monitoring & Metrics

### Health Endpoints
- **Port 3002**: HTTP health check - `GET /health`
- **Port 3003**: Prometheus metrics - `GET /metrics`
- **Port 3001**: Monitoring dashboard - Web UI

### Key Metrics
- Active WebSocket connections
- Message throughput
- Provider response times
- Error rates by provider
- Session count
- Tool execution latency

### Log Locations
```
logs/
├── exai-mcp-daemon.log     # Main daemon logs
├── ws-shim.log            # WebSocket shim logs
├── provider-routing.log   # Provider routing decisions
├── tool-execution.log     # Tool execution results
├── session-management.log # Session lifecycle
└── monitoring/            # Monitoring system logs
```

---

## 🚨 Troubleshooting Guide

### Issue: exai-mcp Failed to Connect

**Diagnosis**:
1. Check daemon: `docker ps | grep exai-mcp-server`
2. Check port: `netstat -tlnp | grep 3010`
3. Check health: `curl http://127.0.0.1:3002/health`

**Solutions**:
1. Start daemon: `docker-compose up -d exai-mcp-daemon`
2. Restart if stuck: `docker-compose restart`
3. Check logs: `docker-compose logs exai-mcp-daemon`

### Issue: npx MCP Servers Failing

**Diagnosis**:
1. Check npm: `npm --version`
2. Check npx: `npx --version`
3. Test package: `npx -y @modelcontextprotocol/server-filesystem --help`

**Solutions**:
1. Install npm: Install Node.js from nodejs.org
2. Clear cache: `npm cache clean --force`
3. Reinstall packages: `npm install -g @modelcontextprotocol/server-filesystem @narasimhaponnada/mermaid-mcp-server`

### Issue: Protocol Translation Errors

**Diagnosis**:
1. Check shim logs: `tail -f logs/ws-shim.log`
2. Monitor messages: Enable debug logging
3. Test routing: Use test scripts

**Solutions**:
1. Restart shim: Restart Claude Code session
2. Clear state: Delete session files
3. Debug mode: Set `LOG_LEVEL=DEBUG` in .env

---

## 📁 Project Structure

```
EX-AI-MCP-Server/
├── src/                    # Source code
│   ├── core/              # Protocol core
│   ├── daemon/            # WebSocket daemon
│   ├── providers/         # AI provider integrations
│   ├── orchestrator/      # Route management
│   ├── auth/              # Authentication
│   ├── monitoring/        # Metrics & health
│   └── prompts/           # System prompts
├── scripts/               # Operational scripts
│   ├── runtime/           # Runtime management
│   ├── validation/        # MCP validation
│   ├── testing/           # Test suite
│   └── monitoring/        # Monitoring tools
├── logs/                  # Application logs
├── docs/                  # Documentation
├── docker-compose.yml     # Service orchestration
├── .env                   # Environment config
├── .mcp.json             # MCP server config (6 servers)
└── CLAUDE.md             # This file
```

---

## 🔑 Key Configuration

### Environment Variables (.env)
```bash
# Core
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3010
SHIM_LISTEN_PORT=3005

# AI Providers
GLM_API_KEY=...
GLM_API_URL=https://api.z.ai/api/paas/v4
KIMI_API_KEY=...
KIMI_API_URL=https://api.moonshot.ai/v1
MINIMAX_M2_KEY=...
MINIMAX_API_URL=https://api.minimax.io/anthropic

# Timeouts
SIMPLE_TOOL_TIMEOUT_SECS=30
WORKFLOW_TOOL_TIMEOUT_SECS=46
EXPERT_ANALYSIS_TIMEOUT_SECS=60
```

### MCP Configuration (.mcp.json)
```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "scripts/runtime/run_ws_shim.py"],
      "env": {
        "EXAI_WS_PORT": "3010",
        "SHIM_LISTEN_PORT": "3005",
        "EXAI_WS_TOKEN": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo",
        ...
      }
    },
    "filesystem-mcp": { ... },
    "git-mcp": { ... },
    "sequential-thinking": { ... },
    "memory-mcp": { ... },
    "mermaid-mcp": { ... }
  }
}
```

**Note**: Currently 3 MCPs connected, 3 MCPs failing. See "Current Issues" below.

---

## 🎓 Learning Resources

### Understanding WebSocket Protocol
1. Review `src/core/websocket_protocol.py`
2. Study message format in `docs/protocol/`
3. Test with `scripts/ws/ws_chat_once.py`

### MCP Protocol Deep Dive
1. Read MCP specification: `docs/mcp/`
2. Study protocol translation: `src/core/mcp_translator.py`
3. Practice with test scripts: `scripts/test_mcp_*.py`

### Provider Integration
1. Review GLM integration: `src/providers/glm.py`
2. Study routing logic: `src/orchestrator/route_manager.py`
3. Analyze routing decisions: `logs/provider-routing.log`

---

## 💡 Best Practices

### Code Development
- **Use sequential-thinking** for complex debugging
- **Log all routing decisions** for provider integration
- **Test with memory-mcp** to track system evolution
- **Document with mermaid-mcp** for architecture changes

### MCP Server Development
- **Always validate MCP connections** before deployment
- **Test protocol translation** with sample messages
- **Monitor WebSocket shim** for connection issues
- **Check provider timeouts** regularly

### System Operations
- **Start with health check**: `curl http://127.0.0.1:3002/health`
- **Monitor metrics**: Prometheus at port 3003
- **Review logs daily**: Check for warnings/errors
- **Track session count**: Monitor resource usage

---

## 🚀 Quick Start for New Agents

1. **Check System Status**
   ```bash
   curl http://127.0.0.1:3002/health
   docker-compose ps
   ```

2. **Verify MCP Connections**
   - Use Claude Code tools list
   - Check connection status
   - Test failed MCPs individually

3. **Review Recent Logs**
   ```bash
   tail -50 logs/exai-mcp-daemon.log
   tail -50 logs/ws-shim.log
   ```

4. **Understand Current Tasks**
   - Read active issues in `docs/`
   - Check development roadmap
   - Review open PRs

5. **Start Development**
   - Use working MCPs (git, sequential-thinking, memory)
   - Debug failed MCPs (exai-mcp, filesystem, mermaid)
   - Follow troubleshooting guide

---

## 🔍 Current Issues to Address

### High Priority - MCP Connection Failures
1. **exai-mcp Connection Failure**
   - Daemon not responding on port 3010
   - Check Docker container status
   - Verify environment variables
   - Review: `docker-compose logs exai-mcp-daemon`

2. **filesystem-mcp Installation**
   - npx package not found or misconfigured
   - May need global installation
   - Check: `npx -y @modelcontextprotocol/server-filesystem`
   - Verify: `npm --version && npx --version`

3. **mermaid-mcp Server**
   - Package detected (1.0.2) but server fails
   - Check for missing dependencies
   - Test: `npx -y @narasimhaponnada/mermaid-mcp-server`

### Medium Priority
- Review port configuration conflicts
- Optimize timeout settings
- Improve error messages
- Add retry logic for failed connections

### Working MCPs (Use These!)
- ✅ **git-mcp** - Version control (uvx mcp-server-git)
- ✅ **sequential-thinking** - Deep analysis (npx)
- ✅ **memory-mcp** - Knowledge graph (npx)

### Failed MCPs (Debug These!)
- ❌ **exai-mcp** - WebSocket MCP server (Python)
- ❌ **filesystem-mcp** - File system access (npx)
- ❌ **mermaid-mcp** - Diagrams (npx)

---

## 🛠️ Testing & Validation Scripts

### Available Scripts
```bash
# MCP Connection Validation
python scripts/validate_mcp_connection.py

# Port Availability Check
python scripts/check_port.py --port 3010

# Environment Validation
python scripts/validate_environment.py

# WebSocket Testing
python scripts/ws/ws_chat_once.py

# Full Test Suite
python scripts/run_all_tests.py
```

### Quick Diagnostics
```bash
# Check all required ports
for port in 3002 3003 3005 3010; do
  echo "Checking port $port..."
  timeout 1 bash -c "</dev/tcp/127.0.0.1/$port" && echo "✓ Port $port open" || echo "✗ Port $port closed"
done

# Check Docker containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check npm/npx
npm --version && npx --version
```

---

**Remember**: This is a **WebSocket MCP server** - you're working with protocol translation, not just a regular project. Focus on understanding the bridge between standard MCP and EX-AI's custom protocol! 🚀

**Current Status**: 3/6 MCPs connected
- Working: git-mcp, sequential-thinking, memory-mcp
- Failing: exai-mcp, filesystem-mcp, mermaid-mcp

---

## 🧹 Process Cleanup System

### Overview
The system includes an **automated process cleanup system** to prevent bloat from Claude Code shell snapshots and orphaned processes.

### Location
**Scripts**: `C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup\`

### Quick Cleanup
```powershell
cd C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup
.\cleanup_all_fixed.ps1
```

### Automated Cleanup
1. **Docker Service**: Runs every 30 minutes (kills processes >2h old)
   ```bash
   docker-compose up -d cleanup-service
   ```

2. **Task Scheduler**: Daily at 2:00 AM
   - Run: `auto_cleanup.bat`
   - Configuration in `scripts/windows-cleanup/`

### What Gets Cleaned
- **Processes**: bash.exe, cmd.exe, node.exe, python.exe (>2 hours old)
- **Shell Snapshots**: Claude Code snapshots in `~/.claude/shell-snapshots/` (>7 days old)

### Documentation
- `scripts/windows-cleanup/README.md` - Quick start
- `scripts/windows-cleanup/CLEANUP_DOCUMENTATION.md` - Technical details
- `PROCESS_CLEANUP_SUMMARY.md` - Complete summary

**Status**: ✅ **System Optimized**
- Stale processes: 0
- Active processes: 80 (healthy)
- Automated cleanup: Enabled

**Last Updated**: 2025-11-12
**Version**: 7.1.0 (Process Cleanup System Added)

---

## 🚀 Quick Start for New Agents (2025-11-13 Update)

### **First Steps:**
1. **Read this entire file** - Understand the project architecture
2. **Check daemon health:** `curl http://127.0.0.1:3002/health`
3. **Review integration guide:** `docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md`
4. **Check for recent fixes:** `docs/integration/` (Lessons Learned section)

### **Development Workflow:**

#### **Daily Checks:**
```bash
# 1. Verify all services are running
docker-compose ps

# 2. Check daemon health
curl http://127.0.0.1:3002/health

# 3. Review recent logs
tail -50 logs/ws_daemon.log
tail -50 logs/ws-shim.log

# 4. Test MCP connection
python scripts/test_mcp_connection.py
```

#### **After Code Changes:**
```bash
# CRITICAL: Rebuild without cache (Docker caches old code!)
docker-compose build --no-cache

# Restart services
docker-compose restart

# Verify everything works
curl http://127.0.0.1:3002/health
```

#### **Common Issues & Solutions:**

**Issue:** "exai-mcp failed to connect"
**Solution:**
- Daemon not running: `docker-compose up -d`
- Port conflict: `docker-compose restart`
- Old code in container: `docker-compose build --no-cache`

**Issue:** Docker build fails
**Solution:**
- Check Dockerfile uses correct path (should be `COPY config/pyproject.toml .`)
- Verify dependencies in `config/pyproject.toml`
- Clean build: `docker system prune -f && docker-compose build --no-cache`

**Issue:** MCP protocol messages not received
**Solution:**
- Check `scripts/runtime/start_ws_shim_safe.py` for stdout redirection bug
- Verify stderr logging, stdout pass-through
- No logging in MCP protocol messages!

### **Key Files to Know:**

#### **Core Components:**
- `src/daemon/ws_server.py` - WebSocket server implementation
- `scripts/runtime/run_ws_shim.py` - MCP stdio bridge (DO NOT LOG STDOUT!)
- `scripts/runtime/start_ws_shim_safe.py` - Safe startup wrapper
- `src/providers/base.py` - Model capabilities (FIXED 2025-11-13)

#### **Configuration:**
- `docker-compose.yml` - Container orchestration (ROOT level)
- `Dockerfile` - Container build (ROOT level)
- `config/pyproject.toml` - Dependencies
- `.mcp.json` - MCP client config
- `.env` - Local environment
- `.env.docker` - Container environment

#### **Monitoring:**
- Health: `http://127.0.0.1:3002/health`
- Metrics: `http://127.0.0.1:3003/metrics`
- Logs: `logs/ws_daemon.log`, `logs/ws-shim.log`

### **Testing:**
```bash
# MCP protocol test
python scripts/test_mcp_connection.py

# Port availability
python scripts/check_port.py --port 3010

# Environment validation
python scripts/validate_environment.py

# WebSocket chat test
python scripts/ws/ws_chat_once.py
```

### **Best Practices:**

1. **Always rebuild Docker without cache** after code changes
2. **Never log to stdout** - MCP clients expect clean JSON
3. **All logs go to stderr** - Keep protocol streams clean
4. **Test with real MCP clients** - Don't rely on unit tests
5. **Document any changes** in docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md
6. **Update this file** when adding new workflows or fixing issues

### **For Debugging:**
```bash
# Watch daemon logs in real-time
docker-compose logs -f exai-daemon

# Watch shim logs
tail -f logs/ws-shim.log

# Watch all logs
tail -f logs/ws_daemon.log

# Check MCP connection in detail
python scripts/test_mcp_connection.py 2>&1 | tee debug.log
```

### **File Locations:**

#### **Root (Essential files only):**
- `README.md` - Project overview
- `CLAUDE.md` - This file
- `CHANGELOG.md` - Version history
- `CONTRIBUTING.md` - Contribution guidelines
- `Dockerfile` - Container build
- `docker-compose.yml` - Container orchestration

#### **Documentation:**
- `docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md` - Integration guide
- `docs/reports/` - Temporary fix documentation (moved 2025-11-13)

#### **Source:**
- `src/` - Core source code
- `tools/` - Tool implementations
- `scripts/` - Operational scripts
- `config/` - Dependencies and configs

**Remember:** This is a production MCP server. Changes affect live integrations. Always test thoroughly and rebuild containers when code changes!
