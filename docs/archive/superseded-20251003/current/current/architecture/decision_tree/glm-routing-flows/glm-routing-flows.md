# Decision Tree – GLM Routing Flows

## Purpose
Document GLM-specific branches in the routing decision tree, including native web search selection.

## Current Implementation
- RouterService chooses GLM models based on defaults and hints; capabilities adapter can inject web_search tools.

## Integration Points
- RoutePlan.web_search=required|allowed|off influences GLM payload tools/tool_choice.

## Status
- 🔧 Requires Adjustment: RoutePlan not yet surfaced; web_search requirement not enforced at selection time.

## Next Steps
1) Add RoutePlan and enforce web_search policy during provider/model selection.
2) Add tests to validate GLM path when browsing is required.

