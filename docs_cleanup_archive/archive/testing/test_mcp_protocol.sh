#!/bin/bash
# MCP Protocol Compliance Test

echo "Testing MCP Server Protocol Compliance..."
echo "========================================="

# Create test input
TEST_INPUT='{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}, "id": 1}'

# Test the MCP server
echo "Sending MCP initialize request..."
echo "$TEST_INPUT" | docker exec -i exai-mcp-stdio python -m src.daemon.mcp_server --mode stdio > /tmp/mcp_stdout.txt 2> /tmp/mcp_stderr.txt

echo "MCP Server stdout output:"
if [ -f /tmp/mcp_stdout.txt ]; then
    cat /tmp/mcp_stdout.txt
else
    echo "No stdout output captured"
fi

echo ""
echo "MCP Server stderr output:"
if [ -f /tmp/mcp_stderr.txt ]; then
    head -20 /tmp/mcp_stderr.txt
else
    echo "No stderr output captured"
fi

# Check if stdout contains only JSON
if [ -f /tmp/mcp_stdout.txt ]; then
    echo ""
    echo "Checking JSON validity..."
    if grep -q '^{' /tmp/mcp_stdout.txt && grep -q '}$' /tmp/mcp_stdout.txt; then
        echo "✅ STDOUT appears to contain JSON"
    else
        echo "❌ STDOUT contains non-JSON output"
        echo "Raw stdout content:"
        cat /tmp/mcp_stdout.txt
    fi
fi

echo ""
echo "Test completed."