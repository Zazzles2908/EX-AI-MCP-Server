# Tool Function Registry – GLM Integration

## Purpose
Describe how GLM-specific tools are registered, gated, and invoked via the Tool Registry.

## Current Implementation
- server.py registers GLM tools when GLM is available: glm_upload_file, glm_multi_file_chat, glm_agent_*, glm_web_search.
- tools/providers/glm/* implement the tool logic.

## Integration Points
- Capabilities adapter injects web_search when requested.

## Status
- ✅ Existing & Complete (registration) ; 🔧 Requires Adjustment (capability-aware routing enforcement).

## Next Steps
1) Ensure tools can request web_search injection and that routing respects policy.
2) Add registry status tool that reports GLM tool availability and env gating.

