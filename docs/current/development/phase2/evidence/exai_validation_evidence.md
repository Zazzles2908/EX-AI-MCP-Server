# EXAI-MCP Phase 1 Validation Evidence (Raw)

(RELLOCATED COPY)

[Original path prior to reorg: docs/augmentcode_phase2/exai_validation_evidence.md]

Timestamp (UTC): 2025-09-28

This file indexes raw artifacts produced by automated validation runs. All artifacts are saved verbatim; see linked JSON/JSONL/MD files for full content.

## Commands Executed

1) Start WS daemon (non-blocking)
- powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\ws_start.ps1 -Restart

2) MCP stdio tool sweep
- .venv\\Scripts\\python.exe scripts\\mcp_tool_sweep.py
- Outputs:
  - docs/mcp_tool_sweep_report.md
  - docs/sweep_reports/2025-09-29_08-57-17/mcp_tool_sweep_report.md

3) WebSocket probe (tools discovery, GLM web search, Kimi streaming)
- .venv\\Scripts\\python.exe scripts\\diagnostics\\ws_probe.py
- Raw artifacts (saved automatically under docs/System_layout/_raw):
  - ws_probe_glm_web_search_glm_news_recent_YYYYMMDDTHHMMSSZ.json
  - ws_probe_glm_web_search_tech_python_asyncio_YYYYMMDDTHHMMSSZ.json
  - ws_probe_kimi_intent_analysis_simple_math_YYYYMMDDTHHMMSSZ.json
  - ws_probe_kimi_intent_analysis_current_events_YYYYMMDDTHHMMSSZ.json
  - ws_probe_kimi_intent_analysis_domain_programming_YYYYMMDDTHHMMSSZ.json
  - ws_probe_kimi_stream_bullets_YYYYMMDDTHHMMSSZ.json (+ .jsonl trace)
  - ws_probe_glm_stream_paragraph_bullets_YYYYMMDDTHHMMSSZ.json (+ .jsonl trace)

4) Stdio chat context + path validation test
- .venv\\Scripts\\python.exe scripts\\diagnostics\\mcp_chat_context_test.py
- Output (examples):
  - docs/augmentcode_phase2/raw/mcp_chat_context_ctx-ce818efc.json
  - docs/augmentcode_phase2/raw/mcp_chat_context_ctx-0b5ab7aa.json

## Key Findings (Observed Behavior)
- Tool registry discovery: WS probe reported tools (~23 on WS) and stdio sweep reported 27 tools (stdio exposes additional internal/diagnostic tools)
- GLM web search: Validated; evidence in ws_probe_glm_web_search_*.json
- Kimi streaming: Streaming chunks captured; evidence in ws_probe_kimi_stream_bullets_*.json and .jsonl
- GLM streaming via chat: continuation_offer observed
- Chat path validation: Absolute path acceptance, relative path rejection (with clear error)
- Kimi upload path validation: Invalid relative path returns structured error with cwd included
- Continuation context reconstruction: Auto-mode follow-up inconsistency observed (now fixed separately)

## Artifact Index (Quick Links)
- MCP sweep report: docs/mcp_tool_sweep_report.md
- Timestamped sweep: docs/sweep_reports/2025-09-29_08-57-17/mcp_tool_sweep_report.md
- WS probe raws: docs/System_layout/_raw/ws_probe_*.json (+ .jsonl traces for streaming)
- Chat context/path tests: docs/augmentcode_phase2/raw/mcp_chat_context_*.json

