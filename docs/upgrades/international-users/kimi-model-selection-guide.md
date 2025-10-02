# Kimi Model Selection Guide

**Document Type:** Model Selection Guide  
**Status:** Active  
**Created:** 2025-10-02  
**Last Updated:** 2025-10-02  
**Purpose:** Definitive guide for choosing the right Kimi model for EX-AI-MCP-Server

---

## Executive Summary

Moonshot AI offers multiple Kimi model generations (K1, K1.5, K2) with different capabilities and trade-offs. This guide provides research-backed recommendations for model selection in production systems.

**Key Recommendation:** Use **`kimi-k2-0905-preview`** for EX-AI-MCP-Server production deployment.

**Rationale:**
- ✅ Latest K2 generation with best agentic/tool-use capabilities
- ✅ Specifically tuned for coding, tool-calling, and multi-step instructions
- ✅ Version pinning ensures stability (won't auto-update)
- ✅ 256K context window (largest available)
- ✅ Enhanced coding capabilities (September 2025 update)
- ✅ Best for MCP server use case (tool integration, code generation, reasoning)

---

## Model Generations Overview

### K1 (Original Generation)

**Status:** Legacy  
**Recommendation:** Not recommended for new deployments

**Characteristics:**
- Original Kimi model generation
- Smaller context window
- Basic capabilities
- Superseded by K1.5 and K2

**Use Cases:** None (use K1.5 or K2 instead)

---

### K1.5 (Multimodal Reasoning)

**Release Date:** ~January 2025  
**Model Name:** `kimi-k1.5-latest`

**Characteristics:**
- Multimodal reasoning capabilities
- Strong comprehension in structured documents
- Good conversational AI
- SOTA reasoning performance (at time of release)
- Trained with reinforcement learning

**Capabilities:**
- ✅ Multimodal input (text, images)
- ✅ Strong reasoning
- ✅ Document comprehension
- ✅ Conversational AI

**Limitations:**
- ❌ Not optimized for agentic tasks
- ❌ Not optimized for tool use
- ❌ Smaller context window than K2
- ❌ Superseded by K2 for most use cases

**Use Cases:**
- Multimodal reasoning tasks
- Document analysis with images
- When K2 is unavailable

**Recommendation:** Use K2 instead unless multimodal input is required

---

### K2 (Agentic Intelligence)

**Release Date:** July 11, 2025  
**Latest Update:** September 5, 2025 (kimi-k2-0905-preview)

**Model Names:**
- `kimi-k2-0905-preview` (September 5, 2025 - **RECOMMENDED**)
- `kimi-k2-0711-preview` (July 11, 2025 - original K2)

**Architecture:**
- 1 trillion total parameters
- 32 billion active parameters (MoE - Mixture of Experts)
- 256K context window

**Characteristics:**
- **"Agentic Intelligence"** - specifically designed for autonomous problem-solving
- Specifically tuned for: **writing and debugging code**, **controlling tools**, **following multi-step instructions**
- SOTA on SWE Bench Verified, Tau2 & AceBench (among open models)
- Enhanced coding capabilities (especially front-end)
- Improved tool-calling integration
- Context length: 256K tokens

**Capabilities:**
- ✅ **Superior tool use** (best for MCP servers)
- ✅ **Advanced coding** (code generation, debugging, explanation)
- ✅ **Multi-step reasoning** (complex task decomposition)
- ✅ **Autonomous problem-solving** (agentic workflows)
- ✅ **256K context window** (largest available)
- ✅ **Enhanced tool-calling** (native MCP support)

**Trade-offs:**
- ⚠️ Slower response speed than K1/K1.5 (per Moonshot docs)
- ⚠️ Higher computational cost (MoE architecture)

**Use Cases:**
- ✅ **MCP servers** (tool integration, function calling)
- ✅ **Code generation and review** (specifically tuned)
- ✅ **Agentic workflows** (multi-step tasks)
- ✅ **Complex reasoning** (problem decomposition)
- ✅ **Long-context tasks** (256K window)

**Recommendation:** **PRIMARY CHOICE** for EX-AI-MCP-Server

---

## kimi-latest vs Version Pinning

### kimi-latest

**Type:** Alias/pointer to current recommended model  
**Behavior:** May auto-update to newer models

**Advantages:**
- ✅ Always uses latest recommended model
- ✅ Automatic improvements
- ✅ Simple configuration

**Disadvantages:**
- ❌ **Version instability** - may change without notice
- ❌ **Unpredictable behavior** - updates may change responses
- ❌ **Testing challenges** - can't reproduce exact behavior
- ❌ **Production risk** - unexpected changes in production

**Use Cases:**
- Development/testing environments
- Rapid prototyping
- When latest features are critical

**Recommendation:** **NOT RECOMMENDED** for production systems

---

### Version Pinning (kimi-k2-0905-preview)

**Type:** Specific model version  
**Behavior:** Fixed version, won't auto-update

**Advantages:**
- ✅ **Version stability** - guaranteed consistent behavior
- ✅ **Reproducible results** - same model always
- ✅ **Controlled updates** - update when ready
- ✅ **Production safety** - no unexpected changes
- ✅ **Testing reliability** - can validate exact version

**Disadvantages:**
- ❌ Manual updates required for new features
- ❌ May miss automatic improvements

**Use Cases:**
- ✅ **Production systems** (stability critical)
- ✅ **Regulated environments** (version control required)
- ✅ **Long-running deployments** (consistency needed)

**Recommendation:** **REQUIRED** for production systems

---

## Pricing Comparison

**Source:** TechTarget article (July 2025)

### Kimi K2 Pricing

- **Input:** $0.60 per million tokens
- **Output:** $2.50 per million tokens

**Value Proposition:**
- "1/5th the price of comparable models" (Claude/GPT-4)
- Significantly cheaper than Western alternatives
- Best price/performance ratio for agentic tasks

### Cost Comparison

| Model | Input ($/M) | Output ($/M) | Context Window |
|-------|-------------|--------------|----------------|
| **Kimi K2** | $0.60 | $2.50 | 256K |
| Claude Sonnet 4 | $3.00 | $15.00 | 200K |
| GPT-4 Turbo | $10.00 | $30.00 | 128K |
| GLM-4.6 | $0.60 | $2.20 | 200K |

**Key Insights:**
- Kimi K2 and GLM-4.6 have similar input pricing ($0.60/M)
- Kimi K2 output slightly more expensive than GLM-4.6 ($2.50 vs $2.20)
- Both are 1/5th the cost of Claude Sonnet 4
- Kimi K2 has largest context window (256K)

---

## Model Selection Decision Tree

```
START: What is your use case?

├─ Need multimodal input (images)?
│  └─ YES → Use kimi-k1.5-latest
│  └─ NO → Continue
│
├─ Need tool use / function calling?
│  └─ YES → Use kimi-k2-0905-preview ✅
│  └─ NO → Continue
│
├─ Need code generation / debugging?
│  └─ YES → Use kimi-k2-0905-preview ✅
│  └─ NO → Continue
│
├─ Need agentic workflows / multi-step reasoning?
│  └─ YES → Use kimi-k2-0905-preview ✅
│  └─ NO → Continue
│
├─ Need long context (>128K tokens)?
│  └─ YES → Use kimi-k2-0905-preview ✅
│  └─ NO → Continue
│
├─ Need fastest response speed?
│  └─ YES → Use kimi-k1.5-latest
│  └─ NO → Use kimi-k2-0905-preview ✅

DEFAULT: Use kimi-k2-0905-preview ✅
```

---

## Recommendations for EX-AI-MCP-Server

### Production Deployment

**Model:** `kimi-k2-0905-preview`

**Rationale:**
1. **Tool Use:** K2 is specifically designed for tool integration (MCP server use case)
2. **Coding:** Enhanced coding capabilities match server's code generation needs
3. **Agentic:** Multi-step reasoning for complex workflows
4. **Context:** 256K window for large codebase analysis
5. **Stability:** Version pinning ensures production reliability
6. **Latest:** September 2025 update has enhanced tool-calling

**Configuration:**
```bash
# .env
KIMI_MODEL=kimi-k2-0905-preview
```

---

### Development/Testing

**Model:** `kimi-k2-0905-preview` (same as production)

**Rationale:**
- Development should match production for accurate testing
- Version pinning ensures reproducible results
- Can test exact production behavior

**Alternative:** `kimi-latest` for rapid prototyping only

---

### Cost Optimization

**Strategy:** Use Kimi K2 for complex tasks, GLM-4.6 for simple tasks

**Routing Logic:**
```python
if task_requires_tool_use or task_requires_coding:
    model = "kimi-k2-0905-preview"  # Best for agentic tasks
elif task_requires_long_context:
    model = "kimi-k2-0905-preview"  # 256K context
else:
    model = "glm-4.6"  # Cheaper output ($2.20 vs $2.50)
```

**Cost Savings:**
- Use GLM-4.6 for simple chat/reasoning (12% cheaper output)
- Use Kimi K2 for tool use/coding (better capabilities)

---

## Migration from kimi-latest

### Current State (Incorrect)

Many Wave 1 documents reference `kimi-latest`:
- docs/guides/parameter-reference.md
- docs/guides/query-examples.md
- docs/guides/tool-selection-guide.md
- Other documentation

### Correct State

**All references should use:** `kimi-k2-0905-preview`

### Migration Steps

1. **Audit all documentation** for `kimi-latest` references
2. **Replace with** `kimi-k2-0905-preview`
3. **Add context** about version pinning rationale
4. **Update examples** to show correct model selection
5. **Document trade-offs** (stability vs auto-updates)

---

## Official Moonshot Guidance

**Source:** platform.moonshot.ai/docs/guide/agent-support

> "Model Selection: If response speed is not a high priority, you can choose to use the kimi-k2-0905-preview or kimi-k2-0711-preview model, which..."

**Interpretation:**
- K2 models trade speed for better capabilities
- For MCP servers, capabilities > speed
- K2-0905 is latest with enhanced features

**Recommendation:** Accept speed trade-off for better tool use and coding

---

## Version History

### kimi-k2-0711-preview (July 11, 2025)

- Original K2 release
- 1T parameters, 32B active (MoE)
- 256K context window
- Agentic intelligence capabilities

### kimi-k2-0905-preview (September 5, 2025) ✅ CURRENT

- Enhanced coding capabilities (especially front-end)
- Improved tool-calling integration
- Context length extended to 256K tokens
- Better integration with MCP

**Recommendation:** Use 0905 (latest) over 0711

---

## Conclusion

**Definitive Recommendation for EX-AI-MCP-Server:**

✅ **Production:** `kimi-k2-0905-preview`  
✅ **Development:** `kimi-k2-0905-preview`  
✅ **Testing:** `kimi-k2-0905-preview`

**Rationale:**
- Best for tool use (MCP server use case)
- Best for coding (code generation/review)
- Best for agentic workflows (multi-step reasoning)
- Largest context window (256K)
- Version stability (production safety)
- Latest features (September 2025 update)

**Do NOT use:**
- ❌ `kimi-latest` (version instability)
- ❌ `kimi-k1.5-latest` (superseded by K2)
- ❌ `kimi-k2-0711-preview` (use 0905 instead)

---

**Document Status:** ✅ COMPLETE  
**Next Steps:** Audit and update all Wave 1 documentation to use `kimi-k2-0905-preview`

