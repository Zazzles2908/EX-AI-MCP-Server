# Getting Started with EXAI MCP Server

Welcome! This guide will get you up and running with EXAI MCP Server in minutes.

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
- ✅ Docker Desktop installed and running
- ✅ Python 3.13+ with virtual environment
- ✅ Claude Desktop installed

### 2. Start the Server
```bash
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d
```

### 3. Verify Installation
```bash
# Check Docker containers
docker ps --filter name=exai-mcp-daemon

# Expected output:
# CONTAINER ID   IMAGE              STATUS
# exai-mcp-daemon  exai-mcp-server   Up (healthy)
```

### 4. Test Connection
In Claude Desktop, try:
```
@exai-mcp status
```

You should see:
- ✅ Server version information
- ✅ 21 available tools
- ✅ Provider status (GLM, Kimi)

## 📋 First Steps

### Check Your Configuration
Your `claude_desktop_config.json` should have:
```json
"EXAI_WS_PORT": "3000"
```

**If you see port 8079, update it to 3000!**

### Try Your First Tool
```
@exai-mcp chat "Hello, can you help me?"
```

### Explore Available Tools
```
@exai-mcp status
```

This shows all 21 tools organized by tier:
- **Essential (3)**: status, chat, planner
- **Core (7)**: analyze, codereview, debug, refactor, testgen, thinkdeep, smart_file_query
- **Advanced (7)**: consensus, docgen, secaudit, tracer, precommit, kimi_chat_with_tools, glm_payload_preview
- **Hidden (4)**: Diagnostic and deprecated tools

## 🎯 Common First Commands

### Code Analysis
```
@exai-mcp analyze <file_path>
```

### Code Review
```
@exai-mcp codereview <file_path>
```

### Chat with AI
```
@exai-mcp chat "Explain the difference between async and sync"
```

### File Upload & Analysis
```
@exai-mcp smart_file_query "Analyze this code" <file_path>
```

## ⚙️ Configuration

### Key Settings
```bash
# .env file
EXAI_WS_PORT=3000          # Host port (connects FROM)
EXAI_WS_HOST=127.0.0.1     # Localhost
LEAN_MODE=true             # Show 10 tools by default

# docker-compose.yml
3000:8079                  # Maps host:container
```

### Port Mapping Explained
```
Your Computer (Windows)
    ↓ Port 3000
Docker Container
    ↓ Port 8079
EXAI Daemon
```

## 🔧 Troubleshooting

### Can't Connect?
1. Check Docker: `docker ps`
2. Check port: `netstat -ano | findstr :3000`
3. Restart: `docker-compose restart`

### Tools Not Loading?
1. Check logs: `tail -f logs/ws_shim_*.log`
2. Verify health: `tail -f logs/ws_daemon.log`
3. Restart Claude Desktop

### Port 3000 in Use?
```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill process (replace PID)
taskkill /PID <PID> /F
```

## 📚 Next Steps

### Learn More
- 📖 [Architecture Overview](../architecture/exai-mcp-architecture.md) - Deep dive into how it works
- 🛠️ [Tool Development](../development/tool-development.md) - Create custom tools
- ⚙️ [Configuration Guide](../development/configuration.md) - Advanced settings
- 🔧 [Troubleshooting](../troubleshooting/) - Common issues and solutions

### Advanced Usage
- Use `@exai-mcp analyze` for code analysis
- Use `@exai-mcp codereview` for code reviews
- Use `@exai-mcp debug` for debugging assistance
- Use `@exai-mcp refactor` for code refactoring
- Use `@exai-mcp testgen` for test generation
- Use `@exai-mcp consensus` for multi-model analysis

## 💡 Pro Tips

### 1. File Paths
Use forward slashes or escape backslashes:
```bash
# Good
C:/Project/file.py
C:\\Project\\file.py

# In EXAI tools
@exai-mcp analyze "C:/Project/file.py"
```

### 2. Context
Provide context in your prompts:
```bash
# Vague
"Fix this"

# Clear
"Fix the performance issue in this sorting algorithm"
```

### 3. Iterative Development
Start simple, then ask for improvements:
```bash
1. "Write a function to parse JSON"
2. "Add error handling"
3. "Optimize for large files"
4. "Add unit tests"
```

## 🆘 Getting Help

### Documentation
- 📖 [Main Documentation Hub](../README.md)
- 🏗️ [Architecture Guide](../architecture/exai-mcp-architecture.md)
- 🔧 [Troubleshooting Guide](../troubleshooting/)

### Logs
- Shim logs: `logs/ws_shim_*.log`
- Daemon logs: `logs/ws_daemon.log`
- Native MCP: `logs/exai_native_mcp.log`

### Status Commands
```bash
# Check server status
@exai-mcp status

# Check Docker
docker ps --filter name=exai-mcp-daemon

# Check ports
netstat -ano | findstr :3000
```

## ✅ Success Indicators

You'll know everything is working when:
- ✅ `@exai-mcp status` returns server information
- ✅ `@exai-mcp chat` responds immediately
- ✅ You can see all 21 tools
- ✅ No errors in logs

## 🎉 You're Ready!

Congratulations! You now have EXAI MCP Server running. Start exploring the tools and see how EXAI can enhance your development workflow.

**Happy coding!** 🚀

---

**Next**: [Read the Architecture Guide](../architecture/exai-mcp-architecture.md) to understand how it all works.
