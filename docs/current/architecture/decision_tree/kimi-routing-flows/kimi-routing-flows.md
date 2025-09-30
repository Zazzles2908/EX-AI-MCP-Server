# Decision Tree  Kimi Routing Flows

## Purpose
Document Kimi-specific branches when long context or file processing dominates.

## Current Implementation
- RouterService can bias long-context models; Kimi provider supports large windows and context cache.

## Integration Points
- RoutePlan should reflect cache/stream flags; workflows must pass session_id/call_key for cache reuse.

## Status
-  Requires Adjustment: classification/complexity not consistently applied; streaming disabled by default.

## Next Steps
1) Add complexity thresholds to bias Kimi.
2) Add env-gated streaming and verify via smoke tests.

