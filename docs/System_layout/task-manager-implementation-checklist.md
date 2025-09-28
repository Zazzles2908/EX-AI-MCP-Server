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
- [ ] RoutePlan plumbing at boundary
  - AC: Every tool call logs `_route_plan` JSONL with chosen model/provider and reasons
  - Deps: src/router/service.py, utils/observability.py
- [ ] Continuation and context threading
  - AC: continuation_id preserved across workflows; thread_context attached
- [ ] Tool map normalization
  - AC: tools are discoverable; allow/deny filtering enforced

## Phase 2 – Providers & Registry
- [ ] GLM provider: SSE/stream + web_search tools injection
  - AC: Streaming smoke passes; GLM payload shows tools=[{"type":"web_search"}] when requested
- [ ] Kimi provider: cache token + optional streaming
  - AC: Cache token appears in metadata; streaming path gated via env
- [ ] Registry trims legacy providers
  - AC: OpenRouter and custom providers removed or guarded behind feature flags

## Phase 3 – Manager-First Routing
- [ ] Router choose_model_with_hint() and capability pruning
  - AC: Auto routes produce stable, explainable decisions with reason codes
- [ ] Fallback coherency with RoutePlan
  - AC: Fallback path appends to route_plan.history and preserves reasons

## Phase 4 – Classification & Complexity
- [ ] Implement classify() outputs
  - AC: _agentic_task_type emitted; complexity score present with token estimate
- [ ] Router hints wired from classification
  - AC: Long-context/file-heavy requests bias to Kimi; short/fast to GLM-Flash

## Phase 5 – Tools & Workflows
- [ ] Propagate flags (use_websearch, stream) and budget
  - AC: Provider payloads reflect requested flags; budget respected in workflows
- [ ] Synthesis hop (optional)
  - AC: When enabled, secondary GLM call logged and annotated in metadata

## Phase 6 – Streaming & Long-Context
- [ ] Kimi streaming (env-gated)
  - AC: Stream demo runs end-to-end with Kimi when enabled
- [ ] Context caching consistency
  - AC: session_id/call_key/token reuse verified via tests

## Phase 7 – Observability & Health
- [ ] RoutePlan + provider telemetry JSONL
  - AC: Per-call JSONL includes route, tokens, latency; aggregates by provider/model exist
- [ ] Health/circuit (optional)
  - AC: Unhealthy provider blocked; health state recorded

## Phase 8 – Test & Verification
- [ ] Router unit tests
  - AC: Explicit/auto routing decisions verified
- [ ] Provider tests (GLM/Kimi)
  - AC: Streaming, file upload, cache token capture tested
- [ ] Workflow tests
  - AC: analyze/debug/refactor/testgen happy-paths pass; continuation_id respected

## Cross-Cutting Docs
- [ ] Validate docs structure & links
  - AC: All internal links resolve; kebab-case enforced; API_platforms index navigates to endpoints
- [ ] Script inventory remains in sync
  - AC: implementation_roadmap/script-inventory-and-phase-mapping.md updated after changes

