# Simple EXAI MCP Connection - Like GitHub MCP

## ✅ Simple Configuration

Just like your GitHub MCP setup, the EXAI MCP Server is now **simple and direct**:

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "python",
      "args": [
        "c:/Users/Jazeel-Home/.claude/exai_mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

## What's Included

**EXAI Tools Available:**
- `exai_chat` - Chat with GLM-4.5-Flash or Kimi models
- `exai_search` - Web search using EXAI
- `exai_analyze` - Analyze code or documents
- `exai_status` - Get server status and information
- `exai_tools` - List all available tools

## How to Use

### 1. Place Configuration File
Put `.mcp.json` in your project root

### 2. Open Claude Web Application
Navigate to: https://claude.ai

### 3. Open Your Project Folder
The web app will automatically detect and load the EXAI MCP server.

### 4. Use EXAI Tools
Available tools:
```bash
@exai-mcp exai_status
@exai-mcp exai_chat "Hello from Claude!"
@exai-mcp exai_search "Python async programming"
@exai-mcp exai_analyze "print('Hello World')"
```

## Why This Works

**Simple and Direct**: Just like your GitHub MCP setup
- ✅ No WebSocket complexity
- ✅ No Windows stdio issues
- ✅ Direct MCP server
- ✅ Works reliably

## Architecture

```
Claude Web App (claude.ai)
         ↓
    .mcp.json
         ↓
exai_mcp_server.py (simple, direct)
         ↓
EXAI MCP Tools
```

**No WebSocket shims. No complex environments. Just like gh-mcp.** 🎯

## Verification

### Test the MCP Server Locally

To verify the EXAI MCP server is working correctly:

```bash
# Test tools/list request
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | python c:/Users/Jazeel-Home/.claude/exai_mcp_server.py
```

You should see a JSON response with 5 EXAI tools, each with proper:
- ✅ `id` field (number)
- ✅ `name` field (string)
- ✅ `description` field (string)
- ✅ `inputSchema` with parameters

### Test with Claude Web Application

1. Open Claude web application: https://claude.ai
2. Open your project folder containing `.mcp.json`
3. You should see EXAI MCP server loaded automatically
4. Test a tool: `@exai-mcp exai_status`

## Files Created

- `c:/Users/Jazeel-Home/.claude/exai_mcp_server.py` - Simple EXAI MCP server
- `C:/Project/EX-AI-MCP-Server/.mcp.json` - Configuration (updated)
