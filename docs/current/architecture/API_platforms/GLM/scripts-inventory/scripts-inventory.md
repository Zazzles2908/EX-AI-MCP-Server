## GLM / Z.ai Scripts Inventory

A concise inventory of all scripts related to GLM (ZhipuAI) and Z.ai endpoints in this repository. Each entry lists the script name, location, and a brief purpose.

- Name: glm_agents.py
  - Location: tools/providers/glm/glm_agents.py
  - Purpose: Implements GLM Agent API tools:
    - GLMAgentChatTool (POST https://api.z.ai/api/v1/agents)
    - GLMAgentGetResultTool (POST /agents/async-result)
    - GLMAgentConversationTool (POST /agents/conversation)
    Uses GLM_API_KEY; returns raw JSON/text and appends a conversation_meta hint when available.

- Name: glm_files.py
  - Location: tools/providers/glm/glm_files.py
  - Purpose: File utilities and multi-file chat for GLM:
    - GLMUploadFileTool: Uploads a file to GLM Files API (purpose=agent).
    - GLMMultiFileChatTool: Uploads multiple files then performs a chat call via the GLM provider.
    Resolves provider from ModelProviderRegistry, falls back to GLMModelProvider with GLM_API_KEY.

- Name: glm_files_cleanup.py
  - Location: tools/providers/glm/glm_files_cleanup.py
  - Purpose: CLI utility to list and optionally delete GLM/Zhipu files in your account. Dry-run by default.
    Uses HttpClient against GLM_API_URL for GET /files and DELETE /files/{file_id}. Supports filters like --older-than-days.

- Name: glm_web_search.py
  - Location: tools/providers/glm/glm_web_search.py
  - Purpose: Direct wrapper for Z.ai Web Search API (POST https://api.z.ai/api/paas/v4/web_search).
    Provides GLMWebSearchTool with parameters like search_engine, search_query, count. Auth via GLM_API_KEY or ZAI_API_KEY.

- Name: glm.py (GLMModelProvider)
  - Location: src/providers/glm.py
  - Purpose: Core provider implementation for GLM models (ZhipuAI). Defines supported models (e.g., glm-4.5-flash, glm-4.5),
    validates names/capabilities, and performs content generation. Prefers official zhipuai SDK if available, otherwise falls
    back to an internal HTTP client with Bearer Authorization to GLM base URL (default https://api.z.ai/api/paas/v4).

- Name: provider_config.py (GLM gating)
  - Location: src/server/providers/provider_config.py
  - Purpose: Detects GLM API key presence (GLM_API_KEY or ZHIPUAI_API_KEY), safely imports GLMModelProvider, and marks the GLM
    provider as available/valid. Also influences whether native APIs are enabled at startup.

- Name: server.py (GLM tool registration)
  - Location: server.py
  - Purpose: Registers GLM-specific tools into the tool registry when available:
    glm_upload_file, glm_multi_file_chat, glm_agent_chat, glm_agent_get_result, glm_agent_conversation, glm_web_search.

- Name: providers.py (GLMProvider)
  - Location: providers.py
  - Purpose: Alternate/legacy high-level provider abstraction including GLMProvider with native web browsing semantics (glm-4.5-flash).
    Handles API key validation, prepares messages, and simulates/coordinates provider invocations (zhipuai client expected in real use).

- Name: provider_capabilities.py (GLM env diagnostics)
  - Location: tools/capabilities/provider_capabilities.py
  - Purpose: Diagnostic tool that summarizes provider readiness from environment variables (e.g., GLM_API_KEY, GLM_API_URL,
    GLM_AGENT_API_URL, GLM_WEBSEARCH_BASE) and can list currently loaded tools. Useful for verifying GLM/Z.ai configuration.

Notes
- Environment example files (.env.example, .env.new) contain GLM configuration keys but are not scripts.
- Compiled artifacts under __pycache__ are excluded.

