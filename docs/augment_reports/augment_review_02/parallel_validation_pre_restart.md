# Parallel Validation – Pre-Restart Strategy Review (STDIO + RAW Mirror)

Date: 2025-09-27
Repo: c:\Project\EX-AI-MCP-Server

## Scope
- Confirm the plan to unblock MCP stdio initialize and validate the raw mirror
- Include EXAI MCP independent review (GLM glm-4.5) and our own local assessment
- Do NOT restart server yet; this is pre-restart review

## Our assessment (local)
- Current failure: stdio E2E client fails during initialize with `McpError: Connection closed`
- We removed stale lock (logs/exai_server.pid) and forward env flags; failure persists
- Providers configure successfully when imported in-process (diagnose script); suggests an early exit specific to stdio launch path
- Raw mirror will only populate after the first successful stdio tool call
- Key suspects: executable mismatch between wrapper and E2E; insufficient stderr/err logging; mixed log directories (logs/ vs .logs/)

### Proposed plan (pre-restart)
1) Clean logs and ensure no stale state
2) Use venv python consistently for wrapper and E2E
3) Enable stderr breadcrumbs; capture wrapper_error.log on failure
4) Run E2E stdio with raw=true and lock disabled (≤60s)
5) Verify toolcalls_raw.jsonl (no system prompt; redaction + size cap)
6) Toggle raw off; verify raw unchanged while summaries update
7) Keep raw ON as default thereafter

## EXAI MCP review (independent) – GLM glm-4.5
Verdict: AGREE (with amendments)

Amendments:
- Add a pre-cleanup step to remove old logs before testing
- Ensure E2E uses the same venv Python as wrapper
- Watch for log path inconsistency: server `.logs/` vs wrapper/tools `logs/`
- Validate raw content redaction/size-capping explicitly

Risks:
- Log path inconsistency could hide raw entries
- E2E may spawn a different interpreter than the wrapper
- Missing handshake timeout in E2E can mask underlying error signatures

Mini checklist:
- Clean logs: rm old .log/.jsonl files
- Set EXAI_LOCK_DISABLE=true + breadcrumbs
- Run E2E with raw=true + venv python
- Check wrapper_error.log + stderr output
- Verify toolcalls_raw.jsonl entries exist
- Re-run E2E with raw=false
- Confirm raw unchanged, summaries updated

### EXAI RAW (verbatim)
RAW START >>>AGREEx7 123456
Plan viable with log path fixes and venv alignment. Focus on handshake timeout.
<<< RAW END

Provider/Model reported by EXAI: GLM glm-4.5

## Consolidated next steps (before restart)
- [ ] Purge old logs in both `logs/` and `.logs/` (keep rotation policy)
- [ ] Ensure `.venv\Scripts\python.exe` is used by both wrapper and E2E client
- [ ] Add/verify stderr breadcrumb and ensure wrapper writes any exception to logs/wrapper_error.log
- [ ] Run stdio E2E with raw=true and lock disabled (≤60s)
- [ ] Inspect `.logs/toolcalls_raw.jsonl` for new entries (no system prompt; redaction ok)
- [ ] Run raw=false and confirm raw file unchanged while summaries update
- [ ] Leave raw=true; proceed later to router decision sample capture

