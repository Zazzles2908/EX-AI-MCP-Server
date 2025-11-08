# EX-AI MCP Server - Centralized Configuration System

## 🎯 Overview

The centralized configuration system prevents configuration drift by providing a **single source of truth** for all configuration values. No more hardcoded ports or scattered settings!

---

## 🏗️ Architecture

```
src/config/
├── __init__.py          # Main config interface
├── settings.py          # Central configuration with type safety
├── secrets_manager.py   # Secure secret management with Supabase
└── drift_detector.py    # Configuration drift detection
```

### Key Features
- ✅ **Single Source of Truth** - All config in one place
- ✅ **Type Safety** - Type hints and validation
- ✅ **Supabase Integration** - Secure secret storage
- ✅ **Environment Variables** - Fallback for local development
- ✅ **Drift Detection** - Identifies configuration changes
- ✅ **Zero Hardcoding** - All values centralized

---

## 🚀 Quick Start

### 1. Basic Usage

```python
from src.config import get_config

# Get configuration
config = get_config()

# Use WebSocket settings
port = config.ws_port  # Automatically 3000
host = config.ws_host  # Automatically 127.0.0.1
uri = config.get_websocket_uri()  # ws://127.0.0.1:3000

# Use API keys
kimi_key = config.kimi_api_key
glm_key = config.glm_api_key

# Use timeouts
timeout = config.simple_tool_timeout
```

### 2. Secure Secret Retrieval

```python
from src.config.secrets_manager import get_secrets_manager

# Get secrets manager
secrets = get_secrets_manager()

# Retrieve JWT token
jwt_token = secrets.get_jwt_token("claude")

# Get API key from Supabase
api_key = secrets.get_secret("KIMI_API_KEY")
```

### 3. Check for Configuration Drift

```python
from src.config import check_config_drift

# Check if config has changed
has_drift, details = check_config_drift()
if has_drift:
    print("Configuration drift detected!")
    for detail in details:
        print(f"  - {detail}")
```

---

## 🔒 Security Features

### 1. Supabase-Backed Secret Storage

**Benefits:**
- Secrets stored in secure Supabase database
- Row-level security (RLS) policies
- Encrypted at rest
- No secrets in source code

**Tables Created:**
- `jwt_tokens` - Store JWT tokens for clients
- `secrets` - Store API keys and sensitive config

### 2. Environment Variable Fallback

```python
#优先级 (Priority order):
# 1. Supabase (secure)
# 2. Environment variables (local dev)
# 3. Default values (config/settings.py)
```

### 3. No Hardcoded Secrets

**Before (CRITICAL RISK):**
```python
# ❌ DANGEROUS
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIs..."
```

**After (SECURE):**
```python
# ✅ SECURE
from src.config.secrets_manager import get_secrets_manager
secrets = get_secrets_manager()
jwt_token = secrets.get_jwt_token("claude")
```

---

## 📦 Migration Guide

### Step 1: Replace Hardcoded Ports

**Before:**
```python
# scripts/ws/ws_chat_once.py
PORT = int(os.getenv("EXAI_WS_PORT", "8765"))  # Wrong!
```

**After:**
```python
# scripts/ws/ws_chat_once.py
from src.config import get_config
config = get_config()
PORT = config.ws_port  # Always correct!
```

### Step 2: Secure JWT Token Handling

**Before:**
```python
# scripts/setup_claude_connection.py
EXAI_JWT_TOKEN_CLAUDE = "eyJ..."  # HARDCODED!
```

**After:**
```python
# scripts/setup_claude_connection.py
from src.config.secrets_manager import get_secrets_manager
secrets = get_secrets_manager()
EXAI_JWT_TOKEN_CLAUDE = secrets.get_jwt_token("claude")
if not EXAI_JWT_TOKEN_CLAUDE:
    raise ValueError("JWT token not found. Use Supabase or environment variable.")
```

### Step 3: Add Configuration Validation

**Before:**
```python
# No validation
port = int(os.getenv("EXAI_WS_PORT", "8765"))
```

**After:**
```python
# With validation
from src.config import get_config
config = get_config()
if not (1024 <= config.ws_port <= 65535):
    raise ValueError(f"Invalid port: {config.ws_port}")
```

---

## 🔧 Configuration Reference

### WebSocket Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ws_host` | str | 127.0.0.1 | WebSocket host |
| `ws_port` | int | 3000 | **WebSocket port (host)** |
| `ws_token` | str | test-token-12345 | Authentication token |
| `ws_connect_timeout` | int | 10 | Connection timeout (seconds) |
| `ws_max_size` | int | 20MB | Max message size |

### API Provider Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `kimi_api_key` | str | - | Kimi API key |
| `glm_api_key` | str | - | GLM API key |
| `kimi_default_model` | str | kimi-k2-0711-preview | Default Kimi model |
| `glm_default_model` | str | glm-4.5-flash | Default GLM model |

### Supabase Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `supabase_url` | str | - | Supabase project URL |
| `supabase_anon_key` | str | - | Supabase anonymous key |
| `supabase_service_key` | str | - | Supabase service role key |

### Timeout Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `simple_tool_timeout` | int | 60 | Simple tool timeout (sec) |
| `workflow_tool_timeout` | int | 120 | Workflow tool timeout (sec) |
| `glm_timeout` | int | 90 | GLM API timeout (sec) |
| `kimi_timeout` | int | 120 | Kimi API timeout (sec) |
| `kimi_websearch_timeout` | int | 150 | Kimi web search timeout (sec) |

### Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `jwt_secret_key` | str | - | JWT signing secret |
| `jwt_algorithm` | str | HS256 | JWT algorithm |
| `jwt_issuer` | str | exai-mcp-server | JWT issuer |
| `jwt_audience` | str | exai-mcp-client | JWT audience |
| `secure_inputs_enforced` | bool | true | Enforce input validation |
| `strict_file_size_rejection` | bool | true | Reject large files |

---

## 🛠️ Environment Variables

Create a `.env` file in the project root:

```env
# ============================================================================
# WEBSOCKET CONFIGURATION
# ============================================================================
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3000
EXAI_WS_TOKEN=test-token-12345

# ============================================================================
# API PROVIDERS
# ============================================================================
KIMI_API_KEY=your-kimi-api-key
GLM_API_KEY=your-glm-api-key

# ============================================================================
# SUPABASE
# ============================================================================
SUPABASE_URL=https://mxaazuhlqewmkweewyaz.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# ============================================================================
# JWT CONFIGURATION
# ============================================================================
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ISSUER=exai-mcp-server
JWT_AUDIENCE=exai-mcp-client

# ============================================================================
# TIMEOUTS
# ============================================================================
SIMPLE_TOOL_TIMEOUT_SECS=60
WORKFLOW_TOOL_TIMEOUT_SECS=120
EXPERT_ANALYSIS_TIMEOUT_SECS=90
GLM_TIMEOUT_SECS=90
KIMI_TIMEOUT_SECS=120
KIMI_WEB_SEARCH_TIMEOUT_SECS=150

# ============================================================================
# SECURITY
# ============================================================================
SECURE_INPUTS_ENFORCED=true
STRICT_FILE_SIZE_REJECTION=true

# ============================================================================
# SESSION
# ============================================================================
EX_SESSION_SCOPE_STRICT=true
EX_SESSION_SCOPE_ALLOW_CROSS_SESSION=false

# ============================================================================
# LOGGING
# ============================================================================
LOG_LEVEL=INFO
```

---

## 📊 Supabase Integration

### Storing Secrets in Supabase

**Method 1: Using Supabase MCP**
```python
# Store JWT token
mcp__supabase-mcp-full__execute_sql(
    project_id="mxaazuhlqewmkweewyaz",
    query="INSERT INTO jwt_tokens (client_id, token) VALUES ('claude', 'your-token');"
)

# Store API key
mcp__supabase-mcp-full__execute_sql(
    project_id="mxaazuhlqewmkweewyaz",
    query="INSERT INTO secrets (key, value, description) VALUES ('KIMI_API_KEY', 'your-key', 'Kimi API Key');"
)
```

**Method 2: Using Script**
```python
from src.config.secrets_manager import get_secrets_manager

secrets = get_secrets_manager()

# Generate and store JWT token
token = secrets.generate_jwt_token(
    client_id="claude",
    expires_days=365,
    store_in_supabase=True
)

# Store API key
secrets.set_secret(
    key="KIMI_API_KEY",
    value="your-api-key",
    store_in_supabase=True
)
```

### Retrieving from Supabase

```python
from src.config.secrets_manager import get_secrets_manager

secrets = get_secrets_manager()

# Get JWT token
claude_token = secrets.get_jwt_token("claude")
vscode1_token = secrets.get_jwt_token("vscode1")

# Get API key
kimi_key = secrets.get_secret("KIMI_API_KEY")
glm_key = secrets.get_secret("GLM_API_KEY")

# List all secrets (without values)
all_secrets = secrets.list_secrets()
# Returns: {"KIMI_API_KEY": True, "GLM_API_KEY": False, ...}
```

---

## 🧪 Configuration Drift Detection

The system automatically tracks configuration state and detects changes:

```python
from src.config.drift_detector import ConfigDriftDetector

detector = ConfigDriftDetector()
has_drift, details = detector.check_drift()

if has_drift:
    print("⚠️ Configuration drift detected!")
    for detail in details:
        print(f"  - {detail}")
else:
    print("✅ No configuration drift")
```

**What it tracks:**
- Environment variables (EXAI_*)
- Configuration file contents
- Secret values

---

## 🔍 Validation & Testing

### Validate Configuration

```python
from src.config import get_config

config = get_config()

# Check if production-ready
if not config.is_production_ready():
    print("⚠️ Not production-ready")
    print("  Missing:", [
        k for k, v in {
            "KIMI_API_KEY": config.kimi_api_key,
            "GLM_API_KEY": config.glm_api_key,
            "JWT_SECRET_KEY": config.jwt_secret_key
        }.items() if not v
    ])

# Convert to dict (redacted)
safe_dict = config.to_dict()
print(safe_dict)
```

### Test Configuration Loading

```python
# scripts/test_config.py
from src.config import get_config, check_config_drift

def test_config():
    # Load config
    config = get_config()
    print(f"✓ Config loaded: {config.ws_host}:{config.ws_port}")

    # Check drift
    has_drift, details = check_config_drift()
    if has_drift:
        print("⚠️ Drift detected:", details)
    else:
        print("✓ No drift")

    # Validate production readiness
    if config.is_production_ready():
        print("✓ Production ready")
    else:
        print("⚠️ Not production ready")

if __name__ == "__main__":
    test_config()
```

---

## 🚀 Migration Checklist

Use this checklist to migrate all scripts:

- [ ] Import `get_config` from `src.config`
- [ ] Replace all hardcoded ports with `config.ws_port`
- [ ] Replace all hardcoded API keys with `config.kimi_api_key` / `config.glm_api_key`
- [ ] Remove hardcoded JWT tokens (use `secrets_manager`)
- [ ] Add configuration validation
- [ ] Test script with new config
- [ ] Update `.env` file with values
- [ ] Store secrets in Supabase
- [ ] Run drift detection check
- [ ] Update documentation

---

## 🐛 Troubleshooting

### Issue: "Configuration validation failed"

**Cause:** Missing or invalid configuration values

**Solution:**
```python
# Check what's missing
from src.config import get_config
config = get_config()

# Validate specific values
assert config.ws_port != 0, "Port cannot be 0"
assert config.kimi_api_key, "KIMI_API_KEY must be set"
```

### Issue: "No module named 'src.config'"

**Cause:** Python path not set

**Solution:**
```python
# Add to script
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Now import
from src.config import get_config
```

### Issue: "Supabase connection failed"

**Cause:** Supabase credentials not set

**Solution:**
```python
# Check Supabase config
import os
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_KEY:", bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY")))

# Use environment fallback
export SUPABASE_URL="..."
export SUPABASE_SERVICE_ROLE_KEY="..."
```

---

## 📚 Best Practices

### DO ✅
- Use `get_config()` for all configuration
- Store secrets in Supabase
- Validate configuration at startup
- Use type hints
- Check for drift regularly
- Test configuration changes

### DON'T ❌
- Hardcode any values
- Print secrets or tokens
- Use different ports in different files
- Skip validation
- Mix config sources
- Ignore drift warnings

---

## 📖 Related Documentation

- [Architecture Overview](architecture/exai-mcp-architecture.md)
- [Script Issues Guide](SCRIPT_ISSUES_FOUND.md)
- [Auto-Fix Script](scripts/auto_fix_script_issues.py)
- [Troubleshooting Guide](troubleshooting/README.md)

---

## 🎯 Summary

**Before:** Configuration scattered, hardcoded values, security risks

**After:** Centralized config, Supabase secrets, type safety, drift detection

**Result:** No more configuration drift! 🎉

---

**Last Updated:** 2025-11-08
**Version:** 1.0.0
