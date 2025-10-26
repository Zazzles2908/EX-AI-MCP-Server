#!/bin/bash
# Verify environment setup for EX-AI MCP Server
# This script checks that all required environment files are properly configured

set -e

echo "=== EX-AI MCP Server - Environment Verification ==="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env.docker exists
echo "1. Checking .env.docker..."
if [ -f ".env.docker" ]; then
    echo -e "${GREEN}✅ .env.docker exists${NC}"
    
    # Check if it contains actual keys (not placeholders)
    if grep -q "your_kimi_api_key_here" .env.docker || grep -q "your_glm_api_key_here" .env.docker; then
        echo -e "${RED}❌ .env.docker contains placeholders - please add your actual API keys${NC}"
        echo -e "${YELLOW}   Run: cp .env.docker.template .env.docker${NC}"
        echo -e "${YELLOW}   Then edit .env.docker and add your API keys${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ .env.docker contains actual API keys${NC}"
    fi
else
    echo -e "${RED}❌ .env.docker not found${NC}"
    echo -e "${YELLOW}   Run: cp .env.docker.template .env.docker${NC}"
    echo -e "${YELLOW}   Then edit .env.docker and add your API keys${NC}"
    exit 1
fi

# Check if .env.docker.template exists
echo ""
echo "2. Checking .env.docker.template..."
if [ -f ".env.docker.template" ]; then
    echo -e "${GREEN}✅ .env.docker.template exists${NC}"
else
    echo -e "${YELLOW}⚠️  .env.docker.template not found (should be in git)${NC}"
fi

# Check if .env.docker is in .gitignore
echo ""
echo "3. Checking .gitignore..."
if grep -q "^\.env\.docker$" .gitignore; then
    echo -e "${GREEN}✅ .env.docker is in .gitignore${NC}"
else
    echo -e "${RED}❌ .env.docker is NOT in .gitignore${NC}"
    echo -e "${YELLOW}   Add it to prevent committing API keys${NC}"
    exit 1
fi

# Check if .env.docker is tracked in git
echo ""
echo "4. Checking git tracking..."
if git ls-files --error-unmatch .env.docker 2>/dev/null; then
    echo -e "${RED}❌ .env.docker is tracked in git${NC}"
    echo -e "${YELLOW}   Run: git rm --cached .env.docker${NC}"
    exit 1
else
    echo -e "${GREEN}✅ .env.docker is NOT tracked in git${NC}"
fi

# Check Supabase env file
echo ""
echo "5. Checking supabase/.env.supabase..."
if [ -f "supabase/.env.supabase" ]; then
    echo -e "${GREEN}✅ supabase/.env.supabase exists${NC}"
    
    # Check if it's tracked in git
    if git ls-files --error-unmatch supabase/.env.supabase 2>/dev/null; then
        echo -e "${RED}❌ supabase/.env.supabase is tracked in git${NC}"
        echo -e "${YELLOW}   Run: git rm --cached supabase/.env.supabase${NC}"
        exit 1
    else
        echo -e "${GREEN}✅ supabase/.env.supabase is NOT tracked in git${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  supabase/.env.supabase not found (optional)${NC}"
fi

# Check required API keys in .env.docker
echo ""
echo "6. Checking required API keys..."
required_keys=("KIMI_API_KEY" "GLM_API_KEY" "SUPABASE_URL" "SUPABASE_ANON_KEY" "SUPABASE_SERVICE_ROLE_KEY")
missing_keys=()

for key in "${required_keys[@]}"; do
    if grep -q "^${key}=" .env.docker; then
        value=$(grep "^${key}=" .env.docker | cut -d'=' -f2 | cut -d'#' -f1 | xargs)
        if [ -n "$value" ] && [ "$value" != "your_${key,,}_here" ]; then
            echo -e "${GREEN}✅ ${key} is set${NC}"
        else
            echo -e "${RED}❌ ${key} is not set or is placeholder${NC}"
            missing_keys+=("$key")
        fi
    else
        echo -e "${RED}❌ ${key} is missing${NC}"
        missing_keys+=("$key")
    fi
done

if [ ${#missing_keys[@]} -gt 0 ]; then
    echo ""
    echo -e "${RED}Missing or invalid API keys: ${missing_keys[*]}${NC}"
    echo -e "${YELLOW}Please edit .env.docker and add the required API keys${NC}"
    exit 1
fi

# Check Docker
echo ""
echo "7. Checking Docker..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is installed${NC}"
    
    if docker info &> /dev/null; then
        echo -e "${GREEN}✅ Docker is running${NC}"
    else
        echo -e "${RED}❌ Docker is not running${NC}"
        echo -e "${YELLOW}   Start Docker Desktop${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo -e "${YELLOW}   Install Docker Desktop${NC}"
    exit 1
fi

# All checks passed
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ All environment checks passed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "You can now run:"
echo "  docker-compose build"
echo "  docker-compose up -d"
echo ""

