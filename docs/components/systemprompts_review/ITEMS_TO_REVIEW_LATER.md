# Items to Review Later

**Date Created:** 2025-10-21  
**Purpose:** Track design decisions and implementation details that need future review

---

## Phase 2.1.1.1: Model-Aware Token Limits

### ✅ RESOLVED: Test Output Organization
**Date:** 2025-10-21  
**Issue:** User questioned why `kimi-thinking-preview` validation test appeared in main output but not in "Helper Functions Test" section.

**Analysis:**
- ✅ Implementation is CORRECT - `kimi-thinking-preview` has 128K context (131,072 tokens)
- ✅ Validation logic is CORRECT - 120,000 requested → 114,688 validated (capped at model limit)
- ℹ️ Test output design: "Helper Functions Test" section only spot-checks 2 models (moonshot-v1-8k, glm-4.6)
- ℹ️ This is intentional - not meant to be comprehensive, just validates helper functions work

**Design Intent:**
```python
# Helper Functions Test section tests:
# 1. get_default_max_tokens() - returns correct default
# 2. get_max_output_tokens() - returns correct max output
# Only needs 2 models to verify functions work correctly
```

**Recommendation:**
- ✅ NO CHANGES NEEDED - Implementation follows design intent
- 📝 Consider: Add more models to helper test section for better visibility (optional enhancement)

**Status:** RESOLVED - Implementation is correct, test output is as designed

---

## Future Considerations

### 1. Comprehensive Helper Function Testing
**Priority:** Low  
**Description:** Expand helper function test section to show all 14 models instead of just 2 spot checks.

**Pros:**
- Better visibility of all model configurations
- Easier to verify limits at a glance

**Cons:**
- More verbose test output
- Not necessary for validation (spot check is sufficient)

**Decision:** Defer to future enhancement (not critical)

---

### 2. Input Token Counting
**Priority:** Medium  
**Description:** Add input token counting to validate against context window limits.

**Current State:** TODO comment in code
```python
validated_max_tokens = validate_max_tokens(
    model_name=model,
    requested_max_tokens=max_output_tokens,
    input_tokens=0,  # TODO: Add token counting for input
    enforce_limits=ENFORCE_MAX_TOKENS
)
```

**Required Work:**
- Implement token counting for input messages
- Update validate_max_tokens() to use actual input token count
- Validate: input_tokens + max_output_tokens <= max_context_tokens

**Status:** Deferred to Phase 2.1.5 or later

---

### 3. Dynamic Limit Adjustment
**Priority:** Low  
**Description:** Adaptive limits based on system prompt size, conversation history, memory constraints.

**Status:** Deferred to future enhancement

---

### 4. Metrics Collection
**Priority:** Medium  
**Description:** Collect token usage metrics for optimization and monitoring.

**Status:** Deferred to Phase 2.1.4 or later

---

## Notes from User

### Supabase Usage Clarification
**Date:** 2025-10-21  
**User Note:**
> "Supabase is meant to be just a storage space, in case worst case situation if a conversation needs to be retrieved."

**Implications:**
- Supabase is backup/recovery storage, NOT primary conversation caching
- Each platform (Kimi, GLM) has its own conversation caching mechanism
- Token limits prevent truncation at API level (before caching layer)
- Don't rely on Supabase for conversation reconstruction in normal flow

**Impact on Design:**
- ✅ Current implementation is correct - focuses on preventing truncation at API level
- ✅ No changes needed to Supabase integration strategy
- 📝 Future: Ensure truncation detection logs to Supabase for monitoring only

---

## Review Checklist for Next Agent

When reviewing this file:
- [ ] Verify all "RESOLVED" items are actually resolved
- [ ] Check if any "Deferred" items should be promoted to active work
- [ ] Update priorities based on production feedback
- [ ] Remove items that are no longer relevant
- [ ] Add new items discovered during implementation

---

**Last Updated:** 2025-10-21  
**Next Review:** After Phase 2.1 completion

