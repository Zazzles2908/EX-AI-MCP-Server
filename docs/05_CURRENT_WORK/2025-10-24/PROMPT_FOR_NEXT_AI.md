# PROMPT FOR NEXT AI AGENT

Copy and paste this prompt to the next AI agent:

---

**URGENT: Multiple errors need fixing in the EXAI-MCP Docker container.**

**CRITICAL INSTRUCTIONS:**

1. **Read the handover document first:**
   - File: `docs/05_CURRENT_WORK/HANDOVER_TO_NEXT_AI__URGENT_FIXES_NEEDED__2025-10-24.md`
   - This contains all context, known issues, and what needs fixing

2. **Check Docker logs immediately:**
   ```bash
   docker logs exai-mcp-daemon --tail=200
   ```
   - Document all errors you find
   - Fix them systematically

3. **Be cost-conscious:**
   - EXAI tool calls cost ~$0.35 each
   - Use free tools (view, codebase-retrieval) first
   - Only use EXAI for complex validation when absolutely necessary

4. **Required reading before starting:**
   - `docs/05_CURRENT_WORK/HANDOVER_TO_NEXT_AI__URGENT_FIXES_NEEDED__2025-10-24.md`
   - `docs/05_CURRENT_WORK/SDK_ARCHITECTURE_TRUTH__CRITICAL_CORRECTION__2025-10-24.md`
   - `docs/05_CURRENT_WORK/COST_INVESTIGATION_FINDINGS__2025-10-24.md`

5. **Known issues to check:**
   - Monitoring dashboard async/await error
   - AI Auditor authentication error (401)
   - Web search pattern matching warnings
   - Any other errors in current Docker logs

6. **Validate the recent fix:**
   - Test that Supabase queries reduced from 4 to 1 per request
   - Verify global storage singleton is working correctly

**Your goal:** Fix all errors in Docker logs and ensure the system is stable.

**Working directory:** `c:\Project\EX-AI-MCP-Server`

**Start by reading the handover document, then check the logs.**

---

**END OF PROMPT**

