# Mini Agent CLI - Quick Reference Card

## 🚀 Quick Start
```bash
cd /c/Project/EX-AI-MCP-Server
mini-agent --workspace .
```

## 📋 Most Common Commands

| Task Type | Example Commands |
|-----------|------------------|
| **Project Analysis** | > Analyze the main.py file<br>> Explain the project architecture<br>> What are the key components? |
| **Docker & System** | > Check container status<br>> View logs from exai-mcp-stdio<br>> Restart failed containers |
| **File Operations** | > Read and summarize README.md<br>> Create PDF from documentation<br>> Convert DOCX to PDF |
| **Code Development** | > Generate unit tests for ws_server<br>> Help optimize the MCP handler<br>> Create new tool template |
| **Documentation** | > Generate API docs as PDF<br>> Create user manual from docs/<br>> Export project status report |

## 🎯 Command Patterns That Work Best

### ✅ Natural Language (Recommended)
```
> "Help me understand this EX-AI MCP Server project"
> "Create a comprehensive PDF report about the current system"
> "Check if all Docker services are healthy"
```

### ✅ Specific Actions
```
> "Analyze src/daemon/ws_server.py for performance issues"
> "Extract all configuration from .env.docker file"
> "Generate unit tests for the MCP protocol handlers"
```

### ✅ Multi-Step Workflows
```
> "First check Docker status, then analyze any errors, finally create a maintenance report"
> "Read README.md, review the tests, and generate development guidelines"
```

## 🛠️ Available Skills

| Skill | Purpose | Example Usage |
|-------|---------|---------------|
| **pdf** | PDF manipulation | > Extract text from manual.pdf<br>> Merge multiple PDFs<br>> Create new PDF report |
| **docx** | Word documents | > Read technical_spec.docx<br>> Create project proposal |
| **pptx** | PowerPoint | > Create presentation from data<br>> Generate slide deck |
| **xlsx** | Excel data | > Export container metrics<br>> Create status dashboard |
| **webapp-testing** | Testing | > Test MCP server endpoints<br>> Run security scans |
| **skill-creator** | Development | > Generate unit tests<br>> Create new MCP tools |

## 🔧 Special Features

### File References
```
✅ Relative paths (from workspace):
  src/daemon/ws_server.py
  docs/api/
  tests/unit/

✅ Absolute paths:
  C:/Project/EX-AI-MCP-Server/config/
  ~/.mini-agent/config/
```

### Docker Integration
```
✅ Your current containers:
  exai-mcp-stdio (MCP server)
  exai-mcp-server (main service)
  exai-redis (database)
  exai-redis-commander (UI)
```

### Environment Variables
```
✅ Accessible variables:
  $MINIMAX_API_KEY
  $EXAI_CONFIG_PATH
  $DOCKER_HOST
```

## 🆘 Quick Troubleshooting

| Problem | Quick Fix |
|---------|-----------|
| API errors | `echo $MINIMAX_API_KEY \| head -c 20` |
| Docker issues | `docker ps \| findstr exai` |
| File access | Check you're in project directory |
| Skill missing | Verify Mini Agent installation |

## 💡 Pro Tips

1. **Be conversational** - Natural language works best
2. **Chain commands** - Build complex workflows
3. **Reference context** - Mention your project/files
4. **Use skills** - Leverage specialized capabilities
5. **Stay specific** - Clear requests get better results

---

**🎉 Ready to try?** Start Mini Agent and ask:
> "What can you help me with for this EX-AI MCP Server project?"

---
*Save this as a quick reference while using Mini Agent CLI*