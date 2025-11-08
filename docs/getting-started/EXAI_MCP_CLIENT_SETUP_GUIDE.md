# EXAI MCP Client Setup Guide
**For connecting VSCode instances and Claude Desktop to the EXAI MCP Server**

---

## 🎯 Current Status

✅ **EXAI MCP Server:** Running on port 3000  
✅ **Docker Container:** exai-mcp-daemon (HEALTHY)  
✅ **Tools Loaded:** 21 EXAI tools available  
✅ **MCP Connection:** Working in current VSCode  

---

## 📋 For Other VSCode Instances

### Scenario 1: VSCode in Other Project Folders

If you open VSCode in **different project folders** (e.g., `C:\Projects\MyApp\`), you need to copy the MCP configuration:

#### Steps:

1. **Copy the .mcp.json file** to your project root:
   ```bash
   # From EX-AI-MCP-Server directory
   copy .mcp.json C:\Projects\MyApp\.mcp.json
   ```

2. **Update the paths** in the copied file:
   - Change `C:/Project/EX-AI-MCP-Server/` to your project path
   - Example: `C:/Projects/MyApp/`

3. **Update the ENV_FILE path** (line 10):
   ```json
   "ENV_FILE": "C:/Projects/MyApp/.env"
   ```

4. **Create a .env file** in your project:
   ```bash
   copy C:\Project\EX-AI-MCP-Server\.env C:\Projects\MyApp\.env
   ```

5. **Restart VSCode** in the project folder

### Scenario 2: VSCode with Different Workspaces

If you use **VSCode Workspace files** (`.code-workspace`):

1. The `.mcp.json` should be in the **workspace root folder**
2. Follow the same steps as Scenario 1
3. Ensure all paths in `.mcp.json` point to the workspace root

### Scenario 3: Multiple VSCode Windows

Each VSCode window needs its own configuration:

1. **Copy configuration** to each project/workspace
2. **Update paths** in each copy
3. **Restart each VSCode instance** to reload configuration

---

## 🤖 For Claude Desktop Application

### If you use Claude Desktop (claude.ai desktop app):

#### Option 1: Use the Template Config

1. **Copy the template**:
   ```bash
   copy config/daemon/mcp-config.template.json %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **Edit the copied file**:
   - Update `EXAI_WS_HOST` to `127.0.0.1`
   - Update `EXAI_WS_PORT` to `3000`
   - Update `ENV_FILE` to your EX-AI-MCP-Server path
   - Example: `C:/Project/EX-AI-MCP-Server/.env`

3. **Restart Claude Desktop**

#### Option 2: Update Existing Config

If you already have a Claude desktop config:

1. **Find your config location**:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Update the `exai-mcp` server section**:
   ```json
   {
     "mcpServers": {
       "exai-mcp": {
         "command": "python",
         "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
         "env": {
           "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
           "EXAI_WS_HOST": "127.0.0.1",
           "EXAI_WS_PORT": "3000"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop**

---

## 🔧 For Augment Code / Other MCP Clients

### If you use Augment Code or other MCP-compatible applications:

1. **Find the MCP config location** for your application
2. **Copy one of the config files** from `config/daemon/`:
   - `mcp-config.augmentcode.json` (for Augment Code)
   - `mcp-config.auggie.json` (for Auggie)
   - `mcp-config.claude.json` (for Claude web)

3. **Update paths** in the copied file to match your setup

4. **Update ENV_FILE** to point to `C:/Project/EX-AI-MCP-Server/.env`

5. **Restart the application**

---

## ✅ Verification Steps

After setting up any client:

1. **Check MCP tools load**:
   - In VSCode: Check the MCP tools panel
   - You should see 21 EXAI tools listed

2. **Test a tool call**:
   - Try calling any EXAI tool
   - Should connect to `ws://127.0.0.1:3000`

3. **Check logs** if it doesn't work:
   - VSCode: Check the Output panel → Claude Code
   - Look for connection errors

---

## 🐛 Troubleshooting

### Issue: Still trying to connect to port 8079

**Solution**: Ensure the `.env` file in the project has:
```
EXAI_WS_PORT=3000
```

### Issue: "Failed to fetch tools"

**Solution**: 
1. Verify Docker container is running: `docker ps | grep exai-mcp`
2. Check port 3000 is accessible: `curl -v http://127.0.0.1:3000`
3. Check MCP config paths are correct

### Issue: "Module not found" errors

**Solution**: Update the Python path in `.mcp.json` to match your setup:
```json
"command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe"
```

### Issue: Connection timeout

**Solution**:
1. Check Windows Firewall isn't blocking port 3000
2. Verify Docker port mapping: `docker port exai-mcp-daemon`
3. Ensure no other process is using port 3000

---

## 📝 Summary of Changes Made

The following files were updated to implement the port strategy:

1. **docker-compose.yml** - Port mappings (3000-3003)
2. **.env** - Windows host config (EXAI_WS_PORT=3000)
3. **.env.docker** - Container config (unchanged internal ports)
4. **Dockerfile** - Fixed PYTHONPATH
5. **src/storage/storage_circuit_breaker.py** - Fixed import
6. **9x MCP config files** - Updated ENV_FILE path (.env.docker → .env)

**Critical Fix**: The ENV_FILE path change from `.env.docker` to `.env` was essential for Windows MCP clients to work correctly.

---

## 🎉 You're All Set!

The EXAI MCP server is now operational on port 3000 with all 21 tools available. Each client (VSCode, Claude Desktop, etc.) just needs the proper configuration to connect to `ws://127.0.0.1:3000`.

**Next Steps:**
- Test your setup with any of the 21 EXAI tools
- Try: `@exai-mcp chat "Help me with code review"`
- All tools are ready to use!
