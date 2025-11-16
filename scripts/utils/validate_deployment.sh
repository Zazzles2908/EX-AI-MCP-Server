#!/bin/bash

# EX-AI MCP Server - Comprehensive Deployment Validation
# ======================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== EX-AI MCP Server Deployment Validation ===${NC}\n"

# 1. Container Status Check
echo -e "${YELLOW}[1/8] Checking container status...${NC}"
CONTAINER_STATUS=$(docker-compose ps --format=json | jq -r '.[] | select(.Name | contains("exai")) | "\(.Name): \(.Status)"')
echo "$CONTAINER_STATUS"

# Count healthy containers
HEALTHY_COUNT=$(docker inspect exai-mcp-server exai-mcp-stdio exai-redis exai-redis-commander 2>/dev/null | jq -r '[.[] | select(.State.Health.Status == "healthy" or .State.Running == true)] | length')
echo -e "${GREEN}✓ $HEALTHY_COUNT/4 containers operational${NC}\n"

# 2. Network Connectivity
echo -e "${YELLOW}[2/8] Testing network connectivity...${NC}"
if docker exec exai-mcp-server ping -c 1 exai-redis > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Internal network connectivity${NC}"
else
    echo -e "${RED}✗ Network connectivity issue${NC}"
fi

# 3. Redis Health
echo -e "\n${YELLOW}[3/8] Checking Redis health...${NC}"
if docker exec exai-redis redis-cli PING | grep -q PONG; then
    echo -e "${GREEN}✓ Redis responding${NC}"
else
    echo -e "${RED}✗ Redis not responding${NC}"
fi

# 4. MCP Server Tool Registry
echo -e "\n${YELLOW}[4/8] Verifying MCP tool registry...${NC}"
TOOL_COUNT=$(docker exec exai-mcp-stdio python -c "
from src.daemon.tool_registry import ToolRegistry
registry = ToolRegistry()
print(len(registry.get_all_tools()))
" 2>/dev/null)

if [ "$TOOL_COUNT" -eq "20" ]; then
    echo -e "${GREEN}✓ All 20 tools registered${NC}"
else
    echo -e "${RED}✗ Tool count mismatch: $TOOL_COUNT${NC}"
fi

# 5. Health Endpoint Check
echo -e "\n${YELLOW}[5/8] Testing health endpoint...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:3002/health || echo "FAILED")
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓ Health endpoint responding${NC}"
else
    echo -e "${RED}✗ Health endpoint not responding${NC}"
fi

# 6. WebSocket Server Status
echo -e "\n${YELLOW}[6/8] Checking WebSocket server...${NC}"
WS_LOGS=$(docker logs exai-mcp-server --tail=10 2>&1)
if echo "$WS_LOGS" | grep -q "Protocol adapter initialized"; then
    echo -e "${GREEN}✓ WebSocket server initialized${NC}"
else
    echo -e "${YELLOW}⚠ WebSocket server may still be starting${NC}"
fi

# 7. STDIO MCP Server
echo -e "\n${YELLOW}[7/8] Verifying native MCP server...${NC}"
STDIO_LOGS=$(docker logs exai-mcp-stdio --tail=5 2>&1)
if echo "$STDIO_LOGS" | grep -q "About to call app.run()"; then
    echo -e "${GREEN}✓ Native MCP server ready${NC}"
else
    echo -e "${YELLOW}⚠ MCP server may still be initializing${NC}"
fi

# 8. Security Check
echo -e "\n${YELLOW}[8/8] Security validation...${NC}"
# Check that secrets are not in environment
if docker exec exai-mcp-server env | grep -q "GLM_API_KEY.*sk-"; then
    echo -e "${RED}✗ WARNING: Secrets exposed in environment${NC}"
else
    echo -e "${GREEN}✓ Secrets not exposed in environment${NC}"
fi

# Network isolation check
if docker inspect exai-redis --format='{{range $p, $conf := .NetworkSettings.Ports}}{{$p}}{{end}}' | grep -q '6379'; then
    echo -e "${YELLOW}⚠ Redis port exposed (intended for development)${NC}"
else
    echo -e "${GREEN}✓ Redis port isolated${NC}"
fi

echo -e "\n${GREEN}=== Validation Complete ===${NC}"
echo -e "For detailed logs, run: docker-compose logs -f"
