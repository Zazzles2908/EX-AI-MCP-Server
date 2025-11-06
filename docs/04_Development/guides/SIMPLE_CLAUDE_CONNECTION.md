# Claude Web Application Connection to EXAI MCP

## ✅ Working Configuration

The following `.mcp.json` configuration is **tested and working** with the Claude web application:

```json
{
  "mcpServers": {
    "claude-enhancements": {
      "command": "python",
      "args": [
        "c:/Users/Jazeel-Home/.claude/claude_web_app_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "c:/Users/Jazeel-Home/.claude"
      }
    }
  }
}
```

## What's Included

**MiniMax Monitoring & Statistics:**
- Track API usage and costs
- Monitor token consumption
- Real-time performance metrics

**Semantic Caching:**
- Faster response times
- Intelligent cache management
- Token savings tracking

**Batch Processing:**
- Queue multiple requests
- Parallel processing capabilities
- Efficiency optimization

## How to Use

### 1. Place Configuration File
Put `.mcp.json` in your project root:
```
C:/Project/EX-AI-MCP-Server/.mcp.json
```

### 2. Open Claude Web Application
Navigate to: https://claude.ai

### 3. Open Your Project Folder
The web app will automatically detect and load the MCP enhancements.

### 4. Use Enhancements
The enhancements will be available in your conversation interface.

## Why This Works

**Problem Solved:** The original configuration used a WebSocket shim that crashes on Windows due to stdio instability.

**Solution:** This configuration uses a **direct, minimal MCP server** that:
- ✅ Has zero dependencies
- ✅ Supports the web app's "enhancements" format
- ✅ Works reliably on Windows
- ✅ Provides MiniMax integration without complexity

## Troubleshooting

### Enhancements Not Loading?
1. Verify `.mcp.json` is in the project root
2. Check the file path to `claude_web_app_mcp.py` is correct
3. Restart the Claude web application
4. Check browser console for errors

### Still Having Issues?
Run the connection test:
```bash
cd /c/Project/EX-AI-MCP-Server
python test_claude_connection.py
```

This will verify:
- Port 8079 is listening (EXAI server status)
- Python configuration is correct
- .mcp.json is properly formatted

## Architecture

```
Claude Web App (claude.ai)
         ↓
    .mcp.json (project config)
         ↓
claude_web_app_mcp.py (minimal server)
         ↓
MiniMax v2 Integration
```

**No WebSocket complexity. No Windows stdio issues. Just works.** 🎯
