# Implementation Checklist (Import-Ready)

This checklist enumerates concrete, sequenced tasks by roadmap phase. Each item includes acceptance criteria (AC) and dependencies (Deps). Use as-is in your task manager.

## Phase 0 – Bootstrap & Layout
- [ ] Verify stdio entry and config bootstrap
  - AC: `python server.py --help` runs; config loads without errors
  - Deps: utils/config_bootstrap.py
- [ ] Ensure requirements + lock are current
  - AC: `pip install -r requirements.txt` succeeds locally
- [ ] Repo hygiene pass (logs/.logs exist; .env guidance present)

## Phase 1 – MCP Boundary & Request Handling
- [x] RoutePlan plumbing at boundary
  - AC: Every tool call logs `_route_plan` JSONL with chosen model/provider and reasons
  - Deps: src/router/service.py, utils/observability.py
- [x] Continuation and context threading
  - AC: continuation_id preserved across workflows; thread_context attached
- [x] Tool map normalization
  - AC: tools are discoverable; allow/deny filtering enforced

## Phase 2 – Providers & Registry
- [x] GLM provider: SSE/stream + web_search tools injection
  - AC: Streaming smoke passes; GLM payload shows tools=[{"type":"web_search"}] when requested
  - Evidence: docs/System_layout/_raw/phase2_glm_payload_preview_artefact.json (tools injection visible)
  - Evidence: tests/phase2/test_glm_tool_injection.py (unit + preview tool)
- [x] Kimi provider: cache token + optional streaming
  - AC: Cache token appears in metadata; streaming path gated via env
  - Evidence: tools/providers/kimi/kimi_capture_headers.py (diagnostic tool)
  - Evidence: tests/phase2/test_kimi_cache_metadata.py (metadata.cache attached/saved keys)
- [x] Registry trims legacy providers
  - AC: OpenRouter and custom providers removed or guarded behind feature flags
  - Evidence: src/server/providers/provider_config.py (ENABLE_OPENROUTER/ENABLE_CUSTOM gating)

## Phase 3 – Manager-First Routing
- [x] Router choose_model_with_hint() and capability pruning
  - AC: Auto routes produce stable, explainable decisions with reason codes
  - Scripts: src/router/service.py (choose_model_with_hint), src/providers/capabilities.py (capability checks)
- [x] Fallback coherency with RoutePlan
  - AC: Fallback path appends to route_plan.history and preserves reasons
  - Scripts: src/router/service.py (fallback handling)
- [x] RoutePlan JSONL enrichment (feeds Phase 7)
  - Purpose: Persist full route plan with decisions, provider, model, flags
  - AC: Per-call JSONL appended under logs/routeplan/*.jsonl with route_plan.history + reasons
  - Scripts: utils/observability.py (append_routeplan_jsonl), src/router/service.py (invoke)
  - Evidence: tests/phase3/test_routeplan_jsonl.py (passing), logs/routeplan/* created on demand; docs/System_layout/_raw/phase7_validation_mcp_memo.md (Phase 7 memo)
  - Deps: Phase 7 Observability

## Phase 4 – Classification & Complexity
- [x] Implement classify() outputs
  - Purpose: Emit _agentic_task_type, complexity score, token estimate for routing
  - AC: classify() returns {type, complexity, est_tokens}; persisted into route_plan.meta
  - Scripts: src/router/classifier.py (new)
  - Evidence: tests/phase4/test_classifier_outputs.py (passing)
  - Deps: utils/token_estimator.py (new)
- [x] Router hints wired from classification
  - Purpose: Bias to Kimi for long-context/file-heavy; GLM-Flash for short/fast
  - AC: choose_model_with_hint() consumes classify() output and flips provider/model accordingly; reasons logged
  - Scripts: src/router/service.py (consume classifier), src/providers/registry.py (capabilities hints)
  - Tests: tests/phase4/test_routing_hints_bias.py (passing)
  - Evidence: docs/System_layout/_raw/phase4_routing_hints_bias.md

## Phase 5 – Tools & Workflows
- [x] Propagate flags (use_websearch, stream) and budget
  - Purpose: Ensure tool/workflow layer forwards flags + budget to providers and logs them
  - AC: Provider payloads reflect requested flags; budget respected; JSONL shows flags/budget
  - Scripts: tools/chat.py (propagate flags/env-gated streaming), src/router/service.py (budget filter + meta), utils/observability.py (route_plan JSONL)
  - Tests: tests/phase5/test_flag_propagation_and_budget.py (passing)
  - Evidence: docs/System_layout/_raw/phase5_flag_budget_propagation.md (artifact summary)
- [x] Synthesis hop (optional)
  - Purpose: When enabled, perform secondary GLM synthesis call (metadata + logs)
  - AC: route_plan meta includes synthesis hop; JSONL emits synthesis_hop event
  - Scripts: src/router/synthesis.py (new), src/router/service.py (invoke), utils/observability.py (append_synthesis_hop_jsonl)
  - Tests: tests/phase5/test_synthesis_hop.py (passing)
  - Evidence: docs/System_layout/_raw/phase5_synthesis_hop_smoke.md (artifact summary)
- [x] Kimi chat tool remediation (Phase 2 reliability)
  - Purpose: Eliminate “No result received” by broadening input handling and hardening return paths
  - AC: kimi_chat_with_tools accepts messages as array or string; never returns empty; clear error envelope on failures
  - Scripts: tools/providers/kimi/kimi_tools_chat.py (schema + normalization), tests/phase2/test_kimi_chat_with_tools_schema.py
  - Evidence: docs/System_layout/_raw/phase5_kimi_chat_schema_validation.md
- [x] Chat tool context isolation (conversation continuity)
  - Purpose: Maintain history across calls using continuation_id
  - AC: Given a continuation_id, Chat tool restores N past turns and includes in provider messages
  - Scripts: src/conversation/history_store.py (new), src/conversation/memory_policy.py (new), tools/chat.py (wire-in)
  - Tests: tests/phase5/test_chat_context_continuation.py (passing)
  - Evidence: docs/System_layout/_raw/phase5_chat_context_continuation_smoke.md

## Phase 6 – Streaming & Long-Context
- [x] Kimi streaming (env-gated)
  - AC: Stream demo runs end-to-end with Kimi when enabled
  - Evidence: docs/System_layout/_raw/ws_probe_kimi_stream_bullets_20250928T101447Z.json
  - Evidence: docs/System_layout/_raw/kimi_normalize_tester_artefacts_20250928.md (empty-message guard verified)
- [x] GLM streaming (env-gated)
  - AC: Chat tool streams via provider when GLM_STREAM_ENABLED=true; JSONL traces saved
  - Evidence: docs/System_layout/_raw/phase6_streaming_validation_run_2025-09-28T20-02Z.md
  - Evidence: docs/System_layout/_raw/ws_probe_glm_stream_paragraph_bullets_20250928T101505Z.json
- [x] Context caching consistency
  - AC: session_id/call_key/token reuse verified via tests
  - Scripts: src/conversation/cache_store.py (new), tools/chat.py (cache capture + preface), tests/phase6/test_context_caching_consistency.py (passing)
  - Evidence: docs/System_layout/_raw/phase6_context_caching_consistency.md

## Phase 7 – Observability & Health
- [x] RoutePlan + provider telemetry JSONL
  - Purpose: Capture per-call route, flags, tokens, latency; aggregate by provider/model
  - AC: JSONL per-call under logs/telemetry/*.jsonl; daily aggregates in logs/telemetry/aggregates/*.json
  - Scripts: utils/observability.py (emit_telemetry_jsonl, rollup_aggregates), src/router/service.py (invoke)
  - Tests: tests/phase7/test_telemetry_jsonl_and_aggregates.py (passing)
  - Evidence: docs/System_layout/_raw/phase7_telemetry_and_health.md
- [x] Health/circuit (optional)
  - Purpose: Detect provider errors/timeouts; block unhealthy providers for a window
  - AC: Circuit opens on error; provider bypassed while open (unit-tested via explicit open)
  - Scripts: utils/health.py (singleton + sync helpers), src/router/service.py (skip blocked)
  - Tests: tests/phase7/test_health_circuit.py (passing)
  - Evidence: docs/System_layout/_raw/phase7_telemetry_and_health.md

## Phase 8 – Test & Verification
- [x] Router unit tests
  - Purpose: Verify explicit/auto routing and fallback decisions
  - AC: choose_model_with_hint + fallback paths covered with assertions on reasons and outcomes
  - Scripts/Tests: tests/phase8/test_router_routing.py (passing)
  - Evidence: docs/System_layout/_raw/phase8_test_coverage_summary.md; live validation: docs/System_layout/_raw/phase8_live_glm_websearch_raw.json, docs/System_layout/_raw/phase8_live_kimi_upload_extract_raw.json, docs/System_layout/_raw/phase8_live_validation_report.md
- [x] Provider tests (GLM/Kimi)
  - Purpose: Validate streaming, file upload, cache token capture, tool injection (offline-friendly: schema/tooling validation)
  - AC: GLM web_search schema injected; Kimi web_search schema modes validated; prior Kimi chat reliability tests remain passing
  - Scripts/Tests: tests/phase8/test_provider_glm_websearch.py, tests/phase8/test_provider_kimi_tools_schema.py (passing)
  - Evidence: docs/System_layout/_raw/phase8_test_coverage_summary.md
- [x] Workflow tests
  - Purpose: Ensure end-to-end continuation_id behavior across turns
  - AC: Happy path passes; continuation_id respected and history reconstructed
  - Scripts/Tests: tests/phase8/test_workflows_end_to_end.py (passing)
  - Evidence: docs/System_layout/_raw/phase8_test_coverage_summary.md

## Phase 2 – Kimi Tool Reliability Remediation (Follow-up)
- [x] kimi_chat_with_tools: eliminate client-side "No result received" failures
  - Purpose: Accept string or array inputs; ensure non-empty result or structured error
  - AC: Pass tests for string/array messages; non-stream and stream paths return valid envelopes
  - Scripts: tools/providers/kimi/kimi_tools_chat.py; tests/phase2/test_kimi_chat_with_tools_schema.py
  - Evidence: tests/phase2/test_kimi_chat_with_tools_schema.py (passing)
  - Deps: Phase 5 flag propagation (stream toggles)
- [x] Chat tool context isolation fix
  - Purpose: Persist/restore conversation history by continuation_id
  - AC: N-turn continuity validated; messages assembled with prior turns
  - Scripts: src/conversation/history_store.py, src/conversation/memory_policy.py, tools/chat.py
  - Evidence: tests/phase5/test_chat_context_continuation.py (passing)

## Cross-Cutting Docs
- [x] Validate docs structure & links
  - AC: All internal links resolve; kebab-case enforced; API_platforms index navigates to endpoints
  - Scripts: utils/docs_validator.py (library), scripts/validate_docs.py (CLI), tests/docs/test_docs_validator.py (passing)
  - Evidence: docs/System_layout/_raw/phase_docs_validation_report.json, docs/System_layout/_raw/phase_docs_validation_mcp_memo.md
- [x] Script inventory remains in sync
  - AC: implementation_roadmap/script-inventory-and-phase-mapping.md updated after changes
  - Evidence: docs/implementation_roadmap/script-inventory-and-phase-mapping.md

