# GLM File Visibility — How To

This note explains practical ways to view and manage files you upload via GLM tools.

## 1) Vendor account console (recommended if available)
- Sign in to your Z.ai / ZhipuAI account console.
- Navigate to the section typically labeled “Files”, “Assets”, or “Data”.
- Filter by date or name; expect the identifiers to match the `file_id` returned by our tools (or shown by the cleanup utility).
- You can delete files directly in the console UI when no longer needed.
- Caveat: Console label/URL may vary by region/tenant/plan; if you don’t see “Files”, use the API path below.

## 2) Use the cleanup utility (no coding)
- Run in dry‑run to list:
  - `python -X utf8 scripts/maintenance/glm_files_cleanup.py --list --limit 200`
- Show only a summary count:
  - `python -X utf8 scripts/maintenance/glm_files_cleanup.py --summary`
- Delete older than N days (dry‑run default):
  - `python -X utf8 scripts/maintenance/glm_files_cleanup.py --older-than-days 7`
- Actually delete:
  - `python -X utf8 scripts/maintenance/glm_files_cleanup.py --older-than-days 7 --no-dry-run`

Requirements:
- Environment variables set: `GLM_API_KEY` and `GLM_API_URL` (default v4 base).

## 3) Direct API (advanced)
- List files (pseudocode HTTP):
  - `GET {GLM_API_URL}/files` with `Authorization: Bearer <GLM_API_KEY>`
- Delete a file:
  - `DELETE {GLM_API_URL}/files/{file_id}`
- Note: Response shape can be either a list or `{ data: [...] }` depending on API version; our utility handles common variants.

## 4) Local cache awareness
- Our tools maintain a local `sha256 -> file_id` cache at `.cache/filecache.json` with a default TTL of 7 days.
- Expiration removes only the local mapping; provider‑side files remain until you delete them via console/API.

See also: file-storage-and-retention/file-storage-and-retention.md

