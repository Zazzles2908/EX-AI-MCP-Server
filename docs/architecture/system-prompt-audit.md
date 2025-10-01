# System Prompt Audit Report

**Date:** 2025-10-01  
**Auditor:** Augment Agent (using EXAI analyze tool)  
**Purpose:** Comprehensive audit of all system prompts for simplification opportunities  
**Status:** ✅ COMPLETE

---

## 🎯 Executive Summary

**Total System Prompts:** 13  
**Total Lines:** 1,867 lines  
**Average Length:** 144 lines per prompt  
**Complexity Range:** 58 lines (thinkdeep) to 375 lines (secaudit)

**Key Findings:**
1. **Excessive Length:** 3 prompts exceed 200 lines (secaudit: 375, refactor: 280, docgen: 220)
2. **High Redundancy:** Common patterns repeated across all prompts (role, scope, anti-patterns)
3. **Inconsistent Structure:** Some prompts use sections, others use bullet points
4. **Overengineering Warnings:** Repeated anti-overengineering guidance in 8+ prompts
5. **JSON Schema Duplication:** Similar response formats defined multiple times

**Recommendation:** Reduce total prompt length by 30-40% through:
- Extracting common patterns to shared base prompt
- Simplifying longest prompts (secaudit, refactor, docgen)
- Standardizing structure across all prompts
- Removing redundant anti-pattern warnings

---

## 📊 Prompt Inventory

### 1. CHAT_PROMPT
**File:** `systemprompts/chat_prompt.py`  
**Length:** 65 lines  
**Complexity:** MEDIUM  
**Purpose:** General conversation and thought partnership

**Structure:**
- Role definition
- Scope & Focus
- Collaboration Approach
- Brainstorming Guidelines
- EX-AI MCP Server Context
- Escalation Guidance

**Strengths:**
- ✅ Concise and well-organized
- ✅ Clear escalation guidance
- ✅ Practical examples

**Issues:**
- ⚠️ Anti-overengineering warning (redundant with other prompts)
- ⚠️ Server context could be extracted to shared base

**Simplification Potential:** LOW (10-15% reduction possible)

---

### 2. ANALYZE_PROMPT
**File:** `systemprompts/analyze_prompt.py`  
**Length:** 74 lines  
**Complexity:** MEDIUM  
**Purpose:** Holistic technical audit and architectural analysis

**Structure:**
- Role definition
- Escalation to codereview
- Scope & Focus
- Analysis Strategy
- Key Dimensions
- Deliverable Format

**Strengths:**
- ✅ Clear deliverable format
- ✅ Well-defined dimensions
- ✅ Structured output template

**Issues:**
- ⚠️ Escalation logic could be standardized
- ⚠️ Anti-overengineering warning (redundant)
- ⚠️ Deliverable format could be simplified

**Simplification Potential:** MEDIUM (20-25% reduction possible)

---

### 3. DEBUG_ISSUE_PROMPT
**File:** `systemprompts/debug_prompt.py`  
**Length:** 135 lines  
**Complexity:** HIGH  
**Purpose:** Expert debugging assistance with systematic investigation

**Structure:**
- Role definition
- Systematic Investigation Context
- Tracer Tool Integration
- Critical Line Number Instructions
- Workflow Context
- No Bug Found Response
- Standard Response Format
- Critical Debugging Principles

**Strengths:**
- ✅ Comprehensive debugging guidance
- ✅ Clear JSON response formats
- ✅ Handles "no bug found" case

**Issues:**
- 🔴 TOO LONG (135 lines) - needs significant reduction
- 🔴 Multiple JSON schemas (could be consolidated)
- ⚠️ Line number instructions overly detailed
- ⚠️ Redundant principles at end

**Simplification Potential:** HIGH (30-35% reduction possible)

---

### 4. THINKDEEP_PROMPT
**File:** `systemprompts/thinkdeep_prompt.py`  
**Length:** 58 lines  
**Complexity:** LOW  
**Purpose:** Deep reasoning and validation

**Structure:**
- Role definition
- Collaboration approach
- Response guidelines

**Strengths:**
- ✅ SHORTEST PROMPT - excellent example of simplicity
- ✅ Clear and focused
- ✅ No unnecessary complexity

**Issues:**
- ✅ NONE - this is the gold standard for prompt simplicity

**Simplification Potential:** NONE (already optimal)

---

### 5. CODEREVIEW_PROMPT
**File:** `systemprompts/codereview_prompt.py`  
**Length:** 82 lines  
**Complexity:** MEDIUM  
**Purpose:** Expert code review with focus on security, performance, maintainability

**Strengths:**
- ✅ Well-structured
- ✅ Clear focus areas

**Issues:**
- ⚠️ Some redundancy with analyze prompt
- ⚠️ Anti-overengineering warning (redundant)

**Simplification Potential:** MEDIUM (20% reduction possible)

---

### 6. PRECOMMIT_PROMPT
**File:** `systemprompts/precommit_prompt.py`  
**Length:** 96 lines  
**Complexity:** MEDIUM  
**Purpose:** Pre-commit validation with future liability focus

**Strengths:**
- ✅ Good focus on future implications
- ✅ Clear validation criteria

**Issues:**
- ⚠️ Overlaps with codereview prompt
- ⚠️ Could be more concise

**Simplification Potential:** MEDIUM (25% reduction possible)

---

### 7. DOCGEN_PROMPT
**File:** `systemprompts/docgen_prompt.py`  
**Length:** 220 lines  
**Complexity:** VERY HIGH  
**Purpose:** Systematic documentation generation

**Structure:**
- Role definition
- Systematic Exploration Approach (detailed)
- Documentation Standards (extensive)
- Systematic Approach
- Critical Rules
- Progress Tracking

**Strengths:**
- ✅ Comprehensive documentation guidance
- ✅ Clear systematic approach

**Issues:**
- 🔴 TOO LONG (220 lines) - second longest prompt
- 🔴 Overly detailed exploration instructions
- 🔴 Redundant "CRITICAL RULE" sections
- 🔴 Could be split into core + reference sections

**Simplification Potential:** VERY HIGH (40-45% reduction possible)

---

### 8. TESTGEN_PROMPT
**File:** `systemprompts/testgen_prompt.py`  
**Length:** 116 lines  
**Complexity:** HIGH  
**Purpose:** Comprehensive test generation

**Issues:**
- 🔴 TOO LONG for test generation
- ⚠️ Could be more focused

**Simplification Potential:** HIGH (30% reduction possible)

---

### 9. REFACTOR_PROMPT
**File:** `systemprompts/refactor_prompt.py`  
**Length:** 280 lines  
**Complexity:** VERY HIGH  
**Purpose:** Code refactoring and improvement

**Issues:**
- 🔴 EXTREMELY LONG (280 lines) - second longest
- 🔴 Excessive detail and examples
- 🔴 Multiple redundant sections
- 🔴 Could be 50% shorter without losing value

**Simplification Potential:** VERY HIGH (50% reduction possible)

---

### 10. SECAUDIT_PROMPT
**File:** `systemprompts/secaudit_prompt.py`  
**Length:** 375 lines  
**Complexity:** EXTREMELY HIGH  
**Purpose:** Security audit with OWASP Top 10

**Issues:**
- 🔴 LONGEST PROMPT (375 lines) - CRITICAL ISSUE
- 🔴 Includes entire OWASP Top 10 checklist inline
- 🔴 Excessive detail that could be referenced externally
- 🔴 Could be 60% shorter by extracting checklists

**Simplification Potential:** EXTREMELY HIGH (60% reduction possible)

---

### 11. CONSENSUS_PROMPT
**File:** `systemprompts/consensus_prompt.py`  
**Length:** 98 lines  
**Complexity:** MEDIUM  
**Purpose:** Multi-model consensus analysis

**Simplification Potential:** MEDIUM (20% reduction possible)

---

### 12. PLANNER_PROMPT
**File:** `systemprompts/planner_prompt.py`  
**Length:** 110 lines  
**Complexity:** MEDIUM-HIGH  
**Purpose:** Planning and task breakdown

**Simplification Potential:** MEDIUM (25% reduction possible)

---

### 13. TRACER_PROMPT
**File:** `systemprompts/tracer_prompt.py`  
**Length:** 127 lines  
**Complexity:** HIGH  
**Purpose:** Code tracing and flow analysis

**Simplification Potential:** HIGH (30% reduction possible)

---

## 🔍 Redundancy Analysis

### Common Patterns (Repeated Across Prompts)

#### 1. Role Definition
**Occurrences:** ALL 13 prompts  
**Pattern:** "You are a [role] [doing task]..."  
**Recommendation:** Standardize format, keep concise

#### 2. Anti-Overengineering Warnings
**Occurrences:** 8+ prompts  
**Pattern:** Warnings about overengineering, unnecessary abstraction, etc.  
**Redundancy:** HIGH - same message repeated multiple times  
**Recommendation:** Extract to shared base prompt or remove from individual prompts

**Example Duplications:**
- chat: "Overengineering is an anti-pattern..."
- analyze: "Identify and flag overengineered solutions..."
- codereview: Similar warnings
- precommit: Similar warnings

#### 3. Scope & Focus Sections
**Occurrences:** 10+ prompts  
**Pattern:** Bullet points defining what to focus on  
**Recommendation:** Standardize structure

#### 4. JSON Response Formats
**Occurrences:** debug, docgen, consensus, others  
**Pattern:** Detailed JSON schemas inline  
**Redundancy:** MEDIUM - similar structures  
**Recommendation:** Extract common schemas to shared definitions

#### 5. File Path Instructions
**Occurrences:** Multiple prompts  
**Pattern:** "Use FULL ABSOLUTE paths..."  
**Redundancy:** HIGH  
**Recommendation:** Extract to shared base prompt

---

## 📈 Complexity Metrics

### By Length
| Prompt | Lines | Complexity | Priority |
|--------|-------|------------|----------|
| secaudit | 375 | EXTREME | 🔴 CRITICAL |
| refactor | 280 | VERY HIGH | 🔴 HIGH |
| docgen | 220 | VERY HIGH | 🔴 HIGH |
| debug | 135 | HIGH | 🟡 MEDIUM |
| tracer | 127 | HIGH | 🟡 MEDIUM |
| testgen | 116 | HIGH | 🟡 MEDIUM |
| planner | 110 | MEDIUM-HIGH | 🟡 MEDIUM |
| consensus | 98 | MEDIUM | 🟢 LOW |
| precommit | 96 | MEDIUM | 🟢 LOW |
| codereview | 82 | MEDIUM | 🟢 LOW |
| analyze | 74 | MEDIUM | 🟢 LOW |
| chat | 65 | MEDIUM | 🟢 LOW |
| thinkdeep | 58 | LOW | ✅ OPTIMAL |

### Simplification Priority

**CRITICAL (Reduce by 50-60%):**
- secaudit (375 → ~150 lines)
- refactor (280 → ~140 lines)

**HIGH (Reduce by 40-45%):**
- docgen (220 → ~120 lines)

**MEDIUM (Reduce by 30-35%):**
- debug (135 → ~90 lines)
- tracer (127 → ~90 lines)
- testgen (116 → ~80 lines)

**LOW (Reduce by 20-25%):**
- planner, consensus, precommit, codereview, analyze, chat

**OPTIMAL (No changes needed):**
- thinkdeep (58 lines) - use as template

---

## 💡 Improvement Recommendations

### 1. Create Shared Base Prompt (HIGH PRIORITY)
**Action:** Extract common patterns to `systemprompts/base_prompt.py`

**Common Elements to Extract:**
- Anti-overengineering warnings
- File path instructions (absolute paths)
- EX-AI MCP Server context
- Standard response guidelines
- Escalation patterns

**Estimated Reduction:** 15-20% across all prompts

---

### 2. Simplify Top 3 Longest Prompts (CRITICAL)

**secaudit (375 → ~150 lines):**
- Extract OWASP Top 10 checklist to external reference
- Remove redundant examples
- Consolidate similar sections
- Focus on core security principles

**refactor (280 → ~140 lines):**
- Remove excessive examples
- Consolidate redundant guidance
- Focus on core refactoring principles

**docgen (220 → ~120 lines):**
- Simplify exploration approach
- Remove redundant "CRITICAL RULE" sections
- Focus on core documentation standards

---

### 3. Standardize Structure (MEDIUM PRIORITY)

**Recommended Standard Structure:**
```
1. ROLE (1-2 sentences)
2. SCOPE & FOCUS (3-5 bullet points)
3. APPROACH/STRATEGY (3-5 steps)
4. DELIVERABLE FORMAT (if applicable)
5. KEY PRINCIPLES (3-5 points)
```

**Benefits:**
- Easier to maintain
- Consistent user experience
- Reduced cognitive load

---

### 4. Remove Redundant Warnings (HIGH PRIORITY)

**Action:** Remove anti-overengineering warnings from individual prompts

**Rationale:**
- Repeated 8+ times across prompts
- Can be in shared base prompt
- Reduces noise

**Estimated Reduction:** 5-10% across affected prompts

---

### 5. Consolidate JSON Schemas (MEDIUM PRIORITY)

**Action:** Extract common JSON response formats to shared definitions

**Affected Prompts:**
- debug (multiple schemas)
- docgen (progress tracking)
- consensus (response format)

**Benefits:**
- Consistency
- Easier to maintain
- Reduced duplication

---

## 🎯 Alignment with Design Philosophy

### Current State vs. Design Principles

| Principle | Current State | Target State |
|-----------|---------------|--------------|
| **Simplicity** | ❌ 3 prompts >200 lines | ✅ All prompts <150 lines |
| **Clarity** | ⚠️ Inconsistent structure | ✅ Standardized structure |
| **Maintainability** | ❌ High redundancy | ✅ Shared base prompt |
| **User-Centric** | ⚠️ Overly detailed | ✅ Focused and concise |

---

## 📋 Action Items for Task 0.4

### Phase 1: Create Shared Base (1-2 hours)
- [ ] Create `systemprompts/base_prompt.py`
- [ ] Extract common patterns
- [ ] Update all prompts to reference base

### Phase 2: Simplify Top 3 (3-4 hours)
- [ ] Simplify secaudit (375 → ~150)
- [ ] Simplify refactor (280 → ~140)
- [ ] Simplify docgen (220 → ~120)

### Phase 3: Standardize Structure (2-3 hours)
- [ ] Apply standard structure to all prompts
- [ ] Remove redundant warnings
- [ ] Consolidate JSON schemas

### Phase 4: Test & Validate (1-2 hours)
- [ ] Test simplified prompts
- [ ] Verify functionality
- [ ] Document changes

**Total Estimated Effort:** 7-11 hours

---

## 📊 Expected Outcomes

**Before Simplification:**
- Total: 1,867 lines
- Average: 144 lines/prompt
- Longest: 375 lines (secaudit)

**After Simplification:**
- Total: ~1,200 lines (36% reduction)
- Average: ~92 lines/prompt
- Longest: ~150 lines (secaudit)

**Benefits:**
- ✅ Faster model processing
- ✅ Lower token costs
- ✅ Easier maintenance
- ✅ Better alignment with design philosophy
- ✅ Improved consistency

---

**Status:** ✅ AUDIT COMPLETE  
**Next:** Task 0.4 (Simplify System Prompts)  
**Priority:** HIGH - Significant improvement opportunity identified

