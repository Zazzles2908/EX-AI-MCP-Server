# Comprehensive MCP Tool Validation — Multi-Model Matrix (2025-09-29)

(RELOCATED COPY) See raw artifacts referenced within.

[Original path prior to reorg: docs/augmentcode_phase2/tool_validation_matrix_20250929.md]

---

## Summary
- Total Scenarios executed: 8
- Success: 6, Failures: 2 (thinkdeep timeouts)
- Providers verified: GLM, Kimi
- Auto-mode continuation: PASS (ID chained)
- File upload & file-assisted chat: PASS
- Web search: PASS

Artifacts folder: docs/augmentcode_phase2/raw/

---

## Scenario Results

### 1) Single-turn chat (GLM, web off)
- Model: glm-4.5-flash
- Prompt: "GLM OK"
- Result: PASS — "GLM OK"
- Duration: ~2.7s | Tokens: ~229
- Raw: raw/validation_chat_glm_single.json

### 2) Single-turn chat (Kimi, web on)
- Model: kimi-latest, use_websearch=true
- Result: PASS — "Kimi OK — web on."
- Duration: ~1.7s | Tokens: ~231
- Raw: raw/validation_chat_kimi_single.json

### 3) Multi-turn continuation (auto mode)
- Turn 1 -> Turn 2 with continuation_id
- Models selected: glm-4.5-flash (auto resolved)
- Results: PASS — Turn1: "ready"; Turn2: "ACK"
- Durations: ~5.2s then ~2.4s
- Raw: raw/validation_chat_auto_turn1.json, raw/validation_chat_auto_turn2.json

### 4) File-assisted chat (GLM)
- Files: hello.txt, sample.json, sample.md
- Result: PASS — "FILES OK"
- Duration: ~2.1s
- Raw: raw/validation_chat_glm_files.json

### 5) Kimi upload & extract
- Files: hello.txt, sample.json, sample.md
- Result: PASS — 3 files extracted with content
- Raw: raw/validation_kimi_upload_extract.json

### 6) GLM Web Search
- Query: "Zhipu GLM web_search API streaming example"
- Result: PASS — results returned from bigmodel docs
- Raw: raw/validation_glm_web_search.json

### 7) thinkdeep (glm-4.5-flash)
- With relevant_files and findings
- Result: FAIL — Daemon timeout
- Raw: raw/validation_thinkdeep_glm_timeout.txt

### 8) thinkdeep (kimi-thinking-preview)
- With relevant_files and findings
- Result: FAIL — Daemon timeout
- Raw: raw/validation_thinkdeep_kimi_timeout.txt

---

## Quick Ops Stats
- Tools validated: chat, glm_web_search, kimi_upload_and_extract, listmodels, version
- Tools partially validated: thinkdeep (timeouts)
- Models exercised: glm-4.5-flash, kimi-latest, auto (→ glm-4.5-flash)
- Features covered: continuation, file ingestion, uploads, web search

---

## Issues & Repro
- thinkdeep timeouts
  - Repro: call thinkdeep_EXAI-WS with minimal step and findings, with relevant_files set
  - Observed: "Daemon did not return call_tool_res in time" (twice; GLM and Kimi thinking)
  - Hypotheses: tool-side schema strictness + missing internal execution path; long model latency; manager timeout below model response; transport boundary issue

---

## Recommendations (Next Steps)
1) Instrument thinkdeep path (boundary + provider call) with timing spans; raise daemon timeout to 60s for workflows.
2) Add a minimal thinkdeep happy-path unit using short prompt and no web; verify locally.
3) Extend smoke suite to cover one more workflow (analyze or debug) to confirm file auto-provision end-to-end.
4) Keep capturing all raw artifacts under raw/ and update this matrix when re-running.

---

## Appendices
- Model list: raw/validation_listmodels.md
- Server version: raw/validation_version.md

