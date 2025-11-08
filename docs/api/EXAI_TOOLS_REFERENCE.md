# EXAI Tools Reference
**21 AI-Powered Development Tools Available via MCP**

---

## 📋 Available Tools

### 🔍 Analysis & Investigation
1. **analyze** - Comprehensive code analysis with expert validation
2. **debug** - Debug & root cause analysis with structured workflow
3. **thinkdeep** - Multi-stage investigation & reasoning for complex problems

### 💬 Chat & Communication
4. **chat** - General chat with AI (GLM-4.6, Kimi K2)
5. **kimi_chat_with_tools** - Kimi chat with tool capabilities
6. **kimi_intent_analysis** - Classify user prompts and route intelligently

### 🔎 Code Review & Quality
7. **codereview** - Comprehensive code review with expert validation
8. **secaudit** - Security audit (OWASP, compliance, vulnerabilities)
9. **refactor** - Refactoring analysis (code smells, modernization)

### 📚 Documentation & Generation
10. **docgen** - Comprehensive code documentation generation
11. **testgen** - Comprehensive test generation with edge cases

### 🏗️ Architecture & Planning
12. **planner** - Interactive sequential planning for complex tasks
13. **consensus** - Multi-model consensus for decision making
14. **precommit** - Pre-commit validation with expert analysis
15. **tracer** - Step-by-step code tracing (execution flow, dependencies)

### ⚡ Utilities & Management
16. **status** - EXAI server status and health check
17. **version** - Version info and configuration details
18. **listmodels** - List available AI models
19. **glm_payload_preview** - Preview GLM chat completions payload
20. **smart_file_query** - Unified file upload and query
21. **kimi_manage_files** - Manage Kimi uploaded files

---

## 🚀 Quick Start Examples

### Code Review
```
@exai-mcp codereview "Review this authentication service for security issues"
```

### Debugging
```
@exai-mcp debug "I'm getting a connection timeout error in the WebSocket client"
```

### Documentation
```
@exai-mcp docgen "Generate documentation for the storage_manager.py module"
```

### Test Generation
```
@exai-mcp testgen "Create tests for the user authentication flow"
```

### Security Audit
```
@exai-mcp secaudit "Audit this API endpoint for OWASP Top 10 vulnerabilities"
```

### Planning
```
@exai-mcp planner "Plan the implementation of a microservices architecture"
```

### File Analysis
```
@exai-mcp smart_file_query "Analyze the performance of this database query"
```

### Chat with Tools
```
@exai-mcp kimi_chat_with_tools "Help me refactor this legacy codebase"
```

---

## 💡 Usage Tips

### 1. Be Specific
The more context you provide, the better the results:
- Include file paths
- Describe the problem clearly
- Mention expected vs actual behavior

### 2. Use the Right Tool
- **Code Review**: Use `codereview` for code quality
- **Security**: Use `secaudit` for security analysis
- **Debugging**: Use `debug` for error investigation
- **Documentation**: Use `docgen` for code docs
- **Tests**: Use `testgen` for test coverage

### 3. Multi-Step Workflows
Some tools support multi-step analysis:
- `analyze` → `codereview` → `testgen`
- `debug` → `thinkdeep` → `planner`

### 4. File Context
Many tools can analyze files. Just mention the file path in your request.

---

## 🔧 Integration Examples

### VSCode Integration
In any VSCode chat window, simply type:
```
@exai-mcp [tool-name] [your request]
```

Examples:
```
@exai-mcp chat "Explain async/await in Python"
@exai-mcp debug "Why is my Docker container crashing?"
@exai-mcp refactor "Optimize this database schema"
```

### Claude Desktop Integration
Same syntax in Claude Desktop with the EXAI MCP server configured.

---

## 📊 Tool Categories

| Category | Tools | Best For |
|----------|-------|----------|
| **Analysis** | analyze, debug, thinkdeep | Investigation, problem solving |
| **Review** | codereview, refactor, precommit | Code quality, improvements |
| **Security** | secaudit | Vulnerability assessment |
| **Documentation** | docgen, testgen | Docs and tests |
| **Planning** | planner, consensus | Architecture decisions |
| **Utilities** | status, version, listmodels | System info |
| **File Ops** | smart_file_query, kimi_manage_files | File analysis |

---

## 🎯 What Each Tool Does

### Core Tools

**chat** - General conversational AI with access to:
- GLM-4.6 (fast, general purpose)
- Kimi K2 (large context, file analysis)
- Web search capabilities
- Multiple thinking modes

**analyze** - Structured code analysis with:
- Expert validation
- Architecture assessment
- Performance evaluation
- Security analysis

**debug** - Root cause analysis for:
- Bugs and errors
- Performance issues
- Race conditions
- Memory leaks

### Specialized Tools

**codereview** - Code quality assessment:
- Bug detection
- Security issues
- Performance problems
- Code smells

**secaudit** - Security assessment:
- OWASP Top 10 analysis
- Authentication/authorization review
- Input validation gaps
- Compliance checking

**docgen** - Documentation generation:
- API documentation
- Code comments
- Call flow diagrams
- Complexity analysis

**testgen** - Test suite generation:
- Unit tests
- Integration tests
- Edge cases
- Mock strategies

---

## ⚙️ Advanced Usage

### Streaming Responses
Most tools support streaming for real-time feedback:
- Progress updates
- Partial results
- Long-running tasks

### File Upload
Tools like `smart_file_query` and `kimi_chat_with_tools` can:
- Upload files up to 100MB
- Analyze code, documents, images
- Query with file context

### Web Search
Enabled tools can:
- Search current documentation
- Find best practices
- Research solutions
- Verify information

---

## 📚 Documentation

For detailed information on any tool:
- Check tool descriptions in VSCode MCP panel
- Review tool source code in `tools/` directory
- Use `status` tool to get server info

---

## 🆘 Getting Help

If tools aren't working:
1. Check server status: `@exai-mcp status`
2. Verify connection: Check VSCode Output panel
3. Review logs: Check `logs/ws_shim_*.log`
4. Test manually: Use WebSocket tools

---

**All 21 tools are now ready to use!** 🎉

Start with `@exai-mcp chat "Hello"` to test the connection, then explore the other tools based on your needs.
