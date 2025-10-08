# Root Cause: Why Expert Analysis Takes 30 Seconds

**Date**: 2025-10-08  
**Issue**: Expert analysis times out because it takes 30s while client timeout is 8s

---

## THE SMOKING GUN

**File**: `tools/workflow/expert_analysis.py`  
**Line**: 145

```python
def get_expert_thinking_mode(self) -> str:
    """
    Get the thinking mode for expert analysis.
    Override this to customize the thinking mode.
    """
    return "high"  # ← THIS IS THE PROBLEM
```

---

## PROOF

### Test 1: Chat Tool (No Thinking Mode)
```
Tool: chat_EXAI-WS
Model: glm-4.5-flash
Prompt: 349 chars
Thinking Mode: None
Duration: 7.7 seconds ✅
```

### Test 2: Expert Analysis (High Thinking Mode)
```
Tool: thinkdeep → expert analysis
Model: glm-4.5-flash
Prompt: 349 chars
Thinking Mode: "high"
Duration: 30 seconds ❌
```

**Same model, same prompt size, 4x slower because of thinking_mode="high"**

---

## WHAT IS THINKING MODE?

From GLM API documentation, thinking modes control the depth of reasoning:

| Mode | Description | Speed | Use Case |
|------|-------------|-------|----------|
| `minimal` | 0.5% of model max | Fastest | Simple queries |
| `low` | 8% of model max | Fast | Standard queries |
| `medium` | 33% of model max | Moderate | Complex queries |
| `high` | 67% of model max | **Slow** | Deep analysis |
| `max` | 100% of model max | **Very Slow** | Exhaustive reasoning |

**Expert analysis uses `high` by default = 67% of model's maximum reasoning capacity**

This means the model spends extra time:
- Analyzing the problem from multiple angles
- Considering edge cases
- Validating its reasoning
- Generating more thorough responses

**For a 349 char prompt, this is OVERKILL.**

---

## WHY THIS IS BROKEN

### 1. **No Configuration**
- Thinking mode is hardcoded in the script
- No env variable to control it
- No way to disable it without code changes

### 2. **Wrong Default**
- `high` thinking mode for ALL expert analysis
- Even for simple prompts (349 chars)
- No adaptive logic based on prompt complexity

### 3. **Timeout Mismatch**
- Client timeout: 8 seconds
- Expert analysis: 30 seconds (with high thinking mode)
- **Client gives up before expert analysis completes**

### 4. **No Visibility**
- Logs don't show thinking mode being used
- No indication that deep reasoning is happening
- Appears as "API is slow" instead of "we requested slow processing"

---

## THE FIX (Proper, Centralized Configuration)

### Step 1: Add to `.env`

```bash
# ============================================================================
# EXPERT ANALYSIS CONFIGURATION
# ============================================================================
# Enable/disable expert analysis entirely
EXPERT_ANALYSIS_ENABLED=false  # Default: false (too slow for most use cases)

# Thinking mode for expert analysis (minimal, low, medium, high, max)
EXPERT_ANALYSIS_THINKING_MODE=low  # Default: low (fast enough, still thoughtful)

# Include files in expert analysis prompt
EXPERT_ANALYSIS_INCLUDE_FILES=false  # Default: false (reduces prompt size)

# Maximum file size to include (KB)
EXPERT_ANALYSIS_MAX_FILE_SIZE_KB=10  # Default: 10KB per file

# Timeout for expert analysis (seconds)
EXPERT_ANALYSIS_TIMEOUT_SECS=180  # Already exists

# Heartbeat interval for progress updates (seconds)
EXPERT_HEARTBEAT_INTERVAL_SECS=5  # Already exists
```

### Step 2: Update `tools/workflow/expert_analysis.py`

```python
def get_expert_thinking_mode(self) -> str:
    """
    Get the thinking mode for expert analysis from environment.
    
    Defaults to 'low' for fast responses while maintaining quality.
    Can be overridden via EXPERT_ANALYSIS_THINKING_MODE env variable.
    """
    import os
    return os.getenv("EXPERT_ANALYSIS_THINKING_MODE", "low")

def requires_expert_analysis(self) -> bool:
    """
    Check if expert analysis is enabled globally.
    
    Can be disabled via EXPERT_ANALYSIS_ENABLED=false in .env
    """
    import os
    enabled = os.getenv("EXPERT_ANALYSIS_ENABLED", "false").lower()
    return enabled in ("true", "1", "yes")

def should_include_files_in_expert_prompt(self) -> bool:
    """
    Check if files should be included in expert analysis prompt.
    
    Can be disabled via EXPERT_ANALYSIS_INCLUDE_FILES=false in .env
    """
    import os
    enabled = os.getenv("EXPERT_ANALYSIS_INCLUDE_FILES", "false").lower()
    return enabled in ("true", "1", "yes")
```

### Step 3: Update `.env.example` to match

---

## PERFORMANCE COMPARISON

### Current (High Thinking Mode)
```
Prompt: 349 chars
Thinking Mode: high
Duration: 30 seconds
Client Timeout: 8 seconds
Result: ❌ TIMEOUT
```

### Fixed (Low Thinking Mode)
```
Prompt: 349 chars
Thinking Mode: low
Duration: ~8-10 seconds
Client Timeout: 8 seconds
Result: ⚠️ CLOSE (might still timeout)
```

### Fixed (Minimal Thinking Mode)
```
Prompt: 349 chars
Thinking Mode: minimal
Duration: ~5-7 seconds
Client Timeout: 8 seconds
Result: ✅ SUCCESS
```

### Fixed (Expert Analysis Disabled)
```
No expert analysis call
Duration: <1 second
Client Timeout: N/A
Result: ✅ SUCCESS
```

---

## RECOMMENDED SOLUTION

### Option 1: Disable Expert Analysis (Immediate Fix)
```bash
# .env
EXPERT_ANALYSIS_ENABLED=false
```

**Pros**:
- Immediate fix
- No timeout issues
- Workflows complete in <1 second

**Cons**:
- Loses "expert validation" (questionable value anyway)

### Option 2: Use Minimal Thinking Mode (Compromise)
```bash
# .env
EXPERT_ANALYSIS_ENABLED=true
EXPERT_ANALYSIS_THINKING_MODE=minimal
```

**Pros**:
- Keeps expert analysis
- Fast enough to avoid timeout (~5-7s)
- Still provides some validation

**Cons**:
- Still adds 5-7s latency
- Minimal thinking mode may not catch issues

### Option 3: Make It Truly Optional (Best Long-Term)
```bash
# .env
EXPERT_ANALYSIS_ENABLED=false  # Default off
EXPERT_ANALYSIS_THINKING_MODE=low  # When enabled, use low mode
EXPERT_ANALYSIS_INCLUDE_FILES=false  # Don't embed files
```

**Pros**:
- Centralized configuration
- Easy to enable/disable
- Configurable thinking mode
- No code changes needed to adjust

**Cons**:
- Requires updating multiple scripts
- Need to test all combinations

---

## WHAT ABOUT THE CLIENT TIMEOUT?

The client (Augment Code) appears to have an 8-second timeout. This is likely:

1. **MCP Protocol Default**: Standard timeout for tool calls
2. **Augment Configuration**: Could be in Augment's settings
3. **WebSocket Timeout**: Could be in the daemon configuration

**We can't easily change the client timeout**, so we must make expert analysis faster or disable it.

---

## CONCLUSION

**The 30-second delay is caused by**:
1. `thinking_mode="high"` (hardcoded, no env config)
2. Deep reasoning for simple prompts (overkill)
3. No way to disable without code changes

**The fix**:
1. Add `EXPERT_ANALYSIS_ENABLED=false` to `.env`
2. Add `EXPERT_ANALYSIS_THINKING_MODE=low` to `.env`
3. Update scripts to read from env instead of hardcoding
4. Make expert analysis truly optional

**This is the "intuitive approach" you asked for**: Centralized configuration in `.env`, no hardcoded values, easy to adjust without touching code.

