# Phase 8 Live EXAI-WS MCP Validation Report

TS: 2025-09-28T22:25:26Z

## Runs
1) GLM Web Browse
- Tool: glm_web_search_EXAI-WS
- Request: search_query="Validate GLM web browsing: latest ZhipuAI GLM-4.5 announcements and docs", count=5, search_recency_filter=oneYear
- Response: see docs/System_layout/_raw/phase8_live_glm_websearch_raw.json
- Evidence of live model output: provider returned structured search_result with real links (z.ai blog, bigmodel docs, modelscope) and a publish_date string localized. Content snippets are non-deterministic and cannot be trivially hardcoded. Request_id present.

2) Kimi Upload/Extract
- Tool: kimi_upload_and_extract_EXAI-WS
- Request: files=[docs/System_layout/_raw/kimi_upload_sample.txt], purpose=file-extract
- Response: see docs/System_layout/_raw/phase8_live_kimi_upload_extract_raw.json
- Evidence of live file processing: returned role=system, file metadata (file_type, filename, _file_id) and echoed decoded content including unicode (café, naïve, résumé) and JSON payload. Presence of a provider-generated file id (_file_id) indicates real processing.

## Authenticity Checks
- Requests and responses saved with timestamps and full payloads
- GLM web_search: contains multiple authoritative URLs and provider-specific metadata fields
- Kimi upload: unique _file_id and proper UTF-8 handling of unicode characters

## Status
- GLM web browsing: VALIDATED
- Kimi upload/extract: VALIDATED

## Issues/Notes
- None observed during these smoke tests. For deeper E2E streaming/upload/cache tests, run extended scripts against provider endpoints and capture chunk timelines and cache tokens.

