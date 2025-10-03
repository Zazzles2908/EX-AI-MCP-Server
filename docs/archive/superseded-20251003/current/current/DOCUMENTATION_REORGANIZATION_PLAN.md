# Documentation Reorganization Plan

**Date**: 2025-09-30  
**Status**: 🎯 **READY TO EXECUTE**  
**Objective**: Reorganize docs/current/ to contain only relevant, current documentation

---

## 🎯 CURRENT STATE ANALYSIS

### Current Structure

```
docs/current/
├── README.md
├── architecture/
│   ├── AI_manager/
│   ├── API_platforms/
│   ├── IMPLEMENTATION_ROADMAP.md
│   ├── _raw/
│   ├── classification/
│   ├── decision_tree/
│   ├── implementation_roadmap/
│   ├── index.md
│   ├── observability/
│   ├── task-manager-implementation-checklist.md
│   └── tool_function/
├── development/
│   ├── HANDOVER_2025-09-30_request_handler_ready.md
│   ├── PHASE1.3_HANDOFF_COMPLETE.md
│   ├── SESSION_SUMMARY_2025-09-30_PHASE_COMPLETE.md
│   ├── implementation_roadmap/
│   ├── phase1/
│   ├── phase2/
│   └── phase3/
├── policies/
│   └── AUGMENT_CODE_GUIDELINES.md
├── reviews/
│   ├── 20250928_glm_agent_session.json
│   └── 20250928_ws_probe_run.md
└── tools/
    ├── analyze.md
    ├── challenge.md
    ├── chat.md
    ├── ... (15 tool docs)
```

### Problems

1. **Scattered Information**
   - Architecture docs mixed with implementation details
   - Development docs in multiple locations
   - No clear hierarchy

2. **Outdated Content**
   - Old implementation roadmaps
   - Completed phase documents
   - Historical reviews

3. **Poor Discoverability**
   - Hard to find current information
   - No clear entry points
   - Inconsistent naming

4. **Duplication**
   - Multiple roadmap documents
   - Overlapping architecture docs

---

## 🏗️ PROPOSED STRUCTURE

### New Organization

```
docs/current/
├── README.md (updated - main entry point)
│
├── 1_getting_started/
│   ├── quick_start.md
│   ├── installation.md
│   ├── configuration.md
│   └── first_steps.md
│
├── 2_architecture/
│   ├── README.md (architecture overview)
│   ├── system_overview.md
│   ├── ai_manager/
│   │   ├── overview.md
│   │   ├── workflow.md
│   │   ├── prompt_system.md
│   │   └── AI_MANAGER_SYSTEM_PROMPT_REDESIGN.md
│   ├── providers/
│   │   ├── kimi.md
│   │   ├── glm.md
│   │   └── provider_system.md
│   ├── request_flow/
│   │   ├── request_lifecycle.md
│   │   ├── routing.md
│   │   └── context_management.md
│   └── data_flow/
│       ├── streaming.md
│       └── caching.md
│
├── 3_tools/
│   ├── README.md (tools overview)
│   ├── workflow_tools/
│   │   ├── analyze.md
│   │   ├── thinkdeep.md
│   │   ├── codereview.md
│   │   ├── debug.md
│   │   ├── refactor.md
│   │   ├── secaudit.md
│   │   ├── precommit.md
│   │   └── testgen.md
│   ├── planning_tools/
│   │   ├── planner.md
│   │   ├── consensus.md
│   │   └── tracer.md
│   ├── utility_tools/
│   │   ├── chat.md
│   │   ├── docgen.md
│   │   ├── challenge.md
│   │   ├── listmodels.md
│   │   └── version.md
│   └── tool_comparison.md
│
├── 4_guides/
│   ├── README.md (guides overview)
│   ├── using_tools/
│   │   ├── workflow_patterns.md
│   │   ├── multi_step_analysis.md
│   │   └── continuation_handling.md
│   ├── best_practices/
│   │   ├── prompt_engineering.md
│   │   ├── file_handling.md
│   │   └── error_recovery.md
│   └── advanced/
│       ├── custom_providers.md
│       ├── streaming.md
│       └── performance_tuning.md
│
├── 5_reference/
│   ├── README.md (reference overview)
│   ├── api/
│   │   ├── mcp_protocol.md
│   │   ├── tool_schemas.md
│   │   └── provider_api.md
│   ├── configuration/
│   │   ├── environment_variables.md
│   │   ├── provider_config.md
│   │   └── model_restrictions.md
│   └── troubleshooting/
│       ├── common_issues.md
│       ├── debugging.md
│       └── faq.md
│
├── 6_development/
│   ├── README.md (development overview)
│   ├── current_status/
│   │   ├── SESSION_SUMMARY_2025-09-30_PHASE_COMPLETE.md
│   │   └── completed_refactorings.md
│   ├── contributing/
│   │   ├── code_guidelines.md (from AUGMENT_CODE_GUIDELINES.md)
│   │   ├── adding_tools.md
│   │   └── testing.md
│   └── roadmap/
│       ├── future_enhancements.md
│       └── planned_features.md
│
└── archive/
    ├── phase1/ (moved from development/phase1/)
    ├── phase2/ (moved from development/phase2/)
    ├── phase3/ (moved from development/phase3/)
    ├── old_architecture/ (moved from architecture/_raw/)
    └── historical_reviews/ (moved from reviews/)
```

---

## 📋 REORGANIZATION TASKS

### Phase 1: Create New Structure (30 minutes)

**Tasks**:
1. Create new folder structure
2. Create README.md files for each section
3. Set up navigation hierarchy

**Folders to Create**:
- `1_getting_started/`
- `2_architecture/ai_manager/`
- `2_architecture/providers/`
- `2_architecture/request_flow/`
- `2_architecture/data_flow/`
- `3_tools/workflow_tools/`
- `3_tools/planning_tools/`
- `3_tools/utility_tools/`
- `4_guides/using_tools/`
- `4_guides/best_practices/`
- `4_guides/advanced/`
- `5_reference/api/`
- `5_reference/configuration/`
- `5_reference/troubleshooting/`
- `6_development/current_status/`
- `6_development/contributing/`
- `6_development/roadmap/`
- `archive/`

### Phase 2: Move Existing Content (45 minutes)

**Tool Documentation** (Move to `3_tools/`):
```
tools/analyze.md → 3_tools/workflow_tools/analyze.md
tools/thinkdeep.md → 3_tools/workflow_tools/thinkdeep.md
tools/codereview.md → 3_tools/workflow_tools/codereview.md
tools/debug.md → 3_tools/workflow_tools/debug.md
tools/refactor.md → 3_tools/workflow_tools/refactor.md
tools/secaudit.md → 3_tools/workflow_tools/secaudit.md
tools/precommit.md → 3_tools/workflow_tools/precommit.md
tools/testgen.md → 3_tools/workflow_tools/testgen.md
tools/planner.md → 3_tools/planning_tools/planner.md
tools/consensus.md → 3_tools/planning_tools/consensus.md
tools/tracer.md → 3_tools/planning_tools/tracer.md
tools/chat.md → 3_tools/utility_tools/chat.md
tools/docgen.md → 3_tools/utility_tools/docgen.md
tools/challenge.md → 3_tools/utility_tools/challenge.md
tools/listmodels.md → 3_tools/utility_tools/listmodels.md
tools/version.md → 3_tools/utility_tools/version.md
```

**Architecture Documentation** (Reorganize `2_architecture/`):
```
architecture/AI_manager/ → 2_architecture/ai_manager/
architecture/API_platforms/ → 2_architecture/providers/
architecture/AI_MANAGER_SYSTEM_PROMPT_REDESIGN.md → 2_architecture/ai_manager/
```

**Development Documentation** (Move to `6_development/`):
```
development/SESSION_SUMMARY_2025-09-30_PHASE_COMPLETE.md → 6_development/current_status/
policies/AUGMENT_CODE_GUIDELINES.md → 6_development/contributing/code_guidelines.md
```

**Archive Old Content**:
```
development/phase1/ → archive/phase1/
development/phase2/ → archive/phase2/
development/phase3/ → archive/phase3/
architecture/_raw/ → archive/old_architecture/
reviews/ → archive/historical_reviews/
```

### Phase 3: Create New Content (60 minutes)

**Getting Started**:
- `1_getting_started/quick_start.md` - 5-minute quick start guide
- `1_getting_started/installation.md` - Installation instructions
- `1_getting_started/configuration.md` - Basic configuration
- `1_getting_started/first_steps.md` - First tool usage examples

**Architecture**:
- `2_architecture/README.md` - Architecture overview
- `2_architecture/system_overview.md` - High-level system design
- `2_architecture/ai_manager/overview.md` - AI Manager explanation
- `2_architecture/ai_manager/workflow.md` - Request workflow
- `2_architecture/providers/provider_system.md` - Provider architecture

**Guides**:
- `4_guides/using_tools/workflow_patterns.md` - Common patterns
- `4_guides/best_practices/prompt_engineering.md` - How to write good prompts
- `4_guides/best_practices/file_handling.md` - File path best practices

**Reference**:
- `5_reference/configuration/environment_variables.md` - All env vars
- `5_reference/troubleshooting/common_issues.md` - FAQ and solutions

### Phase 4: Update Navigation (15 minutes)

**Update Main README.md**:
- Add clear navigation to numbered sections
- Provide quick links to common tasks
- Include "What's New" section

**Create Section READMEs**:
- Each numbered folder gets a README.md
- Explain section purpose
- List contents with descriptions

---

## 🎯 EXECUTION PLAN

### Step-by-Step

1. **Backup Current Structure**
   ```bash
   Copy-Item -Path "docs\current" -Destination "docs\current_BACKUP_2025-09-30" -Recurse
   ```

2. **Create New Folders**
   - Execute folder creation commands
   - Verify structure

3. **Move Existing Files**
   - Move tool docs to categorized folders
   - Move architecture docs
   - Move development docs
   - Archive old content

4. **Create New Content**
   - Write getting started guides
   - Write architecture overviews
   - Write best practices guides
   - Write reference docs

5. **Update Navigation**
   - Update main README.md
   - Create section READMEs
   - Add cross-references

6. **Verify & Test**
   - Check all links work
   - Verify no broken references
   - Test navigation flow

---

## 📊 EXPECTED OUTCOMES

### Before

- **Total Files**: ~50
- **Folders**: 15
- **Max Depth**: 4 levels
- **Discoverability**: Low
- **Organization**: Poor

### After

- **Total Files**: ~60 (with new guides)
- **Folders**: 25 (better organized)
- **Max Depth**: 3 levels
- **Discoverability**: High
- **Organization**: Excellent

### Benefits

1. **Clear Navigation**
   - Numbered sections show reading order
   - Easy to find information
   - Logical hierarchy

2. **Better Onboarding**
   - Getting started section for new users
   - Progressive disclosure of complexity
   - Clear learning path

3. **Improved Maintenance**
   - Current docs separate from archive
   - Easy to update
   - No duplication

4. **Professional Structure**
   - Industry-standard organization
   - Scalable for future growth
   - Easy to contribute to

---

## 🎯 NEXT STEPS

1. **Review & Approve** this reorganization plan
2. **Create backup** of current structure
3. **Execute reorganization** (estimated 2.5 hours)
4. **Update main README.md** with new navigation
5. **Announce changes** to team

---

**Document Status**: 🎯 **READY TO EXECUTE**  
**Next Action**: Approve plan and begin reorganization  
**Estimated Time**: 2.5 hours

