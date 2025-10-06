# Diagnostics and Logging Guide

**Version:** 1.0  
**Last Updated:** 2025-10-03  
**Status:** ✅ Implemented in Wave 2

---

## Overview

The EX-AI-MCP-Server provides comprehensive diagnostic tools and logging capabilities to help troubleshoot issues, monitor performance, and understand system behavior.

---

## Diagnostic Tools

### 1. Self-Check Tool

**Purpose:** Quick health check of the MCP server

**Usage:**
```json
{
  "tool": "self-check_EXAI-WS",
  "log_lines": 40
}
```

**Returns:**
- Configured providers
- Number of visible tools
- Key environment variables (names only)
- Recent log tail from mcp_server.log

**When to Use:**
- Server not responding
- Tools not appearing
- Provider issues
- Quick status check

---

### 2. Provider Diagnostics Tool

**Purpose:** Comprehensive provider health and configuration check

**Usage:**
```json
{
  "tool": "provider-diagnostics_EXAI-WS",
  "provider": "all",
  "include_test_call": false
}
```

**Parameters:**
- `provider`: "all", "GLM", or "KIMI"
- `include_test_call`: Perform test API call (default: false)

**Returns:**
- API key status
- Model availability
- Capabilities (web search, streaming, etc.)
- Configuration issues
- Recommendations

**When to Use:**
- Provider not working
- Models not available
- Web search issues
- Configuration validation

---

### 3. Health Tool

**Purpose:** MCP/Provider health with observability log tails

**Usage:**
```json
{
  "tool": "health_EXAI-WS",
  "tail_lines": 50
}
```

**Returns:**
- Configured providers
- Available models
- Metrics log tail
- Tool calls log tail

**When to Use:**
- Performance monitoring
- Usage tracking
- Error investigation

---

### 4. Status Tool

**Purpose:** Current server status and statistics

**Usage:**
```json
{
  "tool": "status_EXAI-WS"
}
```

**Returns:**
- Server uptime
- Request count
- Active connections
- Resource usage

---

## Logging System

### Log Files

**Location:** `.logs/` directory

**Files:**
1. **mcp_server.log** - Main server log
2. **metrics.jsonl** - Performance metrics (JSONL format)
3. **toolcalls.jsonl** - Tool call history (JSONL format)

### Log Levels

**Configuration:** Set via `LOG_LEVEL` environment variable

```env
# Available levels
LOG_LEVEL=DEBUG    # Verbose debugging
LOG_LEVEL=INFO     # General information (default)
LOG_LEVEL=WARNING  # Warnings only
LOG_LEVEL=ERROR    # Errors only
```

### Log Categories

**1. MCP Activity Log**
- Progress messages
- Tool execution flow
- User interactions

**2. Provider Log**
- API calls
- Model selection
- Response handling

**3. Tool Log**
- Tool invocations
- Parameter validation
- Response formatting

**4. Metrics Log**
- Request latency
- Token usage
- Cost tracking

---

## Progress Indicators

### Configuration

**Enable/Disable:**
```env
STREAM_PROGRESS=true   # Enable progress messages (default)
STREAM_PROGRESS=false  # Disable progress messages
```

### Progress Message Types

**Analysis Operations:**
- 🔍 Starting analysis
- 📂 Loading files
- ⚙️  Processing context
- 🤖 Calling AI model
- 📝 Processing response

**Web Search:**
- 🔎 Performing web search
- ✅ Search complete
- ❌ Search failed

**Tool Execution:**
- 🔧 Tool call detected
- ⚡ Executing tool
- ✅ Tool complete

**Workflow:**
- 📊 Step progress
- 🎓 Expert analysis
- ✅ Workflow complete

---

## Troubleshooting Guide

### Common Issues

#### 1. Provider Not Working

**Symptoms:**
- "Provider not configured" error
- No models available
- API call failures

**Diagnosis:**
```json
{
  "tool": "provider-diagnostics_EXAI-WS",
  "provider": "all",
  "include_test_call": true
}
```

**Solutions:**
- Check API key is set
- Verify base URL is correct
- Test API connectivity
- Check firewall/proxy settings

---

#### 2. Web Search Not Working

**Symptoms:**
- Models say "I don't have real-time access"
- Search results not incorporated
- Tool calls not detected

**Diagnosis:**
```json
{
  "tool": "provider-diagnostics_EXAI-WS",
  "provider": "KIMI"
}
```

**Solutions:**
- Kimi: Ensure `KIMI_ENABLE_INTERNET_SEARCH=true`
- GLM: Web search currently non-functional (known issue)
- Check progress messages for tool execution

---

#### 3. Tools Not Appearing

**Symptoms:**
- Expected tools missing
- Tool registry empty
- "Unknown tool" errors

**Diagnosis:**
```json
{
  "tool": "self-check_EXAI-WS"
}
```

**Solutions:**
- Check environment variables
- Verify tool registry configuration
- Restart server
- Check logs for initialization errors

---

#### 4. Slow Performance

**Symptoms:**
- Long response times
- Timeouts
- High latency

**Diagnosis:**
```json
{
  "tool": "health_EXAI-WS",
  "tail_lines": 100
}
```

**Solutions:**
- Check metrics log for bottlenecks
- Verify network connectivity
- Check model selection (use faster models)
- Enable streaming for long responses

---

## Monitoring Best Practices

### 1. Regular Health Checks

Run health checks periodically:
```bash
# Every hour
*/60 * * * * curl -X POST http://localhost:8765/health
```

### 2. Log Rotation

Configure log rotation to prevent disk space issues:
```bash
# Rotate logs daily, keep 7 days
logrotate -f /path/to/logrotate.conf
```

### 3. Metrics Collection

Monitor key metrics:
- Request latency (p50, p95, p99)
- Error rate
- Token usage
- Cost per request

### 4. Alert Configuration

Set up alerts for:
- High error rate (>5%)
- Slow responses (>30s)
- Provider failures
- Disk space low

---

## Advanced Diagnostics

### Debug Mode

Enable debug logging for detailed troubleshooting:
```env
LOG_LEVEL=DEBUG
STREAM_PROGRESS=true
```

### Network Diagnostics

Test provider connectivity:
```bash
# Test GLM API
curl -H "Authorization: Bearer $GLM_API_KEY" https://api.z.ai/api/paas/v4/chat/completions

# Test Kimi API
curl -H "Authorization: Bearer $KIMI_API_KEY" https://api.moonshot.ai/v1/models
```

### Performance Profiling

Enable performance profiling:
```env
ENABLE_PROFILING=true
PROFILE_OUTPUT_DIR=.logs/profiles
```

---

## Related Documentation

- [UX Improvements](../features/ux-improvements.md)
- [Provider Configuration](../configuration/providers.md)
- [Error Handling](./error-handling.md)

