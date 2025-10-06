# GLM – Native Web Search

## Purpose
Use GLM provider‑native web browsing capability instead of custom HTTP search tools.

## Current Implementation (code paths)
- src/providers/capabilities.py: GLMCapabilities.get_websearch_tool_schema() → tools=[{"type":"web_search","web_search":{}}].
- src/providers/glm.py: generate_content accepts tools/tool_choice and forwards via SDK/HTTP.
- Boundary/tooling: request_handler may set arguments["use_websearch"]; tools should request injection via capabilities.

## Parameters
- GLM_ENABLE_WEB_BROWSING (default true)

## Dependencies
- zhipuai SDK or HTTP endpoint /chat/completions

## Integration Points
- Tools set use_websearch; provider capability adapter injects schema.

## Status Assessment
- 🔧 Requires Adjustment: Injection path exists but route plan does not mark web_search as required/allowed; not enforced in provider selection.

## Implementation Notes
- Ensure tool_choice="auto" when tools are present to let GLM call web_search.

## Next Steps
1) Add RoutePlan.web_search = required|allowed|off and bias provider/model selection accordingly.
2) Add tests asserting GLM request payload contains correct tools/tool_choice when use_websearch=true.

