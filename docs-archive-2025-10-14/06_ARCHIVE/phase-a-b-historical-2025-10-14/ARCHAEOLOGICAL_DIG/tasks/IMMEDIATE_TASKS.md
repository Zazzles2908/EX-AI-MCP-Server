# IMMEDIATE TASKS - SIMPLE LIST
**Date:** 2025-10-12
**Priority:** Do these in order

---

## TASK 1: FIX FILE INCLUSION (MY MISTAKE)

**What I Did Wrong:**
I commented out code in 4 files thinking it was a "temporary fix":
- `tools/workflows/analyze.py` (lines 323-327)
- `tools/workflows/codereview.py` (lines 307-311)
- `tools/workflows/refactor.py` (lines 313-317)
- `tools/workflows/secaudit.py` (lines 456-460)

**What Should Happen:**
File inclusion is ALREADY controlled by `.env` variable:
- `EXPERT_ANALYSIS_INCLUDE_FILES=false`

**Fix:**
1. Remove my commented-out code from those 4 files
2. Ensure tools respect the .env variable
3. Test that it works

**Estimated Time:** 30 minutes

---

## TASK 2: REORGANIZE MARKDOWN FILES

**Problem:** Too many markdown files, overwhelming

**Solution:** Follow the reorganization plan you provided

**Estimated Time:** 2-3 hours

---

## TASK 3: DOCUMENT MODEL CAPABILITIES

**Problem:** No clear documentation of which models support what

**Solution:** Create simple table in .env.example showing:
- Which models support file uploads
- Which models support web search
- Cost per model
- Context window per model

**Estimated Time:** 1 hour

---

## TASK 4: INVESTIGATE DAEMON CRASHES

**Problem:** Daemon crashes during extended EXAI sessions

**Solution:** 
1. Review daemon logs
2. Identify crash patterns
3. Implement fixes

**Estimated Time:** 4-8 hours

---

## TASK 5: RESUME WORKFLOWTOOLS TESTING

**After tasks 1-4 are complete:**
- Complete remaining 5 code reviews
- Functional testing of all 12 tools
- Document results

**Estimated Time:** 4-6 hours

---

**TOTAL ESTIMATED TIME:** 12-19 hours

**RECOMMENDATION:** Start with Task 1 (quick fix), then Task 2 (reorganize), then others

