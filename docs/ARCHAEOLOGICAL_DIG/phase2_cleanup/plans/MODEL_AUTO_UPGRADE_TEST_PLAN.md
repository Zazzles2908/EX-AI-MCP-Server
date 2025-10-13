# Model Auto-Upgrade & Adaptive Timeout Test Plan
**Date:** 2025-10-11  
**Purpose:** Comprehensive validation of model auto-upgrade and adaptive timeout implementation

---

## 🎯 Implementation Summary

### **Changes Made:**

1. **Auto-Upgrade Logic** (`tools/workflow/expert_analysis.py`)
   - Detects when model doesn't support thinking mode
   - Auto-upgrades within same provider:
     - GLM: glm-4.5-flash → glm-4.6
     - Kimi: kimi-k2-0905-preview → kimi-thinking-preview
   - Logs upgrade transparently

2. **Adaptive Timeout** (`tools/workflows/thinkdeep.py`)
   - Uses `EXPERT_ANALYSIS_TIMEOUT_SECS` from .env as base (180s)
   - Applies multipliers based on thinking mode:
     - minimal: 0.5x (90s)
     - low: 0.7x (126s)
     - medium: 1.0x (180s)
     - high: 1.5x (270s)
     - max: 2.0x (360s)
   - Can be overridden via `THINKDEEP_EXPERT_TIMEOUT_SECS` env var

3. **Documentation** (`.env.example`)
   - Added explanation of adaptive timeout behavior
   - Documented override mechanism

---

## ✅ Test Scenarios

### **Test 1: Chat Tool (Simple, No Expert Analysis)**
**Purpose:** Verify basic functionality works

| Model | Expected Behavior | Status |
|-------|------------------|--------|
| glm-4.5-flash | Works, no upgrade needed | ⏳ |
| glm-4.6 | Works, no upgrade needed | ⏳ |
| kimi-k2-0905-preview | Works, no upgrade needed | ⏳ |

### **Test 2: Thinkdeep with Auto-Upgrade (GLM)**
**Purpose:** Verify auto-upgrade from glm-4.5-flash → glm-4.6

| Scenario | Model | Thinking Mode | Expected Timeout | Expected Upgrade | Status |
|----------|-------|---------------|------------------|------------------|--------|
| 2a | glm-4.5-flash | minimal | 90s | → glm-4.6 | ⏳ |
| 2b | glm-4.5-flash | high | 270s | → glm-4.6 | ⏳ |
| 2c | glm-4.6 | high | 270s | No upgrade | ⏳ |

### **Test 3: Thinkdeep with Auto-Upgrade (Kimi)**
**Purpose:** Verify auto-upgrade from kimi-k2-0905-preview → kimi-thinking-preview

| Scenario | Model | Thinking Mode | Expected Timeout | Expected Upgrade | Status |
|----------|-------|---------------|------------------|------------------|--------|
| 3a | kimi-k2-0905-preview | minimal | 90s | → kimi-thinking-preview | ⏳ |
| 3b | kimi-k2-0905-preview | high | 270s | → kimi-thinking-preview | ⏳ |
| 3c | kimi-thinking-preview | high | 270s | No upgrade | ⏳ |

### **Test 4: Analyze Tool (Should Work with glm-4.6)**
**Purpose:** Verify analyze works with glm-4.6 (user reported it works)

| Scenario | Model | Expected Behavior | Status |
|----------|-------|------------------|--------|
| 4a | glm-4.6 | Works, completes successfully | ⏳ |
| 4b | glm-4.5-flash | Auto-upgrades to glm-4.6 | ⏳ |

### **Test 5: Codereview Tool (Should Work with glm-4.6)**
**Purpose:** Verify codereview works with glm-4.6 (user reported it works)

| Scenario | Model | Expected Behavior | Status |
|----------|-------|------------------|--------|
| 5a | glm-4.6 | Works, completes successfully | ⏳ |
| 5b | glm-4.5-flash | Auto-upgrades to glm-4.6 | ⏳ |

### **Test 6: Env Variable Respect**
**Purpose:** Verify implementation respects existing .env configuration

| Variable | Expected Behavior | Status |
|----------|------------------|--------|
| EXPERT_ANALYSIS_THINKING_MODE=minimal | Used as default thinking mode | ⏳ |
| DEFAULT_USE_ASSISTANT_MODEL=true | Expert analysis enabled | ⏳ |
| EXPERT_ANALYSIS_ENABLED=true | Expert analysis runs | ⏳ |
| EXPERT_ANALYSIS_TIMEOUT_SECS=180 | Used as base for adaptive timeout | ⏳ |

### **Test 7: Manual Override**
**Purpose:** Verify THINKDEEP_EXPERT_TIMEOUT_SECS override works

| Scenario | Env Var | Expected Timeout | Status |
|----------|---------|------------------|--------|
| 7a | THINKDEEP_EXPERT_TIMEOUT_SECS=60 | 60s (ignores adaptive) | ⏳ |
| 7b | Not set | Adaptive (90s-360s) | ⏳ |

---

## 📊 Test Execution Log

### Test Results:
*(To be filled during testing)*

---

## 🔍 Validation Checklist

- [ ] Auto-upgrade works for GLM (glm-4.5-flash → glm-4.6)
- [ ] Auto-upgrade works for Kimi (kimi-k2-0905-preview → kimi-thinking-preview)
- [ ] Adaptive timeout works (minimal=90s, high=270s, max=360s)
- [ ] Manual override works (THINKDEEP_EXPERT_TIMEOUT_SECS)
- [ ] No conflicts with EXPERT_ANALYSIS_THINKING_MODE
- [ ] No conflicts with DEFAULT_USE_ASSISTANT_MODEL
- [ ] No conflicts with EXPERT_ANALYSIS_ENABLED
- [ ] Logs show upgrade transparently
- [ ] Logs show timeout calculation
- [ ] All workflow tools work (thinkdeep, analyze, codereview, debug, etc.)

---

## 🚨 Known Issues

*(To be filled if issues found)*

---

## ✅ Sign-Off

- [ ] All tests passed
- [ ] Documentation updated
- [ ] Ready for Phase 2 QA validation
- [ ] Ready to commit


