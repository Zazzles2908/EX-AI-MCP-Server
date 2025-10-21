# Ripgrep Tool Integration Issue

**Date:** 2025-10-14  
**Status:** ⚠️ AUGMENT LIMITATION (Cannot fix in codebase)  
**Impact:** grep-search tool unavailable in Augment Agent  

---

## Issue Description

Augment Agent's `grep-search` tool reports "Ripgrep binary is not found" even though ripgrep is installed on the system.

**Evidence:**
```
Ripgrep binary is not found. grep-search tool is not available. Do not try to call it again. Use other tools.
```

**System Check:**
```powershell
PS> Get-Command rg
CommandType     Name                                               Version    Source
-----------     ----                                               -------    ------
Application     rg.exe                                             14.1.1.0   C:\ProgramData\chocolatey\bin\rg.exe
```

**Ripgrep IS installed at:** `C:\ProgramData\chocolatey\bin\rg.exe`

---

## Root Cause

This is an **Augment Agent configuration issue**, not a project codebase issue. The grep-search tool in Augment cannot locate the ripgrep binary even though it exists in the system PATH.

**Possible Causes:**
1. Augment's tool configuration doesn't check Chocolatey bin directory
2. Augment expects ripgrep in a different location
3. Augment's PATH environment doesn't include Chocolatey paths
4. Augment tool bridge has hardcoded ripgrep path

---

## Workarounds

Since this is an Augment limitation, use alternative search methods:

### 1. Use PowerShell Select-String
```powershell
Get-ChildItem -Path . -Recurse -Include *.py | Select-String -Pattern "pattern"
```

### 2. Use view tool with search_query_regex
```python
view(path="file.py", type="file", search_query_regex="pattern")
```

### 3. Use codebase-retrieval for semantic search
```python
codebase-retrieval(information_request="Find code that does X")
```

### 4. Use direct ripgrep via launch-process
```powershell
rg "pattern" --type py
```

---

## Impact on Project

**Low Impact:**
- Alternative search methods available
- codebase-retrieval often better for semantic search
- view tool with regex works for single files
- PowerShell Select-String works for multi-file search

**No Action Required:**
- This is not a project codebase issue
- Cannot be fixed by modifying project files
- Workarounds are sufficient

---

## Recommendation

**For Augment Team:**
- Update grep-search tool to check Chocolatey bin directory
- Or document expected ripgrep installation location
- Or provide better error message with installation instructions

**For Project:**
- Document this limitation in known issues
- Use alternative search methods
- Mark task as "Cannot Fix - External Dependency"

---

**Status:** Documented as known limitation  
**Resolution:** Use workarounds (codebase-retrieval, view with regex, PowerShell)  
**Action:** None required in project codebase

