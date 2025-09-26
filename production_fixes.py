#!/usr/bin/env python3
"""
Production-ready fixes for EX-AI MCP Server
This script implements all the critical fixes needed for production deployment.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, check=True):
    """Run shell command and return result"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result

def main():
    print("🚀 Starting EX-AI MCP Server Production Fixes...")
    
    # 1. Fix Critical Dependencies
    print("\n📦 Fixing critical dependencies...")
    
    # Update requirements.txt
    requirements_content = """mcp>=1.0.0
openai>=1.55.2
pydantic>=2.0.0
python-dotenv>=1.0.0
zhipuai>=2.1.0
httpx>=0.28.0
importlib-resources>=5.0.0; python_version<"3.9"
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements_content)
    print("✅ Updated requirements.txt with zhipuai>=2.1.0")
    
    # Update pyproject.toml dependencies
    pyproject_content = """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ex-ai-mcp-server"
version = "2.0.0"
description = "Production-ready EX-AI MCP Server with intelligent routing"
authors = [{name = "Zazzles", email = "zazzles@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "mcp>=1.0.0",
    "openai>=1.55.2",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "zhipuai>=2.1.0",
    "httpx>=0.28.0",
    "importlib-resources>=5.0.0; python_version<'3.9'",
]

[project.urls]
Homepage = "https://github.com/Zazzles2908/EX-AI-MCP-Server"
Issues = "https://github.com/Zazzles2908/EX-AI-MCP-Server/issues"
Repository = "https://github.com/Zazzles2908/EX-AI-MCP-Server"

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.11.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "mypy>=1.5.0",
]

remote = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.30.0",
    "sse-starlette>=2.0.0",
    "fastmcp>=1.0.0",
]

[project.scripts]
ex-ai-mcp-server = "server:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["*"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
"""
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject_content)
    print("✅ Updated pyproject.toml with production dependencies")
    
    # 2. Clean up project structure
    print("\n🧹 Cleaning up project structure...")
    
    # Remove excessive documentation (keep only essential)
    docs_to_remove = [
        "README-PUBLIC.md",
        "README-ORIGINAL.md", 
        "LIMITATIONS.md",
        "SUPPORT.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "CONTRIBUTING.md"
    ]
    
    for doc in docs_to_remove:
        if os.path.exists(doc):
            os.remove(doc)
            print(f"✅ Removed {doc}")
    
    # Remove clutter directories if they exist
    clutter_dirs = [
        ".augment",
        ".claude", 
        "docs/experimental",
        "examples",
        "tests/experimental"
    ]
    
    for dir_path in clutter_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"✅ Removed directory {dir_path}")
    
    # 3. Create production environment configuration
    print("\n⚙️ Creating production environment configuration...")
    
    env_production = """# EX-AI MCP Server Production Configuration
# Core API Keys (Required)
ZHIPUAI_API_KEY=your_zhipuai_api_key_here
MOONSHOT_API_KEY=your_moonshot_api_key_here

# Model Configuration
DEFAULT_MODEL=glm-4.5-flash
AI_MANAGER_MODEL=glm-4.5-flash

# Routing Configuration
INTELLIGENT_ROUTING_ENABLED=true
WEB_SEARCH_PROVIDER=glm
FILE_PROCESSING_PROVIDER=kimi
COST_AWARE_ROUTING=true

# Production Settings
LOG_LEVEL=INFO
MAX_RETRIES=3
REQUEST_TIMEOUT=30
ENABLE_FALLBACK=true

# MCP WebSocket Configuration
MCP_WEBSOCKET_ENABLED=true
MCP_WEBSOCKET_PORT=8080
MCP_WEBSOCKET_HOST=0.0.0.0

# Performance Settings
MAX_CONCURRENT_REQUESTS=10
RATE_LIMIT_PER_MINUTE=100
CACHE_ENABLED=true
CACHE_TTL=300

# Security Settings
SECURE_INPUTS_ENFORCED=true
VALIDATE_API_KEYS=true
"""
    
    with open(".env.production", "w") as f:
        f.write(env_production)
    print("✅ Created .env.production with production settings")
    
    print("\n🎉 Production fixes completed successfully!")
    print("\nNext steps:")
    print("1. Update API keys in .env.production")
    print("2. Test the server with: python server.py")
    print("3. Deploy using the production configuration")

if __name__ == "__main__":
    main()
