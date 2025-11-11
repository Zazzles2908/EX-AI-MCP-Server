# EXAI MCP Server - Claude Code Configuration

> **Agent-Based MCP Configuration for EXAI System**  
> Version: 6.0.0 | Last Updated: 2025-11-11

## Overview

This project integrates Claude Code with EXAI MCP Server for AI-powered development workflows.

### What's Configured
- **Models**: GLM-4.6 & Kimi K2 for enhanced code understanding
- **MCP Server**: 29 AI-powered tools
- **Routing**: Intelligent model selection
- **GitHub MCP**: Full git operations
- **Supabase MCP**: Data persistence
- **No Prompts**: Auto-approved operations

## Quick Start

### 1. Set Environment Variables
```bash
# Windows
$env:GLM_API_KEY="your_key"
$env:KIMI_API_KEY="your_key"

# Linux/Mac
export GLM_API_KEY="your_key"
export KIMI_API_KEY="your_key"
```

### 2. Start Development
```bash
# Open in VSCode
code .

# Start using MCP tools via @-mentions:
# @exai-mcp chat "Analyze this code"
# @gh-mcp gh_repo_list
# @supabase-mcp-full list_projects
```

### 3. Available Agents
- **@glm-coder** - Primary coding (GLM-4.6)
- **@exai-validator** - Code review & validation
- **@kimi-analyzer** - Large file analysis (Kimi K2)
- **@glm-architect** - Architecture decisions

## Development Workflow

### Core Principles
1. **Use EXAI throughout** - Every task uses EXAI for analysis, fixing, and verification
2. **Fix issues immediately** - Don't just identify, fix right away
3. **Security first** - No hardcoded credentials
4. **Professional standards** - A+ quality, industry best practices

### Code Quality Standards
- ✅ 80%+ test coverage
- ✅ Type hints on all public APIs
- ✅ Comprehensive error handling
- ✅ Clean imports and minimal dependencies
- ✅ No TODO/FIXME comments

### Root Directory Organization
- **Maximum 5 files** at root:
  1. `README.md` - Project overview
  2. `CONTRIBUTING.md` - Contribution guidelines
  3. `LICENSE` - Project license
  4. `CHANGELOG.md` - Version history
  5. `CLAUDE.md` - This file

- **All other files** in appropriate subdirectories:
  - `src/` - Source code
  - `tests/` - Test files
  - `docs/` - Documentation
  - `scripts/` - Scripts
  - `config/` - Configuration

## File Structure

```
c:\Project\EX-AI-MCP-Server\
├── src/                      # Source code
│   ├── daemon/              # WebSocket daemon
│   ├── providers/           # AI providers (GLM, Kimi)
│   ├── storage/             # Storage layer
│   └── server.py            # MCP server entry point
├── tools/                   # Tool implementations
├── scripts/                 # Scripts
├── tests/                   # Test files
├── utils/                   # Utilities
├── docs/                    # Documentation
└── logs/                    # Log files
```

## Testing

### Run Tests
```bash
# Quick unit tests
python run_tests.py --quick

# Full test suite with coverage
python run_tests.py --coverage

# Single module
python run_tests.py --module <module_name>

# Detailed coverage analysis
python run_tests.py --coverage-analysis
```

### System Management
```bash
# Check system health
python system_manager.py --status

# Validate configuration
python system_manager.py --validate

# Generate dashboard
python system_manager.py --dashboard
```

## System Status

### Components
- **WebSocket Daemon**: Running on port 3000
- **Tools Available**: 2 (chat, analyze)
- **GLM Provider**: ✅ Active
- **Kimi Provider**: ⚠️ Requires auth check

### Health Check
```bash
cat logs/ws_daemon.health.json
```

## Configuration

### Centralized Config
All configuration in `src/config/settings.py` - single source of truth:
- No hardcoded values
- Use `config.ws_port`, `config.ws_host`, etc.
- Prevents configuration drift

### Secrets Management
- Use `secrets.get_jwt_token("claude")` - not hardcoded
- All tokens in environment variables
- No secrets in source code

## Best Practices

### Error Handling
- Use specific exception types
- Log errors with context
- Provide actionable error messages
- Never swallow exceptions silently
- Always handle file I/O errors

### Import Management
- One class/module per file (when reasonable)
- Clear separation of concerns
- Single responsibility principle
- Proper type hints

### Security
- Zero tolerance for hardcoded credentials
- No JWT tokens in source code
- No secrets in console output
- Use Supabase for secure storage

## Troubleshooting

### Daemon Issues
```bash
# Check daemon status
cat logs/ws_daemon.health.json

# Check daemon logs
tail -f logs/ws_daemon.log

# Restart daemon
python scripts/ws/run_ws_daemon.py
```

### Import Errors
```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Provider Issues
```bash
# Test GLM provider
python -c "from src.providers.glm_provider import GLMProvider; ..."

# Test Kimi provider
python -c "from src.providers.kimi import KimiProvider; ..."
```

## Documentation

### Main Documentation
- **[documents/01-architecture-overview/](documents/01-architecture-overview/)** - System architecture
- **[documents/02-database-integration/](documents/02-database-integration/)** - Supabase integration
- **[documents/03-security-authentication/](documents/03-security-authentication/)** - Security & auth
- **[documents/04-api-tools-reference/](documents/04-api-tools-reference/)** - API & tools
- **[documents/05-operations-management/](documents/05-operations-management/)** - Operations
- **[documents/06-development-guides/](documents/06-development-guides/)** - Development

## Quality Gates

Before marking any task complete:
- [ ] Used EXAI for analysis
- [ ] Used EXAI for fixes
- [ ] Verified with EXAI
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Security review passed
- [ ] Documentation updated
- [ ] Tests passing
- [ ] 80%+ code coverage

## Support

For issues and questions:
- Check daemon logs in `logs/`
- Review system health: `logs/ws_daemon.health.json`
- Consult documentation in `docs/`

---

**Status**: ✅ Operational | **Version**: 6.0.0
