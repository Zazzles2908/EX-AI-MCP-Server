# MODEL ROUTING INVESTIGATION - FINDINGS
**Date:** 2025-10-10 (10th October 2025, Thursday)  
**Category:** Model Selection & Routing Logic  
**Status:** 🔍 Investigation In Progress

---

## INVESTIGATION QUESTION

**User's Concern:**
> "kimi-latest-128k does exist, but it is not preferred kimi model I want selected... the application needs to understand what model to select or the system needs to be self aware what is the best option."

**What We Need to Discover:**
1. How does the existing provider registry work?
2. Why did kimi-latest-128k get selected instead of preferred model?
3. What is DEFAULT_MODEL in .env supposed to do?
4. How should routing rules work?

---

## WHAT EXISTS

### Provider Registry System

**Multiple Registry Files Found:**
```
src/providers/
├── registry.py              # Main registry
├── registry_config.py       # Configuration
├── registry_core.py         # Core functionality
├── registry_selection.py    # Model selection logic
└── provider_registration.py # Generates provider_registry_snapshot.json
```

**Plus:**
```
src/server/providers/
└── provider_registration.py # Another registration script?
```

**Question:** Are there TWO provider registration systems?

### Provider Registry Snapshot

**User mentioned:**
> "This generates this json file provider_registry_snapshot.json, which I think should give this visibility to the system of how each model should be seen as well."

**Location:** `logs/provider_registry_snapshot.json` (in .gitignore)

**Need to review this file to understand:**
- What models are registered?
- What are their capabilities?
- What are the routing rules?
- Is kimi-latest-128k listed?

---

## INVESTIGATION TASKS

### Task 1: Review Provider Registry Snapshot
- [ ] Read logs/provider_registry_snapshot.json
- [ ] Document all registered models
- [ ] Document model capabilities
- [ ] Document routing rules
- [ ] Check if kimi-latest-128k is listed

### Task 2: Understand Registry Architecture
- [ ] Read src/providers/registry.py
- [ ] Read src/providers/registry_config.py
- [ ] Read src/providers/registry_core.py
- [ ] Read src/providers/registry_selection.py
- [ ] Read src/providers/provider_registration.py
- [ ] Map how they connect

### Task 3: Check DEFAULT_MODEL Usage
- [ ] Read .env for DEFAULT_MODEL value
- [ ] Search codebase for DEFAULT_MODEL usage
- [ ] Understand how it affects routing
- [ ] Check if it's being respected

### Task 4: Trace Model Selection Flow
- [ ] How does request_handler select model?
- [ ] Does it consult registry?
- [ ] Does it use DEFAULT_MODEL?
- [ ] Where does routing logic live?

---

## PRELIMINARY FINDINGS

### Finding 1: Complex Registry System Exists
- ✅ Multiple registry files exist
- ✅ Generates provider_registry_snapshot.json
- ❓ Unknown if it's being used
- ❓ Unknown if routing rules are enforced

### Finding 2: Potential Duplicate Systems
**Concern:** Two provider_registration.py files:
- `src/providers/provider_registration.py`
- `src/server/providers/provider_registration.py`

**Question:** Which one is active? Are they duplicates?

### Finding 3: User's Insight is Critical
**User knows:**
> "kimi-latest-128k does exist, but it is not preferred"

**This means:**
- Model exists in Kimi API
- But system should prefer different model (kimi-k2-0905-preview?)
- Routing rules should prevent selection
- But they're not working

---

## NEXT STEPS

1. **Immediate:** Read provider_registry_snapshot.json
2. **Then:** Understand registry architecture
3. **Then:** Trace model selection flow
4. **Then:** Identify why routing failed
5. **Finally:** Recommend fix

---

**STATUS: AWAITING REGISTRY SNAPSHOT REVIEW**

Next: Read logs/provider_registry_snapshot.json to understand registered models.

