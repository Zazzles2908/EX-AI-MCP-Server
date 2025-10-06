# EX-AI-MCP-Server Design Context

**Generated:** 2025-10-03
**Purpose:** Complete design intent for code review

---



## 01-system-overview.md

**Source:** `docs/system-reference/01-system-overview.md`

---

# System Overview: EX-AI-MCP-Server

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Target Audience:** International developers using api.z.ai (NOT mainland China)

---

## What is EX-AI-MCP-Server?

EX-AI-MCP-Server is a **Model Context Protocol (MCP) WebSocket daemon** that provides a unified interface for accessing advanced AI capabilities through ZhipuAI's international platform (api.z.ai) and Moonshot's Kimi API. It serves as an intelligent middleware layer that enables developers to leverage cutting-edge language models with agentic routing, streaming support, and comprehensive tool integration.

### Key Characteristics

- **Protocol:** WebSocket-based MCP daemon running on `ws://127.0.0.1:8765`
- **Target Market:** International users accessing api.z.ai (NOT mainland China endpoints)
- **Architecture:** Manager-first agentic routing with intelligent model selection
- **Deployment:** Turnkey GitHub repository with comprehensive documentation
- **Language:** Python 3.8+ with modern async/await patterns

---

## Core Components

### 1. Provider System

**GLM Provider (ZhipuAI/Z.ai)**
- **SDK:** zai-sdk v0.0.4 (international version) - **NO BREAKING CHANGES**
- **Flagship Model:** GLM-4.6 with 200K context window (355B/32B MoE architecture)
- **Endpoint:** https://api.z.ai/api/paas/v4/
- **Features:** Web search, tool calling, streaming, multimodal support
- **Pricing:** $0.60 input / $2.20 output per million tokens
- **New Features:** CogVideoX-2 (video generation), Assistant API, CharGLM-3 (character RP)

**Kimi Provider (Moonshot)**
- **API:** Moonshot API (Tier 2 access)
- **Recommended Model:** kimi-k2-0905-preview (256K context, 1T/32B MoE)
- **Alternative Models:** kimi-k2-0711-preview (256K), moonshot-v1-128k (128K)
- **Pricing:** $0.60 input / $2.50 output per million tokens
- **Features:** Agentic intelligence, tool use, coding, long context support (256K)
- **Use Case:** Tool integration, code generation, agentic workflows, complex reasoning
- **Performance:** SOTA on SWE Bench Verified, Tau2, AceBench (among open models)

### 2. Agentic Routing System

**Manager-First Architecture:**
- **Default Manager:** GLM-4.5-flash (fast, cost-effective routing decisions)
- **Routing Logic:** Intelligent task classification and model selection
- **Escalation:** Simple tasks → GLM-4.5-flash, Complex tasks → GLM-4.6 or Kimi
- **Benefits:** Optimal cost/performance balance, automatic complexity assessment

### 3. Tool Ecosystem

The EX-AI-MCP-Server provides a comprehensive tool ecosystem with 16+ tools organized into three categories:

**Tool Categories:**
- **Simple Tools** (7 tools): Request/response for conversations, planning, and analysis
- **Workflow Tools** (9 tools): Multi-step investigation with pause enforcement
- **Utility Tools** (2 tools): System information and diagnostics

**Key Capabilities:**
- Self-assessment of information sufficiency
- Early termination when goals achieved
- Dynamic step adjustment mid-workflow
- Configurable sufficiency thresholds

**📖 For complete tool documentation, see:** [03-tool-ecosystem-overview.md](03-tool-ecosystem-overview.md)

### 4. Technology Stack

**Core Technologies:**
- **Language:** Python 3.8+
- **Protocol:** WebSocket (MCP standard)
- **SDK:** zai-sdk 0.0.4 (international), zhipuai 2.1.0+ (dual SDK approach)
- **Async Framework:** asyncio with modern async/await patterns
- **Streaming:** Server-Sent Events (SSE) for real-time responses

**Key Dependencies:**
```
zai-sdk>=0.0.4          # International SDK for api.z.ai
zhipuai>=2.1.0          # Mainland China SDK (dual approach)
websockets>=12.0        # WebSocket server
httpx>=0.27.0           # HTTP client with streaming
pydantic>=2.0           # Data validation
python-dotenv>=1.0.0    # Environment configuration
```

---

## System Architecture

### High-Level Flow

```
User Request
    ↓
WebSocket MCP Daemon (ws://127.0.0.1:8765)
    ↓
AI Manager (GLM-4.5-flash)
    ↓
Task Classification & Routing
    ↓
    ├─→ Simple Task → GLM-4.5-flash (fast response)
    ├─→ Complex Task → GLM-4.6 (advanced reasoning)
    ├─→ Quality Task → Kimi (caching + quality)
    └─→ Tool Execution → Workflow Tools (multi-step)
    ↓
Response (streaming or complete)
    ↓
User
```

### Dual SDK/HTTP Fallback Pattern

**Primary Path:** zai-sdk (OpenAI-compatible API)
```python
sdk_client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True,
    tools=[...]
)
```

**Fallback Path:** HTTP client with SSE streaming
```python
httpx.post(
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={...},
    stream=True
)
```

**Benefits:**
- Resilience: Automatic fallback if SDK fails
- Flexibility: Can use HTTP for debugging
- Compatibility: Works with both SDK and raw API

---

## Target Audience

### Primary Users

**International Developers:**
- Accessing api.z.ai (NOT mainland China endpoints)
- Building AI-powered applications
- Requiring advanced agentic capabilities
- Needing cost-effective GLM-4.6 access

**Use Cases:**
- AI coding assistants (Claude Code, Kilo Code, Roo Code, Cline)
- Agentic workflows and automation
- Multi-turn conversational AI
- Code analysis and review systems
- Security auditing and testing
- Documentation generation

### NOT For

- Mainland China users (use zhipuai SDK directly with open.bigmodel.cn)
- Users requiring only simple chat (use Z.ai web interface)
- Users without API access (requires api.z.ai API key)

---

## Key Features

### 1. Streaming Support (Environment-Gated)

**Configuration:**
```env
GLM_STREAM_ENABLED=true  # Enable streaming for GLM provider
```

**Benefits:**
- Real-time response generation
- Lower perceived latency
- Better user experience for long responses
- Token-by-token delivery

### 2. Web Search Integration

**Native GLM Web Search:**
- Automatically triggered by query content
- No manual search required
- Integrated into chat responses
- Configurable search engines (search_pro_jina, search_pro_bing)

**Features:**
- Recency filters (oneDay, oneWeek, oneMonth, oneYear)
- Domain whitelisting
- Content size control (medium, high)
- Result sequencing (before, after)

### 3. Tool Calling and Function Execution

**OpenAI-Compatible Function Calling:**
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {...}
      }
    }
  ]
}
```

**Supported Tool Types:**
- Function calling (custom functions)
- Web search (native integration)
- Retrieval (knowledge base)

### 4. Multimodal Support

**Supported Input Types:**
- Text (standard messages)
- Images (vision models)
- Audio (audio processing)
- Video (video understanding)
- Files (document analysis)

**Models:**
- GLM-4.5V series (vision)
- GLM-4.6 (multimodal)
- CogVideoX-2 (video generation)

### 5. Advanced Features (New in v0.0.4)

**Video Generation (CogVideoX-2):**
- Text-to-video generation
- Image-to-video generation
- Customizable quality, FPS, size
- Audio support

**Assistant API:**
- Structured conversations
- Context management
- Streaming support
- Metadata and attachments

**Character Role-Playing (CharGLM-3):**
- Character creation
- Meta parameters
- Conversation handling
- Role-playing scenarios

---

## Deployment Model

### Turnkey GitHub Repository

**Installation:**
```bash
git clone https://github.com/your-org/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
pip install -r requirements.txt
```

**Configuration:**
```bash
cp .env.example .env
# Edit .env with your api.z.ai API key
```

**Startup:**
```bash
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1

# Linux/Mac
./scripts/ws_start.sh
```

**Verification:**
```bash
# Server should be running on ws://127.0.0.1:8765
# Check logs in .logs/mcp_server.log
```

---

## Documentation Structure

### System Reference (This Folder)
- `01-system-overview.md` - This document
- `02-provider-architecture.md` - Provider system design
- `03-tool-ecosystem.md` - Complete tool catalog
- `04-features-and-capabilities.md` - System capabilities
- `05-api-endpoints-reference.md` - API reference
- `06-deployment-guide.md` - Deployment instructions
- `07-upgrade-roadmap.md` - Current upgrade status

### User Guides
- `docs/guides/tool-selection-guide.md` - Which tool for which purpose
- `docs/guides/parameter-reference.md` - All tool parameters
- `docs/guides/web-search-guide.md` - Web search usage
- `docs/guides/query-examples.md` - Working examples
- `docs/guides/troubleshooting.md` - Common issues

### Architecture Documentation
- `docs/architecture/` - Design decisions and implementation details
- `docs/upgrades/` - Upgrade guides and migration paths

---

## Quick Start

### 1. Get API Key
Visit https://z.ai/manage-apikey/apikey-list and create an API key

### 2. Install
```bash
git clone <repository>
cd EX-AI-MCP-Server
pip install -r requirements.txt
```

### 3. Configure
```bash
cp .env.example .env
# Edit .env:
# GLM_API_KEY=your_api_key_here
# GLM_BASE_URL=https://api.z.ai/v1
```

### 4. Run
```bash
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1
```

### 5. Verify
Server should start on `ws://127.0.0.1:8765`

---

## Support and Resources

### Official Documentation
- **Z.ai API Docs:** https://docs.z.ai/
- **GLM-4.6 Guide:** https://docs.z.ai/guides/llm/glm-4.6
- **zai-sdk GitHub:** https://github.com/zai-org/z-ai-sdk-python

### Community
- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share experiences

---

## Version History

**v1.0 (Current)**
- Initial release with GLM-4.6 support
- zai-sdk v0.0.4 integration
- Agentic routing and tool ecosystem
- Comprehensive documentation

**Upcoming (v1.1)**
- Video generation (CogVideoX-2)
- Assistant API integration
- Character role-playing (CharGLM-3)
- Enhanced web search diagnostics

---

**Next:** Read `02-provider-architecture.md` for detailed provider system design





## 02-provider-architecture.md

**Source:** `docs/system-reference/02-provider-architecture.md`

---

# Provider Architecture

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [01-system-overview.md](01-system-overview.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

The EX-AI-MCP-Server implements a **dual-provider architecture** with intelligent routing between GLM (ZhipuAI/Z.ai) and Kimi (Moonshot) providers. This design maximizes cost-efficiency, performance, and reliability through a manager-first routing strategy and dual SDK/HTTP fallback pattern.

---

## Provider Comparison

| Feature | GLM Provider | Kimi Provider |
|---------|--------------|---------------|
| **SDK** | zai-sdk v0.0.4 | Moonshot API |
| **Flagship Model** | GLM-4.6 (200K context) | kimi-k2-0905-preview (256K context) |
| **Base URL** | https://api.z.ai/v1 | https://api.moonshot.ai/v1 |
| **Pricing** | $0.60/$2.20 per M tokens | $0.60/$2.50 per M tokens |
| **Web Search** | Native integration | Not available |
| **Streaming** | SSE streaming | SSE streaming |
| **Tool Calling** | OpenAI-compatible | OpenAI-compatible |
| **Best For** | Web search, cost optimization | Tool use, coding, agentic workflows |
| **Multimodal** | Images, audio, video, files | Text only |
| **Caching** | Prompt caching | Advanced caching |

---

## Providers

### GLM Provider (ZhipuAI/Z.ai)

**Primary Use Cases:**
- Web search integration
- Cost-effective general tasks
- Multimodal capabilities (images, audio, video)
- Fast routing decisions (GLM-4.5-flash as manager)

**📖 For complete GLM provider documentation, see:** [providers/glm.md](providers/glm.md)

---

### Kimi Provider (Moonshot)

**Primary Use Cases:**
- Quality reasoning and analysis
- Long context processing (256K tokens)
- Tool use and agentic workflows
- Code generation and debugging

**📖 For complete Kimi provider documentation, see:** [providers/kimi.md](providers/kimi.md)

---

## Agentic Routing

**Manager-First Architecture:**
- **Default Manager:** GLM-4.5-flash (fast, cost-effective routing decisions)
- **Routing Logic:** Intelligent task classification and model selection
- **Escalation:** Simple tasks → GLM-4.5-flash, Complex tasks → GLM-4.6 or Kimi
- **Benefits:** Optimal cost/performance balance, automatic complexity assessment

**📖 For complete routing documentation, see:** [providers/routing.md](providers/routing.md)

---

## Architecture Patterns

### Dual SDK/HTTP Fallback

**Pattern:**
```python
try:
    # Primary: Use SDK
    response = client.chat.completions.create(...)
except Exception:
    # Fallback: Use HTTP
    response = httpx.post(...)
```

**Benefits:**
- Reliability through redundancy
- Graceful degradation
- Compatibility across SDK versions

---

## Related Documentation

- [providers/glm.md](providers/glm.md) - Complete GLM provider details
- [providers/kimi.md](providers/kimi.md) - Complete Kimi provider details
- [providers/routing.md](providers/routing.md) - Agentic routing logic
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Feature details
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints





## 03-tool-ecosystem.md

**Source:** `docs/system-reference/03-tool-ecosystem.md`

---

# Tool Ecosystem Overview

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [01-system-overview.md](01-system-overview.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

The EX-AI-MCP-Server provides a comprehensive tool ecosystem designed for agentic AI workflows. Tools are organized into three categories: **Simple Tools** (request/response), **Workflow Tools** (multi-step investigation), and **Utility Tools** (system information).

---

## Tool Categories

### Simple Tools (Request/Response)

Quick, single-call tools for conversations, planning, and analysis:

- **[chat](tools/simple-tools/chat.md)** - Collaborative thinking partner for development conversations
- **[thinkdeep](tools/simple-tools/thinkdeep.md)** - Extended reasoning partner to challenge assumptions
- **[planner](tools/simple-tools/planner.md)** - Sequential step-by-step planning with branching
- **[consensus](tools/simple-tools/consensus.md)** - Multi-model consensus workflow for complex decisions
- **[challenge](tools/simple-tools/challenge.md)** - Critical analysis and truth-seeking

### Workflow Tools (Multi-Step Investigation)

Systematic investigation tools with pause enforcement between steps:

- **[analyze](tools/workflow-tools/analyze.md)** - Smart file analysis and code understanding
- **[debug](tools/workflow-tools/debug.md)** - Systematic investigation & expert debugging
- **[codereview](tools/workflow-tools/codereview.md)** - Professional code review with prioritized feedback
- **[refactor](tools/workflow-tools/refactor.md)** - Intelligent refactoring with top-down decomposition
- **[testgen](tools/workflow-tools/testgen.md)** - Comprehensive test generation with edge case coverage
- **[tracer](tools/workflow-tools/tracer.md)** - Code tracing and dependency mapping
- **[secaudit](tools/workflow-tools/secaudit.md)** - Comprehensive security audit with OWASP assessment
- **[docgen](tools/workflow-tools/docgen.md)** - Documentation generation with complexity analysis
- **[precommit](tools/workflow-tools/precommit.md)** - Pre-commit validation and change analysis

### Utility Tools

System information and diagnostics:

- **[listmodels](tools/simple-tools/listmodels.md)** - Display all available AI models by provider
- **[version](tools/simple-tools/version.md)** - Server version, configuration, and tool listing

---

## Tool Selection Guide

### For Understanding Code
- **New codebase?** → Use [analyze](tools/workflow-tools/analyze.md) for comprehensive exploration
- **Specific function?** → Use [tracer](tools/workflow-tools/tracer.md) to map execution flow
- **Architecture review?** → Use [analyze](tools/workflow-tools/analyze.md) with `analysis_type: architecture`

### For Finding Issues
- **Runtime error?** → Use [debug](tools/workflow-tools/debug.md) for systematic investigation
- **Code quality?** → Use [codereview](tools/workflow-tools/codereview.md) for comprehensive review
- **Security concerns?** → Use [secaudit](tools/workflow-tools/secaudit.md) for OWASP assessment
- **Before commit?** → Use [precommit](tools/workflow-tools/precommit.md) to validate changes

### For Improving Code
- **Need refactoring?** → Use [refactor](tools/workflow-tools/refactor.md) for decomposition analysis
- **Missing tests?** → Use [testgen](tools/workflow-tools/testgen.md) for comprehensive test generation
- **No documentation?** → Use [docgen](tools/workflow-tools/docgen.md) for automated docs

### For Planning & Discussion
- **Brainstorming?** → Use [chat](tools/simple-tools/chat.md) for open-ended discussions
- **Complex decision?** → Use [consensus](tools/simple-tools/consensus.md) for multi-model perspectives
- **Need deeper analysis?** → Use [thinkdeep](tools/simple-tools/thinkdeep.md) to challenge assumptions
- **Breaking down tasks?** → Use [planner](tools/simple-tools/planner.md) for step-by-step planning

---

## Agentic Enhancements (Phase 1)

All workflow tools support agentic capabilities:

### Self-Assessment
- Evaluate information sufficiency at each step
- Determine if enough evidence has been gathered
- Decide when to proceed vs. continue investigation

### Early Termination
- Stop investigation when goals are achieved
- Avoid unnecessary steps when confidence is high
- Configurable confidence thresholds

### Dynamic Step Adjustment
- Adjust total_steps mid-workflow as understanding evolves
- Add or remove steps based on findings
- Backtrack to revise previous steps when new insights emerge

### Configurable Sufficiency Thresholds
- Set minimum confidence levels for completion
- Customize investigation depth per use case
- Balance thoroughness vs. efficiency

---

## Common Parameters

### Workflow Tools
All workflow tools share these parameters:
- `step` (required): Current investigation step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps (adjustable)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Discoveries and evidence from this step
- `confidence` (optional): Confidence level (exploring → certain)
- `continuation_id` (optional): Continue previous investigations

### Model Selection
All tools support:
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth (minimal|low|medium|high|max)
- `temperature` (optional): Response creativity (0-1)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

---

## Best Practices

### Choosing the Right Tool
1. **Start with the most specific tool** - Use specialized tools (debug, codereview, secaudit) over general ones (analyze)
2. **Consider investigation depth** - Workflow tools for thorough analysis, simple tools for quick answers
3. **Leverage continuation** - Build on previous investigations with `continuation_id`
4. **Use appropriate models** - Large context models (Kimi) for comprehensive analysis, fast models (GLM-4.5-flash) for quick tasks

### Workflow Tool Usage
1. **Be thorough in step 1** - Clearly describe investigation plan and objectives
2. **Track all evidence** - Document findings, files checked, methods examined
3. **Evolve hypotheses** - Update theories as investigation progresses
4. **Use backtracking** - Revise previous steps when new insights emerge
5. **Signal completion** - Set `next_step_required: false` when investigation is complete

### File References
- **Always use absolute paths** - Relative paths may fail
- **Include relevant files** - Provide context for better analysis
- **Use images when helpful** - Screenshots, diagrams, error messages

---

## Related Documentation

- [01-system-overview.md](01-system-overview.md) - System architecture and components
- [02-provider-architecture.md](02-provider-architecture.md) - GLM and Kimi provider details
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Streaming, web search, multimodal
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints and authentication
- [06-deployment-guide.md](06-deployment-guide.md) - Installation and configuration
- [07-upgrade-roadmap.md](07-upgrade-roadmap.md) - Upgrade project status

---

## Quick Reference

| Need | Tool | Category |
|------|------|----------|
| Understand code | [analyze](tools/workflow-tools/analyze.md) | Workflow |
| Fix bug | [debug](tools/workflow-tools/debug.md) | Workflow |
| Review code | [codereview](tools/workflow-tools/codereview.md) | Workflow |
| Refactor code | [refactor](tools/workflow-tools/refactor.md) | Workflow |
| Generate tests | [testgen](tools/workflow-tools/testgen.md) | Workflow |
| Trace execution | [tracer](tools/workflow-tools/tracer.md) | Workflow |
| Security audit | [secaudit](tools/workflow-tools/secaudit.md) | Workflow |
| Generate docs | [docgen](tools/workflow-tools/docgen.md) | Workflow |
| Validate changes | [precommit](tools/workflow-tools/precommit.md) | Workflow |
| Brainstorm | [chat](tools/simple-tools/chat.md) | Simple |
| Deep analysis | [thinkdeep](tools/simple-tools/thinkdeep.md) | Simple |
| Plan tasks | [planner](tools/simple-tools/planner.md) | Simple |
| Get consensus | [consensus](tools/simple-tools/consensus.md) | Simple |
| Critical analysis | [challenge](tools/simple-tools/challenge.md) | Simple |
| List models | [listmodels](tools/simple-tools/listmodels.md) | Utility |
| Check version | [version](tools/simple-tools/version.md) | Utility |





## 04-features-and-capabilities.md

**Source:** `docs/system-reference/04-features-and-capabilities.md`

---

# Features and Capabilities

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [02-provider-architecture.md](02-provider-architecture.md), [05-api-endpoints-reference.md](05-api-endpoints-reference.md)

---

## Overview

The EX-AI-MCP-Server provides comprehensive AI capabilities through the ZhipuAI (Z.ai) and Moonshot (Kimi) platforms. This document provides an overview of all available features with links to detailed documentation.

**Upgrade Status:** Wave 2 (Synthesis & UX Improvements) - IN PROGRESS  
**Target SDK:** zai-sdk v0.0.4  
**Breaking Changes:** **NONE** - 100% backward compatible upgrade

---

## Core Features

### Streaming Support
Real-time response generation with token-by-token delivery for better user experience.

**📖 For complete streaming documentation, see:** [features/streaming.md](features/streaming.md)

---

### Web Search Integration
Native GLM web search with automatic triggering and multiple search engine support.

**📖 For complete web search documentation, see:** [features/web-search.md](features/web-search.md)

---

### Multimodal Support
Process images, audio, video, and files alongside text for comprehensive AI interactions.

**📖 For complete multimodal documentation, see:** [features/multimodal.md](features/multimodal.md)

---

### Caching
Prompt caching and advanced caching strategies for improved performance and cost reduction.

**📖 For complete caching documentation, see:** [features/caching.md](features/caching.md)

---

### Tool Calling
OpenAI-compatible function calling for agentic workflows and tool integration.

**📖 For complete tool calling documentation, see:** [features/tool-calling.md](features/tool-calling.md)

---

## Feature Comparison

| Feature | GLM Provider | Kimi Provider |
|---------|--------------|---------------|
| **Streaming** | ✅ SSE streaming | ✅ SSE streaming |
| **Web Search** | ✅ Native integration | ❌ Not available |
| **Multimodal** | ✅ Images, audio, video, files | ❌ Text only |
| **Caching** | ✅ Prompt caching | ✅ Advanced caching |
| **Tool Calling** | ✅ OpenAI-compatible | ✅ OpenAI-compatible |
| **Context Window** | 200K tokens (GLM-4.6) | 256K tokens (kimi-k2-0905-preview) |

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_STREAM_ENABLED=true
GLM_ENABLE_WEB_BROWSING=true
GLM_DEFAULT_MODEL=glm-4.6
```

**Kimi Provider:**
```env
KIMI_STREAM_ENABLED=true
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
```

---

## Related Documentation

- [features/streaming.md](features/streaming.md) - Streaming implementation details
- [features/web-search.md](features/web-search.md) - Web search configuration
- [features/multimodal.md](features/multimodal.md) - Multimodal capabilities
- [features/caching.md](features/caching.md) - Caching strategies
- [features/tool-calling.md](features/tool-calling.md) - Tool calling patterns
- [02-provider-architecture.md](02-provider-architecture.md) - Provider details
- [05-api-endpoints-reference.md](05-api-endpoints-reference.md) - API endpoints





## 05-api-endpoints-reference.md

**Source:** `docs/system-reference/05-api-endpoints-reference.md`

---

# API Endpoints Reference

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [02-provider-architecture.md](02-provider-architecture.md), [04-features-and-capabilities.md](04-features-and-capabilities.md)

---

## Overview

This document provides an overview of all API endpoints available in the EX-AI-MCP-Server. For detailed documentation on each endpoint, see the linked pages below.

---

## Base URLs

### International Users (api.z.ai)

**Primary Base URL:**
```
https://api.z.ai/v1
```

**Full API Path:**
```
https://api.z.ai/api/paas/v4/
```

**Alternative Endpoints:**
- **Anthropic-compatible:** `https://api.z.ai/api/anthropic`
- **Coding-specific:** `https://api.z.ai/api/coding/paas/v4`

---

## API Endpoints

### Authentication
Bearer token authentication for all API requests.

**📖 For complete authentication documentation, see:** [api/authentication.md](api/authentication.md)

---

### Chat Completions
Primary endpoint for conversational AI interactions.

**📖 For complete chat completions documentation, see:** [api/chat-completions.md](api/chat-completions.md)

---

### Embeddings
Generate vector embeddings for text.

**📖 For complete embeddings documentation, see:** [api/embeddings.md](api/embeddings.md)

---

### Files
Upload, manage, and extract content from files.

**📖 For complete files documentation, see:** [api/files.md](api/files.md)

---

### Web Search
Native web search integration (GLM provider only).

**📖 For complete web search documentation, see:** [api/web-search.md](api/web-search.md)

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat/completions` | POST | Conversational AI |
| `/embeddings` | POST | Vector embeddings |
| `/files` | POST | Upload files |
| `/files/{id}` | GET | Retrieve file |
| `/files/{id}/content` | GET | Extract file content |
| `/files/{id}` | DELETE | Delete file |

---

## Related Documentation

- [api/authentication.md](api/authentication.md) - Authentication details
- [api/chat-completions.md](api/chat-completions.md) - Chat completions endpoint
- [api/embeddings.md](api/embeddings.md) - Embeddings endpoint
- [api/files.md](api/files.md) - Files management
- [api/web-search.md](api/web-search.md) - Web search integration
- [02-provider-architecture.md](02-provider-architecture.md) - Provider details
- [04-features-and-capabilities.md](04-features-and-capabilities.md) - Feature details





## 06-deployment-guide.md

**Source:** `docs/system-reference/06-deployment-guide.md`

---

# Deployment Guide

**Version:** 1.0  
**Last Updated:** 2025-10-02  
**Related:** `01-system-overview.md`, `05-api-endpoints-reference.md`

---

## Prerequisites

### System Requirements

**Operating System:**
- Windows 10/11 (PowerShell 5.1+)
- Linux (Ubuntu 20.04+, Debian 11+)
- macOS 11+

**Python:**
- Python 3.8 or higher
- pip package manager
- virtualenv (recommended)

**Network:**
- Internet connection for API access
- Firewall allowing outbound HTTPS (port 443)
- WebSocket support (port 8765 for local server)

### API Access

**Required:**
- Z.ai API key from https://z.ai/manage-apikey/apikey-list
- Active Z.ai account with billing enabled

**Optional:**
- Moonshot (Kimi) API key for Kimi provider
- GitHub account for repository access

---

## Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/EX-AI-MCP-Server.git
cd EX-AI-MCP-Server
```

### Step 2: Create Virtual Environment (Recommended)

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies Installed:**
```
zai-sdk>=0.0.4          # International SDK for api.z.ai
zhipuai>=2.1.0          # Mainland China SDK (dual approach)
websockets>=12.0        # WebSocket server
httpx>=0.27.0           # HTTP client with streaming
pydantic>=2.0           # Data validation
python-dotenv>=1.0.0    # Environment configuration
openai>=1.55.2          # OpenAI-compatible SDK
```

### Step 4: Verify Installation

```bash
python -c "import zai; print(zai.__version__)"
```

Expected output: `0.0.4` or higher

---

## Configuration

### Step 1: Create Environment File

```bash
cp .env.example .env
```

### Step 2: Edit .env File

**Minimum Configuration (GLM Only):**
```env
# GLM Provider (Required)
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/v1

# Server Configuration
MCP_SERVER_PORT=8765
MCP_SERVER_HOST=127.0.0.1

# Streaming (Optional)
GLM_STREAM_ENABLED=true
```

**Full Configuration (GLM + Kimi):**
```env
# GLM Provider (Required)
GLM_API_KEY=your_glm_api_key
GLM_BASE_URL=https://api.z.ai/v1
GLM_DEFAULT_MODEL=glm-4.6
GLM_TEMPERATURE=0.6
GLM_MAX_TOKENS=65536
GLM_STREAM_ENABLED=true

# Kimi Provider (Optional)
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TEMPERATURE=0.5
KIMI_STREAM_ENABLED=true

# Server Configuration
MCP_SERVER_PORT=8765
MCP_SERVER_HOST=127.0.0.1
LOG_LEVEL=INFO

# Manager Configuration
DEFAULT_MANAGER_MODEL=glm-4.5-flash  # Fast manager for routing
ENABLE_AGENTIC_ROUTING=true

# Web Search (Optional)
GLM_ENABLE_WEB_BROWSING=true
DEFAULT_SEARCH_ENGINE=search_pro_jina
```

### Step 3: Validate Configuration

```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('GLM_API_KEY:', 'SET' if os.getenv('GLM_API_KEY') else 'NOT SET')"
```

Expected output: `GLM_API_KEY: SET`

---

## Starting the Server

### Windows

**Using PowerShell Script:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1
```

**Manual Start:**
```powershell
python server.py
```

### Linux/macOS

**Using Shell Script:**
```bash
chmod +x scripts/ws_start.sh
./scripts/ws_start.sh
```

**Manual Start:**
```bash
python3 server.py
```

### Server Output

```
[2025-10-02 10:00:00] INFO: Starting EX-AI-MCP-Server
[2025-10-02 10:00:00] INFO: Loading configuration from .env
[2025-10-02 10:00:00] INFO: GLM provider initialized (base_url=https://api.z.ai/v1)
[2025-10-02 10:00:00] INFO: Kimi provider initialized (base_url=https://api.moonshot.ai/v1)
[2025-10-02 10:00:00] INFO: WebSocket server starting on ws://127.0.0.1:8765
[2025-10-02 10:00:01] INFO: Server ready - accepting connections
```

---

## Verification

### Step 1: Check Server Status

**Check Logs:**
```bash
tail -f .logs/mcp_server.log
```

**Expected Output:**
```
[INFO] Server started successfully
[INFO] Listening on ws://127.0.0.1:8765
[INFO] GLM provider: READY
[INFO] Kimi provider: READY
```

### Step 2: Test WebSocket Connection

**Using wscat (Node.js):**
```bash
npm install -g wscat
wscat -c ws://127.0.0.1:8765
```

**Expected Response:**
```json
{
  "type": "connection_established",
  "server": "EX-AI-MCP-Server",
  "version": "1.0"
}
```

### Step 3: Test Chat Endpoint

**Send Test Message:**
```json
{
  "tool": "chat",
  "params": {
    "prompt": "Hello, are you working?",
    "model": "glm-4.6"
  }
}
```

**Expected Response:**
```json
{
  "type": "response",
  "content": "Yes, I'm working! How can I help you today?",
  "model": "glm-4.6",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

---

## Restarting the Server

### After Code Changes

**Windows:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

**Linux/macOS:**
```bash
./scripts/ws_start.sh --restart
```

### Manual Restart

1. Stop server: `Ctrl+C`
2. Start server: `python server.py`

---

## Troubleshooting

### Issue: "Module not found" Error

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "Invalid API key" Error

**Cause:** API key not set or incorrect

**Solution:**
1. Check `.env` file: `GLM_API_KEY=your_key_here`
2. Verify key at https://z.ai/manage-apikey/apikey-list
3. Restart server after updating `.env`

### Issue: "Connection refused" Error

**Cause:** Server not running or wrong port

**Solution:**
1. Check server is running: `ps aux | grep server.py`
2. Check port in `.env`: `MCP_SERVER_PORT=8765`
3. Check firewall settings

### Issue: "Rate limit exceeded" Error

**Cause:** Too many requests

**Solution:**
1. Wait for rate limit reset (check headers)
2. Implement request throttling
3. Upgrade API plan if needed

### Issue: Streaming Not Working

**Cause:** Streaming not enabled

**Solution:**
1. Check `.env`: `GLM_STREAM_ENABLED=true`
2. Restart server
3. Verify client supports SSE

### Issue: Web Search Not Working

**Cause:** Web search not enabled or configured

**Solution:**
1. Check `.env`: `GLM_ENABLE_WEB_BROWSING=true`
2. Verify model supports web search (GLM-4.6)
3. Check search engine configuration

---

## Production Deployment

### Using systemd (Linux)

**Create Service File:**
```bash
sudo nano /etc/systemd/system/exai-mcp.service
```

**Service Configuration:**
```ini
[Unit]
Description=EX-AI-MCP-Server
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/EX-AI-MCP-Server
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable exai-mcp
sudo systemctl start exai-mcp
```

**Check Status:**
```bash
sudo systemctl status exai-mcp
```

### Using Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8765

CMD ["python", "server.py"]
```

**Build and Run:**
```bash
docker build -t exai-mcp-server .
docker run -d -p 8765:8765 --env-file .env exai-mcp-server
```

### Using Docker Compose

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  exai-mcp:
    build: .
    ports:
      - "8765:8765"
    env_file:
      - .env
    restart: unless-stopped
    volumes:
      - ./logs:/app/.logs
```

**Start:**
```bash
docker-compose up -d
```

---

## Monitoring

### Log Files

**Location:**
```
.logs/mcp_server.log
```

**Rotation:**
- Automatic rotation at 10MB
- Keep last 5 log files
- Compressed older logs

**View Logs:**
```bash
tail -f .logs/mcp_server.log
```

### Health Check Endpoint

**Endpoint:**
```
GET http://127.0.0.1:8765/health
```

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "providers": {
    "glm": "ready",
    "kimi": "ready"
  }
}
```

### Metrics

**Available Metrics:**
- Request count
- Response time
- Error rate
- Token usage
- Provider availability

**Access Metrics:**
```
GET http://127.0.0.1:8765/metrics
```

---

## Security Best Practices

### API Key Management

**DO:**
- Store API keys in `.env` file
- Add `.env` to `.gitignore`
- Use environment variables
- Rotate keys regularly

**DON'T:**
- Commit API keys to Git
- Share API keys publicly
- Hardcode API keys in code
- Use same key across environments

### Network Security

**Recommendations:**
- Run server on localhost only (127.0.0.1)
- Use reverse proxy for external access
- Enable HTTPS for production
- Implement rate limiting
- Use firewall rules

### Access Control

**Recommendations:**
- Implement authentication
- Use API key rotation
- Monitor access logs
- Set up alerts for suspicious activity

---

## Backup and Recovery

### Configuration Backup

**Backup `.env` file:**
```bash
cp .env .env.backup
```

**Backup logs:**
```bash
tar -czf logs-backup-$(date +%Y%m%d).tar.gz .logs/
```

### Disaster Recovery

**Steps:**
1. Restore `.env` from backup
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Restart server
4. Verify functionality

---

## Upgrading

### Minor Version Upgrade

```bash
git pull origin main
pip install -r requirements.txt --upgrade
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart
```

### Major Version Upgrade

1. Read upgrade guide in `docs/upgrades/`
2. Backup configuration and data
3. Follow migration steps
4. Test in staging environment
5. Deploy to production

---

## Support

### Documentation

- **System Reference:** `docs/system-reference/`
- **User Guides:** `docs/guides/`
- **Architecture:** `docs/architecture/`
- **Upgrades:** `docs/upgrades/`

### Community

- **GitHub Issues:** Report bugs and request features
- **Discussions:** Ask questions and share experiences

### Official Resources

- **Z.ai API Docs:** https://docs.z.ai/
- **GLM-4.6 Guide:** https://docs.z.ai/guides/llm/glm-4.6
- **zai-sdk GitHub:** https://github.com/zai-org/z-ai-sdk-python

---

**Next:** Read `07-upgrade-roadmap.md` for current upgrade project status





## 07-upgrade-roadmap.md

**Source:** `docs/system-reference/07-upgrade-roadmap.md`

---

# Upgrade Roadmap: zai-sdk v0.0.4 Integration

**Version:** 2.0
**Last Updated:** 2025-10-02
**Project Status:** Wave 2 - Synthesis & UX Improvements (IN PROGRESS)

---

## Project Overview

### Objective

Upgrade EX-AI-MCP-Server from zai-sdk v0.0.3.3 to v0.0.4, integrate GLM-4.6 with 200K context window, and implement new features (video generation, assistant API, character role-playing) for international users accessing api.z.ai.

**Key Finding:** NO BREAKING CHANGES - zai-sdk v0.0.4 is 100% backward compatible

### Timeline

**Start Date:** 2025-10-01
**Target Completion:** 2025-10-15
**Current Phase:** Wave 2 (Synthesis & UX Improvements)
**Wave 1 Status:** ✅ COMPLETE (100%)

---

## Wave-Based Execution Plan

### Wave 1: Foundation (Research + Independent Docs) - ✅ COMPLETE

**Status:** ✅ 100% Complete

**Track A: Research (CRITICAL PATH)**
- ✅ Task 2.1: Research zai-sdk latest version (v0.0.4)
- ✅ Task 2.2: Research GLM-4.6 specifications (200K context, $0.60/$2.20 pricing)
- ✅ Task 2.3: Research api.z.ai endpoints (comprehensive API documentation)
- ✅ Task 2.4: Breaking changes analysis - **NO BREAKING CHANGES** (100% backward compatible)
- ✅ Task 2.5: New features documentation (CogVideoX-2, Assistant API, CharGLM-3)

**Track B: Independent Documentation**
- ✅ Task 1.1: Create `docs/guides/tool-selection-guide.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.2: Create `docs/guides/parameter-reference.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.3: Create `docs/guides/web-search-guide.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.4: Create `docs/guides/query-examples.md` (validated with codereview_EXAI-WS)
- ✅ Task 1.5: Create `docs/guides/troubleshooting.md` (validated with codereview_EXAI-WS)

**Validation Checkpoint:**
- ✅ All documentation validated with `codereview_EXAI-WS`
- ✅ Research findings verified against official sources (web-search)
- ✅ All deliverables reviewed with `analyze_EXAI-WS` (100% quality metrics)
- ✅ **Decision: PROCEED TO WAVE 2**

**Deliverables:** 24 files (~290KB documentation)

---

### Wave 2: Synthesis & UX (Research Synthesis + UX Improvements)

**Status:** IN PROGRESS (Epic 2.1 COMPLETE)

**Epic 2.1: Research Synthesis & Documentation Rewrite** ✅ COMPLETE
- ✅ Synthesize all Wave 1 research findings
- ✅ Create comprehensive research synthesis document (wave2-research-synthesis.md)
- ✅ Create updated implementation plan (wave2-implementation-plan.md)
- ✅ Document NO BREAKING CHANGES finding
- ✅ Document GLM-4.6 specifications (200K context, 355B/32B MoE)
- ✅ Document Kimi K2 specifications (256K context, 1T/32B MoE)
- ✅ Document new features (CogVideoX-2, Assistant API, CharGLM-3)

**Epic 2.2: Web Search Prompt Injection Fix** (HIGH PRIORITY)
- Fix chat_EXAI-WS web search issue
- Implement context-aware search triggers
- Test with various query types

**Epic 2.3: EXAI Tool UX Improvements**
- Implement dynamic context-aware messaging (continuation_id)
- Improve path validation error messages
- Add flexible tool parameters

**Epic 2.4: Diagnostic Tools & Logging**
- Create diagnostic tools for debugging
- Add comprehensive logging
- Implement progress indicators

**Epic 2.5: Wave 2 Validation & Testing**
- Test all UX improvements
- Validate web search fix
- Ensure no regressions
- **Decision Gate:** Proceed to Wave 3?

**Validation Checkpoint:**
- Review synthesized documentation ✅
- Test UX improvements (pending)
- Verify web search fix works correctly (pending)

---

### Wave 3: Core SDK Upgrade (Requirements + Provider + GLM-4.6)

**Status:** Not Started

**Tasks:**
- Task 5.1: Update `requirements.txt` (zai-sdk>=0.0.4)
- Task 5.2: Update `src/providers/glm_chat.py` for GLM-4.6
- Task 5.3: Implement 200K context window support
- Task 5.4: Update pricing configuration
- Task 5.5: Test streaming with new SDK
- Task 5.6: Test tool calling with new SDK
- Task 5.7: Verify backward compatibility

**Validation Checkpoint:**
- Run smoke tests with GLM-4.6
- Verify streaming works
- Verify tool calling works
- Confirm backward compatibility

---

### Wave 4: New Features (Video + Assistant + Character RP)

**Status:** Not Started

**Video Generation (CogVideoX-2):**
- Task 6.1: Implement video generation endpoint
- Task 6.2: Add async task polling
- Task 6.3: Create video generation tool
- Task 6.4: Add video generation examples

**Assistant API:**
- Task 7.1: Implement assistant conversation endpoint
- Task 7.2: Add metadata and attachment support
- Task 7.3: Create assistant tool
- Task 7.4: Add assistant examples

**Character Role-Playing (CharGLM-3):**
- Task 8.1: Implement character RP endpoint
- Task 8.2: Add meta parameter support
- Task 8.3: Create character RP tool
- Task 8.4: Add character RP examples

**Validation Checkpoint:**
- Test each new feature independently
- Verify integration with existing system
- Validate examples work correctly

---

### Wave 5: Testing & Validation

**Status:** Not Started

**Tasks:**
- Task 9.1: Create comprehensive test suite
- Task 9.2: Run integration tests
- Task 9.3: Perform security audit
- Task 9.4: Load testing and performance validation
- Task 9.5: Verify turnkey deployment
- Task 9.6: Test all documentation examples

**Validation Checkpoint:**
- All tests passing
- No security vulnerabilities
- Performance meets requirements
- Turnkey deployment verified

---

### Wave 6: Finalization (README + Sign-off)

**Status:** Not Started

**Tasks:**
- Task 10.1: Update main README.md
- Task 10.2: Create release notes
- Task 10.3: Update changelog
- Task 10.4: Final documentation review
- Task 10.5: Create upgrade guide for existing users
- Task 10.6: Tag release and push to GitHub

**Validation Checkpoint:**
- Final review complete
- All documentation accurate
- Release notes comprehensive
- Ready for production

---

## Research Findings (Wave 1)

### zai-sdk v0.0.4 (Task 2.1)

**Release Date:** September 30, 2025  
**Current Version:** v0.0.3.3  
**Upgrade Path:** 0.0.3.3 → 0.0.4

**Key Features:**
- Chat Completions (standard, streaming, tool calling, character RP, multimodal)
- Embeddings
- Video Generation (CogVideoX-2)
- Audio Processing
- Assistant API
- Web Search integration
- File Management
- Content Moderation
- Image Generation

**Installation:**
```bash
pip install zai-sdk>=0.0.4
```

**GitHub:** https://github.com/zai-org/z-ai-sdk-python  
**Python Support:** 3.8, 3.9, 3.10, 3.11, 3.12

---

### GLM-4.6 Specifications (Task 2.2)

**Release Date:** September 30, 2025

**Key Improvements:**
- **Context Window:** 200,000 tokens (expanded from 128K)
- **Pricing:** $0.60 input / $2.20 output per million tokens (1/5th cost of Claude Sonnet 4)
- **Performance:** Near parity with Claude Sonnet 4 (48.6% win rate)
- **Token Efficiency:** ~15% fewer tokens than GLM-4.5
- **Capabilities:** Advanced agentic abilities, superior coding, advanced reasoning, refined writing

**Benchmarks:**
- Near parity with Claude Sonnet 4
- Lags behind Claude Sonnet 4.5 in coding tasks
- Superior agentic abilities
- Advanced reasoning capabilities

**Official Documentation:** https://docs.z.ai/guides/llm/glm-4.6

---

### api.z.ai Endpoints (Task 2.3)

**Base URL:** `https://api.z.ai/api/paas/v4/`

**Authentication:** Bearer token (`Authorization: Bearer <token>`)

**Main Endpoints:**

1. **Chat Completions:** `POST /paas/v4/chat/completions`
   - Multimodal inputs (text, images, audio, video, files)
   - Streaming support
   - Tool calling (function, web search, retrieval)
   - Models: glm-4.6, glm-4.5, glm-4.5-air, glm-4.5-x, glm-4.5-airx, glm-4.5-flash

2. **Video Generation:** `POST /paas/v4/videos/generations` (async)
   - Model: cogvideox-2
   - Text-to-video and image-to-video
   - Customizable quality, FPS, size
   - Audio support

3. **Web Search Tool:** Integrated into chat completions
   - Search engines: search_pro_jina (default), search_pro_bing
   - Recency filters, domain whitelisting
   - Content size control, result sequencing

4. **Assistant API:** `POST /paas/v4/assistant/conversation`
   - Model: glm-4-assistant
   - Structured conversations
   - Metadata and attachments

5. **File Upload:** `POST /paas/v4/files/upload`
   - Multimodal chat support
   - Document analysis

6. **Embeddings:** Generate text embeddings
   - Configurable dimensions
   - Batch processing

**OpenAI Compatibility:**
- Full OpenAI-compatible API interface
- Drop-in replacement for OpenAI API
- Compatible with Claude Code, Kilo Code, Roo Code, Cline

---

## Breaking Changes (Task 2.4 - PENDING)

**To Be Determined:**
- API signature changes
- Parameter deprecations
- Response format changes
- Migration steps

**Analysis Method:**
- Use `analyze_EXAI-WS` to compare SDK versions
- Review zai-sdk changelog
- Test backward compatibility

---

## New Features Documentation (Task 2.5 - PENDING)

### CogVideoX-2 (Video Generation)

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Examples (text-to-video, image-to-video)
- Best practices

### Assistant API

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Conversation management
- Examples

### CharGLM-3 (Character Role-Playing)

**To Be Documented:**
- Capabilities and use cases
- API usage and parameters
- Character creation
- Examples

---

## Known Issues

### Web Search Prompt Injection (Wave 2 Fix)

**Issue:** chat_EXAI-WS with `use_websearch=true` responds with "SEARCH REQUIRED: Please immediately perform a web search..." instead of autonomously executing searches.

**Root Cause:** System prompt not sufficiently agentic to trigger autonomous web search behavior.

**Workaround:** Use web-search tool directly for now.

**Planned Fix:** Update chat tool system prompts in Wave 2 (UX Improvements).

**Impact:** Slows research tasks but doesn't block progress.

---

## Success Criteria

### Wave 1 (Current)
- ✅ All research findings documented with accurate sources
- ⏳ 5 user guides created and validated with codereview_EXAI-WS
- ⏳ Wave 1 validation checkpoint passed
- ⏳ Ready to proceed to Wave 2

### Wave 2
- Research synthesis complete
- UX improvements implemented
- Web search issue fixed
- Documentation updated

### Wave 3
- zai-sdk v0.0.4 installed
- GLM-4.6 integrated
- 200K context window working
- Backward compatibility verified

### Wave 4
- Video generation working
- Assistant API working
- Character RP working
- All examples tested

### Wave 5
- All tests passing
- No security vulnerabilities
- Performance validated
- Turnkey deployment verified

### Wave 6
- Documentation complete
- Release notes published
- Upgrade guide available
- Production ready

---

## Dependencies

### External Dependencies
- zai-sdk v0.0.4 (PyPI)
- Z.ai API access (api.z.ai)
- GitHub repository access

### Internal Dependencies
- Phase 0: Architecture & Design (COMPLETE)
- Phase 1: EXAI Recommendations + Dynamic Step Management (COMPLETE)
- Phase 1 Follow-Up: Meta-validation fixes (COMPLETE)

---

## Risk Assessment

### High Risk
- Breaking changes in zai-sdk v0.0.4 (mitigation: thorough testing)
- Web search integration issues (mitigation: Wave 2 fix planned)

### Medium Risk
- New feature integration complexity (mitigation: incremental implementation)
- Backward compatibility (mitigation: comprehensive testing)

### Low Risk
- Documentation accuracy (mitigation: EXAI validation)
- Performance regression (mitigation: load testing)

---

## Next Steps

### Immediate (Wave 1 Completion)
1. Complete Task 2.4: Identify breaking changes using analyze_EXAI-WS
2. Complete Task 2.5: Document new features using chat_EXAI-WS with web search
3. Create 5 user guides (Tasks 1.1-1.5)
4. Validate all documentation with codereview_EXAI-WS
5. Push Wave 1 changes to GitHub

### Short-term (Wave 2)
1. Synthesize research findings
2. Fix web search prompt injection issue
3. Rewrite upgrade documentation
4. Improve UX

### Medium-term (Waves 3-4)
1. Upgrade to zai-sdk v0.0.4
2. Integrate GLM-4.6
3. Implement new features

### Long-term (Waves 5-6)
1. Comprehensive testing
2. Final documentation
3. Release preparation

---

## Progress Tracking

**Overall Progress:** 15% (Wave 1: 60%, Waves 2-6: 0%)

**Completed:**
- ✅ Preliminary Step: Current state analysis
- ✅ Task 2.1: zai-sdk version research
- ✅ Task 2.2: GLM-4.6 specifications research
- ✅ Task 2.3: api.z.ai endpoints research

**In Progress:**
- ⏳ Task 2.4: Breaking changes identification
- ⏳ Task 2.5: New features documentation
- ⏳ Tasks 1.1-1.5: User guides creation

**Pending:**
- Waves 2-6 (all tasks)

---

**Last Updated:** 2025-10-02  
**Next Review:** After Wave 1 completion  
**Document Owner:** Development Team





## api\authentication.md

**Source:** `docs/system-reference/api\authentication.md`

---

# Authentication

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

Bearer token authentication for all API requests. Both GLM and Kimi providers use the same authentication mechanism.

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_API_KEY=your_zhipuai_api_key
```

**Kimi Provider:**
```env
KIMI_API_KEY=your_moonshot_api_key
```

---

## Authentication Methods

### Bearer Token (Recommended)

**HTTP Header:**
```http
Authorization: Bearer your_api_key
```

**Python Example:**
```python
from openai import OpenAI

# GLM
glm_client = OpenAI(
    api_key="your_zhipuai_api_key",
    base_url="https://api.z.ai/v1"
)

# Kimi
kimi_client = OpenAI(
    api_key="your_moonshot_api_key",
    base_url="https://api.moonshot.ai/v1"
)
```

---

## Security Best Practices

### API Key Management

- **Never commit API keys** to version control
- **Use environment variables** for API keys
- **Rotate keys regularly** for security
- **Use separate keys** for development and production
- **Monitor API usage** for anomalies

### Environment Files

**.env (Local Development):**
```env
GLM_API_KEY=your_zhipuai_api_key
KIMI_API_KEY=your_moonshot_api_key
```

**.env.example (Template):**
```env
GLM_API_KEY=your_zhipuai_api_key_here
KIMI_API_KEY=your_moonshot_api_key_here
```

---

## Error Handling

### Invalid API Key

**Response:**
```json
{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Missing API Key

**Response:**
```json
{
  "error": {
    "message": "Missing API key",
    "type": "invalid_request_error",
    "code": "missing_api_key"
  }
}
```

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider details
- [chat-completions.md](chat-completions.md) - Chat completions API





## api\chat-completions.md

**Source:** `docs/system-reference/api\chat-completions.md`

---

# Chat Completions API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Primary endpoint for conversational AI interactions. OpenAI-compatible API for both GLM and Kimi providers.

---

## Endpoint

**POST** `/chat/completions`

**Base URLs:**
- GLM: `https://api.z.ai/v1/chat/completions`
- Kimi: `https://api.moonshot.ai/v1/chat/completions`

---

## Request

### Basic Request

```json
{
  "model": "glm-4.6",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model to use (e.g., "glm-4.6", "kimi-k2-0905-preview") |
| `messages` | array | Yes | Array of message objects |
| `temperature` | float | No | Sampling temperature (0.0-1.0, default: 0.7) |
| `max_tokens` | integer | No | Maximum tokens to generate |
| `stream` | boolean | No | Enable streaming (default: false) |
| `tools` | array | No | Function calling tools |
| `tool_choice` | string | No | Tool selection strategy ("auto", "none", specific tool) |

---

## Response

### Non-Streaming Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "glm-4.6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Streaming Response

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"glm-4.6","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)
```

### Streaming

```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../features/streaming.md](../features/streaming.md) - Streaming support
- [../features/tool-calling.md](../features/tool-calling.md) - Tool calling





## api\embeddings.md

**Source:** `docs/system-reference/api\embeddings.md`

---

# Embeddings API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Generate vector embeddings for text. Useful for semantic search, clustering, and similarity comparisons.

---

## Endpoint

**POST** `/embeddings`

**Base URLs:**
- GLM: `https://api.z.ai/v1/embeddings`
- Kimi: Not available (GLM only)

---

## Request

### Basic Request

```json
{
  "model": "embedding-3",
  "input": "The quick brown fox jumps over the lazy dog"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Embedding model (e.g., "embedding-3") |
| `input` | string or array | Yes | Text to embed (string or array of strings) |
| `encoding_format` | string | No | Format for embeddings ("float", "base64") |

---

## Response

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "index": 0,
      "embedding": [0.123, -0.456, 0.789, ...]
    }
  ],
  "model": "embedding-3",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_glm_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.embeddings.create(
    model="embedding-3",
    input="The quick brown fox jumps over the lazy dog"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")
```

### Batch Embeddings

```python
response = client.embeddings.create(
    model="embedding-3",
    input=[
        "First text to embed",
        "Second text to embed",
        "Third text to embed"
    ]
)

for i, data in enumerate(response.data):
    print(f"Embedding {i}: {len(data.embedding)} dimensions")
```

---

## Use Cases

### Semantic Search
- Index documents with embeddings
- Search by semantic similarity
- Rank results by cosine similarity

### Clustering
- Group similar texts together
- Identify topics and themes
- Detect duplicates

### Similarity Comparison
- Compare text similarity
- Find related content
- Recommend similar items

---

## Provider Support

| Provider | Embeddings Support |
|----------|-------------------|
| GLM | ✅ embedding-3 model |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../providers/glm.md](../providers/glm.md) - GLM provider details





## api\files.md

**Source:** `docs/system-reference/api\files.md`

---

# Files API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [authentication.md](authentication.md)

---

## Overview

Upload, manage, and extract content from files. Both GLM and Kimi providers support file operations.

---

## Endpoints

### Upload File

**POST** `/files`

**Base URLs:**
- GLM: `https://api.z.ai/v1/files`
- Kimi: `https://api.moonshot.ai/v1/files`

### Retrieve File

**GET** `/files/{file_id}`

### Extract File Content

**GET** `/files/{file_id}/content`

### Delete File

**DELETE** `/files/{file_id}`

---

## Upload File

### Request

```python
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677652288,
  "filename": "document.pdf",
  "purpose": "file-extract"
}
```

---

## Retrieve File

### Request

```python
file = client.files.retrieve("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677652288,
  "filename": "document.pdf",
  "purpose": "file-extract"
}
```

---

## Extract File Content

### Request

```python
content = client.files.content("file-abc123")
```

### Response

```json
{
  "content": "Extracted text content from the file...",
  "file_id": "file-abc123"
}
```

---

## Delete File

### Request

```python
client.files.delete("file-abc123")
```

### Response

```json
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

---

## Use with Chat Completions

```python
# Upload file
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

# Use in chat
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": file.id},
        {"role": "user", "content": "Summarize this document"}
    ]
)

# Delete file after use
client.files.delete(file.id)
```

---

## Supported File Types

### GLM Provider
- PDF, DOCX, TXT, MD
- Images (JPEG, PNG, GIF, WebP)
- Audio (MP3, WAV, FLAC)
- Video (MP4, AVI, MOV)

### Kimi Provider
- PDF, DOCX, TXT, MD
- Text-based files only

---

## Best Practices

### File Management
- **Delete files after use** to avoid accumulation
- **Track file IDs** for cleanup
- **Verify cleanup** with `files.list()` API
- **Use batch uploads** for multiple files

### Size Limits
- **GLM:** 100MB per file
- **Kimi:** 100MB per file

---

## Provider Support

| Provider | Files Support |
|----------|--------------|
| GLM | ✅ Full support |
| Kimi | ✅ Full support |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [authentication.md](authentication.md) - Authentication details
- [../features/multimodal.md](../features/multimodal.md) - Multimodal support
- [../providers/kimi.md](../providers/kimi.md) - Kimi file management best practices





## api\web-search.md

**Source:** `docs/system-reference/api\web-search.md`

---

# Web Search API

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md), [../features/web-search.md](../features/web-search.md)

---

## Overview

Native web search integration for GLM provider. Web search is automatically triggered by query content without manual intervention.

**Note:** Web search is only available for GLM provider, not Kimi.

---

## Endpoint

**POST** `/api/paas/v4/web_search`

**Base URL:**
- GLM: `https://api.z.ai/api/paas/v4/web_search`

---

## Configuration

### Environment Variables

```env
GLM_ENABLE_WEB_BROWSING=true
```

---

## Request

### Basic Request

```json
{
  "model": "glm-4.6",
  "messages": [
    {"role": "user", "content": "What's the latest news about AI?"}
  ],
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek"
      }
    }
  ]
}
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search_engine` | string | Search engine ("search_pro_jina", "search_pro_bing") |
| `search_recency_filter` | string | Time range ("oneDay", "oneWeek", "oneMonth", "oneYear", "noLimit") |
| `domain_whitelist` | array | Limit to specific domains |
| `content_size` | string | Summary length ("medium": 400-600 chars, "high": 2500 chars) |
| `result_sequence` | string | Show results "before" or "after" response |
| `search_result` | boolean | Whether to return search results |
| `require_search` | boolean | Force model to use search results |
| `search_prompt` | string | Custom prompt for processing results |

---

## Response

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "glm-4.6",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on recent news...",
        "web_search_results": [
          {
            "title": "Latest AI Developments",
            "url": "https://example.com/ai-news",
            "snippet": "Recent advancements in AI..."
          }
        ]
      },
      "finish_reason": "stop"
    }
  ]
}
```

---

## Examples

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_glm_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "What's the latest news about AI?"}
    ],
    tools=[
        {
            "type": "web_search",
            "web_search": {
                "search_engine": "search_pro_jina",
                "search_recency_filter": "oneWeek"
            }
        }
    ]
)

print(response.choices[0].message.content)
```

---

## Search Engines

### Jina AI Search (Default)
- **ID:** `search_pro_jina`
- **Features:** Fast, comprehensive results
- **Best For:** General web search

### Bing Search
- **ID:** `search_pro_bing`
- **Features:** Microsoft Bing integration
- **Best For:** Enterprise search

---

## Provider Support

| Provider | Web Search Support |
|----------|-------------------|
| GLM | ✅ Native integration |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../05-api-endpoints-reference.md](../05-api-endpoints-reference.md) - API endpoints overview
- [../features/web-search.md](../features/web-search.md) - Web search features
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [chat-completions.md](chat-completions.md) - Chat completions API





## features\caching.md

**Source:** `docs/system-reference/features\caching.md`

---

# Caching

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/kimi.md](../providers/kimi.md)

---

## Overview

Prompt caching and advanced caching strategies for improved performance and cost reduction. Both GLM and Kimi providers support caching with different implementations.

---

## Provider Support

### GLM Provider - Prompt Caching

**Features:**
- Automatic prompt caching
- Reduced costs for repeated prompts
- Faster response times

**Configuration:**
```env
GLM_ENABLE_CACHING=true
```

### Kimi Provider - Advanced Caching

**Features:**
- Automatic prompt caching
- Up to 90% cost reduction for repeated prompts
- Significantly faster response times
- No configuration required

**Benefits:**
- Ideal for iterative workflows
- Reduced costs for repeated queries
- Faster response times for cached content

---

## Caching Strategies

### Automatic Caching
- Both providers cache prompts automatically
- No manual configuration required
- Transparent to the user

### Cache Invalidation
- Caches expire after a certain period
- New prompts invalidate old caches
- Provider-managed cache lifecycle

---

## Best Practices

- Use consistent prompts for better caching
- Leverage caching for iterative workflows
- Monitor cache hit rates for optimization
- Use Kimi for maximum caching benefits

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM caching details
- [../providers/kimi.md](../providers/kimi.md) - Kimi caching details





## features\multimodal.md

**Source:** `docs/system-reference/features\multimodal.md`

---

# Multimodal Support

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/glm.md](../providers/glm.md)

---

## Overview

Process images, audio, video, and files alongside text for comprehensive AI interactions. Multimodal support is available for GLM provider only.

**Note:** Multimodal support is only available for GLM provider, not Kimi.

---

## Supported Modalities

### Images
- **Models:** GLM-4.5V, GLM-4.5V-plus
- **Formats:** JPEG, PNG, GIF, WebP
- **Max Size:** 20MB per image
- **Use Cases:** Image analysis, OCR, visual Q&A

### Audio
- **Models:** GLM-4-audio
- **Formats:** MP3, WAV, FLAC
- **Max Duration:** 30 minutes
- **Use Cases:** Transcription, audio analysis

### Video
- **Models:** GLM-4V-flash
- **Formats:** MP4, AVI, MOV
- **Max Duration:** 10 minutes
- **Use Cases:** Video analysis, content extraction

### Files
- **Models:** All GLM models
- **Formats:** PDF, DOCX, TXT, MD
- **Max Size:** 100MB per file
- **Use Cases:** Document analysis, content extraction

---

## Usage

### Image Analysis

```python
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "https://..."}}
            ]
        }
    ]
)
```

### File Upload

```python
# Upload file
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

# Use in chat
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": file.id},
        {"role": "user", "content": "Summarize this document"}
    ]
)
```

---

## Provider Support

| Provider | Multimodal Support |
|----------|-------------------|
| GLM | ✅ Images, audio, video, files |
| Kimi | ❌ Text only |

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [../api/files.md](../api/files.md) - File management API





## features\streaming.md

**Source:** `docs/system-reference/features\streaming.md`

---

# Streaming Support

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

The EX-AI-MCP-Server provides real-time streaming support for both GLM and Kimi providers using Server-Sent Events (SSE) protocol. Streaming enables token-by-token delivery for better user experience and lower perceived latency.

---

## Configuration

### Environment Variables

**GLM Provider:**
```env
GLM_STREAM_ENABLED=true
```

**Kimi Provider:**
```env
KIMI_STREAM_ENABLED=true
```

---

## Benefits

- **Real-time response generation** - See responses as they're generated
- **Lower perceived latency** - Immediate feedback instead of waiting for complete response
- **Better user experience** - Progressive display of long responses
- **Token-by-token delivery** - Smooth streaming without buffering
- **Immediate feedback** - Users see progress immediately

---

## Implementation

### Server-Sent Events (SSE) Protocol

**Automatic chunk aggregation:**
- Chunks are aggregated automatically
- Metadata tracking (`metadata.streamed = true`)
- Graceful fallback to non-streaming if errors occur

**Usage:**
```python
response = await client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

async for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Provider Support

| Provider | Streaming Support | Protocol |
|----------|------------------|----------|
| GLM | ✅ Yes | SSE |
| Kimi | ✅ Yes | SSE |

---

## Best Practices

- Enable streaming for long responses
- Handle connection interruptions gracefully
- Aggregate chunks for display
- Monitor metadata for streaming status
- Use fallback for non-streaming scenarios

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM streaming details
- [../providers/kimi.md](../providers/kimi.md) - Kimi streaming details





## features\tool-calling.md

**Source:** `docs/system-reference/features\tool-calling.md`

---

# Tool Calling

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../03-tool-ecosystem.md](../03-tool-ecosystem.md)

---

## Overview

OpenAI-compatible function calling for agentic workflows and tool integration. Both GLM and Kimi providers support tool calling with the same API.

---

## Configuration

**Environment Variables:**
```env
# Enable tool calling
GLM_ENABLE_TOOL_CALLING=true
KIMI_ENABLE_TOOL_CALLING=true
```

---

## Usage

### Define Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### Call with Tools

```python
response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        # Execute function and return result
```

---

## Provider Support

| Provider | Tool Calling Support |
|----------|---------------------|
| GLM | ✅ OpenAI-compatible |
| Kimi | ✅ OpenAI-compatible |

---

## Best Practices

- Define clear function descriptions
- Use strict parameter schemas
- Handle tool call errors gracefully
- Return structured results
- Use Kimi for complex tool workflows

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../03-tool-ecosystem.md](../03-tool-ecosystem.md) - Available tools
- [../providers/glm.md](../providers/glm.md) - GLM tool calling
- [../providers/kimi.md](../providers/kimi.md) - Kimi tool calling





## features\web-search.md

**Source:** `docs/system-reference/features\web-search.md`

---

# Web Search Integration

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [../04-features-and-capabilities.md](../04-features-and-capabilities.md), [../providers/glm.md](../providers/glm.md)

---

## Overview

Native GLM web search integration with automatic triggering and multiple search engine support. Web search is automatically triggered by query content without manual intervention.

**Note:** Web search is only available for GLM provider, not Kimi.

---

## Configuration

### Environment Variables

```env
GLM_ENABLE_WEB_BROWSING=true
```

---

## Search Engines

- `search_pro_jina` (default) - Jina AI search
- `search_pro_bing` - Bing search

---

## Parameters

**Search Configuration:**
```json
{
  "tools": [
    {
      "type": "web_search",
      "web_search": {
        "search_engine": "search_pro_jina",
        "search_recency_filter": "oneWeek",
        "content_size": "medium",
        "result_sequence": "after",
        "search_result": true
      }
    }
  ]
}
```

**Parameters:**
- `search_engine`: Which search engine to use
- `search_recency_filter`: Time range (oneDay, oneWeek, oneMonth, oneYear, noLimit)
- `domain_whitelist`: Limit to specific domains
- `content_size`: Summary length (medium: 400-600 chars, high: 2500 chars)
- `result_sequence`: Show results before or after response
- `search_result`: Whether to return search results
- `require_search`: Force model to use search results
- `search_prompt`: Custom prompt for processing results

---

## Usage

Web search is automatically triggered when the query content suggests it would be helpful. No manual search required.

---

## Provider Support

| Provider | Web Search Support |
|----------|-------------------|
| GLM | ✅ Native integration |
| Kimi | ❌ Not available |

---

## Related Documentation

- [../04-features-and-capabilities.md](../04-features-and-capabilities.md) - Features overview
- [../providers/glm.md](../providers/glm.md) - GLM provider details
- [../api/web-search.md](../api/web-search.md) - Web search API





## providers\glm.md

**Source:** `docs/system-reference/providers\glm.md`

---

# GLM Provider (ZhipuAI/Z.ai)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [kimi.md](kimi.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## GLM Provider (ZhipuAI/Z.ai)

### Configuration

**Environment Variables:**
```env
# Required
GLM_API_KEY=your_api_key_here
GLM_BASE_URL=https://api.z.ai/v1

# Optional
GLM_STREAM_ENABLED=true
GLM_DEFAULT_MODEL=glm-4.6
GLM_TEMPERATURE=0.6
GLM_MAX_TOKENS=65536
```

### Available Models

**GLM-4.6 Series (Latest - September 30, 2025):**
- `glm-4.6` - Flagship model with 200K context window
  - **Context:** 200,000 tokens (expanded from 128K)
  - **Pricing:** $0.60 input / $2.20 output per million tokens
  - **Performance:** Near parity with Claude Sonnet 4 (48.6% win rate)
  - **Features:** Advanced agentic abilities, superior coding, refined writing
  - **Token Efficiency:** ~15% fewer tokens than GLM-4.5

**GLM-4.5 Series:**
- `glm-4.5` - Previous flagship with 128K context
- `glm-4.5-air` - Lightweight version
- `glm-4.5-x` - Extended capabilities
- `glm-4.5-airx` - Air extended
- `glm-4.5-flash` - Fast, cost-effective (default manager)

**GLM-4.5V Series (Vision):**
- `glm-4.5v` - Vision model with multimodal support
- `glm-4.5v-plus` - Enhanced vision capabilities

**Legacy:**
- `glm-4-32b-0414-128k` - 32B parameter model

### SDK Integration (zai-sdk v0.0.4)

**Installation:**
```bash
pip install zai-sdk>=0.0.4
```

**Basic Usage:**
```python
from zai import ZAI

client = ZAI(
    api_key="your_api_key",
    base_url="https://api.z.ai/v1"
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.6,
    max_tokens=65536,
    stream=False
)
```

**Streaming:**
```python
stream = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

**Tool Calling:**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[...],
    tools=tools,
    tool_choice="auto"
)
```

### HTTP Fallback

**Direct API Call:**
```python
import httpx

response = httpx.post(
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "glm-4.6",
        "messages": [...],
        "temperature": 0.6,
        "max_tokens": 65536,
        "stream": False
    }
)
```

**SSE Streaming:**
```python
with httpx.stream(
    "POST",
    "https://api.z.ai/api/paas/v4/chat/completions",
    headers={...},
    json={..., "stream": True}
) as stream:
    for line in stream.iter_lines():
        if line.startswith("data: "):
            data = line[6:]
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            # Process chunk
```

### Implementation Pattern

**Dual SDK/HTTP Approach:**
```python
def generate_content(
    sdk_client: Any,
    http_client: Any,
    prompt: str,
    model_name: str,
    use_sdk: bool = True,
    **kwargs
) -> ModelResponse:
    """Generate content with SDK/HTTP fallback."""
    
    if use_sdk and sdk_client:
        try:
            # Primary: Use SDK
            response = sdk_client.chat.completions.create(
                model=model_name,
                messages=[...],
                **kwargs
            )
            return response
        except Exception as e:
            logger.warning(f"SDK failed: {e}, falling back to HTTP")
            use_sdk = False
    
    if not use_sdk and http_client:
        # Fallback: Use HTTP
        response = http_client.post(
            f"{base_url}/chat/completions",
            json={...}
        )
        return response
```

---




## providers\kimi.md

**Source:** `docs/system-reference/providers\kimi.md`

---

# Kimi Provider (Moonshot)

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [glm.md](glm.md), [routing.md](routing.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Configuration

**Environment Variables:**
```env
# Required
KIMI_API_KEY=your_moonshot_api_key
KIMI_BASE_URL=https://api.moonshot.ai/v1

# Optional
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TEMPERATURE=0.5
KIMI_MAX_TOKENS=32768
```

---

## Available Models

### K2 Series (Agentic Intelligence)

**kimi-k2-0905-preview** - Latest K2 **[RECOMMENDED]**
- **Context:** 256K tokens
- **Architecture:** 1T/32B MoE (Mixture of Experts)
- **Pricing:** $0.60 input / $2.50 output per million tokens
- **Features:** Enhanced coding, tool-calling, agentic workflows
- **Performance:** SOTA on SWE Bench Verified, Tau2, AceBench (among open models)
- **Use Case:** Production deployments with version pinning for stability

**kimi-k2-0711-preview** - Original K2
- **Context:** 256K tokens
- **Features:** Original K2 capabilities
- **Use Case:** Legacy compatibility

### Legacy Models

- `moonshot-v1-128k` - 128K context window (superseded by K2)
- `moonshot-v1-32k` - 32K context window (legacy)
- `moonshot-v1-8k` - 8K context window (legacy)

**Note:** Use `kimi-k2-0905-preview` for production (version pinning ensures stability)

---

## SDK Integration

### OpenAI-Compatible API

**Installation:**
```bash
pip install openai>=1.55.2
```

**Basic Usage:**
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_moonshot_api_key",
    base_url="https://api.moonshot.ai/v1"
)

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.5
)
```

### Streaming Support

```python
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[...],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

---

## Features

### Advanced Caching

**Automatic Prompt Caching:**
- Caches repeated prompts automatically
- Reduced costs for repeated queries
- Faster response times for cached content
- No configuration required

**Benefits:**
- Up to 90% cost reduction for repeated prompts
- Significantly faster response times
- Ideal for iterative workflows

### Quality Reasoning

**Superior Reasoning Capabilities:**
- Better for complex analysis and problem-solving
- Excellent for long-context tasks (256K tokens)
- Strong performance on coding benchmarks
- Advanced tool-calling and agentic workflows

**Best For:**
- Code generation and debugging
- Long-context analysis
- Complex reasoning chains
- Agentic workflows with tool use

---

## File Management

### Upload Files

```python
# Upload file
file = client.files.create(
    file=open("document.pdf", "rb"),
    purpose="file-extract"
)

# Use in chat
response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "system",
            "content": file.id  # Reference uploaded file
        },
        {
            "role": "user",
            "content": "Summarize this document"
        }
    ]
)
```

### Extract File Content

```python
# Extract content from uploaded file
content = client.files.content(file.id)
print(content.text)
```

### Delete Files

```python
# Delete file after use
client.files.delete(file.id)
```

**Best Practices:**
- Delete files after use to avoid accumulation
- Use batch uploads for multiple files
- Track file IDs for cleanup
- Verify cleanup with `files.list()` API

---

## Use Cases

### Code Generation & Debugging
- Superior coding capabilities
- Excellent for complex algorithms
- Strong debugging assistance

### Long-Context Analysis
- 256K token context window
- Ideal for large codebases
- Comprehensive document analysis

### Agentic Workflows
- Advanced tool-calling
- Multi-step reasoning
- Complex task orchestration

### Quality Reasoning
- Complex problem-solving
- Detailed analysis
- High-quality outputs

---

## Performance Characteristics

**Strengths:**
- Long context processing (256K tokens)
- Quality reasoning and analysis
- Advanced caching for cost reduction
- Strong coding and tool-calling

**Considerations:**
- Slightly higher cost than GLM ($0.60/$2.50 vs $0.60/$2.20)
- No native web search (use GLM for web search)
- Text-only (no multimodal support)

---

## Related Documentation

- [glm.md](glm.md) - GLM provider details
- [routing.md](routing.md) - Agentic routing logic
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider architecture overview
- [../api/files.md](../api/files.md) - File management API
- [../features/caching.md](../features/caching.md) - Caching strategies





## providers\routing.md

**Source:** `docs/system-reference/providers\routing.md`

---

# Agentic Routing

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Related:** [glm.md](glm.md), [kimi.md](kimi.md), [../02-provider-architecture.md](../02-provider-architecture.md)

---

## Overview

The EX-AI-MCP-Server implements a **manager-first routing architecture** that intelligently routes requests between GLM and Kimi providers based on task complexity, cost optimization, and capability requirements.

---

## Manager-First Architecture

### Default Manager: GLM-4.5-flash

**Purpose:**
- Fast, cost-effective routing decisions
- Initial task classification
- Simple task handling

**Characteristics:**
- Low latency (~100ms response time)
- Cost-effective ($0.05/$0.15 per M tokens)
- Sufficient for 70% of tasks

---

## Routing Logic

### Task Classification

**Simple Tasks → GLM-4.5-flash:**
- General questions
- Basic code explanations
- Simple refactoring suggestions
- Quick documentation lookups

**Complex Tasks → GLM-4.6:**
- Detailed code analysis
- Architecture design
- Performance optimization
- Security audits

**Specialized Tasks → Kimi:**
- Long context analysis (>100K tokens)
- Complex reasoning chains
- Agentic workflows
- Tool-heavy operations

---

## Escalation Strategy

**Level 1: GLM-4.5-flash (Manager)**
- Initial request handling
- Task complexity assessment
- Simple task completion

**Level 2: GLM-4.6**
- Complex analysis
- Detailed reasoning
- Multi-step workflows

**Level 3: Kimi**
- Long context processing
- Advanced reasoning
- Specialized capabilities

---

## Benefits

1. **Cost Optimization**: Use cheaper models for simple tasks
2. **Performance**: Fast routing decisions with GLM-4.5-flash
3. **Quality**: Route complex tasks to appropriate models
4. **Flexibility**: Dynamic routing based on task requirements

---

## Configuration

```env
# Manager model
GLM_MANAGER_MODEL=glm-4.5-flash

# Routing thresholds
ROUTING_COMPLEXITY_THRESHOLD=0.7
ROUTING_CONTEXT_THRESHOLD=100000
```

---

## Related Documentation

- [glm.md](glm.md) - GLM provider details
- [kimi.md](kimi.md) - Kimi provider details
- [../02-provider-architecture.md](../02-provider-architecture.md) - Provider architecture overview




## README.md

**Source:** `docs/system-reference/README.md`

---

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





## tools\simple-tools\challenge.md

**Source:** `docs/system-reference/tools\simple-tools\challenge.md`

---

# challenge_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Critical Analysis)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [consensus.md](consensus.md)

---

## Purpose

Critical analysis and truth-seeking to prevent reflexive agreement

---

## Use Cases

- Preventing reflexive agreement when users challenge responses
- Critical evaluation of statements and assumptions
- Truth verification and fact-checking
- Assumption challenging and validation
- Reasoning validation and logical analysis

---

## Key Features

- **Automatic invocation** when user questions or disagrees
- **Critical thinking** instead of automatic agreement
- **Truth-seeking** through reasoned analysis
- **Assumption validation** and challenge
- **Logical reasoning** evaluation

---

## Key Parameters

- `prompt` (required): The user's message or statement to analyze critically

---

## Automatic Invocation

The tool is automatically triggered when the user:
- Questions or disagrees with previous statements ("But I don't think...")
- Challenges assumptions ("You're assuming...")
- Expresses confusion ("I'm confused why...")
- Believes an error was made ("That doesn't seem right...")
- Seeks justification ("Why did you...")
- Shows surprise at conclusions ("Wait, why...")

**Common patterns:**
- "But..."
- "Why did you..."
- "I thought..."
- "Shouldn't we..."
- "That seems wrong..."
- "Are you sure..."
- "I'm confused..."

---

## Manual Invocation

Users can explicitly request critical analysis by using the word "challenge" in their message.

---

## Usage Examples

### User Disagreement
```
User: "But I don't think that approach will work because of the performance implications"
```
→ Tool automatically invokes challenge to critically analyze the disagreement

### Questioning Assumptions
```
User: "You're assuming the database can handle that load, but have you considered peak traffic?"
```
→ Tool critically evaluates the assumption

### Seeking Justification
```
User: "Why did you recommend PostgreSQL over MongoDB for this use case?"
```
→ Tool provides reasoned justification instead of reflexive agreement

---

## Best Practices

- **Think critically** - Don't automatically agree when challenged
- **Provide reasoning** - Explain your analysis clearly
- **Acknowledge errors** - If wrong, admit it and correct course
- **Defend when right** - If correct, explain why with evidence
- **Seek truth** - Truth and correctness matter more than agreement

---

## When to Use

- **Automatic:** When user questions, disagrees, or challenges previous statements
- **Manual:** When user explicitly requests critical analysis with "challenge"
- **Use `challenge` for:** Critical evaluation and truth-seeking
- **Use `chat` for:** Collaborative discussions without critical analysis
- **Use `thinkdeep` for:** Deep reasoning without challenging assumptions
- **Use `consensus` for:** Multiple perspectives on decisions

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [consensus.md](consensus.md) - Multi-model consensus





## tools\simple-tools\chat.md

**Source:** `docs/system-reference/tools\simple-tools\chat.md`

---

# chat_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Request/Response)  
**Related:** [thinkdeep.md](thinkdeep.md), [analyze.md](../workflow-tools/analyze.md)

---

## Purpose

Your collaborative thinking partner for development conversations

---

## Description

The `chat` tool is designed to help you brainstorm, validate ideas, get second opinions, and explore alternatives in a conversational format. It's your thinking partner for bouncing ideas, getting expert opinions, and collaborative problem-solving.

---

## Use Cases

- Collaborative thinking partner for analysis and planning
- Get second opinions on designs and approaches
- Brainstorm solutions and explore alternatives
- Validate checklists and implementation plans
- General development questions and explanations
- Technology comparisons and best practices
- Architecture and design discussions

---

## Key Features

- **File reference support**: Include code files for context-aware discussions
- **Image support**: Screenshots, diagrams, UI mockups for visual analysis
- **Dynamic collaboration**: Can request additional files or context during conversation
- **Web search capability**: Analyzes when web searches would be helpful and recommends specific searches

---

## Key Parameters

- `prompt` (required): Your question or discussion topic
- `model` (optional): auto|kimi-k2-0905-preview|glm-4.5|glm-4.5-flash (default: auto)
- `use_websearch` (optional): Enable web search (default: true)
- `temperature` (optional): Response creativity (0-1, default: 0.5)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `files` (optional): Files for context (absolute paths)
- `images` (optional): Images for visual context (absolute paths or base64)
- `continuation_id` (optional): Continue previous conversations

---

## Usage Examples

### Basic Development Chat
```
"Chat about the best approach for user authentication in my React app"
```

### Technology Comparison
```
"Discuss whether PostgreSQL or MongoDB would be better for my e-commerce platform"
```

### File Context Analysis
```
"Chat about the current authentication implementation in auth.py and suggest improvements"
```

### Visual Analysis
```
"Chat about this UI mockup screenshot - is the user flow intuitive?"
```

---

## Best Practices

- Be specific about context - include relevant files or describe your project scope
- Ask for trade-offs - request pros/cons for better decision-making
- Use conversation continuation - build on previous discussions with `continuation_id`
- Leverage visual context - include diagrams, mockups, or screenshots when discussing UI/UX
- Request web searches - ask for current best practices or recent developments

---

## When to Use

- **Use `chat` for:** Open-ended discussions, brainstorming, second opinions, technology comparisons
- **Use `thinkdeep` for:** Extending specific analysis, challenging assumptions, deeper reasoning
- **Use `analyze` for:** Understanding existing code structure and patterns
- **Use `debug` for:** Specific error diagnosis and troubleshooting

---

## Related Tools

- [thinkdeep.md](thinkdeep.md) - Extended reasoning with multi-stage investigation
- [analyze.md](../workflow-tools/analyze.md) - Comprehensive code analysis
- [debug.md](../workflow-tools/debug.md) - Root cause analysis and debugging





## tools\simple-tools\consensus.md

**Source:** `docs/system-reference/tools\simple-tools\consensus.md`

---

# consensus_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Multi-Model Consensus)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [planner.md](planner.md)

---

## Purpose

Multi-model consensus workflow for complex decisions

---

## Use Cases

- Complex decisions requiring multiple perspectives
- Architectural choices with trade-offs
- Feature proposals needing validation
- Technology evaluations and comparisons
- Strategic planning with diverse viewpoints

---

## Key Features

- **Sequential model consultation** - One model at a time
- **Stance steering** - Models can argue for/against/neutral positions
- **Perspective synthesis** - Track and combine viewpoints
- **Structured debate** - Same model with different stances
- **Comprehensive consensus** - Final synthesis of all perspectives

---

## Key Parameters

- `step` (required): Current consensus step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Total steps (equals number of models)
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Summary of findings from this step
- `models` (required): List of model configurations to consult
- `model` (optional): Model to use for synthesis (default: auto)
- `use_assistant_model` (optional): Use expert analysis (default: true)
- `continuation_id` (optional): Continue previous consensus discussions

---

## Model Configuration

Each model in the `models` list can have:
- `model` (required): Model name (e.g., "kimi-k2-0905-preview", "glm-4.6")
- `stance` (optional): for|against|neutral (default: neutral)
- `stance_prompt` (optional): Custom stance instructions

**Note:** Same model can be used multiple times with different stances, but each model + stance combination must be unique.

---

## Workflow

1. **Step 1**: Provide your own neutral analysis of the proposal
2. **Tool consults each model** one by one
3. **Track perspectives** as they accumulate
4. **Synthesize findings** from all models
5. **Final step**: Present comprehensive consensus and recommendations

---

## Usage Examples

### Basic Consensus
```json
{
  "step": "Should we build a search component in SwiftUI for use in an AppKit app?",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial analysis suggests SwiftUI integration is feasible but has trade-offs",
  "models": [
    {"model": "kimi-k2-0905-preview", "stance": "for"},
    {"model": "glm-4.6", "stance": "against"},
    {"model": "kimi-k2-0905-preview", "stance": "neutral"}
  ]
}
```

### Technology Evaluation
```json
{
  "step": "Evaluate the proposal to migrate our database from MySQL to PostgreSQL",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Migration would provide better JSON support but requires significant effort",
  "models": [
    {"model": "glm-4.6", "stance": "for"},
    {"model": "kimi-k2-0905-preview", "stance": "against"}
  ]
}
```

---

## Best Practices

- Phrase step 1 as a clear question or proposal
- Provide your own analysis first (step 1)
- Use diverse models for varied perspectives
- Leverage stance steering for structured debate
- Consider using same model with different stances for balanced view

---

## When to Use

- **Use `consensus` for:** Complex decisions needing multiple expert perspectives
- **Use `chat` for:** Open-ended discussions without formal consensus
- **Use `thinkdeep` for:** Deep analysis from a single perspective
- **Use `planner` for:** Breaking down implementation steps

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [planner.md](planner.md) - Sequential planning
- [challenge.md](challenge.md) - Critical analysis





## tools\simple-tools\listmodels.md

**Source:** `docs/system-reference/tools\simple-tools\listmodels.md`

---

# listmodels_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Utility Tool  
**Related:** [version.md](version.md)

---

## Purpose

Display all available AI models organized by provider

---

## Use Cases

- Discover available models and their capabilities
- Understand which providers are configured
- Check model aliases and context windows
- Verify model availability before use

---

## Key Features

- **Provider organization** - Models grouped by provider (GLM, Kimi)
- **Model details** - Context windows, aliases, capabilities
- **Configuration status** - Shows which providers are active
- **Comprehensive listing** - All available models in one view

---

## Key Parameters

- `model` (optional): Ignored by listmodels tool

---

## Output Information

For each provider, displays:
- Provider name and status
- Available models
- Model aliases
- Context window sizes
- Special capabilities (streaming, web search, multimodal)

---

## Usage Examples

### Basic Usage
```
"List all available models"
```

### Check Specific Provider
```
"Show me all GLM models"
```

### Verify Configuration
```
"What models can I use?"
```

---

## Best Practices

- Run listmodels to discover available models before starting work
- Check context windows when working with large codebases
- Verify provider configuration if models are missing
- Use model aliases for convenience

---

## When to Use

- **Use `listmodels` for:** Discovering available models and their capabilities
- **Use `version` for:** Checking server version and configuration details
- **Use `chat` for:** Asking questions about model selection

---

## Related Tools

- [version.md](version.md) - Server version and configuration





## tools\simple-tools\planner.md

**Source:** `docs/system-reference/tools\simple-tools\planner.md`

---

# planner_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Sequential Planning)  
**Related:** [chat.md](chat.md), [thinkdeep.md](thinkdeep.md), [consensus.md](consensus.md)

---

## Purpose

Sequential step-by-step planning with branching and revision support

---

## Use Cases

- Breaking down complex tasks into manageable steps
- Project planning and implementation roadmaps
- Task sequencing and dependency mapping
- Exploring alternative approaches through branching
- Revising plans as understanding evolves

---

## Key Features

- **Sequential thinking** - Build plans step-by-step
- **Deep reflection** for complex planning scenarios
- **Branching** into alternative approaches
- **Revisions** of previous steps when new insights emerge
- **Dynamic step adjustment** - Add or modify steps as needed

---

## Key Parameters

- `step` (required): Current planning step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps needed
- `next_step_required` (required): Whether another step is needed
- `is_step_revision` (optional): True if revising a previous step
- `revises_step_number` (optional): Which step number is being revised
- `is_branch_point` (optional): True if branching from a previous step
- `branch_from_step` (optional): Which step is the branching point
- `branch_id` (optional): Identifier for the current branch (e.g., 'approach-A')
- `model` (optional): Model to use (default: auto)
- `use_assistant_model` (optional): Use expert analysis (default: true)

---

## Usage Examples

### Basic Planning
```json
{
  "step": "Outline goals and constraints for zai-sdk upgrade",
  "step_number": 1,
  "total_steps": 5,
  "next_step_required": true
}
```

### Branching Approach
```json
{
  "step": "Explore microservices approach as alternative",
  "step_number": 4,
  "total_steps": 6,
  "next_step_required": true,
  "is_branch_point": true,
  "branch_from_step": 3,
  "branch_id": "microservices-path"
}
```

### Revising Previous Step
```json
{
  "step": "Revise authentication strategy based on new security requirements",
  "step_number": 3,
  "total_steps": 5,
  "next_step_required": true,
  "is_step_revision": true,
  "revises_step_number": 2
}
```

---

## Best Practices

- Start with high-level goals and constraints
- Break down complex tasks into smaller, manageable steps
- Use branching to explore alternative approaches
- Revise steps when new information emerges
- Be flexible with total_steps - adjust as planning evolves

---

## When to Use

- **Use `planner` for:** Breaking down complex tasks, creating implementation roadmaps
- **Use `chat` for:** Open-ended brainstorming without structured planning
- **Use `thinkdeep` for:** Deep analysis of specific problems
- **Use `consensus` for:** Getting multiple perspectives on decisions

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [thinkdeep.md](thinkdeep.md) - Extended reasoning
- [consensus.md](consensus.md) - Multi-model consensus





## tools\simple-tools\thinkdeep.md

**Source:** `docs/system-reference/tools\simple-tools\thinkdeep.md`

---

# thinkdeep_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Simple Tool (Multi-Stage Investigation)  
**Related:** [chat.md](chat.md), [analyze.md](../workflow-tools/analyze.md)

---

## Purpose

Extended reasoning partner - get a second opinion to challenge assumptions

---

## Description

The `thinkdeep` tool provides extended reasoning capabilities, offering a second perspective to the AI client's analysis. It's designed to challenge assumptions, find edge cases, and provide alternative approaches to complex problems through multi-stage investigation.

---

## Use Cases

- Complex problem analysis with systematic investigation
- Architecture decisions requiring deep validation
- Performance challenges needing thorough analysis
- Security analysis with comprehensive threat modeling
- Systematic hypothesis testing and validation
- Expert validation of design patterns

---

## Key Features

- **Multi-stage workflow** with structured investigation steps
- **Provides second opinion** on AI client's analysis
- **Challenges assumptions** and identifies edge cases
- **Offers alternative perspectives** and approaches
- **Validates architectural decisions** and design patterns
- **File reference support**: Include code files for context
- **Image support**: Analyze architectural diagrams, flowcharts, design mockups
- **Web search capability**: Identifies areas where current documentation would strengthen analysis

---

## Key Parameters

- `step` (required): Current investigation step description
- `step_number` (required): Current step number (starts at 1)
- `total_steps` (required): Estimated total steps needed
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Important findings and evidence from this step
- `hypothesis` (optional): Current theory about the issue/goal
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: high)
- `problem_context` (optional): Additional context about the problem or goal
- `focus_areas` (optional): Specific aspects to focus on (architecture, performance, security, etc.)
- `files` (optional): File paths for additional context (absolute paths)
- `images` (optional): Images for visual analysis (absolute paths)
- `use_websearch` (optional): Enable web search (default: true)
- `continuation_id` (optional): Continue previous investigations

---

## Workflow

1. **Step 1**: Describe investigation plan and begin forming systematic approach
2. **STOP** - Investigate using appropriate tools
3. **Step 2+**: Report findings with concrete evidence
4. **Continue** until investigation complete
5. **Expert Analysis**: Receive comprehensive analysis based on all findings

---

## Usage Examples

### Architecture Design
```
"Think deeper about my microservices authentication strategy using max thinking mode"
```

### With File Context
```
"Think deeper about my API design with reference to api/routes.py and models/user.py"
```

### Visual Analysis
```
"Think deeper about this system architecture diagram - identify potential bottlenecks"
```

### Problem Solving
```
"I'm considering using GraphQL vs REST for my API. Think deeper about the trade-offs using high thinking mode"
```

---

## Best Practices

- Provide detailed context - share your current thinking, constraints, and objectives
- Be specific about focus areas - mention what aspects need deeper analysis
- Include relevant files - reference code, documentation, or configuration files
- Use appropriate thinking modes - higher modes for complex problems, lower for quick validations
- Leverage visual context - include diagrams or mockups for architectural discussions
- Build on discussions - use continuation to extend previous analyses

---

## When to Use

- **Use `thinkdeep` for:** Extending specific analysis, challenging assumptions, architectural decisions
- **Use `chat` for:** Open-ended brainstorming and general discussions
- **Use `analyze` for:** Understanding existing code without extending analysis
- **Use `codereview` for:** Finding specific bugs and security issues

---

## Related Tools

- [chat.md](chat.md) - Collaborative thinking partner
- [analyze.md](../workflow-tools/analyze.md) - Comprehensive code analysis
- [consensus.md](consensus.md) - Multi-model consensus workflow





## tools\simple-tools\version.md

**Source:** `docs/system-reference/tools\simple-tools\version.md`

---

# version_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Utility Tool  
**Related:** [listmodels.md](listmodels.md)

---

## Purpose

Get server version, configuration details, and list of available tools

---

## Use Cases

- Check server version and build information
- Verify configuration settings
- List all available tools
- Debug server setup issues
- Understand server capabilities

---

## Key Features

- **Version information** - Server version and build details
- **Configuration details** - Active providers, settings, features
- **Tool listing** - All available tools and their categories
- **Diagnostic information** - Helpful for troubleshooting

---

## Key Parameters

- `model` (optional): Ignored by version tool

---

## Output Information

Displays:
- Server version number
- Build date and commit hash
- Active providers (GLM, Kimi)
- Configuration settings
- Available tools (simple, workflow, utility)
- Feature flags and capabilities

---

## Usage Examples

### Basic Usage
```
"Show server version"
```

### Configuration Check
```
"What's the current server configuration?"
```

### Troubleshooting
```
"Display version and configuration for debugging"
```

---

## Best Practices

- Run version check after server updates
- Use for troubleshooting configuration issues
- Verify tool availability before use
- Check feature flags for capability verification

---

## When to Use

- **Use `version` for:** Checking server version and configuration
- **Use `listmodels` for:** Discovering available AI models
- **Use `chat` for:** Asking questions about server capabilities

---

## Related Tools

- [listmodels.md](listmodels.md) - List available AI models





## tools\workflow-tools\analyze.md

**Source:** `docs/system-reference/tools\workflow-tools\analyze.md`

---

# analyze_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [debug.md](debug.md), [codereview.md](codereview.md), [refactor.md](refactor.md)

---

## Purpose

Smart file analysis - general-purpose code understanding and exploration

---

## Description

The `analyze` tool provides comprehensive code analysis and understanding capabilities through workflow-driven investigation. It helps you explore codebases, understand architecture, and identify patterns across files and directories. The tool guides the AI client through systematic investigation of code structure, patterns, and architectural decisions before providing expert analysis.

---

## Use Cases

- Analyze single files or entire directories
- Architectural assessment and system-level design
- Performance evaluation and bottleneck identification
- Security analysis and vulnerability assessment
- Code quality and maintainability review
- Pattern detection and anti-pattern identification
- Strategic planning and improvement recommendations

---

## Key Features

- **Analyzes single files or entire directories** with intelligent file filtering
- **Specialized analysis types**: architecture, performance, security, quality, general
- **Large codebase support**: Handle massive codebases with 200K+ token context models
- **Cross-file relationship mapping**: Understand dependencies and interactions
- **Architecture visualization**: Describe system structure and component relationships
- **Image support**: Analyze architecture diagrams, UML charts, flowcharts
- **Web search capability**: Enhance analysis with current documentation and best practices
- **Pattern recognition**: Identify design patterns, anti-patterns, and refactoring opportunities

---

## Key Parameters

### Workflow Investigation Parameters
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in analysis sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and insights collected in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly relevant to the analysis (absolute paths)
- `relevant_context` (optional): Methods/functions/classes central to analysis findings
- `issues_found` (optional): Issues or concerns identified with severity levels
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from (for revisions)
- `images` (optional): Visual references for analysis context

### Initial Configuration
- `model` (optional): Model to use (default: auto)
- `analysis_type` (optional): architecture|performance|security|quality|general (default: general)
- `output_format` (optional): summary|detailed|actionable (default: detailed)
- `temperature` (optional): Temperature for analysis (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)
- `continuation_id` (optional): Continue previous analysis sessions

---

## Workflow

1. **Step 1**: AI client describes analysis plan and begins examining code structure
2. **STOP** - Investigate architecture, patterns, dependencies, design decisions
3. **Step 2+**: Report findings with evidence from code examination
4. **Throughout**: Track findings, relevant files, insights, confidence levels
5. **Completion**: Once analysis is comprehensive, signal completion
6. **Expert Analysis**: Receive comprehensive analysis summary (unless confidence=certain)

---

## Analysis Types

- **General Analysis (default)**: Overall code structure, key components, data flow, design patterns
- **Architecture Analysis**: System-level design, module dependencies, separation of concerns, scalability
- **Performance Analysis**: Bottlenecks, algorithmic complexity, memory usage, I/O efficiency
- **Security Analysis**: Security patterns, vulnerabilities, input validation, authentication mechanisms
- **Quality Analysis**: Code quality metrics, testing coverage, documentation, best practices

---

## Usage Examples

### Single File Analysis
```
"Analyze user_controller.py to understand the authentication flow"
```

### Directory Architecture Analysis
```
"Analyze the src/ directory architecture and identify the main components"
```

### Performance-Focused Analysis
```
"Analyze backend/api/ for performance bottlenecks, focus on database queries"
```

### Large Codebase Analysis
```
"Analyze the entire project structure to understand how all components work together"
```

---

## Best Practices

- Be specific about goals - clearly state what you want to understand or discover
- Use appropriate analysis types - choose the type that matches your needs
- Include related files - analyze modules together for better context understanding
- Leverage large context models - use Kimi for comprehensive codebase analysis
- Combine with visual context - include architecture diagrams or documentation
- Use continuation - build on previous analysis for deeper understanding

---

## When to Use

- **Use `analyze` for:** Understanding code structure, exploring unfamiliar codebases, architecture assessment
- **Use `codereview` for:** Finding bugs and security issues with actionable fixes
- **Use `debug` for:** Diagnosing specific runtime errors or performance problems
- **Use `refactor` for:** Getting specific refactoring recommendations and implementation plans

---

## Related Tools

- [debug.md](debug.md) - Root cause analysis and debugging
- [codereview.md](codereview.md) - Professional code review
- [refactor.md](refactor.md) - Intelligent refactoring analysis
- [tracer.md](tracer.md) - Code tracing and dependency mapping





## tools\workflow-tools\codereview.md

**Source:** `docs/system-reference/tools\workflow-tools\codereview.md`

---

# codereview_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Professional code review with prioritized feedback

**Description:**
The `codereview` tool provides professional code review capabilities with actionable feedback, severity-based issue prioritization, and support for various review types from quick style checks to comprehensive security audits. This workflow tool guides the AI client through systematic investigation steps with forced pauses to ensure thorough code examination.

**Use Cases:**
- Comprehensive code review with actionable feedback
- Security audits and vulnerability assessment
- Performance analysis and optimization opportunities
- Architectural assessment and pattern evaluation
- Code quality evaluation and maintainability review
- Anti-pattern detection and refactoring recommendations

**Key Features:**
- **Issues prioritized by severity** (🔴 CRITICAL → 🟢 LOW)
- **Specialized review types**: full, security, performance, quick
- **Coding standards enforcement**: PEP8, ESLint, Google Style Guide, etc.
- **Severity filtering**: Report only critical/high/medium/low issues
- **Image support**: Review code from screenshots, error dialogs, visual bug reports
- **Multi-file analysis**: Comprehensive review of entire directories or codebases
- **Actionable feedback**: Specific recommendations with line numbers and code examples
- **Language-specific expertise**: Tailored analysis for Python, JavaScript, Java, C#, Swift, and more
- **Integration issue detection**: Cross-file dependencies and architectural problems
- **Security vulnerability scanning**: Common security patterns and anti-patterns

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in review sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and evidence collected in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly relevant to review (absolute paths)
- `relevant_context` (optional): Methods/functions/classes central to review findings
- `issues_found` (optional): Issues identified with severity levels
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from
- `images` (optional): Visual references for review context

*Initial Review Configuration:*
- `model` (optional): Model to use (default: auto)
- `review_type` (optional): full|security|performance|quick (default: full)
- `focus_on` (optional): Specific aspects to focus on (e.g., "security vulnerabilities", "performance bottlenecks")
- `standards` (optional): Coding standards to enforce (e.g., "PEP8", "ESLint")
- `severity_filter` (optional): critical|high|medium|low|all (default: all)
- `temperature` (optional): Temperature for consistency (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)
- `continuation_id` (optional): Continue previous review discussions

**Review Types:**
- **Full Review (default)**: Comprehensive analysis including bugs, security, performance, maintainability
- **Security Review**: Focus on vulnerabilities, authentication, authorization, input validation
- **Performance Review**: Bottlenecks, algorithmic complexity, resource usage
- **Quick Review**: Style, naming conventions, basic code quality

**Workflow:**
1. **Step 1**: Describe review plan and pass files in `relevant_files`
2. **STOP** - Investigate code quality, security, performance, architecture
3. **Step 2+**: Report findings with evidence and severity classifications
4. **Throughout**: Track findings, issues, confidence levels
5. **Completion**: Once review is comprehensive, signal completion
6. **Expert Analysis**: Receive comprehensive review summary (unless confidence=certain)

**Usage Examples:**

*Security-Focused Review:*
```
"Perform a codereview on auth.py for security issues and potential vulnerabilities"
```

*Performance Review:*
```
"Review backend/api/ for performance bottlenecks and optimization opportunities"
```

*Full Codebase Review:*
```
"Comprehensive code review of src/ directory with actionable recommendations"
```

**Best Practices:**
- Be specific about review objectives and focus areas
- Include coding standards to enforce
- Use severity filtering for large codebases
- Leverage large context models for comprehensive analysis
- Include visual context when reviewing UI/UX code

**When to Use:**
- Use `codereview` for: Finding bugs and security issues with actionable fixes
- Use `analyze` for: Understanding code structure without finding specific issues
- Use `debug` for: Diagnosing specific runtime errors
- Use `refactor` for: Getting refactoring recommendations



## tools\workflow-tools\debug.md

**Source:** `docs/system-reference/tools\workflow-tools\debug.md`

---

# debug_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [codereview.md](codereview.md), [precommit.md](precommit.md)

---

## Purpose

Systematic investigation & expert debugging assistance

---

## Description

The `debug` workflow guides the AI client through a systematic investigation process where the client performs methodical code examination, evidence collection, and hypothesis formation across multiple steps. Once the investigation is complete, the tool provides expert analysis based on all gathered findings (unless confidence is "certain").

---

## Use Cases

- Complex bugs requiring systematic investigation
- Mysterious errors with unclear root causes
- Performance issues and bottlenecks
- Race conditions and concurrency bugs
- Memory leaks and resource exhaustion
- Integration problems and API failures
- Runtime environment issues

---

## Key Features

- **Multi-step investigation process** with evidence collection and hypothesis evolution
- **Systematic code examination** with file and method tracking throughout investigation
- **Confidence assessment and revision** capabilities for investigative steps
- **Backtracking support** to revise previous steps when new insights emerge
- **Expert analysis integration** that provides final debugging recommendations
- **Error context support**: Stack traces, logs, and runtime information
- **Visual debugging**: Include error screenshots, stack traces, console output
- **Conversation threading**: Continue investigations across multiple sessions
- **Large context analysis**: Handle extensive log files and multiple related code files
- **Multi-language support**: Debug issues across Python, JavaScript, Java, C#, Swift, and more
- **Web search integration**: Identifies when additional research would help solve problems

---

## Key Parameters

### Investigation Step Parameters
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in investigation sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and evidence collected in this step
- `hypothesis` (required): Current best guess about the underlying cause
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (optional): Files directly tied to the root cause (absolute paths)
- `relevant_context` (optional): Specific methods/functions involved in the issue
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from
- `continuation_id` (optional): Thread ID for continuing investigations
- `images` (optional): Visual debugging materials (error screenshots, logs)

### Model Selection
- `model` (optional): Model to use (default: auto)
- `thinking_mode` (optional): Thinking depth - minimal|low|medium|high|max (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

---

## Workflow

1. **Step 1**: AI client describes the issue and begins thinking deeply about possible causes
2. **STOP** - Examine relevant code, trace errors, test hypotheses, gather evidence
3. **Step 2+**: Report findings with concrete evidence from code examination
4. **Throughout**: Track findings, files checked, methods involved, evolving hypotheses
5. **Backtracking**: Revise previous steps when new insights emerge
6. **Completion**: Once investigation is thorough, signal completion
7. **Expert Analysis**: Receive debugging recommendations (unless confidence=certain)

---

## Investigation Methodology

### Step-by-Step Investigation (Client-Led)
1. **Initial Problem Description**: Describe issue and think about possible causes
2. **Code Examination**: Systematically examine relevant files, trace execution paths
3. **Evidence Collection**: Gather findings, track files checked, identify methods involved
4. **Hypothesis Formation**: Develop working theories about root cause
5. **Iterative Refinement**: Backtrack and revise previous steps as understanding evolves
6. **Investigation Completion**: Signal when sufficient evidence has been gathered

### Expert Analysis Phase (When Used)
- **Root Cause Analysis**: Deep analysis of all investigation findings
- **Solution Recommendations**: Specific fixes with implementation guidance
- **Prevention Strategies**: Measures to avoid similar issues
- **Testing Approaches**: Validation methods for proposed solutions

---

## Debugging Categories

- **Runtime Errors**: Exceptions, crashes, null pointer errors, type errors, memory leaks
- **Logic Errors**: Incorrect algorithms, off-by-one errors, state management issues, race conditions
- **Integration Issues**: API failures, database connection problems, third-party service integration
- **Performance Problems**: Slow response times, memory spikes, CPU-intensive operations, I/O bottlenecks

---

## Valid Hypotheses

- "No bug found - possible user misunderstanding"
- "Symptoms appear unrelated to any code issue"
- Concrete theories about failures, incorrect assumptions, or violated constraints
- When no bug is found, consider: "Recommend discussing with thought partner for clarification"

---

## Usage Examples

### Error Debugging
```
"Debug this TypeError: 'NoneType' object has no attribute 'split' in my parser.py"
```

### With Stack Trace
```
"Debug why my API returns 500 errors with this stack trace: [paste full traceback]"
```

### Performance Debugging
```
"Debug to find out why the app is consuming excessive memory during bulk edit operations"
```

### Multi-File Investigation
```
"Debug the data processing pipeline issues across processor.py, validator.py, and output_handler.py"
```

---

## Best Practices

### For Investigation Steps
- Be thorough in step descriptions - explain what you're examining and why
- Track all files examined - include even files that don't contain the bug
- Document findings clearly - summarize discoveries, suspicious patterns, evidence
- Evolve hypotheses - update theories as investigation progresses
- Use backtracking wisely - revise previous steps when new insights emerge
- Include visual evidence - screenshots, error dialogs, console output

### For Initial Problem Description
- Provide complete error context - full stack traces, error messages, logs
- Describe expected vs actual behavior - clear symptom description
- Include environment details - runtime versions, configuration, deployment context
- Mention previous attempts - what debugging steps have already been tried
- Be specific about occurrence - when, where, and how the issue manifests

---

## When to Use

- **Use `debug` for:** Specific runtime errors, exceptions, crashes, performance issues requiring systematic investigation
- **Use `codereview` for:** Finding potential bugs in code without specific errors or symptoms
- **Use `analyze` for:** Understanding code structure and flow without troubleshooting specific issues
- **Use `precommit` for:** Validating changes before commit to prevent introducing bugs

---

## Related Tools

- [analyze.md](analyze.md) - Comprehensive code analysis
- [codereview.md](codereview.md) - Professional code review
- [precommit.md](precommit.md) - Pre-commit validation
- [tracer.md](tracer.md) - Code tracing and dependency mapping





## tools\workflow-tools\docgen.md

**Source:** `docs/system-reference/tools\workflow-tools\docgen.md`

---



**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---


---

### docgen_EXAI-WS

**Purpose:** Comprehensive documentation generation with complexity analysis

**Description:**
The `docgen` tool creates thorough documentation by analyzing code structure, understanding function complexity, and documenting gotchas and unexpected behaviors. This workflow tool guides the AI client through systematic investigation of code functionality before generating comprehensive documentation.

**Use Cases:**
- Comprehensive documentation generation for undocumented code
- Code documentation analysis and quality assessment
- Complexity assessment with Big O notation
- Documentation modernization and style updates
- API documentation with call flow information
- Gotchas and unexpected behavior documentation

**Key Features:**
- **Systematic file-by-file approach** - Complete documentation with progress tracking
- **Modern documentation styles** - Enforces /// for Objective-C/Swift, /** */ for Java/JavaScript
- **Complexity analysis** - Big O notation for algorithms and performance characteristics
- **Call flow documentation** - Dependencies and method relationships
- **Counter-based completion** - Prevents stopping until all files are documented
- **Large file handling** - Systematic portion-by-portion documentation
- **Final verification scan** - Mandatory check to ensure no functions are missed
- **Bug tracking** - Surfaces code issues without altering logic
- **Configuration parameters** - Control complexity analysis, call flow, inline comments

**Key Parameters:**

*Workflow Parameters:*
- `step` (required): Current step description - discovery (step 1) or documentation (step 2+)
- `step_number` (required): Current step number in documentation sequence
- `total_steps` (required): Dynamically calculated as 1 + total_files_to_document
- `next_step_required` (required): Whether another step is needed
- `findings` (required): Discoveries about code structure and documentation needs
- `relevant_files` (optional): Files being actively documented in current step
- `num_files_documented` (required): Counter tracking completed files (starts at 0)
- `total_files_to_document` (required): Total count of files needing documentation

*Configuration Parameters (required fields):*
- `document_complexity` (required): Include Big O complexity analysis (default: true)
- `document_flow` (required): Include call flow and dependency information (default: true)
- `update_existing` (required): Update existing documentation when incorrect/incomplete (default: true)
- `comments_on_complex_logic` (required): Add inline comments for complex algorithmic steps (default: true)

**Critical Counters:**
- `num_files_documented`: Increment by 1 ONLY when file is 100% documented
- `total_files_to_document`: Set in step 1 after discovering all files
- **Cannot set `next_step_required=false` unless `num_files_documented == total_files_to_document`**

**Workflow:**
1. **Step 1 (Discovery)**: Discover ALL files needing documentation and report exact count
2. **Step 2+ (Documentation)**: Document files one-by-one with complete coverage validation
3. **Throughout**: Track progress with counters and enforce modern documentation styles
4. **Completion**: Only when all files are documented (counters match)
5. **Documentation Generation**: Complete documentation with style consistency

**Usage Examples:**

*Class Documentation:*
```
"Generate comprehensive documentation for the PaymentProcessor class including complexity analysis"
```

*Module Documentation:*
```
"Document all functions in the authentication module with call flow information"
```

*API Documentation:*
```
"Create API documentation for the REST endpoints with complexity and flow analysis"
```

**Best Practices:**
- Let the tool discover all files first (step 1)
- Document one file at a time for thoroughness
- Include complexity analysis for algorithms
- Document call flows for better understanding
- Update existing docs when incorrect
- Add inline comments for complex logic

**When to Use:**
- Use `docgen` for: Generating comprehensive documentation with complexity analysis
- Use `codereview` for: Finding bugs and improving code quality
- Use `analyze` for: Understanding code structure
- Use `refactor` for: Improving code organization



## tools\workflow-tools\refactor.md

**Source:** `docs/system-reference/tools\workflow-tools\refactor.md`

---

# refactor_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Intelligent code refactoring with top-down decomposition

**Description:**
The `refactor` tool provides intelligent code refactoring recommendations with a focus on top-down decomposition and systematic code improvement. This workflow tool enforces systematic investigation of code smells, decomposition opportunities, and modernization possibilities with precise implementation guidance.

**Use Cases:**
- Comprehensive refactoring analysis with prioritization
- Code smell detection and anti-pattern identification
- Decomposition planning for large files/classes/functions
- Modernization opportunities (language features, patterns)
- Organization improvements and structure optimization
- Maintainability enhancements and complexity reduction

**Key Features:**
- **Intelligent prioritization** - Refuses low-priority work if critical decomposition needed first
- **Top-down decomposition strategy** - Analyzes file → class → function levels systematically
- **Four refactor types**: codesmells, decompose, modernize, organization
- **Precise line-number references** - Exact line numbers for implementation
- **Language-specific guidance** - Tailored suggestions for each language
- **Style guide integration** - Uses existing project files as pattern references
- **Conservative approach** - Careful dependency analysis to prevent breaking changes
- **Multi-file analysis** - Understands cross-file relationships and dependencies
- **Priority sequencing** - Recommends implementation order for changes
- **Image support**: Analyze architecture diagrams, legacy system charts

**Refactor Types (Progressive Priority System):**

**1. `decompose` (CRITICAL PRIORITY)** - Context-aware decomposition:
- **AUTOMATIC decomposition** (CRITICAL severity - blocks all other refactoring):
  - Files >15,000 LOC, Classes >3,000 LOC, Functions >500 LOC
- **EVALUATE decomposition** (contextual severity - intelligent assessment):
  - Files >5,000 LOC, Classes >1,000 LOC, Functions >150 LOC
  - Only recommends if genuinely improves maintainability
  - Respects legacy stability, domain complexity, performance constraints

**2. `codesmells`** - Applied only after decomposition complete:
- Long methods, complex conditionals, duplicate code, magic numbers, poor naming

**3. `modernize`** - Applied only after decomposition complete:
- Update to modern language features (f-strings, async/await, etc.)

**4. `organization`** - Applied only after decomposition complete:
- Improve logical grouping, separation of concerns, module structure

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in refactoring sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries and refactoring opportunities in this step
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly needing refactoring (absolute paths)
- `relevant_context` (optional): Methods/functions/classes requiring refactoring
- `issues_found` (optional): Refactoring opportunities with severity and type
- `confidence` (optional): Confidence level (exploring, incomplete, partial, complete)
- `backtrack_from_step` (optional): Step number to backtrack from

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `refactor_type` (optional): codesmells|decompose|modernize|organization (default: codesmells)
- `style_guide_examples` (optional): Existing code files as style reference (absolute paths)
- `temperature` (optional): Temperature (0-1, default: 0.2)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Describe refactoring plan and pass files in `relevant_files`
2. **STOP** - Investigate code smells, decomposition needs, modernization opportunities
3. **Step 2+**: Report findings with evidence and precise line numbers
4. **Throughout**: Track findings, opportunities, confidence levels
5. **Completion**: Once investigation is thorough, signal completion
6. **Expert Analysis**: Receive refactoring recommendations (unless confidence=complete)

**Usage Examples:**

*Decompose Large Class:*
```
"Decompose my_crazy_big_class.m into smaller, maintainable extensions"
```

*Code Smell Detection:*
```
"Find code smells in the authentication module and suggest improvements"
```

*Modernization:*
```
"Modernize legacy_code.py to use current Python best practices and features"
```

**Best Practices:**
- Start with decomposition for large files/classes
- Provide style guide examples for consistency
- Use conservative approach for legacy code
- Consider dependencies before refactoring
- Implement changes in recommended order

**When to Use:**
- Use `refactor` for: Getting specific refactoring recommendations and implementation plans
- Use `codereview` for: Finding bugs and security issues
- Use `analyze` for: Understanding code structure without refactoring
- Use `debug` for: Diagnosing specific errors



## tools\workflow-tools\secaudit.md

**Source:** `docs/system-reference/tools\workflow-tools\secaudit.md`

---

# secaudit_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Comprehensive security audit with OWASP-based assessment

**Description:**
The `secaudit` tool provides comprehensive security auditing capabilities with systematic OWASP Top 10 assessment, compliance framework evaluation, and threat modeling. This workflow tool guides the AI client through methodical security investigation with forced pauses to ensure thorough vulnerability assessment.

**IMPORTANT**: AI models may not identify all security vulnerabilities. Always perform additional manual security reviews, penetration testing, and verification.

**Use Cases:**
- Comprehensive security assessment with OWASP Top 10 coverage
- Compliance evaluation (SOC2, PCI DSS, HIPAA, GDPR, FedRAMP)
- Vulnerability identification and threat modeling
- Security architecture review and attack surface mapping
- Authentication and authorization assessment
- Input validation and data security review

**Key Features:**
- **OWASP Top 10 (2021) systematic assessment** with specific vulnerability identification
- **Multi-compliance framework support**: SOC2, PCI DSS, HIPAA, GDPR, FedRAMP
- **Threat-level aware analysis**: Critical, high, medium, low threat classifications
- **Technology-specific security patterns**: Web apps, APIs, mobile, cloud, enterprise systems
- **Risk-based prioritization**: Business impact and exploitability assessment
- **Audit focus customization**: Comprehensive, authentication, data protection, infrastructure
- **Image support**: Security analysis from architecture diagrams, network topology
- **Multi-file security analysis**: Cross-component vulnerability identification
- **Compliance gap analysis**: Specific framework requirements with remediation guidance
- **Attack surface mapping**: Entry points, data flows, privilege boundaries
- **Security control effectiveness**: Evaluation of existing security measures

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current security investigation step description
- `step_number` (required): Current step number in audit sequence
- `total_steps` (required): Estimated total investigation steps (typically 4-6)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Security discoveries and evidence collected
- `files_checked` (optional): All files examined during security investigation
- `relevant_files` (required in step 1): Files directly relevant to security audit (absolute paths)
- `relevant_context` (optional): Methods/functions/classes with security implications
- `issues_found` (optional): Security issues with severity levels
- `confidence` (optional): Confidence level in audit completeness
- `images` (optional): Visual references (architecture diagrams, network topology)

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `audit_focus` (optional): owasp|compliance|infrastructure|dependencies|comprehensive (default: comprehensive)
- `threat_level` (optional): low|medium|high|critical (default: medium)
- `security_scope` (optional): Application context (web app, mobile app, API, enterprise system)
- `compliance_requirements` (optional): List of applicable frameworks (SOC2, PCI DSS, HIPAA, GDPR, ISO 27001)
- `severity_filter` (optional): critical|high|medium|low|all (default: all)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_websearch` (optional): Enable web search (default: true)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Security scope analysis - identify application type, tech stack, attack surface
2. **Step 2**: Authentication & authorization assessment
3. **Step 3**: Input validation & data security review
4. **Step 4**: OWASP Top 10 (2021) systematic review
5. **Step 5**: Dependencies & infrastructure security
6. **Step 6**: Compliance & risk assessment
7. **Expert Analysis**: Comprehensive security assessment summary

**Usage Examples:**

*E-Commerce Security Audit:*
```
"Perform a secaudit on this e-commerce web application focusing on payment processing security and PCI DSS compliance"
```

*Authentication System Audit:*
```
"Conduct a comprehensive security audit of the authentication system, threat level high, focus on HIPAA compliance"
```

*API Security Assessment:*
```
"Security audit of REST API focusing on OWASP Top 10 and authentication vulnerabilities"
```

**Best Practices:**
- Define security scope and application context clearly
- Specify compliance requirements upfront
- Use appropriate threat level for risk prioritization
- Include architecture diagrams for better context
- Focus on specific audit areas for targeted assessment

**When to Use:**
- Use `secaudit` for: Comprehensive security assessment and vulnerability identification
- Use `codereview` for: General code quality with some security considerations
- Use `analyze` for: Understanding code structure without security focus



## tools\workflow-tools\testgen.md

**Source:** `docs/system-reference/tools\workflow-tools\testgen.md`

---

# testgen_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Comprehensive test generation with edge case coverage

**Description:**
The `testgen` tool creates comprehensive test suites by analyzing code paths, understanding intricate dependencies, and identifying realistic edge cases and failure scenarios. This workflow tool guides the AI client through systematic investigation of code functionality before generating thorough tests.

**Use Cases:**
- Generating tests for specific functions/classes/modules
- Creating test scaffolding for new features
- Improving test coverage with edge cases
- Edge case identification and boundary condition testing
- Framework-specific test generation
- Realistic failure mode analysis

**Key Features:**
- **Multi-step workflow** analyzing code paths and identifying realistic failure modes
- **Generates framework-specific tests** following project conventions
- **Supports test pattern following** when examples are provided
- **Dynamic token allocation** (25% for test examples, 75% for main code)
- **Prioritizes smallest test files** for pattern detection
- **Can reference existing test files** for style consistency
- **Specific code coverage** - target specific functions/classes rather than testing everything
- **Image support**: Test UI components, analyze visual requirements
- **Edge case identification**: Systematic discovery of boundary conditions and error states
- **Realistic failure mode analysis**: Understanding what can actually go wrong
- **Integration test support**: Tests covering component interactions

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current investigation step description
- `step_number` (required): Current step number in test generation sequence
- `total_steps` (required): Estimated total investigation steps (adjustable)
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries about functionality and test scenarios
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (required in step 1): Files directly needing tests (absolute paths)
- `relevant_context` (optional): Methods/functions/classes requiring test coverage
- `confidence` (optional): Confidence level (exploring, low, medium, high, very_high, almost_certain, certain)
- `backtrack_from_step` (optional): Step number to backtrack from

*Initial Configuration:*
- `model` (optional): Model to use (default: auto)
- `test_examples` (optional): Existing test files as style/pattern reference (absolute paths)
- `thinking_mode` (optional): Thinking depth (default: medium)
- `use_assistant_model` (optional): Use expert test generation phase (default: true)

**Workflow:**
1. **Step 1**: Describe what to test and testing objectives (be specific!)
2. **STOP** - Investigate code functionality, critical paths, edge cases
3. **Step 2+**: Report findings with test scenarios and coverage gaps
4. **Throughout**: Track findings, test scenarios, confidence levels
5. **Completion**: Once investigation is thorough, signal completion
6. **Test Generation**: Receive comprehensive test suite

**Usage Examples:**

*Method-Specific Tests:*
```
"Generate tests for User.login() method covering authentication success, failure, and edge cases"
```

*Class Testing:*
```
"Generate comprehensive tests for PaymentProcessor class"
```

*Following Existing Patterns:*
```
"Generate tests for new authentication module following patterns from tests/unit/auth/"
```

*UI Component Testing:*
```
"Generate tests for this login form component using the UI mockup screenshot"
```

**Best Practices:**
- **Be specific about scope** - Target specific functions/classes/modules, not "test everything"
- **Provide test examples** - Include existing test files for pattern consistency
- **Describe expected behavior** - Explain what the code should do
- **Include edge cases** - Mention known boundary conditions or failure modes
- **Specify framework** - Indicate testing framework (pytest, jest, junit, etc.)

**When to Use:**
- Use `testgen` for: Generating comprehensive test suites with edge case coverage
- Use `codereview` for: Finding bugs in existing code
- Use `debug` for: Diagnosing specific test failures
- Use `analyze` for: Understanding code structure before writing tests



## tools\workflow-tools\tracer.md

**Source:** `docs/system-reference/tools\workflow-tools\tracer.md`

---

# tracer_EXAI-WS

**Version:** 1.1  
**Last Updated:** 2025-10-03  
**Category:** Workflow Tool (Multi-Step Investigation)  
**Related:** [analyze.md](analyze.md), [debug.md](debug.md)

---



**Purpose:** Code tracing and dependency mapping through systematic investigation

**Description:**
The `tracer` tool provides comprehensive code tracing capabilities for understanding execution flows and dependency relationships. This workflow tool guides the AI client through systematic investigation of call chains, usage patterns, and structural dependencies.

**Use Cases:**
- Method execution flow analysis and call chain tracing
- Dependency mapping and structural relationship analysis
- Call chain tracing for debugging and understanding
- Architectural understanding and component relationships
- Code comprehension for unfamiliar codebases
- Impact analysis for code changes

**Key Features:**
- **Two analysis modes**: precision (execution flow) and dependencies (structural relationships)
- **Systematic investigation** with step-by-step evidence collection
- **Call chain analysis**: Where methods are defined, called, and how they flow
- **Execution flow mapping**: Step-by-step execution paths with branching
- **Usage pattern analysis**: Frequency, context, parameter patterns
- **Dependency mapping**: Bidirectional dependencies and coupling analysis
- **Image support**: Analyze visual call flow diagrams, sequence diagrams
- **Multi-language support**: Works with any programming language

**Trace Modes:**

**`precision` Mode** - For methods/functions:
- Traces execution flow, call chains, and usage patterns
- Detailed branching analysis and side effects
- Shows when and how functions are called throughout the system
- Call hierarchy and depth analysis
- Return value usage and parameter passing patterns

**`dependencies` Mode** - For classes/modules/protocols:
- Maps bidirectional dependencies and structural relationships
- Identifies coupling and architectural dependencies
- Shows how components interact and depend on each other
- Inheritance hierarchies and protocol conformance
- Module-level dependency graphs

**`ask` Mode** - Interactive mode:
- Prompts you to choose between precision or dependencies
- Provides guidance on which mode is appropriate
- Explains trade-offs between modes

**Key Parameters:**

*Workflow Investigation Parameters:*
- `step` (required): Current tracing step description
- `step_number` (required): Current step number in tracing sequence
- `total_steps` (required): Estimated total investigation steps
- `next_step_required` (required): Whether another investigation step is needed
- `findings` (required): Discoveries about execution flow or dependencies
- `target_description` (required): What to trace and WHY you need this analysis
- `trace_mode` (required): precision|dependencies|ask
- `files_checked` (optional): All files examined during investigation
- `relevant_files` (optional): Files directly relevant to the trace
- `relevant_context` (optional): Methods/functions/classes involved
- `confidence` (optional): Confidence level in trace completeness
- `images` (optional): Visual references (call flow diagrams, sequence diagrams)

*Model Selection:*
- `model` (optional): Model to use (default: auto)
- `use_assistant_model` (optional): Use expert analysis phase (default: true)

**Workflow:**
1. **Step 1**: Describe what to trace and WHY (context is critical!)
2. **STOP** - Investigate code structure, call chains, dependencies
3. **Step 2+**: Report findings with concrete evidence
4. **Throughout**: Track findings, relevant files, execution paths
5. **Completion**: Once trace is comprehensive, signal completion
6. **Expert Analysis**: Receive detailed trace analysis

**Usage Examples:**

*Method Execution Tracing:*
```
"Trace how UserAuthManager.authenticate is used throughout the system"
```

*Class Dependency Mapping:*
```
"Generate a dependency trace for the PaymentProcessor class to understand its relationships"
```

*With Visual Context:*
```
"Trace the authentication flow using this sequence diagram to validate the implementation"
```

*Complex System Analysis:*
```
"Trace how OrderProcessor.processPayment flows through the entire system including all side effects"
```

**Best Practices:**
- **Provide context** - Explain WHY you need the trace (debugging, refactoring, understanding)
- **Be specific** - Target specific methods/classes rather than entire modules
- **Choose appropriate mode** - Use precision for execution flow, dependencies for structure
- **Include visual context** - Sequence diagrams or call flow charts help validate findings
- **Explain the goal** - Understanding, debugging, impact analysis, or refactoring planning

**When to Use:**
- Use `tracer` for: Understanding execution flow and dependencies
- Use `analyze` for: General code structure understanding
- Use `debug` for: Diagnosing specific runtime errors
- Use `codereview` for: Finding bugs and security issues

