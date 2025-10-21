# Thinking Mode - Corrected Understanding
**Date:** 2025-10-14 (14th October 2025)  
**Purpose:** Correct misunderstandings about thinking mode implementation  
**Status:** REFERENCE DOCUMENT

---

## 🚨 CRITICAL CORRECTION

### What I Got Wrong

**INCORRECT ASSUMPTION:**
> "GLM thinking mode uses categories like minimal/low/medium/high/max"

**CORRECT UNDERSTANDING:**
> GLM thinking mode is a simple boolean: `thinking: {"type": "enabled"}` or `thinking: {"type": "disabled"}`

**Source:** https://docs.z.ai/api-reference/llm/chat-completion

---

## GLM Thinking Mode (ZhipuAI)

### API Format

```json
{
  "model": "glm-4.6",
  "messages": [...],
  "thinking": {
    "type": "enabled"  // or "disabled"
  }
}
```

### Supported Models
- ✅ glm-4.6 (supports thinking)
- ✅ glm-4.5 (supports thinking)
- ❌ glm-4.5-flash (does NOT support thinking)
- ❌ glm-4.5-air (does NOT support thinking)

### Behavior
- **When enabled:** GLM-4.6 and GLM-4.5 automatically determine whether to think
- **GLM-4.5V:** Thinks compulsorily when enabled
- **Default:** enabled

### Response Format

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "...",
      "reasoning_content": "..."  // Reasoning process
    }
  }]
}
```

**Note:** GLM-4.5V may include `<think>` tags or `<|begin_of_box|>` markers in content.

---

## Kimi Thinking Mode (Moonshot)

### API Format

**NOT a parameter!** Use specific model:

```python
{
  "model": "kimi-thinking-preview",  # ← Model-based, not parameter!
  "messages": [...]
}
```

### Supported Models
- ✅ kimi-thinking-preview (thinking model)
- ❌ kimi-k2-0905-preview (does NOT support thinking)
- ❌ kimi-k2-turbo-preview (does NOT support thinking)

### Response Format (Streaming)

```python
# Extract reasoning from streaming response
if hasattr(choice.delta, "reasoning_content"):
    reasoning = getattr(choice.delta, "reasoning_content")
```

**Source:** https://platform.moonshot.ai/docs/guide/use-kimi-thinking-preview-model

---

## EXPERT_ANALYSIS Thinking Mode

### THIS IS DIFFERENT!

The `thinking_mode` parameter with categories (minimal/low/medium/high/max) is for **EXPERT_ANALYSIS**, NOT for GLM/Kimi API!

### Categories

```python
thinking_mode: Optional[str] = Field(
    default=None,
    description="Control the depth of expert analysis reasoning"
)
```

**Options:**
- `minimal`: 0.5% of model capacity, ~5-7s response time
- `low`: 8% of model capacity, ~8-10s response time
- `medium`: 33% of model capacity, ~15-20s response time
- `high`: 67% of model capacity, ~25-30s response time
- `max`: 100% of model capacity, ~40-60s response time

**Environment Variable:**
```env
EXPERT_ANALYSIS_THINKING_MODE=minimal  # Default for speed
```

**Where Used:**
- `tools/workflows/thinkdeep.py`
- `tools/workflows/expert_analysis.py`
- `tools/workflow/orchestration.py`

---

## Implementation Summary

### GLM Provider (src/providers/glm_chat.py)

```python
# Convert thinking_mode parameter to GLM API format
if 'thinking_mode' in kwargs:
    thinking_mode = kwargs.pop('thinking_mode', None)
    from .glm_config import get_capabilities
    caps = get_capabilities(model_name)
    if caps.supports_extended_thinking:
        # GLM uses simple boolean format
        payload["thinking"] = {"type": "enabled"}
        logger.debug(f"Enabled thinking mode for GLM model {model_name}")
    else:
        logger.debug(f"Model {model_name} does not support thinking mode")
```

### Kimi Provider (streaming/streaming_adapter.py)

```python
# Extract reasoning_content from kimi-thinking-preview
if extract_reasoning and hasattr(delta, "reasoning_content"):
    reasoning_piece = getattr(delta, "reasoning_content")
    if reasoning_piece:
        reasoning_parts.append(str(reasoning_piece))

# Format output
final_text = ""
if reasoning_parts:
    reasoning_text = "".join(reasoning_parts)
    final_text = f"[Reasoning]\n{reasoning_text}\n\n[Response]\n"
final_text += "".join(content_parts)
```

---

## Configuration

### Environment Variables

```env
# GLM Thinking Mode (boolean)
# No specific env var - controlled by thinking_mode parameter

# Kimi Thinking Mode (model-based)
KIMI_THINKING_MODEL=kimi-thinking-preview
KIMI_EXTRACT_REASONING=true  # Extract reasoning_content

# Expert Analysis Thinking Mode (categories)
EXPERT_ANALYSIS_THINKING_MODE=minimal  # minimal/low/medium/high/max
EXPERT_ANALYSIS_AUTO_UPGRADE=true  # Auto-upgrade to thinking models
```

### Model Auto-Upgrade

When `EXPERT_ANALYSIS_AUTO_UPGRADE=true`:
- GLM: `glm-4.5-flash` → `glm-4.6` (for thinking support)
- Kimi: `kimi-k2-0905-preview` → `kimi-thinking-preview` (for thinking support)

---

## Testing

### Test GLM Thinking Mode

```python
# Test with chat tool
{
  "tool": "chat",
  "arguments": {
    "prompt": "Explain quantum computing",
    "model": "glm-4.6",
    "thinking_mode": "enabled"  # Will be converted to thinking: {"type": "enabled"}
  }
}
```

### Test Kimi Thinking Mode

```python
# Test with chat tool
{
  "tool": "chat",
  "arguments": {
    "prompt": "Explain quantum computing",
    "model": "kimi-thinking-preview"  # Model-based thinking
  }
}
```

### Test Expert Analysis Thinking Mode

```python
# Test with thinkdeep tool
{
  "tool": "thinkdeep",
  "arguments": {
    "step": "Analyze this code for bugs",
    "thinking_mode": "high"  # Expert analysis depth
  }
}
```

---

## Common Mistakes

### ❌ WRONG: Passing thinking_mode categories to GLM
```python
payload["thinking_mode"] = "minimal"  # GLM doesn't understand this!
```

### ✅ CORRECT: Use boolean format for GLM
```python
payload["thinking"] = {"type": "enabled"}  # GLM API format
```

### ❌ WRONG: Passing thinking_mode to Kimi
```python
payload["thinking_mode"] = "enabled"  # Kimi doesn't have this parameter!
```

### ✅ CORRECT: Use kimi-thinking-preview model
```python
payload["model"] = "kimi-thinking-preview"  # Model-based thinking
```

### ❌ WRONG: Using thinking_mode for provider APIs
```python
# This is for EXPERT_ANALYSIS, not provider APIs!
thinking_mode = "minimal"
```

### ✅ CORRECT: Separate concerns
```python
# For GLM API: boolean
payload["thinking"] = {"type": "enabled"}

# For Kimi API: model selection
model = "kimi-thinking-preview"

# For Expert Analysis: categories
expert_thinking_mode = "minimal"  # or low/medium/high/max
```

---

## Summary

**Three Different "Thinking Modes":**

1. **GLM Thinking Mode:** Boolean (`enabled`/`disabled`)
   - API parameter: `thinking: {"type": "enabled"}`
   - Models: glm-4.6, glm-4.5

2. **Kimi Thinking Mode:** Model-based
   - Model selection: `kimi-thinking-preview`
   - Extract: `reasoning_content` from streaming

3. **Expert Analysis Thinking Mode:** Categories
   - Parameter: `thinking_mode` (minimal/low/medium/high/max)
   - Controls depth of expert analysis reasoning
   - NOT related to provider APIs!

**Key Takeaway:** Don't confuse expert analysis thinking_mode categories with provider API thinking modes!

---

**Last Updated:** 2025-10-14 (14th October 2025)  
**Status:** REFERENCE - Corrected understanding

