# SDK Integration (Kimi/GLM)

## Purpose & Responsibility

The SDK Integration component provides a unified interface for interacting with multiple AI providers (Kimi and GLM). It abstracts the differences between provider APIs, implements consistent request/response handling, and manages provider-specific optimizations.

**Key Architecture (2025-10-20):**
- **Kimi uses OpenAI SDK** (fully compatible with OpenAI format)
- **GLM uses ZhipuAI SDK** (independent, NOT OpenAI compatible)
- **Supabase records EVERYTHING in parallel** (non-blocking async storage)
- **Fallback chain**: SDK (primary) → Supabase recovery → HTTP mode (if platform down)

---

## 🎯 **EXAI TOOL LANDSCAPE (4-TIER SYSTEM)**

**Last Updated:** 2025-10-29

### **Overview**

EXAI provides 33 tools organized into 4 tiers to prevent overwhelming agents while maintaining full functionality:

- **ESSENTIAL (3 tools)**: Absolute must-haves for basic operation
- **CORE (7 tools)**: Frequently used for common workflows (80% of use cases)
- **ADVANCED (7 tools)**: Specialized tools for complex scenarios
- **HIDDEN (16 tools)**: Internal/diagnostic/deprecated tools

**Progressive Disclosure:** Agents see Essential + Core (10 tools) by default. Advanced tools revealed based on context. Hidden tools completely invisible.

---

### **ESSENTIAL TIER (3 tools)** - Always Visible

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `status` | System status checking | Starting a session, checking if system is operational |
| `chat` | Basic communication interface | General questions, explanations, brainstorming |
| `planner` | Task planning and coordination | Complex tasks requiring structured planning |

**Usage:**
```python
# Check system health
status()

# Ask a question
chat(prompt="How do I implement OAuth2?")

# Plan complex task
planner(
    step="Break down authentication implementation",
    step_number=1,
    total_steps=3,
    next_step_required=True,
    findings="Initial analysis shows..."
)
```

---

### **CORE TIER (7 tools)** - Default Workflow

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `analyze` | Strategic architectural assessment | Understanding code structure, patterns, architecture |
| `codereview` | Systematic code review | Reviewing code for bugs, security issues, code smells |
| `debug` | Root cause investigation | Finding root cause of bugs, performance issues |
| `refactor` | Code improvement and modernization | Identifying code smells, decomposition opportunities |
| `testgen` | Test case generation | Generating unit tests, integration tests, edge cases |
| `thinkdeep` | Extended hypothesis-driven reasoning | Complex reasoning, architectural decisions |
| `smart_file_query` | **⭐ UNIFIED file operations** | ALL file operations (upload, query, chat, manage) |

**Usage:**
```python
# Analyze codebase
analyze(
    step="Analyze authentication system architecture",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Discovered JWT-based auth with Redis session storage"
)

# Review code
codereview(
    step="Review authentication changes for security issues",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Found potential SQL injection in login handler",
    relevant_files=["/mnt/project/src/auth/login.py"]
)

# Debug issue
debug(
    step="Investigate login failure",
    hypothesis="JWT token expiration issue",
    confidence="exploring",
    step_number=1,
    total_steps=2,
    next_step_required=True,
    findings="Token expires after 15 minutes, no refresh mechanism"
)

# File operations (REPLACES 6+ old tools)
smart_file_query(
    file_path="/mnt/project/EX-AI-MCP-Server/src/file.py",
    question="Analyze this code for security issues"
)
```

---

### **ADVANCED TIER (7 tools)** - Specialized Scenarios

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `consensus` | Multi-agent coordination | Complex decisions requiring multiple perspectives |
| `docgen` | Documentation generation | Generating comprehensive code documentation |
| `secaudit` | Security auditing | OWASP Top 10 analysis, compliance evaluation |
| `tracer` | Code execution tracing | Understanding execution flow, call chains |
| `precommit` | Pre-commit hook management | Validating changes before commit |
| `kimi_chat_with_tools` | Advanced Kimi capabilities | Advanced Kimi-specific features |
| `glm_payload_preview` | GLM payload inspection | Debugging GLM API calls |

**Usage:**
```python
# Multi-model consensus
consensus(
    step="Evaluate database migration proposal",
    models=[
        {"model": "glm-4.6", "stance": "for"},
        {"model": "kimi-k2-0905-preview", "stance": "against"}
    ],
    step_number=1,
    total_steps=2,
    next_step_required=True,
    findings="Initial analysis of migration proposal..."
)

# Security audit
secaudit(
    step="Audit authentication system for OWASP Top 10",
    audit_focus="owasp",
    threat_level="high",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Found SQL injection vulnerability in login handler"
)
```

---

### **HIDDEN TIER (16 tools)** - System/Diagnostic Only

**Diagnostic Tools:**
- `provider_capabilities` - System diagnostics
- `listmodels` - Model listing
- `activity` - Activity monitoring
- `version` - Version information
- `health` - Health checks
- `toolcall_log_tail` - Tool call logging
- `test_echo` - Load testing
- `kimi_capture_headers` - Header inspection
- `kimi_intent_analysis` - Intent classification

**⚠️ DEPRECATED FILE TOOLS (Use `smart_file_query` instead):**
- `kimi_upload_files` → Use `smart_file_query`
- `kimi_chat_with_files` → Use `smart_file_query`
- `kimi_manage_files` → Use `smart_file_query`
- `glm_upload_file` → Use `smart_file_query`
- `glm_multi_file_chat` → Use `smart_file_query`
- `glm_web_search` - Internal utility
- `kimi_web_search` - Internal utility

**Note:** Hidden tools are invisible to agents and should not be used directly. Use the recommended alternatives above.

---

### **Tool Selection Quick Reference**

```
File Operations → smart_file_query
Code Analysis → analyze
Code Review → codereview
Debugging → debug
Refactoring → refactor
Test Generation → testgen
Planning → planner
Deep Reasoning → thinkdeep
Security Audit → secaudit
Documentation → docgen
Code Tracing → tracer
Multi-Agent → consensus
Pre-Commit → precommit
```

**For detailed tool selection guidance, see:**
- `docs/00_Quick_Start_Guide.md` - Get started in 5 minutes
- `docs/01_Tool_Decision_Tree.md` - Comprehensive tool selection guide

---

## Architecture & Design Patterns

### Provider Abstraction Layer

```mermaid
graph TB
    subgraph "EXAI SDK Layer"
        AI[AI Provider Interface]
        PM[Provider Manager]
        RR[Request Router]
    end
    
    subgraph "Provider Implementations"
        Kimi[Kimi SDK]
        GLM[GLM SDK]
    end
    
    subgraph "SDK Native Features"
        KCS[Kimi Conversation State]
        GCS[GLM Conversation State]
        KCW[Kimi Context Window]
        GCW[GLM Context Window]
    end
    
    AI --> PM
    PM --> RR
    RR --> Kimi
    RR --> GLM
    Kimi --> KCS
    Kimi --> KCW
    GLM --> GCS
    GLM --> GCW
```

### Design Patterns

1. **Adapter Pattern**: Standardizes different provider APIs to a common interface
2. **Strategy Pattern**: Selects appropriate provider based on request characteristics
3. **Factory Pattern**: Creates provider-specific instances
4. **Observer Pattern**: Monitors provider performance and health

## SDK Native Conversation Management

### Kimi SDK (Moonshot) - Uses OpenAI SDK

**CRITICAL**: Kimi uses OpenAI SDK, NOT a custom SDK!

**Native Features:**
- Built-in conversation state management
- Automatic context window handling (model-dependent, see below)
- Token-aware message pruning
- Session persistence across API calls

**Context Windows by Model:**
- `kimi-k2-0905-preview`: **256K tokens** (262,144)
- `kimi-k2-turbo-preview`: **256K tokens** (262,144)
- `kimi-k2-0711-preview`: **128K tokens** (131,072)
- `kimi-thinking-preview`: **128K tokens** (131,072)
- `moonshot-v1-128k`: **128K tokens** (131,072)
- `moonshot-v1-32k`: **32K tokens** (32,768)
- `moonshot-v1-8k`: **8K tokens** (8,192)

**Usage:**
```python
from openai import OpenAI  # ← Uses OpenAI SDK!

client = OpenAI(
    api_key="your-kimi-api-key",
    base_url="https://api.moonshot.ai/v1"  # Point to Moonshot
)

# Multi-turn conversation - SDK handles context!
conversation = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Tell me more"}
]

response = client.chat.completions.create(
    model="kimi-k2-0905-preview",
    messages=conversation  # SDK manages context window automatically
)
```

### GLM SDK (Z.AI) - Uses ZhipuAI SDK

**CRITICAL**: GLM uses ZhipuAI SDK, NOT OpenAI compatible!

**Native Features:**
- Built-in conversation state management
- Automatic context window handling (model-dependent, see below)
- Token-aware message pruning
- Session persistence

**Context Windows by Model:**
- `glm-4.6`: **200K tokens** (200,000)
- `glm-4.5`: **128K tokens** (128,000)
- `glm-4.5-flash`: **128K tokens** (128,000)
- `glm-4.5-air`: **128K tokens** (128,000)
- `glm-4.5v`: **65K tokens** (65,536) - Vision model

**Usage:**
```python
from zhipuai import ZhipuAI  # ← Uses ZhipuAI SDK!

client = ZhipuAI(api_key="your-glm-api-key")

# SDK handles conversation state
response = client.chat.completions.create(
    model="glm-4.6",
    messages=conversation  # Automatic context management
)
```

## Key Files & Their Roles

```
src/
├── providers/
│   ├── __init__.py
│   ├── base.py              # Abstract base provider interface
│   ├── kimi_chat.py         # Kimi provider (uses SDK native)
│   ├── glm_chat.py          # GLM provider (uses SDK native)
│   └── manager.py           # Provider selection and management
└── config/
    └── providers.py         # Provider configuration
```

## Configuration Variables

```python
# .env.docker
# Kimi Configuration
KIMI_API_KEY=your_kimi_api_key
KIMI_BASE_URL=https://api.moonshot.ai/v1
KIMI_TIMEOUT=30
KIMI_MAX_RETRIES=3

# GLM Configuration
GLM_API_KEY=your_glm_api_key
GLM_BASE_URL=https://api.z.ai/api/paas/v4
GLM_TIMEOUT=30
GLM_MAX_RETRIES=3

# Provider Selection
DEFAULT_PROVIDER=kimi
ENABLE_FALLBACK=true
```

## Usage Examples

### Basic Provider Usage

```python
from src.providers.manager import ProviderManager

# Initialize provider manager
manager = ProviderManager()

# Get default provider
provider = manager.get_provider()
response = await provider.chat_completion(
    messages=[{"role": "user", "content": "Hello"}],
    model="auto"
)

# Get specific provider
kimi = manager.get_provider("kimi")
glm = manager.get_provider("glm")
```

### Multi-Turn Conversation (SDK Native)

```python
# Let SDK handle conversation state
conversation = [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "Show me an example"}
]

response = await provider.chat_completion(
    messages=conversation,  # SDK manages context automatically
    model="kimi-k2-0905-preview"
)
```

### Provider-Specific Features

```python
# Using Kimi's file analysis capability
kimi = manager.get_provider("kimi")
result = await kimi.analyze_file(
    file_path="/path/to/document.pdf",
    analysis_type="extract_key_points"
)

# Using GLM's code generation capability
glm = manager.get_provider("glm")
code = await glm.generate_code(
    language="python",
    description="Create a REST API with FastAPI"
)
```

## Common Issues & Solutions

### Issue: Provider API Rate Limits
**Solution**: Implement request throttling and use multiple API keys for rotation.

### Issue: Provider Authentication Failures
**Solution**: Verify API keys and implement automatic token refresh.

### Issue: Context Window Overflow
**Solution**: Let SDK handle context pruning automatically. Don't implement custom logic.

## Integration Points & Parallel Architecture

### Supabase Parallel Recording

**CRITICAL**: Supabase records EVERYTHING in parallel, NOT blocking user requests!

```
User Request → Tool Execution → SDK Provider → AI Response → User (FAST PATH)
                                      ↓
                              [PARALLEL ASYNC]
                                      ↓
                            Supabase Storage (Fire-and-Forget)
```

**Implementation:**
```python
async def handle_chat_request(messages, model):
    # 1. Execute SDK request (PRIMARY - fast path)
    response = await sdk_provider.chat_completion(messages, model)

    # 2. Return to user immediately (NO BLOCKING)
    await send_response_to_user(response)

    # 3. Record to Supabase in parallel (fire-and-forget)
    asyncio.create_task(
        supabase_storage.record_interaction(
            messages=messages,
            response=response,
            model=model,
            timestamp=datetime.now()
        )
    )
```

**Benefits:**
- Zero latency impact on user
- Complete audit trail of all interactions
- Fallback recovery if SDK fails
- Analytics and metrics tracking

### Fallback Chain

1. **SDK Mode (PRIMARY)**: Fast, native conversation management
2. **Supabase Recovery (SECONDARY)**: If SDK session expires, recover from Supabase
3. **HTTP Mode (TERTIARY)**: If platform down, use Supabase + direct HTTP calls (slower but works)

The SDK Integration component connects with:
- **MCP Server**: Provides AI capabilities for tool execution
- **Tool Manager**: Uses providers for specific tool implementations
- **Supabase Storage**: Records ALL interactions in parallel (non-blocking)
- **WebSocket Daemon**: Real-time streaming of responses

## Provider-Specific Considerations

### Kimi Provider (OpenAI SDK)
- **SDK**: OpenAI SDK (fully compatible)
- **Strengths**: Superior text analysis, file processing, LARGE context windows (up to 256K)
- **Limitations**: Higher latency for complex requests
- **Best Use Cases**: Document analysis, content extraction, long conversations
- **Top Models**:
  - kimi-k2-0905-preview (256K context)
  - kimi-k2-turbo-preview (256K context, faster)
  - kimi-k2-0711-preview (128K context)

### GLM Provider (ZhipuAI SDK)
- **SDK**: ZhipuAI SDK (NOT OpenAI compatible)
- **Strengths**: Faster response times, better for code generation, thinking mode
- **Limitations**: Smaller context window compared to Kimi K2 models
- **Best Use Cases**: Code generation, quick text completions, reasoning tasks
- **Top Models**:
  - glm-4.6 (200K context, thinking mode)
  - glm-4.5-flash (128K context, fastest)
  - glm-4.5 (128K context)

## Performance Optimization

1. **Use SDK Native Features**: Don't reinvent conversation management
2. **Response Caching**: Cache frequently requested responses
3. **Connection Pooling**: Reuse HTTP connections for multiple requests
4. **Provider Selection**: Choose optimal provider based on request type

## Migration from Custom to SDK Native

**Before (Custom Supabase Management):**
```python
# Load conversation from Supabase
messages = await supabase_memory.load_messages(conversation_id)
# Custom context pruning (5 msgs, 4K tokens)
pruned = prune_context(messages, max_tokens=4000)
# Send to provider
response = await provider.chat(pruned)
```

**After (SDK Native):**
```python
# Load conversation from SDK or build from audit trail
messages = conversation_history  # Full history
# SDK handles context automatically
response = await provider.chat_completion(messages)
# Audit to Supabase (fire-and-forget)
await audit_log(conversation_id, messages, response)
```

**Benefits:**
- 70% less code
- No custom context pruning logic
- Better SDK feature utilization
- Automatic context window handling
- Reduced operational complexity

