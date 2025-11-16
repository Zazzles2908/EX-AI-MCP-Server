# EX-AI MCP Server - Agent Configuration Guide

|**Last Updated**: 2025-11-14  
|**Status**: Production-Ready Native MCP Server with AI Capabilities 🚀  
|**Version**: 6.1.0 (Mini-Max M2 Routing)  
|**Architecture**: Native MCP with Smart AI Provider Routing

---

## 🚨 MANDATORY: Read This First (Agents & Developers)

**Before proceeding with ANY task, you MUST read these 4 documents in order:**

1. **[CLAUDE.md](CLAUDE.md)** ← You are here - Project overview and agent guidance
2. **[README.md](README.md)** ← Project overview and quick start  
3. **[CHANGELOG.md](CHANGELOG.md)** ← Version history and recent fixes
4. **[docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md](docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md)** ← Integration guide

⚠️ **DO NOT proceed with any work until you've read all 4 documents above**

---

## 📚 Documentation Quick Links

### **For Agents (Read First!)**
- **[README.md](README.md)** - Project overview and Mini-Agent optimization
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and critical fixes  
- **[docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md](docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md)** - Integration guide
- **[docs/architecture/](docs/architecture/)** - System architecture & design patterns

### **For Developers**
- **[src/](src/)** - Core system source code
- **[tools/](tools/)** - MCP tool implementations  
- **[scripts/](scripts/)** - Operational scripts and utilities
- **[config/](config/)** - Configuration files and dependencies

### **For Operations** 
- **[scripts/runtime/](scripts/runtime/)** - Service management scripts
- **[logs/](logs/)** - Application and system logs
- **[docs/troubleshooting/](docs/troubleshooting/)** - Debugging and diagnostics

---

## 🎯 Project Overview

**EX-AI MCP Server** is a **production-ready Model Context Protocol (MCP) server** that provides intelligent AI agent coordination through smart provider routing. This system serves as the foundation for advanced AI agent operations with multiple provider integration and native MCP protocol support.

### Core Purpose

This project implements:
- **Native MCP Server**: Direct MCP protocol support over STDIO
- **Smart AI Provider Routing**: Mini-Max M2, GLM, and Kimi API orchestration  
- **Advanced Tool Suite**: 20+ AI-powered tools for analysis, debugging, and automation
- **Session Management**: Multi-user, multi-session coordination
- **Real-time Monitoring**: Performance metrics, health checks, and observability

### Current System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  EX-AI MCP Client                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ (Native MCP over STDIO)
┌─────────────────────────────────────────────────────────────┐
│  EX-AI MCP Server (Native)                                  │
│  • Direct MCP protocol (no translation)                     │
│  • Smart Provider Routing (Mini-Max M2 → GLM → Kimi)       │
│  • 20+ AI-Powered Tools                                     │
│  • Advanced Session Management                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────┴───────────┐
         ▼                       ▼
    AI Providers            Tool Ecosystem
    • Mini-Max M2           • Analysis Tools  
    • GLM (web search)      • Planning Tools
    • Kimi (thinking)       • Routing Intelligence
    • OpenRouter            • Code Review Tools
```

### Port Configuration

| Port | Service | Purpose |
|------|---------|---------|
| STDIO | Native MCP | Direct MCP protocol (no port needed) |
| 3001 | Monitoring Dashboard | Web UI for system status |
| 3002 | Health Check | HTTP health endpoint |
| 3003 | Prometheus Metrics | Metrics collection |

---

## 🛠️ Available MCP Tools

### Current Status ✅
- ✅ **exai-mcp** - Native MCP Server (20+ tools, Version 6.1.0)
- ✅ **git-mcp** - Version control operations (uvx)
- ✅ **sequential-thinking** - Deep analysis (npx)  
- ✅ **memory-mcp** - Knowledge graph (npx)
- ❌ **filesystem-mcp** - Failed (check npx dependencies)
- ❌ **mermaid-mcp** - Failed (check package installation)

### Tool Details

#### 1. exai-mcp (✅ Native MCP Server - Version 6.1.0+)
**Purpose**: Native MCP server with smart provider routing and 20+ AI tools
**Command**: Docker exec with native MCP protocol
**Configuration**:
- Mode: Native MCP over STDIO (no protocol translation)
- Container: exai-mcp-stdio
- Command: `docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio`
- Environment: Full Mini-Max M2, GLM, Kimi config

**Available AI Tools**:
- **Chat & Communication**: `chat`, `kimi_chat_with_tools`, `smart_file_query`
- **Analysis & Research**: `analyze`, `thinkdeep`, `tracer`
- **Code Operations**: `codereview`, `debug`, `refactor`, `testgen`
- **System Operations**: `status`, `version`, `listmodels`, `planner`
- **Security & Compliance**: `secaudit`, `precommit`
- **Documentation**: `docgen`, `consensus`

**Troubleshooting**:
- Check if Docker daemon is running: `docker ps | grep exai-mcp-stdio`
- Start native MCP server: `docker-compose up -d exai-mcp-stdio`
- Verify health: `curl http://127.0.0.1:3002/health`
- Test native MCP: `echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio`

**Changes in v6.1.0**:
- ✅ Smart routing with Mini-Max M2 (AI-powered decisions)
- ✅ 20+ AI tools fully operational
- ✅ Provider priority: Mini-Max M2 → GLM → Kimi → Fallback
- ✅ Native stdio with docker exec
- ✅ 90% code reduction (2,500→259 lines) through smart routing

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

#### 6. mermaid-mcp (❌ Check Required)
**Purpose**: Generate architecture diagrams
**Command**: npx @narasimhaponnada/mermaid-mcp-server
**Usage**: Visualize flows, architecture, system diagrams

---

## 🎯 Agent Responsibilities in EX-AI MCP Server

### Primary Tasks

#### 1. **AI Provider Integration & Routing**
- Optimize Mini-Max M2 smart routing algorithms
- Monitor provider performance and fallback chains
- Manage API key rotation and rate limiting
- Implement intelligent load balancing

#### 2. **Native MCP Server Operations**
- Maintain direct MCP protocol support (no translation layer)
- Optimize tool execution performance
- Handle concurrent session management
- Monitor tool execution latency

#### 3. **Advanced Tool Development**
- Develop new AI-powered tools for agent workflows
- Implement timeout and retry logic for tools
- Create comprehensive tool testing frameworks
- Optimize tool response quality

#### 4. **System Architecture & Performance**
- Multi-user session coordination
- State persistence and recovery
- Memory leak detection and resource cleanup
- Real-time performance monitoring

#### 5. **Monitoring & Observability**
- Health check endpoints and alerting
- Prometheus metrics integration
- Tool execution analytics
- Provider routing decision logs

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

3. **Review Provider Routing**
   ```bash
   tail -f logs/provider-routing.log
   ```

4. **Test AI Tools**
   - Verify MCP tools are connected
   - Test native MCP protocol
   - Validate tool execution quality

#### When Debugging Issues

1. **MCP Connection Failures**
   - Check if daemon is running: `docker ps`
   - Verify port availability: `netstat -tlnp | grep 3001-3003`
   - Check Python environment: `python --version`
   - Review logs: `tail -f logs/exai-mcp.log`

2. **Provider Routing Issues**
   - Check API keys: `grep API_KEY .env`
   - Test provider connectivity
   - Monitor routing decisions: `tail -f logs/provider-routing.log`
   - Verify Mini-Max M2 routing: Check logs for "Smart Router initialized"

3. **Tool Execution Problems**
   - Monitor tool execution logs: `tail -f logs/tool-execution.log`
   - Check session management: `tail -f logs/session-management.log`
   - Verify timeout configurations
   - Test individual tools with minimal parameters

#### Code Development

1. **Core Components**
   - `src/daemon/ws_server.py` - Native MCP server implementation
   - `src/providers/` - AI provider integrations and routing
   - `src/orchestrator/` - Smart routing logic
   - `tools/` - MCP tool implementations

2. **Testing**
   - Native MCP validation: `python scripts/validate_mcp_connection.py`
   - Provider routing tests: `python scripts/test_provider_routing.py`
   - Tool execution tests: `python scripts/test_tools.py`

3. **Deployment**
   - Docker build: `docker-compose build --no-cache`
   - Service restart: `docker-compose restart exai-mcp-stdio`
   - Health verification: `curl http://127.0.0.1:3002/health`

---

## 🔧 Common Operations

### Starting the System
```bash
# Start native MCP server (RECOMMENDED - v6.1.0+)
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d exai-mcp-stdio

# Start full stack (server + monitoring + redis)
docker-compose up -d

# Verify startup
docker-compose ps
curl http://127.0.0.1:3002/health
```

### Native MCP Server Commands (v6.1.0+)
```bash
# Start native MCP server
docker-compose up -d exai-mcp-stdio

# Test native MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | \
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio

# List tools via native MCP
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | \
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio

# Check MCP server logs
docker-compose logs -f exai-mcp-stdio
```

### Checking System Status
```bash
# All services
docker-compose ps

# Logs (native MCP server)
docker-compose logs -f exai-mcp-stdio

# Health check
curl http://127.0.0.1:3002/health

# Metrics
curl http://127.0.0.1:3003/metrics
```

### Testing AI Tools
```bash
# Test chat functionality
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"chat","arguments":{"prompt":"Hello, test connection"}}}' | \
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio

# Test analysis tools
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"thinkdeep","arguments":{"step":"Test system status","step_number":1,"total_steps":1,"next_step_required":false}}}' | \
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio
```

### Debugging Tools
```bash
# MCP validation
python scripts/validation/validate_mcp_configs.py

# Provider routing test
python scripts/test_provider_routing.py

# Environment validation
python scripts/validate_environment.py

# Tool execution test
python scripts/test_tools.py
```

---

## 📊 Monitoring & Metrics

### Health Endpoints
- **Port 3002**: HTTP health check - `GET /health`
- **Port 3003**: Prometheus metrics - `GET /metrics`  
- **Port 3001**: Monitoring dashboard - Web UI

### Key Metrics
- Active MCP connections
- Tool execution throughput
- Provider response times and success rates
- Mini-Max M2 routing decisions
- Session count and memory usage
- Tool execution latency per provider

### Log Locations
```
logs/
├── exai-mcp.log          # Main MCP server logs
├── provider-routing.log  # Smart routing decisions  
├── tool-execution.log    # Tool execution results
├── session-management.log # Session lifecycle
└── monitoring/           # Monitoring system logs
```

---

## 🚨 Troubleshooting Guide

### Issue: exai-mcp Failed to Connect

**Diagnosis**:
1. Check daemon: `docker ps | grep exai-mcp-stdio`
2. Check ports: `netstat -tlnp | grep 3001-3003`
3. Check health: `curl http://127.0.0.1:3002/health`

**Solutions**:
1. Start daemon: `docker-compose up -d exai-mcp-stdio`
2. Rebuild if stuck: `docker-compose build --no-cache && docker-compose restart`
3. Check logs: `docker-compose logs exai-mcp-stdio`

### Issue: AI Tools Not Responding

**Diagnosis**:
1. Check provider routing: `tail -f logs/provider-routing.log`
2. Verify API keys: `grep -E "(MINIMAX|GLM|KIMI)_API_KEY" .env`
3. Test Mini-Max M2: Look for "Smart Router initialized" in logs

**Solutions**:
1. Restart with fresh routing: `docker-compose restart exai-mcp-stdio`
2. Check API connectivity: Use test scripts in `scripts/`
3. Verify environment: `python scripts/validate_environment.py`

### Issue: Tool Execution Timeouts

**Diagnosis**:
1. Check timeout logs: `tail -f logs/tool-execution.log`
2. Monitor provider response: `tail -f logs/provider-routing.log`
3. Verify session state: Check session-management logs

**Solutions**:
1. Increase timeout in .env.docker: `WORKFLOW_TOOL_TIMEOUT_SECS=60`
2. Check provider health: Use provider test scripts
3. Restart container: `docker-compose restart exai-mcp-stdio`

### Issue: Provider Routing Failures

**Diagnosis**:
1. Check Mini-Max M2: `grep "MiniMax M2" logs/provider-routing.log`
2. Test fallback chain: Verify GLM and Kimi connectivity
3. Monitor routing decisions: Check "Routing to provider" entries

**Solutions**:
1. Verify anthropic package: `docker exec exai-mcp-stdio python -c "import anthropic; print('OK')"`
2. Check API keys: Ensure all providers have valid keys
3. Manual provider test: Use provider-specific test scripts

---

## 📁 Project Structure

```
EX-AI-MCP-Server/
├── src/                    # Core source code
│   ├── daemon/            # Native MCP server
│   ├── providers/         # AI provider integrations
│   ├── orchestrator/      # Smart routing logic
│   └── prompts/           # System prompts
├── tools/                 # MCP tool implementations (20+ tools)
├── scripts/               # Operational scripts
│   ├── runtime/           # Service management
│   ├── validation/        # MCP validation
│   └── testing/           # Test suite
├── agent-workspace/       # Mini-Agent skills (optional)
├── logs/                  # Application logs
├── docs/                  # Documentation
├── docker-compose.yml     # Service orchestration
├── .env                   # Environment config
├── .mcp.json             # MCP server config
├── README.md             # Project overview
├── CLAUDE.md             # This file
└── CHANGELOG.md          # Version history
```

---

## 🔑 Key Configuration

### Environment Variables (.env)
```bash
# Core
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3010

# AI Providers (Smart Routing Priority)
MINIMAX_M2_KEY=...          # Primary (AI-powered routing)
MINIMAX_API_URL=https://api.minimax.io/anthropic
GLM_API_KEY=...            # Secondary (web search)
GLM_API_URL=https://api.z.ai/api/paas/v4
KIMI_API_KEY=...           # Tertiary (thinking mode)
KIMI_API_URL=https://api.moonshot.ai/v1

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
      "command": "docker",
      "args": [
        "exec",
        "-i", 
        "exai-mcp-stdio",
        "python",
        "-m",
        "src.daemon.ws_server",
        "--mode",
        "stdio"
      ],
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env.docker",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8"
      }
    },
    "git-mcp": { "command": "uvx", "args": ["mcp-server-git"] },
    "sequential-thinking": { "command": "npx", "args": ["@modelcontextprotocol/server-sequential-thinking"] },
    "memory-mcp": { "command": "npx", "args": ["@modelcontextprotocol/server-memory"] },
    "filesystem-mcp": { "command": "npx", "args": ["@modelcontextprotocol/server-filesystem"] },
    "mermaid-mcp": { "command": "npx", "args": ["@narasimhaponnada/mermaid-mcp-server"] }
  }
}
```

---

## 🎓 Learning Resources

### Understanding Smart Provider Routing
1. Review `src/providers/` - AI provider integration
2. Study routing logic: `src/orchestrator/route_manager.py`  
3. Analyze routing decisions: `logs/provider-routing.log`

### MCP Protocol Deep Dive
1. Read MCP specification: `docs/mcp/`
2. Study native implementation: `src/daemon/ws_server.py`
3. Practice with test scripts: `scripts/test_mcp_*.py`

### AI Tool Development
1. Review tool implementations: `tools/`
2. Study tool registry: `src/daemon/tool_registry.py`
3. Test tool execution: `scripts/test_tools.py`

---

## 💡 Best Practices

### Code Development
- **Use thinkdeep** for complex debugging and architectural decisions
- **Log all routing decisions** for provider integration debugging
- **Test with memory-mcp** to track system evolution
- **Document with mermaid-mcp** for architecture changes

### MCP Server Development
- **Always validate MCP connections** before deployment
- **Test protocol handling** with sample messages
- **Monitor tool execution** for performance issues
- **Check provider timeouts** and routing decisions regularly

### System Operations
- **Start with health check**: `curl http://127.0.0.1:3002/health`
- **Monitor metrics**: Prometheus at port 3003
- **Review logs daily**: Check for warnings/errors in routing decisions
- **Track provider usage**: Monitor Mini-Max M2 vs fallback usage

### AI Tool Usage
- **Configure thinking modes**: Use `thinking_mode: 'max'` for complex analysis
- **Set assistant model**: Always use `use_assistant_model: True` for AI tools
- **Provide context**: Include relevant files and background information
- **Test tool parameters**: Experiment with temperature and other parameters

---

## 🚀 Quick Start for New Agents

### **First Steps:**
1. **Read this entire file** - Understand the project architecture and AI capabilities
2. **Check daemon health:** `curl http://127.0.0.1:3002/health`
3. **Review integration guide:** `docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md`
4. **Check for recent fixes:** `CHANGELOG.md` for version 6.1.0 improvements

### **Development Workflow:**

#### **Daily Checks:**
```bash
# 1. Verify all services are running
docker-compose ps

# 2. Check daemon health  
curl http://127.0.0.1:3002/health

# 3. Review provider routing logs
tail -20 logs/provider-routing.log

# 4. Test MCP connection
python scripts/validate_mcp_connection.py
```

#### **Testing AI Capabilities:**
```bash
# Test Mini-Max M2 routing
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"thinkdeep","arguments":{"step":"Test AI capabilities","step_number":1,"total_steps":1,"next_step_required":false,"use_assistant_model":true,"thinking_mode":"max"}}}' | \
docker exec -i exai-mcp-stdio python -m src.daemon.ws_server --mode stdio
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
- Daemon not running: `docker-compose up -d exai-mcp-stdio`
- Port conflict: `docker-compose restart`  
- Old code in container: `docker-compose build --no-cache`

**Issue:** AI tools not responding
**Solution:**
- Check Mini-Max M2 routing: `tail -f logs/provider-routing.log`
- Verify API keys: `grep API_KEY .env.docker`
- Test provider connectivity: Use `scripts/test_provider_routing.py`

**Issue:** Docker build fails
**Solution:**
- Check Dockerfile uses correct path (should be `COPY config/pyproject.toml .`)
- Verify dependencies in `config/pyproject.toml`
- Clean build: `docker system prune -f && docker-compose build --no-cache`

---

## 🔍 Current System Status

### **Production Ready Components ✅**
- ✅ **Mini-Max M2 Smart Routing**: AI-powered provider selection
- ✅ **Native MCP Server**: Direct protocol support, no translation layer
- ✅ **20+ AI Tools**: Chat, analysis, debugging, planning, code review, etc.
- ✅ **Provider Integration**: Mini-Max M2 → GLM → Kimi → Fallback
- ✅ **Container Health**: All 4 containers running successfully
- ✅ **Monitoring**: Health checks, metrics, and observability

### **Issues to Address ❌**
- ❌ **filesystem-mcp**: npx package dependency issues
- ❌ **mermaid-mcp**: Server startup failures

### **Working Tools (Use These!)**
- ✅ **exai-mcp**: Native MCP with 20+ AI tools
- ✅ **git-mcp**: Version control (uvx mcp-server-git)
- ✅ **sequential-thinking**: Deep analysis (npx)
- ✅ **memory-mcp**: Knowledge graph (npx)

### **Key Files to Know:**

#### **Core Components:**
- `src/daemon/ws_server.py` - Native MCP server implementation (v6.1.0)
- `src/providers/` - Smart provider routing (Mini-Max M2, GLM, Kimi)
- `src/orchestrator/route_manager.py` - AI-powered routing logic
- `tools/` - All AI tool implementations

#### **Configuration:**
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container build configuration  
- `config/pyproject.toml` - Dependencies
- `.mcp.json` - MCP client configuration
- `.env.docker` - Container environment variables

#### **Monitoring:**
- Health: `http://127.0.0.1:3002/health`
- Metrics: `http://127.0.0.1:3003/metrics`
- Logs: `logs/exai-mcp.log`, `logs/provider-routing.log`

---

## 🧹 Process Management

### Automated System Cleanup
The system includes an **automated cleanup system** to prevent process bloat:

**Scripts**: `scripts/windows-cleanup/`
**Quick Cleanup**:
```powershell
cd C:\Project\EX-AI-MCP-Server\scripts\windows-cleanup
.\cleanup_all_fixed.ps1
```

### What Gets Cleaned
- **Processes**: Old bash, cmd, node, python processes
- **Shell Snapshots**: Temporary agent files
- **Docker Resources**: Unused containers and images

---

**Remember**: This is a **production MCP server with AI capabilities** - you're working with smart provider routing, not just a regular server. Focus on understanding the AI tool ecosystem and smart routing architecture! 🚀

**Current Status**: Production-ready with Mini-Max M2 smart routing
- All core services: Running and healthy
- AI tools: 20+ tools operational  
- Provider routing: AI-powered decisions active
- MCP protocol: Native support fully functional

---

**Philosophy**: Implement intelligent systems, document real capabilities, maintain production quality.

**This is a clean, production-ready system optimized for AI agent operations.**