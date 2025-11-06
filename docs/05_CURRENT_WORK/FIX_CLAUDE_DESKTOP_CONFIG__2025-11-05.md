# Fix CLAUDE DESKTOP Config - 2025-11-05

## 🚨 CRITICAL ERRORS TO FIX

### Error 1: JSON Syntax Error
**Problem**: Missing opening quote on key names

```json
// WRONG ❌
{
  "exai-mcp": {
    id": 3,
```

```json
// CORRECT ✅
{
  "exai-mcp": {
    "id": 3,
```

### Error 2: Invalid Fields for MCP Protocol
**Problem**: Adding fields that don't belong in MCP server configuration

```json
// WRONG ❌ - These fields are NOT part of MCP spec
{
  "mcpServers": {
    "exai-mcp": {
      "id": 1,
      "name": "EXAI MCP",
      "description": "...",
      "type": "stdio",
      "trust": true
    }
  }
}
```

### Error 3: Incorrect File Location
**Problem**: Wrong config file location

**WRONG**: `.mcp.json` in project root (for Claude Code IDE)
**CORRECT**: `claude_desktop_config.json` in `%APPDATA%\Claude\` (for Claude Desktop)

## ✅ CORRECTED CONFIGURATION

### File Location
```
C:\Users\Jazeel-Home\AppData\Roaming\Claude\claude_desktop_config.json
```

### Copy This Configuration

```json
{
  "mcpServers": {
    "gh-mcp": {
      "command": "node",
      "args": ["C:/Project/Git_cli/gh-cli/mcp/gh-mcp/dist/server.js"],
      "env": { "GH_HOST": "github.com" }
    },
    "excalidraw-mermaid": {
      "command": "node",
      "args": ["C:/Project/exaclidraw/excalidraw/mcp-server/index.js"],
      "env": { "PORT": "3003" }
    },
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"
      ],
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_JWT_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjbGF1ZGVAZXhhaS1tY3AubG9jYWwiLCJpc3MiOiJleGFpLW1jcC1zZXJ2ZXIiLCJhdWQiOiJleGFpLW1jcC1jbGllbnQiLCJpYXQiOjE3NjIxMjUwNzMsImV4cCI6MTc5MzY2MTA3M30.hVzyioI0JRDgGnbVIq7NYZOsPiiOYjjuRXwAPBVtFn0"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/Project",
        "C:/Users/Jazeel-Home",
        "C:/Project/ADP"
      ]
    }
  }
}
```

## 🔧 STEPS TO FIX

### Step 1: Locate the Config File
```bash
# Navigate to the config directory
cd C:\Users\Jazeel-Home\AppData\Roaming\Claude\
```

### Step 2: Backup Current Config
```bash
# Create a backup
copy claude_desktop_config.json claude_desktop_config.json.backup
```

### Step 3: Replace with Corrected Config
1. Open the corrected config file:
   ```
   C:/Project/EX-AI-MCP-Server/docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json
   ```
2. Copy all contents
3. Paste into `claude_desktop_config.json`
4. Save the file

### Step 4: Restart Claude Desktop
1. Close Claude Desktop completely
2. Wait 5 seconds
3. Reopen Claude Desktop

### Step 5: Verify Connection
1. Open a new chat
2. Look for MCP servers loading in the logs
3. Test with: `@exai-mcp exai_status`

## ✅ WHAT SHOULD BE REMOVED

1. ❌ `"id": 1, 2, 3, 4` - Not part of MCP spec
2. ❌ `"name": "..."` - Not part of MCP spec
3. ❌ `"description": "..."` - Not part of MCP spec
4. ❌ `"type": "stdio"` - Not needed (default)
5. ❌ `"trust": true` - Not part of MCP spec
6. ❌ `"cwd": "..."` - Not needed for most servers

## ✅ WHAT SHOULD REMAIN

1. ✅ `"command"` - The executable to run
2. ✅ `"args"` - Command line arguments
3. ✅ `"env"` - Environment variables
4. ✅ Server names (keys in mcpServers object)

## 📚 Reference Files

- **Corrected Config**: `docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json`
- **This Guide**: `docs/05_CURRENT_WORK/FIX_CLAUDE_DESKTOP_CONFIG__2025-11-05.md`
- **Connection Guide**: `docs/05_CURRENT_WORK/EXAI_MCP_CONNECTION_GUIDE__2025-11-05.md`
- **Quick Start**: `docs/05_CURRENT_WORK/EXAI_QUICK_START__2025-11-05.md`

## 🎯 VALIDATION

After applying the fix, you should see:
- ✅ Claude Desktop starts without JSON errors
- ✅ All 4 MCP servers load successfully
- ✅ EXAI MCP shows 21 tools available
- ✅ No "invalid_union" or "invalid_type" errors

## 🆘 TROUBLESHOOTING

### JSON Still Invalid
```bash
# Validate JSON syntax
python -c "import json; json.load(open('claude_desktop_config.json')); print('Valid')"
```

### EXAI MCP Not Loading
1. Check Docker containers are running:
   ```bash
   docker ps | grep exai
   ```
2. Check logs:
   ```bash
   tail -f C:/Project/EX-AI-MCP-Server/logs/exai-mcp.log
   ```
3. Verify .env file exists:
   ```bash
   ls -la C:/Project/EX-AI-MCP-Server/.env
   ```

### Connection Refused
1. Verify WebSocket is running:
   ```bash
   curl http://127.0.0.1:8079/health
   ```
2. Check firewall settings
3. Verify JWT token is valid

---

**Applied**: 2025-11-05 09:50 UTC
**Status**: ✅ Ready to Apply
**Next Step**: Copy corrected config → Save → Restart Claude Desktop
