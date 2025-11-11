# Claude Code + EX-AI with MiniMax M2

> **Full Power Configuration for MiniMax M2 Model**  >
> Optimized for coding and agentic workflows  >
> Last Updated: 2025-11-11

---

## 🚀 What's Configured

### **MiniMax M2 Integration**
- **Model**: MiniMax M2 (10B active / 230B total parameters)
- **Optimized for**: Multi-file edits, coding-run-fix loops, long-horizon toolchains
- **Performance**: #1 ranked open-source model for coding tasks
- **Thinking**: Interleaved thinking with `<think>...</think>` tags
- **Tool Calling**: Full support for complex workflows

### **MCP Servers Available**
- **exai-mcp**: 29 AI-powered tools with intelligent routing (GLM-4.6, Kimi K2, MiniMax M2)
- **git-mcp**: Full git operations
- **supabase-mcp-full**: Database management and Supabase tools

### **Recommended Inference Settings**
```json
{
  "temperature": 1.0,
  "top_p": 0.95,
  "top_k": 40,
  "max_tokens": 16384
}
```

---

## ⚡ Quick Start

### **1. Environment is Pre-Configured** ✅
All environment variables are set in `.env`:
- `GLM_API_KEY` ✅
- `KIMI_API_KEY` ✅
- `MINIMAX_M2_KEY` ✅ (from .env and .env.docker)

### **2. Port Configuration**
- **Claude Code connects to**: 127.0.0.1:3010
- **WebSocket daemon**: Running on port 3010 (local dev)
- **Docker daemon**: Runs on port 8079 (separate container)

### **3. Start Using**
Just open VSCode in this directory - everything auto-connects!

---

## 🎯 MiniMax M2 Capabilities

### **Advanced Coding Features**
- **Multi-file edits**: Understands and modifies entire codebases
- **Compile-run-fix loops**: Autonomous debugging and repair
- **Test-validated repairs**: Creates and runs tests to verify fixes
- **Long-horizon toolchains**: Plans and executes complex workflows

### **Thinking Mode** 🧠
- MiniMax M2 uses interleaved thinking: `<think>...</think>`
- **CRITICAL**: These thinking tags MUST be preserved in conversation history
- Removing them degrades performance significantly
- Model provides transparent reasoning process

### **Best Use Cases**
1. **Large codebase analysis** - Understands complex architectures
2. **Refactoring projects** - Safe, methodical code changes
3. **Bug fixing** - Reproduces, fixes, and tests fixes
4. **Test generation** - Creates comprehensive test suites
5. **Code review** - Deep, intelligent analysis

---

## 🛠️ Available Tools

### **Via @-mentions**
```
@exai-mcp chat "Explain this codebase architecture"
@exai-mcp analyze "Review this code for security issues"
@exai-mcp refactor "Improve this function"
@exai-mcp test "Generate tests for this module"

@git-mcp gh_repo_list
@git-mcp gh_branch_create

@supabase-mcp-full list_projects
@supabase-mcp-full get_project
```

### **Direct Tool Calls**
```
/exai_chat - Chat with AI models (GLM, Kimi, MiniMax M2)
/exai_analyze - Deep code analysis
/exai_web_search - Web search integration
/exai_vision - Image analysis
```

---

## 🏗️ Agent Workflow

### **Specialized Agents Available**
- **@glm-coder** - Primary coding (GLM-4.6)
- **@exai-validator** - Code review & validation
- **@kimi-analyzer** - Large file analysis (Kimi K2)
- **@glm-architect** - Architecture decisions

### **Routing Intelligence**
- **Smart routing** using MiniMax M2 for optimal model selection
- **Cache**: 5-minute TTL for routing decisions
- **Fallback**: Automatic fallback if MiniMax M2 unavailable
- **Cost optimization**: Balance performance and cost

---

## 📋 MiniMax M2 Configuration

### **Environment Variables** (from .env)
```bash
MINIMAX_M2_KEY=eyJhbGciOi...  # JWT token
MINIMAX_ENABLED=true
MINIMAX_TIMEOUT=5
MINIMAX_RETRY=2
```

### **Recommended Usage Patterns**

#### **1. Standard Coding Task**
```python
@glm-coder Write a user authentication service
```
Uses GLM for fast, practical coding

#### **2. Complex Refactoring**
```python
@kimi-analyzer Analyze auth_service.py for improvement opportunities
```
Uses Kimi K2 for deep analysis

#### **3. Architecture Decisions**
```python
@glm-architect Design a microservices architecture for this project
```
Uses GLM for architectural patterns

#### **4. Multi-step Workflow**
```python
@exai-mcp chat "Create a complete CI/CD pipeline with tests"
```
Uses intelligent routing to select best model for each step

---

## 🔧 Troubleshooting

### **Connection Issues**
```bash
# Check if WebSocket is running
tail -f logs/ws_daemon.log

# Check health
cat logs/ws_daemon.health.json

# Restart if needed
python scripts/ws/run_ws_daemon.py
```

### **MiniMax M2 Not Working**
1. Check `MINIMAX_M2_KEY` in `.env`
2. Verify network connectivity to MiniMax API
3. Check logs for routing errors

### **Performance Issues**
- MiniMax M2 is optimized for complex tasks
- For simple tasks, GLM/Kimi may be faster
- Routing cache helps with repeated decisions

---

## 📊 Performance

### **Benchmarks**
- **Terminal-Bench**: 46.3
- **SWE-bench Verified**: 69.4
- **BrowseComp**: 44
- **Artificial Analysis**: #1 (score: 61)

### **Resource Usage**
- **Active parameters**: 10B (efficient for real-time use)
- **Memory**: Lower than full 230B models
- **Latency**: Optimized for agent workflows
- **Throughput**: High concurrent runs

---

## 🎓 Best Practices

### **Working with MiniMax M2**

1. **Respect the thinking** - Don't truncate `<think>...</think>` tags
2. **Use for complexity** - Best for multi-file, long-horizon tasks
3. **Chain workflows** - Break complex tasks into steps
4. **Validate outputs** - Use tests to verify changes
5. **Leverage routing** - Let MiniMax choose optimal models

### **Code Quality**
- ✅ Follow patterns from Linux Kernel, Kubernetes
- ✅ Use EXAI for all analysis, fixes, verification
- ✅ Maintain 80%+ test coverage
- ✅ No TODO/FIXME comments
- ✅ Professional A+ grade standards

---

## 📁 File Structure

```
c:\Project\EX-AI-MCP-Server\
├── .claude/                     # Claude Code configuration
│   ├── CLAUDE.md               # This file
│   ├── .mcp.json              # MCP server config
│   └── agents/                 # Custom agents
├── .env                        # Local development config
├── .env.docker                 # Docker container config
├── src/                        # Source code
├── tools/                      # Tool implementations
└── scripts/                    # Scripts
```

---

## 🔐 Security

- **No hardcoded credentials** - All in `.env` files
- **JWT tokens** - Used for WebSocket authentication
- **Environment isolation** - Dev (3010) vs Docker (8079) separation
- **API keys** - Stored in environment variables only

---

## 🎉 Ready to Go!

**Status**: ✅ Fully Configured  >
**Models**: GLM-4.6, Kimi K2, MiniMax M2  >
**Tools**: 29 AI-powered tools  >
**Routing**: Intelligent MiniMax M2-based selection  >
**Performance**: #1 ranked open-source coding model

**Just start coding with @-mentions - everything auto-connects!** 🚀

---

**Configuration Version**: 6.0.0  >
**Last Updated**: 2025-11-11  >
**MiniMax M2**: Enabled & Optimized
