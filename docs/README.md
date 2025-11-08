# Documentation Hub

Welcome to the EXAI MCP Server documentation. This repository contains comprehensive guides for understanding, configuring, and using the EXAI MCP Server.

## 📚 Documentation Structure

### 🚀 Quick Start
- **[Getting Started Guide](getting-started/)** - Installation, setup, and first steps
- **[Quick Start Guide](00_Quick_Start_Guide.md)** - Fast-track to get you productive
- **[Client Setup Guide](../EXAI_MCP_CLIENT_SETUP_GUIDE.md)** - Configure Claude Desktop

### 🏗️ Architecture & Design
- **[EXAI MCP Architecture](architecture/exai-mcp-architecture.md)** ⭐ - Complete technical architecture with diagrams
  - 5-layer architecture overview
  - Message flow sequences
  - Port mapping details
  - Tool execution flow
  - Component deep-dives
- **[System Capabilities](../docs/SYSTEM_CAPABILITIES_OVERVIEW.md)** - System overview and features
- **[Agent Capabilities](../docs/AGENT_CAPABILITIES.md)** - Available agent functions

### 🛠️ Development
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[Tool Development Guide](development/tool-development.md)** - Create custom EXAI tools
- **[Configuration Guide](development/configuration.md)** - Configure servers and clients
- **[EXAI Tool Usage Guide](development/exai-tool-usage-guide.md)** ⚠️ - **Correct usage patterns & common errors**
- **[Deployment Guide](development/deployment.md)** - Deploy in production

### 📖 API Reference
- **[MCP Protocol Guide](api/mcp-protocol.md)** - Understanding MCP messages
- **[Tool Integration](api/tool-integration.md)** - Integrate with EXAI tools
- **[Tool Reference](../EXAI_TOOLS_REFERENCE.md)** - Complete tool reference

### 🔧 Troubleshooting
- **[Troubleshooting Guide](troubleshooting/)** - Common issues and solutions
- **[MCP Status](../MCP_STATUS.md)** - Current server status
- **[Port Strategy Guide](../PORT_STRATEGY_CONNECTION_GUIDE.md)** - Port configuration details

### 📋 Project Status
- **[Implementation Status](../PHASE_2_IMPLEMENTATION_COMPLETE.md)** - Phase 2 completion report
- **[Port Strategy Report](../PORT_STRATEGY_IMPLEMENTATION_REPORT.md)** - Port mapping strategy
- **[Verification Report](../PORT_STRATEGY_VERIFICATION_REPORT.md)** - Port verification results
- **[Migration Guide](../PHASE_1_MIGRATION_EXECUTION.md)** - Migration procedures
- **[Changelog](../CHANGELOG.md)** - Version history

### 📊 Project Overview
- **[Main README](../README.md)** - Project overview and quick links
- **[Supabase Optimization](../docs/SUPABASE_OPTIMIZATION_MASTER_PLAN.md)** - Database optimization
- **[Tool Decision Tree](../docs/01_Tool_Decision_Tree.md)** - Choose the right tool

## 🎯 Recommended Reading Path

### New Users
1. Start with [Getting Started Guide](getting-started/)
2. Read [Quick Start Guide](00_Quick_Start_Guide.md)
3. Review [EXAI MCP Architecture](architecture/exai-mcp-architecture.md)

### Developers
1. Read [EXAI MCP Architecture](architecture/exai-mcp-architecture.md)
2. **Review [EXAI Tool Usage Guide](development/exai-tool-usage-guide.md) ⚠️** - Learn correct usage patterns
3. Follow [Tool Development Guide](development/tool-development.md)
4. Review [MCP Protocol Guide](api/mcp-protocol.md)
5. Check [Contributing Guide](../CONTRIBUTING.md)

### System Administrators
1. Review [EXAI MCP Architecture](architecture/exai-mcp-architecture.md) (Port Mapping section)
2. Follow [Deployment Guide](development/deployment.md)
3. Read [Configuration Guide](development/configuration.md)
4. Bookmark [Troubleshooting Guide](troubleshooting/)

## 🔍 Key Concepts

### Architecture Layers
```
Claude Desktop (stdio) → WebSocket Shim → Docker (3000:8079) → EXAI Daemon → Tools
```

### 21 EXAI Tools
- **Essential (3)**: status, chat, planner
- **Core (7)**: analyze, codereview, debug, refactor, testgen, thinkdeep, smart_file_query
- **Advanced (7)**: consensus, docgen, secaudit, tracer, precommit, kimi_chat_with_tools, glm_payload_preview
- **Hidden (4)**: Diagnostic and deprecated tools

### Critical Configuration
- **Port Mapping**: `3000:8079` (host:container)
- **Shim Port**: 3000 (connects FROM)
- **Daemon Port**: 8079 (listens TO)
- **LEAN_MODE**: true (shows 10 tools by default)

## 🆘 Need Help?

1. **Can't connect?**: See [Troubleshooting → Connection Issues](troubleshooting/connection-issues.md)
2. **Tools not loading?**: Check [MCP Status](../MCP_STATUS.md)
3. **Port errors?**: Review [Port Strategy Guide](../PORT_STRATEGY_CONNECTION_GUIDE.md)
4. **Configuration issues?**: Read [Configuration Guide](development/configuration.md)

## 📝 Contributing

Found an issue in the documentation? Want to add a guide? See the [Contributing Guide](../CONTRIBUTING.md) for details on how to help improve these docs.

## 📄 License

This project is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

**Last Updated**: 2025-11-08
**Version**: 4.0.0
**Maintained By**: EX-AI MCP Server Team
