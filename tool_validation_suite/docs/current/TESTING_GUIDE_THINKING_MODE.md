# Testing Guide: thinking_mode Parameter Implementation

**Date**: 2025-10-09  
**Status**: ✅ IMPLEMENTATION COMPLETE - READY FOR MANUAL TESTING  
**Purpose**: Verify thinking_mode parameter works end-to-end with detailed logging

---

## What Was Implemented

### 1. Parameter Support
- Added `thinking_mode` parameter to workflow tool schemas
- Implemented hybrid fallback: parameter → env → default
- Added comprehensive logging to track execution flow

### 2. Detailed Logging Added

The implementation now includes **detailed logging** at every stage:

#### Thinking Mode Selection
```
🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=low | REQUEST_HAS_PARAM=True
✅ [THINKING_MODE] FINAL_MODE=low | VALID=True
```

#### Expert Analysis Start
```
🔥 [EXPERT_ANALYSIS_START] ========================================
🔥 [EXPERT_ANALYSIS_START] Tool: thinkdeep
🔥 [EXPERT_ANALYSIS_START] Model: glm-4.5-flash
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_START] Temperature: 0.3
🔥 [EXPERT_ANALYSIS_START] Prompt Length: 1234 chars
🔥 [EXPERT_ANALYSIS_START] Thinking Mode Selection Time: 0.001s
🔥 [EXPERT_ANALYSIS_START] ========================================
```

#### Expert Analysis Complete
```
🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================
🔥 [EXPERT_ANALYSIS_COMPLETE] Tool: thinkdeep
🔥 [EXPERT_ANALYSIS_COMPLETE] Model: glm-4.5-flash
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: 8.45s
🔥 [EXPERT_ANALYSIS_COMPLETE] Response Length: 2345 chars
🔥 [EXPERT_ANALYSIS_COMPLETE] ========================================
```

---

## Manual Testing Instructions

### Prerequisites
1. Server must be running (`.\scripts\ws_start.ps1 -Restart`)
2. `.env` must have `EXPERT_ANALYSIS_ENABLED=true`
3. `.env` must have `EXPERT_ANALYSIS_THINKING_MODE=minimal`

### Test 1: Default Thinking Mode (Env Fallback)

**Call**:
```python
thinkdeep(
    step="Analyze REST vs GraphQL APIs",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Testing default thinking mode from env",
    model="glm-4.5-flash"
    # No thinking_mode parameter - should use minimal from env
)
```

**Expected Logs**:
```
🎯 [THINKING_MODE] SOURCE=ENV_FALLBACK | MODE=minimal | ENV_VALUE=minimal | REQUEST_HAS_PARAM=False
✅ [THINKING_MODE] FINAL_MODE=minimal | VALID=True
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: minimal
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: minimal
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~5-7s
```

**Verification**:
- ✅ SOURCE shows ENV_FALLBACK
- ✅ MODE is minimal
- ✅ Duration is ~5-7 seconds
- ✅ Expert analysis actually ran

---

### Test 2: User-Provided thinking_mode=low

**Call**:
```python
thinkdeep(
    step="Analyze microservices vs monolithic architecture",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Testing user-provided thinking_mode=low",
    model="glm-4.5-flash",
    thinking_mode="low"  # User provides thinking mode
)
```

**Expected Logs**:
```
🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=low | REQUEST_HAS_PARAM=True
✅ [THINKING_MODE] FINAL_MODE=low | VALID=True
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: low
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~8-10s
```

**Verification**:
- ✅ SOURCE shows USER_PARAMETER
- ✅ MODE is low
- ✅ Duration is ~8-10 seconds (longer than minimal)
- ✅ Expert analysis actually ran

---

### Test 3: User-Provided thinking_mode=high

**Call**:
```python
thinkdeep(
    step="Deep analysis: Should we use event sourcing for a financial trading system?",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Testing user-provided thinking_mode=high for deep analysis",
    model="glm-4.5-flash",
    thinking_mode="high"  # User requests deep analysis
)
```

**Expected Logs**:
```
🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=high | REQUEST_HAS_PARAM=True
✅ [THINKING_MODE] FINAL_MODE=high | VALID=True
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: high
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: high
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~25-30s
```

**Verification**:
- ✅ SOURCE shows USER_PARAMETER
- ✅ MODE is high
- ✅ Duration is ~25-30 seconds (much longer than low)
- ✅ Expert analysis actually ran

---

### Test 4: Invalid Thinking Mode (Fallback)

**Call**:
```python
thinkdeep(
    step="Test invalid thinking mode",
    step_number=1,
    total_steps=1,
    next_step_required=False,
    findings="Testing invalid thinking_mode - should fall back to minimal",
    model="glm-4.5-flash",
    thinking_mode="invalid"  # Invalid mode
)
```

**Expected Logs**:
```
🎯 [THINKING_MODE] SOURCE=USER_PARAMETER | MODE=invalid | REQUEST_HAS_PARAM=True
❌ [THINKING_MODE] INVALID_MODE=invalid | FALLING_BACK_TO=minimal
✅ [THINKING_MODE] FINAL_MODE=minimal | VALID=True
🔥 [EXPERT_ANALYSIS_START] Thinking Mode: minimal
🔥 [EXPERT_ANALYSIS_COMPLETE] Thinking Mode: minimal
🔥 [EXPERT_ANALYSIS_COMPLETE] Total Duration: ~5-7s
```

**Verification**:
- ✅ Invalid mode detected
- ✅ Fallback to minimal
- ✅ Duration is ~5-7 seconds
- ✅ Expert analysis still ran successfully

---

## Where to Find Logs

### Option 1: Server Terminal Output
The logs will appear in the terminal where the server is running (with 🎯 and 🔥 emojis for easy spotting).

### Option 2: Log Files
Check these log files:
- `logs/server.log` - Main server logs
- `logs/mcp_activity.log` - MCP activity logs
- Terminal output from `.\scripts\ws_start.ps1`

### Option 3: Search for Specific Markers
Search for these strings in logs:
- `THINKING_MODE` - Shows thinking mode selection
- `EXPERT_ANALYSIS_START` - Shows when expert analysis begins
- `EXPERT_ANALYSIS_COMPLETE` - Shows when expert analysis finishes

---

## Success Criteria

For the implementation to be considered working, you must verify:

### 1. Parameter Recognition
- [ ] User-provided `thinking_mode` parameter is recognized
- [ ] Env fallback works when parameter not provided
- [ ] Invalid modes fall back to minimal with warning

### 2. Execution Flow
- [ ] Expert analysis is actually called (not skipped)
- [ ] Thinking mode is passed to the provider
- [ ] Provider call completes successfully

### 3. Performance Variation
- [ ] `minimal` mode: ~5-7 seconds
- [ ] `low` mode: ~8-10 seconds
- [ ] `high` mode: ~25-30 seconds
- [ ] Duration increases with thinking mode depth

### 4. Logging Visibility
- [ ] All 🎯 THINKING_MODE logs appear
- [ ] All 🔥 EXPERT_ANALYSIS logs appear
- [ ] Logs show correct mode and source
- [ ] Logs show actual duration

---

## Troubleshooting

### Issue: Expert analysis not running (0.00s duration)
**Cause**: `EXPERT_ANALYSIS_ENABLED=false` in .env  
**Fix**: Set `EXPERT_ANALYSIS_ENABLED=true` and restart server

### Issue: No thinking mode logs appear
**Cause**: Logs not being written or server not restarted  
**Fix**: Restart server with `.\scripts\ws_start.ps1 -Restart`

### Issue: All tests use same duration
**Cause**: Thinking mode not being passed to provider  
**Fix**: Check logs for "🔥 [EXPERT_ANALYSIS_START] Thinking Mode: X"

### Issue: Logs show wrong thinking mode
**Cause**: Parameter not being passed correctly  
**Fix**: Verify parameter name is exactly `thinking_mode` (lowercase, underscore)

---

## Next Steps After Testing

Once manual testing confirms everything works:

1. **Document results** - Record actual durations for each mode
2. **Apply to other tools** - Add thinking_mode to debug, analyze, codereview
3. **Update user documentation** - Add examples to tool docs
4. **Create automated tests** - Build integration tests for CI/CD

---

## Summary

The `thinking_mode` parameter implementation is **code-complete** with **comprehensive logging** added. Manual testing through the MCP interface will verify:

✅ Parameter is recognized and used  
✅ Env fallback works correctly  
✅ Expert analysis actually runs  
✅ Thinking mode affects performance  
✅ Logging shows internal execution flow  

The detailed logging (🎯 and 🔥 markers) makes it easy to verify the implementation is working as expected.

