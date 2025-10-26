# Phase 2.4 Quick Start Checklist

**Date:** 2025-10-22  
**Purpose:** Immediate action items for Phase 2.4 execution  
**Full Plan:** See `PHASE_2.4_IMPLEMENTATION_PLAN_2025-10-22.md`

---

## 🚀 START HERE

### Before You Begin
- [ ] Read `PHASE_2.4_IMPLEMENTATION_PLAN_2025-10-22.md` (comprehensive plan)
- [ ] Review `MIGRATION_STRATEGY_EVOLUTION_2025-10-22.md` (context)
- [ ] Understand current status: Phase 2.3 Complete (33% overall)

---

## 📅 Days 1-2: Foundation Completion

### Task 1: Implement Missing Handlers (4-6 hours)
**File:** `src/file_management/migration_facade.py`

- [ ] Implement `_legacy_download()` method
  - [ ] Follow pattern from `_legacy_kimi_upload()` (lines 339-403)
  - [ ] Import SupabaseStorageManager
  - [ ] Call manager.download_file(file_id)
  - [ ] Convert to FileOperationResult
  - [ ] Add error handling

- [ ] Implement `_legacy_delete()` method
  - [ ] Follow pattern from `_legacy_kimi_upload()` (lines 339-403)
  - [ ] Import SupabaseStorageManager
  - [ ] Call manager.delete_file(file_id)
  - [ ] Convert to FileOperationResult
  - [ ] Add error handling

- [ ] Create test cases
  - [ ] Test download operations
  - [ ] Test delete operations
  - [ ] Test error scenarios

- [ ] EXAI validation
  - [ ] Use `codereview_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

### Task 2: Fix Migration Tracking (6-8 hours)
**Reference:** `PHASE_D_PRODUCTION_READINESS_PLAN.md` Task 1

- [ ] Backup current state
  - [ ] Export full database schema
  - [ ] Backup all data
  - [ ] Document current migration state

- [ ] Schema audit
  - [ ] Compare current schema vs. migration files
  - [ ] Identify untracked changes
  - [ ] Document discrepancies

- [ ] Create migration files
  - [ ] Export current schema to new migration file
  - [ ] Include extensions, policies, indexes
  - [ ] Use idempotent SQL (IF NOT EXISTS)

- [ ] Mark migrations as applied
  - [ ] Run: `supabase db push --include-tags`
  - [ ] Validate migration tracking synchronized
  - [ ] Verify no pending migrations

- [ ] Test branch creation
  - [ ] Create test branch
  - [ ] Verify status is not MIGRATIONS_FAILED
  - [ ] Validate branch schema matches main

- [ ] EXAI validation
  - [ ] Use `debug_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

---

## 📅 Days 3-4: Validation & Monitoring

### Task 3: Shadow Mode Validation (24-48 hours)

- [ ] Enable shadow mode
  - [ ] Set `ENABLE_SHADOW_MODE=true` in .env.docker
  - [ ] Set `SHADOW_MODE_SAMPLE_RATE=0.05` (5%)
  - [ ] Restart Docker container

- [ ] Monitor for 24-48 hours
  - [ ] Check logs for shadow mode comparisons
  - [ ] Track comparison count (target: >50)
  - [ ] Monitor error rate (target: <5%)
  - [ ] Monitor discrepancy rate (target: <2%)

- [ ] Analyze results
  - [ ] Review comparison logs
  - [ ] Investigate any discrepancies
  - [ ] Document findings

- [ ] EXAI validation
  - [ ] Use `analyze_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

### Task 4: Monitoring Dashboard Setup (8-10 hours)

- [ ] Create monitoring endpoint
  - [ ] Add `/monitoring/hybrid-status` endpoint
  - [ ] Include rollout status
  - [ ] Include shadow mode metrics
  - [ ] Include performance metrics

- [ ] Test dashboard
  - [ ] Access via localhost
  - [ ] Verify all metrics updating
  - [ ] Test historical data retention

- [ ] Configure alerts
  - [ ] Error rate >5%
  - [ ] Performance degradation >20%
  - [ ] Discrepancy rate >2%

- [ ] EXAI validation
  - [ ] Use `chat_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

---

## 📅 Day 5: Rollout Preparation

### Task 5: Rollback Procedures (4-6 hours)

- [ ] Implement emergency rollback
  - [ ] Create `emergency_rollback()` function
  - [ ] Set all rollout percentages to 0
  - [ ] Disable unified manager
  - [ ] Enable fallback to legacy

- [ ] Implement gradual rollback
  - [ ] Create `gradual_rollback(target_percentage)` function
  - [ ] Reduce rollout in 10% increments
  - [ ] Wait 5 minutes between reductions

- [ ] Implement feature-specific rollback
  - [ ] Create `rollback_feature(feature)` function
  - [ ] Support per-tool rollback

- [ ] Test rollback procedures
  - [ ] Test emergency rollback in staging
  - [ ] Test gradual rollback in staging
  - [ ] Test feature-specific rollback in staging

- [ ] Document rollback triggers
  - [ ] Error rate >5%
  - [ ] Performance degradation >20%
  - [ ] Data consistency issues
  - [ ] System resource utilization >80%

- [ ] EXAI validation
  - [ ] Use `secaudit_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

### Task 6: Success Metrics Definition (2-3 hours)

- [ ] Define 1% rollout criteria
  - [ ] Error rate: <1%
  - [ ] Performance degradation: <5%
  - [ ] Duration: 24 hours minimum

- [ ] Define 10% rollout criteria
  - [ ] Error rate: <0.5%
  - [ ] Performance degradation: <3%
  - [ ] Duration: 72 hours minimum

- [ ] Define 50% rollout criteria
  - [ ] Error rate: <0.2%
  - [ ] Performance degradation: <2%
  - [ ] Duration: 72 hours minimum

- [ ] Define 100% rollout criteria
  - [ ] Error rate: <0.1%
  - [ ] Performance degradation: <1%
  - [ ] Duration: 48 hours minimum

- [ ] EXAI validation
  - [ ] Use `planner_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231
  - [ ] Get approval before proceeding

---

## 📅 Days 6-14: Gradual Rollout

### Task 7: 1% Rollout (Day 6)

- [ ] Enable 1% rollout
  - [ ] Set `KIMI_ROLLOUT_PERCENTAGE=1` in .env.docker
  - [ ] Set `ENABLE_KIMI_MIGRATION=true` in .env.docker
  - [ ] Restart Docker container

- [ ] Monitor for 24 hours
  - [ ] Check error rate (target: <1%)
  - [ ] Check performance (target: <5% degradation)
  - [ ] Check data consistency
  - [ ] Review monitoring dashboard

- [ ] Decision point
  - [ ] If success criteria met: Proceed to 10%
  - [ ] If not met: Rollback and investigate

- [ ] EXAI validation
  - [ ] Use `tracer_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231

### Task 8: 10% Rollout (Days 7-9)

- [ ] Increase to 10%
  - [ ] Set `KIMI_ROLLOUT_PERCENTAGE=10`
  - [ ] Expand to all tools if Kimi successful
  - [ ] Restart Docker container

- [ ] Monitor for 72 hours
  - [ ] Check error rate (target: <0.5%)
  - [ ] Check performance (target: <3% degradation)
  - [ ] Performance optimization if needed

- [ ] Decision point
  - [ ] If success criteria met: Proceed to 50%
  - [ ] If not met: Rollback and investigate

- [ ] EXAI validation
  - [ ] Use `testgen_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231

### Task 9: 50% Rollout (Days 10-12)

- [ ] Scale to 50%
  - [ ] Set `KIMI_ROLLOUT_PERCENTAGE=50`
  - [ ] Restart Docker container

- [ ] Monitor for 72 hours
  - [ ] Check error rate (target: <0.2%)
  - [ ] Check performance (target: <2% degradation)
  - [ ] Full system validation

- [ ] Decision point
  - [ ] If success criteria met: Proceed to 100%
  - [ ] If not met: Rollback and investigate

- [ ] EXAI validation
  - [ ] Use `consensus_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231

### Task 10: 100% Rollout (Days 13-14)

- [ ] Complete migration
  - [ ] Set `KIMI_ROLLOUT_PERCENTAGE=100`
  - [ ] Disable shadow mode: `ENABLE_SHADOW_MODE=false`
  - [ ] Restart Docker container

- [ ] Monitor for 48 hours
  - [ ] Check error rate (target: <0.1%)
  - [ ] Check performance (target: <1% degradation)
  - [ ] Verify all users migrated

- [ ] Cleanup
  - [ ] Archive legacy code paths
  - [ ] Update documentation
  - [ ] Create handoff document

- [ ] EXAI final validation
  - [ ] Use `refactor_EXAI-WS` tool
  - [ ] Continuation ID: 014e83a9-e53c-4d4b-ae8e-bb73eaf88231

---

## 🎯 Success Criteria Summary

### Phase 2.4.1 (Days 1-2)
- ✅ Missing handlers implemented and tested
- ✅ Migration tracking fixed and validated
- ✅ EXAI validation complete

### Phase 2.4.2 (Days 3-4)
- ✅ Shadow mode validated (24-48 hours)
- ✅ Monitoring dashboard operational
- ✅ EXAI validation complete

### Phase 2.4.3 (Day 5)
- ✅ Rollback procedures documented and tested
- ✅ Success metrics defined and validated
- ✅ EXAI validation complete

### Phase 2.4.4 (Days 6-14)
- ✅ 1% rollout successful (24 hours)
- ✅ 10% rollout successful (72 hours)
- ✅ 50% rollout successful (72 hours)
- ✅ 100% rollout successful (48 hours)
- ✅ EXAI final validation complete

---

## 🚨 Emergency Contacts

**EXAI Continuation ID:** 014e83a9-e53c-4d4b-ae8e-bb73eaf88231  
**Remaining Exchanges:** 17

**Emergency Rollback:**
```bash
# Set in .env.docker
ENABLE_UNIFIED_MANAGER=false
ENABLE_FALLBACK_TO_LEGACY=true
KIMI_ROLLOUT_PERCENTAGE=0
SMART_HANDLER_ROLLOUT_PERCENTAGE=0
SUPABASE_ROLLOUT_PERCENTAGE=0

# Restart Docker
docker-compose restart
```

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-22  
**Status:** Ready for Execution

