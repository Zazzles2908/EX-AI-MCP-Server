# EXAI‑MCP Technical Debt and Architectural Issues Audit (Comprehensive)

Date: 2025‑09‑28
Scope: Entire repository with emphasis on MCP server, tool registry, providers (GLM, Kimi), streaming, and conversation context.

---

## 1) Script Function Density Audit (decomposition targets)
Guideline: Prefer ≤500 lines per module and single‑responsibility. Files exceeding threshold or packing too many disparate concerns:

High‑priority refactor candidates:
- src/server/handlers/request_handler.py (~1221 lines)
  - Symptoms: Multiplexes dispatch, env flags, context handling, cache, provider auto‑model selection, progress capture, heartbeats, and more.
  - Recommendation: Split into request lifecycle units:
    - handler_core.py (argument normalization, continuation handling)
    - handler_dispatch.py (tool routing + invocation)
    - handler_observability.py (progress/telemetry/heartbeat)
    - handler_consensus_autoselect.py (consensus model auto‑selection)
- src/providers/openai_compatible.py (~992 lines)
  - Symptoms: Transport, retries, vision, timeouts, error mapping, and cross‑provider shims all in one.
  - Recommendation: Extract:
    - http_client.py (httpx/OpenAI clients + timeout/proxy policy)
    - retries.py (retry / circuit breaker)
    - adapters/vision.py, adapters/chat.py (feature specific)
- server.py (~602 lines)
  - Symptoms: Process bootstrap + MCP server wiring + tool registry definitions.
  - Recommendation: Move registry to tools/registry.py and server bootstrap to src/server/bootstrap.py; keep server.py thin entrypoint.
- src/providers/kimi.py (~526 lines)
  - Symptoms: Chat, uploads, context cache headers, model gating tightly coupled.
  - Recommendation: Extract:
    - kimi_client.py (OpenAI‑compatible client construction + headers)
    - kimi_files.py (uploads/list)
    - kimi_chat.py (chat, non‑stream) and kimi_stream.py (provider‑level streaming)

Borderline/complexity watchlist (near 500 or highly complex):
- tools/providers/kimi/kimi_tools_chat.py (~462 lines): Tool loop, streaming, web search integration; split tool orchestration from provider I/O.
- src/router/service.py (~350) but dense logic; consider splitting candidate selection vs. policy.

Acceptance: Open issues created for each refactor unit with explicit cut plan and tests.

---

## 2) EXAI‑MCP Tool Implementation Gaps
Evidence suggests mixed reliability due to registry mismatches and partial implementations.

Findings:
- Tool discovery: server.TOOLS vs tools/registry.py dual sources cause drift in visibility and LEAN_MODE gating.
- Self‑check/diagnostics: references exist but no stable “self_check” tool alias consistently exposed; audits reported failures to find/run.
- Kimi tool(s): kimi_chat_with_tools present but context propagation inconsistent (see §3). Streaming sits at tool layer, not provider.

Fixes:
- Single source of truth: Adopt tools/registry.build_tools() as authoritative. server.py should import from registry only; remove local TOOLS duplication.
- Stable aliases: Ensure "self_check" and "diagnostics" canonical names exist with backward‑compatible aliases.
- Capability flags: Registry must compute capabilities (needs files, supports streaming) and inject them into metadata for clients.
- Tests: Add MCP discovery test ensuring all expected tools enumerate and basic help/echo invocations succeed.

---

## 3) Conversation Context Isolation: Root‑cause and Remediation
Observed issue: Conversation continuity works for tools expecting a single `prompt` string but fails for tools expecting `messages` arrays (e.g., Kimi chat‑with‑tools).

Root‑cause:
- Thread reconstruction (src/server/context/thread_context.py) returns enhanced_arguments with `prompt` only.
- Request handler applies reconstruction for any tool with `continuation_id`, but does not translate/enrich `messages`.
- Kimi tool path consumes `messages` exclusively and ignores `prompt`, so reconstructed history is effectively dropped.

Remediation Plan:
- Harmonize context injection post‑reconstruction in request handler:
  - If arguments include `messages` (or tool = kimi_chat_with_tools), prepend a synthetic system message carrying the reconstructed conversation history and follow‑up instructions; also append the new user `prompt` as a message when `messages` missing it.
  - Otherwise keep existing `prompt` flow.
- Provide a helper util ContextInjector:
  - to_messages(enhanced_prompt) -> List[Message]
  - to_prompt(messages) -> str
- Add feature flag: CONTEXT_INJECTION_MODE=auto|prompt|messages (default auto).
- Tests: Multi‑turn across chat->kimi and kimi->chat.

---

## 4) Path Validation and UX Friction
Symptoms: Some tools/docs require absolute paths; others accept relative paths; uploads bypass central validation.

Current capability:
- src/core/validation/secure_input_validator.py enforces repo‑root containment and optional allowlist for external absolute paths.

Gaps:
- Not consistently applied in providers/tools (notably Kimi file upload/list paths).
- User guidance mismatched with actual behavior.

Fixes:
- Standardize: All file path inputs should use SecureInputValidator.normalize_and_check, accepting repo‑relative inputs by default.
- Update user‑facing docs to state: prefer repo‑relative paths; absolute outside repo requires EX_ALLOW_EXTERNAL_PATHS=true plus EX_ALLOWED_EXTERNAL_PREFIXES.
- Add validation decorators or shared mixin for tools that accept files.

---

## 5) Connection Stability and Streaming Reliability
Symptoms: Mixed reliability in streaming (timeouts/cancellations), particularly for Kimi when combined with web‑search or long responses.

Findings:
- Streaming lives in tools/providers/kimi/kimi_tools_chat.py via a threaded adapter; provider (src/providers/kimi.py) does not offer first‑class streaming.
- Timeout policies vary across code paths; some SDK calls inherit default client timeouts, others pass none.
- Event generator and background thread lifecycle race on cancellation/heartbeat paths.
- Extra headers/context‑cache options passed variably; potential incompatibility with OpenAI SDK arg shapes.

Recommendations:
- Move streaming into provider layer (kimi_stream.py) and expose a uniform ProviderInterface.stream_chat(...), returning a standardized event iterator with chunk aggregation.
- Unify timeout policies via central client factory (http_client.py) with read/connect/timeouts and retry/backoff.
- SSE vs SDK parity: implement HTTP SSE fallback when SDK streaming fails; choose via env KIMI_STREAM_TRANSPORT=sdk|sse|auto.
- Deterministic teardown: ensure cancellation signals propagate and generators close cleanly; add watchdog logs.
- Observability: attach route_id/req_id to all stream events; log first token latency and chunks/sec.

---

## 6) Kimi Streaming: Required Code Changes vs. Acceptance Criteria
Acceptance criteria (from user requirements):
- Provider‑isolated modules and shared utilities
- Env‑gated Kimi SSE streaming with chunk aggregation
- metadata.streamed flag, chunk metadata, and final aggregation
- Register kimi_chat_with_tools; propagate chat→provider streaming flag
- Production‑quality error handling/logging

Delta (what’s missing):
- Streaming is implemented in tool, not provider; no provider‑level SSE path.
- No explicit `metadata.streamed` surfaced to caller; mixed representations of stream internals.
- Inconsistent flag propagation from chat args to provider call.

Proposed changes:
1) Provider module split:
   - src/providers/kimi_client.py (build OpenAI client + common headers)
   - src/providers/kimi_stream.py (stream_chat: iterator yielding standardized chunks)
   - src/providers/kimi_chat.py (non‑streaming chat)
2) Shared streaming utilities:
   - streaming/streaming_adapter.py gains a provider‑agnostic aggregator (append_text, on_tool_call, finalize)
3) Env gates:
   - KIMI_STREAM_ENABLED=true|false (default true)
   - KIMI_STREAM_TRANSPORT=auto|sdk|sse (default auto)
   - KIMI_STREAM_MAX_WAIT_MS, KIMI_STREAM_HEARTBEAT_MS
4) API contract:
   - Provider returns { text, chunks: [...], metadata: { streamed: true, first_token_ms, model, route_id } }
   - Tool layer passes through without re‑implementing streaming logic
5) Error handling:
   - Unified retry/circuit patterns; on stream errors, surface partial text with error metadata and suggest retry.
6) Tests:
   - Unit: chunk aggregation correctness, metadata.streamed presence
   - Integration: GLM+Kimi streaming smoke tests; long response; cancellation

---

## 7) Priority Matrix and Production Impact
High (fix ASAP):
- Conversation context injection mismatch for `messages` tools (user‑visible context loss)
- Kimi streaming at tool layer only; lack of provider‑level streaming and metadata.streamed

Medium:
- request_handler.py and openai_compatible.py decomposition (maintainability)
- Path validation consistency across tools/providers

Low:
- server.py decomposition; router/service split by policy vs. selection logic

---

## 8) Concrete Next Steps (Phase‑wise)
Phase A – Context and Registry (1–2 days)
- Implement messages‑aware context injection in request_handler; add CONTEXT_INJECTION_MODE=auto.
- Make tools/registry authoritative; remove server.TOOLS duplication; add stable alias for self_check.
- Tests: discovery, multi‑turn across chat↔kimi.

Phase B – Kimi Streaming (2–3 days)
- Extract provider‑level streaming (kimi_stream.py) with env‑gates and SSE fallback.
- Add metadata.streamed and chunk metrics; wire propagation from tool args.
- Tests: stream smoke tests and cancellation.

Phase C – Decomposition + Validation (2–4 days)
- Split request_handler.py and openai_compatible.py; migrate common http client + retries.
- Standardize path validation; update docs and examples.
- Run EXAI‑WS MCP smoke suite; capture raw outputs under docs/System_layout/_raw/validations/.

---

## 9) Evidence and References
Representative locations identified during audit:
- Thread reconstruction: src/server/context/thread_context.py (enhances `prompt`, not `messages`).
- Handler hook: src/server/handlers/request_handler.py (calls reconstruct and then routes without messages enrichment).
- Secure input validator: src/core/validation/secure_input_validator.py (not consistently used by Kimi upload paths).
- Kimi provider: src/providers/kimi.py (no provider‑level streaming function).
- Kimi tool: tools/providers/kimi/kimi_tools_chat.py (contains streaming logic today).

Planned evidence capture:
- After fixes, run WS MCP: GLM browse + Kimi stream smoke; store raw JSONL chunks and final outputs into docs/System_layout/_raw/validations/ with timestamps.

---

## 10) Acceptance & Sign‑off Checklist
- [ ] Registry is single‑sourced; diagnostics/self_check discoverable
- [ ] Context injection works for both prompt and messages tools
- [ ] Kimi provider streaming implemented; chunk aggregation and metadata.streamed present
- [ ] Path validation unified; docs updated
- [ ] Decomposition PRs created with tests
- [ ] WS MCP smoke evidence files saved with real model outputs

