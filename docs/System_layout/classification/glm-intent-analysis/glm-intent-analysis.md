# Classification – GLM Intent Analysis

## Purpose
Classify requests to guide GLM-optimized routing (fast/inexpensive paths, native web search usage).

## Current Implementation
- src/core/agentic/task_router.py: IntelligentTaskRouter.classify() scaffold exists; not consistently invoked.

## Parameters
- ENABLE_INTELLIGENT_SELECTION=true|false

## Integration Points
- RouterService.choose_model_with_hint(): feed platform=GLM when classification favors GLM (short prompts, web_search allowed).

## Status
- 🔧 Requires Adjustment: wire classifier at boundary; add web_search intent detection.

## Next Steps
1) Invoke classifier in request_handler; attach _agentic_task_type.
2) Add heuristics/prompt-based detection for browsing needs; bias GLM.

