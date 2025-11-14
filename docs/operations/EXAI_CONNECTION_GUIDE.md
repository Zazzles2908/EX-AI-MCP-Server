# EXAI MCP Server - Connection Guide for Future Projects

**Version:** 6.0.0
**Last Updated:** 2025-11-14
**Status:** ✅ Production Ready

---

## 🎯 Purpose

This guide provides comprehensive instructions for connecting new projects to the EXAI MCP Server, enabling access to all 29 MCP tools with intelligent routing across GLM-4.6, Kimi K2, and MiniMax M2-Stable models.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Automated Health Checking](#automated-health-checking)
4. [Container Management](#container-management)
5. [Connection Methods](#connection-methods)
6. [Port Reference](#port-reference)
7. [MCP Configuration](#mcp-configuration)
8. [Environment Setup](#environment-setup)
9. [Testing Connection](#testing-connection)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Configuration](#advanced-configuration)

---

## Prerequisites

### Required Software

- **Docker Desktop** (Windows with WSL2)
- **Python 3.13+** (for local development)
- **Node.js 18+** (for MCP tools)
- **Claude Code** (MCP client)

### Directory Structure

Your project should be located in:
```
C:\Project\[Your-Project-Name]\
```

The EXAI MCP Server expects access to:
- `C:\Project\EX-AI-MCP-Server\` (EXAI server)
- `C:\Project\Orchestator\` (Orchestrator bridge)

---

## Quick Start

### Option A: Start Existing Container (Fastest)

If the EXAI container is already running:

```bash
# Verify container is running
docker ps | grep exai-mcp-server

# Should show:
# exai-mcp-server              (healthy)
```

**Jump to:** [MCP Configuration](#mcp-configuration)

---

### Option B: Rebuild and Start Container

If you need to rebuild or the container was removed:

```bash
# 1. Navigate to EXAI directory
cd C:\Project\EX-AI-MCP-Server

# 2. Build the image (no cache)
docker-compose build --no-cache

# 3. Start all services
docker-compose up -d

# 4. Verify startup
docker-compose ps
curl http://127.0.0.1:3002/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"6.0.0"}
```

**Verify all services:**
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected output:**
```
NAMES                   STATUS           PORTS
exai-mcp-server         Up (healthy)     0.0.0.0:3001->8080/tcp,...
exai-redis              Up (healthy)     0.0.0.0:6379->6379/tcp
exai-redis-commander    Up (healthy)     0.0.0.0:8081->8081/tcp
```

---

## Automated Health Checking

The EXAI MCP Server includes an **automated health check system** that runs after every container rebuild to detect issues, errors, and bugs.

### What It Checks

- **Critical Issues**: Missing dependencies, configuration errors, startup failures
- **Warnings**: API connectivity issues, missing packages, deprecated features
- **Container Logs**: Parses all container logs for ERROR, WARNING, FATAL patterns
- **Endpoints**: Tests health (3002), dashboard (3001), and metrics (3003) endpoints
- **Redis**: Validates connectivity, authentication, and configuration
- **WebSocket**: Checks daemon startup and port availability

### Running the Health Check

The EXAI MCP Server has **automatic health checking integrated into the container startup process**.

**Option 1: Automatic (Default - No Action Required)**
The health check runs automatically every time the container starts:
```bash
# Start container (health check runs automatically)
docker-compose up -d

# Check logs for health check output
docker-compose logs exai-mcp-server

# View latest health report
cat docs/reports/CONTAINER_HEALTH_REPORT.md
```

**Option 2: Manual Run**
```bash
# Run health check manually
cd C:\Project\EX-AI-MCP-Server
python scripts/health_check_automated.py

# Exit codes:
# 0 = All good (healthy)
# 1 = Critical issues detected
# 2 = Multiple warnings
```

**Option 3: Post-Build Script**
```bash
# Run the wrapper that builds, checks, and starts
bash scripts/run_post_build_health_check.sh
```

### Health Report Location

After running, check the report at:
```
docs/reports/CONTAINER_HEALTH_REPORT.md
```

This report contains:
- List of critical issues with recommendations
- Warning summary with sources
- Container log analysis
- Endpoint test results
- Redis connectivity tests
- Automated recommendations for fixes

### Example Health Report

```markdown
# EXAI MCP Server - Automated Health Report

**Status:** CRITICAL ISSUES DETECTED

## Critical Issues Detected: 1
## Warnings Detected: 3

## CRITICAL ISSUES

### 1. MiniMax M2-Stable: anthropic package missing
**Source:** exai-mcp-server
**Impact:** High - MiniMax M2-Stable model unavailable
**Recommendation:** Install anthropic package in Dockerfile

## RECOMMENDATIONS

1. Fix MiniMax M2-Stable: Install anthropic package in Dockerfile
2. Create Supabase conversations table or disable Supabase integration
3. Add Prometheus metrics endpoint
```

### Why This Matters

**Before:** Issues were hidden in logs, only discovered during runtime
**After:** All issues automatically detected and documented after every build

This ensures:
- ✅ **Early Detection** - Problems found immediately after build
- ✅ **Clear Reporting** - Issues categorized and prioritized
- ✅ **Actionable Guidance** - Specific recommendations for each issue
- ✅ **Historical Tracking** - Reports overwritten each time (use git to track)
- ✅ **Zero Manual Effort** - Runs automatically or with single command

---

## Container Management

### Starting Services

```bash
# Start all services
cd C:\Project\EX-AI-MCP-Server
docker-compose up -d

# Start specific service
docker-compose up -d exai-mcp-server
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop exai-mcp-server
```

### Removing Services (Option B)

```bash
# Remove containers and volumes (complete cleanup)
docker-compose down -v

# Remove images as well (nuclear option)
docker-compose down -v --rmi all
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f exai-mcp-server

# Last 100 lines
docker-compose logs --tail=100 exai-mcp-server
```

### Health Monitoring

```bash
# Check health endpoint
curl http://127.0.0.1:3002/health

# Check all services
docker-compose ps

# View resource usage
docker stats exai-mcp-server exai-redis
```

---

## Connection Methods

### Method 1: Direct MCP Connection (Recommended)

This method uses MCP protocol directly with the EXAI container.

#### Step 1: Create `.mcp.json` in Your Project

Create `C:\Project\[Your-Project]\.mcp.json`:

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/start_ws_shim_safe.py"
      ],
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "SHIM_LISTEN_PORT": "3005",
        "EXAI_WS_PORT": "3010",
        "EXAI_WS_TOKEN": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo",
        "SIMPLE_TOOL_TIMEOUT_SECS": "30",
        "WORKFLOW_TOOL_TIMEOUT_SECS": "46",
        "EXPERT_ANALYSIS_TIMEOUT_SECS": "60",
        "GLM_TIMEOUT_SECS": "30",
        "KIMI_TIMEOUT_SECS": "40"
      }
    }
  }
}
```

#### Step 2: Set Up Virtual Environment

```bash
cd C:\Project\EX-AI-MCP-Server
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.13+
```

#### Step 3: Configure Claude Code

Update your Claude Code settings:

```json
{
  "mcpServers": {
    "exai-mcp": "C:/Project/[Your-Project]/.mcp.json"
  }
}
```

#### Step 4: Test Connection

```bash
# Test health endpoint
curl http://127.0.0.1:3002/health

# Expected response:
# {"status":"healthy","container":"exai-mcp-server",...}
```

---

### Method 2: WebSocket Direct Connection

For custom applications that don't use MCP protocol:

```python
import asyncio
import websockets
import json

async def connect_to_exai():
    uri = "ws://127.0.0.1:3010"
    token = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"

    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "token": token
        }))

        # Send request
        await websocket.send(json.dumps({
            "type": "request",
            "method": "exai_chat",
            "params": {
                "message": "Hello EXAI",
                "model": "glm-4.5-flash"
            }
        }))

        # Receive response
        response = await websocket.recv()
        print(json.loads(response))

# Run
asyncio.run(connect_to_exai())
```

---

## Port Reference

### Host Ports (Windows)

| Port | Service | Protocol | Access | Description |
|------|---------|----------|--------|-------------|
| **3005** | Shim | TCP | Localhost | MCP Shim (for .mcp.json connections) |
| **3010** | WebSocket | WebSocket | Localhost | EXAI Daemon (direct WebSocket) |
| **3001** | Dashboard | HTTP | Browser | Monitoring Dashboard |
| **3002** | Health | HTTP | Localhost | Health Check Endpoint |
| **3003** | Metrics | HTTP | Prometheus | Prometheus Metrics |

### Container Ports (Linux)

| Port | Service | Description |
|------|---------|-------------|
| **8079** | WebSocket Daemon | Internal EXAI WebSocket server |
| **8080** | Dashboard | Monitoring UI |
| **8082** | Health Check | HTTP health endpoint |
| **8000** | Metrics | Prometheus metrics |

### Communication Flow

```
┌─────────────────────┐
│  Your Application   │
└──────────┬──────────┘
           │
           ├─→ Method 1: MCP Protocol
           │    ↓
           │  ┌─────────────────────────┐
           │  │  .mcp.json Config       │
           │  │  Port: 3005 (Shim)      │
           │  └──────────┬──────────────┘
           │             │
           │             ↓
           │         ┌──────────┐
           │         │  WebSocket  │
           │         │  Port: 3010 │
           │         └─────┬──────┘
           │               │
           │               ↓
           │         ┌───────────────┐
           │         │  Container    │
           │         │  Port: 8079   │
           │         └───────────────┘
           │
           └─→ Method 2: Direct WebSocket
                ↓
              Port: 3010 (Host) → 8079 (Container)
```

---

## MCP Configuration

### Available MCP Tools

The EXAI MCP Server provides 29 tools across multiple categories:

#### Chat & Analysis Tools
- `exai_chat` - Chat with AI models (GLM, Kimi, MiniMax)
- `exai_analyze` - Deep code analysis
- `exai_web_search` - Web search integration

#### Workflow Tools
- `exai_planner` - Task planning and execution
- `exai_consensus` - Multi-model consensus
- `exai_refactor` - Code refactoring

#### Code Intelligence
- `exai_codereview` - Code review and quality checks
- `exai_debug` - Debugging assistance
- `exai_testgen` - Test generation

#### File Operations
- `exai_upload_file` - File upload to AI providers
- `exai_kimi_upload_files` - Kimi-specific file handling

### Example Usage in Claude Code

```python
# Chat with EXAI
@exai-mcp chat "Explain this code architecture"

# Analyze code
@exai-mcp analyze "Review this file for security issues"

# Use web search
@exai-mcp web_search "Latest Docker best practices"

# Multi-model consensus
@exai-mcp consensus "Evaluate this architecture design"

# Code review
@exai-mcp codereview "Review my pull request"

# Generate tests
@exai-mcp testgen "Create tests for this module"
```

---

## Environment Setup

### Required Environment Variables

Create `C:\Project\EX-AI-MCP-Server\.env`:

```bash
# EXAI WebSocket Configuration
EXAI_WS_HOST=127.0.0.1
SHIM_LISTEN_PORT=3005
EXAI_WS_PORT=3010
EXAI_WS_TOKEN=pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo

# Timeouts
SIMPLE_TOOL_TIMEOUT_SECS=30
WORKFLOW_TOOL_TIMEOUT_SECS=46
EXPERT_ANALYSIS_TIMEOUT_SECS=60

# Provider Timeouts
GLM_TIMEOUT_SECS=30
KIMI_TIMEOUT_SECS=40
KIMI_WEB_SEARCH_TIMEOUT_SECS=30

# Session Configuration
EX_SESSION_SCOPE_STRICT=true
EX_SESSION_SCOPE_ALLOW_CROSS_SESSION=false
```

### Docker Environment (`.env.docker`)

Container environment is managed via `.env.docker`:

```bash
# WebSocket
EXAI_WS_HOST=0.0.0.0
EXAI_WS_PORT=8079

# Timeouts
WORKFLOW_TOOL_TIMEOUT_SECS=180
TOOL_TIMEOUT_SECS=180
DAEMON_TIMEOUT_SECS=270

# Provider Configurations
GLM_DEFAULT_MODEL=glm-4.5-flash
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview

# Redis
REDIS_PASSWORD=ExAi2025RedisSecurePass123
```

---

## Testing Connection

### 1. Health Check Test

```bash
curl http://127.0.0.1:3002/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "container": "exai-mcp-server",
  "timestamp": "2025-11-14T...",
  "version": "6.0.0",
  "uptime": "2h 15m 30s"
}
```

### 2. Metrics Test

```bash
curl http://127.0.0.1:3003/metrics
```

**Expected Output:** Prometheus-format metrics

### 3. Dashboard Test

Open browser to: `http://127.0.0.1:3001`

You should see the EXAI monitoring dashboard.

### 4. MCP Connection Test

```bash
# Test with a simple MCP request
python -c "
import subprocess
result = subprocess.run([
    'C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe',
    '-u',
    'C:/Project/EX-AI-MCP-Server/scripts/runtime/start_ws_shim_safe.py'
], capture_output=True, text=True, timeout=10)
print(result.returncode)
"
```

Expected: Exit code 0 (success)

---

## Troubleshooting

### Issue: Container Won't Start

**Symptoms:**
- `docker-compose up -d` fails
- Container exits immediately

**Solutions:**

1. **Check logs:**
   ```bash
   docker-compose logs exai-mcp-server
   ```

2. **Verify ports are available:**
   ```bash
   netstat -tln | grep -E ":(3001|3002|3003|3010)"
   ```

3. **Check disk space:**
   ```bash
   docker system df
   ```

4. **Rebuild from scratch:**
   ```bash
   docker-compose down -v
   docker system prune -f
   docker-compose build --no-cache
   docker-compose up -d
   ```

### Issue: MCP Connection Timeout

**Symptoms:**
- Claude Code can't connect to EXAI
- Timeout errors in logs

**Solutions:**

1. **Verify container health:**
   ```bash
   curl http://127.0.0.1:3002/health
   ```

2. **Check shim is running:**
   ```bash
   docker-compose exec exai-mcp-server ps aux | grep run_ws_shim
   ```

3. **Verify port 3010:**
   ```bash
   docker-compose exec exai-mcp-server netstat -tln | grep 8079
   ```

4. **Restart services:**
   ```bash
   docker-compose restart
   ```

### Issue: "Container exai-mcp-daemon not found"

**Cause:** Old documentation referenced wrong container name

**Solution:**
```bash
# New container name is: exai-mcp-server
docker ps | grep exai-mcp-server

# Not: exai-mcp-daemon (old name)
```

### Issue: Port Already in Use

**Symptoms:**
- `Error: port 3010 is already in use`

**Solutions:**

1. **Find process using port:**
   ```bash
   netstat -ano | findstr :3010
   ```

2. **Kill process:**
   ```bash
   taskkill /PID [PID] /F
   ```

3. **Change port in docker-compose.yml:**
   ```yaml
   ports:
     - "3011:8079"  # Use 3011 instead of 3010
   ```

4. **Update .mcp.json:**
   ```json
   "EXAI_WS_PORT": "3011"
   ```

### Issue: WebSocket Connection Refused

**Symptoms:**
- WebSocket connection fails
- Error: "Connection refused"

**Solutions:**

1. **Verify container is running:**
   ```bash
   docker-compose ps | grep exai-mcp-server
   ```

2. **Check WebSocket is listening:**
   ```bash
   docker-compose exec exai-mcp-server netstat -tln | grep 8079
   ```

3. **Verify firewall:**
   - Windows Firewall may block ports 3001-3003, 3010
   - Add exceptions for Docker

4. **Test with telnet:**
   ```bash
   telnet 127.0.0.1 3010
   ```

---

## Advanced Configuration

### Custom Provider Configuration

Edit `C:\Project\EX-AI-MCP-Server\.env.docker`:

```bash
# GLM Configuration
GLM_API_KEY=your_glm_api_key
GLM_DEFAULT_MODEL=glm-4.6
GLM_TIMEOUT_SECS=120

# Kimi Configuration
KIMI_API_KEY=your_kimi_api_key
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TIMEOUT_SECS=180

# MiniMax Configuration
MINIMAX_M2_KEY=your_minimax_key
MINIMAX_ENABLED=true
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
exai-mcp-server:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M
```

### Custom Volumes

Add custom volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./my-data:/app/my-data:ro
  - ./my-logs:/app/my-logs
```

### Custom Health Checks

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8082/health')"]
  interval: 30s
  timeout: 5s
  retries: 3
  start_period: 60s
```

---

## Security Considerations

### Token Authentication

All connections require authentication:

- **Token:** `pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo`
- **Rotate regularly** in production
- **Never commit** to version control

### Network Isolation

EXAI runs in Docker's isolated network:

```bash
# Default network: exai-network
docker network inspect exai-network
```

### Secrets Management

Use environment variables for sensitive data:

```bash
# .env (local)
GLM_API_KEY=sk-...

# .env.docker (container)
GLM_API_KEY=${GLM_API_KEY}
```

Never hardcode secrets in:
- `.mcp.json`
- `docker-compose.yml`
- Source code

---

## Monitoring & Observability

### Health Endpoints

```bash
# Container health
curl http://127.0.0.1:3002/health

# Detailed status
curl http://127.0.0.1:3002/status

# Redis health
curl http://127.0.0.1:3002/redis/health
```

### Metrics

```bash
# Prometheus metrics
curl http://127.0.0.1:3003/metrics

# Key metrics:
# - exai_requests_total
# - exai_request_duration_seconds
# - exai_provider_latency_seconds
# - exai_error_rate
```

### Logs

```bash
# Application logs
docker-compose logs exai-mcp-server

# Real-time tail
docker-compose logs -f exai-mcp-server

# Last 100 lines
docker-compose logs --tail=100 exai-mcp-server

# Search for errors
docker-compose logs exai-mcp-server | grep ERROR
```

### Dashboard

Open browser to: `http://127.0.0.1:3001`

Features:
- Real-time metrics
- Active sessions
- Request history
- Provider status
- Error rates

---

## Performance Optimization

### Concurrent Requests

Default limits:
- **Global:** 24 concurrent requests
- **Per session:** 8 concurrent requests
- **Per provider:** 4-6 inflight requests

### Timeout Configuration

```bash
# Simple tools: 30s
SIMPLE_TOOL_TIMEOUT_SECS=30

# Workflow tools: 46s
WORKFLOW_TOOL_TIMEOUT_SECS=46

# Expert analysis: 60s
EXPERT_ANALYSIS_TIMEOUT_SECS=60

# Provider-specific:
GLM_TIMEOUT_SECS=30
KIMI_TIMEOUT_SECS=40
```

### Caching

EXAI implements intelligent caching:

- **Model responses:** 5-minute TTL
- **Routing decisions:** 5-minute TTL
- **File metadata:** Persistent

---

## Integration Examples

### Python Integration

```python
import asyncio
import websockets
import json

class EXAIClient:
    def __init__(self, uri="ws://127.0.0.1:3010"):
        self.uri = uri
        self.token = "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        self.websocket = None

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)
        await self.authenticate()

    async def authenticate(self):
        await self.websocket.send(json.dumps({
            "type": "auth",
            "token": self.token
        }))

    async def chat(self, message, model="glm-4.5-flash"):
        await self.websocket.send(json.dumps({
            "type": "request",
            "method": "exai_chat",
            "params": {
                "message": message,
                "model": model
            }
        }))
        response = await self.websocket.recv()
        return json.loads(response)

    async def close(self):
        if self.websocket:
            await self.websocket.close()

# Usage
async def main():
    client = EXAIClient()
    await client.connect()
    result = await client.chat("Hello EXAI!")
    print(result)
    await client.close()

asyncio.run(main())
```

### JavaScript Integration

```javascript
const WebSocket = require('ws');

class EXAIClient {
    constructor(uri = 'ws://127.0.0.1:3010') {
        this.uri = uri;
        this.token = 'pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo';
        this.ws = null;
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(this.uri);

            this.ws.on('open', () => {
                this.authenticate().then(resolve).catch(reject);
            });

            this.ws.on('error', reject);
        });
    }

    authenticate() {
        return new Promise((resolve, reject) => {
            this.ws.send(JSON.stringify({
                type: 'auth',
                token: this.token
            }));

            this.ws.once('message', (data) => {
                const response = JSON.parse(data);
                if (response.status === 'authenticated') {
                    resolve();
                } else {
                    reject(new Error('Authentication failed'));
                }
            });
        });
    }

    async chat(message, model = 'glm-4.5-flash') {
        return new Promise((resolve, reject) => {
            this.ws.send(JSON.stringify({
                type: 'request',
                method: 'exai_chat',
                params: {
                    message,
                    model
                }
            }));

            this.ws.once('message', (data) => {
                try {
                    const response = JSON.parse(data);
                    resolve(response);
                } catch (e) {
                    reject(e);
                }
            });
        });
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Usage
async function main() {
    const client = new EXAIClient();
    await client.connect();
    const result = await client.chat('Hello EXAI!');
    console.log(result);
    client.close();
}

main().catch(console.error);
```

### cURL Test

```bash
# Health check
curl http://127.0.0.1:3002/health

# Test WebSocket connection
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Key: SGVsbG9XQUI=" \
     -H "Sec-WebSocket-Version: 13" \
     http://127.0.0.1:3010/ws

# Test metrics
curl http://127.0.0.1:3003/metrics | head -20
```

---

## Frequently Asked Questions

### Q: What models are available?

**A:** EXAI supports three providers:
- **GLM-4.5-flash** (fast, cost-effective)
- **GLM-4.6** (high quality)
- **Kimi K2-0905-preview** (excellent for analysis)
- **MiniMax M2-Stable** (best for coding)

### Q: How many concurrent requests?

**A:**
- **Global limit:** 24 concurrent requests
- **Per session:** 8 concurrent requests
- **Per provider:** 4-6 inflight requests

### Q: Can I use EXAI from other machines?

**A:** Currently, EXAI is configured for localhost only. To expose externally:

1. Change `EXAI_WS_HOST` from `127.0.0.1` to `0.0.0.0`
2. Update firewall rules
3. Use authentication tokens
4. Consider using reverse proxy (nginx, Traefik)

### Q: How do I add new MCP tools?

**A:**
1. Create tool in `C:\Project\EX-AI-MCP-Server\tools\`
2. Register in tool registry
3. Update MCP manifest
4. Rebuild container
5. Test with new tool

### Q: Where are logs stored?

**A:**
- **Container logs:** `docker-compose logs exai-mcp-server`
- **Volume logs:** `C:\Project\EX-AI-MCP-Server\logs\`
- **Dashboard:** `http://127.0.0.1:3001`

### Q: How do I backup data?

**A:**
```bash
# Backup Redis data
docker-compose exec exai-redis redis-cli BGSAVE
docker cp exai-mcp-server:/data/dump.rdb ./backup.rdb

# Backup logs
tar -czf exai-logs-$(date +%Y%m%d).tar.gz logs/

# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)
```

---

## Support & Resources

### Documentation
- **Main Docs:** `C:\Project\EX-AI-MCP-Server\docs\README.md`
- **Operations:** `C:\Project\EX-AI-MCP-Server\docs\operations\`
- **API Reference:** `C:\Project\EX-AI-MCP-Server\docs\api\`

### External Links
- [MCP Specification](https://modelcontextprotocol.io)
- [GLM Platform](https://open.bigmodel.cn)
- [Kimi Platform](https://platform.moonshot.cn)
- [Docker Documentation](https://docs.docker.com)

### Getting Help

1. **Check health endpoint:** `curl http://127.0.0.1:3002/health`
2. **Review logs:** `docker-compose logs exai-mcp-server`
3. **Read documentation:** `docs/troubleshooting/`
4. **Open dashboard:** `http://127.0.0.1:3001`

---

## Quick Reference Card

```bash
# Start EXAI
docker-compose up -d

# Check status
docker-compose ps
curl http://127.0.0.1:3002/health

# View logs
docker-compose logs -f

# Stop EXAI
docker-compose down

# Rebuild EXAI
docker-compose build --no-cache

# Test connection
curl http://127.0.0.1:3002/health

# Dashboard
open http://127.0.0.1:3001

# Metrics
curl http://127.0.0.1:3003/metrics

# Container name: exai-mcp-server
# WebSocket port: 3010 (host) → 8079 (container)
# Health port: 3002
# Dashboard port: 3001
```

---

**Document Version:** 6.0.0
**Last Updated:** 2025-11-14
**Maintained By:** EX-AI MCP Server Team
**Status:** ✅ Production Ready
