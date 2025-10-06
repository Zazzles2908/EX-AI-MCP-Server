# Quick Start Guide
**Last Updated:** 2025-10-04  
**For:** New users and developers

---

## 🚀 GET STARTED IN 5 MINUTES

### Prerequisites
- Python 3.8+
- API keys for Kimi (Moonshot) and/or GLM (ZhipuAI)
- Windows, macOS, or Linux

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure environment:**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
KIMI_API_KEY=your_kimi_api_key_here
GLM_API_KEY=your_glm_api_key_here
```

**4. Start the server:**

**Windows:**
```powershell
.\scripts\ws_start.ps1
```

**Linux/macOS:**
```bash
./scripts/ws_start.sh
```

**5. Verify it's running:**
```bash
# Server should be running on ws://127.0.0.1:8765
# Check logs in logs/mcp_server.log
```

---

## 💡 FIRST STEPS

### Test the Server

**1. Use the chat tool:**
```python
# Example: Simple chat
{
  "tool": "chat",
  "prompt": "Hello! Can you help me understand this codebase?",
  "model": "auto"
}
```

**2. Try web search:**
```python
# Example: Web search with Kimi
{
  "tool": "chat",
  "prompt": "What's the latest news about AI?",
  "model": "kimi-k2-0905-preview",
  "use_websearch": true
}
```

**3. Analyze code:**
```python
# Example: Code analysis
{
  "tool": "analyze",
  "step": "Analyze the authentication system",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Starting analysis of auth system"
}
```

### Available Tools

**Workflow Tools:**
- `analyze` - Code analysis and architecture review
- `debug` - Bug hunting and root cause analysis
- `refactor` - Refactoring analysis and recommendations
- `codereview` - Comprehensive code review
- `precommit` - Pre-commit validation
- `secaudit` - Security audit
- `testgen` - Test generation
- `docgen` - Documentation generation
- `tracer` - Code tracing and dependency mapping

**Simple Tools:**
- `chat` - General chat and Q&A
- `thinkdeep` - Deep investigation and reasoning
- `planner` - Step-by-step planning
- `consensus` - Multi-model consensus
- `challenge` - Critical analysis
- `listmodels` - List available models

### Common Tasks

**Task: Analyze a file**
```python
{
  "tool": "analyze",
  "step": "Analyze src/providers/glm_chat.py for code quality",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Analyzing GLM chat provider implementation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\glm_chat.py"]
}
```

**Task: Debug an issue**
```python
{
  "tool": "debug",
  "step": "Investigate why web search is failing",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Starting investigation of web search failure",
  "hypothesis": "May be related to API configuration"
}
```

**Task: Generate tests**
```python
{
  "tool": "testgen",
  "step": "Generate tests for text_format_handler.py",
  "step_number": 1,
  "total_steps": 1,
  "next_step_required": false,
  "findings": "Analyzing text format handler for test generation",
  "relevant_files": ["c:\\Project\\EX-AI-MCP-Server\\src\\providers\\text_format_handler.py"]
}
```

---

## 📚 LEARN MORE

### Documentation
- **README.md** - Project overview
- **CURRENT_STATUS.md** - Current project status
- **DOCUMENTATION_INDEX.md** - Complete documentation index
- **docs/guides/** - User guides and tutorials
- **docs/system-reference/** - Architecture documentation

### Configuration

**Environment Variables:**
```bash
# API Configuration
KIMI_API_KEY=your_key
KIMI_API_URL=https://api.moonshot.ai/v1
GLM_API_KEY=your_key
GLM_API_URL=https://api.z.ai/api/paas/v4/

# Feature Flags
KIMI_ENABLE_INTERNET_SEARCH=true
GLM_ENABLE_WEB_BROWSING=true

# File Handling
EX_ALLOW_RELATIVE_PATHS=true
TEST_FILES_DIR=c:\Project\EX-AI-MCP-Server
```

**Model Selection:**
- `auto` - Automatic model selection (recommended)
- `kimi-k2-0905-preview` - Kimi flagship model (200K context)
- `glm-4.6` - GLM flagship model (200K context)
- `glm-4.5-flash` - Fast GLM model (128K context)

### Troubleshooting

**Server won't start:**
1. Check API keys in .env
2. Verify Python version (3.8+)
3. Check logs in logs/mcp_server.log
4. Ensure port 8765 is available

**Web search not working:**
1. Verify API keys are correct
2. Check KIMI_ENABLE_INTERNET_SEARCH=true
3. Check GLM_ENABLE_WEB_BROWSING=true
4. Use kimi-k2-0905-preview for most reliable web search

**Tool errors:**
1. Check file paths are absolute (or EX_ALLOW_RELATIVE_PATHS=true)
2. Verify required fields are provided
3. Check logs for detailed error messages
4. See docs/guides/ for tool-specific guides

---

## 🎯 NEXT STEPS

1. **Explore the codebase:**
   - Use `analyze` tool to understand architecture
   - Use `tracer` tool to map dependencies
   - Read docs/system-reference/ for design docs

2. **Try different tools:**
   - Test each workflow tool with sample code
   - Experiment with different models
   - Try web search with various queries

3. **Read the guides:**
   - docs/guides/web-search-guide.md
   - docs/guides/tool-usage-guide.md
   - docs/system-reference/README.md

4. **Join the community:**
   - Report issues on GitHub
   - Contribute improvements
   - Share your use cases

---

## 💬 GET HELP

**Documentation:**
- Check DOCUMENTATION_INDEX.md for all docs
- See docs/guides/ for how-to guides
- Read docs/system-reference/ for technical details

**Issues:**
- Check logs/mcp_server.log for errors
- See CURRENT_STATUS.md for known issues
- Report bugs on GitHub

**Questions:**
- Use the `chat` tool to ask questions
- Check existing documentation first
- Ask in community channels

---

**Welcome to EX-AI-MCP-Server!** 🎉

Start exploring and building amazing AI-powered applications!

