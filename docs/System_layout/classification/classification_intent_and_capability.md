# Classification – Intent and Capability Analysis

## Purpose
Identify task intent (file/QA/analytics, web/real‑time/reports, general workflows) and required capabilities (web_search, long_context, streaming, multimodal) to guide routing.

## Current Implementation (code paths)
- src/core/agentic/task_router.py: IntelligentTaskRouter(TaskType) with simple heuristics (multimodal check, ~token estimate, long_context threshold).
- Not currently invoked in request_handler; no complexity score module.

## Parameters
- Token threshold: hardcoded 128_000 in task_router.classify().

## Dependencies
- None at runtime; designed to be deterministic and unit‑testable.

## Integration Points
- Boundary: src/server/handlers/request_handler.py should call IntelligentTaskRouter.classify() and a new complexity scorer; persist into arguments (e.g., _agentic_task_type, _complexity_score, _required_capabilities).
- RouterService.accept_agentic_hint() can consume platform/task_type hints.

## Status Assessment
- ❌ Missing/Incomplete: Classifier exists but is not wired into runtime; no complexity scoring nor capability matrix.

## Implementation Notes
- Add utils/complexity.py to compute score and flags: token_estimate, file_count/size, image presence, tool depth, latency target.

## Next Steps
1) Wire IntelligentTaskRouter into request_handler before model resolution.
2) Implement complexity scorer and pass hint to RouterService.choose_model_with_hint().
3) Define capability matrix (min context window, web_search, streaming) for pruning fallback candidates.

