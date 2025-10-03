# Configuration Management Guide

**Date:** 2025-10-01  
**Phase:** 0 (Architecture & Design)  
**Task:** 0.6  
**Status:** ✅ COMPLETE

---

## Executive Summary

This guide provides comprehensive configuration management documentation for the EX-AI-MCP-Server, aligned with the UX improvements from Task 0.5 and the design philosophy from Task 0.1. It introduces a simplified two-tier configuration approach: `.env.minimal` for quick start and `.env.advanced` for power users.

**Key Principles:**
- **Simplicity First:** Minimal configuration gets you started in 5 minutes
- **Progressive Disclosure:** Advanced features available when needed
- **Fail Fast:** Configuration validation on startup
- **Clear Defaults:** Sensible defaults for 90% of use cases

---

## Configuration Tiers

### Tier 1: Minimal Configuration (Quick Start)

**File:** `.env.minimal` (10 lines)  
**Use Case:** New users, development, simple deployments  
**Time to Configure:** 2 minutes

```env
# EX-AI MCP Server - Minimal Configuration
# Copy to .env and add your API keys

# Required: At least one provider API key
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# Optional: Basic settings (defaults shown)
DEFAULT_MODEL=glm-4.5-flash
LOG_LEVEL=INFO
EXAI_WS_PORT=8079
```

**What This Gives You:**
- ✅ Full chat functionality
- ✅ All workflow tools (analyze, debug, thinkdeep, etc.)
- ✅ GLM web browsing
- ✅ Kimi file processing
- ✅ Intelligent routing
- ✅ Structured logging

### Tier 2: Advanced Configuration (Power Users)

**File:** `.env.advanced` (reference only)  
**Use Case:** Production deployments, custom setups, performance tuning  
**Time to Configure:** 15-30 minutes

See [Advanced Configuration Reference](#advanced-configuration-reference) below.

---

## Complete Configuration Reference

### Core Settings (Required)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GLM_API_KEY` | ✅ (or KIMI) | - | ZhipuAI API key for GLM models |
| `KIMI_API_KEY` | ✅ (or GLM) | - | Moonshot API key for Kimi models |
| `DEFAULT_MODEL` | ❌ | `glm-4.5-flash` | Default model for chat and tools |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `EXAI_WS_PORT` | ❌ | `8079` | WebSocket server port |

**Validation Rules:**
- At least one API key (GLM or KIMI) must be provided
- `DEFAULT_MODEL` must be a valid model name
- `LOG_LEVEL` must be one of: DEBUG, INFO, WARNING, ERROR
- `EXAI_WS_PORT` must be 1024-65535

---

### Provider Configuration

#### GLM (ZhipuAI) Provider

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GLM_API_KEY` | ✅ | - | API key (required for GLM) |
| `GLM_API_URL` | ❌ | `https://api.z.ai/api/paas/v4` | API endpoint (international users) |
| `GLM_ENABLE_WEB_BROWSING` | ❌ | `true` | Enable web search capability |
| `GLM_STREAM_ENABLED` | ❌ | `false` | Enable streaming responses |

**Aliases (Backward Compatibility):**
- `ZHIPUAI_API_KEY` → `GLM_API_KEY`
- `ZHIPUAI_API_URL` → `GLM_API_URL`
- `ZHIPUAI_BASE_URL` → `GLM_API_URL`

**Note:** For international users, use `GLM_API_URL=https://api.z.ai/api/paas/v4` (NOT mainland China endpoint)

#### Kimi (Moonshot) Provider

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `KIMI_API_KEY` | ✅ | - | API key (required for Kimi) |
| `KIMI_API_URL` | ❌ | `https://api.moonshot.ai/v1` | API endpoint |
| `KIMI_ENABLE_INTERNET_SEARCH` | ❌ | `true` | Enable internet search |
| `KIMI_STREAM_ENABLED` | ❌ | `false` | Enable streaming responses |
| `KIMI_DEFAULT_MODEL` | ❌ | `kimi-k2-0711-preview` | Default Kimi model |
| `KIMI_THINKING_MODEL` | ❌ | `kimi-thinking-preview` | Model for deep reasoning |
| `KIMI_FILES_MAX_SIZE_MB` | ❌ | `20` | Max file upload size (MB) |

**Aliases (Backward Compatibility):**
- `KIMI_BASE_URL` → `KIMI_API_URL`
- `MOONSHOT_API_KEY` → `KIMI_API_KEY`

---

### Advanced Settings (Optional)

#### Routing & Intelligence

| Variable | Default | Description |
|----------|---------|-------------|
| `ROUTER_ENABLED` | `true` | Enable intelligent routing |
| `COST_AWARE_ROUTING` | `true` | Optimize for cost |

#### Timeouts & Retries

| Variable | Default | Description |
|----------|---------|-------------|
| `HTTP_CONNECT_TIMEOUT` | `10` | Connection timeout (seconds) |
| `HTTP_READ_TIMEOUT` | `60` | Read timeout (seconds) |
| `HTTP_TOTAL_TIMEOUT` | `90` | Total request timeout (seconds) |
| `KIMI_CONNECT_TIMEOUT_SECS` | `10` | Kimi connection timeout |
| `KIMI_READ_TIMEOUT_SECS` | `300` | Kimi read timeout |

#### Caching (Kimi)

| Variable | Default | Description |
|----------|---------|-------------|
| `KIMI_CACHE_TOKEN_TTL_SECS` | `1800` | Cache token TTL (30 min) |
| `KIMI_CACHE_TOKEN_LRU_MAX` | `256` | Max cached tokens |

#### Logging & Monitoring

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LOG_MAX_SIZE` | `10MB` | Max log file size |
| `LOG_BACKUP_COUNT` | `5` | Number of log backups |

---

## Configuration Validation

### Startup Validation

The server validates configuration on startup and fails fast with clear error messages:

```python
# Example validation errors
ERROR: At least one API key required (GLM_API_KEY or KIMI_API_KEY)
ERROR: Invalid LOG_LEVEL 'TRACE'. Must be: DEBUG, INFO, WARNING, ERROR
ERROR: Invalid EXAI_WS_PORT '99999'. Must be 1024-65535
```

### Manual Validation

Use the `selfcheck` tool to validate configuration:

```bash
# Via MCP
{"tool": "selfcheck"}

# Expected output
{
  "status": "ok",
  "providers": ["GLM", "KIMI"],
  "config_valid": true,
  "warnings": []
}
```

---

## Best Practices by Deployment Scenario

### Development

**Recommended Configuration:**
```env
GLM_API_KEY=your_dev_key
KIMI_API_KEY=your_dev_key
DEFAULT_MODEL=glm-4.5-flash
LOG_LEVEL=DEBUG
GLM_STREAM_ENABLED=false
KIMI_STREAM_ENABLED=false
```

**Rationale:**
- DEBUG logging for troubleshooting
- Streaming disabled for simpler debugging
- Fast model (glm-4.5-flash) for quick iteration

### Staging

**Recommended Configuration:**
```env
GLM_API_KEY=your_staging_key
KIMI_API_KEY=your_staging_key
DEFAULT_MODEL=glm-4.5-flash
LOG_LEVEL=INFO
GLM_STREAM_ENABLED=true
KIMI_STREAM_ENABLED=true
ROUTER_ENABLED=true
COST_AWARE_ROUTING=true
```

**Rationale:**
- INFO logging (production-like)
- Streaming enabled (test production behavior)
- Intelligent routing enabled
- Cost optimization enabled

### Production

**Recommended Configuration:**
```env
GLM_API_KEY=your_prod_key
KIMI_API_KEY=your_prod_key
DEFAULT_MODEL=glm-4.5-flash
LOG_LEVEL=WARNING
GLM_STREAM_ENABLED=true
KIMI_STREAM_ENABLED=true
ROUTER_ENABLED=true
COST_AWARE_ROUTING=true
HTTP_TOTAL_TIMEOUT=120
KIMI_FILES_MAX_SIZE_MB=50
```

**Rationale:**
- WARNING logging (reduce noise)
- Streaming enabled (better UX)
- Increased timeouts for reliability
- Higher file size limit for production use

---

## Troubleshooting Common Configuration Issues

### Issue 1: "At least one API key required"

**Cause:** Neither GLM_API_KEY nor KIMI_API_KEY is set

**Fix:**
```env
# Add at least one API key
GLM_API_KEY=your_key_here
# OR
KIMI_API_KEY=your_key_here
```

### Issue 2: "Connection refused" or "Invalid API key"

**Cause:** Wrong API endpoint or invalid key

**Fix for International Users:**
```env
# Use api.z.ai for international access (NOT mainland China)
GLM_API_URL=https://api.z.ai/api/paas/v4
GLM_API_KEY=your_valid_key
```

### Issue 3: "Request timeout"

**Cause:** Default timeouts too short for large requests

**Fix:**
```env
HTTP_TOTAL_TIMEOUT=180
KIMI_READ_TIMEOUT_SECS=600
```

### Issue 4: "File too large"

**Cause:** File exceeds default 20MB limit

**Fix:**
```env
KIMI_FILES_MAX_SIZE_MB=100
```

### Issue 5: Streaming not working

**Cause:** Streaming disabled or provider doesn't support it

**Fix:**
```env
GLM_STREAM_ENABLED=true
KIMI_STREAM_ENABLED=true
```

---

## Migration Guide

### From .env.production to .env.minimal

**Old (.env.production - 100+ lines):**
```env
ZHIPUAI_API_KEY=xxx
MOONSHOT_API_KEY=yyy
INTELLIGENT_ROUTING_ENABLED=true
AI_MANAGER_MODEL=glm-4.5-flash
# ... 90+ more lines
```

**New (.env.minimal - 10 lines):**
```env
GLM_API_KEY=xxx
KIMI_API_KEY=yyy
DEFAULT_MODEL=glm-4.5-flash
LOG_LEVEL=INFO
```

**Migration Steps:**
1. Copy `.env.minimal` to `.env`
2. Transfer API keys: `ZHIPUAI_API_KEY` → `GLM_API_KEY`, `MOONSHOT_API_KEY` → `KIMI_API_KEY`
3. Set `DEFAULT_MODEL` (was `AI_MANAGER_MODEL`)
4. Remove all other settings (sensible defaults apply)
5. Test with `selfcheck` tool

---

## Alignment with Design Philosophy

This configuration management approach supports the design principles from Task 0.1:

1. **Simplicity Over Complexity:** Two-tier approach (minimal vs. advanced)
2. **User-Centric Design:** Quick start in 2 minutes, progressive disclosure
3. **Fail Fast, Fail Clear:** Validation on startup with clear error messages
4. **Configuration Over Code:** All behavior configurable via environment

---

**Task 0.6 Status:** ✅ COMPLETE

