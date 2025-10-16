---
type: "agent_requested"
description: "EXAI-MCP Docker Architecture and Usage Guidelines"
---

# Augment Code: Rules and User Guidelines for EXAI‑MCP Usage (Default at Every Prompt)

These guidelines standardize how Augment Code interacts with EXAI‑MCP. They are concise, adoption‑ready, and align with our routing, logging, and safety practices.

## 🐳 CRITICAL: EXAI Architecture (Docker-based)
- **EXAI runs in a Docker container**, NOT as a direct terminal command
- **Access via WebSocket daemon** at `ws://127.0.0.1:8079`
- **MCP Configuration**: Uses `Daemon/mcp-config.augmentcode.json` with stdio transport to `scripts/run_ws_shim.py`
- **Restart command**: `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart`
- **Never use direct Python execution** - always go through the WebSocket shim

## 1) Always use EXAI‑MCP by default
- All prompts should go through EXAI‑MCP tools unless explicitly requested otherwise.
- Prefer workflow tools for multi‑step tasks (thinkdeep, analyze, codereview, debug, planner, refactor, tracer, testgen, precommit, secaudit).
- For quick one‑shot operations, simple tools (chat, status, listmodels, version) are acceptable.

## 2) Required workflow fields (multi‑step tools)
Always include the following for workflow tools:
- `step`: current step description
- `step_number`: integer starting at 1
- `total_steps`: best current estimate (update as needed)
- `next_step_required`: boolean
- `findings`: brief evidence/progress so far

Continuation handling:
- Persist and pass `continuation_id` across calls. The client wrapper auto‑propagates it, but tools should preserve it when present.
- **CRITICAL**: Continue conversation IDs for context preservation (e.g., `debb44af-15b9-456d-9b88-6a2519f81427`)

## 3) Model Selection and Routing
**Default Model Preferences:**
- **GLM-4.6**: Default for important calls, web search, and comprehensive analysis
- **GLM-4.5-flash**: For simple, quick operations and routine tasks
- **Kimi K2 (kimi-k2-0905-preview)**: For deep reasoning, long-context, and quality analysis
- **Auto routing**: Use `model: auto` to let the router decide based on context

**Routing hints and cues:**
- `estimated_tokens`: provide when large (the client wrapper injects an estimate). Thresholds:
  - `> 48k` → prefer Kimi/Moonshot (long‑context)
  - `> 128k` → strongly prefer Kimi/Moonshot
- `use_websearch: true` and/or include URLs/time‑sensitive wording to bias GLM browsing path.
- Vision/multimodal cues bias to GLM unless overridden.

## 4) Lean tool expectations
- Only lean tools are visible when `LEAN_MODE=true, STRICT_LEAN=true`.
- Do not assume optional tools are available; check tool listings where necessary.

## 5) Logging and verification
- Always check `MCP_CALL_SUMMARY` in logs for: resolved model, token counts, duration.
- For failures, capture the top error lines and any `Traceback` entries in the activity log.
- Prefer small, safe verification runs (tests/linters/builds) over broad or stateful operations.

## 6) Safety and cost practices
- Never commit secrets. Use `.env`; document placeholders in `.env.example`.
- Expert second‑pass (external validation) is OFF by default; enable per‑call only when needed.
- Keep runs efficient: minimal input that preserves intent; batch independent read‑only calls.

## 7) Windows and environment notes
- On Windows PowerShell, chain commands with `;` (not `&&`).
- Ensure `.env` is loaded by your launch entrypoint so provider keys and routing toggles are active.

## 8) Concurrency and batching guidance
- Use parallel tool calls for independent reads (view, codebase retrieval, web search).
- Sequence dependent or conflicting edits (same file/region changes).

## 09) Escalation policy
- If output truncates or context overflows: raise `estimated_tokens`, re‑run with long‑context preference.
- If information requires live sources: set `use_websearch: true` and include URLs/time cues.
- For high‑risk changes: enable expert second‑pass and include evidence for decisions.

## 10) Authoring guidance for commits/PRs
- Commit format: `<type>: <scope> <summary>`; keep subject concise; use body for details.



