# Augment Review 02 – Change Log (2025-09-26)

## Summary
- Flipped EXAI_WS_COMPAT_TEXT default to OFF (root-cause-first policy).
- Added dedicated JSONL handler for router decisions (logs/router.jsonl).
- No behavior changes to routing policy; added observability only.

## Files Touched
- .env.example
  - Set `EXAI_WS_COMPAT_TEXT=false` (with caution note)
- server.py
  - setup_logging(): added RotatingFileHandler for `router` logger writing pure JSON lines to `.\logs\router.jsonl`.

## Rationale
- Aligns with Deepagent plan Phase 1 (observability) and your policy to avoid enabling compat flags until root cause is proven.
- Router JSONL creates high-signal, machine-readable artifacts for decisions without altering runtime logic.

## Next Steps (Phase 1)
- Consider adding lightweight counters (decisions, errors, fallbacks) to metrics.jsonl via utils/observability.
- Validate WS daemon end-to-end with unpredictable prompts and record real outputs (EXAI-WS MCP).
- Draft CI stub (lint + unit + secret scan) and commit on chore/registry-switch-and-docfix.

## Validation Notes
- No dependencies added; safe change. Will verify log file emission during next WS daemon run.

