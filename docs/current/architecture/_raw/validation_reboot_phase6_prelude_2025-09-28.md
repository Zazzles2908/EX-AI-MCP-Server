# Validation — Server Restart and Import Fixes (Prelude to Phase 6)

## Commands
- Restart: scripts/ws_start.ps1 -Restart (non-blocking)
- Status: scripts/ws/ws_status.py → running
- Probe: scripts/diagnostics/ws_probe.py → exit 0

## Evidence
```
[probe] tools (...): [... 'glm_web_search', 'kimi_intent_analysis', ...]
[probe] glm_web_search preview: {... JSON ...}
[probe] kimi_intent_analysis preview: {"needs_websearch": true, "recommended_model": "glm-4.5-flash", ...}
```

## Outcome
- Server restarted cleanly; imports resolved.
- Pylance-targeted issues addressed via type-ignore and TYPE_CHECKING guards.
- Ready to proceed to Phase 6 (streaming stabilization).

