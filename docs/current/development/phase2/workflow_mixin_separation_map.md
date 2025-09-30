# Workflow Mixin Separation Map
**Date**: 2025-09-29  
**Source**: tools/workflow/workflow_mixin.py (1,937 lines)  
**Target**: 4 modules (~500 lines each)

---

## Module 1: orchestration.py (~500 lines)

**Purpose**: Core workflow orchestration, step execution, pause/resume logic

**Lines**: 1-100, 849-914, 1005-1053, 1536-1615, 1863-1938

**Contents**:
- `BaseWorkflowMixin` class definition and `__init__`
- Abstract method declarations (get_name, get_workflow_request_model, etc.)
- Core workflow execution:
  - `execute()` - main entry point (lines 1882-1912)
  - `execute_workflow()` - main workflow logic (NOT IN VISIBLE RANGE, likely 700-1500)
  - `prepare_prompt()` - base implementation (lines 1916-1930)
  - `format_response()` - base implementation (lines 1932-1937)
- Step processing:
  - `prepare_step_data()` (lines 849-913)
  - `build_base_response()` (lines 914-1004)
  - `_process_work_step()` (lines 1863-1878)
- Completion handling:
  - `should_skip_expert_analysis()` (lines 1005-1013)
  - `handle_completion_without_expert_analysis()` (lines 1014-1052)
  - `handle_work_continuation()` (lines 1536-1579)
- Backtracking:
  - `_handle_backtracking()` (lines 1580-1586)
  - `_update_consolidated_findings()` (lines 1587-1608)
  - `_reprocess_consolidated_findings()` (lines 1609-1614)
  - `_prepare_work_summary()` (lines 1615-1862)

**Dependencies**:
- Import from file_embedding: file handling methods
- Import from expert_analysis: expert analysis methods
- Import from conversation_integration: thread/turn methods
- External: mcp.types, utils.progress, config, base_models

---

## Module 2: file_embedding.py (~500 lines)

**Purpose**: Context-aware file selection, token budgeting, deduplication

**Lines**: 353-467, 474-633

**Contents**:
- File preparation for expert analysis:
  - `_prepare_files_for_expert_analysis()` (lines 353-415)
  - `_force_embed_files_for_expert_analysis()` (lines 416-466)
  - `wants_line_numbers_by_default()` (lines 467-472)
  - `_add_files_to_expert_context()` (lines 474-484)
- Workflow file context handling:
  - `_handle_workflow_file_context()` (lines 485-521)
  - `_should_embed_files_in_workflow_step()` (lines 522-551)
  - `_embed_workflow_files()` (lines 552-632)
  - `_reference_workflow_files()` (lines 633-848)
- File content accessors:
  - `get_embedded_file_content()` (lines 1090-1096)
  - `get_file_reference_note()` (lines 1097-1103)
  - `get_actually_processed_files()` (lines 1104-1110)

**Dependencies**:
- External: utils.file_utils, config (MCP_PROMPT_SIZE_LIMIT)
- Internal: get_model_provider, _prepare_file_content_for_prompt (from BaseTool)

---

## Module 3: expert_analysis.py (~500 lines)

**Purpose**: External model integration, analysis formatting, response consolidation

**Lines**: 158-238, 305-312, 1248-1275 (plus execute_workflow expert analysis section ~700-1500)

**Contents**:
- Expert analysis decision logic:
  - `should_call_expert_analysis()` (lines 158-182)
  - `prepare_expert_analysis_context()` (lines 183-207)
  - `requires_expert_analysis()` (lines 208-216)
  - `should_include_files_in_expert_prompt()` (lines 217-223)
  - `should_embed_system_prompt()` (lines 224-230)
- Expert analysis configuration:
  - `get_expert_thinking_mode()` (lines 231-237)
  - `get_expert_timeout_secs()` (lines 238-248)
  - `get_expert_heartbeat_interval_secs()` (lines 249-266)
  - `get_expert_analysis_instruction()` (lines 305-311)
  - `get_expert_analysis_guidance()` (lines 1248-1274)
- Expert analysis execution:
  - `_call_expert_analysis()` (likely lines 700-1500, need to extract)
  - Response parsing and consolidation

**Dependencies**:
- Import from file_embedding: file preparation methods
- External: asyncio, time, utils.progress, get_model_provider

---

## Module 4: conversation_integration.py (~437 lines)

**Purpose**: Thread reconstruction, turn management, continuation offers, cross-tool context

**Lines**: 1304-1320, 1386-1535

**Contents**:
- Conversation storage:
  - `store_conversation_turn()` (lines 1304-1319)
  - `_add_workflow_metadata()` (lines 1320-1385)
  - `_extract_clean_workflow_content_for_history()` (lines 1386-1535)
- Request field accessors (for conversation context):
  - `get_request_continuation_id()` (lines 1130-1136)
  - `get_request_next_step_required()` (lines 1137-1143)
  - `get_request_step_number()` (lines 1144-1150)
  - `get_request_relevant_files()` (lines 1151-1157)
  - `get_request_files_checked()` (lines 1158-1164)
  - `get_current_arguments()` (lines 1165-1171)
  - `get_backtrack_step()` (lines 1172-1178)
- Initial request handling:
  - `store_initial_issue()` (lines 1179-1183)
  - `get_initial_request()` (lines 1184-1192)

**Dependencies**:
- External: utils.conversation_memory (add_turn, create_thread)
- Internal: get_name, get_model_provider

---

## Module 5: request_accessors.py (~500 lines) [ADDITIONAL MODULE NEEDED]

**Purpose**: Request field extraction and validation (getter methods)

**Lines**: 267-304, 1053-1247

**Contents**:
- Temperature and model settings:
  - `get_request_temperature()` (lines 267-273)
  - `get_validated_temperature()` (lines 274-290)
  - `get_request_thinking_mode()` (lines 291-297)
  - `get_request_use_websearch()` (lines 298-304)
  - `get_request_use_assistant_model()` (lines 312-333)
  - `get_request_model_name()` (lines 1118-1129)
- Request data extraction:
  - `get_request_confidence()` (lines 1053-1059)
  - `get_request_relevant_context()` (lines 1060-1066)
  - `get_request_issues_found()` (lines 1067-1073)
  - `get_request_hypothesis()` (lines 1074-1080)
  - `get_request_images()` (lines 1081-1089)
- Current state accessors:
  - `get_current_model_context()` (lines 1111-1117)
- Completion and status:
  - `prepare_work_summary()` (lines 1193-1196)
  - `get_completion_status()` (lines 1197-1200)
  - `get_final_analysis_from_request()` (lines 1201-1204)
  - `get_confidence_level()` (lines 1205-1208)
  - `get_completion_message()` (lines 1209-1215)
  - `get_skip_reason()` (lines 1216-1219)
  - `get_skip_expert_analysis_status()` (lines 1220-1223)
  - `get_completion_next_steps_message()` (lines 1224-1247)
- Response customization:
  - `customize_workflow_response()` (lines 1275-1303)
  - `get_step_guidance_message()` (lines 334-352)

**Dependencies**:
- Minimal - mostly pure getters with try/except wrappers

---

## Revised Split Strategy (5 modules instead of 4)

Given the analysis, I recommend **5 modules** instead of 4 to maintain clean separation:

1. **orchestration.py** (~450 lines): Core workflow execution, step processing, backtracking
2. **file_embedding.py** (~480 lines): File context handling, embedding logic
3. **expert_analysis.py** (~450 lines): Expert model integration, analysis execution
4. **conversation_integration.py** (~280 lines): Thread/turn management, metadata
5. **request_accessors.py** (~280 lines): Request field getters, validation helpers

**Total**: ~1,940 lines (matches original)

---

## Migration Order

1. Create `request_accessors.py` first (no dependencies on other new modules)
2. Create `conversation_integration.py` (depends on request_accessors)
3. Create `file_embedding.py` (depends on request_accessors)
4. Create `expert_analysis.py` (depends on file_embedding, request_accessors)
5. Create `orchestration.py` (depends on all above)
6. Update `workflow_mixin.py` to import and delegate from all 5 modules

---

## Import Structure

```python
# tools/workflow/orchestration.py
from .request_accessors import RequestAccessorMixin
from .file_embedding import FileEmbeddingMixin
from .expert_analysis import ExpertAnalysisMixin
from .conversation_integration import ConversationIntegrationMixin

class BaseWorkflowMixin(
    RequestAccessorMixin,
    FileEmbeddingMixin,
    ExpertAnalysisMixin,
    ConversationIntegrationMixin,
    ABC
):
    # Core orchestration logic only
    pass
```

---

## Next Steps

1. Extract request_accessors.py (pure getters, no complex logic)
2. Extract conversation_integration.py (uses request_accessors)
3. Extract file_embedding.py (uses request_accessors)
4. Extract expert_analysis.py (uses file_embedding + request_accessors)
5. Extract orchestration.py (uses all above)
6. Test with workflow tools via EXAI-WS MCP

---

**End of Separation Map**

