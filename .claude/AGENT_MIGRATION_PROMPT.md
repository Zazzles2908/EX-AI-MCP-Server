# Agent-Based Architecture Migration Prompt

> **Reusable prompt for migrating any project to optimized Claude Code agent format**  
> Created: 2025-11-04  
> Version: 1.0.0

---

## 📋 **PROMPT FOR OTHER PROJECT**

Copy the entire section below and paste it into your other project's AI assistant (MiniMax M2, Claude, or any AI):

---

### **🎯 MIGRATION TASK: Convert to Agent-Based Architecture**

I need you to migrate this project from documentation-heavy Claude Code configuration to an optimized **agent-based architecture** that reduces token usage by 94%.

**Current Problem:**
- Large CLAUDE.md or .claude/claude.md files (500+ lines)
- Consumes ~50,000 tokens on every Claude Code developer mode sync
- Inefficient for multi-agent workflows

**Target Architecture:**
- Custom agents in `.claude/agents/` directory (JSON format)
- Minimal CLAUDE.md (< 100 lines) - just quick start guide
- Agents only load when invoked with `@agent-name`
- Token usage reduced to ~3,000 per sync (94% reduction)

---

### **📁 STEP 1: Create Agent Definitions**

Create these 4 agent files in `.claude/agents/` directory:

#### **1. Primary Coder Agent**

**File:** `.claude/agents/minimax-coder.json`

```json
{
  "name": "minimax-coder",
  "description": "Primary coding agent using MiniMax M2 for implementation tasks",
  "model": "MiniMax-M2",
  "provider": "minimax",
  "systemPrompt": "You are a senior software engineer specialized in [YOUR_TECH_STACK]. Focus on:\n\n- Writing clean, maintainable code\n- Following project conventions and style guides\n- Providing complete, working implementations\n- Using inline comments only for complex logic\n- Breaking large tasks into focused, incremental changes\n\nProject Context: [YOUR_PROJECT_DESCRIPTION]\n\nKey Technologies: [YOUR_FRAMEWORKS]\n\nCoding Standards:\n- [YOUR_STANDARD_1]\n- [YOUR_STANDARD_2]\n- [YOUR_STANDARD_3]",
  "tools": ["exai-mcp", "gh-mcp", "supabase-mcp-full"],
  "temperature": 0.1,
  "maxTokens": 16384,
  "config": {
    "baseURL": "https://api.minimax.io/anthropic",
    "apiKeyEnv": "MINIMAX_API_KEY"
  },
  "capabilities": [
    "code_generation",
    "refactoring",
    "bug_fixes",
    "feature_implementation"
  ],
  "usage": "Use @minimax-coder for all coding tasks, feature implementation, and refactoring"
}
```

#### **2. Code Review Agent**

**File:** `.claude/agents/exai-validator.json`

```json
{
  "name": "exai-validator",
  "description": "Code review and validation specialist using GLM-4.6 via EXAI",
  "model": "glm-4.6",
  "provider": "exai",
  "systemPrompt": "You are a senior code reviewer with expertise in:\n\n- Security best practices for [YOUR_DOMAIN]\n- Code quality and maintainability\n- Performance optimization\n- Documentation standards\n- Type safety and static analysis\n\nReview Checklist:\n1. **Type Hints**: Complete type annotations\n2. **Docstrings**: [YOUR_DOCSTRING_STYLE] with Args, Returns, Raises\n3. **Error Handling**: Comprehensive try-except with specific exceptions\n4. **Security**: No hardcoded secrets, proper input validation\n5. **Performance**: Profiling data for critical paths\n6. **Testing**: Unit tests with >80% coverage\n7. **Documentation**: README and inline comments for complex logic\n\nCode Quality Standards:\n- [YOUR_LANGUAGE] [VERSION]+ with strict type checking\n- Formatting: [YOUR_FORMATTER] (line length [YOUR_LINE_LENGTH])\n- Linting: [YOUR_LINTER]\n- [YOUR_ASYNC_PATTERN] for I/O operations\n\nProvide specific, actionable feedback with code examples.",
  "tools": ["exai-mcp"],
  "temperature": 0.15,
  "maxTokens": 16000,
  "config": {
    "exaiTool": "codereview",
    "defaultModel": "glm-4.6",
    "useWebSearch": true
  },
  "capabilities": [
    "code_review",
    "security_audit",
    "quality_assessment",
    "best_practices_validation"
  ],
  "usage": "Use @exai-validator for code reviews, security audits, and quality validation"
}
```

#### **3. Large File Analyzer**

**File:** `.claude/agents/kimi-analyzer.json`

```json
{
  "name": "kimi-analyzer",
  "description": "Large file and codebase analysis specialist using Kimi K2",
  "model": "kimi-k2-0905-preview",
  "provider": "kimi",
  "systemPrompt": "You are a codebase analysis specialist with expertise in:\n\n- Large file analysis (>5KB)\n- Dependency mapping and tracing\n- Architecture comprehension\n- Performance profiling\n- Code pattern detection\n\nAnalysis Approach:\n1. Use file upload for large files (70-80% token savings)\n2. Maintain conversation context with continuation_id\n3. Provide comprehensive analysis with specific line references\n4. Identify architectural patterns and anti-patterns\n5. Map dependencies and call chains\n6. Highlight performance bottlenecks\n\nProject Context: [YOUR_PROJECT_DESCRIPTION]\n\nFocus Areas:\n- [YOUR_FOCUS_1]\n- [YOUR_FOCUS_2]\n- [YOUR_FOCUS_3]",
  "tools": ["exai-mcp"],
  "temperature": 0.2,
  "maxTokens": 128000,
  "config": {
    "exaiTool": "analyze",
    "defaultModel": "kimi-k2-0905-preview",
    "useWebSearch": false,
    "fileUploadEnabled": true
  },
  "capabilities": [
    "large_file_analysis",
    "dependency_mapping",
    "architecture_analysis",
    "performance_profiling"
  ],
  "usage": "Use @kimi-analyzer for analyzing large files (>5KB), dependency mapping, and architecture comprehension"
}
```

#### **4. Architecture Specialist**

**File:** `.claude/agents/glm-architect.json`

```json
{
  "name": "glm-architect",
  "description": "Architecture and design decision specialist using GLM-4.6",
  "model": "glm-4.6",
  "provider": "glm",
  "systemPrompt": "You are a senior software architect specialized in [YOUR_DOMAIN]. Focus on:\n\n- High-level system design\n- Architecture patterns and trade-offs\n- Scalability and performance considerations\n- Technology stack evaluation\n- Integration strategies\n\nArchitectural Principles:\n1. **Simplicity**: Favor simple solutions over complex ones\n2. **Modularity**: Design for loose coupling and high cohesion\n3. **Scalability**: Consider growth and performance implications\n4. **Maintainability**: Optimize for long-term maintenance\n5. **Security**: Security by design, not as an afterthought\n\nProject Context: [YOUR_PROJECT_DESCRIPTION]\n\nArchitecture Style: [YOUR_ARCHITECTURE_STYLE]\n\nKey Constraints:\n- [YOUR_CONSTRAINT_1]\n- [YOUR_CONSTRAINT_2]\n- [YOUR_CONSTRAINT_3]\n\nProvide architectural guidance with clear rationale and trade-off analysis.",
  "tools": ["exai-mcp"],
  "temperature": 0.3,
  "maxTokens": 16000,
  "config": {
    "exaiTool": "thinkdeep",
    "defaultModel": "glm-4.6",
    "useWebSearch": true,
    "thinkingMode": "high"
  },
  "capabilities": [
    "architecture_design",
    "technology_evaluation",
    "scalability_planning",
    "integration_strategy"
  ],
  "usage": "Use @glm-architect for architecture decisions, design patterns, and technology evaluation"
}
```

---

### **📁 STEP 2: Update .claude/settings.local.json**

Update your `.claude/settings.local.json` to reference the agents:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "description": "Optimized Claude Code settings with agent-based architecture",
  "version": "2.1.0",
  "lastUpdated": "2025-11-04",

  "model": "minimax-m2",
  "mcpConfigPath": "[YOUR_MCP_CONFIG_PATH]",

  "environmentVariables": [
    {
      "name": "ANTHROPIC_BASE_URL",
      "value": "https://api.minimax.io/anthropic"
    },
    {
      "name": "ANTHROPIC_AUTH_TOKEN",
      "value": "${env:MINIMAX_API_KEY}"
    },
    {
      "name": "ANTHROPIC_MODEL",
      "value": "MiniMax-M2"
    }
  ],

  "enableAllProjectMcpServers": true,
  "alwaysThinkingEnabled": false,

  "tokenLimits": {
    "maxOutputTokens": 8000,
    "maxPromptTokens": 100000,
    "maxContextLength": 200000
  },

  "systemPrompt": {
    "base": "You are a senior engineering thought-partner. Provide technical guidance with precise reasoning.",
    "rules": [
      "Use FULL ABSOLUTE paths for file references",
      "For files >5KB: use kimi_upload_files",
      "Use continuation_id for multi-turn conversations",
      "Provide balanced perspectives with trade-offs",
      "Avoid overengineering - favor simplicity"
    ],
    "projectContext": "[YOUR_PROJECT_DESCRIPTION]"
  },

  "multiAgentConfig": {
    "enabled": true,
    "roles": {
      "coder": {
        "agent": "minimax-coder",
        "provider": "minimax-m2"
      },
      "reviewer": {
        "agent": "exai-validator",
        "provider": "glm-4.6"
      },
      "analyzer": {
        "agent": "kimi-analyzer",
        "provider": "kimi-k2-0905-preview"
      },
      "architect": {
        "agent": "glm-architect",
        "provider": "glm-4.6"
      }
    }
  },

  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["*"]
  }
}
```

---

### **📁 STEP 3: Minimize CLAUDE.md**

Replace your large CLAUDE.md with this minimal version:

```markdown
# Claude Code + [YOUR_PROJECT_NAME]

> **Agent-Based Configuration**  
> Last Updated: 2025-11-04 | Version: 2.0.0

---

## 🎯 What's Configured

This project uses **custom agents** for optimal Claude Code performance:

### ✅ What's Set Up:
- **MiniMax M2 Model** - Enhanced code understanding
- **Custom Agents** - Specialized AI assistants
- **MCP Servers** - [YOUR_MCP_SERVERS]
- **No Permission Prompts** - Everything auto-approved

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
@exai-validator Review the authentication code for security
@kimi-analyzer Analyze auth_service.py for performance
@glm-architect Evaluate the authentication architecture
```

---

## 📚 Documentation

- **Agent Details**: See `.claude/agents/README.md`
- **Configuration**: See `.claude/settings.local.json`

---

**Configuration Status:** ✅ **COMPLETE AND READY TO USE!**
```

---

### **📁 STEP 4: Create Agent README**

Create `.claude/agents/README.md` with detailed agent documentation (this file is NOT loaded on sync):

```markdown
# Custom Agents Documentation

> **Detailed agent specifications and usage guide**  
> This file is NOT loaded during Claude Code sync - only when explicitly referenced

---

## 🤖 Available Agents

### 1. @minimax-coder
**Purpose:** Primary coding and implementation  
**Model:** MiniMax M2  
**Best For:** Feature development, refactoring, bug fixes  
**Token Limit:** 16,384  
**Temperature:** 0.1 (deterministic)

**When to Use:**
- Implementing new features
- Refactoring existing code
- Fixing bugs
- Writing tests

**Example:**
```
@minimax-coder Implement user authentication with JWT tokens
```

---

### 2. @exai-validator
**Purpose:** Code review and quality validation  
**Model:** GLM-4.6 via EXAI  
**Best For:** Security audits, code reviews, quality checks  
**Token Limit:** 16,000  
**Temperature:** 0.15

**When to Use:**
- Pre-commit code reviews
- Security audits
- Quality validation
- Best practices verification

**Example:**
```
@exai-validator Review auth_service.py for security vulnerabilities
```

---

### 3. @kimi-analyzer
**Purpose:** Large file and codebase analysis  
**Model:** Kimi K2 (128K context)  
**Best For:** Analyzing large files, dependency mapping  
**Token Limit:** 128,000  
**Temperature:** 0.2

**When to Use:**
- Analyzing files >5KB
- Dependency mapping
- Architecture comprehension
- Performance profiling

**Example:**
```
@kimi-analyzer Analyze the entire authentication module for dependencies
```

---

### 4. @glm-architect
**Purpose:** Architecture and design decisions  
**Model:** GLM-4.6  
**Best For:** System design, technology evaluation  
**Token Limit:** 16,000  
**Temperature:** 0.3

**When to Use:**
- Architecture decisions
- Technology stack evaluation
- Design pattern selection
- Scalability planning

**Example:**
```
@glm-architect Evaluate microservices vs monolith for our use case
```

---

## 🔄 Agent Workflow Examples

### Example 1: Feature Development
```
1. @glm-architect Design the user notification system
2. @minimax-coder Implement the notification service
3. @exai-validator Review the implementation for security
4. @kimi-analyzer Analyze performance implications
```

### Example 2: Bug Fix
```
1. @kimi-analyzer Analyze error logs and identify root cause
2. @minimax-coder Implement the fix
3. @exai-validator Validate the fix doesn't introduce regressions
```

### Example 3: Refactoring
```
1. @kimi-analyzer Map dependencies in the legacy module
2. @glm-architect Design the refactored architecture
3. @minimax-coder Implement the refactoring
4. @exai-validator Review for quality and correctness
```

---

## 📊 Token Usage Comparison

| Approach | Tokens per Sync | Efficiency |
|----------|----------------|------------|
| **Large CLAUDE.md** | ~50,000 | Baseline |
| **Agent-Based** | ~3,000 | **94% reduction** |

---

## 🎯 Customization Guide

### Adding New Agents

1. Create JSON file in `.claude/agents/`
2. Define agent properties (name, model, systemPrompt)
3. Update `.claude/settings.local.json` multiAgentConfig
4. Document in this README

### Modifying Existing Agents

1. Edit the agent's JSON file
2. Update systemPrompt for behavior changes
3. Adjust temperature for creativity vs determinism
4. Update documentation

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-04
```

---

### **✅ STEP 5: Verification**

After migration, verify:

1. **Agent Files Created:**
   ```
   .claude/agents/
   ├── minimax-coder.json
   ├── exai-validator.json
   ├── kimi-analyzer.json
   ├── glm-architect.json
   └── README.md
   ```

2. **CLAUDE.md Minimized:**
   - File size < 100 lines
   - Only quick start guide
   - References to `.claude/agents/README.md`

3. **Settings Updated:**
   - `.claude/settings.local.json` has multiAgentConfig
   - Environment variables configured
   - MCP servers enabled

4. **Test Agents:**
   ```
   @minimax-coder Hello!
   @exai-validator What can you review?
   @kimi-analyzer What files can you analyze?
   @glm-architect What architecture patterns do you recommend?
   ```

---

### **📝 Customization Checklist**

Replace these placeholders with your project-specific values:

- [ ] `[YOUR_TECH_STACK]` - Your technology stack (e.g., "Python, FastAPI, Docker")
- [ ] `[YOUR_PROJECT_DESCRIPTION]` - Brief project description
- [ ] `[YOUR_FRAMEWORKS]` - Key frameworks used
- [ ] `[YOUR_STANDARD_1/2/3]` - Your coding standards
- [ ] `[YOUR_DOCSTRING_STYLE]` - Docstring format (e.g., "Google-style", "NumPy-style")
- [ ] `[YOUR_LANGUAGE]` - Programming language
- [ ] `[VERSION]` - Language version
- [ ] `[YOUR_FORMATTER]` - Code formatter (e.g., "black", "prettier")
- [ ] `[YOUR_LINE_LENGTH]` - Max line length
- [ ] `[YOUR_LINTER]` - Linter tool
- [ ] `[YOUR_ASYNC_PATTERN]` - Async pattern (e.g., "asyncio", "promises")
- [ ] `[YOUR_DOMAIN]` - Application domain (e.g., "AI systems", "web apps")
- [ ] `[YOUR_FOCUS_1/2/3]` - Analysis focus areas
- [ ] `[YOUR_ARCHITECTURE_STYLE]` - Architecture style (e.g., "microservices", "monolith")
- [ ] `[YOUR_CONSTRAINT_1/2/3]` - Key constraints
- [ ] `[YOUR_MCP_CONFIG_PATH]` - Path to MCP configuration
- [ ] `[YOUR_MCP_SERVERS]` - List of MCP servers
- [ ] `[YOUR_PROJECT_NAME]` - Project name

---

**END OF MIGRATION PROMPT**

---

## 📊 Expected Results

After running this prompt, your project will have:

1. ✅ **4 Custom Agents** - Specialized for different tasks
2. ✅ **Minimal CLAUDE.md** - < 100 lines (94% token reduction)
3. ✅ **Optimized Settings** - Agent-based configuration
4. ✅ **Comprehensive Documentation** - In `.claude/agents/README.md`
5. ✅ **Token Efficiency** - ~3,000 tokens per sync vs ~50,000

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Maintained By:** EX-AI MCP Server Team

