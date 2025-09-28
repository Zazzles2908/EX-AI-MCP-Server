# GLM/Z.ai Execution Flows

This doc focuses purely on GLM tool flows and includes functional Mermaid diagrams.

## glm_multi_file_chat
```mermaid
sequenceDiagram
  participant Client
  participant Server
  participant Handler as request_handler
  participant Tool as GLMMultiFileChatTool
  participant Prov as GLMModelProvider
  Client->>Server: MCP call_tool(glm_multi_file_chat)
  Server->>Handler: delegate
  Handler->>Tool: execute(arguments)
  loop files
    Tool->>Prov: upload_file(file)
    Prov-->>Tool: file_id
  end
  Tool->>Prov: generate_content(prompt, system_preamble)
  Prov-->>Tool: content
  Tool-->>Handler: {content, uploaded}
  Handler-->>Client: TextContent[]
```

## glm_agent_*
```mermaid
graph TD
  A[call_tool glm_agent_chat]-->B[tools/providers/glm/glm_agents.py]
  B-->C[POST https://api.z.ai/api/v1/agents]
  A2[glm_agent_get_result]-->B2[gl m_agents.py]
  B2-->C2[POST .../agents/async-result]
  A3[glm_agent_conversation]-->B3[glm_agents.py]
  B3-->C3[POST .../agents/conversation]
```

## glm_web_search
```mermaid
graph TD
  A[call_tool glm_web_search]-->B[tools/providers/glm/glm_web_search.py]
  B-->C[POST https://api.z.ai/api/paas/v4/web_search]
```

## Stdio vs WS transport (both converge)
```mermaid
graph TD
  A[MCP stdio]-->B[server.py]
  A2[WS daemon]-->C[src/daemon/ws_server.py]
  B-->D[handlers/request_handler]
  C-->D
  D-->E[tool.execute to provider]
```

