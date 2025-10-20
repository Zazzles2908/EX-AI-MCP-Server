# EXAI MCP Server: Quick Reference Card
**Date:** 2025-10-19  
**For:** Next AI Agent

---

## 🚀 QUICK START

### The 7-Step Process (Memorize This!)
```
1. INVESTIGATE → 2. CONSULT EXAI → 3. FIX → 4. REBUILD → 5. TEST → 6. VERIFY LOGS → 7. MOVE ON
```

### Golden Rules
- ✅ ALWAYS use `model="glm-4.6"`
- ✅ ALWAYS check Docker logs after changes
- ✅ ALWAYS fix discovered errors immediately
- ✅ NEVER ignore errors to "fix later"
- ✅ NEVER assume - verify everything

---

## 🛠️ EXAI Tool Quick Reference

### When to Use Which Tool

⚠️ **CRITICAL WARNING (Bug #10):** ALL workflow tools can loop infinitely! Circuit breaker detects stagnation but doesn't abort. Use `chat_EXAI-WS` for safety or monitor logs closely!

| Tool | Use When | Status | Key Params |
|------|----------|--------|------------|
| `chat_EXAI-WS` | Quick questions & complex reasoning | ✅ **SAFE** | `prompt`, `files`, `model` |
| `debug_EXAI-WS` | Bug investigation | ⚠️ **CAN LOOP** | `step`, `findings`, `hypothesis`, `confidence` |
| `codereview_EXAI-WS` | Code quality review | ⚠️ **CAN LOOP** | `step`, `findings`, `relevant_files`, `confidence` |
| `analyze_EXAI-WS` | Architecture analysis | ⚠️ **CAN LOOP** | `step`, `findings`, `relevant_files`, `confidence` |
| ~~`thinkdeep_EXAI-WS`~~ | ~~Complex reasoning~~ | ❌ **BROKEN** | Bug #9/#10: Infinite loop |

**Recommendation:** Use `chat_EXAI-WS` for all tasks until Bug #10 is fixed!

### Tool Call Template

**SAFEST OPTION (Recommended):**
```python
chat_EXAI-WS(
    prompt="I need help debugging X. Here's what I know: [detailed context]",
    files=["c:\\Project\\EX-AI-MCP-Server\\path\\to\\file.py"],
    model="glm-4.6",
    use_websearch=false
)
```

**Workflow Tools (⚠️ Monitor logs for infinite loops!):**
```python
debug_EXAI-WS(
    step="What you're investigating",
    findings="What you've discovered so far",
    hypothesis="Your theory about the cause",
    relevant_files=["c:\\Project\\EX-AI-MCP-Server\\path\\to\\file.py"],
    model="glm-4.6",
    confidence="certain",  # ⚠️ Set to "certain" when done to force early termination!
    use_websearch=false
)
```

**⚠️ IMPORTANT:** If using workflow tools, watch Docker logs for "Confidence stagnant" warnings. If you see 3+ consecutive warnings, the tool is stuck in an infinite loop!

---

## 📊 Docker Log Commands

### Essential Commands
```bash
# Check recent logs
docker logs exai-mcp-daemon --tail 100

# Follow logs in real-time
docker logs -f exai-mcp-daemon

# Search for errors
docker logs exai-mcp-daemon --tail 200 | grep -i "error\|exception\|failed"

# Search for specific conversation
docker logs exai-mcp-daemon --tail 200 | grep "conversation_id_here"

# Check for success patterns
docker logs exai-mcp-daemon --tail 100 | grep -i "success\|saved\|uploaded"
```

### Success vs. Failure Patterns
```bash
# ✅ Success Patterns
"INFO: Saved conversation"
"INFO: [CONTEXT_PRUNING] Loaded X messages"
"HTTP/2 200 OK" or "HTTP/2 201 Created"

# ❌ Failure Patterns
"WARNING: Failed to read"
"ERROR:" or "CRITICAL:"
"Exception:" or "Traceback:"
"Circuit breaker triggered"
```

---

## 🔧 Container Management

### Rebuild Container
```bash
docker-compose down
docker-compose up -d --build
```

### Check Container Status
```bash
docker ps -a | grep exai-mcp-daemon
# Wait for "(healthy)" status
```

### Quick Restart
```bash
docker-compose restart exai-mcp-daemon
```

---

## 🎯 Common Scenarios

### Scenario 1: Tool Call Fails
```
1. Check Docker logs immediately
2. Look for error patterns
3. Retry with modified parameters
4. If still failing, use chat_EXAI-WS
5. Document the failure
```

### Scenario 2: Discover New Bug While Working
```
1. STOP current task
2. FIX the discovered bug IMMEDIATELY
3. TEST thoroughly
4. VERIFY in Docker logs
5. DOCUMENT the fix
6. RETURN to original task
```

### Scenario 3: WebSocket Connection Drops
```
1. Note the error: "no close frame received or sent"
2. Check Docker logs for root cause
3. Retry the operation
4. If persists, restart container
```

---

## 📝 Investigation Checklist

Before calling EXAI:
- [ ] Reproduced the issue
- [ ] Checked Docker logs for error patterns
- [ ] Identified the file(s) involved
- [ ] Formed an initial hypothesis
- [ ] Gathered relevant file paths

After EXAI consultation:
- [ ] Understood the root cause
- [ ] Implemented targeted fix
- [ ] Rebuilt container
- [ ] Tested the fix
- [ ] Verified in Docker logs
- [ ] Updated task manager
- [ ] Documented the fix

---

## 🚨 Red Flags

**Stop and Reconsider If:**
- ⚠️ You're about to ignore an error you discovered
- ⚠️ You haven't checked Docker logs after a change
- ⚠️ You're assuming something works without testing
- ⚠️ You're moving on without verifying the fix
- ⚠️ You're using `model="auto"` (use `glm-4.6` instead)

---

## 📚 Key Files to Know

### Configuration
- `.env.docker` - Docker environment variables
- `docker-compose.yml` - Container configuration

### Core System
- `tools/chat.py` - Chat tool implementation
- `tools/workflow/orchestration.py` - Workflow orchestration
- `tools/workflow/performance_optimizer.py` - Path normalization
- `utils/conversation/threads.py` - Thread context management

### Documentation
- `docs/current/AGENT_HANDOFF_GUIDE_2025-10-19.md` - Full guide
- `docs/current/CONTEXT_WINDOW_EXPLOSION_FIX_2025-10-19.md` - Bug #1 fix
- `docs/current/ASSISTANT_RESPONSE_SAVING_FIX_2025-10-19.md` - Bug #6-7 fix
- `docs/current/PATH_NORMALIZATION_FIX_2025-10-19.md` - Bug #8 fix

---

## 🎓 Remember

**The Investigative Mindset:**
> Don't just fix symptoms - understand root causes.  
> Don't just make errors disappear - verify correct behavior appears.  
> Don't just move fast - move systematically and thoroughly.

**The Golden Rule:**
> If you discover an error during investigation, FIX IT IMMEDIATELY.  
> "Later" never comes, and small issues compound into big problems.

---

**Good luck! 🚀**

