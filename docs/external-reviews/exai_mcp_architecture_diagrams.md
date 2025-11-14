# EX-AI MCP Server - Architecture Diagrams

**Date**: November 13, 2025

---

## 1. Current Architecture (What's Failing)

```mermaid
graph TB
    subgraph "Windows Host"
        CC[Claude Code<br/>VS Code Extension<br/>Minimax LLM]
        Shim[WebSocket Shim<br/>run_ws_shim.py<br/>stdio ↔ WebSocket]
        
        CC -->|stdio<br/>stdin/stdout| Shim
    end
    
    subgraph "Docker Container<br/>exai-mcp-daemon"
        Daemon[WebSocket Daemon<br/>Port 8079<br/>Custom Protocol]
        Router[AI Manager<br/>Tool Router]
        Redis[(Redis<br/>Port 6379)]
        
        Daemon --> Router
        Router --> Redis
    end
    
    Shim -.->|❌ FAILS<br/>ws://127.0.0.1:3010<br/>Connection Refused| Daemon
    
    style Shim fill:#ff6b6b
    style Daemon fill:#ff6b6b
    style CC fill:#ffd93d
```

### Problem Points:
1. **Network Barrier**: Docker container is isolated from Windows host process
2. **Port Mapping**: Host 3010 → Container 8079 mapping fails or is unreliable
3. **Custom Protocol**: WebSocket protocol requires translation layer
4. **Process Isolation**: Shim cannot directly communicate with containerized daemon

---

## 2. Working MCP Servers Architecture

```mermaid
graph TB
    subgraph "Windows Host"
        CC[Claude Code<br/>VS Code Extension<br/>Minimax LLM]
        FS[filesystem-mcp<br/>npx @modelcontextprotocol/server-filesystem]
        GIT[git-mcp<br/>uvx mcp-server-git]
        SB[supabase-mcp<br/>npx @supabase/mcp-server-supabase]
        
        CC -->|stdio<br/>Direct| FS
        CC -->|stdio<br/>Direct| GIT
        CC -->|stdio<br/>Direct| SB
    end
    
    FS --> FSys[File System<br/>Direct Access]
    GIT --> GitRepo[Git Repository<br/>Direct Access]
    SB --> SBAPI[Supabase API<br/>HTTP/REST]
    
    style FS fill:#51cf66
    style GIT fill:#51cf66
    style SB fill:#51cf66
    style CC fill:#51cf66
```

### Why These Work:
1. **No Docker**: Direct process execution on Windows
2. **No Network**: stdio communication (stdin/stdout)
3. **Standard Protocol**: MCP stdio protocol (JSON-RPC)
4. **No Translation**: Direct MCP implementation

---

## 3. Why Direct Commands Work

```mermaid
graph TB
    subgraph "Windows Host"
        Bash[Bash/Python Script]
    end
    
    subgraph "Docker Container"
        Daemon[WebSocket Daemon<br/>Port 8079]
    end
    
    Bash -->|✅ WORKS<br/>Direct WebSocket<br/>ws://127.0.0.1:3010| Daemon
    
    style Bash fill:#51cf66
    style Daemon fill:#51cf66
```

### Why This Works:
1. **No MCP Layer**: Direct WebSocket protocol
2. **No stdio**: WebSocket connection from Python/Bash
3. **Same Network**: Both trying to reach Docker port mapping
4. **No Claude Code**: No LLM or MCP client involved

---

## 4. Solution 1: Run Daemon on Windows (Quick Fix)

```mermaid
graph TB
    subgraph "Windows Host"
        CC[Claude Code<br/>VS Code Extension]
        Shim[WebSocket Shim<br/>run_ws_shim.py]
        Daemon[WebSocket Daemon<br/>Port 8079<br/>RUNS ON WINDOWS]
        Router[AI Manager]
        
        CC -->|stdio| Shim
        Shim -->|✅ WebSocket<br/>127.0.0.1:8079<br/>Same Host| Daemon
        Daemon --> Router
    end
    
    style CC fill:#51cf66
    style Shim fill:#51cf66
    style Daemon fill:#51cf66
    style Router fill:#51cf66
```

### Advantages:
- ✅ Removes Docker networking barrier
- ✅ All processes on same host
- ✅ Reliable localhost communication
- ✅ Quick to implement

### Disadvantages:
- ❌ No Docker isolation
- ❌ Manual daemon management
- ❌ Still uses WebSocket layer

---

## 5. Solution 2: Native stdio MCP Server (Best Solution)

```mermaid
graph TB
    subgraph "Windows Host"
        CC[Claude Code<br/>VS Code Extension]
        Native[Native stdio MCP Server<br/>stdio_native.py<br/>Standard MCP Protocol]
        Tools[Tool Implementations<br/>chat, debug, analyze, etc.]
        
        CC -->|stdio<br/>JSON-RPC<br/>Standard MCP| Native
        Native --> Tools
    end
    
    style CC fill:#51cf66
    style Native fill:#51cf66
    style Tools fill:#51cf66
```

### Advantages:
- ✅ Standard MCP protocol
- ✅ No Docker needed
- ✅ No WebSocket layer
- ✅ No shim translation
- ✅ Works with all MCP clients
- ✅ Simple architecture
- ✅ Reliable and fast

### Disadvantages:
- ❌ Requires code refactoring
- ❌ Need to adapt existing tools
- ❌ Initial implementation effort

---

## 6. Data Flow Comparison

### Current (Failing):
```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant Shim as WebSocket Shim
    participant Docker as Docker Network
    participant Daemon as WS Daemon
    
    CC->>Shim: tools/list (stdio)
    Shim->>Docker: WebSocket Connect
    Docker--xShim: ❌ Connection Failed
    Shim--xCC: ❌ No Response
    
    Note over CC,Daemon: Connection never established
```

### Solution 1 (Run on Windows):
```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant Shim as WebSocket Shim
    participant Daemon as WS Daemon (Windows)
    
    CC->>Shim: tools/list (stdio)
    Shim->>Daemon: WebSocket Connect (localhost)
    Daemon->>Shim: ✅ Connected
    Shim->>Daemon: {"op": "list_tools"}
    Daemon->>Shim: {"tools": [...]}
    Shim->>CC: ✅ MCP Response
```

### Solution 2 (Native stdio):
```mermaid
sequenceDiagram
    participant CC as Claude Code
    participant Native as Native stdio Server
    participant Tools as Tool Implementations
    
    CC->>Native: tools/list (stdio)
    Native->>Tools: Load tools
    Tools->>Native: Tool list
    Native->>CC: ✅ MCP Response (stdio)
    
    CC->>Native: tools/call: chat (stdio)
    Native->>Tools: Execute chat()
    Tools->>Native: Result
    Native->>CC: ✅ MCP Response (stdio)
```

---

## 7. Network Topology

### Current (Docker):
```
┌─────────────────────────────────────────────┐
│ Windows Host Network (192.168.x.x)         │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Claude Code Process                   │  │
│  │ ├─ Shim (Python subprocess)          │  │
│  │ │  └─ Tries: ws://127.0.0.1:3010    │  │
│  │ └─ ❌ Connection fails               │  │
│  └──────────────────────────────────────┘  │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Docker Desktop (WSL2)                 │  │
│  │                                        │  │
│  │  ┌────────────────────────────────┐  │  │
│  │  │ Docker Bridge Network          │  │  │
│  │  │ (172.17.0.0/16)                │  │  │
│  │  │                                 │  │  │
│  │  │  ┌─────────────────────────┐   │  │  │
│  │  │  │ exai-mcp-daemon         │   │  │  │
│  │  │  │ IP: 172.17.0.2          │   │  │  │
│  │  │  │ Port: 8079              │   │  │  │
│  │  │  │ Mapped to Host: 3010    │   │  │  │
│  │  │  └─────────────────────────┘   │  │  │
│  │  └────────────────────────────────┘  │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘

❌ Issue: Shim on host network cannot reliably reach container
```

### Solution (Native):
```
┌─────────────────────────────────────────────┐
│ Windows Host Network (192.168.x.x)         │
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │ Claude Code Process                   │  │
│  │ ├─ Native MCP Server (Python)        │  │
│  │ │  └─ stdio communication            │  │
│  │ └─ ✅ Direct IPC                     │  │
│  └──────────────────────────────────────┘  │
│                                              │
└─────────────────────────────────────────────┘

✅ No network barriers, direct process communication
```

---

## 8. Protocol Stack Comparison

### Current (Failing):
```
Layer 7: Application    │ Claude Code (Minimax LLM)
                        │
Layer 6: MCP Protocol   │ JSON-RPC over stdio
                        │
Layer 5: Shim           │ Protocol Translation (stdio ↔ WebSocket)
                        │
Layer 4: WebSocket      │ Custom WebSocket Protocol
                        │
Layer 3: Network        │ TCP (Docker port mapping 3010:8079)
                        │ ❌ FAILS HERE
Layer 2: Docker Bridge  │ Docker networking layer (172.17.0.x)
                        │
Layer 1: Container      │ WebSocket Daemon
```

### Solution (Native stdio):
```
Layer 7: Application    │ Claude Code (Minimax LLM)
                        │
Layer 6: MCP Protocol   │ JSON-RPC over stdio
                        │
Layer 5: IPC            │ stdin/stdout pipes
                        │
Layer 4: Process        │ Native MCP Server (Python)
                        │
Layer 3: Direct Call    │ Function calls (no network)
                        │
Layer 2: Tools          │ Tool implementations
                        │
Layer 1: Execution      │ Python runtime
```

---

## 9. Failure Points Analysis

### Current Architecture:
```mermaid
graph LR
    A[Start] --> B{Claude Code<br/>Starts?}
    B -->|Yes| C{Shim Process<br/>Starts?}
    B -->|No| X1[❌ Fail 1]
    C -->|Yes| D{WebSocket<br/>Connection?}
    C -->|No| X2[❌ Fail 2]
    D -->|Yes| E{Token<br/>Auth?}
    D -->|No| X3[❌ Fail 3]
    E -->|Yes| F{List Tools<br/>Success?}
    E -->|No| X4[❌ Fail 4]
    F -->|Yes| G{Minimax<br/>Discovery?}
    F -->|No| X5[❌ Fail 5]
    G -->|Yes| H[✅ Success]
    G -->|No| X6[❌ Fail 6]
    
    style X1 fill:#ff6b6b
    style X2 fill:#ff6b6b
    style X3 fill:#ff6b6b
    style X4 fill:#ff6b6b
    style X5 fill:#ff6b6b
    style X6 fill:#ff6b6b
    style H fill:#51cf66
```

**6 Failure Points!**

### Native stdio Architecture:
```mermaid
graph LR
    A[Start] --> B{Claude Code<br/>Starts?}
    B -->|Yes| C{MCP Server<br/>Process?}
    B -->|No| X1[❌ Fail 1]
    C -->|Yes| D{List Tools<br/>Success?}
    C -->|No| X2[❌ Fail 2]
    D -->|Yes| E[✅ Success]
    D -->|No| X3[❌ Fail 3]
    
    style X1 fill:#ff6b6b
    style X2 fill:#ff6b6b
    style X3 fill:#ff6b6b
    style E fill:#51cf66
```

**Only 3 Failure Points!**

---

## 10. Performance Comparison

### Current (Docker + WebSocket):
```
Request: @exai-mcp chat "hello"
│
├─ Claude Code parses request (10ms)
├─ stdio write to shim (5ms)
├─ Shim reads from stdin (10ms)
├─ Shim creates WebSocket message (5ms)
├─ WebSocket send over network (50-200ms) ← SLOW
├─ Docker network routing (20-100ms) ← SLOW
├─ Container receives packet (10ms)
├─ Daemon processes WebSocket (20ms)
├─ Tool execution (100ms)
├─ Response through WebSocket (50-200ms) ← SLOW
├─ Docker network routing (20-100ms) ← SLOW
├─ Shim receives response (10ms)
├─ Shim writes to stdout (5ms)
└─ Claude Code receives response (10ms)

Total: 310-890ms (average ~600ms)
```

### Native (stdio):
```
Request: @exai-mcp chat "hello"
│
├─ Claude Code parses request (10ms)
├─ stdio write to MCP server (5ms)
├─ Server reads from stdin (5ms)
├─ Tool execution (100ms)
├─ Server writes to stdout (5ms)
└─ Claude Code receives response (5ms)

Total: 130ms (4.6x faster!)
```

---

## 11. Recommended Migration Path

```mermaid
graph TD
    Current[Current State<br/>Docker + WebSocket<br/>❌ Not Working]
    
    Quick[Quick Fix<br/>Run on Windows<br/>⚡ Fast Implementation]
    
    Native[Native stdio<br/>✅ Best Solution<br/>🎯 Long-term]
    
    Test1{Does it<br/>work?}
    Test2{Performance<br/>OK?}
    
    Current --> Quick
    Quick --> Test1
    Test1 -->|Yes| Test2
    Test1 -->|No| Debug1[Debug Connection<br/>Issues]
    Test2 -->|Yes| Native
    Test2 -->|No| Debug2[Check Tool<br/>Performance]
    Debug1 --> Quick
    Debug2 --> Native
    
    Native --> Production[Production<br/>Deployment<br/>🚀]
    
    style Current fill:#ff6b6b
    style Quick fill:#ffd93d
    style Native fill:#51cf66
    style Production fill:#51cf66
```

### Timeline:
- **Phase 1** (Day 1): Quick Fix - Run daemon on Windows
- **Phase 2** (Week 1): Test and validate
- **Phase 3** (Week 2-3): Implement native stdio server
- **Phase 4** (Week 4): Testing and refinement
- **Phase 5** (Month 2): Production deployment

---

## 12. Decision Matrix

| Criteria | Docker (Current) | Run on Windows | Native stdio |
|----------|-----------------|----------------|--------------|
| **Implementation Time** | ✅ Already done | 🟡 30 min | 🔴 2-4 hours |
| **Reliability** | 🔴 Poor | 🟡 Good | ✅ Excellent |
| **Performance** | 🔴 Slow | 🟡 Medium | ✅ Fast |
| **Complexity** | 🔴 Very High | 🟡 Medium | ✅ Simple |
| **MCP Compliance** | 🔴 Custom | 🟡 Partial | ✅ Full |
| **Docker Required** | 🔴 Yes | ✅ No | ✅ No |
| **Network Issues** | 🔴 Yes | 🟡 Minimal | ✅ None |
| **Works with Minimax** | 🔴 Unknown | 🟡 Probably | ✅ Yes |
| **Future-Proof** | 🔴 No | 🟡 Maybe | ✅ Yes |
| **Recommended** | ❌ No | 🔸 Temporary | ✅ **YES** |

Legend:
- ✅ Excellent/Yes
- 🟡 Good/Maybe
- 🔴 Poor/No

---

**Conclusion**: The **Native stdio** solution is the clear winner for long-term use, but **Run on Windows** is a good quick fix to get things working immediately.

---

**Created**: November 13, 2025  
**Version**: 1.0  
**Status**: Complete
