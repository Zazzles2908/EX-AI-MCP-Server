# Claude Code + EXAI Integration

> **Agent-Based Configuration for EX-AI MCP Server v2.3**
> Last Updated: 2025-11-09 | Version: 4.1.0

---

## 🎯 What's Configured

This project uses **custom agents** for optimal Claude Code performance with minimal token usage:

### ✅ What's Already Set Up:
- **GLM-4.6 & Kimi K2 Models** - Enhanced code understanding and reasoning
- **EXAI-WS MCP Server** - 29 AI-powered tools (GLM-4.6, Kimi K2)
- **Intelligent Routing** - Automatic model selection based on task
- **GitHub CLI MCP** - Full git operations
- **Supabase MCP** - Data persistence and monitoring
- **No Permission Prompts** - Everything auto-approved

### 🎯 Quick Start Steps:

1. **Set Environment Variables** (Required for providers):
   ```bash
   # Windows PowerShell
   $env:GLM_API_KEY="your_glm_api_key_here"
   $env:KIMI_API_KEY="your_kimi_api_key_here"

   # Linux/Mac
   export GLM_API_KEY="your_glm_api_key_here"
   export KIMI_API_KEY="your_kimi_api_key_here"
   ```

2. **Open this folder in VSCode**

3. **Start chatting with Claude Code** - GLM-4.6 and Kimi K2 are configured!

4. **Use MCP servers with @-mentions:**
   - `@exai-mcp chat "Analyze my code with GLM-4.6"`
   - `@gh-mcp gh_repo_list`
   - `@supabase-mcp-full list_projects`

---

## 🤖 Custom Agents

Use specialized agents for different tasks:

- **@glm-coder** - Primary coding (GLM-4.6)
- **@exai-validator** - Code review & validation (GLM-4.6)
- **@kimi-analyzer** - Large file analysis (Kimi K2)
- **@glm-architect** - Architecture decisions (GLM-4.6)

**Example:**
```
@glm-coder Create a user authentication service
@exai-validator Review the authentication code for security issues
@kimi-analyzer Analyze auth_service.py for performance optimization
@glm-architect Evaluate the authentication architecture
```

---

## 📚 Documentation

- **Agent Details**: See `.claude/agents/README.md`
- **Configuration Guide**: See `.claude/EXAI_MCP_CONFIGURATION_GUIDE.md`
- **Quick Reference**: See `.claude/QUICK_REFERENCE_EXAI_MODELS.md`

---

**Configuration Status:** ✅ **COMPLETE AND READY TO USE!**

**Version:** 4.1.0
**Last Updated:** 2025-11-09
**Maintained By:** EX-AI MCP Server Team

