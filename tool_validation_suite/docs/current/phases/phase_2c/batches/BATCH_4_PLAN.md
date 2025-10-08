# Phase 2C - Batch 4: Code Cleanup

**Date:** 2025-10-07  
**Status:** 🚧 IN PROGRESS  
**Time Estimate:** 1 hour  
**Time Spent:** 0 hours  
**Completion:** 0%

---

## 🎯 **OBJECTIVE**

Clean up remaining code quality issues: dead code, unused imports, commented code, and improve code organization.

---

## 📋 **SCOPE**

### **From Phase 1 Audit:**
- **14 performance anti-patterns** identified
- **Commented-out code** scattered throughout
- **Unused imports** in multiple files
- **Dead code paths** that are never executed
- **Inconsistent error handling** patterns

---

## 🔍 **CLEANUP CATEGORIES**

### **Priority 1: Dead Code Removal (30 minutes)**

**Target Files:**
1. `src/daemon/ws_server.py`
2. `src/providers/kimi_chat.py`
3. `src/providers/glm_chat.py`
4. `src/core/config.py`

**What to Look For:**
- Commented-out code blocks
- Unused functions/methods
- Unreachable code paths
- Legacy compatibility code no longer needed

---

### **Priority 2: Import Cleanup (15 minutes)**

**Target Files:**
1. All files in `src/daemon/`
2. All files in `src/providers/`
3. All files in `src/core/`

**What to Look For:**
- Unused imports
- Duplicate imports
- Wildcard imports (`from x import *`)
- Circular import risks

---

### **Priority 3: Code Organization (15 minutes)**

**Target Areas:**
1. Long functions (>100 lines)
2. Deeply nested code (>4 levels)
3. Duplicate code patterns
4. Magic numbers without constants

**What to Look For:**
- Functions that should be split
- Code that should be extracted to helpers
- Repeated patterns that should be DRY'd up
- Hardcoded values that should be constants

---

## 🎯 **IMPLEMENTATION PLAN**

### **Step 1: Audit ws_server.py (15 minutes)**
1. Search for commented-out code
2. Identify unused functions
3. Check for unreachable code paths
4. List findings

### **Step 2: Audit Provider Files (15 minutes)**
1. Check kimi_chat.py for dead code
2. Check glm_chat.py for dead code
3. Identify unused imports
4. List findings

### **Step 3: Clean Up Dead Code (15 minutes)**
1. Remove commented-out code
2. Remove unused functions
3. Remove unreachable code paths
4. Test after each removal

### **Step 4: Clean Up Imports (15 minutes)**
1. Remove unused imports
2. Organize imports (stdlib, third-party, local)
3. Remove wildcard imports
4. Test after cleanup

---

## 🚨 **SAFETY RULES**

**Before Removing Anything:**
1. ✅ Verify it's truly unused (search for references)
2. ✅ Check git history for context
3. ✅ Test after each removal
4. ✅ Document what was removed and why

**What NOT to Remove:**
- ❌ Code with TODO comments (might be planned work)
- ❌ Code that looks unused but is called dynamically
- ❌ Compatibility shims for different Python versions
- ❌ Error handling that seems redundant but isn't

---

## 📊 **EXPECTED OUTCOMES**

**Code Quality:**
- Before: Commented code, unused imports, dead code
- After: Clean, maintainable code

**File Size Reduction:**
- Estimated: 5-10% reduction in LOC
- Focus: Remove noise, keep signal

**Maintainability:**
- Before: Confusing dead code paths
- After: Clear, intentional code

---

## 📋 **SUCCESS CRITERIA**

1. ✅ No commented-out code blocks
2. ✅ No unused imports
3. ✅ No unreachable code paths
4. ✅ All tests passing
5. ✅ Server restarts successfully
6. ✅ No regressions

---

**Status:** Ready to begin  
**Confidence:** HIGH - Conservative approach, test after each change  
**Next:** Audit ws_server.py for dead code

