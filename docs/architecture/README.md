# Architecture Documentation

This directory contains detailed technical documentation about the EXAI MCP Server architecture.

## 📖 Available Guides

### Core Architecture
- **[EXAI MCP Architecture](exai-mcp-architecture.md)** ⭐ - **START HERE**
  - Complete 5-layer architecture
  - Message flow sequences with MERMAID diagrams
  - Port mapping visualization
  - Tool execution flow
  - Component deep-dives
  - Configuration reference
  - Troubleshooting guide

## 🎯 Reading Path

### For Everyone
1. Start with [EXAI MCP Architecture](exai-mcp-architecture.md)
   - Overview section for high-level understanding
   - 5-Layer Architecture diagram
   - Message Flow section for communication patterns

### For Developers
1. Read [EXAI MCP Architecture](exai-mcp-architecture.md)
   - Component Details section
   - Connection Protocol section
   - Configuration Reference section

### For System Administrators
1. Read [EXAI MCP Architecture](exai-mcp-architecture.md)
   - Port Mapping section
   - Session Management section
   - Configuration Reference section
   - Troubleshooting section

## 🔍 Key Concepts

### 5-Layer Architecture
```
┌─────────────────────────────────────────┐
│ Layer 1: Claude Desktop (MCP Client)    │
└────────────┬────────────────────────────┘
             │ stdio
             ↓
┌─────────────────────────────────────────┐
│ Layer 2: WebSocket Shim                 │
└────────────┬────────────────────────────┘
             │ WebSocket (3000)
             ↓
┌─────────────────────────────────────────┐
│ Layer 3: Docker Port Mapping            │
└────────────┬────────────────────────────┘
             │ Network
             ↓
┌─────────────────────────────────────────┐
│ Layer 4: EXAI Daemon                    │
└────────────┬────────────────────────────┘
             │ Python calls
             ↓
┌─────────────────────────────────────────┐
│ Layer 5: EXAI Tools (21 tools)          │
└─────────────────────────────────────────┘
```

### Message Flow
1. **Claude Desktop** → **Shim** (stdio)
2. **Shim** → **Daemon** (WebSocket: 3000→8079)
3. **Daemon** → **Tool Registry** (Python)
4. **Tool** → **AI Provider** (GLM/Kimi API)
5. Response flows back through the same path

### Critical Configuration
- **Port 3000**: Where shim connects FROM (host)
- **Port 8079**: Where daemon listens TO (container)
- **Mapping**: `3000:8079` in docker-compose.yml

## 📊 What You'll Learn

After reading these guides, you'll understand:
- ✅ How MCP protocol maps to WebSocket
- ✅ Why Docker is used for isolation
- ✅ How session management works
- ✅ Where timeouts are configured
- ✅ How tools are registered and executed
- ✅ What to check when things go wrong

## 🛠️ Hands-On Learning

### Trace a Request
1. Read the Message Flow section
2. Try `@exai-mcp status` in Claude Desktop
3. Check the logs: `tail -f logs/ws_shim_*.log`
4. Compare what you see with the sequence diagrams

### Understand Port Mapping
1. Read the Port Mapping section
2. Run `docker port exai-mcp-daemon 8079`
3. Run `netstat -ano | findstr :3000`
4. See how the architecture maps to reality

### Explore Tool Execution
1. Read the Tool Execution Flow section
2. Try `@exai-mcp chat "Hello"`
3. Watch the logs during execution
4. Trace through the state diagram

## 📚 Related Documentation

- **[Getting Started](../getting-started/)** - Quick setup and first steps
- **[API Reference](../api/)** - Tool integration details
- **[Development](../development/)** - Create custom tools
- **[Troubleshooting](../troubleshooting/)** - Fix common issues

## 💡 Tips

- Use the MERMAID diagrams to visualize complex flows
- Compare the sequence diagrams with actual log output
- Reference the configuration tables when setting up
- Keep the troubleshooting checklist handy

---

**Start with**: [EXAI MCP Architecture](exai-mcp-architecture.md)
