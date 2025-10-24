# Multi-VSCode Instance Setup Guide

**Date:** 2025-10-24  
**Purpose:** Configure multiple VSCode instances to use separate MCP server sessions without conflicts

## Problem Statement

When multiple VSCode instances use the same MCP configuration:
1. **Double-up entries in Supabase** - Both instances share the same session_id
2. **Request bottlenecks** - Requests queue up and block each other
3. **Monitoring confusion** - Can't distinguish which VSCode made which request

## Solution: Unique Session IDs Per VSCode Instance

Each VSCode instance gets its own unique `EXAI_SESSION_ID` and `MCP_SERVER_ID` to ensure:
- ✅ Separate session tracking in Supabase
- ✅ Independent request processing (no blocking)
- ✅ Clear monitoring visibility per VSCode instance

## Configuration Files

### VSCode Instance 1
**File:** `Daemon/mcp-config.augmentcode.vscode1.json`

```json
{
  "mcpServers": {
    "EXAI-WS-VSCode1": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_SESSION_ID": "vscode-instance-1",
        "MCP_SERVER_ID": "exai-ws-vscode1"
      }
    }
  }
}
```

### VSCode Instance 2
**File:** `Daemon/mcp-config.augmentcode.vscode2.json`

```json
{
  "mcpServers": {
    "EXAI-WS-VSCode2": {
      "type": "stdio",
      "trust": true,
      "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
      "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
      "cwd": "C:/Project/EX-AI-MCP-Server",
      "env": {
        "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
        "PYTHONUNBUFFERED": "1",
        "PYTHONIOENCODING": "utf-8",
        "LOG_LEVEL": "INFO",
        "EXAI_WS_HOST": "127.0.0.1",
        "EXAI_WS_PORT": "8079",
        "EXAI_SESSION_ID": "vscode-instance-2",
        "MCP_SERVER_ID": "exai-ws-vscode2"
      }
    }
  }
}
```

## Setup Instructions

### Step 1: Copy Config Files to VSCode Settings

**For VSCode Instance 1:**
1. Open VSCode Instance 1
2. Press `Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)"
3. Add or update the `mcp` section:
   ```json
   {
     "mcp": {
       "configPath": "C:/Project/EX-AI-MCP-Server/Daemon/mcp-config.augmentcode.vscode1.json"
     }
   }
   ```

**For VSCode Instance 2:**
1. Open VSCode Instance 2
2. Press `Ctrl+Shift+P` → "Preferences: Open User Settings (JSON)"
3. Add or update the `mcp` section:
   ```json
   {
     "mcp": {
       "configPath": "C:/Project/EX-AI-MCP-Server/Daemon/mcp-config.augmentcode.vscode2.json"
     }
   }
   ```

### Step 2: Reload VSCode Windows

1. In each VSCode instance: `Ctrl+Shift+P` → "Developer: Reload Window"
2. Wait for MCP server to connect (check status bar)

### Step 3: Verify Separation

**Check Supabase:**
```sql
SELECT DISTINCT session_id, COUNT(*) as request_count
FROM messages
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY session_id
ORDER BY created_at DESC;
```

You should see:
- `vscode-instance-1` - Requests from VSCode 1
- `vscode-instance-2` - Requests from VSCode 2

**Check Monitoring Dashboard:**
- Visit `http://localhost:8080`
- Filter by session_id to see requests from each VSCode instance separately

## Key Differences Between Configs

⚠️ **CRITICAL:** The MCP server name in the config file MUST be unique for each VSCode instance!

| Setting | VSCode 1 | VSCode 2 | Purpose |
|---------|----------|----------|---------|
| **MCP Server Name** | `EXAI-WS-VSCode1` | `EXAI-WS-VSCode2` | **CRITICAL:** Unique server name so Augment sees them as different MCP servers |
| `EXAI_SESSION_ID` | `vscode-instance-1` | `vscode-instance-2` | Unique session tracking in Supabase |
| `MCP_SERVER_ID` | `exai-ws-vscode1` | `exai-ws-vscode2` | Unique MCP server identification |
| `EXAI_WS_PORT` | `8079` | `8079` | Both connect to same Docker daemon (shared backend) |

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  VSCode 1       │         │  VSCode 2       │
│  session-1      │         │  session-2      │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │  WebSocket (8079)         │  WebSocket (8079)
         │                           │
         └───────────┬───────────────┘
                     │
         ┌───────────▼────────────┐
         │  Docker Daemon         │
         │  (Port 8079)           │
         │  - Shared backend      │
         │  - Separate sessions   │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │  Supabase Storage      │
         │  - session-1 messages  │
         │  - session-2 messages  │
         └────────────────────────┘
```

## Benefits

1. **No Double-Ups:** Each VSCode instance has unique session_id
2. **No Blocking:** Requests processed independently (shared daemon handles concurrency)
3. **Clear Monitoring:** Can filter by session_id to see which VSCode made which request
4. **Shared Backend:** Both instances use same Docker daemon (efficient resource usage)

## Troubleshooting

### Issue: Still seeing double-ups in Supabase
**Solution:** Verify each VSCode is using the correct config file:
1. Check VSCode settings.json has correct `mcp.configPath`
2. Reload VSCode window after changing config
3. Check logs: `logs/ws_shim.log` should show different session_ids

### Issue: Requests still blocking each other
**Solution:** This is expected behavior - the Docker daemon processes requests sequentially. For true parallel processing, you would need multiple daemon instances on different ports (see Advanced Setup below).

## Advanced Setup: Multiple Daemon Instances (Optional)

If you need true parallel processing without any blocking:

1. **Run multiple Docker daemon instances:**
   ```bash
   # Daemon 1 on port 8079
   docker-compose up -d
   
   # Daemon 2 on port 8080 (requires separate docker-compose file)
   # Not implemented yet - contact maintainer if needed
   ```

2. **Update configs to use different ports:**
   - VSCode 1: `EXAI_WS_PORT: "8079"`
   - VSCode 2: `EXAI_WS_PORT: "8080"`

**Note:** This requires additional Docker configuration and is only needed for high-concurrency scenarios.

## Maintenance

- **Adding more VSCode instances:** Copy `vscode2.json`, increment the instance number, and update session_id/server_id
- **Removing instances:** Delete the config file and remove from VSCode settings
- **Monitoring:** Use Supabase queries to track session activity and identify issues

## Related Documentation

- [Comprehensive Monitoring System Design](./COMPREHENSIVE_MONITORING_SYSTEM_DESIGN_2025-10-24.md)
- [Docker Architecture](../../DEPENDENCY_MAP.md)
- [MCP Configuration Guide](../../.augment/rules/gh-tool_kit_mcp.md)

