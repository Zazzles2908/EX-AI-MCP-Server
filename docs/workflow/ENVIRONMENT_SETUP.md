# Environment Configuration Guide

**Purpose:** Clear guide to environment file management
**Audience:** Developers and Claude Code agents

---

## 📋 Environment Files Overview

### **The 5 Environment Files Explained**

| File | Status | Purpose | Usage |
|------|--------|---------|-------|
| `.env` | ✅ ACTIVE | Local development settings | Python scripts on Windows |
| `.env.docker` | ✅ ACTIVE | Docker container settings | Inside Docker container |
| `.env.example` | 📝 TEMPLATE | Documentation template | Copy to `.env` for new setup |
| `.env.docker.template` | ⚠️ DEPRECATED | Old template (DO NOT USE) | Replaced by `.env.example` |
| `.env.patched` | 🔧 TEMPORARY | Temporary test changes | Delete after use |

---

## 🛠️ Setup for Local Development

### **Step 1: Copy Template**
```bash
# Copy example to create active files
cp .env.example .env
cp .env.example .env.docker
```

### **Step 2: Fill in Values**

**Edit `.env` (for Python scripts):**
```bash
# AI Provider API Keys (REQUIRED)
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
MINIMAX_M2_KEY=your_minimax_m2_key_here

# WebSocket Configuration
EXAI_WS_HOST=127.0.0.1
EXAI_WS_PORT=3010
EXAI_WS_TOKEN=your_websocket_token_here

# Timeouts (adjust as needed)
SIMPLE_TOOL_TIMEOUT_SECS=30
WORKFLOW_TOOL_TIMEOUT_SECS=180
```

**Edit `.env.docker` (for container):**
```bash
# Same keys but for inside container
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here
MINIMAX_M2_KEY=your_minimax_m2_key_here

# Container-specific settings
EXAI_WS_HOST=0.0.0.0
EXAI_WS_PORT=8079
REDIS_PASSWORD=your_redis_password_here
```

### **Step 3: Verify Setup**
```bash
# Test environment loads
python -c "from dotenv import load_dotenv; load_dotenv('.env'); import os; print('GLM_API_KEY:', 'SET' if os.getenv('GLM_API_KEY') else 'MISSING')"

# Test Docker environment
docker-compose exec exai-mcp-daemon python -c "import os; print('GLM_API_KEY:', 'SET' if os.getenv('GLM_API_KEY') else 'MISSING')"
```

---

## 🔒 Security & .gitignore

### **Files in .gitignore (NOT Committed)**
```
.env                 # ACTIVE - Contains real API keys
.env.docker          # ACTIVE - Contains real API keys
.env.patched         # TEMPORARY - Test changes only
.venv/               # Python virtual environment
```

### **Files Committed (Safe to Share)**
```
.env.example         # TEMPLATE - No real keys
.env.docker.template # DEPRECATED TEMPLATE
```

**⚠️ CRITICAL: NEVER commit files containing real API keys**

---

## 📊 Key Configuration Categories

### **1. AI Provider Configuration**
```bash
# GLM (Zhipu AI)
GLM_API_KEY=sk-...              # Your API key
GLM_API_URL=https://api.z.ai/api/paas/v4
GLM_DEFAULT_MODEL=glm-4.5-flash
GLM_TIMEOUT_SECS=120

# KIMI (Moonshot AI)
KIMI_API_KEY=sk-...             # Your API key
KIMI_API_URL=https://api.moonshot.ai/v1
KIMI_DEFAULT_MODEL=kimi-k2-0905-preview
KIMI_TIMEOUT_SECS=180

# MiniMax
MINIMAX_M2_KEY=eyJhbGci...       # JWT token
MINIMAX_API_URL=https://api.minimax.io/anthropic
MINIMAX_TIMEOUT=5
```

### **2. WebSocket Daemon Configuration**
```bash
EXAI_WS_HOST=127.0.0.1          # Local development
EXAI_WS_PORT=3010               # Host port
EXAI_WS_TOKEN=your_token_here   # Authentication

# Docker container uses:
# EXAI_WS_HOST=0.0.0.0
# EXAI_WS_PORT=8079
```

### **3. Timeout Configuration**
```bash
# Coordinated timeout hierarchy
SIMPLE_TOOL_TIMEOUT_SECS=30      # Chat, status, etc.
WORKFLOW_TOOL_TIMEOUT_SECS=180   # Debug, analyze, etc.
EXPERT_ANALYSIS_TIMEOUT_SECS=180 # AI analysis

# Provider-specific
GLM_TIMEOUT_SECS=120
KIMI_TIMEOUT_SECS=180
```

### **4. Redis Configuration**
```bash
REDIS_PASSWORD=secure_password   # Authentication
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

---

## 🔧 Common Modifications

### **Adding New Environment Variables**

1. **Update `.env.example` (DOCUMENTATION)**
   ```bash
   # ============================================================================
   # NEW FEATURE CONFIGURATION
   # ============================================================================
   NEW_FEATURE_ENABLED=true
   NEW_FEATURE_API_KEY=your_new_feature_key_here
   NEW_FEATURE_TIMEOUT=30
   ```

2. **Add to Code**
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv('.env')

   # Get variable with default
   enabled = os.getenv('NEW_FEATURE_ENABLED', 'false').lower() == 'true'
   api_key = os.getenv('NEW_FEATURE_API_KEY')
   timeout = int(os.getenv('NEW_FEATURE_TIMEOUT', '30'))
   ```

3. **Document Usage**
   - Update ENVIRONMENT_SETUP.md
   - Add to relevant README sections
   - Update CHANGELOG.md

### **Modifying Existing Variables**

1. **Check Current Value**
   ```bash
   grep "VARIABLE_NAME" .env
   ```

2. **Update Value**
   ```bash
   # Edit file
   vim .env

   # Or use sed (quick change)
   sed -i 's/OLD_VALUE/NEW_VALUE/' .env
   ```

3. **Verify Change**
   ```bash
   python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print(os.getenv('VARIABLE_NAME'))"
   ```

---

## 🐳 Docker-Specific Notes

### **How Docker Uses Environment Files**

```bash
# docker-compose.yml
env_file:
  - .env.docker    # ← Loads this file into container

# Inside container
# All variables from .env.docker are available as environment variables
```

### **Container vs Host Differences**

| Setting | Host (.env) | Container (.env.docker) |
|---------|-------------|-------------------------|
| EXAI_WS_HOST | 127.0.0.1 | 0.0.0.0 |
| EXAI_WS_PORT | 3010 | 8079 |
| REDIS_HOST | localhost | redis |

**Why Different?**
- Host connects TO container (port mapping)
- Container listens FOR connections (all interfaces)

---

## 🚨 Troubleshooting

### **"Environment variable not found"**
```bash
# Check file exists
ls -la .env

# Check file is loaded
python -c "from dotenv import load_dotenv; load_dotenv('.env'); print('Loaded')"

# Check variable is set
python -c "import os; print(os.getenv('VAR_NAME', 'NOT_FOUND'))"
```

### **"Docker can't read environment"**
```bash
# Check .env.docker exists
ls -la .env.docker

# Check Docker is loading it
docker-compose config | grep env_file

# Restart Docker
docker-compose down
docker-compose up -d
```

### **"API key not working"**
```bash
# Verify key format (no extra spaces)
cat .env | grep API_KEY

# Check key is correct (test with provider)
curl -H "Authorization: Bearer $GLM_API_KEY" https://api.z.ai/api/paas/v4/models
```

---

## 📚 Related Documentation

- **AGENT_WORKFLOW.md** - Agent guidelines and standards
- **ARCHITECTURE.md** - System architecture and integration
- **docs/integration/EXAI_MCP_INTEGRATION_GUIDE.md** - MCP integration details
- **docs/troubleshooting/README.md** - Troubleshooting guide

---

## ✅ Environment File Checklist

### **Before Making Changes**
- [ ] Understand which file to modify (.env vs .env.docker)
- [ ] Backup current values
- [ ] Check .env.example for documentation

### **When Adding Variables**
- [ ] Add to `.env.example` (documentation)
- [ ] Add to `.env` (local testing)
- [ ] Add to `.env.docker` (container)
- [ ] Update ENVIRONMENT_SETUP.md
- [ ] Test in both local and Docker

### **Security**
- [ ] Never commit `.env` or `.env.docker`
- [ ] Use `.env.example` for documentation
- [ ] Rotate API keys regularly
- [ ] Use strong passwords/tokens

---

**Status:** Current and maintained
**Last Updated:** 2025-11-14
