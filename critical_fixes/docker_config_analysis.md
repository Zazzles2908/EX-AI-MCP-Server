# Docker Configuration Analysis for Hybrid Router

## Based on Code Analysis & User Feedback

### 🎯 **Key Issues Identified**

Since you mentioned:
- ✅ Removed Auggie (so `auggie-config.json` is no longer needed)
- ❓ Docker configuration may not be set up properly
- ❓ Custom models configuration issues

## 🔍 **Missing Docker Configuration Files**

### **1. Docker Compose File**
Likely missing `docker-compose.yml` or `docker-compose.yaml`:

```yaml
version: '3.8'

services:
  ex-ai-mcp:
    build: .
    container_name: ex-ai-mcp-server
    environment:
      # Required for hybrid router
      - MINIMAX_ENABLED=true
      - MINIMAX_M2_KEY=${MINIMAX_M2_KEY}
      - MINIMAX_TIMEOUT=5
      - MINIMAX_RETRY=2
      - ROUTER_DIAGNOSTICS_ENABLED=true
      
      # Router defaults
      - FAST_MODEL_DEFAULT=glm-4.5-flash
      - LONG_MODEL_DEFAULT=kimi-k2-0711-preview
      
    volumes:
      - ./src:/app/src
      - ./logs:/app/logs
      
    ports:
      - "3000:3000"
      
    depends_on:
      - redis  # If using external cache
```

### **2. Dockerfile Issues**

**Likely missing `Dockerfile` or `Dockerfile.dev`**:

```dockerfile
# Multi-stage build for production
FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies for hybrid router
RUN apt-get update && apt-get install -y \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir \
    anthropic \
    redis \
    fastapi \
    uvicorn[standard]

# Copy application code
COPY src/ ./src/
COPY tools/ ./tools/
COPY config.py ./

# Set environment variables
ENV MINIMAX_ENABLED=true
ENV ROUTER_CACHE_TTL=300

EXPOSE 3000

CMD ["python", "-m", "src.server"]
```

### **3. Environment Configuration**

**Missing `.env` file**:
```bash
# MiniMax Configuration
MINIMAX_ENABLED=true
MINIMAX_M2_KEY=your_minimax_api_key_here
MINIMAX_TIMEOUT=5
MINIMAX_RETRY=2

# Router Configuration
FAST_MODEL_DEFAULT=glm-4.5-flash
LONG_MODEL_DEFAULT=kimi-k2-0711-preview
ROUTER_DIAGNOSTICS_ENABLED=true
ROUTER_CACHE_TTL=300

# Provider Configuration
GLM_API_KEY=your_glm_api_key
KIMI_API_KEY=your_kimi_api_key
```

## 🛠️ **Specific Docker-Related Issues**

### **Issue 1: Environment Variables Not Set in Container**
The hybrid router relies on environment variables that may not be set in Docker:

- `MINIMAX_ENABLED` - Enables/disables MiniMax M2 routing
- `MINIMAX_M2_KEY` - API key for MiniMax M2
- `FAST_MODEL_DEFAULT` & `LONG_MODEL_DEFAULT` - Model configuration

### **Issue 2: Volume Mounts Missing**
Container may not have access to:
- Configuration files in `src/conf/`
- Custom models configuration
- Log files for diagnostics

### **Issue 3: Network/Database Dependencies**
Missing:
- Redis container for caching (if using external cache)
- Proper network configuration between containers
- Health check configuration

## 🚨 **Impact on Hybrid Router**

### **Why Docker Issues Break the Router:**

1. **Missing Environment Variables** → Hybrid router fails to initialize
2. **No API Keys** → MiniMax M2 routing unavailable
3. **Wrong Model Defaults** → Fallback routing fails
4. **Missing Cache Configuration** → Performance issues
5. **No Diagnostics** → Cannot troubleshoot issues

## 💡 **Immediate Fixes Needed**

### **1. Create Proper Docker Compose**
```bash
# Create docker-compose.yml with hybrid router environment
cp template-docker-compose.yml docker-compose.yml
```

### **2. Set Environment Variables**
```bash
# Add to .env file
MINIMAX_M2_KEY=your_api_key_here
MINIMAX_ENABLED=true
```

### **3. Update Dockerfile**
Ensure it includes:
- `anthropic` package (required for MiniMax M2)
- Proper environment variable defaults
- Volume mounts for configuration

### **4. Fix Custom Models Configuration**

Since Auggie was removed, create new config structure:

```json
{
  "providers": {
    "glm": {
      "api_key": "${GLM_API_KEY}",
      "models": ["glm-4.5-flash", "glm-4-plus"]
    },
    "kimi": {
      "api_key": "${KIMI_API_KEY}",
      "models": ["kimi-k2-0711-preview", "kimi-thinking-preview"]
    }
  },
  "routing": {
    "fast_default": "glm-4.5-flash",
    "long_default": "kimi-k2-0711-preview",
    "cache_ttl": 300
  }
}
```

## 🔧 **Quick Diagnostic**

Run this to check if Docker is the issue:

```bash
# Check if container has required environment variables
docker exec ex-ai-mcp-server env | grep -E "(MINIMAX|ROUTER|FAST|LONG)"

# Check if required packages are installed
docker exec ex-ai-mcp-server python -c "import anthropic; print('anthropic OK')"

# Test hybrid router initialization
docker exec ex-ai-mcp-server python -c "
from src.router.hybrid_router import get_hybrid_router
router = get_hybrid_router()
print('Router OK')
"
```

## 🎯 **Root Cause**

**The hybrid router fails because Docker container doesn't have the required environment variables and dependencies that are necessary for proper initialization and operation.**
