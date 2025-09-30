# Script Inventory and Phase Mapping

This document lists key scripts/modules and maps them to roadmap phases (2–8 complete, 6 context caching added).

## Core Routing & Providers
- src/router/service.py — Phase 3/4/5/7 (routing, hints, budget, health, telemetry)
- src/router/classifier.py — Phase 4 (classification + complexity)
- src/router/synthesis.py — Phase 5 (optional synthesis hop)
- src/providers/capabilities.py — Phase 2/3 (capabilities, web_search tooling)
- src/providers/registry.py — Phase 2 (provider registry)

## Tools
- tools/chat.py — Phase 5 (flags), Phase 6 (context caching header), Phase 8 (workflows test target)
- tools/simple/base.py — Tool base class (foundation)

## Conversation & Context
- src/conversation/history_store.py — Phase 5 (continuation context)
- src/conversation/memory_policy.py — Phase 5 (context assembly)
- src/conversation/cache_store.py — Phase 6 (context caching consistency)

## Observability & Health
- utils/observability.py — Phase 3/7 (routeplan/telemetry/aggregates)
- utils/health.py — Phase 7 (circuit skip)

## Docs & Validation
- utils/docs_validator.py — Cross-Cutting Docs (link + kebab checks)
- scripts/validate_docs.py — Cross-Cutting Docs (CLI wrapper)
- scripts/health/validate_system_health.py — Health runner for selected test suites

## Tests (Illustrative)
- tests/phase4/* — Classification & routing hints
- tests/phase5/* — Flags/budget + synthesis hop + continuation
- tests/phase6/* — Context caching consistency
- tests/phase7/* — Telemetry + health/circuit
- tests/phase8/* — Router/provider/workflow validation
- tests/docs/test_docs_validator.py — Cross-Cutting Docs validator

## Evidence (_raw)
- docs/System_layout/_raw — Phase artifacts and MCP memos (Phase 2–8; Phase 6 caching; Phase 8 live validations)

