# ARCHAEOLOGICAL DIG - CONTEXT AND SCOPE
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Timezone:** AEDT (Melbourne, Australia)  
**Status:** Investigation Phase

---

## WHY THIS INVESTIGATION IS NEEDED

### The Original Problem
I was asked to perform root cause analysis on 5 issues:
1. Static system prompts causing weak responses
2. Model training date awareness
3. Model routing rules not working
4. File size limits & missing GLM embeddings
5. Log visibility & Supabase integration

### What I Discovered
After creating detailed implementation plans, the user revealed:
- **Systemprompts folder already exists** with 15+ specialized prompts
- **Timezone.py already exists** in src/utils/
- **Provider registry system already exists** with multiple scripts
- **Utils folder has 30+ scripts** with no organization
- **Two separate utils folders** (src/utils/ and utils/)
- **Existing logging infrastructure** that may be disconnected

### The Real Problem
**I was recommending creating NEW scripts when existing systems already exist but may be:**
- Disconnected from the main system
- Not working as intended
- Orphaned/dead code
- Poorly organized

---

## INVESTIGATION SCOPE

### Phase 0: Archaeological Dig (Current Phase)

We need to understand what EXISTS before implementing anything new.

**Investigation Categories:**

1. **Prompts** - How system prompts currently work
2. **Timezone** - How timestamps are handled
3. **Routing** - How model selection works
4. **Utilities** - What scripts exist and their status
5. **Message Bus** - Supabase integration design intent
6. **Layout Map** - Overall system architecture

---

## USER'S CRITICAL INSIGHTS

### Issue 1: System Prompts
**User's Response:**
> "I believe our current system has hardcoded script that uses generic scripts prompts and has bypassed the system prompts."

**Investigation Needed:**
- Are systemprompts/ files being used?
- Where is the hardcoded bypass?
- How should systemprompts/ connect to tools?

### Issue 2: Timezone Detection
**User's Response:**
> "I think lets implement the easiest strat, can you research how typically how other applications do this and implement that."

**Investigation Needed:**
- Research industry standard timezone detection
- How do web apps detect user timezone?
- How do desktop apps detect user timezone?
- Best practice for timezone handling

### Issue 3: Model Routing
**User's Response:**
> "You have access to already it is saved under folder name logs, i cant tag it, because of ignore file"

**Investigation Needed:**
- Review logs/provider_registry_snapshot.json
- Understand existing routing logic
- Identify why kimi-latest-128k routing fails

### Issue 4: Utils Folder Chaos
**User's Response:**
> "I think this needs to be another folder called something utilities where you identify whether you believe the scripts are good, bad or something else"

**Investigation Needed:**
- Audit all 30+ scripts in utils/
- Identify active vs. orphaned code
- Check for duplicate functionality
- Recommend reorganization

### Issue 5: Message Bus & Logging
**User's Response:**
> "We clearly had a design in place for logging, because we have .logs and logs, and under logs it looks way more designed better, but it appears disconnected fundamentally"

**Investigation Needed:**
- Understand .logs/ vs logs/ design intent
- Review logging infrastructure
- Identify disconnection points
- Understand message_bus_client.py design intent

---

## IMMEDIATE ACTION ITEMS

### 1. Fix Type Error (URGENT)
**File:** `src/core/message_bus_client.py` line 139  
**Error:** Variable not allowed in type expression  
**Status:** Will fix immediately

### 2. Create Investigation Folders
```
docs/ARCHAEOLOGICAL_DIG/
├── 00_CONTEXT_AND_SCOPE.md (this file)
├── prompts/
│   └── investigation_findings.md
├── timezone/
│   └── investigation_findings.md
├── routing/
│   └── investigation_findings.md
├── utilities/
│   └── investigation_findings.md
├── message_bus/
│   └── investigation_findings.md
└── layoutmap/
    └── system_architecture.md
```

### 3. Systematic Investigation
For each category:
1. Document what exists
2. Document what's connected vs. orphaned
3. Document design intent (if discoverable)
4. Recommend actions (fix, connect, remove, reorganize)

---

## INVESTIGATION METHODOLOGY

### For Each Category

**Step 1: Discovery**
- List all related files
- Read code to understand purpose
- Check imports to see what's connected

**Step 2: Connection Analysis**
- Trace how files are imported
- Identify entry points
- Map data flow

**Step 3: Status Assessment**
- Active (currently used)
- Orphaned (exists but not connected)
- Duplicate (functionality exists elsewhere)
- Dead (obsolete code)

**Step 4: Design Intent**
- What was the original purpose?
- Is it still relevant?
- How should it work?

**Step 5: Recommendations**
- Fix (broken but needed)
- Connect (exists but not integrated)
- Remove (dead code)
- Reorganize (good code, wrong location)
- Document (working but undocumented)

---

## SUCCESS CRITERIA

### Investigation Complete When:
- [ ] All existing systems mapped
- [ ] Active vs. orphaned code identified
- [ ] Design intent understood
- [ ] Recommendations documented
- [ ] User approves next steps

### Implementation Can Begin When:
- [ ] We know what to fix vs. what to build
- [ ] We know what to connect vs. what to create
- [ ] We know what to remove vs. what to keep
- [ ] We have clear, evidence-based plan

---

## GUIDING PRINCIPLES

### 1. Understand Before Changing
Don't recommend new code until we understand existing code.

### 2. Connect Before Creating
If functionality exists, connect it. Don't duplicate.

### 3. Evidence-Based Decisions
Every recommendation must be backed by code analysis.

### 4. User's Instincts Are Correct
The user knows this codebase. Trust their insights.

### 5. Document Everything
Future developers (including us) need to understand the archaeology.

---

## NEXT STEPS

1. ✅ Create this context document
2. ⏳ Fix message_bus_client.py type error
3. ⏳ Create investigation folders
4. ⏳ Begin systematic investigation
5. ⏳ Document findings
6. ⏳ Present recommendations

---

**STATUS: INVESTIGATION PHASE INITIATED**

Let the archaeological dig begin! 🏛️

