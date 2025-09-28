# Kimi (Moonshot) API – Files

## Authentication
- HTTP Authorization: `Bearer ${MOONSHOT_API_KEY}`
- Base URL: `https://api.moonshot.ai/v1`

## Upload File
- POST `/files` (multipart/form-data)
- Fields: `file` (binary), `purpose` (e.g., `file-extract`)

## List Files
- GET `/files`

## Delete File
- DELETE `/files/{file_id}`

## Notes
- For extraction, set `purpose: "file-extract"`.

