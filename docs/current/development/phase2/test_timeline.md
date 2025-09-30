# Phase 2 Test Timeline (Chronological)

This document tracks all notable validation tasks, with links to raw artifacts and reports.

## 2025-09-28
- Phase 1 evidence baseline captured
  - Evidence index: evidence/exai_validation_evidence.md (relocated)

## 2025-09-29 (Phase 2)
- Provider inventory and server info
  - listmodels → raw/validation_listmodels.md
  - version → raw/validation_version.md

- Core chats
  - GLM single-turn (web off) → raw/validation_chat_glm_single.json
  - Kimi single-turn (web on) → raw/validation_chat_kimi_single.json
  - Auto-mode continuation
    - Turn 1 → raw/validation_chat_auto_turn1.json
    - Turn 2 (with continuation_id) → raw/validation_chat_auto_turn2.json

- File-assisted operations
  - GLM chat with files (TEST_FILES_DIR) → raw/validation_chat_glm_files.json
  - Kimi upload & extract → raw/validation_kimi_upload_extract.json

- Web search
  - GLM web_search → raw/validation_glm_web_search.json

- Workflow tool attempts
  - thinkdeep (glm-4.5-flash) → raw/validation_thinkdeep_glm_timeout.txt (timeout)
  - thinkdeep (kimi-thinking-preview) → raw/validation_thinkdeep_kimi_timeout.txt (timeout)

- Consolidated reports
  - Tool Status Report → reports/tool_status_report_20250929.md
  - Validation Matrix → reports/tool_validation_matrix_20250929.md

- Consultations
  - Schema strictness (draft-07, additionalProperties:false) → consultations/phase3_schema_consultation_exai_chat.md
  - GLM consultation on thinkdeep timeouts → raw/consult_glm_thinkdeep_timeout_20250929.md

## Pending / Next
- Re-run thinkdeep with increased daemon timeout and streaming enabled; capture raw outputs
- Add analyze or debug workflow smoke; capture raw and update matrix
- Expand matrix to include glm-4.5 and kimi-k2-0905-preview variants (streaming toggles)

