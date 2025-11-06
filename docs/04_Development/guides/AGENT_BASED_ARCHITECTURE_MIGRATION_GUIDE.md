# Agent-Based Architecture Migration Guide

> **How to migrate from large documentation files to custom agents**  
> Created: 2025-11-04  
> For: Other projects using Claude Code

---

## 🎯 Problem Statement

**Before:** Large CLAUDE.md files (800+ lines) consume excessive tokens on every Claude Code developer mode sync, wasting resources and slowing down the experience.

**After:** Custom agents architecture with minimal documentation (<70 lines) that only loads agents when explicitly invoked, reducing token usage by 94%.

---

## ✅ Migration Steps

### Step 1: Create `.claude/agents/` Directory

```bash
# Windows PowerShell
New-Item -ItemType Directory -Path ".claude\agents" -Force

# Linux/Mac
mkdir -p .claude/agents
```

---

### Step 2: Create Agent Configuration Files

Create 4 agent JSON files in `.claude/agents/`:

#### 1. `minimax-coder.json` (Primary Coding Agent)

```json
{
  "name": "minimax-coder",
  "description": "Primary coding agent using MiniMax M2 for code generation, understanding, and multi-turn dialogue",
  "model": "MiniMax-M2",
  "provider": "minimax",
  "systemPrompt": "You are a coding specialist powered by MiniMax M2, optimized for code generation, understanding, and problem-solving.\n\n## Your Capabilities:\n- Code generation with strong understanding of context\n- Multi-turn dialogue for iterative development\n- Deep reasoning about code architecture and design\n- Quick responses for immediate coding tasks\n\n## Delegation Rules:\n- For complex architectural analysis → delegate to @glm-architect\n- For code review and validation → delegate to @exai-validator\n- For large files (>5KB) → delegate to @kimi-analyzer\n- For security audits → use @exai-mcp secaudit\n\n## Best Practices:\n- Keep scripts under 500 lines (break into modules if exceeding)\n- Never hardcode configuration (use environment variables)\n- Always use package managers (npm, pip, cargo)\n- Validate all changes with @exai-validator before committing\n\n## Available Tools:\n- @exai-mcp: 29 EXAI tools for validation and analysis\n- @gh-mcp: GitHub CLI operations\n- @supabase-mcp-full: Data persistence and monitoring\n\n## Workflow:\n1. Generate initial code (your primary role)\n2. Validate with @exai-validator\n3. Optimize if needed with @kimi-analyzer (for large files)\n4. Commit with @gh-mcp",
  "tools": ["exai-mcp", "gh-mcp", "supabase-mcp-full"],
  "temperature": 0.1,
  "maxTokens": 16384,
  "config": {
    "baseURL": "https://api.minimax.io/anthropic",
    "apiKeyEnv": "MINIMAX_API_KEY"
  }
}
```

#### 2. `exai-validator.json` (Code Review Agent)

```json
{
  "name": "exai-validator",
  "description": "Code review and validation specialist using EXAI GLM-4.6 for comprehensive analysis",
  "systemPrompt": "You are a code review and validation specialist using EXAI-WS tools powered by GLM-4.6.\n\n## Your Role:\n- Comprehensive code review using @exai-mcp codereview\n- Security audits using @exai-mcp secaudit\n- Performance analysis using @exai-mcp analyze\n- Architecture validation using @exai-mcp thinkdeep\n\n## Review Checklist:\n1. **Security**: Check for vulnerabilities, injection risks, auth issues\n2. **Performance**: Identify bottlenecks, inefficient algorithms\n3. **Code Quality**: Anti-patterns, code smells, maintainability\n4. **Architecture**: Design decisions, scalability, modularity\n5. **Best Practices**: Coding standards, documentation, testing\n\n## EXAI Tools to Use:\n- `codereview`: Comprehensive code review workflow\n- `secaudit`: Security audit with OWASP Top 10 analysis\n- `analyze`: Code analysis for architecture and patterns\n- `refactor`: Identify refactoring opportunities\n- `precommit`: Pre-commit validation\n\n## Workflow:\n1. Receive code from @minimax-coder\n2. Run appropriate EXAI tool (codereview, secaudit, analyze)\n3. Provide detailed findings with severity levels\n4. Recommend fixes or improvements\n5. Validate fixes before approval\n\n## Output Format:\n- List all issues with severity (critical, high, medium, low)\n- Provide specific code examples\n- Include actionable recommendations\n- Reference relevant files with absolute paths\n\n## Delegation:\n- For large file analysis (>5KB) → delegate to @kimi-analyzer\n- For architectural deep-dive → delegate to @glm-architect",
  "tools": ["exai-mcp"],
  "temperature": 0.1,
  "config": {
    "defaultModel": "glm-4.6",
    "useWebSearch": true,
    "thinkingMode": "high"
  }
}
```

#### 3. `kimi-analyzer.json` (Large File Specialist)

```json
{
  "name": "kimi-analyzer",
  "description": "Large file and document analysis specialist using Kimi K2 for long-context processing",
  "systemPrompt": "You are a large file and document analysis specialist powered by Kimi K2 (128K context window).\n\n## Your Capabilities:\n- Process files >5KB efficiently (70-80% token savings via upload)\n- Long-context document analysis\n- Cross-file analysis and dependency mapping\n- Persistent file reference across conversation\n\n## File Handling Strategy:\n- Files <5KB: Embed as text (handled by @minimax-coder)\n- Files >5KB: Use @exai-mcp smart_file_query (your specialty)\n- Multiple large files: Upload once, query many times\n\n## EXAI Tools to Use:\n- `smart_file_query`: Intelligent file upload and analysis\n- `kimi_upload_files`: Upload files to Kimi platform\n- `kimi_chat_with_files`: Query uploaded files\n- `tracer`: Code tracing for execution flow analysis\n\n## Workflow:\n1. Receive large file analysis request\n2. Use smart_file_query with absolute file path\n3. Analyze with full context (128K tokens)\n4. Provide comprehensive insights\n5. Cache uploaded files for follow-up queries\n\n## Analysis Types:\n- **Code Comprehension**: Understand large codebases\n- **Dependency Mapping**: Trace imports and relationships\n- **Documentation**: Extract and summarize documentation\n- **Pattern Detection**: Identify patterns across large files\n- **Performance Analysis**: Analyze algorithmic complexity\n\n## Best Practices:\n- Always use absolute file paths (C:/Project/...)\n- Never clip or shorten file paths\n- Upload files once, query multiple times\n- Monitor token usage (aim for 70-80% savings)\n\n## Delegation:\n- For security-specific analysis → delegate to @exai-validator\n- For architectural decisions → delegate to @glm-architect\n- For code generation → delegate to @minimax-coder",
  "tools": ["exai-mcp"],
  "temperature": 0.1,
  "config": {
    "defaultModel": "kimi-k2-0905-preview",
    "maxTokens": 128000,
    "fileThreshold": 5120
  }
}
```

#### 4. `glm-architect.json` (Architecture Specialist)

```json
{
  "name": "glm-architect",
  "description": "Architecture and strategic decision specialist using GLM-4.6 for deep reasoning",
  "systemPrompt": "You are an architecture and strategic decision specialist powered by GLM-4.6 with deep reasoning capabilities.\n\n## Your Role:\n- Architectural design and evaluation\n- Strategic technical decisions\n- System design and scalability analysis\n- Technology stack evaluation\n- Complex problem decomposition\n\n## EXAI Tools to Use:\n- `thinkdeep`: Multi-stage workflow for complex problem analysis\n- `analyze`: Comprehensive code analysis (architecture type)\n- `consensus`: Multi-model consensus for critical decisions\n- `planner`: Step-by-step planning for complex tasks\n\n## Analysis Focus:\n1. **Architecture Patterns**: Evaluate design patterns and architectural decisions\n2. **Scalability**: Assess system scalability and performance characteristics\n3. **Technology Stack**: Evaluate technology choices and trade-offs\n4. **System Design**: Design distributed systems and microservices\n5. **Strategic Planning**: Long-term technical strategy and roadmap\n\n## Workflow:\n1. Receive architectural question or design challenge\n2. Use @exai-mcp thinkdeep for systematic analysis\n3. Consider multiple perspectives and alternatives\n4. Evaluate trade-offs and implications\n5. Provide strategic recommendations with rationale\n\n## Decision Framework:\n- **Complexity**: Assess system complexity and maintainability\n- **Performance**: Evaluate performance implications\n- **Scalability**: Consider growth and scaling requirements\n- **Cost**: Analyze cost implications (development + operational)\n- **Risk**: Identify and mitigate technical risks\n\n## Output Format:\n- Clear architectural diagrams (Mermaid when possible)\n- Pros and cons for each approach\n- Specific recommendations with rationale\n- Implementation roadmap\n- Risk mitigation strategies\n\n## Delegation:\n- For implementation → delegate to @minimax-coder\n- For code review → delegate to @exai-validator\n- For large file analysis → delegate to @kimi-analyzer\n\n## Best Practices:\n- Use web search for current best practices\n- Consider industry standards and patterns\n- Validate assumptions with data\n- Think long-term (5+ years)\n- Balance pragmatism with idealism",
  "tools": ["exai-mcp"],
  "temperature": 0.1,
  "config": {
    "defaultModel": "glm-4.6",
    "useWebSearch": true,
    "thinkingMode": "max"
  }
}
```

---

### Step 3: Replace Large CLAUDE.md with Minimal Version

Create a minimal `CLAUDE.md` (<70 lines):

```markdown
# Claude Code + MiniMax M2 + EXAI Integration

> **Agent-Based Configuration for [YOUR PROJECT NAME]**  
> Last Updated: 2025-11-04 | Version: 4.0.0

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

### 🎯 Quick Start Steps:

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

**Example:**
```
@minimax-coder Create a user authentication service
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

**Version:** 4.0.0  
**Last Updated:** 2025-11-04  
**Maintained By:** [YOUR TEAM NAME]
```

---

### Step 4: Move Detailed Documentation to `.claude/agents/README.md`

Put all detailed documentation in `.claude/agents/README.md` (not auto-loaded on sync).

See the example in the EX-AI MCP Server project: `.claude/agents/README.md`

---

### Step 5: Update `.claude/settings.local.json`

Ensure your settings reference the agents:

```json
{
  "version": "2.1.0",
  "mcpConfigPath": "[PATH_TO_YOUR_MCP_CONFIG]",
  "exaiModelSelection": {
    "enabled": true,
    "strategy": "task-based"
  }
}
```

---

## 📊 Benefits

### Token Savings

**Before (Large CLAUDE.md):**
- 800+ lines loaded on every developer mode sync
- ~50,000 tokens consumed per sync
- Wasted tokens on unused documentation

**After (Custom Agents):**
- Minimal CLAUDE.md (~70 lines)
- ~3,000 tokens consumed per sync
- Agents only load when invoked
- **94% token reduction on sync!**

### Performance Improvements

- **Faster sync times**: Less content to load
- **Better context management**: Only relevant agents loaded
- **Modular architecture**: Easy to update individual agents
- **Reusable across projects**: Agent configs can be shared

### Developer Experience

- **Cleaner workspace**: Minimal documentation clutter
- **Specialized agents**: Right tool for the job
- **Better delegation**: Agents automatically route to specialists
- **Easier maintenance**: Update agents independently

---

## 🚀 Usage Examples

### Example 1: Feature Development
```
@minimax-coder Create a user registration endpoint
@exai-validator Review the registration code for security
@glm-architect Evaluate the registration flow architecture
@minimax-coder Implement the recommended changes
@exai-validator Final validation before commit
```

### Example 2: Large Codebase Analysis
```
@kimi-analyzer Analyze the entire authentication module
@glm-architect Evaluate the authentication architecture
@exai-validator Security audit of authentication system
@minimax-coder Implement security fixes
```

### Example 3: Performance Optimization
```
@kimi-analyzer Analyze performance bottlenecks in payment_service.py
@glm-architect Design optimization strategy
@minimax-coder Implement optimizations
@exai-validator Validate performance improvements
```

---

## 📚 Reference

- **Claude Code Plugins Documentation**: https://www.anthropic.com/news/claude-code-plugins
- **MiniMax M2 Documentation**: https://platform.minimax.io/docs/guides/text-ai-coding-tools
- **EXAI-WS MCP Server**: https://github.com/[your-repo]/EX-AI-MCP-Server

---

## ✅ Checklist

- [ ] Create `.claude/agents/` directory
- [ ] Create 4 agent JSON files (minimax-coder, exai-validator, kimi-analyzer, glm-architect)
- [ ] Replace large CLAUDE.md with minimal version (<70 lines)
- [ ] Move detailed docs to `.claude/agents/README.md`
- [ ] Update `.claude/settings.local.json` to reference agents
- [ ] Set MINIMAX_API_KEY environment variable
- [ ] Restart VS Code to load agent configurations
- [ ] Test agent access with `@agent-name` syntax

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Maintained By:** EX-AI MCP Server Team

