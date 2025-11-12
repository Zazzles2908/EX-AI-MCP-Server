#!/usr/bin/env python3
"""
Docker Configuration Fix for Hybrid Router
Creates missing Docker files that the hybrid router requires.
"""

import os
from pathlib import Path
import yaml

def create_docker_compose():
    """Create docker-compose.yml for hybrid router."""
    
    print("Creating Docker Compose configuration...")
    
    compose_config = {
        "version": "3.8",
        "services": {
            "ex-ai-mcp": {
                "build": ".",
                "container_name": "ex-ai-mcp-server",
                "environment": [
                    # MiniMax M2 Configuration
                    "MINIMAX_ENABLED=true",
                    "MINIMAX_M2_KEY=${MINIMAX_M2_KEY}",
                    "MINIMAX_TIMEOUT=5",
                    "MINIMAX_RETRY=2",
                    
                    # Router Configuration  
                    "FAST_MODEL_DEFAULT=glm-4.5-flash",
                    "LONG_MODEL_DEFAULT=kimi-k2-0711-preview",
                    "ROUTER_DIAGNOSTICS_ENABLED=true",
                    "HYBRID_CACHE_TTL=300",
                    "HYBRID_FALLBACK_ENABLED=true",
                    
                    # Logging
                    "ROUTER_LOG_LEVEL=INFO",
                ],
                "volumes": [
                    "./src:/app/src",
                    "./logs:/app/logs", 
                    "./tools:/app/tools",
                ],
                "ports": [
                    "3000:3000"
                ],
                "healthcheck": {
                    "test": ["CMD", "python", "-c", "from src.router.hybrid_router import get_hybrid_router; print('OK')"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            },
            # Optional Redis for caching
            "redis": {
                "image": "redis:7-alpine",
                "container_name": "ex-ai-redis",
                "ports": ["6379:6379"],
                "volumes": ["redis_data:/data"]
            }
        },
        "volumes": {
            "redis_data": {}
        }
    }
    
    with open("docker-compose.yml", "w") as f:
        yaml.dump(compose_config, f, default_flow_style=False)
    print("  ✅ Created docker-compose.yml")

def create_dockerfile():
    """Create Dockerfile for hybrid router."""
    
    print("Creating Dockerfile...")
    
    dockerfile_content = """# Multi-stage Dockerfile for EX-AI-MCP-Server with Hybrid Router
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for hybrid router
RUN apt-get update && apt-get install -y \\
    redis-tools \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies including required packages
RUN pip install --no-cache-dir \\
    anthropic \\
    redis \\
    fastapi \\
    uvicorn[standard] \\
    pydantic \\
    python-multipart \\
    jinja2 \\
    python-dotenv

# Copy application code
COPY src/ ./src/
COPY tools/ ./tools/
COPY config.py ./
COPY *.json ./

# Create necessary directories
RUN mkdir -p logs

# Set environment variables for hybrid router
ENV MINIMAX_ENABLED=true
ENV ROUTER_CACHE_TTL=300
ENV ROUTER_DIAGNOSTICS_ENABLED=true
ENV HYBRID_FALLBACK_ENABLED=true

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \\
    CMD python -c "from src.router.hybrid_router import get_hybrid_router; print('OK')" || exit 1

# Start command
CMD ["python", "-m", "src.server"]
"""

    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("  ✅ Created Dockerfile")

def create_env_template():
    """Create .env template for Docker environment."""
    
    print("Creating environment template...")
    
    env_content = """# EX-AI-MCP-Server Environment Configuration
# Copy this to .env and fill in your API keys

# MiniMax M2 Configuration
MINIMAX_ENABLED=true
MINIMAX_M2_KEY=your_minimax_api_key_here
MINIMAX_TIMEOUT=5
MINIMAX_RETRY=2

# Router Configuration
FAST_MODEL_DEFAULT=glm-4.5-flash
LONG_MODEL_DEFAULT=kimi-k2-0711-preview
ROUTER_DIAGNOSTICS_ENABLED=true
ROUTER_CACHE_TTL=300
HYBRID_CACHE_TTL=300
HYBRID_FALLBACK_ENABLED=true

# Provider API Keys
GLM_API_KEY=your_glm_api_key_here
KIMI_API_KEY=your_kimi_api_key_here

# Logging
ROUTER_LOG_LEVEL=INFO

# Redis (if using external cache)
REDIS_URL=redis://redis:6379

# Development settings
ENVIRONMENT=development
DEBUG=false
"""

    with open(".env.template", "w") as f:
        f.write(env_content)
    print("  ✅ Created .env.template")

def create_dockerignore():
    """Create .dockerignore file."""
    
    print("Creating .dockerignore...")
    
    dockerignore_content = """# Docker ignore file for EX-AI-MCP-Server

# Version control
.git
.gitignore
.gitattributes

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log

# Environment files
.env
.env.local
.env.development
.env.test
.env.production

# Docker files to exclude
Dockerfile
docker-compose*.yml
.dockerignore

# Documentation
README.md
*.md
docs/

# Test files
tests/
test_*
*test.py

# Build artifacts
build/
dist/
*.egg-info/
"""

    with open(".dockerignore", "w") as f:
        f.write(dockerignore_content)
    print("  ✅ Created .dockerignore")

def create_docker_start_script():
    """Create docker start script."""
    
    print("Creating Docker start script...")
    
    start_script = """#!/bin/bash
# Docker start script for EX-AI-MCP-Server with Hybrid Router

echo "Starting EX-AI-MCP-Server with Hybrid Router..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "💡 Copy .env.template to .env and fill in your API keys"
    exit 1
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$MINIMAX_M2_KEY" ] || [ "$MINIMAX_M2_KEY" == "your_minimax_api_key_here" ]; then
    echo "⚠️  MINIMAX_M2_KEY not set - MiniMax M2 routing will be disabled"
fi

if [ -z "$GLM_API_KEY" ] || [ "$GLM_API_KEY" == "your_glm_api_key_here" ]; then
    echo "⚠️  GLM_API_KEY not set"
fi

if [ -z "$KIMI_API_KEY" ] || [ "$KIMI_API_KEY" == "your_kimi_api_key_here" ]; then
    echo "⚠️  KIMI_API_KEY not set"
fi

echo "🚀 Starting Docker containers..."

# Start with docker-compose
docker-compose up --build -d

echo "✅ Docker containers started!"
echo ""
echo "📊 Monitor logs with:"
echo "   docker-compose logs -f ex-ai-mcp"
echo ""
echo "🔍 Check hybrid router health:"
echo "   docker-compose exec ex-ai-mcp python -c 'from src.router.hybrid_router import get_hybrid_router; print(\\\"OK\\\")'"
echo ""
echo "🛑 Stop containers:"
echo "   docker-compose down"
"""

    with open("docker-start.sh", "w") as f:
        f.write(start_script)
    print("  ✅ Created docker-start.sh")

def create_updated_config_structure():
    """Update config structure since Auggie was removed."""
    
    print("Creating updated configuration structure...")
    
    # Create src/conf directory if it doesn't exist
    src_conf_dir = Path("src/conf")
    src_conf_dir.mkdir(parents=True, exist_ok=True)
    
    # Create updated custom_models.json (without Auggie references)
    custom_models_config = {
        "providers": {
            "glm": {
                "api_key_env": "GLM_API_KEY",
                "models": ["glm-4.5-flash", "glm-4-plus"],
                "capabilities": ["chat", "web_search", "vision"],
                "fast_model": "glm-4.5-flash"
            },
            "kimi": {
                "api_key_env": "KIMI_API_KEY", 
                "models": ["kimi-k2-0711-preview", "kimi-thinking-preview", "kimi-k2-thinking"],
                "capabilities": ["chat", "long_context", "thinking", "file_analysis"],
                "long_model": "kimi-k2-0711-preview"
            }
        },
        "routing": {
            "fast_default": "glm-4.5-flash",
            "long_default": "kimi-k2-0711-preview",
            "cache_ttl": 300,
            "minimax_enabled": True,
            "fallback_enabled": True
        }
    }
    
    with open(src_conf_dir / "models.json", "w") as f:
        import json
        json.dump(custom_models_config, f, indent=2)
    print("  ✅ Created src/conf/models.json")

def main():
    """Main function to create all Docker configuration files."""
    
    print("=" * 70)
    print("DOCKER CONFIGURATION FIX FOR HYBRID ROUTER")
    print("=" * 70)
    
    try:
        create_docker_compose()
        create_dockerfile()
        create_env_template()
        create_dockerignore()
        create_docker_start_script()
        create_updated_config_structure()
        
        print("\n" + "=" * 70)
        print("DOCKER CONFIGURATION SUMMARY")
        print("=" * 70)
        
        print("\n📁 FILES CREATED:")
        print("  ✅ docker-compose.yml - Main Docker compose configuration")
        print("  ✅ Dockerfile - Container build instructions") 
        print("  ✅ .env.template - Environment variables template")
        print("  ✅ .dockerignore - Docker build exclusions")
        print("  ✅ docker-start.sh - Easy start script")
        print("  ✅ src/conf/models.json - Updated configuration (no Auggie)")
        
        print("\n🚀 NEXT STEPS:")
        print("  1. Copy .env.template to .env")
        print("  2. Fill in your API keys in .env")
        print("  3. Run: chmod +x docker-start.sh")
        print("  4. Run: ./docker-start.sh")
        
        print("\n🔍 TO VERIFY HYBRID ROUTER:")
        print("  docker-compose exec ex-ai-mcp python -c '")
        print("  from src.router.hybrid_router import get_hybrid_router")
        print("  router = get_hybrid_router()")
        print("  print(\\\"Hybrid Router OK:\\\")")
        print("  print(f\\\"  - MiniMax enabled: {router.minimax_enabled}\\\")")
        print("  print(f\\\"  - Fallback enabled: {router.fallback_enabled}\\\")")
        print("  print(f\\\"  - Cache TTL: {router.cache_ttl}s\\\")")
        print("  '")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to create Docker configuration: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
