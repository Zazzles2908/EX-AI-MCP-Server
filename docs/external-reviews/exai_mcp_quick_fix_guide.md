# EX-AI MCP Server - Quick Fix Guide

**Date**: November 13, 2025  
**Target**: Windows + VS Code + Claude Code + Minimax

---

## 🔴 Problem Summary

**Your MCP server doesn't work because**:
1. ❌ Docker networking prevents Windows shim from connecting to container
2. ❌ Custom WebSocket protocol requires translation layer (shim)
3. ❌ Minimax LLM may not support MCP discovery properly
4. ✅ Direct bash/python works because it bypasses MCP protocol entirely

---

## 🎯 Quick Diagnosis (5 minutes)

### Step 1: Check Docker Container
```bash
# Is container running?
docker ps | grep exai-mcp-daemon

# Check logs
docker logs exai-mcp-daemon --tail 50

# Expected: "WebSocket daemon started on 0.0.0.0:8079"
```

**Result**: 
- ✅ If running and showing logs → Container is OK
- ❌ If not running → Run `docker-compose up -d`

### Step 2: Test WebSocket Connection
Create `test_ws.py`:
```python
import asyncio
import websockets
import json

async def test():
    try:
        print("Connecting to ws://127.0.0.1:3010...")
        ws = await asyncio.wait_for(
            websockets.connect("ws://127.0.0.1:3010"),
            timeout=10
        )
        print("✅ Connected!")
        
        # Send hello
        await ws.send(json.dumps({
            "op": "hello",
            "protocolVersion": "2024-11-05",
            "token": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
        }))
        
        # Wait for response
        response = await asyncio.wait_for(ws.recv(), timeout=5)
        print(f"✅ Response: {response}")
        
        await ws.close()
        return True
    except asyncio.TimeoutError:
        print("❌ TIMEOUT: Docker container not responding")
        return False
    except ConnectionRefusedError:
        print("❌ CONNECTION REFUSED: Port 3010 not listening")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test())
    print("\n" + "="*50)
    if success:
        print("DIAGNOSIS: Network is OK, problem is in MCP layer")
    else:
        print("DIAGNOSIS: Network connection failed, this is the root cause")
```

Run it:
```bash
python test_ws.py
```

**Result**:
- ✅ If successful → Network is OK, problem is MCP/shim layer
- ❌ If failed → **This is your main problem** (Docker networking)

### Step 3: Test Shim Manually
```bash
# Set environment variables
set EXAI_WS_HOST=127.0.0.1
set EXAI_WS_PORT=3010
set EXAI_WS_TOKEN=pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo
set LOG_LEVEL=DEBUG

# Run shim
python C:\Project\EX-AI-MCP-Server\scripts\runtime\run_ws_shim.py
```

**Watch for**:
```
✅ Good: [DAEMON_CONNECT] ✓ Connected to daemon
❌ Bad:  [DAEMON_CONNECT] ✗ Failed to connect
```

### Step 4: Check Other MCP Servers
In Claude Code, try:
```
@filesystem-mcp list_allowed_directories
@git-mcp git_status
```

**Result**:
- ✅ If working → Minimax supports MCP, problem is EX-AI specific
- ❌ If not working → Minimax MCP support issue

---

## 🛠️ Solution Options

### Option 1: Quick Fix - Run Daemon on Windows (30 minutes)

**This removes Docker networking from the equation**

#### Step 1: Stop Docker Container
```bash
docker-compose down
```

#### Step 2: Install Dependencies on Windows
```bash
cd C:\Project\EX-AI-MCP-Server

# Create virtual environment (if not exists)
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Run Daemon Directly on Windows
```bash
# Set environment variables
copy .env.example .env
# Edit .env file with your settings

# Run daemon
python scripts\ws\run_ws_daemon.py
```

**Expected Output**:
```
[INFO] WebSocket daemon started on 0.0.0.0:8079
[INFO] Waiting for connections...
```

#### Step 4: Update MCP Configuration
Edit your Claude Code config (`C:\Users\<YourUser>\.config\claude-code\settings.json` or similar):

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"
      ],
      "env": {
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",  // Changed from 3010 to 8079
        "EXAI_WS_TOKEN": "pYf69sHNkOYlYLRTJfMrxCQghO5OJOUFbUxqaxp9Zxo"
      }
    }
  }
}
```

#### Step 5: Test
1. Restart Claude Code
2. Try: `@exai-mcp chat "test"`
3. Should now work! ✅

**Pros**:
- ✅ Fast solution
- ✅ Eliminates Docker networking issues
- ✅ Easy to debug

**Cons**:
- ❌ No Docker isolation
- ❌ Need to run daemon manually
- ❌ Need Redis on Windows (or remove Redis dependency)

---

### Option 2: Best Fix - Native stdio MCP Server (2-4 hours)

**This is the proper long-term solution**

#### Step 1: Create Native stdio Server

Create `C:\Project\EX-AI-MCP-Server\scripts\mcp\stdio_native.py`:

```python
#!/usr/bin/env python
"""Native stdio MCP server for EX-AI tools."""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
_repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_repo_root))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from src.bootstrap import load_env

# Load environment
load_env()

# Initialize MCP server
app = Server("exai-mcp-native")

# Import your tools
# TODO: Import actual tool implementations
# Example:
# from tools.chat import chat_tool
# from tools.debug import debug_tool
# etc.

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of available tools."""
    # TODO: Replace with actual tool definitions
    return [
        Tool(
            name="chat",
            description="Chat with AI assistant",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Message to send"
                    }
                },
                "required": ["message"]
            }
        ),
        # Add more tools here
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool and return results."""
    try:
        # TODO: Route to actual tool implementations
        if name == "chat":
            # Example: call your actual chat implementation
            # result = await chat_tool(arguments["message"])
            result = f"Chat response: {arguments.get('message', '')}"
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(
                type="text",
                text=f"Tool '{name}' not implemented yet"
            )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing tool {name}: {str(e)}"
        )]

async def main():
    """Run the stdio MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        stream=sys.stderr  # IMPORTANT: Logs go to stderr, not stdout
    )
    
    logging.info("Starting EX-AI native stdio MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### Step 2: Update MCP Configuration

Edit your Claude Code config:

```json
{
  "mcpServers": {
    "exai-mcp": {
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": [
        "-u",
        "C:/Project/EX-AI-MCP-Server/scripts/mcp/stdio_native.py"
      ],
      "env": {}  // No WebSocket config needed!
    }
  }
}
```

#### Step 3: Test
1. Restart Claude Code
2. Try: `@exai-mcp chat "test"`
3. Should work! ✅

**Pros**:
- ✅ Standard MCP protocol
- ✅ No Docker needed
- ✅ No WebSocket layer
- ✅ No shim needed
- ✅ Works with all MCP clients
- ✅ Best long-term solution

**Cons**:
- ❌ Requires code refactoring
- ❌ Need to adapt existing tools

---

### Option 3: Fix Docker Networking (Advanced)

**Only if you really need Docker**

#### Step 1: Use Host Network Mode (Linux Only)

**Note**: This won't work on Windows Docker Desktop

```yaml
# docker-compose.yml
services:
  exai-daemon:
    network_mode: "host"  # Linux only
```

#### Step 2: For Windows - Use npiperelay (Complex)

This is very complex and not recommended. Use Option 1 or 2 instead.

---

## 🧪 Testing Your Fix

### Test 1: Basic Connection
```
@exai-mcp chat "hello"
```

**Expected**: Should get a response

### Test 2: Tool Discovery
In Claude Code, check if tools appear:
```
@exai-mcp [Tab]
```

**Expected**: Should show list of tools

### Test 3: Complex Tool
```
@exai-mcp analyze_files {"paths": ["test.py"]}
```

**Expected**: Should execute without errors

---

## 📋 Troubleshooting Common Issues

### Issue: "Connection refused"
**Cause**: Daemon not running  
**Fix**: Start daemon (Option 1) or check Docker (if using Docker)

### Issue: "Authentication failed"
**Cause**: Token mismatch  
**Fix**: Ensure token matches in:
- `.env` file
- `mcp-config.claude.json`
- Running daemon configuration

### Issue: "Tool not found"
**Cause**: MCP discovery failed  
**Fix**: 
1. Check shim logs
2. Verify `list_tools()` returns tools
3. Test with `@filesystem-mcp` to verify Minimax MCP support

### Issue: "Timeout"
**Cause**: Slow connection or tool execution  
**Fix**: Increase timeout values:
```json
{
  "env": {
    "SIMPLE_TOOL_TIMEOUT_SECS": "120",
    "WORKFLOW_TOOL_TIMEOUT_SECS": "180"
  }
}
```

### Issue: "Other MCP servers work, but not exai-mcp"
**Cause**: Docker/WebSocket specific issue  
**Fix**: Use Option 1 or Option 2 above

---

## 🎯 Recommended Path

**For Quick Fix** → Use **Option 1** (Run on Windows)  
**For Best Solution** → Use **Option 2** (Native stdio)  
**For Docker Fans** → Use **Option 1** temporarily, then plan migration

---

## 📞 Additional Help

If none of these work:

1. **Check full analysis**: Read `exai_mcp_analysis.md` for detailed technical information
2. **Enable debug logging**:
   ```bash
   set LOG_LEVEL=DEBUG
   ```
3. **Check logs**:
   - Shim logs: stderr output
   - Daemon logs: `docker logs exai-mcp-daemon`
   - Claude Code logs: VS Code Developer Tools Console

4. **Test with real Claude API** (temporary test):
   ```json
   {
     "claudeCode.selectedModel": "claude-3-5-sonnet-20241022",
     "claudeCode.environmentVariables": [
       {
         "name": "ANTHROPIC_API_KEY",
         "value": "sk-ant-your-real-key"
       }
     ]
   }
   ```
   This rules out Minimax-specific issues.

---

## 📚 Files Referenced

- **Main Analysis**: `/home/ubuntu/exai_mcp_analysis.md`
- **Repository**: https://github.com/Zazzles2908/EX-AI-MCP-Server
- **Shim Script**: `scripts/runtime/run_ws_shim.py`
- **Daemon Script**: `scripts/ws/run_ws_daemon.py`
- **Docker Config**: `docker-compose.yml`

---

**Last Updated**: November 13, 2025  
**Version**: 1.0  
**Status**: Ready for Implementation
