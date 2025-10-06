# System Reference Documentation

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Purpose:** Definitive reference for EX-AI-MCP-Server architecture and functionality

---

## Overview

This folder contains comprehensive system documentation that serves as the authoritative source for understanding how the complete EX-AI-MCP-Server system operates. These documents consolidate all research findings, architectural decisions, and operational procedures.

---

## Reading Order

### For New Users

1. **`01-system-overview.md`** - Start here to understand what the system is and does
2. **`06-deployment-guide.md`** - Follow this to get the system running
3. **`03-tool-ecosystem.md`** - Learn about available tools and when to use them
4. **`04-features-and-capabilities.md`** - Explore what the system can do

### For Developers

1. **`01-system-overview.md`** - High-level architecture
2. **`02-provider-architecture.md`** - Provider system design and implementation
3. **`03-tool-ecosystem.md`** - Tool catalog and agentic enhancements
4. **`05-api-endpoints-reference.md`** - Complete API reference
5. **`07-upgrade-roadmap.md`** - Current upgrade project status

### For Operations

1. **`06-deployment-guide.md`** - Installation and deployment
2. **`01-system-overview.md`** - System architecture
3. **`04-features-and-capabilities.md`** - Feature configuration
4. **`07-upgrade-roadmap.md`** - Upgrade planning

---

## Document Summaries

### 01-system-overview.md

**Purpose:** High-level introduction to the system

**Contents:**
- What EX-AI-MCP-Server is (MCP WebSocket daemon)
- Target audience (international users, api.z.ai)
- Core components (GLM + Kimi providers, tools, routing)
- Technology stack (Python, WebSocket, zai-sdk)
- Key features overview
- Quick start guide

**Read this if:** You're new to the system or need a high-level overview

---

### 02-provider-architecture.md

**Purpose:** Detailed provider system design

**Contents:**
- GLM Provider (zai-sdk v0.0.4, GLM-4.6)
- Kimi Provider (Moonshot API)
- Manager-first routing architecture
- Dual SDK/HTTP fallback pattern
- Streaming implementation
- Error handling and retries
- Performance optimization
- Cost optimization

**Read this if:** You need to understand or modify provider implementation

---

### 03-tool-ecosystem.md

**Purpose:** Complete tool catalog and usage guide

**Contents:**
- Simple tools (chat, thinkdeep, planner, consensus, challenge)
- Workflow tools (analyze, debug, codereview, precommit, refactor, testgen, tracer, secaudit, docgen)
- Agentic enhancements (self-assessment, early termination, dynamic steps)
- Tool selection guidance
- Parameter reference
- Usage examples

**Read this if:** You need to use tools or understand tool capabilities

---

### 04-features-and-capabilities.md

**Purpose:** Detailed feature documentation

**Contents:**
- Streaming support (environment-gated)
- Web search integration (native GLM)
- Tool calling and function execution
- Multimodal support (text, images, audio, video, files)
- Multi-turn conversations
- Advanced features (video generation, assistant API, character RP)
- Configuration parameters
- Response formats
- OpenAI compatibility
- Performance characteristics

**Read this if:** You need to configure or use specific features

---

### 05-api-endpoints-reference.md

**Purpose:** Complete API reference

**Contents:**
- Base URLs (api.z.ai)
- Authentication (Bearer token)
- Chat completions endpoint
- Video generation endpoint
- Web search tool
- Assistant API endpoint
- File upload endpoint
- Embeddings endpoint
- Function calling
- Retrieval tool
- Rate limits
- Error responses
- SDK examples

**Read this if:** You need API details or are integrating with the system

---

### 06-deployment-guide.md

**Purpose:** Installation and deployment instructions

**Contents:**
- Prerequisites (system requirements, API access)
- Installation steps (clone, venv, dependencies)
- Configuration (.env setup)
- Starting the server (Windows, Linux, macOS)
- Verification steps
- Troubleshooting common issues
- Production deployment (systemd, Docker)
- Monitoring and logging
- Security best practices
- Backup and recovery
- Upgrading

**Read this if:** You need to install, deploy, or maintain the system

---

### 07-upgrade-roadmap.md

**Purpose:** Current upgrade project status

**Contents:**
- Project overview (zai-sdk v0.0.4 upgrade)
- Wave-based execution plan (6 waves)
- Research findings (zai-sdk v0.0.4, GLM-4.6, api.z.ai)
- Breaking changes analysis
- New features documentation
- Known issues (web search prompt injection)
- Success criteria
- Dependencies
- Risk assessment
- Progress tracking

**Read this if:** You need to understand the current upgrade project

---

## Related Documentation

### User Guides (`docs/guides/`)

- `tool-selection-guide.md` - Which tool for which purpose
- `parameter-reference.md` - All tool parameters
- `web-search-guide.md` - Web search usage
- `query-examples.md` - Working examples
- `troubleshooting.md` - Common issues

### Architecture Documentation (`docs/architecture/`)

- Design decisions and implementation details
- Phase 0, Phase 1 documentation
- Comparative analyses
- Technical debt audits

### Upgrade Documentation (`docs/upgrades/`)

- Upgrade guides and migration paths
- International users documentation
- Version-specific changes

---

## Document Maintenance

### Update Frequency

- **System Overview:** Update with major releases
- **Provider Architecture:** Update when provider changes
- **Tool Ecosystem:** Update when tools added/modified
- **Features:** Update when features added/changed
- **API Reference:** Update with API changes
- **Deployment Guide:** Update with deployment changes
- **Upgrade Roadmap:** Update weekly during upgrade project

### Version Control

All documents include:
- Version number
- Last updated date
- Related documents

### Review Process

1. Technical review by development team
2. Validation with EXAI tools (codereview_EXAI-WS)
3. User testing for clarity
4. Final approval before merge

---

## Contributing

### Adding New Documentation

1. Follow existing document structure
2. Include version and date
3. Cross-reference related documents
4. Validate with EXAI tools
5. Submit pull request

### Updating Existing Documentation

1. Update version number
2. Update "Last Updated" date
3. Document changes in commit message
4. Validate with EXAI tools
5. Submit pull request

---

## Support

### Questions About Documentation

- **GitHub Issues:** Report documentation bugs
- **Discussions:** Ask clarification questions
- **Pull Requests:** Suggest improvements

### Official Resources

- **Z.ai API Docs:** https://docs.z.ai/
- **GLM-4.6 Guide:** https://docs.z.ai/guides/llm/glm-4.6
- **zai-sdk GitHub:** https://github.com/zai-org/z-ai-sdk-python

---

## Quick Reference

### Common Tasks

**Get Started:**
1. Read `01-system-overview.md`
2. Follow `06-deployment-guide.md`
3. Explore `03-tool-ecosystem.md`

**Use a Tool:**
1. Check `03-tool-ecosystem.md` for tool selection
2. Review `docs/guides/parameter-reference.md` for parameters
3. See `docs/guides/query-examples.md` for examples

**Configure a Feature:**
1. Read `04-features-and-capabilities.md` for feature details
2. Check `06-deployment-guide.md` for configuration
3. Verify with `05-api-endpoints-reference.md` for API details

**Troubleshoot an Issue:**
1. Check `06-deployment-guide.md` troubleshooting section
2. Review `docs/guides/troubleshooting.md`
3. Check logs in `.logs/mcp_server.log`

**Understand Upgrade Project:**
1. Read `07-upgrade-roadmap.md` for current status
2. Check `docs/upgrades/international-users/` for details
3. Review research findings in `07-upgrade-roadmap.md`

---

## Document Statistics

**Total Documents:** 7  
**Total Pages:** ~100 (estimated)  
**Total Words:** ~25,000 (estimated)  
**Coverage:** Complete system documentation

**Last Full Review:** 2025-10-02  
**Next Scheduled Review:** 2025-10-15 (after Wave 1 completion)

---

**Created:** 2025-10-02  
**Purpose:** Consolidate all system knowledge in one authoritative location  
**Audience:** Developers, operators, users, contributors

