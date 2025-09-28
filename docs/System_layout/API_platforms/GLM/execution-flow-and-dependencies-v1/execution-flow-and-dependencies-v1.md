# EX-AI MCP Server: Execution Flow and Dependencies (GLM/Z.ai Focus) – v1 (Deprecated)

Last updated: {{today}}

> Note: This v1 document is retained for historical reference. See `../execution-flows/execution-flows.md` for the current view.

## Scope
- Entry points from external clients to response delivery (stdio MCP and WS daemon)
- Inter-script dependencies (imports/calls) along the critical path
- GLM/Z.ai flows: glm_multi_file_chat, glm_agent_* and glm_web_search
- Cleanup preparation: critical vs legacy/duplicate vs orphaned vs dev-only
- Staging strategy for safe removals

---

[Content preserved from v1]

