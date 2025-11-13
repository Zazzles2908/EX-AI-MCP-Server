#!/bin/bash
echo "=== EXAI MCP Tool Testing Report ==="
echo "Generated: $(date)"
echo ""

# Test each tool
for tool in "kimi_chat_with_tools" "kimi_intent_analysis" "listmodels" "status" "version"; do
  echo "Testing tool: $tool"
  echo "---"
done
