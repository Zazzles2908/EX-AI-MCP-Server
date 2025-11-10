# Custom Agents for Claude Code

> **Detailed documentation for agent-based architecture**  
> Last Updated: 2025-11-04

---

## 🎯 Overview

This project uses **custom agents** to optimize Claude Code performance and minimize token usage. Instead of loading massive documentation files on every sync, agents are only loaded when explicitly invoked.

---

## 🤖 Available Agents

### 1. @glm-coder (Primary Coding Agent)

**Model:** GLM-4.6  
**Purpose:** Code generation, understanding, and multi-turn dialogue  
**Configuration:** `.claude/agents/glm-coder.json`

**When to Use:**
- Writing new code
- Refactoring existing code
- Quick bug fixes
- Iterative development
- General coding tasks

**Capabilities:**
- Strong code understanding and context awareness
- Multi-turn dialogue for iterative development
- Fast response times
- Deep reasoning about code architecture

**Delegation Rules:**
- Complex architectural analysis → @glm-architect
- Code review and validation → @exai-validator
- Large files (>5KB) → @kimi-analyzer
- Security audits → @exai-validator

**Example Usage:**
```
@glm-coder Create a REST API endpoint for user authentication
@glm-coder Refactor the payment processing module
@glm-coder Fix the bug in auth_service.py line 42
```

---

### 2. @exai-validator (Code Review & Validation)

**Model:** GLM-4.6 (via EXAI-WS)  
**Purpose:** Comprehensive code review, security audits, validation  
**Configuration:** `.claude/agents/exai-validator.json`

**When to Use:**
- Code review before committing
- Security vulnerability scanning
- Performance analysis
- Architecture validation
- Pre-commit validation

**EXAI Tools Used:**
- `codereview` - Comprehensive code review workflow
- `secaudit` - Security audit with OWASP Top 10 analysis
- `analyze` - Code analysis for architecture and patterns
- `refactor` - Identify refactoring opportunities
- `precommit` - Pre-commit validation

**Review Checklist:**
1. **Security**: Vulnerabilities, injection risks, auth issues
2. **Performance**: Bottlenecks, inefficient algorithms
3. **Code Quality**: Anti-patterns, code smells, maintainability
4. **Architecture**: Design decisions, scalability, modularity
5. **Best Practices**: Coding standards, documentation, testing

**Example Usage:**
```
@exai-validator Review auth_service.py for security issues
@exai-validator Validate the payment processing architecture
@exai-validator Run pre-commit validation on all changes
```

---

### 3. @kimi-analyzer (Large File Specialist)

**Model:** Kimi K2 (128K context window)  
**Purpose:** Large file and document analysis  
**Configuration:** `.claude/agents/kimi-analyzer.json`

**When to Use:**
- Analyzing files >5KB
- Long-context document analysis
- Cross-file dependency mapping
- Processing multiple large files
- Persistent file reference across conversation

**File Handling Strategy:**
- Files <5KB: Handled by @minimax-coder (embed as text)
- Files >5KB: Use @kimi-analyzer (70-80% token savings)
- Multiple large files: Upload once, query many times

**EXAI Tools Used:**
- `smart_file_query` - Intelligent file upload and analysis
- `kimi_upload_files` - Upload files to Kimi platform
- `kimi_chat_with_files` - Query uploaded files
- `tracer` - Code tracing for execution flow analysis

**Analysis Types:**
- Code comprehension for large codebases
- Dependency mapping and tracing
- Documentation extraction and summarization
- Pattern detection across large files
- Performance and complexity analysis

**Example Usage:**
```
@kimi-analyzer Analyze C:/Project/EX-AI-MCP-Server/src/large_module.py
@kimi-analyzer Map dependencies for the entire authentication system
@kimi-analyzer Extract documentation from all API files
```

---

### 4. @glm-architect (Architecture & Strategy)

**Model:** GLM-4.6 (via EXAI-WS)  
**Purpose:** Architectural design, strategic decisions, system design  
**Configuration:** `.claude/agents/glm-architect.json`

**When to Use:**
- Architectural design and evaluation
- Strategic technical decisions
- System design and scalability analysis
- Technology stack evaluation
- Complex problem decomposition

**EXAI Tools Used:**
- `thinkdeep` - Multi-stage workflow for complex problem analysis
- `analyze` - Comprehensive code analysis (architecture type)
- `consensus` - Multi-model consensus for critical decisions
- `planner` - Step-by-step planning for complex tasks

**Analysis Focus:**
1. **Architecture Patterns**: Design patterns and architectural decisions
2. **Scalability**: System scalability and performance characteristics
3. **Technology Stack**: Technology choices and trade-offs
4. **System Design**: Distributed systems and microservices
5. **Strategic Planning**: Long-term technical strategy and roadmap

**Decision Framework:**
- **Complexity**: System complexity and maintainability
- **Performance**: Performance implications
- **Scalability**: Growth and scaling requirements
- **Cost**: Development + operational costs
- **Risk**: Technical risks and mitigation

**Example Usage:**
```
@glm-architect Evaluate microservices vs monolith for our system
@glm-architect Design a scalable authentication architecture
@glm-architect Should we use Redis or Memcached for caching?
```

---

## 🔄 Workflow Examples

### Example 1: Feature Development
```
1. @minimax-coder Create a user registration endpoint
2. @exai-validator Review the registration code for security
3. @glm-architect Evaluate the registration flow architecture
4. @minimax-coder Implement the recommended changes
5. @exai-validator Final validation before commit
```

### Example 2: Large Codebase Analysis
```
1. @kimi-analyzer Analyze the entire authentication module
2. @glm-architect Evaluate the authentication architecture
3. @exai-validator Security audit of authentication system
4. @minimax-coder Implement security fixes
```

### Example 3: Performance Optimization
```
1. @kimi-analyzer Analyze performance bottlenecks in payment_service.py
2. @glm-architect Design optimization strategy
3. @minimax-coder Implement optimizations
4. @exai-validator Validate performance improvements
```

---

## 📊 Token Optimization

### Why Agents?

**Before (Large CLAUDE.md):**
- 800+ lines loaded on every developer mode sync
- ~50,000 tokens consumed per sync
- Wasted tokens on unused documentation

**After (Custom Agents):**
- Minimal CLAUDE.md (~70 lines)
- ~3,000 tokens consumed per sync
- Agents only load when invoked
- **94% token reduction on sync!**

### Best Practices:

1. **Use the right agent for the task**
   - Coding → @minimax-coder
   - Review → @exai-validator
   - Large files → @kimi-analyzer
   - Architecture → @glm-architect

2. **Chain agents for complex workflows**
   - Generate code with @minimax-coder
   - Validate with @exai-validator
   - Optimize with @glm-architect

3. **Leverage agent delegation**
   - Agents automatically delegate to specialists
   - No need to manually switch agents

4. **Monitor token usage**
   - Check token consumption in Claude Code
   - Optimize by using appropriate agents

---

## 🔧 Configuration

### Agent Configuration Files

All agents are defined in `.claude/agents/` directory:

```
.claude/agents/
├── minimax-coder.json       # Primary coding agent
├── exai-validator.json      # Code review agent
├── kimi-analyzer.json       # Large file specialist
├── glm-architect.json       # Architecture decisions
└── README.md                # This file
```

### Settings Configuration

Main configuration in `.claude/settings.local.json`:

```json
{
  "version": "2.1.0",
  "mcpConfigPath": "C:/Project/EX-AI-MCP-Server/project-template/.mcp.json",
  "exaiModelSelection": {
    "enabled": true,
    "strategy": "task-based"
  }
}
```

### MCP Configuration

MCP servers configured in `project-template/.mcp.json`:

- **exai-mcp**: EXAI-WS MCP Server (29 AI tools)
- **gh-mcp**: GitHub CLI operations
- **supabase-mcp-full**: Data persistence and monitoring
- **claude-enhancements**: Additional Claude Code enhancements

---

## 🚀 Getting Started

1. **Restart VS Code** to load agent configurations

2. **Test agent access:**
   ```
   @minimax-coder Hello! Can you help me with coding?
   @exai-validator Can you review code?
   @kimi-analyzer Can you analyze large files?
   @glm-architect Can you help with architecture?
   ```

3. **Start using agents in your workflow!**

---

## 📚 Additional Resources

- **EXAI Configuration Guide**: `.claude/EXAI_MCP_CONFIGURATION_GUIDE.md`
- **Quick Reference**: `.claude/QUICK_REFERENCE_EXAI_MODELS.md`
- **Configuration Summary**: `.claude/CONFIGURATION_UPDATE_SUMMARY.md`
- **MiniMax M2 Documentation**: https://platform.minimax.io/docs/guides/text-ai-coding-tools

---

**Version:** 4.0.0  
**Last Updated:** 2025-11-04  
**Maintained By:** EX-AI MCP Server Team

