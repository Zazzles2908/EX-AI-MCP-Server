# Claude Code + MiniMax M2 + EXAI Integration

> **Agent-Based Configuration for EX-AI MCP Server v2.3**
> Last Updated: 2025-11-08 | Version: 5.0.0

---

## 🎯 What's Configured

This project uses **custom agents** for optimal Claude Code performance with minimal token usage:

### ✅ What's Already Set Up:
- **MiniMax M2 Model** - Enhanced code understanding and reasoning
- **EXAI-WS MCP Server** - 29 AI-powered tools (GLM-4.6, Kimi K2)
- **Intelligent Routing** - Automatic model selection based on task
- **GitHub CLI MCP** - Full git operations
- **Supabase MCP** - Data persistence and monitoring
- **No Permission Prompts** - Everything auto-approved
- **Centralized Configuration** - Single source of truth to prevent drift
- **Secure Secret Management** - Supabase-backed token storage

---

## 🎓 Best Practices (From Production Experience)

### Core Principles
**ALWAYS use EXAI throughout the entire process** - every interaction should leverage EXAI tools for:
- Code review and validation
- Issue identification and fixing
- Proactive problem-solving
- Continuous quality improvement

### 1. Use EXAI for EVERYTHING
```python
# DON'T just identify issues
# DO use EXAI to find AND fix them
@exai-mcp codereview "Find and fix all JSON parsing issues"
@exai-mcp analyze "Review this codebase for security vulnerabilities"
@exai-mcp refactor "Improve error handling patterns"
```

### 2. Proactive Problem-Solving
- **DON'T:** "I found a bug, you should fix it"
- **DO:** "I found a bug, let me use EXAI to fix it right now"
- **Pattern:** Identify → Use EXAI → Fix → Verify → Document

### 3. Configuration Management
- **Centralized config** in `src/config/settings.py` - single source of truth
- **No hardcoded values** - use config.ws_port, config.ws_host, etc.
- **Prevent drift** - all scripts import from src.config
- **Use secrets manager** - `secrets.get_jwt_token("claude")` not hardcoded tokens

### 4. Security First
- **Zero tolerance** for hardcoded credentials
- **No JWT tokens** in source code
- **No secrets** in console output
- **Use Supabase** for secure storage

### 5. Code Quality Standards
- **JSON parsing** always has try-except blocks
- **Error handling** is comprehensive
- **Imports** are clean and minimal
- **Exit patterns** are consistent (`sys.exit()`)

### 6. Root Directory Organization
- **Maximum 5 files** at root level:
  1. README.md
  2. CONTRIBUTING.md
  3. LICENSE
  4. CHANGELOG.md
  5. CLAUDE.md
- **All other files** in appropriate subdirectories
- **Test files** → `tests/`
- **Documentation** → `docs/`
- **Scripts** → `scripts/`
- **Config** → `config/`

---

## 🎯 Quick Start Steps

### For Development

1. **Set Environment Variables** (Required for MiniMax M2):
   ```bash
   # Windows PowerShell
   $env:MINIMAX_API_KEY="your_api_key_here"
   $env:MINIMAX_BASE_URL="https://api.minimax.io/anthropic"

   # Linux/Mac
   export MINIMAX_API_KEY="your_api_key_here"
   export MINIMAX_BASE_URL="https://api.minimax.io/anthropic"
   ```

2. **Open this folder in VSCode**

3. **Start chatting with Claude Code** - MiniMax M2 is now your primary model!

4. **Use MCP servers with @-mentions:**
   - `@exai-mcp chat "Analyze my code with GLM-4.6"`
   - `@gh-mcp gh_repo_list`
   - `@supabase-mcp-full list_projects`

---

## 🤖 Custom Agents

Use specialized agents for different tasks:

- **@minimax-coder** - Primary coding (MiniMax M2)
- **@exai-validator** - Code review & validation (GLM-4.6)
- **@kimi-analyzer** - Large file analysis (Kimi K2)
- **@glm-architect** - Architecture decisions (GLM-4.6)

**Example Workflow:**
```
@minimax-coder Create a user authentication service
@exai-validator Review the authentication code for security issues
@kimi-analyzer Analyze auth_service.py for performance optimization
@glm-architect Evaluate the authentication architecture
```

---

## 🔧 Development Workflow (The Right Way)

### When Fixing Issues:
1. **Use EXAI to analyze** - "Find all security issues in this codebase"
2. **Use EXAI to fix** - "Fix all JSON parsing error handling"
3. **Verify with EXAI** - "Verify all fixes are complete"
4. **Update documentation** - Document what was fixed

### When Adding Features:
1. **Plan with EXAI** - "Design the architecture for this feature"
2. **Code with EXAI** - "Implement this feature with proper error handling"
3. **Review with EXAI** - "Review this code for quality and security"
4. **Test with EXAI** - "Generate tests for this feature"

### When Reviewing Code:
1. **Start every review** with EXAI: `@exai-mcp codereview "Review this code"`
2. **Fix issues immediately** - don't just report them
3. **Verify fixes** - use EXAI to confirm resolution

---

## 📚 Documentation Structure

- **Agent Details**: See `.claude/agents/README.md`
- **Configuration Guide**: See `docs/CENTRALIZED_CONFIG_GUIDE.md`
- **Script Issues**: See `docs/SCRIPT_ISSUES_FOUND.md`
- **Final Status**: See `docs/reports/FINAL_FIX_STATUS_REPORT.md`
- **Root Reorganization**: See `docs/reports/ROOT_DIRECTORY_REORGANIZATION_REPORT.md`

---

## 🔒 Security Policy

### Zero Tolerance For:
- Hardcoded JWT tokens or API keys
- Credentials in source code
- Secrets in console output
- Missing error handling
- Configuration drift

### Always Use:
- Centralized configuration
- Secrets manager for tokens
- Comprehensive error handling
- EXAI for security review

---

## ✅ Quality Gates

Before marking ANY task complete:
- [ ] Used EXAI for analysis
- [ ] Used EXAI for fixes
- [ ] Verified with EXAI
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Security review passed
- [ ] Documentation updated
- [ ] Tests passing

---

## 📖 Key Learnings From This Session

### What Worked:
1. **EXAI throughout** - Using EXAI for every step was powerful
2. **Centralized config** - Prevented configuration drift
3. **Security-first** - Eliminated all hardcoded credentials
4. **Proactive fixing** - Fixed issues immediately, not later
5. **Documentation** - Created comprehensive reports

### What to Avoid:
1. **Tool misconfigurations** - Always provide required parameters
2. **Ignoring issues** - Fix problems when found
3. **Configuration drift** - Use centralized config
4. **Security vulnerabilities** - No hardcoded secrets
5. **Root pollution** - Keep root directory clean

---

## 🎉 Project Status

### Completed Achievements:
- ✅ 15+ security & quality issues fixed
- ✅ Centralized configuration system
- ✅ Secure secret management
- ✅ JSON error handling added everywhere
- ✅ Root directory reorganized
- ✅ 5-file rule compliance
- ✅ 100% EXAI-powered workflow

**Configuration Status:** ✅ **COMPLETE AND PRODUCTION READY!**

**Version:** 5.0.0
**Last Updated:** 2025-11-08
**Maintained By:** EX-AI MCP Server Team

---

## 💡 The Golden Rule

**"Use EXAI for everything, fix issues immediately, maintain professional standards."**

This isn't just a guideline - it's how we ensure enterprise-grade quality in every interaction.
