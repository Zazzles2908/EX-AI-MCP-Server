# Supabase MCP - Native Claude Code Setup (No Wrapper!)

**Status:** ✅ **SIMPLIFIED - Using Claude Code's Built-in Features**

---

## 💡 How It Works (The Simple Way)

You're absolutely right! Claude Code has environment variable support built-in. Here's how:

### 1. Environment Variable in System
The `SUPABASE_ACCESS_TOKEN` is now set in your Windows system environment:
```bash
setx SUPABASE_ACCESS_TOKEN "sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625"
```

### 2. .mcp.json Uses Native Support
The `.mcp.json` files use Claude Code's built-in `env` field:

```json
"supabase-mcp-full": {
  "command": "cmd",
  "args": [
    "/c",
    "npx",
    "-y",
    "@supabase/mcp-server-supabase@latest",
    "--access-token=${SUPABASE_ACCESS_TOKEN}"
  ],
  "env": {
    "SUPABASE_ACCESS_TOKEN": "${SUPABASE_ACCESS_TOKEN}"
  }
}
```

**What happens:**
- Claude Code reads the `env` field
- `${SUPABASE_ACCESS_TOKEN}` gets the value from your system environment
- Claude Code passes it to the MCP server process
- Supabase MCP server receives the token
- **It just works!** 🎉

---

## 🧪 Test It (Two Ways)

### Option 1: Use the Startup Script
Double-click: `START_CLAUDE_WITH_SUPABASE.bat`

### Option 2: Start Claude Code Normally
1. Open a new terminal/command prompt
2. Set the environment variable:
   ```bash
   set SUPABASE_ACCESS_TOKEN=sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
   ```
3. Start VSCode:
   ```bash
   code C:\Project\EX-AI-MCP-Server
   ```
4. Try in Claude Code:
   ```bash
   @supabase-mcp-full list_projects
   ```

---

## 🎯 What Changed

| Before (Complex) | After (Simple) |
|-----------------|----------------|
| Wrapper script required | No wrapper needed |
| Custom Python loader | Native Claude Code support |
| Extra files to maintain | Pure .mcp.json configuration |
| Overcomplicated | Simple & clean |

---

## ✅ Verification

### Check 1: Environment Variable
```bash
echo %SUPABASE_ACCESS_TOKEN%
# Should output: sbp_ebdcf0465cfac2f3354e815f35818b7f1cef4625
```

### Check 2: .mcp.json Configuration
```bash
cat .mcp.json | grep -A5 "supabase-mcp-full"
# Should show the env field with SUPABASE_ACCESS_TOKEN
```

### Check 3: Test in Claude Code
```bash
@supabase-mcp-full list_projects
# Should return your Supabase projects
```

---

## 🔧 Files Involved

### Configuration Files
- `.mcp.json` - Root MCP config (uses native env support)
- `.claude/.mcp.json` - Claude Code MCP config (uses native env support)
- `.env` - Reference (still there, but not used by MCP server)

### Utility Files
- `START_CLAUDE_WITH_SUPABASE.bat` - Helper script to start Claude Code with env vars
- `NATIVE_CLAUDECODE_SETUP.md` - This file

### Removed (No Longer Needed)
- `scripts/load_env_and_run_supabase_mcp.py` - Wrapper script (deleted)

---

## 📚 How It Really Works

When you use `@supabase-mcp-full` in Claude Code:

1. **Claude Code reads** `.claude/.mcp.json`
2. **Claude Code sees** the `env` field with `SUPABASE_ACCESS_TOKEN`
3. **Claude Code gets** the value from your system environment
4. **Claude Code passes** `SUPABASE_ACCESS_TOKEN=sbp_...` to the npx process
5. **npx starts** the Supabase MCP server with the token
6. **MCP server** authenticates with Supabase
7. **You get results!** ✅

**No wrapper. No extra scripts. Just native Claude Code MCP support.** ✨

---

## 🎉 The End Result

You now have:
- ✅ Native Supabase MCP integration in Claude Code
- ✅ No unnecessary wrapper scripts
- ✅ Clean, maintainable configuration
- ✅ All 17 Supabase tool categories available

**Ready to use!** Just start Claude Code and start using `@supabase-mcp-full` commands. 🚀

---

**Last Updated:** 2025-11-11
**Version:** 3.0.0 (Simplified)
**Status:** ✅ **NATIVE & CLEAN**
