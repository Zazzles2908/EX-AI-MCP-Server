# 🚀 EX-AI MCP Server - Start Here

**Last Updated:** 2025-10-21  
**Project Status:** ✅ Week 1 CRITICAL Fixes Complete - Foundation Validated  
**Next Phase:** Week 2 HIGH Priority Fixes

---

## 📋 Quick Navigation

### For New AI Agents
1. **Read this file first** - Understand current status and what's been done
2. **[Architecture Overview](01_Core_Architecture/01_System_Overview.md)** - Understand the system
3. **[Fix Roadmap](fix_implementation/WEEKLY_FIX_ROADMAP_2025-10-20.md)** - See what needs to be done
4. **[Week 1 Completion](fix_implementation/WEEK_1_COMPLETION_SUMMARY_2025-10-21.md)** - What's already fixed

### For Continuing Work
- **[Week 2 Fixes](fix_implementation/WEEKLY_FIX_ROADMAP_2025-10-20.md#week-2-high-priority-fixes)** - Next tasks
- **[EXAI Tool Guide](02_Service_Components/EXAI_TOOL_DECISION_GUIDE.md)** - How to use EXAI tools
- **[Testing Guide](02_Service_Components/04_Testing.md)** - How to validate changes

---

## 🎯 Project Overview

**EX-AI MCP Server** is a WebSocket-based MCP (Model Context Protocol) server providing AI capabilities through multiple providers:
- **Kimi/Moonshot** - Primary AI provider (OpenAI SDK)
- **GLM/ZhipuAI** - Secondary AI provider (Independent SDK)
- **Supabase** - Audit trail and persistence (async, non-blocking)

### Key Architecture Points
- **WebSocket daemon** on port 8079 (internal communication hub)
- **Docker-based** deployment (WSL/Linux container)
- **Multi-provider** orchestration with fallback
- **Supabase integration** for audit trail (NOT primary gateway)
- **Redis** for caching and session management

---

## ✅ Current Status (2025-10-21)

### Week 1 CRITICAL Fixes - COMPLETE ✅

All 5 critical fixes have been implemented, validated, and tested:

1. **✅ Fix #1: Semaphore Leak on Timeout** - Early return bypassed cleanup
2. **✅ Fix #2: _inflight_reqs Memory Leak** - Request IDs never removed
3. **✅ Fix #3: GIL False Safety Claim** - Misleading documentation
4. **✅ Fix #4: Check-Then-Act Race Conditions** - Vulnerable patterns fixed
5. **✅ Fix #5: No Thread Safety for Providers** - Added proper locking

**BONUS Fix:** Double-Semaphore Release Bug (discovered during stress testing)

### Foundation Validated ✅

- **WebSocket version:** 14.2 (required by Supabase realtime dependency)
- **Stress test results:** 40/40 requests successful (100%)
- **Docker logs:** Zero semaphore errors
- **All containers:** Healthy and running

See: [Foundation Validation](fix_implementation/FOUNDATION_WEBSOCKETS_DEPENDENCY_2025-10-21.md)

---

## 📁 Documentation Structure

### Core Documentation
```
Documentations/
├── 00_START_HERE.md                    ← YOU ARE HERE
├── 01_Core_Architecture/               ← System design and architecture
│   ├── 01_System_Overview.md
│   ├── 02_SDK_Integration.md
│   └── 03_Supabase_Audit_Trail.md
├── 02_Service_Components/              ← Individual components
│   ├── 01_Daemon_WebSocket.md
│   ├── 02_Docker.md
│   ├── 03_MCP_Server.md
│   ├── 04_Testing.md
│   ├── 05_UI_Components.md
│   ├── 06_System_Prompts.md
│   └── EXAI_TOOL_DECISION_GUIDE.md    ← IMPORTANT: How to use EXAI tools
├── 03_Data_Management/                 ← Data layer
│   ├── 01_User_Auth.md
│   ├── 02_Tools_Functions.md
│   └── 03_File_Storage.md
└── fix_implementation/                 ← Bug fixes and improvements
    ├── README.md                       ← Fix implementation overview
    ├── WEEKLY_FIX_ROADMAP_2025-10-20.md ← Master roadmap (49 fixes)
    ├── WEEK_1_COMPLETION_SUMMARY_2025-10-21.md
    ├── CRITICAL_BUG_FIX_DOUBLE_SEMAPHORE_2025-10-21.md
    ├── FOUNDATION_WEBSOCKETS_DEPENDENCY_2025-10-21.md
    └── [Other fix documentation...]
```

---

## 🔧 Development Workflow

### Two-Tier Consultation Approach (MANDATORY)

**Tier 1:** Use EXAI workflow tools for investigation
- `debug_EXAI-WS` - Root cause analysis
- `codereview_EXAI-WS` - Code review
- `analyze_EXAI-WS` - Architecture analysis
- `secaudit_EXAI-WS` - Security audit
- `refactor_EXAI-WS` - Refactoring opportunities

**Tier 2:** MANDATORY consultation with EXAI before implementation
- Use `chat_EXAI-WS` with GLM-4.6 model
- Enable web search for documentation lookup
- Validate proposed solution before making changes
- Only proceed after EXAI confirms approach is correct

See: [EXAI Tool Decision Guide](02_Service_Components/EXAI_TOOL_DECISION_GUIDE.md)

### Testing Requirements

1. **Before making changes:** Use EXAI tools to investigate
2. **After making changes:** Run stress tests to validate
3. **Before committing:** Use `precommit_EXAI-WS` for validation
4. **After validation:** Check Docker logs for errors

---

## 🎯 Next Steps - Week 2 HIGH Priority Fixes

### Ready to Implement (8 fixes)

1. **Fix #6:** Hardcoded Timeouts (centralize in .env)
2. **Fix #7:** No Timeout Validation (validate env vars)
3. **Fix #8:** Inconsistent Error Handling (standardize patterns)
4. **Fix #9:** Missing Input Validation (add validation layer)
5. **Fix #10:** No Request Size Limits (prevent DoS)
6. **Fix #11:** Weak Session ID Generation (use secrets module)
7. **Fix #12:** No Session Expiry (implement TTL)
8. **Fix #13:** Missing CORS Configuration (add proper headers)

See: [Week 2 Roadmap](fix_implementation/WEEKLY_FIX_ROADMAP_2025-10-20.md#week-2-high-priority-fixes)

---

## 🚨 Critical Constraints

### Dependency Constraints
- **websockets==14.2** - REQUIRED by Supabase realtime (cannot upgrade to 15.x)
- **Supabase realtime** - Core dependency for audit trail
- See: [Foundation Validation](fix_implementation/FOUNDATION_WEBSOCKETS_DEPENDENCY_2025-10-21.md)

### Environment
- **EXAI runs in:** WSL (Linux) Docker container
- **User operates in:** Windows
- **VSCode connects via:** MCP using run_ws_shim.py at localhost:8079
- **Single-user development:** Configure for 5 users max (not production scale)

### Configuration
- **All timeouts:** Must be in .env (never hardcoded)
- **All parameters:** Must be in .env with validation
- **Package management:** Always use package managers (never edit package files directly)

---

## 📊 Key Metrics

### Stress Test Results (Latest)
- **Duration:** 0.12s
- **Total Requests:** 40
- **Success Rate:** 100%
- **Requests/sec:** 320.33
- **Response Time (mean):** 0.004s

### System Health
- **Semaphore errors:** 0
- **Memory leaks:** 0 (fixed)
- **Race conditions:** 0 (fixed)
- **Thread safety:** ✅ Implemented

---

## 🔗 Important Links

- **Main Roadmap:** [WEEKLY_FIX_ROADMAP_2025-10-20.md](fix_implementation/WEEKLY_FIX_ROADMAP_2025-10-20.md)
- **Week 1 Summary:** [WEEK_1_COMPLETION_SUMMARY_2025-10-21.md](fix_implementation/WEEK_1_COMPLETION_SUMMARY_2025-10-21.md)
- **EXAI Tool Guide:** [EXAI_TOOL_DECISION_GUIDE.md](02_Service_Components/EXAI_TOOL_DECISION_GUIDE.md)
- **Architecture:** [01_System_Overview.md](01_Core_Architecture/01_System_Overview.md)
- **Testing:** [04_Testing.md](02_Service_Components/04_Testing.md)

---

## 💡 Tips for AI Agents

1. **Always read this file first** - It's the single source of truth for current status
2. **Use EXAI tools** - They provide expert validation and catch issues early
3. **Follow the two-tier approach** - Investigate first, validate before implementing
4. **Test thoroughly** - Run stress tests after every change
5. **Document everything** - Update relevant docs when making changes
6. **Check constraints** - Review dependency constraints before upgrading packages

---

## 📝 Recent Updates

- **2025-10-21:** Week 1 CRITICAL fixes complete, foundation validated
- **2025-10-21:** Discovered and documented Supabase websockets constraint
- **2025-10-21:** Fixed double-semaphore release bug (stress test discovery)
- **2025-10-20:** Implemented all 5 Week 1 fixes with EXAI validation
- **2025-10-20:** Created comprehensive fix roadmap (49 fixes across 4 weeks)

---

**Ready to continue? Start with Week 2 HIGH priority fixes!** 🚀

