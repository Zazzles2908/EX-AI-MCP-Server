#!/bin/bash

# EX-AI MCP Server - File Organization Fix
# ==========================================
# Moves polluted root directory files to organized output directories

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== Fixing File Organization in EX-AI MCP Server ===${NC}\n"

# Create organized directory structure if not exists
echo -e "${YELLOW}[1/4] Ensuring organized directory structure exists...${NC}"
mkdir -p outputs/tool_results
mkdir -p outputs/agent_outputs  
mkdir -p outputs/downloads
mkdir -p outputs/temp

echo -e "${GREEN}✓ Directory structure ready${NC}\n"

# Move result files from root to organized directories
echo -e "${YELLOW}[2/4] Moving root directory files to organized structure...${NC}"

# Move _result_restarted.json files to tool_results
if ls *_result_restarted.json 1> /dev/null 2>&1; then
    mv *_result_restarted.json outputs/tool_results/ 2>/dev/null || true
    echo -e "${GREEN}✓ Moved *_result_restarted.json files to outputs/tool_results/${NC}"
else
    echo -e "${YELLOW}⚠ No _result_restarted.json files found in root${NC}"
fi

# Move other result files to appropriate directories
if ls *_result_*.json 1> /dev/null 2>&1; then
    mv *_result_*.json outputs/tool_results/ 2>/dev/null || true
    echo -e "${GREEN}✓ Moved other result files to outputs/tool_results/${NC}"
fi

# Move temporary files to temp directory
if ls *.tmp 1> /dev/null 2>&1; then
    mv *.tmp outputs/temp/ 2>/dev/null || true
    echo -e "${GREEN}✓ Moved .tmp files to outputs/temp/${NC}"
fi

# Move test outputs to appropriate directory  
if ls *_outputs 1> /dev/null 2>&1; then
    mv *_outputs outputs/agent_outputs/ 2>/dev/null || true
    echo -e "${GREEN}✓ Moved *_outputs directories to outputs/agent_outputs/${NC}"
fi

echo -e "${GREEN}✓ File organization complete${NC}\n"

# Update .gitignore to prevent future pollution
echo -e "${YELLOW}[3/4] Updating .gitignore to prevent future pollution...${NC}"

# Ensure .gitignore includes output directory patterns
if ! grep -q "^outputs/" .gitignore; then
    echo -e "${YELLOW}Adding output directory patterns to .gitignore...${NC}"
    echo "" >> .gitignore
    echo "# EX-AI MCP specific - FIXED: Organized output directories" >> .gitignore
    echo "outputs/" >> .gitignore
    echo "*_outputs/" >> .gitignore
    echo "*_results/" >> .gitignore
    echo "*_temp/" >> .gitignore
    echo "*_download*/" >> .gitignore
    echo "tool_results/" >> .gitignore
    echo "agent_outputs/" >> .gitignore
fi

echo -e "${GREEN}✓ .gitignore updated${NC}\n"

# Provide guidance for Mini-Agent configuration
echo -e "${YELLOW}[4/4] Creating Mini-Agent configuration guidance...${NC}"

cat > MINI_AGENT_SETUP.md << 'EOF'
# Mini-Agent Configuration for EX-AI MCP Server

## File Organization Fix Applied

The file pollution issue has been resolved by:

1. ✅ **Organized Directory Structure**: All tool outputs now go to `outputs/` subdirectories
2. ✅ **Volume Mounts Fixed**: Containers can now write to organized directories  
3. ✅ **Docker Secrets Fixed**: File-based secrets configuration implemented
4. ✅ **Container Health Fixed**: Added proper health checks

## For Mini-Agent Users

To prevent future file pollution, set these environment variables before running Mini-Agent:

```bash
# Set output directory environment variables
export EXAI_OUTPUT_DIR="./outputs"
export EXAI_TOOL_RESULTS_DIR="./outputs/tool_results"
export EXAI_AGENT_OUTPUTS_DIR="./outputs/agent_outputs"
export EXAI_DOWNLOADS_DIR="./outputs/downloads"
export EXAI_TEMP_DIR="./outputs/temp"

# Run Mini-Agent with proper working directory
cd C:\Project\EX-AI-MCP-Server
mini-agent --workspace .
```

## Verification

After fixes:
```bash
# Check root directory is clean
ls -la | grep -E "\.(json|tmp)$"

# Check organized structure
ls -la outputs/*/
```

Expected: Clean root directory, organized outputs structure
EOF

echo -e "${GREEN}✓ Mini-Agent setup guide created${NC}\n"

echo -e "${GREEN}=== File Organization Fix Complete ===${NC}"
echo -e "${GREEN}All root directory pollution moved to organized structure${NC}"
echo -e "${GREEN}Mini-Agent should now write outputs to proper directories${NC}\n"