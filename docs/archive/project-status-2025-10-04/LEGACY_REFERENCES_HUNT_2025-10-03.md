# Legacy References Hunt - 2025-10-03
## Systematic Search for Old/Redundant Terms

**Date:** 2025-10-03
**Status:** 🔍 IN PROGRESS
**Priority:** MEDIUM

---

## 🎯 Search Targets

**Legacy Terms to Find:**
1. "Claude" / "claude" / "CLAUDE" - Old AI assistant references
2. "Zen" / "zen" / "ZEN" - Original repository name
3. Other redundant/outdated terms

---

## 📊 Findings Summary

### Category 1: Legitimate Claude References (KEEP)
**These are OK - they refer to Claude Desktop client:**

1. **Daemon/mcp-config.claude.json** - Claude Desktop MCP config file
2. **run-server.ps1** lines 977-984 - Claude Desktop client detection
3. **run-server.ps1** lines 1429-1450 - Claude CLI integration
4. **run-server.sh** lines 1245-1256 - Claude Code registration
5. **src/server/handlers/mcp_handlers.py** lines 36-49 - Client detection with CLAUDE_* fallback

**Verdict:** ✅ KEEP - These are legitimate references to Claude Desktop as a client

---

### Category 2: Legacy CLAUDE_* Environment Variables (DOCUMENTED)
**Status:** ✅ ALREADY DOCUMENTED AS DEPRECATED

**Files:**
1. **.env.example** lines 152-158 - Deprecation notice with CLIENT_* preferred
2. **src/server/handlers/mcp_handlers.py** line 48-49 - Backward compatibility fallback

**Code:**
```python
# Preferred: CLIENT_TOOL_ALLOWLIST
# Legacy fallback: CLAUDE_TOOL_ALLOWLIST
raw_allow = os.getenv("CLIENT_TOOL_ALLOWLIST", os.getenv("CLAUDE_TOOL_ALLOWLIST", ""))
```

**Verdict:** ✅ KEEP - Backward compatibility maintained, properly documented

---

### Category 3: Legacy "Zen" References (NEEDS FIXING)

#### 🚨 FOUND: run-server.sh line 1247
**File:** `run-server.sh`
**Line:** 1247
**Code:**
```bash
print_success "Successfully added Zen to Claude Code"
```

**Issue:** Should say "EXAI" not "Zen"
**Severity:** LOW
**Fix Required:** Change "Zen" → "EXAI"

#### 🚨 FOUND: run-server.ps1 lines 1440-1448
**File:** `run-server.ps1`
**Lines:** 1440, 1443, 1444, 1448
**Code:**
```powershell
if ($claudeConfig -match "zen") {
    Write-Success "Claude CLI already configured for zen server"
} else {
    Write-Info "To add zen server to Claude CLI, run:"
    Write-Host "  claude config add-server zen $PythonPath $ServerPath"
}
# ...
Write-Host "  claude config add-server zen $PythonPath $ServerPath"
```

**Issue:** Multiple "zen" references should be "exai"
**Severity:** LOW
**Fix Required:** Change all "zen" → "exai"

---

### Category 4: Documentation References (ARCHIVE ONLY)

**Found in archived/superseded docs:**
- `docs/archive/superseded-20251003/` - Multiple Claude/Zen references
- `docs/archive/cleanup_backup_20251003_082921/` - Legacy references
- `docs/archive/legacy-scripts/` - Old code with legacy terms

**Verdict:** ✅ KEEP - These are archived for historical reference

---

### Category 5: Workflow Tool References (ALREADY FIXED)

**Previously Fixed:**
- ✅ `tools/workflow/file_embedding.py` - Changed "Claude" → "the AI assistant"
- ✅ `tools/workflow/orchestration.py` - Changed "Claude" → "the AI assistant"
- ✅ `tools/workflow/request_accessors.py` - Changed "Claude" → "the AI assistant"

**Validation:** ✅ CONFIRMED - No "Claude" in tool outputs

---

## 🔧 Fixes Required

### Fix #1: run-server.sh Line 1247
**File:** `run-server.sh`
**Change:**
```bash
# BEFORE
print_success "Successfully added Zen to Claude Code"

# AFTER
print_success "Successfully added EXAI to Claude Code"
```

### Fix #2: run-server.ps1 Lines 1440-1448
**File:** `run-server.ps1`
**Changes:**
```powershell
# BEFORE
if ($claudeConfig -match "zen") {
    Write-Success "Claude CLI already configured for zen server"
} else {
    Write-Info "To add zen server to Claude CLI, run:"
    Write-Host "  claude config add-server zen $PythonPath $ServerPath"
}

# AFTER
if ($claudeConfig -match "exai") {
    Write-Success "Claude CLI already configured for exai server"
} else {
    Write-Info "To add exai server to Claude CLI, run:"
    Write-Host "  claude config add-server exai $PythonPath $ServerPath"
}
```

---

## 📋 Action Items

### High Priority
- [ ] Fix run-server.sh line 1247 (Zen → EXAI)
- [ ] Fix run-server.ps1 lines 1440-1448 (zen → exai, 4 occurrences)

### Medium Priority
- [ ] Search for any other "zen" references in active code
- [ ] Verify no "Zen" in user-facing messages
- [ ] Check for "zen" in configuration files

### Low Priority
- [ ] Review archived docs for completeness
- [ ] Document all legitimate Claude references
- [ ] Create style guide for naming conventions

---

## 🎯 Search Commands Used

**Codebase Retrieval:**
```
Find all occurrences of legacy references: "Claude", "claude", "Zen", "zen", "CLAUDE", "ZEN"
```

**Manual Inspection:**
- Reviewed run-server.sh
- Reviewed run-server.ps1
- Reviewed .env.example
- Reviewed mcp_handlers.py
- Reviewed workflow tools

---

## ✅ Verification Checklist

**After Fixes:**
- [ ] Run server startup scripts
- [ ] Verify success messages show "EXAI"
- [ ] Test Claude CLI integration messages
- [ ] Confirm no "zen" in user-facing output
- [ ] Validate backward compatibility maintained

---

**Last Updated:** 2025-10-03 21:45
**Status:** 🔍 2 files need fixing (run-server.sh, run-server.ps1)
**Total Issues:** 5 occurrences of "zen" to change to "exai"

