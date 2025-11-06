# EXAI MCP Quick Start - 2025-11-05

## 🚀 FASTEST WAY TO GET CONNECTED

### Prerequisites (2 minutes)

```bash
# Check Docker containers
docker ps | grep exai

# If not running, start them
cd C:/Project/EX-AI-MCP-Server
docker-compose up -d
```

### Claude Desktop (5 minutes)

1. **Open config file:**
   ```
   C:\Users\Jazeel-Home\AppData\Roaming\Claude\claude_desktop_config.json
   ```

2. **Replace contents** with config from:
   ```
   docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json
   ```

3. **Save file** and **restart Claude Desktop**

4. **Test connection:**
   ```
   @exai-mcp exai_status
   ```

### Claude Code/Augment Code (3 minutes)

1. **Create .mcp.json** in your project root:
   ```bash
   cat > .mcp.json << 'EOF'
   {
     "mcpServers": {
       "exai-mcp": {
         "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
         "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
         "env": {
           "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
           "EXAI_WS_HOST": "127.0.0.1",
           "EXAI_WS_PORT": "8079"
         }
       }
     }
   }
   EOF
   ```

2. **Reload VS Code window:**
   ```
   Ctrl+Shift+P → "Developer: Reload Window"
   ```

3. **Test:**
   ```
   @exai-mcp exai_tools
   ```

## ✅ SUCCESS!

You now have access to 21 EXAI tools:
- `exai_chat` - Chat with GLM-4.5-Flash or Kimi
- `exai_search` - Intelligent web search
- `exai_analyze` - Analyze code or documents
- `exai_status` - Check system status
- `exai_tools` - List all available tools
- +16 more tools

## 🆘 Common Issues

### "MCP server failed to load"
- ✅ Verify Docker containers: `docker ps | grep exai`
- ✅ Check JWT token in .env file

### "WebSocket connection refused"
- ✅ Port 8079 accessible: `netstat -an | grep 8079`
- ✅ Restart containers: `docker-compose restart`

### "Tools not appearing"
- ✅ Restart Claude Desktop or VS Code
- ✅ Check config file has correct format (no id/name/description fields)

## 📚 Full Documentation

- **Complete Fix Guide**: `docs/05_CURRENT_WORK/FIX_CLAUDE_DESKTOP_CONFIG__2025-11-05.md`
- **Connection Guide**: `docs/05_CURRENT_WORK/EXAI_MCP_CONNECTION_GUIDE__2025-11-05.md`
- **Corrected Config**: `docs/05_CURRENT_WORK/CORRECTED_CLAUDE_DESKTOP_CONFIG__2025-11-05.json`

## 🎯 Testing Commands

```bash
# Test MCP server directly
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
  python C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py

# Check API health
curl http://127.0.0.1:8000/api/health

# View logs
tail -f C:/Project/EX-AI-MCP-Server/logs/exai-mcp.log
```

---

**Total Time**: 5-10 minutes
**Status**: ✅ Ready to Deploy
**Last Updated**: 2025-11-05 09:50 UTC
