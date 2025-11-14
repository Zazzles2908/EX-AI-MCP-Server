# Agent Workflow Guide

**Status:** MANDATORY - All agents MUST read this first
**Purpose:** Standardized workflow for all Claude Code agents

---

## 🚨 CRITICAL: Read Order

### **Step 1: READ FIRST (MANDATORY)**
```bash
1. CLAUDE.md                    # Project overview & context
2. AGENT_WORKFLOW.md            # This file - workflow standards
3. ENVIRONMENT_SETUP.md         # Environment file management
4. ARCHITECTURE.md              # System architecture & integration
```

**⚠️ AGENTS: Do NOT proceed with ANY task until reading all 4 files above**

---

## 📋 Standard Agent Workflow

### **Phase 1: Understand Before Acting**

1. **Read Required Documentation**
   - [ ] CLAUDE.md (project context)
   - [ ] AGENT_WORKFLOW.md (this file)
   - [ ] ENVIRONMENT_SETUP.md (env management)
   - [ ] ARCHITECTURE.md (system design)

2. **Check Project Status**
   ```bash
   # Verify system is healthy
   curl http://127.0.0.1:3002/health

   # Check Docker services
   docker ps | grep exai

   # Check for any .md files in root (should only be 5-6 max)
   ls *.md | wc -l  # Should be: README, CLAUDE, CONTRIBUTING, CHANGELOG, LICENSE
   ```

3. **Understand the Task**
   - Ask clarifying questions BEFORE making changes
   - Understand WHY the change is needed
   - Identify what else might be affected

### **Phase 2: Plan Before Acting**

1. **Create TODO List**
   Use TodoWrite to track:
   - What files will be created
   - What files will be modified
   - What tests need updating
   - What docs need updating

2. **Check for Existing Solutions**
   ```bash
   # Search for similar functionality
   grep -r "function_name" --include="*.py" .

   # Check if tests already exist
   find tests/ -name "test_*.py"

   # Check documentation
   find docs/ -name "*.md"
   ```

3. **Plan Documentation Updates**
   - Where will NEW documentation go?
   - What EXISTING docs need updating?
   - Will this affect ARCHITECTURE.md?

### **Phase 3: Act with Quality**

1. **Code Quality Standards**
   - ✅ Write tests FIRST (TDD preferred)
   - ✅ Add type hints for public APIs
   - ✅ Include error handling
   - ✅ Document public functions/classes
   - ✅ Follow existing patterns in codebase

2. **File Organization Rules**
   - ✅ New source code → `src/` or `tools/`
   - ✅ New tests → `tests/` (one per module)
   - ✅ New docs → `docs/` subdirectory (NEVER in root)
   - ✅ New scripts → `scripts/` directory
   - ✅ New config → `config/` directory

3. **Documentation Standards**
   - ✅ Update README.md if adding new major features
   - ✅ Update CHANGELOG.md with changes
   - ✅ Add docstrings to all public functions
   - ✅ Reference: docs/ARCHITECTURE.md for system design

### **Phase 4: Test & Validate**

1. **Run Tests**
   ```bash
   # Unit tests
   python -m pytest tests/

   # Specific module
   python -m pytest tests/test_<module>.py

   # With coverage
   python -m pytest --cov=src tests/
   ```

2. **Integration Testing**
   ```bash
   # Test Docker services
   docker-compose ps

   # Test health endpoints
   curl http://127.0.0.1:3002/health

   # Test MCP integration
   @exai-mcp status  # (in Claude Code)
   ```

3. **Verify Documentation**
   - [ ] README.md reflects changes
   - [ ] CHANGELOG.md updated
   - [ ] New docs in correct location
   - [ ] Cross-references updated

---

## 📁 File Naming Conventions

### **Documentation Files**
```bash
# Root level (MAXIMUM 5 files)
README.md                    # Main navigation hub
CLAUDE.md                    # Project context (agents read first)
CONTRIBUTING.md              # Contribution guidelines
CHANGELOG.md                 # Version history
LICENSE                      # License

# DO NOT create other .md files in root!

# Documentation directory
docs/
├── getting-started/          # Onboarding content
├── architecture/             # System design
├── reference/                # API & commands
├── development/              # Contributing
├── examples/                 # Tutorials
├── troubleshooting/          # Help & support
└── integration/              # Integration guides

# File naming in docs/
- Use kebab-case: getting-started-guide.md
- Use descriptive names: mcp-integration-guide.md
- Add index.md to each subdirectory
```

### **Test Files**
```bash
tests/
├── conftest.py              # Shared fixtures
├── test_<module>.py         # Unit tests (one per module)
└── test_integration.py      # Integration tests

# Naming: test_<what_is_tested>.py
examples:
- test_websocket_protocol.py
- test_mcp_integration.py
- test_provider_routing.py
```

### **Source Files**
```bash
src/                         # Core source code
├── core/                    # Protocol core
├── daemon/                  # WebSocket daemon
├── providers/               # AI provider integrations
├── orchestrator/            # Route management
└── utils/                   # Shared utilities

tools/                       # Tool implementations
├── chat.py                  # Chat tool
├── debug.py                 # Debug tool
└── analyze.py               # Analysis tool
```

---

## 🧪 Test Script Standards

### **When Creating Tests**

1. **Test File Location**
   - Unit tests → `tests/test_<module>.py`
   - Integration tests → `tests/test_integration.py`
   - End-to-end tests → `tests/test_e2e.py`

2. **Test Naming**
   ```python
   # GOOD: Descriptive test names
   def test_websocket_connection_establishes_successfully():
       ...

   def test_mcp_tool_call_returns_valid_response():
       ...

   # BAD: Unclear names
   def test_connection():
       ...
   ```

3. **Test Structure (Arrange-Act-Assert)**
   ```python
   def test_tool_execution():
       # Arrange
       tool = ChatTool()
       request = {"message": "test"}

       # Act
       result = tool.execute(request)

       # Assert
       assert result.status == "success"
       assert "response" in result
   ```

4. **Test Coverage**
   - ✅ 80%+ code coverage target
   - ✅ Test all public functions/classes
   - ✅ Include edge cases and error handling
   - ✅ Mock external dependencies

---

## 📚 Documentation Standards

### **Adding New Documentation**

1. **Determine Location**
   ```
   Feature implementation docs → docs/development/
   Integration guides → docs/integration/
   Troubleshooting → docs/troubleshooting/
   Architecture → docs/architecture/
   API reference → docs/reference/
   ```

2. **Create index.md for Subdirectories**
   ```markdown
   # Section Name

   ## Overview
   Brief description of this section

   ## Contents
   - [Topic 1](topic1.md)
   - [Topic 2](topic2.md)

   ## Quick Links
   - [Back to main README](../README.md)
   - [System Architecture](../architecture/ARCHITECTURE.md)
   ```

3. **Update Navigation**
   - Update `docs/index.md` with new doc
   - Update `README.md` if it's a major feature
   - Add cross-references in related docs

### **Documentation Quality Checklist**
- [ ] Clear, descriptive titles
- [ ] Code examples for all features
- [ ] Quick start guide for new users
- [ ] Command reference documentation
- [ ] Troubleshooting section
- [ ] Cross-references to related docs

---

## 🚫 What NOT to Do

### **❌ NEVER Create**
- `.md` files in root directory (except required 5)
- `TODO.md` or `FIXME.md` files (fix issues or don't create)
- Duplicate documentation
- Undocumented public APIs

### **❌ NEVER Do**
- Delete or modify CLAUDE.md without approval
- Skip writing tests for new code
- Add markdown files to project root
- Ignore existing patterns in codebase
- Make changes without understanding impact

### **❌ NEVER Assume**
- Your way is the only/best way
- Tests aren't needed
- Documentation can be "added later"
- Breaking changes are OK without discussion

---

## 🔧 Environment File Management

### **Environment Files Explained**

| File | Purpose | Should Modify? |
|------|---------|----------------|
| `.env` | **ACTIVE** - Current settings | ✅ YES (for local dev) |
| `.env.docker` | **ACTIVE** - Docker settings | ✅ YES (container config) |
| `.env.example` | Template - Copy from this | ❌ NO (document only) |
| `.env.docker.template` | **DEPRECATED** | ❌ NO (use .env.example) |
| `.env.patched` | Temporary changes | ❌ NO (delete after use) |

### **Modifying Environment Files**

1. **For Local Development**
   ```bash
   # Edit ACTIVE files
   .env                    # For Python scripts
   .env.docker            # For Docker container

   # Use .env.example as template
   cp .env.example .env   # Copy template
   # Edit .env with your values
   ```

2. **For Documentation**
   - Update `.env.example` with new variables
   - Document variables in ENVIRONMENT_SETUP.md
   - NEVER commit actual API keys

3. **Security Rules**
   - ❌ NEVER commit `.env` (in .gitignore)
   - ❌ NEVER commit `.env.docker` (in .gitignore)
   - ✅ OK to commit `.env.example`
   - ✅ OK to commit `.env.docker.template`

---

## ✅ Pre-Submission Checklist

### **Before Marking Task Complete**

- [ ] Read CLAUDE.md, AGENT_WORKFLOW.md, ENVIRONMENT_SETUP.md, ARCHITECTURE.md
- [ ] Created TODO list and tracked progress
- [ ] All new files in correct directories
- [ ] No `.md` files in root (except required 5)
- [ ] 80%+ test coverage achieved
- [ ] All tests passing
- [ ] Documentation complete and accurate
- [ ] README.md updated if needed
- [ ] CHANGELOG.md reflects changes
- [ ] No TODO/FIXME comments remaining
- [ ] Environment files handled correctly
- [ ] Cross-references updated

### **Quality Verification**
- [ ] Code follows established patterns
- [ ] Error handling is comprehensive
- [ ] Logging is structured and useful
- [ ] Configuration is validated
- [ ] Recovery mechanisms tested
- [ ] Health monitoring functional

---

## 🆘 When Uncertain

1. **Ask Questions**
   - "I found X, Y, Z - which should I modify?"
   - "Should this be a new file or modify existing?"
   - "Where should documentation for this go?"

2. **Check Examples**
   - Look for similar features in codebase
   - Check how other tools are structured
   - Review existing documentation patterns

3. **Seek Guidance**
   - Check ARCHITECTURE.md for system design
   - Review docs/integration/ for integration patterns
   - Look at similar PRs in git history

---

**Remember: Quality over speed. Better to ask questions than make mistakes.**

**Status:** MANDATORY for all agents
**Last Updated:** 2025-11-14
