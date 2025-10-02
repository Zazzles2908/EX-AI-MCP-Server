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

**Simple Tools (Request/Response):**
- `chat` - General conversation with web search support
- `thinkdeep` - Multi-stage investigation and reasoning
- `planner` - Sequential step-by-step planning
- `consensus` - Multi-model consensus workflow
- `challenge` - Critical analysis and truth-seeking

**Workflow Tools (Multi-Step with Pause Enforcement):**
- `analyze` - Comprehensive code analysis
- `debug` - Root cause analysis and debugging
- `codereview` - Systematic code review
- `precommit` - Pre-commit validation
- `refactor` - Refactoring analysis and recommendations
- `testgen` - Test generation with edge case coverage
- `tracer` - Code tracing and dependency mapping
- `secaudit` - Security audit and vulnerability assessment
- `docgen` - Documentation generation

**Agentic Enhancements (Phase 1 Implementation):**
- Self-assessment of information sufficiency
- Early termination when goals achieved
- Dynamic step adjustment mid-workflow
- Configurable sufficiency thresholds

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

