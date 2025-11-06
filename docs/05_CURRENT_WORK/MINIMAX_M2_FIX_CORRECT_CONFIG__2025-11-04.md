# MiniMax M2 Configuration Fix - Correct Method

> **EXAI-Validated Solution for Claude Code CLI**  
> Created: 2025-11-04  
> EXAI Consultation ID: bbae2baf-1366-496b-83f2-742b5bb330fa

---

## ❌ **What Was Wrong**

### **Incorrect Configuration**

We initially configured `.claude/settings.local.json` in the project directory:
```
C:\Project\EX-AI-MCP-Server\.claude\settings.local.json
```

**Problem:** This file is used by the **VS Code extension**, NOT the **Claude Code CLI** (`claude` command).

### **Root Cause (EXAI Analysis)**

1. **Wrong File Location**: `.claude/settings.local.json` is for VS Code extension only
2. **Wrong Schema**: The JSON structure was for the extension, not the CLI
3. **CLI Doesn't Read Project Config**: The `claude` CLI command reads from user home directory

---

## ✅ **Correct Configuration**

### **File Location**

**Correct Path:** `C:\Users\Jazeel-Home\.claude\config.json`

This is in your **user home directory** (`~/.claude/config.json`), NOT the project directory.

### **Correct Configuration Content**

```json
{
  "model": "minimax-m2",
  "api_base": "https://api.minimax.io/anthropic",
  "api_key": "${env:MINIMAX_API_KEY}"
}
```

---

## 🔧 **What Was Fixed**

### **1. Created Correct Config File**

**Location:** `C:\Users\Jazeel-Home\.claude\config.json`

**Content:**
```json
{
  "model": "minimax-m2",
  "api_base": "https://api.minimax.io/anthropic",
  "api_key": "${env:MINIMAX_API_KEY}"
}
```

### **2. Configuration Breakdown**

- **`model`**: Specifies "minimax-m2" as the default model
- **`api_base`**: Points to MiniMax's Anthropic-compatible API endpoint
- **`api_key`**: References the MINIMAX_API_KEY environment variable

---

## 🔑 **Environment Variable Setup**

### **Required Environment Variable**

```powershell
$env:MINIMAX_API_KEY = "your-actual-minimax-api-key-here"
```

### **Make It Persistent**

Add to your PowerShell profile:

**File:** `C:\Users\Jazeel-Home\Documents\PowerShell\Microsoft.PowerShell_profile.ps1`

**Content:**
```powershell
# MiniMax API Key for Claude Code
$env:MINIMAX_API_KEY = "your-actual-minimax-api-key-here"
```

---

## ✅ **Verification Steps**

### **1. Check Config File Exists**

```powershell
Test-Path "$env:USERPROFILE\.claude\config.json"
# Should return: True
```

### **2. View Config Content**

```powershell
Get-Content "$env:USERPROFILE\.claude\config.json"
```

**Expected Output:**
```json
{
  "model": "minimax-m2",
  "api_base": "https://api.minimax.io/anthropic",
  "api_key": "${env:MINIMAX_API_KEY}"
}
```

### **3. Verify Environment Variable**

```powershell
$env:MINIMAX_API_KEY
# Should output your API key
```

### **4. Test Claude Code**

```powershell
claude --help
```

Then try:
```powershell
claude "What model are you?"
```

**Expected:** Should use MiniMax M2 instead of Claude Sonnet

---

## 📊 **Configuration Comparison**

| Aspect | Wrong (Before) | Correct (After) |
|--------|----------------|-----------------|
| **File Location** | `C:\Project\EX-AI-MCP-Server\.claude\settings.local.json` | `C:\Users\Jazeel-Home\.claude\config.json` |
| **Scope** | Project-specific (VS Code extension) | User-wide (CLI) |
| **Used By** | VS Code extension only | Claude Code CLI |
| **Schema** | VS Code extension schema | CLI configuration schema |

---

## 🎯 **Key Insights from EXAI**

### **CLI vs VS Code Extension**

**Claude Code CLI (`claude` command):**
- Reads from: `~/.claude/config.json` (user home directory)
- Environment variables: Direct shell environment
- Configuration schema: Simple JSON with `model`, `api_base`, `api_key`

**VS Code Extension:**
- Reads from: `.claude/settings.local.json` (project directory)
- Environment variables: VS Code settings
- Configuration schema: Complex JSON with `modelConfig`, `exaiModelSelection`, etc.

### **Why Two Different Files?**

- **CLI**: Standalone tool, user-wide configuration
- **Extension**: Integrated with VS Code, project-specific configuration
- **They are separate tools** with different configuration systems!

---

## 🚀 **Next Steps**

### **1. Set Your API Key**

```powershell
$env:MINIMAX_API_KEY = "your-actual-minimax-api-key-here"
```

### **2. Test the Configuration**

```powershell
# Test basic functionality
claude --help

# Test model selection
claude "Hello, what model are you?"
```

### **3. Verify Model Usage**

Look for output indicating MiniMax M2 is being used instead of Claude Sonnet.

---

## 🔍 **Troubleshooting**

### **Issue: Still showing Claude Sonnet**

**Check:**
1. Config file exists: `Test-Path "$env:USERPROFILE\.claude\config.json"`
2. Config is valid JSON: `Get-Content "$env:USERPROFILE\.claude\config.json" | ConvertFrom-Json`
3. API key is set: `$env:MINIMAX_API_KEY`
4. Restart PowerShell session

### **Issue: API authentication errors**

**Solutions:**
1. Verify API key is correct
2. Test API endpoint:
   ```powershell
   curl -H "Authorization: Bearer $env:MINIMAX_API_KEY" https://api.minimax.io/anthropic/v1/models
   ```
3. Check network connectivity to MiniMax API

### **Issue: Command not found**

**Check:**
1. Claude Code is installed: `claude --version`
2. PATH includes Claude Code binary
3. Restart PowerShell after installation

---

## 📝 **Summary**

### **What We Learned**

1. **`.claude/settings.local.json`** is for **VS Code extension** only
2. **`~/.claude/config.json`** is for **Claude Code CLI**
3. They are **separate tools** with **different configuration systems**
4. The CLI reads from **user home directory**, not project directory

### **Correct Configuration**

**File:** `C:\Users\Jazeel-Home\.claude\config.json`

```json
{
  "model": "minimax-m2",
  "api_base": "https://api.minimax.io/anthropic",
  "api_key": "${env:MINIMAX_API_KEY}"
}
```

**Environment Variable:**
```powershell
$env:MINIMAX_API_KEY = "your-api-key-here"
```

---

## ✅ **Completion Checklist**

- [x] Created `~/.claude/config.json` with correct schema
- [x] Set `model` to "minimax-m2"
- [x] Set `api_base` to MiniMax endpoint
- [x] Configured `api_key` to use environment variable
- [ ] Set `MINIMAX_API_KEY` environment variable (user action required)
- [ ] Test with `claude "What model are you?"` (user action required)
- [ ] Verify MiniMax M2 is being used (user action required)

---

**EXAI Consultation:** bbae2baf-1366-496b-83f2-742b5bb330fa (19 exchanges remaining)  
**Version:** 1.0.0  
**Created:** 2025-11-04  
**Validated By:** EXAI GLM-4.6 with web search

