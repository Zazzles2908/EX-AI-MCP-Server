# Mini Agent Architecture Understanding Report

## **🔍 COMPLETE MINI AGENT ANALYSIS**

### **ARCHITECTURE OVERVIEW**

Mini Agent is a **local AI agent system** that uses MiniMax M2 API as backend intelligence, enhanced with tool capabilities for filesystem, shell commands, and MCP protocol integration.

### **CORE COMPONENTS DISCOVERED:**

#### **1. Configuration System**
```
C:\Users\Jazeel-Home\.mini-agent\config\
├── config.yaml              # Main Mini-Agent config (user-level)
├── global.yaml             # Global defaults for all projects  
├── .mcp.json               # MCP servers connection config
├── infrastructure.yaml     # EX-AI infrastructure integration
└── supabase.json           # Supabase MCP server config
```

#### **2. MCP Integration Architecture**
```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "docker",
      "args": ["exec", "-i", "exai-mcp-stdio", "python", "-m", "src.daemon.mcp_server", "--mode", "stdio"],
      "env": {...}
    }
  }
}
```

**KEY INSIGHT**: Mini Agent **executes commands inside the EX-AI MCP container** to access tools!

#### **3. Tool System Architecture**
```yaml
tools:
  enable_file_tools: true     # File operations
  enable_bash: true          # Shell commands  
  enable_mcp: true           # MCP protocol
  enable_skills: true        # Claude Skills
  enable_note: true          # Session notes
```

#### **4. System Prompt Integration**
```yaml
system_prompt:
  path: "./system_prompt.md"        # Primary prompt
  fallback_paths:                   # Fallback locations
    - "./prompts.md"
    - "./system_prompt.txt"
  inject_skills_metadata: true      # Auto-inject capabilities
```

### **EX-AI MCP SERVER INTEGRATION**

#### **Connection Method:**
- **Docker-based integration**: Mini Agent runs `docker exec` inside the `exai-mcp-stdio` container
- **STDIO protocol**: Direct communication through containerized MCP server
- **Environment propagation**: Environment variables passed to container

#### **Infrastructure Awareness:**
```yaml
EXAI_INFRASTRUCTURE:
  enabled: true
  auto_discovery: true
  health_check_script: "scripts/system-health.ps1"
  discovery_script: "scripts/infrastructure-discovery.py"
  
  paths:
    project_root: "C:/Project/EX-AI-MCP-Server"
    agent_mcp_config: "C:/Users/Jazeel-Home/.mini-agent/config/mcp.json"
    health_endpoint: "http://127.0.0.1:3002/health"
    websocket_uri: "ws://127.0.0.1:3010"
```

### **CAPABILITY ENHANCEMENT CHAIN**

```
Mini Agent (Local AI Agent)
    ↓ Uses tools (file, bash, notes, skills)
    ↓ Connects to MCP servers (.mcp.json config)
    ↓ Executes commands in containers (docker exec)
    ↓ Accesses EX-AI MCP Server tools
    ↓ Gets AI analysis from MiniMax M2 API
```

### **WORKFLOW UNDERSTANDING**

1. **User starts Mini Agent** (via `launch_mini_agent.bat`)
2. **Mini Agent loads config** from `~/.mini-agent/config/`
3. **Discovers project structure** and available MCP servers
4. **Connects to EX-AI MCP container** via Docker
5. **Routes AI requests through MCP tools** for enhanced capabilities
6. **Returns enhanced responses** combining MiniMax AI + tool execution

### **KEY INSIGHTS FOR PROJECT ORGANIZATION**

#### **Critical Dependencies:**
- **EX-AI MCP Server must be accessible** via Docker container `exai-mcp-stdio`
- **System prompts must be discoverable** by Mini Agent (prompts.md, system_prompt.md)
- **Configuration files must be stable** (.mcp.json, environment variables)

#### **Integration Points:**
- **Workspace directory**: Mini Agent creates `./workspace` for file operations
- **System prompt loading**: Auto-loads from project root or Mini Agent config
- **Tool discovery**: Auto-discovers MCP tools via .mcp.json configuration
- **Health monitoring**: Auto-monitors EX-AI MCP server status

#### **Why Organization Matters:**
- **Mini Agent expects stable paths** for system prompts and configs
- **EX-AI MCP integration depends on container accessibility**
- **Tool discovery requires consistent .mcp.json locations**
- **Infrastructure health checks need predictable project structure**

---

## **🎯 UPDATED ORGANIZATION STRATEGY**

Based on Mini Agent architecture understanding, the organization plan must:

### **Preserve Mini Agent Integration:**
✅ **Keep .mcp.json accessible** (used by both project and Mini Agent)  
✅ **Maintain system prompt files** in discoverable locations  
✅ **Ensure Docker container integration** remains functional  
✅ **Keep environment variables stable** (.env, .env.docker)

### **Enhanced Organization Approach:**
1. **Configuration Centralization** → Move to `/config/` but maintain .mcp.json sync
2. **System Prompt Consolidation** → Keep prompts.md accessible for Mini Agent
3. **Documentation Organization** → Move docs to `/docs/` but preserve system integration
4. **Workspace Compatibility** → Ensure Mini Agent can still discover tools and prompts

### **Updated File Organization Plan:**
```
BEFORE (Chaos):
Root/ (44 scattered files)

AFTER (Organized):
├── src/                    # Core implementation  
├── tools/                  # Tool implementations
├── docs/                   # Essential documentation
├── config/                 # Configuration files
│   ├── .mcp.json          # MCP config (synchronized with Mini Agent)
│   ├── .env               # Environment variables
│   └── ... (other configs)
├── scripts/               # Utility scripts
└── 8 essential files in root (README, docker-compose, etc.)
```

---

## **💡 STRATEGIC IMPLICATIONS**

### **Why This Understanding Changes Everything:**

1. **EX-AI MCP Server is NOT standalone** - it's part of a Mini Agent ecosystem
2. **File organization affects Mini Agent discovery** - can't break tool loading
3. **System prompts must remain discoverable** - critical for Mini Agent operation
4. **Configuration synchronization required** - .mcp.json must match between project and Mini Agent

### **Optimized Improvement Approach:**

1. **Preserve Integration First** - Ensure Mini Agent connectivity
2. **Organize Within Constraints** - Move files but maintain accessibility
3. **Use Mini Agent to Optimize EX-AI MCP** - Leverage the integration for improvements
4. **Validate Tool Discovery** - Ensure all tools remain accessible post-organization

---

## **🏆 CONCLUSION**

**Mini Agent is the master orchestrator** that connects to EX-AI MCP Server through Docker containers to provide enhanced AI capabilities. 

**The EX-AI MCP Server is a specialized tool provider** that Mini Agent leverages for advanced AI analysis, file operations, and system diagnostics.

**Organization must preserve this relationship** while cleaning up the codebase for better maintainability.

**This explains why the tools work when properly configured** - Mini Agent provides the intelligent routing and context, while EX-AI MCP provides the specialized tools and AI analysis capabilities.
