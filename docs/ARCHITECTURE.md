# Multi-Project AI Orchestration Architecture

**Last Updated:** 2025-11-14
**Status:** Production-Ready

---

## 🏗️ System Architecture

This system implements a **three-tier distributed AI orchestration platform**:

### Tier 1: Client Access Layer
**Location:** End-user machines (Windows/Mac/Linux)
**Components:**
- Claude Code (VS Code Extension)
- MCP Configuration: `~/.claude/config/.mcp.json`
- Access Protocol: MCP stdio (JSON-RPC 2.0)

**Purpose:** Provides user interface to AI services

---

### Tier 2: Orchestration Layer
**Location:** `C:/Project/Orchestator/`
**Components:**
- `services/mcp_bridge/` - Protocol translation (MCP ↔ WebSocket)
- `services/agents/` - Specialized AI agents
- `orchestrator/` - Routing and coordination
- Bridge Service: `direct_bridge.py` (port 8008)

**Purpose:** Intelligently routes requests, translates protocols, coordinates services

---

### Tier 3: Infrastructure Layer
**Location:** `C:/Project/EX-AI-MCP-Server/`
**Components:**
- Docker Compose deployment
- EXAI Daemon (WebSocket server, port 3010)
- Redis (session persistence, port 6379)
- Monitoring (Prometheus metrics, port 3003)

**Purpose:** Executes AI workloads, manages state, provides observability

---

## 🔌 Data Flow

### MCP Tool Call Flow
```
1. Claude Code (client)
   ↓ sends: {"method": "tools/call", "params": {...}}
2. ~/.claude/config/.mcp.json
   → Executes: mcp_server_wrapper.py
3. mcp_server_wrapper.py (Orchestator)
   ↓ sends: WebSocket message
4. direct_bridge.py:8008 (Orchestator)
   ↓ sends: WebSocket with token
5. EXAI daemon:3010 (Docker)
   → Executes tool
   ↓ returns: result
6. Response flows back through chain to Claude Code
```

### Protocol Translation Points
- **MCP → JSON-RPC:** mcp_server_wrapper.py
- **JSON-RPC → EXAI Protocol:** direct_bridge.py
- **EXAI → JSON-RPC:** direct_bridge.py (response)
- **JSON-RPC → MCP:** mcp_server_wrapper.py (response)

---

## 📋 Deployment Requirements

### Development Environment (Current)
All three tiers run on same Windows machine:
- Client: VS Code with Claude Code extension
- Orchestrator: C:/Project/Orchestator/ (Python 3.13)
- Infrastructure: Docker Desktop

### Production Environment (Target)
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Clients    │      │ Orchestrator │      │ Infrastructure│
│              │      │              │      │              │
│ - Claude     │◄────►│ - Bridge     │◄────►│ - EXAI Daemon│
│ - CLI        │ HTTP │ - Agents     │ WS   │ - Redis      │
│ - Web UI     │      │ - Router     │      │ - Monitoring │
└──────────────┘      └──────────────┘      └──────────────┘
     │                        │                      │
     └────────────────────────┼──────────────────────┘
                              ▼
                      ┌──────────────┐
                      │   Database   │
                      │ (Postgres)   │
                      └──────────────┘
```

---

## 🔧 Configuration Files

### Critical Config Locations

**Client Configuration:**
```bash
~/.claude/config/.mcp.json
```
**Points to:** Orchestator bridge (CORRECT)

**Avoid conflicts:**
```bash
# DELETE these if they exist:
~/.claude/config/mcp-config.claude.json  ❌ CONFLICT
```

**Orchestrator Configuration:**
```bash
C:/Project/Orchestator/.mcp.json
C:/Project/Orchestator/services/mcp_bridge/direct_bridge.py
```

**Infrastructure Configuration:**
```bash
C:/Project/EX-AI-MCP-Server/.env
C:/Project/EX-AI-MCP-Server/docker-compose.yml
```

---

## 🚀 Deployment Commands

### Development (Current Setup)

**Start Infrastructure:**
```bash
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d
curl http://127.0.0.1:3002/health  # Verify
```

**Start Orchestration:**
```bash
cd C:/Project/Orchestator/services/mcp_bridge
nohup python3 direct_bridge.py > direct_bridge.log 2>&1 &
```

**Verify System:**
```bash
curl http://127.0.0.1:3002/health  # Infrastructure health
netstat -an | grep 8008            # Bridge running
@exai-mcp status                   # Test from Claude Code
```

---

## 📊 Monitoring & Health Checks

### Infrastructure Layer (EX-AI-MCP-Server)
- **Health:** http://127.0.0.1:3002/health
- **Metrics:** http://127.0.0.1:3003/metrics (Prometheus)
- **Dashboard:** http://127.0.0.1:3001 (Web UI)

### Orchestration Layer (Orchestator)
- **Bridge Logs:** `C:/Project/Orchestator/services/mcp_bridge/direct_bridge.log`
- **Process Check:** `netstat -an | grep 8008`

---

## 🛠️ Troubleshooting

### Quick Diagnostics
```bash
# Check all tiers
docker ps | grep exai          # Tier 3: Infrastructure
netstat -an | grep 8008        # Tier 2: Orchestration
ls ~/.claude/config/.mcp.json  # Tier 1: Client

# Test connectivity
curl http://127.0.0.1:3002/health
python3 -c "import websockets; print('OK')"  # Bridge dependency
@exai-mcp status  # Full integration test
```

### Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Container outdated | Dockerfile newer than container | `docker-compose build --no-cache` |
| Bridge not running | Port 8008 not listening | Restart `direct_bridge.py` |
| Config conflict | Two .mcp.json files | Delete `mcp-config.claude.json` |

---

## 📚 Documentation Map

### Project Documentation
- **EX-AI-MCP-Server:** `C:/Project/EX-AI-MCP-Server/docs/`
  - `integration/EXAI_MCP_INTEGRATION_GUIDE.md`
  - `troubleshooting/README.md`
  - `ARCHITECTURE.md` (this file)

- **Orchestator:** `C:/Project/Orchestator/docs/`
  - `index.md` - Navigation hub
  - `CURRENT-SYSTEM/README.md` - System status
  - `architecture/` - Design docs

- **Client:**
  - `~/.claude/config/.mcp.json` - MCP server config

### Cross-Project References
This architecture document should be referenced by all three projects to maintain clarity on system design and inter-project dependencies.

---

## ✅ Verification Checklist

- [ ] EX-AI-MCP-Server Docker containers healthy
- [ ] Orchestator bridge service running (port 8008)
- [ ] Client config points to Orchestator (not EX-AI-MCP-Server)
- [ ] No conflicting MCP config files
- [ ] Health endpoints responding
- [ ] Test MCP call works: `@exai-mcp status`

---

**Status:** Production-ready distributed architecture
**Next Steps:** Scale orchestration layer for multi-server deployment
