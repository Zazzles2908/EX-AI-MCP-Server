# MCP Configuration Guide - Single Source of Truth

**Status:** ✅ **CLEANED UP - Single Configuration**

---

## 📁 MCP File Structure

### The Correct Structure

There are **3 MCP configuration files** in this project:

#### 1. `.claude/.mcp.json` ⭐ **MAIN FILE**
- **Location:** `C:/Project/EX-AI-MCP-Server/.claude/.mcp.json`
- **Used by:** Claude Code
- **Referenced by:** `.claude/settings.local.json` → `"mcpConfigPath"`
- **Status:** ✅ Contains all MCP servers

#### 2. `.mcp.json` (Root)
- **Location:** `C:/Project/EX-AI-MCP-Server/.mcp.json`
- **Used by:** Other MCP clients that look in the root directory
- **Status:** ✅ Identical to `.claude/.mcp.json`

#### 3. `project-template/.mcp.json` (Template)
- **Location:** `C:/Project/EX-AI-MCP-Server/project-template/.mcp.json`
- **Used by:** Template for new projects
- **Status:** ✅ Template/reference only

### Removed
- ❌ `.claude.mcp.json` (was in root - removed as it was wrong)

---

## 🔗 How Other VSCode AI Agents Connect

For **any VSCode AI agent** to use this project's MCP configuration:

### Method 1: Open as Workspace
1. Open this project in VSCode: `C:\Project\EX-AI-MCP-Server`
2. The agent will read `.claude/settings.local.json`
3. Follow the `mcpConfigPath` to `.claude/.mcp.json`
4. **Done!** All MCP servers are available

### Method 2: Direct MCP Config Path
Some agents accept an `mcpConfigPath` parameter:
```json
{
  "mcpConfigPath": "C:/Project/EX-AI-MCP-Server/.claude/.mcp.json"
}
```

### Method 3: Copy Configuration
Copy `.mcp.json` (root) to the agent's config location if needed.

---

## 📋 MCP Servers Configured

Both `.mcp.json` files contain:

### 1. git-mcp
```json
"git-mcp": {
  "command": "uvx",
  "args": ["mcp-server-git"],
  "env": {}
}
```
- **Purpose:** Git operations
- **Tools:** git status, commit, push, pull, branch management

### 2. exai-mcp
```json
"exai-mcp": {
  "command": "C:/Project/EX-AI-MCP-Server/.venv/Scripts/python.exe",
  "args": ["-u", "C:/Project/EX-AI-MCP-Server/scripts/runtime/run_ws_shim.py"],
  "env": {
    "ENV_FILE": "C:/Project/EX-AI-MCP-Server/.env",
    ...
  }
}
```
- **Purpose:** EXAI MCP tools (chat, debug, analyze, etc.)
- **Tools:** 19 EXAI tools

### 3. supabase-mcp-full
```json
"supabase-mcp-full": {
  "command": "cmd",
  "args": ["/c", "npx", "-y", "@supabase/mcp-server-supabase@latest"],
  "env": {
    "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
  }
}
```
- **Purpose:** Supabase management
- **Tools:** 8 categories (docs, account, database, debugging, development, functions, branching, storage)

---

## 🔐 Environment Variables Required

For the Supabase MCP to work, this environment variable must be set:

```bash
SUPABASE_ACCESS_TOKEN=sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
```

### How to Set It

#### Windows (System-wide):
```bash
setx SUPABASE_ACCESS_TOKEN "sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625"
```

#### Windows (Current Session):
```bash
set SUPABASE_ACCESS_TOKEN=sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
```

#### Linux/Mac:
```bash
export SUPABASE_ACCESS_TOKEN=sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
```

---

## 🧪 Testing the Configuration

### Test 1: Check Files Exist
```bash
# Should show 3 files
find . -name "*.mcp.json" | sort

# Should show the main file
ls -la .claude/.mcp.json
```

### Test 2: Verify Configured Servers
```bash
# Should show 3 MCP servers: git-mcp, exai-mcp, supabase-mcp-full
cat .claude/.mcp.json | grep -E '"[a-z-]+":'
```

### Test 3: Check Settings Reference
```bash
# Should show the correct path
cat .claude/settings.local.json | grep mcpConfigPath
# Expected: "mcpConfigPath": "C:/Project/EX-AI-MCP-Server/.claude/.mcp.json"
```

### Test 4: Test in Claude Code
```bash
# These should all work in Claude Code
@git-mcp git_status
@exai-mcp chat "test"
@supabase-mcp-full list_projects
```

---

## 🎯 For AI Agent Developers

### How to Use This Project's MCP Configuration

#### Step 1: Understand the Path
The **authoritative** MCP config is at:
```
C:/Project/EX-AI-MCP-Server/.claude/.mcp.json
```

#### Step 2: Read the Settings
The `.claude/settings.local.json` file shows:
```json
{
  "mcpConfigPath": "C:/Project/EX-AI-MCP-Server/.claude/.mcp.json"
}
```

#### Step 3: Use in Your Agent
```python
# Python example
mcp_config_path = "C:/Project/EX-AI-MCP-Server/.claude/.mcp.json"
with open(mcp_config_path, 'r') as f:
    mcp_config = json.load(f)

# Now you have access to all 3 MCP servers
servers = mcp_config['mcpServers']
```

#### Step 4: Set Environment Variables
Make sure to set `SUPABASE_ACCESS_TOKEN` before using the Supabase MCP.

---

## 📚 Files Reference

### Configuration Files
- `.claude/.mcp.json` - Main MCP config (used by Claude Code)
- `.mcp.json` - Copy for other MCP clients
- `.claude/settings.local.json` - Claude Code settings with mcpConfigPath
- `.env` - Environment variables (contains SUPABASE_ACCESS_TOKEN)

### Documentation
- `MCP_CONFIGURATION_GUIDE.md` - This file
- `SUPABASE_MCP_VALID_FEATURES_FIX.md` - Supabase MCP details
- `NATIVE_CLAUDECODE_SETUP.md` - Setup instructions

---

## ✨ Summary

| File | Purpose | Used By |
|------|---------|---------|
| `.claude/.mcp.json` | Main config | Claude Code |
| `.mcp.json` | Copy for other clients | Other MCP clients |
| `project-template/.mcp.json` | Template | New projects |

**Single source of truth: `.claude/.mcp.json`**

All MCP servers configured: git-mcp, exai-mcp, supabase-mcp-full

---

**Last Updated:** 2025-11-11
**Version:** 1.0.0
**Status:** ✅ **CLEAN AND DOCUMENTED**
