# EX-AI MCP Server – Augment Cleanup and Implementation Plan (Deepagent-aligned)

Date: 2025-09-26
Owner: Augment Agent
Scope: Align the project to deepagent’s production-ready architecture and test posture; deliver a massive cleanup across env, routing, server structure, docs, and CI.

## 1) Sources considered
- project_analysis.md
- codebase_analysis.md
- TEST_SUITE_SUMMARY.md
- External review (20250926_review/*)
- Current repo state (PR #5: combined PR3+PR4, secret scrubs; requirements.txt includes zhipuai>=2.1.0)

## 2) Objectives
- Establish production-ready, manager-first routing with GLM‑4.5‑Flash and Kimi specialization
- Simplify configuration and remove legacy/experimental pathways
- Improve observability (routing logs, metrics, JSONL)
- Maintain a comprehensive, safe test posture (mocks by default; real keys optional)
- Reduce documentation clutter; provide a single source of truth
- Prepare CI and hygiene for sustainable development

## 3) Phased plan (what I intend to do)

### Phase 1: Stabilize + Observe (Immediate)
1. Environment consolidation
   - Canonical vars: GLM_API_KEY, KIMI_API_KEY (retain ZHIPUAI_API_KEY/MOONSHOT_API_KEY as aliases with deprecation notices)
   - .env minimal; .env.example mirrored with friendly guidance (Kimi base_url=https://api.moonshot.ai/v1)
2. Intelligent routing observability
   - Add structured logs for each decision: provider, confidence, reasoning, estimated_cost, estimated_time, fallback_used, tokens_used
   - Emit JSONL logs + lightweight counters (decisions, errors, fallbacks)
3. Test posture hardening
   - Ensure unit tests run fully without real keys (mocks). Mark any real‑API tests to skip unless keys present
4. Repo hygiene (quick wins)
   - Ensure requirements.txt is minimal and accurate (zhipuai present ✓)
   - Add pre-push secret scan and basic lint in CI (no creds)

Deliverables: env alignment diffs, routing log output samples, CI stub, short operator guide.

### Phase 2: Massive cleanup + Structure (Near-term)
1. Server modularization
   - Gradually decompose server.py into src/server/ modules (connection, registry, handlers); keep public surface lean
2. Remove/disable legacy and experimental flags
   - Keep intelligent manager as the primary path; remove duplicative or unused feature flags and pathways
3. Script & tools reorganization (clean structure)
   - Move standalone scripts into standardized subfolders; add shims if needed
4. Documentation consolidation
   - Archive/relocate older reports; keep a single authoritative set (decision tree, quick start, deployment checklist, troubleshooting)

Deliverables: refactored server layout, reduced flags, reorganized scripts, updated docs & diagrams.

### Phase 3: Optimization + CI/CD (Short-term)
1. Performance checkpoints
   - Track routing latencies, fallback rate, provider error rates, token usage; record baseline
2. CI/CD enhancement
   - Add coverage gates (unit), style checks, and smoke validations; no real-key tests in CI
3. Provider consistency
   - Prefer native zhipuai SDK path for GLM; maintain stable OpenAI-compatible path for Kimi; ensure clear error messages and timeouts

Deliverables: metrics snapshots, CI workflow files, provider configuration notes, and a living performance baseline.

## 4) Test suite integration (from TEST_SUITE_SUMMARY)
- Retain comprehensive categories (MCP protocol, routing, providers, e2e, configuration). Keep load testing optional and separate (Locust)
- Keep run_tests.py as a convenience wrapper, with environment derived from OS vars; no embedded secrets
- Skip integration tests automatically if keys are absent; enable when provided

## 5) Branching and PR workflow
- Work off the current combined branch until PR #5 is merged into production-ready-v2
- Next PRs will be grouped by phases above with clear, reviewable diffs
- Never push to main; open PRs against the designated base (production-ready-v2 or the staging branch you select)

## 6) Risks and mitigations
- Refactor risk: Limit Phase 2 to structural movement without behavior changes; validate via unit tests
- Observability overhead: Make logging levels configurable; default to INFO, structured
- CI fragility: Keep CI minimal at first (lint + unit) and expand gradually

## 7) Validation plan
- After Phase 1: run WS daemon and perform real GLM web-browse + Kimi file validations with unpredictable prompts; store raw outputs under docs/augment_reports/augment_review_02 and verify routing logs
- After Phase 2: rerun unit/E2E (mocked) and compare routing/latency snapshots
- After Phase 3: confirm CI stability and coverage thresholds

## 8) Immediate next actions
- Prepare env alignment change set
- Implement routing decision logging + JSONL
- Add CI skeleton (lint + tests + secret scan)
- Draft decision-tree diagram and updated deployment checklist

This plan aligns with deepagent’s architecture and test posture while executing the requested massive cleanup in safe, high‑impact phases.

