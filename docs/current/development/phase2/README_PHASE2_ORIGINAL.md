# Phase 2  EXAI-WS MCP Validation & Evidence Index

This index guides you through our Phase 2 validation work: what we tested, the current status, and where to find raw artifacts and reports.

## Quick Status
- Providers validated: GLM, Kimi
- Core chat + continuation: PASS
- Web search (GLM): PASS
- Kimi upload/extract: PASS
- Workflows (thinkdeep): TIMEOUT (investigating)

## Navigation
- Raw artifacts: ./raw/
- Reports (consolidated): ./reports/
- Evidence (structured indexes): ./evidence/
- Consultations (strategy & schema notes): ./consultations/

## Key Documents
- Reports
  - reports/tool_status_report_20250929.md
  - reports/tool_validation_matrix_20250929.md
- Consultations
  - consultations/phase3_schema_consultation_exai_chat.md
  - raw/consult_glm_thinkdeep_timeout_20250929.md (GLM consultation on timeouts)
- Evidence
  - evidence/exai_validation_evidence.md

## What still needs attention
- Workflow tool E2E validation (thinkdeep first): instrument WS boundary and raise daemon timeout; add minimal happy-path test
- Add second workflow smoke (analyze or debug) to confirm file auto-provision end-to-end

## How to reproduce quickly
1) Restart WS daemon (non-blocking):
   - powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\ws_start.ps1 -Restart
2) Run chat smokes and uploads via EXAI-WS MCP tools
3) Review artifacts in ./raw and updated reports in ./reports

