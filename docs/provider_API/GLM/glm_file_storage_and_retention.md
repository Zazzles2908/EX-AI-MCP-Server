# GLM File Storage and Retention

## Where uploads are stored
- When you run `glm_upload_file` (or `glm_multi_file_chat` which uploads first), files are uploaded to your Z.ai (GLM) account via the GLM Files API (base: `GLM_API_URL`, default `https://api.z.ai/api/paas/v4`).
- The API returns a `file_id`. Our tools treat this as an opaque handle managed by Z.ai. Content retrieval via this path is not implemented in our GLM tools (unlike Kimi's file-extract flow).

## Local cache behavior
- We maintain a local mapping of `sha256(file) -> provider -> file_id` in `.cache/filecache.json` via `utils/file_cache.FileCache`.
- Default TTL is 7 days (`FILECACHE_TTL_SECS=604800`). After TTL, the cached mapping expires and the next request re-uploads the file.
- Env controls:
  - `FILECACHE_ENABLED=true|false`
  - `FILECACHE_PATH=.cache/filecache.json`
  - `FILECACHE_TTL_SECS=604800`

## Server-side retention on Z.ai
- Uploaded files live in your Z.ai account storage until deleted. The repo includes a maintenance utility:
  - `tools/providers/glm/glm_files_cleanup.py` — lists and deletes files via `GET /files` and `DELETE /files/{id}`.
- If you run the WS daemon in long-lived scenarios, we recommend a periodic cleanup policy (e.g., delete files older than N days) to control costs/storage.

## Recommended policy
- For how-to view/manage files, see also: docs/provider_API/GLM/glm_file_visibility_howto.md
- Default: keep `FILECACHE_ENABLED=true` for dedupe; set `FILECACHE_TTL_SECS` between 1–7 days depending on workload repetition.
- Periodic cleanup: schedule `python -X utf8 tools/providers/glm/glm_files_cleanup.py --older-than-days 7 --no-dry-run` off-hours.
- Sensitive data: consider disabling cache for highly sensitive files, and run cleanup more aggressively.

## Notes
- Files uploaded for `glm_multi_file_chat` are referenced by name in the system preamble for context; their raw content is not fetched by our GLM code path at present.
- If Z.ai exposes stable content-retrieval for uploaded files, we can extend the provider and tool to pull and summarize content similar to Kimi's path.

