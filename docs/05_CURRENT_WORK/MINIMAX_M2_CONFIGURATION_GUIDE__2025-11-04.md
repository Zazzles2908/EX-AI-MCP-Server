# MiniMax M2 Configuration Guide for Claude Code

> **Complete guide for configuring Claude Code to use MiniMax M2 instead of Claude models**  
> Created: 2025-11-04  
> Version: 1.0.0

---

## 🎯 **Overview**

This guide explains how to configure Claude Code to use **MiniMax M2** as the primary model instead of Claude models (Haiku, Sonnet, Opus). MiniMax M2 provides enhanced code understanding, multi-turn dialogue, and deep reasoning capabilities.

---

## 📁 **Configuration File Hierarchy**

Claude Code uses a **layered configuration system** with the following priority order:

### **1. Global Config** (Lowest Priority)
- **Location:** `config/settings.json`
- **Scope:** System-wide defaults
- **Used By:** All Claude Code instances
- **Priority:** Lowest (overridden by workspace settings)

### **2. VS Code Workspace** (Medium Priority)
- **Location:** `.vscode/settings.json`
- **Scope:** VS Code GUI only
- **Used By:** VS Code integrated features
- **Priority:** Medium (overrides global, overridden by local)
- **Limitation:** ⚠️ **NOT read by terminal CLI** (`claudecode` command)

### **3. Local Workspace** (Highest Priority) ⭐
- **Location:** `.claude/settings.local.json`
- **Scope:** **Both VS Code GUI and terminal CLI**
- **Used By:** All Claude Code interfaces
- **Priority:** Highest (overrides all other configs)
- **Key Insight:** This is the **ONLY** config file read by the terminal CLI!

---

## 🔧 **Configuration Changes Made**

### **Updated `.claude/settings.local.json`**

Added complete MiniMax M2 configuration to the `modelConfig` section:

```json
{
  "modelConfig": {
    "primaryModel": "MiniMax-M2",
    "fallbackModel": "MiniMax-M2",
    "autoFallback": true,
    "model": "minimax-m2",
    "env": {
      "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
      "ANTHROPIC_AUTH_TOKEN": "${env:MINIMAX_API_KEY}",
      "ANTHROPIC_MODEL": "MiniMax-M2"
    },
    "modelOverrides": {
      "claude-3-5-haiku-20241022": "minimax-m2",
      "claude-3-5-sonnet-20241022": "minimax-m2",
      "claude-3-opus-20240229": "minimax-m2"
    }
  }
}
```

### **Configuration Breakdown**

#### **1. Primary and Fallback Models**
```json
"primaryModel": "MiniMax-M2",
"fallbackModel": "MiniMax-M2",
"autoFallback": true
```
- Sets MiniMax M2 as both primary and fallback model
- Enables automatic fallback if primary model fails

#### **2. Model Identifier**
```json
"model": "minimax-m2"
```
- Specifies the exact model identifier for API calls

#### **3. Environment Variables**
```json
"env": {
  "ANTHROPIC_BASE_URL": "https://api.minimax.io/anthropic",
  "ANTHROPIC_AUTH_TOKEN": "${env:MINIMAX_API_KEY}",
  "ANTHROPIC_MODEL": "MiniMax-M2"
}
```
- **ANTHROPIC_BASE_URL**: MiniMax API endpoint (Anthropic-compatible)
- **ANTHROPIC_AUTH_TOKEN**: Your MiniMax API key (from environment variable)
- **ANTHROPIC_MODEL**: Model name for API requests

#### **4. Model Overrides**
```json
"modelOverrides": {
  "claude-3-5-haiku-20241022": "minimax-m2",
  "claude-3-5-sonnet-20241022": "minimax-m2",
  "claude-3-opus-20240229": "minimax-m2"
}
```
- Redirects all Claude model requests to MiniMax M2
- Ensures consistent model usage across all interfaces

---

## 🔑 **Environment Variables Required**

### **Set in PowerShell (Windows)**

```powershell
# Required
$env:MINIMAX_API_KEY = "your-minimax-api-key-here"

# Optional (already configured in settings.local.json)
$env:ANTHROPIC_BASE_URL = "https://api.minimax.io/anthropic"
$env:ANTHROPIC_MODEL = "MiniMax-M2"
```

### **Set in Bash (Linux/Mac)**

```bash
# Required
export MINIMAX_API_KEY="your-minimax-api-key-here"

# Optional (already configured in settings.local.json)
export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
export ANTHROPIC_MODEL="MiniMax-M2"
```

### **Persistent Configuration**

Add to your shell profile for persistence:

**PowerShell:** Add to `$PROFILE` (usually `~\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`)

**Bash:** Add to `~/.bashrc` or `~/.bash_profile`

---

## ✅ **Verification Steps**

### **1. Test in VS Code Integrated Terminal (Recommended)**

This is the **recommended** approach because the integrated terminal automatically inherits workspace settings.

```powershell
# Open VS Code integrated terminal (Ctrl + `)
cd C:\Project\EX-AI-MCP-Server

# Test with a simple prompt
claudecode "Hello, what model are you?"
```

**Expected Output:**
```
Usage by model:
        MiniMax-M2:  XXX input, XXX output
```

**NOT (Claude):**
```
Usage by model:
        claude-haiku:  0 input, 314 output
       claude-sonnet:  0 input, 434 output
```

### **2. Verify Configuration File**

```powershell
# Check settings.local.json exists and is valid
Get-Content .claude\settings.local.json | ConvertFrom-Json | Select-Object -ExpandProperty modelConfig
```

**Expected Output:**
```
primaryModel   : MiniMax-M2
fallbackModel  : MiniMax-M2
autoFallback   : True
model          : minimax-m2
env            : @{ANTHROPIC_BASE_URL=https://api.minimax.io/anthropic; ANTHROPIC_AUTH_TOKEN=${env:MINIMAX_API_KEY}; ANTHROPIC_MODEL=MiniMax-M2}
modelOverrides : @{claude-3-5-haiku-20241022=minimax-m2; claude-3-5-sonnet-20241022=minimax-m2; claude-3-opus-20240229=minimax-m2}
```

### **3. Run Verification Script**

```powershell
.\scripts\verify_minimax_config.ps1
```

This script checks:
- Configuration file exists and is valid JSON
- MiniMax M2 is set as primary model
- Environment variables are configured
- Model overrides are in place

---

## 🚀 **Usage Recommendations**

### **✅ RECOMMENDED: Use VS Code Integrated Terminal**

**Why?**
- Automatically inherits workspace settings from `.claude/settings.local.json`
- No manual environment variable setup needed
- Consistent behavior across sessions
- Already configured correctly

**How?**
1. Open VS Code
2. Press `Ctrl + \`` to open integrated terminal
3. Use `claudecode` command directly

### **⚠️ ALTERNATIVE: External PowerShell**

If you must use external PowerShell (not recommended), you need to set environment variables manually:

```powershell
# Set environment variables
$env:MINIMAX_API_KEY = "your-api-key-here"
$env:ANTHROPIC_BASE_URL = "https://api.minimax.io/anthropic"
$env:ANTHROPIC_MODEL = "MiniMax-M2"

# Navigate to project directory
cd C:\Project\EX-AI-MCP-Server

# Use claudecode
claudecode "Your prompt here"
```

---

## 🔍 **Troubleshooting**

### **Issue: Still seeing Claude models in output**

**Symptoms:**
```
Usage by model:
        claude-haiku:  0 input, 314 output
       claude-sonnet:  0 input, 434 output
```

**Solutions:**
1. **Restart VS Code completely**
   - Close all VS Code windows
   - Reopen VS Code
   - Open new integrated terminal

2. **Verify configuration file**
   ```powershell
   Get-Content .claude\settings.local.json | ConvertFrom-Json | Select-Object -ExpandProperty modelConfig
   ```

3. **Check environment variable**
   ```powershell
   $env:MINIMAX_API_KEY
   ```
   Should output your API key (not empty)

4. **Clear Claude Code cache**
   ```powershell
   Remove-Item -Recurse -Force "$env:USERPROFILE\.claude\cache" -ErrorAction SilentlyContinue
   ```

### **Issue: Configuration not loading**

**Symptoms:**
- Changes to `.claude/settings.local.json` not taking effect
- Default Claude models still being used

**Solutions:**
1. **Verify JSON syntax**
   ```powershell
   Get-Content .claude\settings.local.json | ConvertFrom-Json
   ```
   Should not produce errors

2. **Check file location**
   - File must be at: `C:\Project\EX-AI-MCP-Server\.claude\settings.local.json`
   - Not in `.vscode\` or `config\`

3. **Restart Claude Code**
   - Close all terminals
   - Restart VS Code
   - Open new integrated terminal

### **Issue: API authentication errors**

**Symptoms:**
```
Error: Authentication failed
Error: Invalid API key
```

**Solutions:**
1. **Verify API key is set**
   ```powershell
   $env:MINIMAX_API_KEY
   ```

2. **Check API key validity**
   - Log in to MiniMax platform
   - Verify API key is active
   - Generate new key if needed

3. **Test API connection**
   ```powershell
   curl -H "Authorization: Bearer $env:MINIMAX_API_KEY" https://api.minimax.io/anthropic/v1/models
   ```

---

## 📊 **Configuration Summary**

### **What Changed**

| Component | Before | After |
|-----------|--------|-------|
| **Primary Model** | Claude Sonnet | MiniMax M2 |
| **Fallback Model** | Claude Sonnet | MiniMax M2 |
| **API Endpoint** | Anthropic | MiniMax (Anthropic-compatible) |
| **Model Overrides** | None | All Claude models → MiniMax M2 |
| **Environment Variables** | None | MINIMAX_API_KEY, ANTHROPIC_BASE_URL |

### **Result**

- ✅ Terminal CLI uses MiniMax M2
- ✅ VS Code GUI uses MiniMax M2
- ✅ Consistent model usage across all interfaces
- ✅ Automatic fallback to MiniMax M2
- ✅ All Claude model requests redirected to MiniMax M2

---

## 🎯 **Best Practices**

### **1. Use Integrated Terminal**
- Always use VS Code integrated terminal (`Ctrl + \``)
- Avoids environment variable configuration issues
- Ensures consistent behavior

### **2. Set Environment Variables Persistently**
- Add to PowerShell profile or `.bashrc`
- Prevents need to set variables every session
- Ensures availability across all terminals

### **3. Verify Configuration After Changes**
- Run verification script after any config changes
- Test with simple prompt to confirm model usage
- Check output for "MiniMax-M2" in usage statistics

### **4. Keep API Key Secure**
- Never commit API key to version control
- Use environment variables only
- Rotate keys periodically

---

## 📚 **Additional Resources**

- **MiniMax Documentation:** https://platform.minimax.io/docs/guides/text-ai-coding-tools
- **Claude Code Documentation:** https://www.anthropic.com/news/claude-code
- **Agent-Based Architecture:** See `.claude/agents/README.md`
- **EXAI Configuration:** See `.claude/EXAI_MCP_CONFIGURATION_GUIDE.md`

---

## ✅ **Quick Reference**

### **Configuration File**
```
.claude/settings.local.json
```

### **Required Environment Variable**
```powershell
$env:MINIMAX_API_KEY = "your-api-key-here"
```

### **Test Command**
```powershell
claudecode "Hello, what model are you?"
```

### **Expected Output**
```
Usage by model:
        MiniMax-M2:  XXX input, XXX output
```

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Maintained By:** EX-AI MCP Server Team

