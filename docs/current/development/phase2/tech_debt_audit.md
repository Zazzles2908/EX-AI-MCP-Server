# Technical Debt Audit (Derived from Validation)

## Summary
This document captures gaps and actionable fixes identified during EXAI-WS MCP validation.

## Issues & Actions

1) Auto-mode continuation inconsistency in Chat
- Observation: Follow-up call using continuation_id failed with "Model 'auto' is not available" while the initial call resolved 'auto' to glm-4.5-flash.
- Impact: Breaks multi-turn continuity and user experience.
- Likely cause: Loss of provider/model flag propagation in continuation path.
- Actions:
  - [ ] Ensure model resolution occurs identically for initial and continued turns.
  - [ ] Add unit test covering continuation_id flow with auto model.
  - [ ] Log chosen provider/model on every turn.

2) Schema normalization for tool input schemas
- Observation: VS Code extension previously rejected schemas using non-standard `nullable` and inconsistent presence of `$schema`.
- Impact: Tool registration/preview errors in some clients.
- Actions:
  - [ ] Enforce `$schema`: draft-07 and `additionalProperties: false` across all tool schemas.
  - [ ] Add validator test to assert JSON Schema compliance for every tool.

3) WS vs Stdio tool surface differences
- Observation: Different tool counts across transports; some diagnostics exist only on stdio.
- Impact: Confusion for users; inconsistent capabilities.
- Actions:
  - [ ] Document intentional differences; expose missing essentials to WS if appropriate.
  - [ ] Add transport parity checklist.

4) Evidence management & indexing
- Observation: Raw artifacts scattered (System_layout/_raw, augmentcode_phase2/raw, sweep_reports/*).
- Impact: Harder to audit quickly.
- Actions:
  - [ ] Maintain single Phase 2 index (docs/augmentcode_phase2/index.md) linking to all raw artifact locations.
  - [ ] Add script to generate an updated evidence map.

5) Path policy harmonization
- Observation: Chat requires absolute file paths; Kimi upload accepted relative paths in some contexts.
- Impact: Inconsistent user expectations.
- Actions:
  - [ ] Document standard: absolute paths for all file parameters.
  - [ ] Enforce/normalize at tool adapters where feasible.

## Acceptance Criteria
- Passing schema validation test suite for all tools.
- Reproduced and fixed auto-mode continuation across two turns with continuation_id.
- Updated docs with parity notes and unified evidence index.
- Added smoke tests for path policy.

