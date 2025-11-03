# Architecture-Implementation Alignment Roadmap
**Date:** 2025-11-03  
**Status:** 🎯 STRATEGIC PLAN  
**EXAI Consultation:** GLM-4.6 (Continuation ID: 2dd7180e-a64a-45da-9bda-8afb1f78319a)

---

## 🎯 EXECUTIVE SUMMARY

**Problem:** Architecture and implementation are misaligned. Documentation describes ideal behavior, implementation has validation logic that doesn't run, schema shows everything as optional, and runtime accepts anything.

**Solution:** Reality-first alignment - make runtime behavior the source of truth, align everything else to it, then empirically test which tools add value and remove those that don't.

**Goal:** Simplify the system without adding complexity, using EXAI to systematically dissect and resolve issues.

---

## 🚨 CORE INSIGHT FROM EXAI

> "Instead of trying to enforce the original design, align documentation to what actually works. This is faster, more honest, and avoids adding complexity."

**Why This Matters:**
- Enforcement requires complex validation logic (adds complexity)
- Documentation updates are simple and immediate (reduces complexity)
- Users need to know what actually works, not what was intended
- Reality-first approach is pragmatic and achievable

---

## 📊 FOUR-PHASE ROADMAP

### Phase 1: Establish Single Source of Truth (Week 1)

**Objective:** Make runtime behavior the authoritative source of truth

**Actions:**
1. ✅ Document current runtime behavior for each tool
   - What parameters are actually required?
   - What happens when investigation is skipped?
   - What validation actually runs?

2. ✅ Update schema to reflect actual runtime
   - Mark truly required fields as required
   - Mark optional fields as optional
   - Remove misleading descriptions

3. ✅ Update documentation to match reality
   - Change "YOU MUST investigate" to "Recommended: investigate first"
   - Document actual behavior, not ideal behavior
   - Add examples of what actually works

4. ✅ Clean up dead code
   - Remove or comment out `get_first_step_required_fields()` if not used
   - Remove validation methods that never run
   - Reduce confusion from unused code

**Deliverables:**
- Runtime behavior documentation for all 8 workflow tools
- Updated schema files
- Updated AGENT_CAPABILITIES.md and SYSTEM_CAPABILITIES_OVERVIEW.md
- List of removed/commented validation methods

**Success Criteria:**
- Schema matches runtime behavior
- Documentation matches runtime behavior
- No contradictions between sources of truth

---

### Phase 2: Empirical Value Testing (Week 2)

**Objective:** Determine which tools actually add value vs just using chat

**Testing Methodology:**

For each workflow tool, run parallel comparison:

**Path A: Direct Analysis (Baseline)**
```
1. Claude investigates using view/codebase-retrieval
2. Claude analyzes and provides findings
3. Claude suggests solution
```

**Path B: Workflow Tool (Test)**
```
1. Claude investigates using view/codebase-retrieval
2. Claude calls workflow tool with findings
3. Expert model validates/enhances
4. Compare expert output vs Claude's original analysis
```

**Evaluation Criteria:**
1. **Mistake Detection:** Did expert catch errors Claude made?
2. **New Insights:** Did expert provide insights Claude missed?
3. **Workflow Value:** Did structured workflow improve quality?
4. **Efficiency:** Time/effort comparison

**Decision Matrix:**
- ✅ **KEEP** if expert adds measurable value (catches mistakes, provides insights)
- ❌ **REMOVE** if chat tool works just as well (no added value)
- 🔧 **FIX** if valuable but broken (worth investing in fixes)

**Tools to Test:**
1. `debug` - Does expert catch bugs Claude misses?
2. `analyze` - Does expert provide architectural insights Claude doesn't?
3. `codereview` - Does expert find code issues Claude overlooks?
4. `secaudit` - Does expert find vulnerabilities Claude misses?
5. `refactor` - Does expert suggest improvements Claude wouldn't?
6. `thinkdeep` - Does expert provide deeper reasoning than Claude?

**Tools Already Decided:**
- ✅ `chat` - Keep (baseline functionality)
- ✅ `consensus` - Keep (multi-model perspectives have inherent value)
- ✅ `testgen` - Keep (creative generation where experts add value)
- ❌ `planner` - Remove (no AI expert, just formatting)
- ❌ `tracer` - Remove (no AI expert, just structure)

**Deliverables:**
- Comparison matrix for each tested tool
- Keep/Remove/Fix decision for each tool
- Evidence documentation (examples where expert added value or didn't)

**Success Criteria:**
- Data-driven decisions based on empirical evidence
- Clear understanding of which tools provide value
- Documented examples of expert value-add (or lack thereof)

---

### Phase 3: Simplification Based on Evidence (Week 3)

**Objective:** Remove tools that don't add value, simplify architecture

**Three-Tier Decision Framework:**

#### Tier 1: Definitely Keep
- `chat` - Baseline functionality, direct AI access
- `consensus` - Multi-model perspectives have inherent value
- `testgen` - Creative generation where experts add value
- Plus any tools from Tier 2 that passed empirical testing

#### Tier 2: Evaluate Based on Testing
- `debug`, `analyze`, `codereview`, `secaudit`, `refactor`, `thinkdeep`
- Keep only if expert validation catches issues Claude misses
- Remove if chat tool works just as well

#### Tier 3: Likely Remove
- `planner` - No AI expert, just formatting (use task manager instead)
- `thinkdeep` - Redundant with Claude's capabilities
- `tracer` - No AI expert, just structure (use view/codebase-retrieval)

**Actions:**
1. ✅ For tools to REMOVE:
   - Mark as deprecated in schema
   - Document migration path to chat tool
   - Update any dependent systems
   - Remove from tool registry
   - Archive code (don't delete, just disable)

2. ✅ For tools to KEEP:
   - Proceed to Phase 4 (alignment)
   - Document value proposition clearly
   - Add usage examples showing when to use vs chat

3. ✅ For tools to FIX:
   - Document specific issues to fix
   - Prioritize fixes based on value
   - Implement fixes in Phase 4

**Deliverables:**
- Final keep/remove list
- Deprecated tool documentation
- Migration guide for removed tools
- Updated tool registry

**Success Criteria:**
- Reduced number of tools (simpler architecture)
- Clear value proposition for remaining tools
- Migration path for users of removed tools

---

### Phase 4: Implementation Alignment (Week 4)

**Objective:** Align implementation for tools we're keeping

**For Tools We Keep:**

1. ✅ **Choose enforcement strategy:**
   - Option A: Enforce "YOU Investigate First" (add validation)
   - Option B: Update docs to say "Recommended" (no enforcement)
   - **Recommendation:** Option B (simpler, no added complexity)

2. ✅ **Align schema with requirements:**
   - Make schema reflect actual runtime requirements
   - Add clear descriptions of when to use each tool
   - Document differences from chat tool

3. ✅ **Clean up validation code:**
   - Remove unused validation methods
   - Keep only validation that actually runs
   - Document what validation exists

4. ✅ **Fix Supabase storage:**
   - Store actual conversation messages
   - Not internal tool execution data
   - Enable conversation reconstruction

**For Tools We Remove:**

1. ✅ **Deprecate cleanly:**
   - Mark as deprecated in schema
   - Add deprecation warnings
   - Set removal date

2. ✅ **Document migration:**
   - How to use chat tool instead
   - Examples of equivalent usage
   - Benefits of simpler approach

3. ✅ **Update dependencies:**
   - Update any systems that reference removed tools
   - Update documentation
   - Update examples

**Deliverables:**
- Aligned schema, docs, and implementation for kept tools
- Fixed Supabase conversation storage
- Deprecated tool warnings
- Migration documentation

**Success Criteria:**
- No contradictions between schema, docs, implementation, runtime
- Supabase stores actual conversations
- Clear migration path for deprecated tools
- Simpler, more maintainable architecture

---

## 🎯 KEY PRINCIPLES

### 1. Reality-First Alignment
**Don't enforce what doesn't work. Document what does.**
- Align documentation to runtime behavior
- Update schema to reflect actual requirements
- Remove validation that doesn't run

### 2. Evidence-Based Decisions
**Test before investing in fixes.**
- Compare Claude's analysis vs expert analysis
- Measure actual value-add
- Remove tools that don't add measurable value

### 3. Simplification Over Enforcement
**Remove complexity, don't add it.**
- Remove tools that don't add clear value
- Don't add complex validation logic
- Focus on user value, not architectural purity

### 4. Incremental Changes
**Small, reversible changes.**
- Test each change independently
- Document before/after
- Easy to rollback if needed

---

## 🚀 IMMEDIATE NEXT STEPS

### Step 1: Start Phase 1 (This Week)
1. Document runtime behavior for all 8 workflow tools
2. Create comparison matrix template for Phase 2
3. Update schema to reflect actual runtime requirements

### Step 2: Test One Tool Completely
1. Pick `debug` (most data available)
2. Run A/B comparison (Claude vs expert)
3. Document findings
4. Make keep/remove/fix decision

### Step 3: Apply Learnings
1. Use debug test as template
2. Test remaining tools
3. Make final keep/remove decisions

---

## ✅ CRITICAL SUCCESS FACTORS

- ✅ **Don't add new validation logic** - Fix or remove existing broken logic
- ✅ **Focus on user value** - Does this help users solve problems better?
- ✅ **Measure objectively** - Time, quality, completeness metrics
- ✅ **Be willing to remove** - Not every tool needs to exist
- ✅ **Use EXAI to critique EXAI** - System evaluates itself

---

## 📋 DECISION LOG

### Decisions Made (2025-11-03)

1. ✅ **Adopt reality-first alignment approach**
   - Rationale: Simpler than enforcement, more honest
   - Impact: Documentation updates instead of validation logic

2. ✅ **Make runtime behavior source of truth**
   - Rationale: It's what users actually experience
   - Impact: Schema and docs align to runtime

3. ✅ **Empirical testing before fixes**
   - Rationale: Don't fix tools that should be removed
   - Impact: Test value first, then decide keep/remove/fix

4. ✅ **Simplification over enforcement**
   - Rationale: Reduce complexity, not add it
   - Impact: Remove tools that don't add value

### Decisions Pending

1. ⏳ **Which tools to keep/remove** (Phase 2 testing required)
2. ⏳ **Enforcement vs recommendation** (Phase 4 decision)
3. ⏳ **Supabase storage fix approach** (Phase 4 implementation)

---

## 🔄 CONTINUATION TRACKING

**EXAI Consultation ID:** 2dd7180e-a64a-45da-9bda-8afb1f78319a  
**Remaining Turns:** 19  
**Model:** GLM-4.6  
**Date:** 2025-11-03

Use this continuation ID to continue the strategic discussion with EXAI about any phase of this roadmap.

---

**Status:** ✅ PHASE 1 COMPLETE - Ready for Phase 2

---

## 📋 PHASE 1 EXECUTION SUMMARY (2025-11-03)

### What Was Accomplished

**EXAI Consultation Strategy:**
- Consulted EXAI (GLM-4.6) for concrete implementation approach
- EXAI recommended hybrid approach: code analysis + systematic testing
- Created lightweight behavior capture script (30 lines as recommended)

**Behavior Capture Script Created:**
- File: `scripts/phase1_behavior_capture.py`
- Analyzes all 12 workflow tools systematically
- Captures: inheritance, schema, validation, categorization
- Generates both markdown and JSON output

**Execution Results:**
- ✅ All 12 tools analyzed successfully (0 errors)
- ✅ Markdown report generated: `PHASE1_BEHAVIOR_ANALYSIS__2025-11-03.md`
- ✅ JSON data saved: `PHASE1_BEHAVIOR_ANALYSIS__2025-11-03.json`

### Key Findings

**Tool Categorization:**
1. **Investigation + Expert Validation (9 tools):**
   - debug, analyze, codereview, testgen, secaudit, refactor, thinkdeep, precommit, docgen
   - All have `should_call_expert_analysis()` method
   - All have `get_first_step_required_fields()` method

2. **Structure Only (2 tools):**
   - planner, tracer
   - No expert validation
   - Just structure work

3. **Multi-Model (1 tool):**
   - consensus
   - Consults multiple models

**Validation Pattern Discovered:**
- Schema shows: `relevant_files` is NOT in required array
- Implementation has: `get_first_step_required_fields()` returns `['relevant_files']`
- **Contradiction confirmed:** Schema doesn't reflect step-specific requirements

**Next Steps:**
- Proceed to Phase 2: Empirical value testing
- Test whether expert models add value vs Claude's analysis
- Make data-driven keep/remove decisions

---

