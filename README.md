# EX-AI MCP Server - Production-Ready v2.0

> 2025-09-28 Cleanup & Reorganization Summary
>
> - Architecture: GLM-first MCP WebSocket daemon; provider-native web browsing via GLM tools schema (no standalone web-search tool)
> - Removed: Orchestrator tools (autopilot/orchestrate_auto/browse_orchestrator), custom GLM web search tool, streaming demo tools
> - Registry: Simplified tool surface; diagnostics retained; listmodels hardened for optional OpenRouter
> - Providers: Kimi ✅, GLM ✅; OpenRouter ❌ (optional, not configured); Custom/Local ❌
> - Observability: .logs/ directory initialized for JSONL metrics
>


A production-ready MCP (Model Context Protocol) server with intelligent routing capabilities using GLM-4.5-Flash as an AI manager.

## 🚀 Key Features

### Intelligent Routing System
- **GLM-4.5-Flash AI Manager**: Orchestrates routing decisions between providers
- **GLM Provider**: Specialized for web browsing and search tasks
- **Kimi Provider**: Optimized for file processing and document analysis
- **Cost-Aware Routing**: Intelligent cost optimization and load balancing
- **Fallback Mechanisms**: Automatic retry with alternative providers

### Production-Ready Architecture
- **MCP Protocol Compliance**: Full WebSocket and stdio transport support
- **Error Handling**: Comprehensive retry logic and graceful degradation
- **Performance Monitoring**: Real-time provider statistics and optimization
- **Security**: API key validation and secure input handling
- **Logging**: Structured logging with configurable levels

### Provider Capabilities
- **GLM (ZhipuAI)**: Web search, browsing, reasoning, code analysis
- **Kimi (Moonshot)**: File processing, document analysis, multi-format support

## 📦 Installation

### Prerequisites
- Python 3.8+
- Valid API keys for ZhipuAI and Moonshot

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Configuration
Copy `.env.production` to `.env` and configure your API keys:

```bash
cp .env.production .env
```

Edit `.env` with your API keys:
```env
# Required API Keys
ZHIPUAI_API_KEY=your_zhipuai_api_key_here
MOONSHOT_API_KEY=your_moonshot_api_key_here

# Intelligent Routing (default: enabled)
INTELLIGENT_ROUTING_ENABLED=true
AI_MANAGER_MODEL=glm-4.5-flash
WEB_SEARCH_PROVIDER=glm
FILE_PROCESSING_PROVIDER=kimi
COST_AWARE_ROUTING=true

# Production Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
REQUEST_TIMEOUT=30
ENABLE_FALLBACK=true
```

## 🏃 Quick Start

### Run the Server
```bash
python server.py
```

### WebSocket Mode (Optional)
```bash
# Enable WebSocket transport
export MCP_WEBSOCKET_ENABLED=true
export MCP_WEBSOCKET_PORT=8080
python server.py
```

## 🔧 Configuration

### Core Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `INTELLIGENT_ROUTING_ENABLED` | `true` | Enable intelligent routing system |
| `AI_MANAGER_MODEL` | `glm-4.5-flash` | Model for routing decisions |
| `WEB_SEARCH_PROVIDER` | `glm` | Provider for web search tasks |
| `FILE_PROCESSING_PROVIDER` | `kimi` | Provider for file processing |
| `COST_AWARE_ROUTING` | `true` | Enable cost optimization |

### Performance Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | `3` | Maximum retry attempts |
| `REQUEST_TIMEOUT` | `30` | Request timeout in seconds |
| `MAX_CONCURRENT_REQUESTS` | `10` | Concurrent request limit |
| `RATE_LIMIT_PER_MINUTE` | `100` | Rate limiting threshold |

### WebSocket Configuration
| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_WEBSOCKET_ENABLED` | `true` | Enable WebSocket transport |
| `MCP_WEBSOCKET_PORT` | `8080` | WebSocket server port |
| `MCP_WEBSOCKET_HOST` | `0.0.0.0` | WebSocket bind address |

## 🧠 Intelligent Routing

The server uses GLM-4.5-Flash as an AI manager to make intelligent routing decisions:

### Task-Based Routing
- **Web Search Tasks** → GLM Provider (native web browsing)
- **File Processing Tasks** → Kimi Provider (document analysis)
- **Code Analysis Tasks** → Best available provider based on performance
- **General Chat** → Load-balanced between providers

### Fallback Strategy
1. Primary provider attempt
2. Automatic fallback to secondary provider
3. Retry with exponential backoff
4. Graceful error handling

### Cost Optimization
- Real-time provider performance tracking
- Cost-aware routing decisions
- Load balancing based on response times
- Automatic provider selection optimization

## 🛠 Development

### Project Structure
```
ex-ai-mcp-server/
├── docs/
│   ├── architecture/
│   └── provider_API/
│       └── GLM/
├── monitoring/
│   └── monitoring_integration_plan.md
├── scripts/
│   ├── ws/
│   └── maintenance/
├── tools/
│   ├── registry.py
│   ├── chat.py
│   ├── capabilities/
│   │   ├── listmodels.py
│   │   └── provider_capabilities.py
│   ├── diagnostics/
│   │   ├── health.py
│   │   ├── status.py
│   │   └── toolcall_log_tail.py
│   ├── providers/
│   │   ├── glm/
│   │   │   └── glm_files.py
│   │   └── kimi/
│   │       └── kimi_upload.py
│   └── workflows/
│       ├── analyze.py
│       ├── debug.py
│       ├── codereview.py
│       ├── refactor.py
│       ├── secaudit.py
│       ├── planner.py
│       ├── tracer.py
│       ├── testgen.py
│       ├── consensus.py
│       ├── thinkdeep.py
│       └── docgen.py
├── src/
│   ├── providers/
│   │   ├── base.py
│   │   ├── registry.py
│   │   ├── glm.py
│   │   └── kimi.py
│   ├── router/                # optional; may be pruned if unused
│   └── utils/                 # internal libs (if present)
├── utils/
│   ├── health.py
│   ├── metrics.py
│   ├── model_restrictions.py
│   └── observability.py
├── .logs/
│   └── .gitkeep
├── README.md
├── .env.example
└── requirements.txt
```

> Removed legacy components (as of 2025-09-28):
> - tools/orchestrators/*
> - tools/streaming/*
> - tools/providers/glm/glm_web_search.py

### Adding New Providers
1. Extend `BaseProvider` in `providers.py`
2. Implement required methods
3. Register in `ProviderFactory`
4. Update routing logic in `intelligent_router.py`

## 📊 Monitoring

### Logging
The server provides structured logging with configurable levels:
- `DEBUG`: Detailed routing decisions and API calls
- `INFO`: General operation status and routing choices
- `WARNING`: Fallback activations and performance issues
- `ERROR`: API failures and critical errors

### Performance Metrics
- Provider success rates
- Average response times
- Routing decision confidence
- Cost tracking per provider

## 🔒 Security

- API key validation on startup
- Secure input handling and validation
- Rate limiting and request throttling
- Error message sanitization

## 🚀 Deployment

### Production Checklist
- [ ] Configure API keys in `.env`
- [ ] Set appropriate log levels
- [ ] Configure rate limiting
- [ ] Enable WebSocket if needed
- [ ] Set up monitoring and alerting
- [ ] Test fallback mechanisms

### Docker Deployment (Optional)
```bash
docker build -t ex-ai-mcp-server .
docker run -d --env-file .env -p 8080:8080 ex-ai-mcp-server
```

## 📝 API Reference

### Available Tools
The server exposes various MCP tools through the intelligent routing system:
- Code analysis and review tools
- Web search and browsing capabilities
- File processing and document analysis
- General chat and reasoning tools

### MCP Protocol
Full compliance with MCP specification:
- Tool discovery and registration
- Request/response handling
- Error propagation
- WebSocket and stdio transports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the logs for detailed error information
2. Verify API key configuration
3. Test individual providers
4. Open an issue with reproduction steps

---

**EX-AI MCP Server v2.0** - Production-ready intelligent routing for MCP applications.
