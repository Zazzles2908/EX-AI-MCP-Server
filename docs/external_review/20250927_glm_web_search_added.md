# GLM Web Search tool added (2025-09-27)

- Tool name: glm_web_search
- Endpoint: POST https://api.z.ai/api/paas/v4/web_search
- File: tools/providers/glm/glm_web_search.py
- Registration: server.register_provider_specific_tools() adds glm_web_search

Input shape (subset)
- search_query: string (required)
- search_engine: string (default: search-prime)
- count: int (default: 10)
- search_domain_filter: string (optional)
- search_recency_filter: enum [oneDay, oneWeek, oneMonth, oneYear, all] (default: all)
- request_id, user_id: optional

Output
- Raw JSON text from Z.ai (includes search_result[])

Note
- WS daemon restart required to load this new tool into the running process.
- ws_probe updated to exercise glm_web_search when available.

