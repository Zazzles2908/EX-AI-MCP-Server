#!/bin/bash

# GitHub MCP Server Setup Test Script
# This script helps verify your GitHub MCP Server setup with Claude Desktop

echo "🔧 GitHub MCP Server Setup Test"
echo "================================"
echo ""

# Check if Docker is installed and running
echo "1. Checking Docker installation..."
if command -v docker &> /dev/null; then
    if docker info &> /dev/null; then
        echo "✅ Docker is installed and running"
    else
        echo "❌ Docker is installed but not running"
        echo "   Please start Docker Desktop and try again"
        exit 1
    fi
else
    echo "❌ Docker is not installed"
    echo "   Please install Docker Desktop from https://www.docker.com/"
    exit 1
fi

# Test pulling the GitHub MCP Server image
echo ""
echo "2. Testing GitHub MCP Server Docker image..."
if docker pull ghcr.io/github/github-mcp-server; then
    echo "✅ Successfully pulled GitHub MCP Server image"
else
    echo "❌ Failed to pull GitHub MCP Server image"
    echo "   This may be a network or authentication issue"
    echo "   Try: docker logout ghcr.io && docker pull ghcr.io/github/github-mcp-server"
fi

# Check configuration file location based on OS
echo ""
echo "3. Checking configuration file location..."

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_PATH="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_PATH="$HOME/.config/Claude/claude_desktop_config.json"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    CONFIG_PATH="$APPDATA/Claude/claude_desktop_config.json"
else
    echo "⚠️  Unknown OS. Please check config path manually."
    CONFIG_PATH=""
fi

if [ -n "$CONFIG_PATH" ]; then
    if [ -f "$CONFIG_PATH" ]; then
        echo "✅ Configuration file found at: $CONFIG_PATH"
        
        # Check if GitHub MCP server is configured
        if grep -q "github-mcp-server" "$CONFIG_PATH"; then
            echo "✅ GitHub MCP Server configuration found"
        else
            echo "❌ GitHub MCP Server configuration not found"
            echo "   Please add the configuration to your config file"
        fi
    else
        echo "❌ Configuration file not found at: $CONFIG_PATH"
        echo "   You may need to create it or Claude Desktop hasn't been started yet"
    fi
fi

echo ""
echo "4. Configuration Tips:"
echo "   - Make sure your PAT has 'repo', 'read:org', and 'read:packages' scopes"
echo "   - Store your PAT securely and never commit it to version control"
echo "   - After updating the config file, restart Claude Desktop"
echo "   - Check Claude logs if you encounter issues:"
echo "     macOS: ~/Library/Logs/Claude/"
echo "     Windows: %APPDATA%\\Claude\\logs\\"

echo ""
echo "5. Quick Test Commands:"
echo ""
echo "   Test your PAT manually:"
echo "   curl -H \"Authorization: token YOUR_PAT\" https://api.github.com/user"
echo ""
echo "   Test Docker image manually:"
echo "   docker run --rm -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_PAT ghcr.io/github/github-mcp-server --help"

echo ""
echo "🎉 Setup test complete!"
echo "   If all checks passed, you're ready to use GitHub MCP Server with Claude Desktop"
echo ""
echo "📚 For detailed setup instructions, see: github_mcp_server_setup_guide.md"