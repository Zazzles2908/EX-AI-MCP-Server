# AI Manager – Routing Logic (Kimi integration)

## Purpose
Describe how the manager routes requests when Kimi is selected (or preferred) and how long‑context/caching and streaming policies influence choice.

## Current Implementation (code paths)
- src/router/service.py: RouterService biases selection when task_type/complexity favor long‑context provider.
- src/providers/registry.py: Kimi provider availability/cost/capabilities are considered alongside GLM models.
- src/providers/kimi.py: chat_completions_create with idempotency + context cache; generate_content wrapper.

## Parameters (env/config)
- LONG_MODEL_DEFAULT (e.g., kimi‑k2‑0711‑preview, moonshot‑v1‑128k)
- KIMI_STREAM_ENABLED (proposed), KIMI_DEFAULT_READ_TIMEOUT_SECS
- KIMI_CACHE_TOKEN_TTL_SECS, KIMI_CACHE_TOKEN_LRU_MAX

## Integration Points
- Classification/Complexity: long files, large token estimate → bias toward Kimi.
- Workflows: pass _session_id/_call_key/_tool_name to enable cache reuse.
- Streaming (optional): enable when KIMI_STREAM_ENABLED=true.

## Status Assessment
- 🔧 Requires Adjustment: Routing hints not consistently fed; streaming disabled by default.

## Next Steps
1) Feed RouterService with task_type + complexity scorer outputs.
2) Add env‑gated streaming and tests.
3) Ensure RoutePlan includes cache/stream context when Kimi path is chosen.

