# Tools functionality overview (GLM/Z.ai focus)

This summarizes the active tools surfaced by the server and the GLM-specific tools registered dynamically.

## Core/general tools (from server tool registry)
- chat: Basic model chat/completions
- analyze: General code/system analysis
- docgen: Documentation generation
- codereview: Code review workflow
- precommit: Pre-commit validation
- debug: Root-cause analysis
- secaudit: Security audit
- refactor: Refactoring analysis
- tracer: Code tracing (precision/dependencies)
- testgen: Test generation
- planner: Sequential planning
- consensus: Multi-model consensus workflow
- thinkdeep: Structured deep investigation
- challenge: Critical analysis handler for disagreements
- listmodels: List configured models/providers with capabilities
- version/selfcheck: Server info and diagnostics

(Note: Exact set may vary by build; refer to server.py TOOL_MAP/registration.)

## GLM provider-specific tools
- glm_upload_file (tools/providers/glm/glm_files.py)
  - Upload a file to Z.ai storage; returns file_id
- glm_multi_file_chat (tools/providers/glm/glm_files.py)
  - Uploads multiple files (if needed) and chats with GLM using those files as context
- glm_agent_chat (tools/providers/glm/glm_agents.py)
  - Calls Z.ai Agents API /v1/agents for agent chat
- glm_agent_get_result (tools/providers/glm/glm_agents.py)
  - Poll async result for an agent operation
- glm_agent_conversation (tools/providers/glm/glm_agents.py)
  - Fetch agent conversation history /v1/agents/conversation
- glm_web_search (tools/providers/glm/glm_web_search.py)
  - Calls Z.ai /api/paas/v4/web_search; returns search results

## Notes
- Provider mediation: glm_upload_file and glm_multi_file_chat use `src/providers/glm.py` (SDK-first) via the provider registry.
- Direct HTTP tools: glm_agent_* and glm_web_search use direct `requests` calls; can be unified under a provider adapter later.

