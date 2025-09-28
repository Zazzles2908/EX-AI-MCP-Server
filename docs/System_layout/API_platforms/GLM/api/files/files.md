# GLM (Z.ai) API – Files

## Authentication
- HTTP Authorization: `Bearer ${ZAI_API_KEY}`
- Base URL: `https://api.z.ai/api/paas/v4`

## Upload File
- POST `/files` (multipart/form-data)
- Fields: `file` (binary), `purpose` (e.g., `agent`)
- Max size: 100MB
- Retention: ~180 days (provider policy; verify account plan)

## List Files
- GET `/files`

## Delete File
- DELETE `/files/{file_id}`

## Notes
- Return shape may vary (list vs `{data: [...]}`); normalize accordingly.

