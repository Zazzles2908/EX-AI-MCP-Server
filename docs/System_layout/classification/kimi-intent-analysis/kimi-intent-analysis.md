# Classification – Kimi Intent Analysis

## Purpose
Classify requests to steer toward Kimi when long context, multi-file processing, or cache reuse will reduce cost/latency.

## Current Implementation
- src/core/agentic/task_router.py: classifier scaffold; no direct Kimi biasing yet.

## Parameters
- LONG_MODEL_DEFAULT=kimi-k2-0711-preview (example)

## Integration Points
- RouterService: when task_type ∈ {long_context, multi_file, code_review_large}, bias Kimi.

## Status
- 🔧 Requires Adjustment: connect complexity scorer to classification; emit hints.

## Next Steps
1) Add token/file-size heuristics; emit _complexity_score.
2) Route to Kimi when thresholds exceed GLM fast path.

